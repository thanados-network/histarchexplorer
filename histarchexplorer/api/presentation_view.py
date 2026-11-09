import json
from dataclasses import asdict, dataclass, field
from typing import Any, Optional

import requests  # type: ignore[import-untyped]
from flask import g, url_for

from histarchexplorer import app, cache
from histarchexplorer.api.api_access import PROXIES
from histarchexplorer.api.util import (
    dict_to_camel_case, format_date,
    get_description_translated,
    get_divisions,
    get_render_type, split_date_string)
from histarchexplorer.services.entity_cache import record_entity_cached


@dataclass
class GeometryModel:
    """Represents a spatial geometry in GeoJSON format.

    Attributes:
        type (str): Geometry type (e.g., 'Point', 'Polygon', 'LineString').
        coordinates (Any): Coordinate values matching the geometry type.
    """
    type: str
    coordinates: Any


@dataclass
class PropertyModel:
    """Represents the properties associated with a spatial feature.

    Attributes:
        location_id (int): ID of the spatial location record.
        entity_id (int): ID of the parent entity.
        title (str): Title or label of the feature.
        description (str): Description text or notes.
        shape_type (str): Geometric shape type (e.g., 'point', 'polygon').
        system_class (str): System class name of the associated entity.
    """
    location_id: int
    entity_id: int
    title: str
    description: str
    shape_type: str
    system_class: str


@dataclass
class FeatureModel:
    """Represents a complete GeoJSON Feature with geometry and properties.

    Attributes:
        geometry (GeometryModel): The spatial geometry object.
        properties (PropertyModel): Associated metadata and attributes.
    """
    geometry: GeometryModel
    properties: PropertyModel


@dataclass
class TimePointModel:
    """Represents a single point in time with fuzzy/chronological bounds.

    Attributes:
        earliest (str | None): Earliest possible date boundary.
        latest (str | None): Latest possible date boundary.
        comment (str | None): Chronological notes or comments.
    """
    earliest: Optional[str] = None
    latest: Optional[str] = None
    comment: Optional[str] = None


@dataclass
class TimeRangeModel:
    """Represents a temporal coverage range with start and end points.

    Attributes:
        start (TimePointModel | None): Temporal start boundary.
        end (TimePointModel | None): Temporal end boundary.
    """
    start: Optional[TimePointModel] = None
    end: Optional[TimePointModel] = None


@dataclass
class TypeHierarchyEntry:
    """Represents an entry within a classification type hierarchy.

    Attributes:
        label (str): Name or label of the hierarchy level.
        descriptions (str | None): Description of the classification level.
        identifier (str): System identifier/code for the level.
    """
    label: str
    descriptions: Optional[str]
    identifier: str


@dataclass
class EntityTypeModel:
    """Represents a classification type applied to an entity.

    Attributes:
        id (int): Unique identifier of the type.
        title (str): Name of the type.
        descriptions (str | None): Classification details.
        is_standard (bool | None): True if it is a standard system type.
        type_hierarchy (list[TypeHierarchyEntry] | None): Hierarchical path.
        value (str | None): Associated quantitative value or text.
        unit (str | None): Measurement unit of the value.
        division (dict[str, str] | None): Division category details.
    """
    id: int
    title: str
    descriptions: Optional[str]
    is_standard: Optional[bool]
    type_hierarchy: Optional[list[TypeHierarchyEntry]]
    value: Optional[str]
    unit: Optional[str]
    division: Optional[dict[str, str]]


@dataclass
class ExternalReferenceModel:
    """Represents a link to an external authority file or reference system.

    Attributes:
        id (str): Unique identifier of the reference.
        type (str): Reference system type (e.g. 'closeMatch', 'exactMatch').
        identifier (str): External ID or key (e.g., Wikidata ID).
        reference_system (str): Name of the external system.
        resolver_url (str | None): URL pattern to resolve the identifier.
        reference_url (str | None): Complete resolved HTTP URL.
    """
    id: str
    type: str
    identifier: str
    reference_system: str
    resolver_url: Optional[str]
    reference_url: Optional[str]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'ExternalReferenceModel':
        return cls(
            id=str(data["id"]),
            type=str(data.get("type") or ""),
            identifier=str(data.get("identifier") or ""),
            reference_system=str(data.get("referenceSystem") or ""),
            resolver_url=data.get("resolverURL"),
            reference_url=data.get("referenceURL"))


