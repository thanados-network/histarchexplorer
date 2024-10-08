from collections import defaultdict

from flask import render_template

from histarchexplorer import app
from histarchexplorer.api.parser import Parser
from histarchexplorer.models.entity import Entity


@app.route('/entity/<int:id_>')
def landing(id_: int) -> str:
    parser = Parser(
        properties=['P46', 'P67'],
        limit=0,
        format='lpx')

    entities = Entity.get_linked_entities_by_properties_recursive(
        id_,
        parser)

    subunits_dict = defaultdict(list)
    feature_dict = defaultdict(list)
    strati_dict = defaultdict(list)
    artifact_dict = defaultdict(list)
    remains_dict = defaultdict(list)
    places_dict = defaultdict(list)

    main_entity = None
    for entity in entities:
        if entity.id == id_:
            main_entity = entity


    for relation in main_entity.relations.values():
        for rel in relation:
            for relation_entity in entities:
                if int(relation_entity.id) == int(rel.relation_to_id):
                    rel.related_entity = relation_entity


    if main_entity.system_class.lower() in [
        "artifact",
        "feature",
        "human remains",
        "place",
        "stratigraphic unit"]:

        for subunit in entities:
            if not subunit.types:
                continue
            for type_ in subunit.types:
                subunits_dict[type_.type_hierarchy[0]['label']].append(subunit)

                match type_.type_hierarchy[0]['label']:
                    case 'Feature':
                        feature_dict[type_.label].append(subunit)
                    case 'Stratigraphic unit':
                        strati_dict[type_.label].append(subunit)
                    case 'Artifact':
                        artifact_dict[type_.label].append(subunit)
                    case 'Human remains':
                        remains_dict[type_.label].append(subunit)
                    case 'Place':
                        places_dict[type_.label].append(subunit)

        # print(subunits_dict['Feature'])

    # print(entity.view_class)
    # print("Types:", entity.types)
    # print("Begin:", entity.begin)
    # print("End:", entity.end)
    # print("Relations:", entity.relations)
    # print("Relation Class:", entity.relation_class)
    print(main_entity.geometry)

    # Description 2/3 column or 1/3 column
    if main_entity.description and len(main_entity.description) > 500:
        main_entity.description_class = "item-middle"
    else:
        main_entity.description_class = "item"
    return render_template(
        'landing.html',
        entity=main_entity,
        view_class=main_entity.view_class,
        relations=main_entity.relations,
        subunits=subunits_dict or {},
        features=feature_dict or {},
        strati=strati_dict or {},
        artifact=artifact_dict or {},
        remains=remains_dict or {},
        places=places_dict or {}
    )
