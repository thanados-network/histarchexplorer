from collections import defaultdict
from typing import Any

from flask import render_template

from histarchexplorer import app
from histarchexplorer.api.parser import Parser
from histarchexplorer.models.entity import Entity
from histarchexplorer.models.types import Types


@app.route('/entity/<int:id_>')
def landing(id_: int) -> str:
    entities = Entity.get_linked_entities_by_properties_recursive(
        id_,
        get_parser_for_landing(id_))

    main_entity = get_main_entity(id_, entities)
    add_entity_object_to_relation(main_entity, entities)
    related_entities = get_related_entities(main_entity, entities)
    ancestor_entities = get_ancestor_entities(main_entity, entities)
    categorized_types = get_categorized_types(main_entity)
    super_entity = ancestor_entities[0] if ancestor_entities else None

    if not main_entity.geometry and super_entity and super_entity.geometry:
        main_entity.geometry = super_entity.geometry

    case_study = []
    for type_ in main_entity.types:
        if type_.root == "Case Study":
            case_study.append(type_)
    if not case_study and super_entity:
        for type_ in super_entity.types:
            if type_.root == "Case Study":
                case_study.append(type_)

    main_image = None
    images = []

    for image in main_entity.depictions:
        if image.main_image:
            main_image = image
            continue
        images.append(image)
        print(images)
    if not main_image and images:
        main_image = images[0]
        del images[0]

    total_images = len([img for img in images if not img.main_image])

    #print("System class:", main_entity.system_class)
    # print("View class:", main_entity.view_class)
    # print("type:", main_entity.types)
    # print("main_entity:", main_entity)
    #print("ANCESTOR ENTITIES:", [entity.name for entity in ancestor_entities])
    # print(subunits_dict['Feature'])

    # print(entity.view_class)
    # print("Types:", entity.types)
    # print("Begin:", entity.begin)
    # print("End:", entity.end)
    # print("Relations:", entity.relations)
    # print("Relation Class:", entity.relation_class)
    # print(main_entity.geometry)
    # print(type(super_entity))
    #print(main_entity.system_class)
    # print(subunit)
    # print("Categorized Types:", categorized_types)

   # print([rel.related_entity.name for rel in main_entity.subunits])


    return render_template(
        'landing.html',
        entity=main_entity,
        related_entities=related_entities,
        main_image=main_image,
        total_images=total_images,
        images=images,
        ancestor_entities=ancestor_entities,
        case_study=case_study,
        categorized_types=categorized_types)


def get_parser_for_landing(id_: int) -> Parser:
    simple_entity = Entity.get_entity(id_, Parser(show=['None']))
    match simple_entity.system_class:
        case 'Place' | 'Feature' | 'Stratigraphic unit':
            properties = ['P46', 'P67']
        case 'Human remains' | 'Artifact':
            properties = ['P46', 'P67', 'P52']
        case 'Source' | 'Source translation':
            properties = ['P67', 'P73', 'P128']
        case 'Event' | 'Acquisition' | 'Activity' | 'Creation' | 'Move' | \
             'Production' | 'Modification':
            properties = [
                'P67', 'P11', 'P14', 'P22', 'P23', 'P25', 'P7',
                'P26', 'P27', 'P24', 'P31', 'P25', 'P108', 'P9',
                'P134']
        case 'Bibliography' | 'Edition' | 'External reference':
            properties = ['P67']
        case 'Group' | 'Person':
            properties = [
                'OA7', 'OA8', 'OA9', 'P107', 'P74', 'P52', 'P11',
                'P14', 'P22', 'P23', 'P25']
        case _:
            properties = []
    return Parser(
        properties=properties,
        limit=0,
        format='lpx')


def add_entity_object_to_relation(
        main_entity: Entity,
        entities: list[Entity]) -> None:
    if not main_entity.relations:
        return None
    for relation in main_entity.relations:
        for relation_entity in entities:
            if int(relation_entity.id) == int(relation.relation_to_id):
                relation.related_entity = relation_entity
    return None


def get_main_entity(id_: int, entities: list[Entity]) -> Entity:
    for entity in entities:
        if entity.id == id_:
            return entity
    raise ValueError(f"Entity with id {id_} not found.")


def get_related_entities(
        main_entity: Entity,
        entities: list[Entity]) -> dict[str, dict[str, list[Entity]]]:
    related_entities: dict[str, Any] = defaultdict(lambda: defaultdict(list))
    for subunit in entities:
        if subunit.id == main_entity.id:
            continue
        match subunit.system_class:
            case 'Group' | 'Person':
                related_entities[subunit.system_class][subunit.name].append(
                    subunit)
            case _:
                if not subunit.types:
                    continue
                for type_ in subunit.types:
                    label = type_.type_hierarchy[0]['label']
                    if label in app.config['STANDARD_TYPES']:
                        related_entities[label][type_.label].append(subunit)
    return related_entities





def get_ancestor_entities(
        main_entity: Entity,
        entities: list[Entity]) -> list[Entity]:
    ancestor_entities = []
    current_entity = main_entity

    while current_entity:
        # If there is a parent, get the actual entity it points to
        if current_entity.parent:
            parent_entity = next(
                (entity for entity in entities if
                 entity.id == current_entity.parent.relation_to_id),
                None
            )
            if parent_entity:
                ancestor_entities.append(parent_entity)
                current_entity = parent_entity  # Move up to the next level
                # in hierarchy
            else:
                break  # Exit if no parent entity
        else:
            break
    ancestor_entities.reverse()
    return ancestor_entities


def get_categorized_types(main_entity: Entity) -> dict[str, Any]:
    # Types Division - Categories + Rest
    type_divisions = app.config['TYPE_DIVISIONS']
    # empty dict with each key
    categorized_types: dict[str, Any] = {
        key: [] for key in type_divisions.keys()}
    # from type_div
    categorized_types['properties'] = []  # + properties for all other

    def extract_id(identifier: str) -> str:
        return identifier.split('/')[-1]

    def is_type_in_division(
            type_item_: Types,
            division_ids_: list[
                int]) -> bool:  # check if type belongs to category
        for type_hierarchy_item in type_item_.type_hierarchy:
            hierarchy_id = extract_id(type_hierarchy_item['identifier'])
            #  print(f"Checking if {hierarchy_id} is in {division_ids_}")
            if int(hierarchy_id) in division_ids_:
                #    print(f"Yes: {hierarchy_id} is in {division_ids_}")
                return True
        return False

    for type_item in main_entity.types:
        # print(f"Processing type: {type_item.label} with ID: {type_item.id}")
        found = False
        for key, division_ids in type_divisions.items():
            if is_type_in_division(type_item, division_ids):
                #  print(f"Categorizing {type_item.label} under {key}")

                # conditionally include value and unit
                type_info = {
                    'label': type_item.label,
                    'value': getattr(type_item, 'value', None),
                    'unit': getattr(type_item, 'unit', None)}

                categorized_types[key].append(type_info)
                found = True
                break
        if not found:
            # print(
            # f"{type_item.label} does not match any division, "
            #  f"--> properties")

            categorized_types['properties'].append(type_item)
    return categorized_types
