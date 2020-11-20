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

def get_maps2d_plot_settings(var_name, var_level):
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
    elif 'AGL' in var_level:
        if 'hPa' in var_level:
            var_GRIB_lvl_typ = '116'
            formal_var_level = (var_level.replace('hPaAGL', '')+' hPa '
                                +'Above Ground')
        elif 'm' in var_level:
            var_GRIB_lvl_typ = '105'
            formal_var_level = (var_level.replace('mAGL', '')+'m '
                                +'Above Ground')
    elif 'UGL' in var_level:
        if 'cm' in var_level:
            var_GRIB_lvl_typ = '112'
            formal_var_level = (var_level.replace('cmUGL', '')+'cm '
                                +'Under Ground')
    elif 'sfc' in var_level:
        var_GRIB_lvl_typ = '1'
        formal_var_level = 'Surface'
    elif 'sigma' in var_level:
        var_GRIB_lvl_typ = '107'
        formal_var_level = var_level.replace('sigma', '')+' Sigma Level'
    elif var_level == 'msl':
        var_GRIB_lvl_typ = '102'
        formal_var_level = 'Mean Sea Level Pressure'
    elif var_level == 'column':
        var_GRIB_lvl_typ = '200'
        formal_var_level = 'Entire Atmosphere'
    elif var_level == 'toa':
        var_GRIB_lvl_typ = '8'
        formal_var_level = 'Top of Atmosphere'
    elif var_level == 'pbl':
        if var_name == 'TCDC':
            var_GRIB_lvl_typ = '211'
            formal_var_level = 'Boundary Layer Cloud Layer'
        else:
            var_GRIB_lvl_typ = '220'
            formal_var_level = 'Planetary Boundary Layer'
    elif var_level == 'low':
        var_GRIB_lvl_typ = '214'
        formal_var_level = 'Low Cloud Layer'
    elif var_level == 'mid':
        var_GRIB_lvl_typ = '224'
        formal_var_level = 'Middle Cloud Layer'
    elif var_level == 'high':
        var_GRIB_lvl_typ = '234'
        formal_var_level = 'High Cloud Layer'
    elif var_level == 'convective':
        var_GRIB_lvl_typ = '244'
        formal_var_level = 'Convective Cloud Layer'
    elif var_level == 'lowcloudbase':
        var_GRIB_lvl_typ = '212'
        formal_var_level = 'Low Cloud Bottom Level'
    elif var_level == 'midcloudbase':
        var_GRIB_lvl_typ = '222'
        formal_var_level = 'Middle Cloud Bottom Level'
    elif var_level == 'highcloudbase':
        var_GRIB_lvl_typ = '232'
        formal_var_level = 'High Cloud Bottom Level'
    elif var_level == 'convectivecloudbase':
        var_GRIB_lvl_typ = '242'
        formal_var_level = 'Convective Cloud Bottom Level'
    elif var_level == 'lowcloudtop':
        var_GRIB_lvl_typ = '213'
        formal_var_level = 'Low Cloud Top Level'
    elif var_level == 'midcloudtop':
        var_GRIB_lvl_typ = '223'
        formal_var_level = 'Middle Cloud Top Level'
    elif var_level == 'highcloudtop':
        var_GRIB_lvl_typ = '233'
        formal_var_level = 'High Cloud Top Level'
    elif var_level == 'convectivecloudtop':
        var_GRIB_lvl_typ = '243'
        formal_var_level = 'Convective Cloud Top Level'
    elif var_level == 'tropopause':
        var_GRIB_lvl_typ = '7'
        formal_var_level = 'Tropopause'
    elif var_level == 'maxwindlev':
        var_GRIB_lvl_typ = '6'
        formal_var_level = 'Maximum Wind Level'
    elif var_level == 'highesttropfrzlev':
        var_GRIB_lvl_typ = '204'
        formal_var_level = 'Highest Tropospheric Freezing Level'
    # Get settings
    if var_name == '4LFTX': #best (4 layer) lifted index (K)
        formal_var_name = 'Best (4-Layer) Lifted Index'
        cmap = plt.cm.magma
        if var_GRIB_lvl_typ == '1': #surface
            levels = np.array([-20,-15,-10,-8,-6,-4,-2,-1,1,2,4,6,8,10,15,20])
            levels_diff = np.array(
                [-3,-2,-1.5,-1,-0.5,-0.1,0,0.1,0.5,1,1.5,2,3]
            )
            var_scale = 1
            var_units = 'K'
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'ACPCP': #Convective precipitation (kg m-2)
        formal_var_name = 'Convective Precipitation'
        cmap = plt.cm.terrain_r
        if var_GRIB_lvl_typ == '1': #surface
            levels = np.array([0.1,0.2,0.4,0.6,0.8,1,1.5,2,2.5,3])
            levels_diff = np.array(
                [-1.5,-1.2,-0.9,-0.6,-0.3,-0.1,0,0.1,0.3,0.6,0.9,1.2,1.5]
            )
            var_scale = 1
            var_units = 'kg 'r'$\mathregular{m^{-2}}$'''
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'ALBDO': #albedo (%)
        formal_var_name = 'Albedo'
        cmap = plt.cm.cubehelix_r
        if var_GRIB_lvl_typ == '1': #surface
            levels = np.array([5,10,15,20,25,30,35,40,45,50])
            levels_diff = np.array(
                [-3,-2,-1.5,-1,-0.5,-0.1,0,0.1,0.5,1,1.5,2,3]
            )
            var_scale = 1
            var_units = '%'
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'APCP': #total precipitation (kg m-2)
        formal_var_name = 'Total Precipitation'
        cmap = plt.cm.terrain_r
        if var_GRIB_lvl_typ == '1': #surface
            levels = np.array([0.1,0.2,0.4,0.6,0.8,1,1.5,2,2.5,3])
            levels_diff = np.array(
                [-1.5,-1.2,-0.9,-0.6,-0.3,-0.1,0,0.1,0.3,0.6,0.9,1.2,1.5]
            )
            var_scale = 1
            var_units = 'kg 'r'$\mathregular{m^{-2}}$'''
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'CAPE': #convective available potential energy (CAPE) (J kg-1)
        formal_var_name = 'CAPE'
        cmap = plt.cm.RdPu
        if var_GRIB_lvl_typ == '1': #surface
            levels = np.array(
                [100,300,500,700,900,1000,1200,1300,1400,1500,1600,1700,1800]
            )
            levels_diff = np.array(
                [-300,-200,-100,-50,-30,-10,0,10,30,50,100,200,300]
            )
            var_scale = 1
            var_units = 'J 'r'$\mathregular{kg^{-1}}$'''
        elif var_GRIB_lvl_typ == '116': #layer between two levels at specified pressure difference from ground to level (hPa)
            levels = np.array(
                [100,300,500,700,900,1000,1200,1300,1400,1500,1600,1700,1800]
            )
            levels_diff = np.array(
                [-300,-200,-100,-50,-30,-10,0,10,30,50,100,200,300]
            )
            var_scale = 1
            var_units = 'J 'r'$\mathregular{kg^{-1}}$'''
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'CIN': #convective inhibition (CIN)(J kg-1)
        formal_var_name = 'CIN'
        cmap = plt.cm.RdPu_r
        if var_GRIB_lvl_typ == '1': #surface
            levels = np.array(
                [-500,-450,-400,-350,-300,-250,-200,-150,-100,-50,-25]
            )
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 1
            var_units = 'J 'r'$\mathregular{kg^{-1}}$'''
        elif var_GRIB_lvl_typ == '116': #layer between two levels at specified pressure difference from ground to level (hPa)
            levels = np.array(
                [-500,-450,-400,-350,-300,-250,-200,-150,-100,-50,-25]
            )
            levels_diff = np.array(
                [-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30]
            )
            var_scale = 1
            var_units = 'J 'r'$\mathregular{kg^{-1}}$'''
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'CLWMR': #cloud water mixing ratio (kg kg-1)
        formal_var_name = 'Cloud Mixing Ratio'
        cmap = plt.cm.Blues
        if var_GRIB_lvl_typ == '100': #isobaric/pressure levels (hPa)
            levels = np.array([0.5,1,5,10,20,40,60,80,100,120,140])
            levels_diff = np.array(
                [-40,-20,-10,-6,-3,-1,-0.1,0,0.1,1,3,6,10,20,40]
            )
            var_scale = 1000000
            var_units = 'ppmg'
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'CWAT': #cloud water (kg m-2)
        formal_var_name = 'Cloud Water'
        cmap = plt.cm.BuGn
        if var_GRIB_lvl_typ == '200': #entire atmosphere/column
            levels = np.array([20,40,60,80,100,120,140,160,180,200])
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 1000
            var_units = 'g 'r'$\mathregular{m^{-2}}$'''
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'CWORK': #cloud work function (J kg-1)
        formal_var_name = 'Cloud Work Function'
        cmap = plt.cm.BuGn
        if var_GRIB_lvl_typ == '200': #entire atmosphere/column
            var_info_title = (
                'Atmospheric Column Cloud Work Function '
                +'(J 'r'$\mathregular{kg^{-1}}$'')'
            )
            levels = np.array([10,20,40,60,80,100,120,140,160,180])
            levels_diff = np.array([-30,-25,-20,-15,-10,-5,0,5,10,15,20,25,30])
            var_scale = 1
            var_units = 'J 'r'$\mathregular{kg^{-1}}$'''
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'DLWRF': #downward longwave radiation flux (W m-2)
        formal_var_name = 'Downward Longwave Flux'
        cmap = plt.cm.gist_heat_r
        if var_GRIB_lvl_typ == '1': #surface
            var_info_title = (
                'Surface Downward Longwave Flux '
                +'(W 'r'$\mathregular{m^{-2}}$'')'
            )
            levels = np.array([5,10,50,100,150,200,250,300,350,400,450,500])
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 1
            var_units = 'W 'r'$\mathregular{m^{-2}}$'''
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'DPT': #dewpoint temperature (K)
        formal_var_name = 'Dewpoint Temperature'
        cmap = plt.cm.Greens
        if var_GRIB_lvl_typ == '105': #height level above ground (m)
            levels = np.array(
                [240,245,250,255,260,265,270,275,280,285,290,295,300]
            )
            levels_diff = np.array([-5,-4,-3,-2,-1,-0.5,0,0.5,1,2,3,4,5])
            var_scale = 1
            var_units = 'K'
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'DSWRF': #downward shortwave radiation flux (W m-2)
        formal_var_name = 'Downward Shortwave Flux'
        cmap = plt.cm.gist_heat_r
        if var_GRIB_lvl_typ == '1': #surface
            levels = np.array([5,10,50,100,150,200,250,300,350,400,450,500])
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 1
            var_units = 'W 'r'$\mathregular{m^{-2}}$'''
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'FLDCP': #field capacity (fraction)
        formal_var_name = 'Field Capacity'
        cmap = plt.cm.PuBuGn
        if var_GRIB_lvl_typ == '1': #surface
            levels = np.array([0.01,0.02,0.04,0.06,0.08,0.1,0.2,0.4,0.6,0.8,1])
            levels_diff = np.array(
                [-1,-0.5,-0.1,-0.05,-0.01,0,0.01,0.05,0.1,0.5,1]
            )
            var_scale = 1
            var_units = 'fraction'
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'GFLUX': #ground heat flux (W m-2)
        formal_var_name = 'Ground Heat Flux'
        var_units = ''
        cmap = plt.cm.PiYG
        if var_GRIB_lvl_typ == '1': #surface
            levels = np.array([-30,-20,-15,-10,-5,-2,2,5,10,15,20,30])
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 1
            var_units = 'W 'r'$\mathregular{m^{-2}}$'''
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'GUST': #wind gust (m s-1)
        formal_var_name = 'Wind Gust'
        cmap = plt.cm.pink_r
        if var_GRIB_lvl_typ == '1': #surface
            levels = np.array([0.5,1,2,4,6,8,10,12,14,16,18,20])
            levels_diff = np.array([-3,-2,-1,-0.5,-0.2,0,0.2,0.5,1,2,3])
            var_scale = 1
            var_units = 'm 'r'$\mathregular{s^{-1}}$'''
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'HGT': #geopotential height (gpm)
        formal_var_name = 'Geopotential Height'
        cmap = plt.cm.cubehelix_r
        if var_GRIB_lvl_typ == '1': #surface
            levels = np.array(
                [100,500,1000,1500,2000,2500,3000,3500,4000,4500,5000,6000,
                 7000,8000]
            )
            levels_diff = np.array(
                [-400,-200,-100,-50,-20,-10,0,10,20,50,100,200,400]
            )
            var_scale = 1
            var_units = 'gpm'
        elif var_GRIB_lvl_typ == '6': #maximum wind level
            levels = np.array([1,2,3,4,5,6,7,8,9,10,12,14,16,18])
            levels_diff = np.array(
                [-1,-0.8,-0.6,-0.4,-0.2,-0.1,0,0.1,0.2,0.4,0.6,0.8,1]
            )
            var_scale = 0.001
            var_units = 'km'
        elif var_GRIB_lvl_typ == '7': #tropopause
            levels = np.array([1,2,3,4,5,6,7,8,9,10,12,14,16,18])
            levels_diff = np.array(
                [-1,-0.8,-0.6,-0.4,-0.2,-0.1,0,0.1,0.2,0.4,0.6,0.8,1]
            )
            var_scale = 0.001
            var_units = 'km'
        elif var_GRIB_lvl_typ == '100': #isobaric/pressure levels (hPa)
            levels = np.nan
            levels_diff = np.array(
                [-120,-80,-40,-20,-10,-5,0,5,10,20,40,80,120]
            )
            var_scale = 1
            var_units = 'gpm'
        elif var_GRIB_lvl_typ == '204': #highest tropospheric freezing level
            levels = np.array(
                [100,500,1000,1500,2000,2500,3000,3500,
                 4000,4500,5000,6000,7000,8000]
            )
            levels_diff = np.array(
                [-400,-200,-100,-50,-20,-10,0,10,20,50,100,200,400]
            )
            var_scale = 1
            var_units = 'gpm'
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'HINDEX': #haines index (no units)
        formal_var_name = 'Haines Index'
        cmap = plt.cm.YlOrRd
        if var_GRIB_lvl_typ == '1': #surface
            levels = np.array([1,2,3,4,5,6,7,8,9])
            levels_diff = np.array(
                [-3,-2,-1,-0.5,-0.1,-0.01,0,0.01,0.1,0.5,1,2,3]
            )
            var_scale = 1
            var_units = ''
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'HPBL': #planetary boundary layer height (m)
        formal_var_name = 'Planetary Boundary Layer Height'
        cmap = plt.cm.cubehelix_r
        if var_GRIB_lvl_typ == '1': #surface
            levels = np.array(
                [300,400,500,600,700,800,900,1000,1100,1200,1400,1600,1800]
            )
            levels_diff = np.array(
                [-600,-400,-200,-100,-50,-20,0,20,50,100,200,400,600]
            )
            var_scale = 1
            var_units = 'm'
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'ICAHT': #ICAO standard atmosphere reference height (m)
        formal_var_name = 'ICAO Standard Atmos. Reference Height'
        cmap = plt.cm.cubehelix_r
        if var_GRIB_lvl_typ == '6': #maximum wind level
            levels = np.array([1,2,3,4,5,6,7,8,9,10,12,14,16,18])
            levels_diff = np.array(
                [-1,-0.8,-0.6,-0.4,-0.2,-0.1,0,0.1,0.2,0.4,0.6,0.8,1]
            )
            var_scale = 0.001
            var_units = 'km'
        elif var_GRIB_lvl_typ == '7': #tropopause
            levels = np.array([1,2,3,4,5,6,7,8,9,10,12,14,16,18])
            levels_diff = np.array(
                [-1,-0.8,-0.6,-0.4,-0.2,-0.1,0,0.1,0.2,0.4,0.6,0.8,1]
            )
            var_scale = 0.001
            var_units = 'km'
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'ICEC': #ice cover (proportion)
        formal_var_name = 'Ice Cover (ice=1, no ice=0)'
        cmap = plt.cm.Blues
        if var_GRIB_lvl_typ == '1': #surface
            levels = np.array(
                [0.01,0.02,0.04,0.06,0.08,0.1,0.2,0.4,0.6,0.8,1]
            )
            levels_diff = np.array(
                [-1,-0.5,-0.1,-0.05,-0.01,0,0.01,0.05,0.1,0.5,1]
            )
            var_scale = 1
            var_units = 'fraction'
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'LFTX': #lifted index (K)
        formal_var_name = 'Lifted Index'
        cmap = plt.cm.magma
        if var_GRIB_lvl_typ == '1': #surface
            levels = np.array([-20,-15,-10,-8,-6,-4,-2,-1,1,2,4,6,8,10,15,20])
            levels_diff = np.array(
                [-3,-2,-1.5,-1,-0.5,-0.1,0,0.1,0.5,1,1.5,2,3]
            )
            var_scale = 1
            var_units = 'K'
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'LHTFL': #latent heat net flux (W m-2)
        formal_var_name = 'Latent Heat Flux'
        cmap = plt.cm.Reds
        if var_GRIB_lvl_typ == '1': #surface
            levels = np.array([5,10,20,40,60,80,100,120,140,160,180,200])
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 1
            var_units = 'W 'r'$\mathregular{m^{-2}}$'''
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
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
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'O3MR': #ozone mixing ratio (kg kg-1)
        formal_var_name = 'Ozone Mixing Ratio'
        cmap = plt.cm.YlGnBu
        if var_GRIB_lvl_typ == '100': #isobaric/pressure levels (hPa)
            levels = np.nan
            levels_diff = np.array(
                [-5,-4,-3,-2,-1,-0.5,0,0.5,1,2,3,4,5]
            )
            var_scale = 1000000
            var_units = 'ppmg'
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'PEVPR': #potential evaporation rate (W m-2)
        formal_var_name = 'Potential Evaporation Rate'
        cmap = plt.cm.copper_r
        if var_GRIB_lvl_typ == '1': #surface
            levels = np.array([5,10,50,100,150,200,250,300,350,400,450,500])
            levels_diff = np.array(
                [-50,-30,-20,-15,-10,-5,0,5,10,15,20,30,50]
            )
            var_scale = 1
            var_units = 'W 'r'$\mathregular{m^{-2}}$'''
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'POT': #potential temperature (K)
        formal_var_name = 'Potential Temperature'
        cmap = plt.cm.rainbow
        if var_GRIB_lvl_typ == '107': #sigma level (sigma value in 1/10000)
            levels = np.array(
                [240,245,250,255,260,265,270,275,280,285,290,295,300]
            )
            levels_diff = np.array([-5,-3,-2,-1,-0.5,-0.1,0,0.1,0.5,1,2,3,5])
            var_scale = 1
            var_units = 'K'
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'PRATE': #precipitation rate ([kg m-2] s-1)
        formal_var_name = 'Precipitation Rate'
        cmap = plt.cm.terrain_r
        if var_GRIB_lvl_typ == '1': #surface
            levels = np.array(
                [0.1,0.2,0.4,0.6,0.8,1,1.5,2,2.5,3]
            )
            levels_diff = np.array(
                [-3-2,-1.5,-1,-0.5,-0.1,0,0.1,0.5,1,1.5,2,3]
            )
            var_scale = 24*3600
            var_units = 'mm 'r'$\mathregular{day^{-1}}$'''
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
        elif var_GRIB_lvl_typ == '6': #maximum wind level
            levels = np.array(
                [10,50,100,120,140,160,180,200,220,240,260,280,300]
            )
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 0.01
            var_units = 'hPa'
        elif var_GRIB_lvl_typ == '7': #tropopause
            levels = np.array([100,120,140,160,180,200,220,240,260,280,300])
            levels_diff = np.array([-20,-15,-10,-5,-2,-1,0,1,2,5,10,15,20])
            var_scale = 0.01
            var_units = 'hPa'
        elif var_GRIB_lvl_typ == '212': #low cloud bottom level
            levels = np.array(
                [780,800,820,840,860,880,900,920,940,960,980,1000,1020]
            )
            levels_diff = np.array([-20,-15,-10,-5,-2,-1,0,1,2,5,10,15,20])
            var_scale = 0.01
            var_units = 'hPa'
        elif var_GRIB_lvl_typ == '213': #low cloud top level
            levels = np.array(
                [600,620,640,660,680,700,720,740,760,780,800,820,840]
            )
            levels_diff = np.array([-20,-15,-10,-5,-2,-1,0,1,2,5,10,15,20])
            var_scale = 0.01
            var_units = 'hPa'
        elif var_GRIB_lvl_typ == '222': #mid cloud bottom level
            levels = np.array(
                [460,480,500,520,540,560,580,600,620,640,660,680,700]
            )
            levels_diff = np.array([-20,-15,-10,-5,-2,-1,0,1,2,5,10,15,20])
            var_scale = 0.01
            var_units = 'hPa'
        elif var_GRIB_lvl_typ == '223': #mid cloud top level
            levels = np.array(
                [300,320,340,360,380,400,420,440,460,480,500,520,540]
            )
            levels_diff = np.array([-20,-15,-10,-5,-2,-1,0,1,2,5,10,15,20])
            var_scale = 0.01
            var_units = 'hPa'
        elif var_GRIB_lvl_typ == '232': #high cloud bottom level
            levels = np.array(
                [180,200,220,240,260,280,300,320,340,360,380,400,420]
            )
            levels_diff = np.array([-20,-15,-10,-5,-2,-1,0,1,2,5,10,15,20])
            var_scale = 0.01
            var_units = 'hPa'
        elif var_GRIB_lvl_typ == '233': #high cloud top level
            levels = np.array(
                [80,100,120,140,160,180,200,220,240,260,280,300,320]
            )
            levels_diff = np.array([-20,-15,-10,-5,-2,-1,0,1,2,5,10,15,20])
            var_scale = 0.01
            var_units = 'hPa'
        elif var_GRIB_lvl_typ == '242': #convective cloud bottom level
            levels = np.array(
                [780,800,820,840,860,880,900,920,940,960,980,1000,1020]
            )
            levels_diff = np.array([-20,-15,-10,-5,-2,-1,0,1,2,5,10,15,20])
            var_scale = 0.01
            var_units = 'hPa'
        elif var_GRIB_lvl_typ == '243': #convective cloud top level
            levels = np.array(
                [150,200,250,300,350,400,450,500,550,600,650,700,800,850]
            )
            levels_diff = np.array([-20,-15,-10,-5,-2,-1,0,1,2,5,10,15,20])
            var_scale = 0.01
            var_units = 'hPa'
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
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
            exit(1)
    elif var_name == 'PWAT': #precipitable water (kg m-2)
        formal_var_name = 'Precipitable Water'
        cmap = plt.cm.BuGn
        if var_GRIB_lvl_typ == '200': #entire atmosphere/column
            var_info_title = (
                'Atmospheric Column Precipitable Water '
                +'(kg 'r'$\mathregular{m^{-2}}$'')'
            )
            levels = np.array([5,10,15,20,25,30,35,40,45,50])
            levels_diff = np.array([-10,-5,-4,-3,-2,-1,0,1,2,3,4,5,10])
            var_scale = 1
            var_units = 'kg 'r'$\mathregular{m^{-2}}$'''
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'RH': #relative humidity (%)
        formal_var_name = 'Relative Humidity'
        cmap = plt.cm.Greens
        if var_GRIB_lvl_typ == '100': #isobaric/pressure levels (hPa)
            levels = np.array([1,5,10,30,50,70,90])
            levels_diff = np.array(
                [-50,-40,-30,-20,-10,-5,0,5,10,20,30,40,50]
            )
            var_scale = 1
            var_units = '%'
        elif var_GRIB_lvl_typ == '105': #height level above ground (m)
            levels = np.array([10,20,30,40,50,60,70,80,90,100])
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 1
            var_units = '%'
        elif var_GRIB_lvl_typ == '107': #sigma level (sigma value in 1/10000)
            levels = np.array([10,20,30,40,50,60,70,80,90,100])
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 1
            var_units = '%'
        elif var_GRIB_lvl_typ == '200': #entire atmosphere/column
            levels = np.array([10,20,30,40,50,60,70,80,90,100])
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 1
            var_units = '%'
        elif var_GRIB_lvl_typ == '204': #highest tropospheric freezing level
            levels = np.array([10,20,30,40,50,60,70,80,90,100])
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 1
            var_units = '%'
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'SHTFL': #sensible heat net flux (W m-2)
        formal_var_name = 'Sensible Heat Flux'
        cmap = plt.cm.Reds
        if var_GRIB_lvl_typ == '1': #surface
            levels = np.array([5,10,20,40,60,80,100,120,140,160,180,200])
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 1
            var_units = 'W 'r'$\mathregular{m^{-2}}$'''
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'SNOD': #snow depth (m)
        formal_var_name = 'Snow Depth'
        cmap = plt.cm.Blues
        if var_GRIB_lvl_typ == '1': #surface
            var_info_title = 'Surface Snow Depth (cm)'
            levels = np.array([1,5,10,20,40,60,80,100,150,200,250])
            levels_diff = np.array(
                [-40,-20,-10,-5,-1,-0.1,0,0.1,1,5,10,20,40]
            )
            var_scale = 100
            var_units = 'cm'
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'SOILW': #volumetric soil moisture content (fraction)
        formal_var_name = 'Volumetric Soil Moisture'
        cmap = plt.cm.summer_r
        if var_GRIB_lvl_typ == '112': #layer between two depths below land surface (cm)
            levels = np.array([10,20,30,40,50,60,70,80,90,100])
            levels_diff = np.array([-20,-15,-10,-5,-3,-1,0,1,3,5,10,15,20])
            var_scale = 100
            var_units = 'fraction'
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'SPFH': #specific humidity (kg kg-1)
        formal_var_name = 'Specific Humidity'
        cmap = plt.cm.Greens
        if var_GRIB_lvl_typ == '100': #isobaric/pressure levels (hPa)
            levels = np.array([1,2,4,6,8,10,12,14,16,18])
            levels_diff = np.array(
                [-3,-2,-1,-0.6,-0.3,-0.1,0,0.1,0.3,0.6,1,2,3]
            )
            var_scale = 1000
            var_units = 'g 'r'$\mathregular{kg^{-1}}$'''
        elif var_GRIB_lvl_typ == '105': #height level above ground (m)
            levels = np.array([1,2,4,6,8,10,12,14,16,18])
            levels_diff = np.array(
                [-3,-2,-1,-0.6,-0.3,-0.1,0,0.1,0.3,0.6,1,2,3]
            )
            var_scale = 1000
            var_units = 'g 'r'$\mathregular{kg^{-1}}$'''
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'SUNSD': #sunshine Duration (s)
        formal_var_name = 'Sunshine Duration'
        cmap = plt.cm.YlOrBr
        if var_GRIB_lvl_typ == '1': #surface
            levels = np.array([0.01,0.05,0.1,0.5,1,2,3,4,5,6])
            levels_diff = np.array([-2,-1,-0.5,-0.1,0,0.1,0.5,1,2])
            var_scale = (1./360.)
            var_units = 'hour'
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'TCDC': #total cloud cover (%)
        formal_var_name = 'Cloud Cover'
        cmap = plt.cm.Blues
        if var_GRIB_lvl_typ == '200': #entire atmosphere/column
            levels = np.array([0,10,20,30,40,50,60,80,100])
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 1
            var_units = '%'
        elif var_GRIB_lvl_typ == '211': #boundary layer cloud layer
            levels = np.array([0,10,20,30,40,50,60,80,100])
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 1
            var_units = '%'
        elif var_GRIB_lvl_typ == '214': #low layer cloud layer
            levels = np.array([0,10,20,30,40,50,60,80,100])
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 1
            var_units = '%'
        elif var_GRIB_lvl_typ == '224': #mid layer cloud layer
            levels = np.array([0,10,20,30,40,50,60,80,100])
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 1
            var_units = '%'
        elif var_GRIB_lvl_typ == '234': #high layer cloud layer
            levels = np.array([0,10,20,30,40,50,60,80,100])
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 1
            var_units = '%'
        elif var_GRIB_lvl_typ == '244': #convective layer cloud layer
            levels = np.array([0,10,20,30,40,50,60,80,100])
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 1
            var_units = '%'
    elif var_name == 'TMAX': #maximum temperature (K)
        formal_var_name = 'Maximum Temperature'
        cmap = plt.cm.rainbow
        if var_GRIB_lvl_typ == '105': #height level above ground (m)
            levels = np.array(
                [240,245,250,255,260,265,270,275,280,285,290,295,300]
            )
            levels_diff = np.array(
                [-5,-4,-3,-2,-1,-0.5,-0.1,0,0.1,0.5,1,2,3,4,5]
            )
            var_scale = 1
            var_units = 'K'
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'TMIN': #minimum temperature (K)
        formal_var_name = 'Minimum Temperature'
        cmap = plt.cm.rainbow
        if var_GRIB_lvl_typ == '105': #height level above ground (m)
            levels = np.array(
                [240,245,250,255,260,265,270,275,280,285,290,295,300]
            )
            levels_diff = np.array(
                [-5,-4,-3,-2,-1,-0.5,-0.1,0,0.1,0.5,1,2,3,4,5]
            )
            var_scale = 1
            var_units = 'K'
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'TMP': #temperature (K)
        formal_var_name = 'Temperature'
        cmap = plt.cm.rainbow
        if var_GRIB_lvl_typ == '1': #surface
            levels = np.array(
                [240,245,250,255,260,265,270,275,280,285,290,295,300]
            )
            levels_diff = np.array(
                [-5,-4,-3,-2,-1,-0.5,-0.1,0,0.1,0.5,1,2,3,4,5]
            )
            var_scale = 1
            var_units = 'K'
        elif var_GRIB_lvl_typ == '6': #maximum wind level
            levels = np.array(
                [160,180,185,190,195,200,205,210,215,220,225,230,235,240]
            )
            levels_diff = np.array([-5,-3,-2,-1,-0.5,-0.1,0,0.1,0.5,1,2,3,5])
            var_scale = 1
            var_units = 'K'
        elif var_GRIB_lvl_typ == '7': #tropopause
            levels = np.array(
                [160,180,185,190,195,200,205,210,215,220,225,230,235,240]
            )
            levels_diff = np.array([-5,-3,-2,-1,-0.5,-0.1,0,0.1,0.5,1,2,3,5])
            var_scale = 1
            var_units = 'K'
        elif var_GRIB_lvl_typ == '100': #isobaric/pressure levels (hPa)
            levels = np.nan
            levels_diff = np.array(
                [-4,-3,-2,-1,-0.5,-0.1,0,0.1,0.5,1,2,3,4]
            )
            var_scale = 1
            var_units = 'K'
        elif var_GRIB_lvl_typ == '105': #height level above ground (m)
            levels = np.array(
                [240,245,250,255,260,265,270,275,280,285,290,295,300]
            )
            levels_diff = np.array(
                [-5,-4,-3,-2,-1,-0.5,-0.1,0,0.1,0.5,1,2,3,4,5]
            )
            var_scale = 1
            var_units = 'K'
        elif var_GRIB_lvl_typ == '107': #sigma level (sigma value in 1/10000)
            levels = np.array(
                [240,245,250,255,260,265,270,275,280,285,290,295,300]
            )
            levels_diff = np.array([-5,-3,-2,-1,-0.5,-0.1,0,0.1,0.5,1,2,3,5])
            var_scale = 1
            var_units = 'K'
        elif var_GRIB_lvl_typ == '213': #low cloud top level
            levels = np.array(
                [220,225,230,235,240,245,250,255,260,265,270,275,280]
            )
            levels_diff = np.array([-5,-3,-2,-1,-0.5,-0.1,0,0.1,0.5,1,2,3,5])
            var_scale = 1
            var_units = 'K'
        elif var_GRIB_lvl_typ == '223': #mid cloud top level
            levels = np.array(
                [200,205,210,215,220,225,230,235,240,245,250,255,260]
            )
            levels_diff = np.array([-5,-3,-2,-1,-0.5,-0.1,0,0.1,0.5,1,2,3,5])
            var_scale = 1
            var_units = 'K'
        elif var_GRIB_lvl_typ == '233': #high cloud top level
            levels = np.array(
                [180,185,190,195,200,205,210,215,220,225,230,235,240]
            )
            levels_diff = np.array([-5,-3,-2,-1,-0.5,-0.1,0,0.1,0.5,1,2,3,5])
            var_scale = 1
            var_units = 'K'
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'TOZNE': #total ozone (Dobson)
        formal_var_name = 'Total Ozone'
        cmap = plt.cm.summer_r
        if var_GRIB_lvl_typ == '200': #entire atmosphere/column
            levels = np.array(
                [160,180,200,220,240,260,280,300,320,340,360,380]
            )
            levels_diff = np.array([-10,-5,-4,-3,-2,-1,0,1,2,3,4,5,10])
            var_scale = 1
            var_units = 'Dobson'
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'TSOIL': #soil temperature (K)
        formal_var_name = 'Soil Temperature'
        cmap = plt.cm.rainbow
        if var_GRIB_lvl_typ == '112': #layer between two depths below land surface (cm)
            levels = np.array(
                [240,245,250,255,260,265,270,275,280,285,290,295,300]
            )
            levels_diff = np.array(
                [-5,-3,-2,-1,-0.5,-0.1,0,0.1,0.5,1,2,3,5]
            )
            var_scale = 1
            var_units = 'K'
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'UFLX': #momentum flux, u component (N m-2)
        formal_var_name = 'Zonal Momentum Flux'
        cmap = plt.cm.PRGn
        if var_GRIB_lvl_typ == '1': #surface
            levels = np.array(
                [-200,-160,-120,-80,-40,-10,10,40,80,120,160,200]
            )
            levels_diff = np.array(
                [-100,-50,-30,-20,-10,-5,0,5,10,20,30,50,100]
            )
            var_scale = 1000
            var_units = '1000 * N 'r'$\mathregular{m^{-2}}$'''
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'UGRD': #zonal wind (m s-1)
        formal_var_name = 'Zonal Wind'
        cmap = plt.cm.PRGn
        if var_GRIB_lvl_typ == '6': #maximum wind level
            levels = np.array(
                [-50,-40,-30,-20,-10,-5,-3,-1,1,3,5,10,20,30,40,50]
            )
            levels_diff = np.array([-20,-10,-5,-3,-2,-1,0,1,2,3,5,10,20])
            var_scale = 1
            var_units = 'm 'r'$\mathregular{s^{-1}}$'''
        elif var_GRIB_lvl_typ == '7': #tropopause
            levels = np.array(
               [-50,-40,-30,-20,-10,-5,-3,-1,1,3,5,10,20,30,40,50]
            )
            levels_diff = np.array([-10,-5,-3,-2,-1,-0.5,0,0.5,1,2,3,5,10])
            var_scale = 1
            var_units = 'm 'r'$\mathregular{s^{-1}}$'''
        elif var_GRIB_lvl_typ == '100': #isobaric/pressure levels (hPa)
            levels = np.array(
                [-100,-70,-50,-30,-20,-10,-5,5,10,20,30,50,70,100]
            )
            levels_diff = np.array(
                [-10,-7,-5,-3,-2,-1,0,1,2,3,5,7,10]
            )
            var_scale = 1
            var_units = 'm 'r'$\mathregular{s^{-1}}$'''
        elif var_GRIB_lvl_typ == '105': #height level above ground (m)
            levels = np.array(
                [-50,-40,-30,-20,-10,-5,-3,-1,1,3,5,10,20,30,40,50]
            )
            levels_diff = np.array([-10,-5,-3,-2,-1,-0.5,0,0.5,1,2,3,5,10])
            var_scale = 1
            var_units = 'm 'r'$\mathregular{s^{-1}}$'''
        elif var_GRIB_lvl_typ == '107': #sigma level (sigma value in 1/10000)
            levels = np.array(
                [-50,-40,-30,-20,-10,-5,-3,-1,1,3,5,10,20,30,40,50]
            )
            levels_diff = np.array([-10,-5,-3,-2,-1,-0.5,0,0.5,1,2,3,5,10])
            var_scale = 1
            var_units = 'm 'r'$\mathregular{s^{-1}}$'''
        elif var_GRIB_lvl_typ == '220': #planetary Boundary Layer (derived from Richardson number)
            levels = np.array(
                [-50,-40,-30,-20,-10,-5,-3,-1,1,3,5,10,20,30,40,50]
            )
            levels_diff = np.array([-10,-5,-3,-2,-1,-0.5,0,0.5,1,2,3,5,10])
            var_scale = 1
            var_units = 'm 'r'$\mathregular{s^{-1}}$'''
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'U-GWD': #zonal flux of gravity wave stress (N m-2)
        formal_var_name = 'Zonal Gravity Wave Stress'
        cmap = plt.cm.PuRd
        if var_GRIB_lvl_typ == '1': #surface
            levels = np.array([5,10,20,40,60,80,100,120,140,160,180])
            levels_diff = np.array(
                [-50,-30,-20,-10,-5,-2,0,2,5,10,20,30,50]
            )
            var_scale = 1000
            var_units = '1000 * N 'r'$\mathregular{m^{-2}}$'''
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'ULWRF': #upward longwave radiation flux (W m-2)
        formal_var_name = 'Upward Longwave Flux'
        cmap = plt.cm.gist_heat_r
        if var_GRIB_lvl_typ == '1': #surface
            levels = np.array([5,10,50,100,150,200,250,300,350,400,450,500])
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 1
            var_units = 'W 'r'$\mathregular{m^{-2}}$'''
        elif var_GRIB_lvl_typ == '8': #nominal top of atmosphere
            levels = np.array([5,10,50,100,150,200,250,300,350,400,450,500])
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 1
            var_units = 'W 'r'$\mathregular{m^{-2}}$'''
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'USWRF': #upward shortwave radiation flux (W m-2)
        formal_var_name = 'Upward Shortwave Flux'
        cmap = plt.cm.gist_heat_r
        if var_GRIB_lvl_typ == '1': #surface
            levels = np.array([5,10,20,40,60,80,100,120,140,160,180,200,300])
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 1
            var_units = 'W 'r'$\mathregular{m^{-2}}$'''
        elif var_GRIB_lvl_typ == '8': #nominal top of atmosphere
            levels = np.array([5,10,20,40,60,80,100,120,140,160,180,200,300])
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 1
            var_units = 'W 'r'$\mathregular{m^{-2}}$'''
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'VFLX': #momentum flux, v component (N m-2)
        formal_var_name = 'Meridional Momentum Flux'
        cmap = plt.cm.PRGn
        if var_GRIB_lvl_typ == '1': #surface
            levels = np.array(
                [-200,-160,-120,-80,-40,-10,10,40,80,120,160,200]
            )
            levels_diff = np.array(
                [-100,-50,-30,-20,-10,-5,0,5,10,20,30,50,100]
            )
            var_scale = 1000
            var_units = '1000 * N 'r'$\mathregular{m^{-2}}$'''
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'VGRD': #meridional wind (m s-1)
        formal_var_name = 'Meridional Wind'
        cmap = plt.cm.PRGn
        if var_GRIB_lvl_typ == '6': #maximum wind level
            levels = np.array(
                [-50,-40,-30,-20,-10,-5,-3,-1,1,3,5,10,20,30,40,50]
            )
            levels_diff = np.array([-20,-10,-5,-3,-2,-1,0,1,2,3,5,10,20])
            var_scale = 1
            var_units = 'm 'r'$\mathregular{s^{-1}}$'''
        elif var_GRIB_lvl_typ == '7': #tropopause
            levels = np.array(
                [-50,-40,-30,-20,-10,-5,-3,-1,1,3,5,10,20,30,40,50]
            )
            levels_diff = np.array(
                [-10,-5,-3,-2,-1,-0.5,0,0.5,1,2,3,5,10]
            )
            var_scale = 1
            var_units = 'm 'r'$\mathregular{s^{-1}}$'''
        elif var_GRIB_lvl_typ == '100': #isobaric/pressure levels (hPa)
            levels = np.array(
                [-50,-30,-20,-10,-5,-1,1,5,10,20,30,50]
            )
            levels_diff = np.array(
                [-10,-7,-5,-3,-2,-1,-0.5,-0.2,0,0.2,0.5,1,2,3,5,7,10]
            )
            var_scale = 1
            var_units = 'm 'r'$\mathregular{s^{-1}}$'''
        elif var_GRIB_lvl_typ == '105': #height level above ground (m)
            levels = np.array(
                [-50,-40,-30,-20,-10,-5,-3,-1,1,3,5,10,20,30,40,50]
            )
            levels_diff = np.array([-10,-5,-3,-2,-1,-0.5,0,0.5,1,2,3,5,10])
            var_scale = 1
            var_units = 'm 'r'$\mathregular{s^{-1}}$'''
        elif var_GRIB_lvl_typ == '107': #sigma level (sigma value in 1/10000)
            levels = np.array(
                [-50,-40,-30,-20,-10,-5,-3,-1,1,3,5,10,20,30,40,50]
            )
            levels_diff = np.array([-10,-5,-3,-2,-1,-0.5,0,0.5,1,2,3,5,10])
            var_scale = 1
            var_units = 'm 'r'$\mathregular{s^{-1}}$'''
        elif var_GRIB_lvl_typ == '220': #planetary Boundary Layer (derived from Richardson number)
            levels = np.array(
                [-50,-40,-30,-20,-10,-5,-3,-1,1,3,5,10,20,30,40,50]
            )
            levels_diff = np.array([-10,-5,-3,-2,-1,-0.5,0,0.5,1,2,3,5,10])
            var_scale = 1
            var_units = 'm 'r'$\mathregular{s^{-1}}$'''
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'V-GWD': #meridional flux of gravity wave stress (N m-2)
        formal_var_name = 'Meridional Gravity Wave Stress'
        cmap = plt.cm.PuRd
        if var_GRIB_lvl_typ == '1': #surface
            levels = np.array([5,10,20,40,60,80,100,120,140,160,180])
            levels_diff = np.array([-50,-30,-20,-10,-5,-2,0,2,5,10,20,30,50])
            var_scale = 1000
            var_units = '1000 * N 'r'$\mathregular{m^{-2}}$'''
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'VIS': #visibility (m)
        formal_var_name = 'Visibility'
        cmap = plt.cm.gray
        if var_GRIB_lvl_typ == '1': #surface
            levels = np.array([1,2,4,6,8,10,15,20])
            levels_diff = np.array([-4,-3,-2,-1,-0.5,-0.1,0,0.1,0.5,1,2,3,4])
            var_scale = 0.001
            var_units = 'km'
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'VRATE': #ventilation Rate (m2 s-1)
        formal_var_name = 'Ventilation Rate'
        cmap = plt.cm.magma_r
        if var_GRIB_lvl_typ == '220': #planetary Boundary Layer (derived from Richardson number)
            levels = np.array([5,10,15,20,25,30,35,40,45])
            levels_diff = np.array([-15,-12,-9,-6,-3,-1,0,1,3,6,9,12,15])
            var_scale = 0.001
            var_units = ''r'$\mathregular{km^{2}}$'' 'r'$\mathregular{s^{-1}}$'''
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'VVEL': #vertical velocity (Pa s-1)
        formal_var_name = 'Vertical Velocity'
        cmap = plt.cm.PRGn
        if var_GRIB_lvl_typ == '100': #isobaric/pressure levels (hPa)
            levels = np.array([-4,-3,-2,-1,-0.5,-0.1,0.1,0.5,1,2,3,4])
            levels_diff = np.array([-4,-3,-2,-1,-0.5,-0.1,0,0.1,0.5,1,2,3,4])
            var_scale = 36
            var_units = 'hPa 'r'$\mathregular{hour^{-1}}$'''
        elif var_GRIB_lvl_typ == '107': #sigma level (sigma value in 1/10000)
            levels = np.array([-4,-3,-2,-1,-0.5,-0.1,0.1,0.5,1,2,3,4])
            levels_diff = np.array([-4,-3,-2,-1,-0.5,-0.1,0,0.1,0.5,1,2,3,4])
            var_scale = 36
            var_units = 'hPa 'r'$\mathregular{hour^{-1}}$'''
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'VWSH': #vertical speed shear (s-1)
        formal_var_name = 'Vertical Speed Shear'
        cmap = plt.cm.PRGn
        if var_GRIB_lvl_typ == '7': #tropopause
            levels = np.array(
                [-100,-50,-40,-30,-20,-10,-5,-3,3,5,10,20,30,40,50,100]
            )
            levels_diff = np.array([-10,-5,-4,-3,-2,-1,0,1,2,3,4,5,10])
            var_scale = 3600
            var_units = ''r'$\mathregular{hour^{-1}}$'''
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'WATR': #water runoff (kg m-2)
        formal_var_name = 'Water Runoff'
        cmap = plt.cm.BuGn
        if var_GRIB_lvl_typ == '1': #surface
            levels = np.array(
                [0.01,0.02,0.04,0.06,0.08,0.1,0.2,0.4,0.6,0.8,1]
            )
            levels_diff = np.array(
                [-1,-0.5,-0.1,-0.05,-0.01,0,0.01,0.05,0.1,0.5,1]
            )
            var_scale = 1
            var_units = 'kg 'r'$\mathregular{m^{-2}}$'''
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'WEASD': #water equiv. of accum. snow depth (kg m-2)
        formal_var_name = 'Water Equivalent of Accum Snow Depth'
        cmap = plt.cm.Blues
        if var_GRIB_lvl_typ == '1': #surface
            levels = np.array([0.1,0.5,1,3,6,10,20,30,40,50,70,90])
            levels_diff = np.array([-8,-6,-4,-2,-1,-0.1,0,0.1,1,2,4,6,8])
            var_scale = 1
            var_units = 'kg 'r'$\mathregular{m^{-2}}$'''
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'WILT': #wilting point (fraction)
        formal_var_name = 'Wilting Point'
        cmap = plt.cm.YlOrBr
        if var_GRIB_lvl_typ == '1': #surface
            levels = np.array([0.01,0.02,0.04,0.06,0.08,0.1,0.2,0.4,0.6,0.8,1])
            levels_diff = np.array(
                [-1,-0.5,-0.1,-0.05,-0.01,0,0.01,0.05,0.1,0.5,1]
            )
            var_scale = 1
            var_units = 'fraction'
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    else:
        print("ERROR: cannot find plot settings for "+var_name)
        exit(1)
    if var_name in ['PRMSL', 'MSLET', 'HPBL']:
        var_info_title = (
            formal_var_name+' ('+var_units+')'
        )
    else:
        var_info_title = (
            formal_var_level+' '+formal_var_name+' ('+var_units+')'
        )
    return (var_info_title, levels, levels_diff, cmap, var_scale,
            formal_var_name)
