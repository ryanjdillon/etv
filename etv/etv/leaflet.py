from . import settings

def view_map(request, sim_params, **kwargs):

    from django.shortcuts import render
    import os
    import json
    from collections import OrderedDict

    simulation = OrderedDict()
    for p in settings.SIM_PARAMS:
        simulation[p] = kwargs[p]

    sections_js = json.dumps(settings.SECTIONS, sort_keys=True,
                             indent=4, separators=(',', ': '))
    sections_django = settings.SECTIONS

    # Concatenate simulations to data path
    simulation['path'] = os.path.join(*tuple(simulation.values()))

    from collections import OrderedDict
    import json

    # Retrieve user configuration for map center location and zoom level
    # Defaults centering location to "verdens beste by"
    map_config = dict()
    map_config['lon0'] = -125.3
    map_config['lat0'] = 40.5
    map_config['zoom'] = 8

    context = {
        'map_config': map_config,
        'sections_js': sections_js,
        'sections_django': sections_django,
        'simulation': simulation
        }

    return render(request, 'leaflet/map.html', context)
