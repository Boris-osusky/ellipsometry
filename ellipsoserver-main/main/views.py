from . import main
from . import simulator
from .file_parser import get_all_materials
from flask import send_from_directory
from flask import render_template, request



@main.route("/")
def index():
    return render_template('index.html', materials=get_all_materials())


@main.route("/image", methods=['POST'])
def image():
    params = validate_params(request.get_json(force=True))
    data = simulator.get_simulation_image_b64(params['materials'][::-1], params['uangle'], params['ustart'], params['uend'], params['uinc'], params['unit'], params['functions'])
    return {'image_url': f'data:image/png;base64, {data}'}


@main.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@main.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)



def validate_params(params):
    for key in ['materials', 'uangle', 'functions']:
        if not key in params:
            raise ValueError()

    if not 'ustart' in params:
        params['ustart'] = 430

    if not 'uend' in params:
        params['uend'] = 820

    if not 'uinc' in params:
        params['uinc'] = 2

    if not 'unit' in params:
        params['unit'] = 'nm'

    if params['unit'].lower() not in ['nm', 'ev']:
        raise ValueError()

    if not all(isinstance(params[key], (int, float)) for key in ['ustart', 'uend', 'uinc']):
        raise ValueError()

    if params['ustart'] >= params['uend']:
        raise ValueError()
    
    if len(params['materials']) < 2:
        raise ValueError()

    return params
