
def get_psi_coords(lons, lats):
    ''' Calcuate psi points from centered grid points

    lons: ndarray (2D)
        Meshed longitudes at the center of grid cells
    lats: ndarray (2D)
        Meshed latitudes for grid

    Returns
    -------
    psi_lons: (2D)
        Meshed longitues at the corners of grid cells
    psi_lats: (2D)
        Meshed latiitues at the corners of grid cells
    '''
    import numpy as np
    import pyproj

    # Create Geod object with WGS84 ellipsoid
    g = pyproj.Geod(ellps='WGS84')

    # Get grid field dimensions
    ydim, xdim = lons.shape

    # Create empty coord arrays
    lons_psi = np.zeros((ydim+1, xdim+1))
    lats_psi = np.zeros((ydim+1, xdim+1))

    # Calculate internal points
    #--------------------------
    for j in range(ydim-1):
        for i in range(xdim-1):
            lon1 = lons[j,i]     # top left point
            lat1 = lats[j,i]
            lon2 = lons[j+1,i+1] # bottom right point
            lat2 = lats[j+1,i+1]
            # Calc distance between points, find position at half of dist
            fwd_az, bck_az, dist = g.inv(lon1,lat1,lon2,lat2)
            lon_psi, lat_psi, bck_az = g.fwd(lon1,lat1,fwd_az,dist*0.5)
            # Assign to psi interior positions
            lons_psi[j+1,i+1] = lon_psi
            lats_psi[j+1,i+1] = lat_psi

    # Caclulate external points (not corners)
    #----------------------------------------
    for j in range(ydim):
        # Left external points
        #~~~~~~~~~~~~~~~~~~~~~
        lon1 = lons_psi[j+1,2] # left inside point
        lat1 = lats_psi[j+1,2]
        lon2 = lons_psi[j+1,1] # left outside point
        lat2 = lats_psi[j+1,1]
        # Calc dist between points, find position at dist*2 from pos1
        fwd_az, bck_az, dist = g.inv(lon1,lat1,lon2,lat2)
        lon_psi, lat_psi, bck_az = g.fwd(lon1,lat1,fwd_az,dist*2.)
        lons_psi[j+1,0] = lon_psi
        lats_psi[j+1,0] = lat_psi

        # Right External points
        #~~~~~~~~~~~~~~~~~~~~~~
        lon1 = lons_psi[j+1,-3] # right inside point
        lat1 = lats_psi[j+1,-3]
        lon2 = lons_psi[j+1,-2] # right outside point
        lat2 = lats_psi[j+1,-2]
        # Calc dist between points, find position at dist*2 from pos1
        fwd_az, bck_az, dist = g.inv(lon1,lat1,lon2,lat2)
        lon_psi, lat_psi, bck_az = g.fwd(lon1,lat1,fwd_az,dist*2.)
        lons_psi[j+1,-1] = lon_psi
        lats_psi[j+1,-1] = lat_psi

    for i in range(xdim):
        # Top external points
        lon1 = lons_psi[2,i+1] # top inside point
        lat1 = lats_psi[2,i+1]
        lon2 = lons_psi[1,i+1] # top outside point
        lat2 = lats_psi[1,i+1]

        # Calc dist between points, find position at dist*2 from pos1
        fwd_az, bck_az, dist = g.inv(lon1,lat1,lon2,lat2)
        lon_psi, lat_psi, bck_az = g.fwd(lon1,lat1,fwd_az,dist*2.)
        lons_psi[0,i+1] = lon_psi
        lats_psi[0,i+1] = lat_psi

        # Bottom external points
        lon1 = lons_psi[-3,i+1] # bottom inside point
        lat1 = lats_psi[-3,i+1]
        lon2 = lons_psi[-2,i+1] # bottom outside point
        lat2 = lats_psi[-2,i+1]

        # Calc dist between points, find position at dist*2 from pos1
        fwd_az, bck_az, dist = g.inv(lon1,lat1,lon2,lat2)
        lon_psi, lat_psi, bck_az = g.fwd(lon1,lat1,fwd_az,dist*2.)
        lons_psi[-1,i+1] = lon_psi
        lats_psi[-1,i+1] = lat_psi

    # Calculate corners:

    # top left corner
    lon1 = lons_psi[2,2] # bottom right point
    lat1 = lats_psi[2,2]
    lon2 = lons_psi[1,1] # top left point
    lat2 = lats_psi[1,1]
    # Calc dist between points, find position at dist*2 from pos1
    fwd_az, bck_az, dist = g.inv(lon1,lat1,lon2,lat2)
    lon_psi, lat_psi, bck_az = g.fwd(lon1,lat1,fwd_az,dist*2.)
    lons_psi[0,0] = lon_psi
    lats_psi[0,0] = lat_psi

    # top right corner
    lon1 = lons_psi[2,-3] # bottom left point
    lat1 = lats_psi[2,-3]
    lon2 = lons_psi[1,-2] # top right point
    lat2 = lats_psi[1,-2]
    # Calc dist between points, find position at dist*2 from pos1
    fwd_az, bck_az, dist = g.inv(lon1,lat1,lon2,lat2)
    lon_psi, lat_psi, bck_az = g.fwd(lon1,lat1,fwd_az,dist*2.)
    lons_psi[0,-1] = lon_psi
    lats_psi[0,-1] = lat_psi

    # bottom left corner
    lon1 = lons_psi[-3,2] # top right point
    lat1 = lats_psi[-3,2]
    lon2 = lons_psi[-2,1] # bottom left point
    lat2 = lats_psi[-2,1]
    # Calc dist between points, find position at dist*2 from pos1
    fwd_az, bck_az, dist = g.inv(lon1,lat1,lon2,lat2)
    lon_psi, lat_psi, bck_az = g.fwd(lon1,lat1,fwd_az,dist*2.)
    lons_psi[-1,0] = lon_psi
    lats_psi[-1,0] = lat_psi

    # bottom right corner
    lon1 = lons_psi[-3,-3] # top left point
    lat1 = lats_psi[-3,-3]
    lon2 = lons_psi[-2,-2] # bottom right point
    lat2 = lats_psi[-2,-2]

    # Calc dist between points, find position at dist*2 from pos1
    fwd_az, bck_az, dist = g.inv(lon1,lat1,lon2,lat2)
    lon_psi, lat_psi, bck_az = g.fwd(lon1,lat1,fwd_az,dist*2.)
    lons_psi[-1,-1] = lon_psi
    lats_psi[-1,-1] = lat_psi

    return lons_psi, lats_psi


