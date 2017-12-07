
def save_json(path_sim, dataset, start_str, sections, lon_min, lon_max,
        lat_min, lat_max, n_timesteps=None, n_depths=None):
    '''Process and save JSON files for specified data

    Args
    ----
    path_sim: str
        Path of simulation with a subdirectory for each simulation parameters
    dataset: netCDF4.Dataset
        Handler object for a netCDF4 Dataset
    start_str: str
        Timestamp string (e.g. '2015-04-12 00:00:00')
    sections: OrderedDict
        Dictionary of attributes for sections and their parameters
    lon_min: float
        Minimum longitude for slice of data to process
    lon_mas: float
        Maximum longitude for slice of data to process
    lat_min: float
        Minimum latitude for slice of data to process
    lat_mas: float
        Maximum latitude for slice of data to process
    n_timesteps: int
        Number of timesteps to process from start of dataset
    n_depths: int
        Number of depth layers to process for each timestep
    '''
    from collections import OrderedDict
    import json
    import numpy as np
    import os
    from os.path import join
    from tqdm import tqdm

    from .data import get_calendar, reduce_data, compare_bounds, save_layer
    from .data import geojson_grid_cell_polygons

    def get_var(dataset, key, val_min, val_max):
        '''Return a dataset and a mask to constrain it by the given bounds'''
        var = dataset.variables[key][:]
        mask = (var > val_min) & (var < val_max)
        return var, mask

    # Get dimensions of dataset variables for iterations and output creation
    if not n_timesteps:
        n_timesteps = dataset.variables['time'].size
    if not n_depths:
        n_depths = dataset.variables['depth'].size

    # Create the directory stucture for the simulation
    os.makedirs(path_sim, exist_ok=True)

    # Generate timestamps from hour data and save to `calendar.json`
    hr_times = dataset.variables['time'][:n_timesteps]
    calendar = get_calendar(hr_times, start_str)
    file_calendar = join(path_sim, 'calendar.json')
    json.dump(calendar, open(file_calendar, 'w'), sort_keys=True)

    # For iteration of sections, parameters, timesteps, and depths, we'll use
    # the `tqdm` for getting a status bar and ETA

    # Iterate sections
    bounds = OrderedDict()
    jdata = OrderedDict()
    for s in tqdm(sections.keys(), desc= '  sections'):

        path_section = join(path_sim, s)
        os.makedirs(path_section, exist_ok=True)

        # Extract longitude and latitudes for grid cell polygon creation
        lons, lon_mask = get_var(dataset, 'lon', lon_min, lon_max)
        lats, lat_mask = get_var(dataset, 'lat', lat_min, lat_max)
        lons_mesh, lats_mesh = np.meshgrid(lons[lon_mask], lats[lat_mask])

        # Create GeoJSON FeatureCollectino of grid cell polygons
        cells = geojson_grid_cell_polygons(lons_mesh, lats_mesh)
        json.dump(cells, open(join(path_section, 'grid.geo.json'), 'w'))

        # Iterate parameters
        for p in tqdm(sections[s]['params'].keys(), desc='parameters'):
            vmin = np.nan
            vmax = np.nan

            # Iterate time-steps
            for t in tqdm(range(n_timesteps), desc='time-steps'):

                # Make output path for data, under the simulation's path
                fmt_t = 'time{:04.0f}'
                path_data = join(path_section, p, fmt_t.format(t))
                os.makedirs(path_data, exist_ok=True)

                if 'depth' in dataset[p].coordinates:
                    # Calculate reduction (i.e. sum or avg) over depth layers for
                    # each time-step; Then save as JSON with reduction name
                    method = sections[s]['params'][p]['method']

                    with np.errstate(invalid='ignore'):
                        data = dataset.variables[p][t, :n_depths, lat_mask, lon_mask]
                    data_reduce = reduce_data(data, method=method)

                    filename = join(path_data, '{}.json'.format(method))
                    save_layer(filename, data_reduce)

                    # Iterate depth layers and save JSON data
                    for d in tqdm(range(n_depths), desc='    depths'):

                        # Get the whole grid's data for time `t` and depth `d`
                        # unravel to 1D array
                        with np.errstate(invalid='ignore'):
                            data = dataset.variables[p][t,d,lat_mask,lon_mask].ravel()

                        filename = join(path_data, 'layer{:02.0f}.json'.format(d))
                        save_layer(filename, data)

                        vmin, vmax = compare_bounds(data, vmin, vmax)
                else:
                    data = dataset.variables[p][t,lat_mask,lon_mask].ravel()

                    filename = join(path_data, 'layer{:02.0f}.json'.format(d))
                    save_layer(filename, data)

                    vmin, vmax = compare_bounds(data, vmin, vmax)

            # Save the extrema for each parameter
            bounds[p] = dict()
            bounds[p]['min'] = round(float(vmin),1)
            bounds[p]['max'] = round(float(vmax),1)

    return bounds


def noaa_simulations_yaml(path_json, dataset):
    '''Generate YAML configuration file for simulation parameters

    Args
    ----
    path_json: str
        Root path to processed json data
    dataset: netCDF4.Dataset
        Handler object for a netCDF4 Dataset
    '''
    from collections import OrderedDict
    import os
    import yamlord

    def slugify(s):
        import re
        '''Remove non-word, numeric chars, and replace space with underscores'''
        s = re.sub(r"[^\w\s]", '', s)
        s = re.sub(r"\s+", '_', s)
        return s

    attrs = ['title', 'institution', 'location']
    simulations = OrderedDict()
    simulations['sim1'] = OrderedDict()
    for attr in attrs:
        simulations['sim1'][attr] = slugify(dataset.getncattr(attr))

    file_yaml = os.path.join(path_json, 'simulations.yml')
    yamlord.write_yaml(simulations, file_yaml)

    return simulations


