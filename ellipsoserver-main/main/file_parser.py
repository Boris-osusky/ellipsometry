import json
import os
from . import formulas


def get_all_materials():
    materials = []
    for f in sorted(os.listdir('storage/newMaterials')):
        umin, umax = get_user_min_max_of_file(f'storage/newMaterials/{f}')
        materials.append({
            'name': f,
            'type': 'file',
            'path': f'storage/newMaterials/{f}',
            'umin': umin,
            'umax': umax
        })

    return materials


# getting json file (.json -> py)
def get_file(file_name):
    with open(file_name, 'r') as file:
        data = json.load(file)
    return data

# temporary function for getting different paths for .refX and for .dsp files
def diff_paths(file_type):

    paths = {

        'file_type': '',
        'meta_path': '',
        'fp_path': '',
        'lp_path': '',
        'inc_path': '',
        'unit_path': ''
    }

    if file_type in ['ref1', 'ref2', 'ref3', 'ref4']:
        paths['file_type'] = file_type
        paths['meta_path'] = 'metadata'
        paths['fp_path'] = 'firstPoint'
        paths['lp_path'] = 'lastPoint'
        paths['inc_path'] = 'increment'
        paths['unit_path'] = 'unit'
        return paths

    elif (file_type == 'dsp'):
        paths['file_type'] = 'dsp'
        paths['meta_path'] = 'general'
        paths['fp_path'] = 'SPmin'
        paths['lp_path'] = 'SPmax'
        paths['inc_path'] = 'SPinc'
        paths['unit_path'] = 'SPunit'
        return paths
    return None


# .json -> json in py -> important json info to py -> elipsometric model
def get_filedata(file_name):
    
    data = {}

    json_file = get_file(file_name)
    file_type = json_file['type']
    paths = diff_paths(file_type)

    data['file_type'] = paths['file_type']
    data['first_point_value'] = json_file[paths['meta_path']][paths['fp_path']]
    data['last_point_value'] = json_file[paths['meta_path']][paths['lp_path']]
    data['inc_value'] = json_file[paths['meta_path']][paths['inc_path']]
    data['unit_value'] = json_file[paths['meta_path']][paths['unit_path']]

    if file_type == 'ref1':
        data['epsRe'] = [item['epsRe'] for item in json_file['data']]
        data['epsIm'] = [item['epsIm'] for item in json_file['data']]

    if file_type == 'ref2':
        data['eV'] = [item['eV'] for item in json_file['data']]
        data['n'] = [item['n'] for item in json_file['data']]
        data['k'] = [item['k'] for item in json_file['data']]

    if file_type == 'ref3':
        data['eV'] = [item['eV'] for item in json_file['data']]
        data['epsRe'] = [item['epsRe'] for item in json_file['data']]
        data['epsIm'] = [item['epsIm'] for item in json_file['data']]

    if file_type == 'ref4':
        data['nm'] = [item['nm'] for item in json_file['data']]
        data['epsRe'] = [item['epsRe'] for item in json_file['data']]
        data['epsIm'] = [item['epsIm'] for item in json_file['data']]

    elif (file_type == 'dsp'):            
        data['formula_id'] = json_file[paths['meta_path']]['formulaID']
        param_count = json_file['parameters']['paramCount']
        parametre = {}
        for i in range(param_count):
            param_name = json_file['parameters'][f'paramName{i}']
            param_value = json_file['parameters'][f'paramValue{i}']
            parametre[f'paramName{i}'] = param_name
            parametre[f'paramValue{i}'] = param_value
        data['parameters'] = parametre
        
    return data


def get_user_min_max_of_file(filename):
    data = get_filedata(filename)

    return [formulas.eVnm(data['last_point_value']), formulas.eVnm(data['first_point_value'])]
