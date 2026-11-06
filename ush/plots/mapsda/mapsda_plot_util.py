import sys
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

def get_obs_subplot_title(obtype, use_monthly_mean):
    """ Get title for observations subplot.

            Args:
                obtype           - string of the reference
                                   observation type used
                use_monthly_mean - string of using monthly mean
                                   data (YES) or monthly climo
                                   data (NO)
    """
    if obtype == 'clwp':
        obs_subplot_title = 'UWisc 1988-2007 CLWP'
    elif obtype == 'nvap':
        obs_subplot_title = 'NVAP 1988-1995'
    elif obtype == 'rad_isccp':
        obs_subplot_title = 'ISCCP 1985-1993'
    elif obtype == 'rad_srb2':
        obs_subplot_title = 'SRB2 1985-1993'
    elif obtype == 'gpcp':
        if use_monthly_mean == 'YES':
            obs_subplot_title = 'GPCP'
        else:
            obs_subplot_title = 'GPCP Climo.'
    elif obtype == 'ghcn_cams':
        if use_monthly_mean == 'YES':
            obs_subplot_title = 'GHCN_CAMS'
        else:
            obs_subplot_title = 'GHCN_CAMS Climo.'
    elif obtype == 'ceres':
        if use_monthly_mean == 'YES':
            obs_subplot_title = 'CERES'
        else:
            obs_subplot_title = 'CERES Climo.'
    return obs_subplot_title

def calculate_area_average(var_data, lat, lon, lat_min, lat_max,
                           lon_min, lon_max):
    """! Calculate area average of dataset,
         weighting in the latitude dimension by the difference
         between the sines of the latitude at the northern and
         southern edges of the grid box. Trying to mimic
         GrADS function aave.

             Args:
                 var_data     - array of variable values
                 lat          - array of latitude values
                 lon          - array of longitude values
                 lat_max      - float of maximum latitude
                                to include in averaging
                 lat_min      - float of minimum latitude
                                to include in averaging
                 lon_max      - float of maximum longitude
                                to include in averaging
                 lon_min      - float of minimum longitude
                                to include in averaging

             Returns:
                 area_average - float of area average
    """
    dlat = np.diff(lat)[0]
    dlon = np.diff(lon)[0]
    mvar_data = np.ma.masked_invalid(var_data)
    weightsum = 0
    arraysum = 0
    for y in range(len(lat)):
        lat_mid = lat[y]
        if lat_mid == -90 or lat_mid == 90:
           weight1 = 0
        elif lat_mid < lat_min or lat_mid > lat_max:
           weight1 = 0
        else:
           lat_high = lat_mid + dlat
           if lat_high < -90:
               lat_high = -90
           if lat_high < lat_min:
               lat_high = lat_min
           if lat_high > 90:
               lat_high = 90
           if lat_high > lat_max:
               lat_high = lat_max
           lat_low = lat_mid - dlat
           if lat_low < -90:
               lat_low = -90
           if lat_low < lat_min:
               lat_low = lat_min
           if lat_low > 90:
               lat_low = 90
           if lat_low > lat_max:
               lat_low = lat_max
           lat_gridbox_top = (lat_mid + lat_high)/2.
           lat_gridbox_bottom = (lat_mid + lat_low)/2.
           weight1 = (
                np.sin(np.deg2rad(lat_gridbox_top))
                - np.sin(np.deg2rad(lat_gridbox_bottom))
           )
        for x in range(len(lon)):
            if lon[x] < lon_min or lon[x] > lon_max:
                weight2 = 0
            else:
                weight2 = dlon
            if np.ma.is_masked(mvar_data[y,x]):
                arraysum = arraysum
                weightsum = weightsum
            else:
                arraysum = arraysum + (mvar_data[y,x] * (weight1 * weight2))
                weightsum = weightsum + (weight1 * weight2)
    if arraysum == 0 and weightsum == 0:
        aa_avg = np.nan
    else:
        aa_avg = arraysum/weightsum
    return aa_avg