@dataclass
class Reference:
    """Represents a bibliographic reference or citation.

    Attributes:
        id (str): Unique reference identifier.
        title (str): Title of the cited source.
        system_class (str): System class of the reference.
        type (str | None): Citation type (e.g., 'primary', 'secondary').
        type_id (int | None): ID of the citation type.
        citation (str | None): Complete pre-formatted citation string.
        pages (str | None): Page numbers or ranges cited.
    """
    id: str
    title: str
    system_class: str
    type: Optional[str] = None
    type_id: Optional[int] = None
    citation: Optional[str] = None
    pages: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'Reference':
        raw_type_id = data.get("typeId")
        type_id = int(raw_type_id) if raw_type_id is not None else None
        return cls(
            id=str(data["id"]),
            title=str(data.get("title") or ""),
            system_class=str(data.get("systemClass") or ""),
            type=data.get("type"),
            type_id=type_id,
            citation=data.get("citation"),
            pages=data.get("pages"))


@dataclass
class File:
    """Represents an associated media file or document.

    Attributes:
        id (int): Unique file identifier.
        title (str): Display title of the file.
        license (str | int | None): License name or ID.
        creator (str | int | None): Author/creator of the file.
        license_holder (str | int | None): Owner of the file license.
        public (bool): True if the file is publicly shareable.
        url (str | int | None): Direct file download or view URL.
        mime_type (str | int | None): File mimetype (e.g., 'image/jpeg').
        iiif_manifest (str | int | None): IIIF manifest endpoint URL.
        iiif_base_path (str | int | None): Base path for IIIF image requests.
        overlay (str | int | None): True/ID if used as a map overlay.
        main_image (str | int | None): True/ID if it is the primary image.
        from_super_entity (bool): True if inherited from a parent entity.
        render_type (str | int | None): UI rendering type categorization.
    """
    id: int
    title: str
    license: str | int | None = None
    creator: str | int | None = None
    license_holder: str | int | None = None
    public: bool = False
    url: str | int | None = None
    mime_type: str | int | None = None
    iiif_manifest: str | int | None = None
    iiif_base_path: str | int | None = None
    overlay: str | int | None = None
    main_image: str | int | None = None
    from_super_entity: bool = False
    render_type: str | int | None = None


@dataclass
class Relation:
    """Represents a semantic relation between two entities.

    Attributes:
        id (int): ID of the related entity.
        name (str): Title/name of the related entity.
        system_class (str): System class of the related entity.
        relation_types (list[dict[str, Any]] | None): Semantic properties of
            the relation (e.g., 'crm:P46i_forms_part_of').
        description (dict[str, str] | None): Translated descriptions.
        aliases (list[str] | None): Alternative names of the related entity.
        time_range (TimeRangeModel | None): Validity period of the relation.
        geometries (list[FeatureModel]): Parsed spatial features.
        geometry_json (dict[str, Any]): Raw API GeoJSON.
        types (list[EntityTypeModel]): Classifications of the related entity.
    """
    id: int
    name: str
    system_class: str
    relation_types: Optional[list[dict[str, Any]]] = None
    description: dict[str, str] | None = None
    aliases: Optional[list[str]] = None
    time_range: Optional[TimeRangeModel] = None
    geometries: list[FeatureModel] = field(default_factory=list)
    geometry_json: Optional[dict[str, Any]] = None
    types: list[EntityTypeModel] = field(default_factory=list)


