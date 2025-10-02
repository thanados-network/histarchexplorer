import json
from dataclasses import asdict, dataclass, field
from typing import Any, Optional

import requests
from flask import g

from histarchexplorer import app, cache
from histarchexplorer.api.api_access import PROXIES
from histarchexplorer.models.util import format_date, \
    get_description_translated, get_divisions, get_icon, \
    get_render_type, split_date_string


@dataclass
class GeometryModel:
    id: int
    type: str
    coordinates: Any

    def swap_latlng(self) -> "GeometryModel":
        def flip(coord):
            return [coord[1], coord[0]]

        if self.type == "Point":
            new_coords = flip(self.coordinates)

        elif self.type == "LineString":
            new_coords = [flip(c) for c in self.coordinates]

        elif self.type == "Polygon":
            # Polygons are lists of linear rings (outer ring + holes)
            new_coords = [[flip(c) for c in ring] for ring in self.coordinates]

        else:
            # Leave untouched if unknown geometry type
            new_coords = self.coordinates

        return GeometryModel(id=self.id, type=self.type, coordinates=new_coords)

@dataclass
class PropertyModel:
    locationId: int
    title: str
    description: str
    shapeType: str


@dataclass
class FeatureModel:
    geometry: GeometryModel
    properties: PropertyModel

    def to_dict(self) -> dict:
        return {
            "type": "Feature",
            "geometry": asdict(self.geometry),
            "properties": asdict(self.properties)}

    def to_json(self, **kwargs) -> str:
        return json.dumps(self.to_dict(), **kwargs)

    def swap_latlng(self) -> "FeatureModel":
        return FeatureModel(
            geometry=self.geometry.swap_latlng(),
            properties=self.properties)

@dataclass
class TimePointModel:
    earliest: Optional[str] = None
    latest: Optional[str] = None
    comment: Optional[str] = None


@dataclass
class TimeRangeModel:
    start: Optional[TimePointModel] = None
    end: Optional[TimePointModel] = None


@dataclass
class TypeHierarchyEntry:
    label: str
    descriptions: Optional[str]
    identifier: str


@dataclass
class EntityTypeModel:
    id: int
    title: str
    descriptions: Optional[str]
    is_standard: Optional[bool]
    type_hierarchy: Optional[list[TypeHierarchyEntry]]
    value: Optional[str]
    unit: Optional[str]
    icon: Optional[str]
    division: Optional[dict[str, str]]

    def to_json(self, *, indent: Optional[int] = 2) -> str:
        return json.dumps(asdict(self), indent=indent, ensure_ascii=False)


@dataclass
class ExternalReferenceModel:
    id: int
    type: str
    identifier: str
    reference_system: str
    resolver_url: Optional[str]
    reference_url: Optional[str]

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            type=data.get("type"),
            identifier=data.get("identifier"),
            reference_system=data.get("referenceSystem"),
            resolver_url=data.get("resolverURL"),
            reference_url=data.get("referenceURL"))


@dataclass
class Reference:
    id: int
    title: str
    system_class: str
    type: Optional[str] = None
    type_id: Optional[int] = None
    citation: Optional[str] = None
    pages: Optional[str] = None

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            title=data.get("title"),
            system_class=data.get("systemClass"),
            type=data.get("type"),
            type_id=data.get("typeId"),
            citation=data.get("citation"),
            pages=data.get("pages"))


@dataclass
class File:
    id: int
    title: str
    license: Optional[str] = None
    creator: Optional[str] = None
    license_holder: Optional[str] = None
    public: bool = False
    url: Optional[str] = None
    mime_type: Optional[str] = None
    iiif_manifest: Optional[str] = None
    iiif_base_path: Optional[str] = None
    main_image: int = None
    render_type: str = None


@dataclass
class Relation:
    id: int
    name: str
    system_class: str
    relation_types: Optional[list[dict[str, Any]]] = None
    description: dict[str, str] | None = None
    aliases: Optional[list[str]] = None
    time_range: Optional[TimeRangeModel] = None
    geometries: list[FeatureModel] = field(default_factory=list)
    types: list[EntityTypeModel] = field(default_factory=list)