def get_mapsda_plot_settings(var_name, var_level):
    """! Get plot settings specific for variable name and level

             Args:
                 var_name  - string of variable GRIB name
                 var_level - string of the variable level

             Returns:

    """
    # Define GRIB level type
    if var_level[-3:] == 'hPa':
        var_GRIB_lvl_typ = '100'
        formal_var_level = var_level
    elif 'sfc' in var_level:
        var_GRIB_lvl_typ = '1'
        formal_var_level = 'Surface'
        var_level.replace('sigma', '')+' Sigma Level'
    elif 'msl' in var_level:
        var_GRIB_lvl_typ = '102'
        formal_var_level = 'Mean Sea Level Pressure'
    if '_' in var_level:
        if 'range' in var_level.split('_')[1]:
            formal_var_time_range = (', '+var_level.split('_')[1] \
                                     .replace('range','')+' range')
        elif 'avg' in var_level.split('_')[1]:
            formal_var_time_range = (', '+var_level.split('_')[1] \
                                     .replace('avg','')+' average')
        elif 'accum' in var_level.split('_')[1]:
            formal_var_time_range = (', '+var_level.split('_')[1] \
                                     .replace('accum','')+' accumulation')
    else: #instanteous
        formal_var_time_range = ''
    # Get settings
    if var_name == 'HGT': #geopotential height (gpm)
        formal_var_name = 'Geopotential Height'
        cmap = plt.cm.cubehelix_r
        if var_GRIB_lvl_typ == '100': #isobaric/pressure levels (hPa)
            levels = np.nan
            levels_diff = np.array([-120,-80,-40,-20,-10,0,10,20,40,80,120])
            var_scale = 1
            var_units = 'gpm'
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            sys.exit(1)
    elif var_name == 'MSLET': #mean sea-level pressure (NAM reduction) (Pa)
        formal_var_name = 'Mean Sea Level Pressure (NAM Reduction)'
        cmap = plt.cm.rainbow
        if var_GRIB_lvl_typ == '102': #mean sea level
            levels = np.array(
                [960,965,970,975,980,985,990,995,1000,1005,1010,1015,1020]
            )
            levels_diff = np.array([-10,-5,-4,-3,-2,-1,0,1,2,3,4,5,10])
            var_scale = 0.01
            var_units = 'hPa'
    elif var_name == 'PRES': #pressure (Pa)
        formal_var_name = 'Pressure'
        cmap = plt.cm.Spectral_r
        if var_GRIB_lvl_typ == '1': #surface
            levels = np.array(
                [500,550,600,650,700,750,800,850,900,950,1000,1010]
            )
            levels_diff = np.array([-10,-5,-4,-3,-2,-1,0,1,2,3,4,5,10])
            var_scale = 0.01
            var_units = 'hPa'
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            sys.exit(1)
    elif var_name == 'O3MR': #ozone mixing ratio (kg kg-1)
        formal_var_name = 'Ozone Mixing Ratio'
        cmap = plt.cm.YlGnBu
        if var_GRIB_lvl_typ == '100': #isobaric/pressure levels (hPa)
            levels = np.nan
            levels_diff = np.array(
                [-2,-1,-0.75,-0.5,-0.25,0,0.25,0.5,0.75,1,2]
            )
            var_scale = 1000000
            var_units = 'ppmg'
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            sys.exit(1)
    elif var_name == 'PRMSL': #pressure reduced to MSL (Pa)
        formal_var_name = 'Pressure Reduced to MSL'
        cmap = plt.cm.rainbow
        if var_GRIB_lvl_typ == '102': #mean sea level
            levels = np.array(
                [960,965,970,975,980,985,990,995,1000,1005,1010,1015,1020]
            )
            levels_diff = np.array([-10,-5,-4,-3,-2,-1,0,1,2,3,4,5,10])
            var_scale = 0.01
            var_units = 'hPa'
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            sys.exit(1)
    elif var_name == 'RH': #relative humidity (%)
        formal_var_name = 'Relative Humidity'
        cmap = plt.cm.Greens
        if var_GRIB_lvl_typ == '100': #isobaric/pressure levels (hPa)
            levels = np.nan
            levels_diff = np.array([-20,-15,-10,-5,-2,0,2,5,10,15,20])
            var_scale = 1
            var_units = '%'
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            sys.exit(1)
    elif var_name == 'TMP': #temperature (K)
        formal_var_name = 'Temperature'
        cmap = plt.cm.rainbow
        if var_GRIB_lvl_typ == '1': #surface
            levels = np.array(
                [240,245,250,255,260,265,270,275,280,285,290,295,300]
            )
            levels_diff = np.array([-4,-3,-2,-1,-0.5,0,0.5,1,2,3,4])
            var_scale = 1
            var_units = 'K'
        elif var_GRIB_lvl_typ == '100': #isobaric/pressure levels (hPa)
            levels = np.nan
            levels_diff = np.array([-4,-3,-2,-1,-0.5,0,0.5,1,2,3,4])
            var_scale = 1
            var_units = 'K'
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            sys.exit(1)
    elif var_name == 'UGRD': #zonal wind (m s-1)
        formal_var_name = 'Zonal Wind'
        cmap = plt.cm.PRGn
        if var_GRIB_lvl_typ == '100': #isobaric/pressure levels (hPa)
            levels = np.array([-30,-20,-10,-5,-2,-1,1,2,5,10,20,30])
            levels_diff = np.array([-5,-3,-2,-1,-0.5,0,0.5,1,2,3,5])
            var_scale = 1
            var_units = 'm 'r'$\mathregular{s^{-1}}$'''
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            sys.exit(1)
    elif var_name == 'VGRD': #meridional wind (m s-1)
        formal_var_name = 'Meridional Wind'
        cmap = plt.cm.PRGn
        if var_GRIB_lvl_typ == '100': #isobaric/pressure levels (hPa)
            levels = np.array([-30,-20,-10,-5,-2,-1,1,2,5,10,20,30])
            levels_diff = np.array([-3,-2,-1,-0.5,-0.25,0,0.25,0.5,1,2,3])
            var_scale = 1
            var_units = 'm 'r'$\mathregular{s^{-1}}$'''
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            sys.exit(1)
    else:
        print("ERROR: cannot find plot settings for "+var_name)
        sys.exit(1)
    if var_name in ['PRMSL', 'MSLET', 'HPBL']:
        var_info_title = (
            formal_var_name+' ('+var_units+')'+formal_var_time_range
        )
    else:
        var_info_title = (
            formal_var_level+' '+formal_var_name+' ('+var_units+')'
            +formal_var_time_range
        )
    return (var_info_title, levels, levels_diff, cmap, var_scale,
            formal_var_name)