# pylint: disable=too-many-instance-attributes
@dataclass
class PresentationView:
    """Model representing the full presentation details for an entity.

    This class serves as the central data contract for entity visualization,
    defining the standard structure returned to frontend clients.

    Attributes:
        id (int): Unique identifier of the entity.
        system_class (str): OpenAtlas system class (e.g., 'place', 'feature').
        view_class (str): CSS or UI class mapping for display.
        title (str): Main display title of the entity.
        description (dict[str, str] | None): Translated description dict.
        aliases (list[str] | None): Alternative names or aliases.
        start (str | None): Formatted start date string.
        end (str | None): Formatted end date string.
        geometries (list[FeatureModel]): Parsed spatial features for mapping.
        geometry_json (dict[str, Any] | None): Raw API GeoJSON geometries.
        when (TimeRangeModel | None): Parsed temporal coverage model.
        types (list[EntityTypeModel]): List of classification types.
        external_reference_systems (list[ExternalReferenceModel]): Links to
            external authority files and resolver URLs.
        references (list[Reference]): Merged bibliographic references.
        files (list[File]): Associated public and licensed media files.
        relations (dict[str, list[Relation]]): Map of related entities grouped
            by their system class name.
    """
    id: int
    system_class: str
    view_class: str
    title: str
    description: dict[str, str] | None
    aliases: list[str] | None
    start: Optional[str]
    end: Optional[str]
    geometries: list[FeatureModel] = field(default_factory=list)
    geometry_json: Optional[dict[str, Any]] = None
    when: Optional[TimeRangeModel] = None
    types: list[EntityTypeModel] = field(default_factory=list)
    external_reference_systems: list[ExternalReferenceModel] = field(
        default_factory=list)
    references: list[Reference] = field(default_factory=list)
    files: list[File] = field(default_factory=list)
    relations: dict[str, list[Relation]] = field(default_factory=dict)

    def to_json(self, *, indent: Optional[int] = 2) -> str:
        """Serialize the model to camelCase JSON for the frontend."""
        data_dict = asdict(self)
        camel_case_data = dict_to_camel_case(data_dict)
        return json.dumps(camel_case_data, indent=indent, ensure_ascii=False)

    @staticmethod
    def parse_geometries(
            geometry_data: Any,
            system_class: str) -> list["FeatureModel"]:

        if not geometry_data:
            return []

        def parse_single(data: dict[str, Any]) -> "FeatureModel":
            geometry_model = GeometryModel(
                type=data['geometry']["type"],
                coordinates=data["geometry"]["coordinates"])
            property_model = PropertyModel(
                location_id=data["properties"]["locationId"],
                entity_id=data["properties"]["entityId"],
                title=data["properties"]["title"],
                description=data["properties"]["description"],
                shape_type=data["properties"]["shapeType"],
                system_class=system_class)
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
    def parse_time_range(when: dict[str, Any]) -> Optional[TimeRangeModel]:
        if not when:
            return None
        return TimeRangeModel(
            start=TimePointModel(**when.get("start", {}))
            if when.get("start") else None,
            end=TimePointModel(**when.get("end", {}))
            if when.get("end") else None)

    @staticmethod
    def parse_types(
            types_data: list[dict[str, Any]]) -> list[EntityTypeModel]:
        types = []
        for type_ in types_data:
            raw_hierarchy = type_.get("typeHierarchy")
            hierarchy_dicts: list[dict[str, str]] = (
                raw_hierarchy if isinstance(raw_hierarchy, list) else [])
            hierarchy = [
                TypeHierarchyEntry(**th)
                for th in hierarchy_dicts if isinstance(th, dict)]
            id_str = str(type_["id"])
            id_ = int(id_str) if id_str.isdigit() else 0
            raw_desc = type_.get("descriptions")
            raw_val = type_.get("value")
            raw_unit = type_.get("unit")
            types.append(EntityTypeModel(
                id=id_,
                title=str(type_.get("title") or ""),
                descriptions=str(raw_desc) if raw_desc is not None else None,
                is_standard=bool(type_.get("isStandard")),
                type_hierarchy=hierarchy,
                value=str(raw_val) if raw_val is not None else None,
                unit=str(raw_unit) if raw_unit is not None else None,
                division=get_divisions(id_, hierarchy_dicts)))
        return types

    @staticmethod
    def parse_relations(
            raw_relations: dict[str, Any]) -> dict[str, list[Relation]]:
        grouped_relations: dict[str, list[Relation]] = {}
        for system_class, relation_list in raw_relations.items():
            relations = []
            for rel in relation_list:
                rel_geometries = PresentationView.parse_geometries(
                    rel.get("geometries"),
                    system_class)
                time_range = PresentationView.parse_time_range(
                    rel.get("when") or {})
                rel_types = []

                standard_type = rel.get("standardType")
                if isinstance(standard_type, dict):
                    rel_types.append(EntityTypeModel(
                        id=int(standard_type.get("id", 0)),
                        title=str(standard_type.get("title") or ""),
                        descriptions=None,
                        is_standard=True,
                        type_hierarchy=[],
                        value=None,
                        unit=None,
                        division=None))

                relation = Relation(
                    id=int(rel["id"]),
                    name=str(rel.get("title") or ""),
                    system_class=str(rel.get("systemClass") or system_class),
                    relation_types=rel.get("relationTypes"),
                    description=get_description_translated(
                        rel.get("description") or ""),
                    aliases=rel.get("aliases", []),
                    time_range=time_range,
                    geometries=rel_geometries,
                    geometry_json=rel.get("geometries"),
                    types=rel_types)
                relations.append(relation)

            if relations:
                grouped_relations[system_class] = relations

        return grouped_relations

    @staticmethod
    def parse_file(raw_file: list[dict[str, Any]]) -> list[File]:
        files = []
        for f in raw_file:
            if not f.get("publicShareable") or not f.get("license"):
                continue
            iiif_base = f.get('IIIFManifest')
            iiif_manifest = (
                f"{iiif_base}?url={url_for('index', _external=True)}entity/"
                if iiif_base else None)
            mimetype = f.get("mimetype")
            files.append(File(
                id=int(f.get("id") or 0),
                title=str(f.get("title") or ""),
                license=f.get("license"),
                creator=f.get("creator"),
                license_holder=f.get("licenseHolder"),
                public=bool(f.get("publicShareable")),
                url=f.get("url"),
                mime_type=mimetype,
                iiif_manifest=iiif_manifest,
                iiif_base_path=f.get("IIIFBasePath"),
                overlay=f.get('overlay'),
                from_super_entity=bool(f.get('fromSuperEntity')),
                main_image=f.get('mainImage'),
                render_type=get_render_type(
                    str(mimetype) if mimetype is not None else "")))
        return files

    @classmethod
    @cache.memoize()
    def from_api(cls, entity_id: int) -> 'PresentationView':
        response = requests.get(
            f"{app.config['API_URL']}entity_presentation_view/{entity_id}",
            params={
                'place_hierarchy': 'true',
                'remove_empty_values': 'true',
                'centroid': 'true',
                'map_overlay': 'true'},
            headers=g.api_headers,
            proxies=PROXIES,
            timeout=60)
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

        view = cls(
            id=data["id"],
            system_class=data.get("systemClass", ""),
            view_class=data.get("viewClass", ""),
            title=data.get("title", ""),
            description=get_description_translated(
                data.get("description", "")),
            aliases=data.get("aliases", []),
            geometries=cls.parse_geometries(
                data.get("geometries", {}),
                data.get("systemClass", "")),
            geometry_json=data.get("geometries", {}),
            when=when_data,
            types=cls.parse_types(data.get("types", [])),
            external_reference_systems=[
                ExternalReferenceModel.from_dict(er)
                for er in data.get("externalReferenceSystems", [])
                if isinstance(er, dict)],
            references=[
                Reference.from_dict(ref)
                for ref in PresentationView.merge_references(
                    data.get("references", []))
                if isinstance(ref, dict)],
            files=cls.parse_file(data.get('files', [])),
            relations=cls.parse_relations(data.get("relations", {})),
            start=start_date,
            end=end_date)
        record_entity_cached(entity_id)
        return view

    @staticmethod
    def merge_references(
            references: list[dict[str, Any]]) -> list[dict[str, Any]]:
        merged = {}
        for ref in references:
            rid = ref["id"]
            if rid not in merged:
                merged[rid] = ref.copy()
            else:
                existing_pages = merged[rid].get("pages", "")
                new_pages = ref.get("pages", "")
                pages_set = {
                    p.strip()
                    for p in (existing_pages + "," + new_pages).split(",")
                    if p.strip()}
                merged[rid]["pages"] = ", ".join(sorted(
                    pages_set,
                    key=lambda x:
                    (not x.isdigit(), int(x) if x.isdigit() else x)))
        return list(merged.values())
