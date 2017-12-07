from django.urls import path, re_path
from django.contrib import admin
from django.views.generic.base import TemplateView
import os

from . import api
from . import leaflet
from .settings import SIM_PARAMS, DATA_PARAMS
from .settings import FILE_SECTIONS#, PLUGINS, PATH_PLUGINS

from . import views


def url_params(base, params):
    '''Create url string for django API routines'''
    for p in params:
        base += '<str:{}>/'.format(p)
    return base


def get_plugin_url(path_plugins, plugin_name):
    '''Add url objects for each plugin to a list of url patterns'''
    import importlib.util

    # Concatenate path to plugin .py views file
    plugin_path = os.path.join(path_plugins, plugin_name,
                               '{}.py'.format(plugin_name))

    # Load plugin views file
    spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Concatenate plugin URL
    url_base = '^{}/'.format(plugin_name)
    if module.API:
        plugin_url = url_params(url_base, SIM_PARAMS)
    else:
        plugin_url = url_base

    # Load view, make static view of template if no `module.view()`
    try:
        view = module.view
    except:
        template_name = '{}/{}.html'.format(plugin_name, plugin_name)
        view = TemplateView.as_view(template_name=template_name)

    return path(plugin_url, view)


# Generate URL regex strings from with URL base and iterated parameter lists
map_url       = url_params('map/', SIM_PARAMS)
data_url      = url_params('api/data/', SIM_PARAMS + DATA_PARAMS)
grid_url      = url_params('api/grid/', SIM_PARAMS + [DATA_PARAMS[0]])
calendar_url  = url_params('api/calendar/', SIM_PARAMS)

urlpatterns = [
    # Static URLs
    path('', views.select, name='select'),

    # Dynamic pages
    path(map_url, leaflet.view_map, {'sim_params':SIM_PARAMS}),

    # API URLs
    path(data_url, api.data, {'all_params': SIM_PARAMS + DATA_PARAMS}),
    path(grid_url, api.general, {'name': 'grid.geo',
                                'ext': '.json',
                                'sim_params': SIM_PARAMS + [DATA_PARAMS[0]],
                                }),
    path(calendar_url, api.general, {'name': 'calendar',
                                    'ext': '.json',
                                    'sim_params': SIM_PARAMS,
                                    }),
    path('api/parameters/', api.general, {'name': FILE_SECTIONS,
                                           'ext': '.yml'}
                                           ),
    ]

## Add existing plugins to `urlpatterns`
#if PLUGINS:
#    for plugin_name in PLUGINS:
#        urlpatterns += [get_plugin_url(PATH_PLUGINS, plugin_name),]