def get_clevels(data, spacing):
    """! Get contour levels for plotting differences
         or bias (centered on 0)

              Args:
                  data    - array of data to be contoured
                  spacing - float for spacing for power function,
                            value of 1.0 gives evenly spaced
                            contour intervals
              Returns:
                  clevels - array of contour levels
    """
    if np.abs(np.nanmin(data)) > np.nanmax(data):
       cmax = np.abs(np.nanmin(data))
       cmin = np.nanmin(data)
    else:
       cmax = np.nanmax(data)
       cmin = -1 * np.nanmax(data)
    if cmax > 100:
        cmax = cmax - (cmax * 0.2)
        cmin = cmin + (cmin * 0.2)
    elif cmax > 10:
        cmax = cmax - (cmax * 0.1)
        cmin = cmin + (cmin * 0.1)
    if cmax > 1:
       cmin = round(cmin-1,0)
       cmax = round(cmax+1,0)
    else:
       cmin = round(cmin-0.1,1)
       cmax = round(cmax+0.1,1)
    steps = 6
    span = cmax
    dx = 1.0 / (steps-1)
    pos = np.array([0 + (i*dx)**spacing*span for i in range(steps)],
                   dtype=float)
    neg = np.array(pos[1:], dtype=float) * -1
    clevels = np.append(neg[::-1], pos)
    return clevels
