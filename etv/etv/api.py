from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import json
import os
import yamlord

from .env import get_json_path

def data(request, all_params, **kwargs):

    file_name = os.path.join(get_json_path(),
                             *tuple(kwargs[p] for p in all_params)) + '.json'

    if os.path.isfile(file_name):
        with open(file_name, 'r') as f:
            return HttpResponse(f.read())
    else:
        # file does not exist, we return empty data dictionary
        return HttpResponse('{"data": [], "lons": [], "lats": []}')


def general(request, name, ext, sim_params='', **kwargs):

    if sim_params:
        sim_params = os.path.join(*tuple(kwargs[p] for p in sim_params))
    filepath = os.path.join(get_json_path(), sim_params, name+ext)

    if ext == '.yml':
        response = yamlord.read_yaml(filepath)
    elif ext == '.json':
        response = json.load(open(filepath, 'r'))
    else:
        raise SystemError('API reads YAML and JSON data. {}'.format(filepath))

    return HttpResponse(json.dumps(response, sort_keys=True))
