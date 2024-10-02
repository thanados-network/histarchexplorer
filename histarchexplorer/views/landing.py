from collections import defaultdict

from flask import render_template

from histarchexplorer import app
from histarchexplorer.api.parser import Parser
from histarchexplorer.models.entity import Entity


@app.route('/entity/<id_>')
def landing(id_: int) -> str:
    parser = Parser()
    entity = Entity.get_entity(id_, parser)
    linked_entities = Entity.get_entities_linked_to_entity(id_, parser)
    for relation in entity.relations.values():
        for r in relation:
            for e_ in linked_entities:
                if int(e_.id) == int(r.relation_to_id):
                    r.set_related_entity(e_)

    subunits_dict = defaultdict(list)
    feature_dict = defaultdict(list)
    strati_dict = defaultdict(list)
    artifact_dict = defaultdict(list)
    remains_dict = defaultdict(list)
    if entity.system_class.lower() in [
        "artifact",
        "feature",
        "human_remains",
        "place",
        "stratigraphic_unit"]:
        subunit_parser = Parser(
            properties=['P46'],
            limit=0,
            format='lpx',
            show=['types'])
        subunits = Entity.get_linked_entities_by_properties_recursive(
            entity.id, subunit_parser)

        for subunit in subunits:
            for type_ in subunit.types:
                subunits_dict[type_.type_hierarchy[0]['label']].append(subunit)
                #  print(type_.type_hierarchy[0]['label'])
                match type_.type_hierarchy[0]['label']:
                    case 'Feature':
                        feature_dict[type_.label].append(subunit)
                    case 'Stratigraphic unit':
                        strati_dict[type_.label].append(subunit)
                    case 'Artifact':
                        artifact_dict[type_.label].append(subunit)
                    case 'Human remains':
                        remains_dict[type_.label].append(subunit)

        # print(subunits_dict['Feature'])

    # print(entity.view_class)
    # print("Types:", entity.types)
    # print("Begin:", entity.begin)
    # print("End:", entity.end)
    # print("Relations:", entity.relations)
    # print("Relation Class:", entity.relation_class)
    print(entity.geometry)

    if entity.depictions is None:
        entity.depictions = []

    # Description 2/3 column or 1/3 column
    if entity.description and len(entity.description) > 500:
        entity.description_class = "item-middle"
    else:
        entity.description_class = "item"

    return render_template(
        'landing.html',
        entity=entity,
        view_class=entity.view_class,
        relations=entity.relations,
        subunits=subunits_dict or {},
        features=feature_dict or {},
        strati=strati_dict or {},
        artifact=artifact_dict or {},
        remains=remains_dict or {}
    )
