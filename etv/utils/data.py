
def gregorian2datetime(start_str, hours, microseconds=False):
    '''Convert hours since start time to datetime string

    Time in proleptic_gregorian, where the first time is time zero for the model
    simulation.

    Args
    ----
    start_str: str
        Timestamp string (e.g. '2015-04-12 00:00:00')
    hours: int
        Number of hours since start timestamp
    microseconds: bool
        Format output with microseconds field (Default: False)

    Returns
    -------
    calendar: str
        String formated timestamp
    '''
    import datetime

    fmt = '%Y-%m-%d %H:%M:%S'
    if microseconds:
        fmt += '.%f'

    t0 = datetime.datetime.strptime(start_str, fmt)
    delta = datetime.timedelta(hours=hours)

    return (t0 + delta).strftime(fmt)


def get_calendar(hr_times, start_str):
    from collections import OrderedDict

    calendar = OrderedDict()
    for i in range(len(hr_times)):
        calendar[str(i)] = gregorian2datetime(start_str, hr_times[i])

    return calendar


def reduce_data(data, method='avg'):
    '''Calculate a sum or average over depth layers for each time-step

    Args
    ----
    data: ndarray
        Three dimensional array of data, i.e. (depth, lon, lat)
    method: str
        Method to use for reducing data to 2D array ('avg' or 'sum')

    Returns
    -------
    data_reduce: ndarray (2d)
        Two dimensional array of data, i.e. (lon, lat)
    '''
    import numpy as np

    data_reduce = np.sum(data, axis=0).ravel()

    if method is 'avg':
        data_reduce = data_reduce / data.shape[0]

    return data_reduce


def compare_bounds(data, vmin, vmax, p_lo=5, p_hi=95):
    '''Find maximum and minimum values for given percentiles

    Args
    ----
    data: ndarray
        Multidimensional data array
    vmin: float
        Minimum value previously encountered in data
    vmax: float
        Maximum value previously encountered in data
    p_lo: float
        The lower percentile bound for calculating the minimum value
    p_hi: float
        The upper percentile bound for calculating the maximum value

    Returns
    -------
    vmin: float
        Minimum value encountered including the passed data
    vmax: float
        Maximum value encountered including the passed data
    '''
    import numpy as np

    with np.warnings.catch_warnings():
        msg = r'All-NaN (slice|axis) encountered'
        np.warnings.filterwarnings('ignore', msg)
        vmin = np.nanmin([np.nanpercentile(data, p_lo), vmin])
        vmax = np.nanmin([np.nanpercentile(data, p_hi), vmax])
    return vmin, vmax


def save_layer(filepath, data):
    '''Convert data to list for JSON serialization, then write JSON

    Masked values are replaced with `None`, which are converted to `null`
    in json and javascript. The numpy array must be converted to a list for
    json serialization.

    Args
    ----
    filepath: str
        Path to file to which JSON data will be written
    data: ndarray (2D)
        Two dimensional data array
    '''
    from collections import OrderedDict
    import json
    import numpy as np

    mask = np.isnan(data)
    data = data.astype(object)
    data[mask] = None
    data = data.tolist()

    jdata = OrderedDict(tuple([(i, v) for i, v in enumerate(data)]))
    json.dump(jdata, open(filepath, 'w'), sort_keys=True)

    return None


def geojson_grid_cell_polygons(lons_mesh, lats_mesh):
    '''Create a GeoJSON Feature collection of grid cells

    Args
    ----
    lons_mesh: ndarray
        Meshed longitues at the center of grid cells
    lats_mesh: ndarray
        Meshed latiitues at the center of grid cells
    '''
    from collections import OrderedDict

    from .geo import get_psi_coords

    lons_psi, lats_psi = get_psi_coords(lons_mesh, lats_mesh)

    cells = OrderedDict()
    cells['type'] = 'FeatureCollection'
    cells['features'] = list()

    for i in range(lats_mesh.shape[0]):
        for j in range(lons_mesh.shape[1]):
             cell = OrderedDict()
             cell['type'] = 'Feature'
             cell['id'] = (i*(lons_mesh.shape[1]))+j
             cell['geometry'] = OrderedDict()
             cell['geometry']['type'] = 'Polygon'

             # Coordinates require an additional list layer for GeoJSON
             # Polygons must be constructed counter-clockwise in GeoJSON
             coords = [[lons_psi[i,j],     lats_psi[i,j]],     # Top left
                       [lons_psi[i,j+1],   lats_psi[i,j+1]],   # Bottom left
                       [lons_psi[i+1,j+1], lats_psi[i+1,j+1]], # Bottom right
                       [lons_psi[i+1,j],   lats_psi[i+1,j]],   # Top right
                       [lons_psi[i,j],     lats_psi[i,j]]]     # Back to Top Left

             cell['geometry']['coordinates'] = [coords]

             cells['features'].append(cell)

    return cells
