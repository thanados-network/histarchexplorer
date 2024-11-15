from flask import render_template, request

from histarchexplorer import app
from histarchexplorer.api.api_access import ApiAccess
from histarchexplorer.api.parser import Parser
from histarchexplorer.models.entity import Entity


@app.route('/test')
def test() -> str:
    return render_template('test/test.html')


@app.route('/test/entity/<int:id_>')
def test_entity(id_: int) -> str:
    parser = Parser(format='lpx')
    entity = Entity.get_entity(id_, parser)
    return render_template('test/entity.html', entity=entity)


@app.route('/test/linked_entities_by_properties_recursive/<int:id_>')
def test_linked_entities_by_properties_recursive(id_: int) -> str:
    parser = Parser(
        properties=[request.args.get('properties') or ''],
        limit=0,
        format='lpx')
    entities = Entity.get_linked_entities_by_properties_recursive(id_, parser)
    return render_template('test/list_entities.html', entities=entities)


@app.route('/test/subunit/<int:id_>')
def test_subunit(id_: int) -> str:
    parser = Parser(format='lpx')
    entity = ApiAccess.get_subunits(id_, parser)
    return render_template('test/entity.html', entity=entity)


@app.route('/test/system_class/<class_>')
def test_system_class(class_: str) -> str:
    parser = Parser(limit=0, show=['none'],  sort='desc', format='lpx')
    return render_template(
        'test/list_entities.html',
        entities=Entity.get_by_system_class(class_, parser))


@app.route('/test/system_class/')
def test_system_class_count() -> str:
    parser = Parser(type_id=app.config['OPENATLAS_CASE_STUDY_IDS'])
    return render_template(
        'test/system_class_count.html',
        classes=ApiAccess.get_system_class_count(parser))