@dataclass
class PresentationView:
    id: int
    system_class: str
    title: str
    description: dict[str, str]
    aliases: list[str]
    start: str
    end: str
    geometries: list[FeatureModel] = field(default_factory=list)
    when: Optional[TimeRangeModel] = None
    types: list[EntityTypeModel] = field(default_factory=list)
    externalReferenceSystems: list[ExternalReferenceModel] = field(
        default_factory=list)
    references: list[Reference] = field(default_factory=list)
    files: list[File] = field(default_factory=list)
    relations: dict[str, list[Relation]] = field(default_factory=dict)

    def to_json(self, *, indent: Optional[int] = 2) -> str:
        return json.dumps(asdict(self), indent=indent, ensure_ascii=False)

    @staticmethod
    def parse_geometries(
            geometry_data: Any,
            relation_id: int = 0) -> list["FeatureModel"]:

        if not geometry_data:
            return []

        def parse_single(data: dict) -> "FeatureModel":
            geometry_model = GeometryModel(
                id=relation_id,
                type=data['geometry']["type"],
                coordinates=data["geometry"]["coordinates"])
            property_model = PropertyModel(
                locationId=data["properties"]["locationId"],
                title=data["properties"]["title"],
                description=data["properties"]["description"],
                shapeType=data["properties"]["shapeType"])
            return FeatureModel(
                geometry=geometry_model,
                properties=property_model)

        geometries = []
        if geometry_data.get('type') == 'FeatureCollection':
            for geom in geometry_data['features']:
                geometries.append(parse_single(geom))
        else:
            geometries.append(parse_single(geometry_data))
        return geometries

    @staticmethod
    def parse_time_range(when: dict) -> Optional[TimeRangeModel]:
        if not when:
            return None
        return TimeRangeModel(
            start=TimePointModel(**when.get("start", {}))
            if when.get("start") else None,
            end=TimePointModel(**when.get("end", {}))
            if when.get("end") else None)

    @staticmethod
    def parse_types(types_data: list[dict]) -> list[EntityTypeModel]:
        types = []
        for type_ in types_data:
            hierarchy = []
            if type_.get("typeHierarchy"):
                hierarchy = [
                    TypeHierarchyEntry(**th)
                    for th in type_.get("typeHierarchy", [])]
            types.append(EntityTypeModel(
                id=type_["id"],
                title=type_.get("title", ""),
                descriptions=type_.get("descriptions"),
                is_standard=type_.get("isStandard"),
                type_hierarchy=hierarchy,
                value=type_.get("value"),
                unit=type_.get("unit"),
                icon=get_icon(type_["id"], type_.get("typeHierarchy")),
                division=get_divisions(type_["id"],
                                       type_.get("typeHierarchy"))))
        return types

    @staticmethod
    def parse_relations(raw_relations: dict) -> dict[str, list[Relation]]:
        grouped_relations: dict[str, list[Relation]] = {}
        for system_class, relation_list in raw_relations.items():
            relations = []
            for rel in relation_list:
                if not isinstance(rel, dict):
                    continue

                rel_geometries = PresentationView.parse_geometries(
                    rel.get("geometries"), rel.get("id", 0))
                time_range = PresentationView.parse_time_range(rel.get("when"))
                rel_types = []

                standard_type = rel.get("standardType")
                if isinstance(standard_type, dict):
                    rel_types.append(EntityTypeModel(
                        id=standard_type.get("id", 0),
                        title=standard_type.get("title", ""),
                        descriptions=None,
                        is_standard=True,
                        type_hierarchy=[],
                        value=None,
                        unit=None,
                        icon=None,
                        division=None))

                relation = Relation(
                    id=rel["id"],
                    name=rel.get("title"),
                    system_class=rel.get("systemClass", system_class),
                    relation_types=rel.get("relationTypes"),
                    description=get_description_translated(
                        rel.get("description")),
                    aliases=rel.get("aliases", []),
                    time_range=time_range,
                    geometries=rel_geometries,
                    types=rel_types)

                relations.append(relation)

            if relations:
                grouped_relations[system_class] = relations

        return grouped_relations

    @staticmethod
    def parse_file(entity_id: int, raw_file: dict) -> list[File]:
        files = []
        for f in raw_file:
            if isinstance(f, dict):
                files.append(File(
                    id=f["id"],
                    title=f["title"],
                    license=f.get("license"),
                    creator=f.get("creator"),
                    license_holder=f.get("licenseHolder"),
                    public=f["publicShareable"],
                    url=f.get("url"),
                    mime_type=f.get("mimetype"),
                    iiif_manifest=f.get("IIIFManifest"),
                    iiif_base_path=f.get("IIIFBasePath"),
                    main_image=g.main_images.get(entity_id) == entity_id,
                    render_type=get_render_type(f.get("mimetype"))))
        return files

    @classmethod
    @cache.memoize()
    def from_api(cls, entity_id: int) -> 'PresentationView':
        response = requests.get(
            f"{app.config['API_URL']}entity_presentation_view/{entity_id}",
            params={
                'place_hierarchy': 'true',
                'remove_empty_values': 'true',
                'centroid': 'true'},
            headers=g.api_headers,
            proxies=PROXIES,
            timeout=30)
        response.raise_for_status()
        data = response.json()

        when_data = cls.parse_time_range(data.get("when"))

        start_date = None
        end_date = None
        if when_data and when_data.start:
            start_date = format_date(
                split_date_string(when_data.start.earliest),
                split_date_string(when_data.start.latest))
        if when_data and when_data.end:
            end_date = format_date(
                split_date_string(when_data.end.earliest),
                split_date_string(when_data.end.latest))

        return cls(
            id=data["id"],
            system_class=data.get("systemClass", ""),
            title=data.get("title", ""),
            description=get_description_translated(
                data.get("description", "")),
            aliases=data.get("aliases", []),
            geometries=cls.parse_geometries(data.get("geometries", {})),
            when=when_data,
            types=cls.parse_types(data.get("types", [])),
            externalReferenceSystems=[
                ExternalReferenceModel.from_dict(er)
                for er in data.get("externalReferenceSystems", [])
                if isinstance(er, dict)],
            references=[
                Reference.from_dict(ref)
                for ref in data.get("references", [])
                if isinstance(ref, dict)],
            files=cls.parse_file(data["id"], data.get('files', [])),
            relations=cls.parse_relations(data.get("relations", {})),
            start=start_date,
            end=end_date)
