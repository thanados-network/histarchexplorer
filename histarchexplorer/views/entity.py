import json

from histarchexplorer import app
from flask import render_template, abort, jsonify

from histarchexplorer.api.parser import Parser
from histarchexplorer.models.entity import Entity

sidebarelements = app.config['SIDEBAR_OPTIONS']
valid_routes = {item['route'] for item in sidebarelements}


@app.route('/entity/<int:id_>/')
@app.route('/entity/<int:id_>/<tab_name>')
def entity(id_: int, tab_name="overview") -> str:
    if tab_name not in valid_routes:
        abort(404)

    return render_template('entity.html', sidebarelements=sidebarelements, page_name="landing", active_tab=tab_name,
                           entity_id=id_)


@app.route('/getentity/<int:id_>/<tab_name>')
def getentity(id_: int, tab_name=None, json_serializable=None) -> str:
    data={}


    def get_entity():
        entity = Entity.get_entity(id_, Parser())
        return {'entity': json.dumps(entity.to_serializable(), ensure_ascii=False, indent=4)}

    def get_map_data():
        entities = Entity.get_linked_entities_by_properties_recursive(
            id_, Parser(show='geometry', properties='P46'))
        features = {'type': 'FeatureCollection', 'features': []}
        for ent in entities:
            if ent.system_class in ['Feature', 'Place', 'Stratigraphic unit', 'Human remains', 'Artifact'] and ent.geometry:
                features['features'].append(
                    {'type': 'Feature', 'geometry': ent.geometry, 'properties': {'id': ent.id, 'label': ent.name, 'class': ent.system_class}})
        return features

    def get_file_data():
        file_data = {}
        return file_data

    if tab_name == 'map':
        data['spatial'] = get_map_data()
        print(len(data['spatial']))
        if len(data['spatial']['features']) == 0:
            print('404')
            abort(404)

    if tab_name == 'overview':
        data = get_entity()

    if tab_name not in valid_routes:
        print('notvalid')
        abort(404)

    return render_template(f'tabs/{tab_name}.html', data=json.dumps(data))
