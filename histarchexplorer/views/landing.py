from flask import render_template, g

from histarchexplorer import app
from histarchexplorer.api.parser import Parser
from histarchexplorer.models.entity import Entity


@app.route('/entity/<id_>')
def landing(id_: int) -> str:
    parser = Parser()
    entity = Entity.get_entity(id_, parser)

    print("Types:", entity.types)
    #print("Begin:", entity.begin)
    #print("End:", entity.end)
    print("Relations:", entity.relations)
    print("Relation Class:", entity.relation_class)


    if entity.depictions is None:
        entity.depictions = []


    return render_template('landing.html', entity=entity, relations=entity.relations)