def noaa_parameters_yaml(path_json, dataset, sections, n_depths, bounds):
    '''Generate YAML configuration file for data parameters

    Args
    ----
    path_json: str
        Root path to processed json data
    dataset: netCDF4.Dataset
        Handler object for a netCDF4 Dataset
    sections: OrderedDict
        Dictionary of attributes for sections and their parameters
    n_depths: int
        Number of depth layers to process for each timestep
    bounds: OrderedDict
        Dictionary of parameters and their associated minimum and maximum
        values over the entire period of data processed
    '''
    from collections import OrderedDict
    import os
    import yamlord

    depths = dataset.variables['depth'][:n_depths]

    yml = OrderedDict()

    for s in sections.keys():
        yml[s] = OrderedDict()
        yml[s]['screen_name'] = sections[s]['screen_name']
        yml[s]['slice_title'] = sections[s]['screen_name']
        yml[s]['parameters'] = OrderedDict()

        for p in sections[s]['params'].keys():
                param = OrderedDict()
                param['unit'] = dataset.variables[p].units
                param['short_description'] = dataset.variables[p].long_name
                param['dimension_name'] = 'layer'
                param['colors'] = sections[s]['params'][p]['colors']
                param['min'] = bounds[p]['min']
                param['max'] = bounds[p]['max']

                # Store reduction type for parameter
                param['reduction'] = sections[s]['params'][p]['method']

                # Generate dimension layer ids and names
                fmt_l = '{:03.0f}'
                layers = [{i:fmt_l.format(depths[i])} for i in range(n_depths)]
                param['layers'] = layers

                # Store parameter settings to section
                yml[s]['parameters'][p] = param


    file_yaml = os.path.join(path_json, 'parameters.yml')
    yamlord.write_yaml(yml, file_yaml)

    return None


def sample_data(path_json='./', n_timesteps=3, n_depths=2):
    '''Generate sample JSON data and YAML configuration files

    NOAA HYCOM data is aggregated for use as sample data, which has modeled
    data from 2013 to present. We use the data from Region 6, but the
    following link has an overview of other areas available:
    https://goo.gl/fW27Bd

    Args
    ----
    path_json: str
        Root path to processed json data
    n_timesteps: int
        Number of timesteps to process from start of dataset
    n_depths: int
        Number of depth layers to process for each timestep

    Note
    ----
    This example is configured after inspection of the netCDF dataset being
    processed. You can do this from a Python interpreter by first loading the
    dataset and looking at the data/metadata within.

    Inspect variables available:
    datset.variables.keys()

    Inspect attributes of variable:
    dataset.variables['salinity']
    dataset.variables['salinity'].shape
    '''

    def add_dict_attrs(d, parent_key, **kwargs):
        '''Add dictionary attributes to field of new dictionary with parent key
        '''
        if parent_key not in d:
            d[parent_key] = OrderedDict()

        for key, val in sorted(kwargs.items()):
            d[parent_key][key] = val

        return d

    def add_parameter(sections, section, param, method, colors):
        '''Add a new parameter and its attributes to sections dictionary
        '''
        from collections import OrderedDict

        if section not in sections:
            sections[section] = OrderedDict()

        if 'params' not in sections[section]:
            sections[section]['params'] = OrderedDict()

        if param not in sections[section]['params']:
            sections[section]['params'][param] = OrderedDict()

        sections[section]['params'][param]['method'] = method
        sections[section]['params'][param]['colors'] = colors

        return sections

    import netCDF4
    import os
    from collections import OrderedDict

    # Load the dataset. Data isn't downloaded until it is accessed.
    print('\nLoading NOAA NCOM Alaska region OPeNDAP dataset...')
    url = ('https://ecowatch.ncddc.noaa.gov/thredds/dodsC/'
           'alaska_aggregation/'
           'Alaska_best.ncd')
    dataset = netCDF4.Dataset(url)

    # Create a dictionary of configuration values for our JSON output
    sections = OrderedDict()

    # Add attributes for each section. We only have one in this example.
    sections = add_dict_attrs(sections, 'ocean', screen_name='Ocean',
                                                 slice_title='Depth layers')

    # Add parameters to be processed, their reduction (i.e. sum or avg), and their
    # display colors for their display on the map
    salinity_colors = ['#0075B4', '#70B5DC']
    water_temp_colors = ['#f442ce', '#f44248']
    sections = add_parameter(sections, 'ocean', 'salinity', 'avg', salinity_colors)
    sections = add_parameter(sections, 'ocean', 'water_temp', 'avg', water_temp_colors)

    print('\nCreating `simulations.yml` file...')
    simulations = noaa_simulations_yaml(path_json, dataset)

    lon_min, lon_max = (233.5, 236.5)
    lat_min, lat_max = (39.5, 41.5)
    start_str = '2015-04-12 00:00:00'

    print('\nCreating JSON data...')
    path_sim = os.path.join(path_json, *simulations['sim1'].values())
    bounds = save_json(path_sim, dataset, start_str, sections, lon_min,
            lon_max, lat_min, lat_max, n_timesteps, n_depths)

    print('\n\n')
    print('\nCreating `parameters.yml` file...')
    noaa_parameters_yaml(path_json, dataset, sections, n_depths, bounds)

    return bounds
