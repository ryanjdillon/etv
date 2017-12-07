from . import env
from . import settings

def select(request):

    from collections import OrderedDict
    from django.shortcuts import render
    from django.template import RequestContext
    import os
    import yamlord

    path_json = env.get_json_path()

    # TODO check for configured data type (serve, local), then check if local
    # empty before passing this message
    if path_json is None:
        error_message = ('You need to scp JSON data from the server '
                         '(/home/git/data) and point PATH_JSON to it. The demo '
                         'JSON data has been removed from the repo.')
        return render(request, 'error.html', {'error_message': error_message})

    simulations = settings.SIMULATIONS
    for name, sim in simulations.items():
        params = list()
        for key, val in sim.items():
            params.append(val)
        simulations[name]['path'] = '/'.join(params)

    context = {'simulations': simulations,
               'sim_params': settings.SIM_PARAMS}

    return render(request, 'select.html', context)
