import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

def calculate_area_average(var_data, lat, lon):
    """! Calculate area average of dataset,
         weighting in the latitude dimension by the difference 
         between the sines of the latitude at the northern and
         southern edges of the grid box. Trying to mimic
         GrADS function aave.
        
             Args:
                 var_data     - array of variable values
                 lat          - array of latitude values 
                 lon          - array of longitude values
 
             Returns:
                 area_average - float of area average
    """
    dlat = 181./len(lat)
    latr = np.deg2rad(lat)
    mx = np.ma.masked_invalid(var_data)
    weights = np.empty_like(var_data)
    weightsum = 0
    arraysum = 0
    for y in range(len(lat)):
        if lat[y] == -90.0:
            weights[y,:] = 0
        elif lat[y] == 90.0:
            weights[y,:] = 0
        elif np.cos(latr[y]) != 0:
            weights[y,:] = (
                np.sin(np.deg2rad((lat[y] + lat[y+1])/2.))
                - np.sin(np.deg2rad((lat[y] + lat[y-1])/2.))
            ) * dlat
        for x in range(len(lon)):
            if mx[y,x] <= -9999.:
                arraysum = arraysum
                weightsum = weightsum
            else:
                if np.ma.is_masked(mx[y,x]) == False:
                   arraysum = arraysum + (mx[y,x] * weights[y,x])
                   weightsum = weightsum + weights[y,x]
                else:
                   arraysum = arraysum
                   weightsum = weightsum
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
    elif 'AGL' in var_level:
        if 'hPa' in var_level:
            var_GRIB_lvl_typ = '116'
        elif 'm' in var_level:
            var_GRIB_lvl_typ = '105'
    elif 'UGL' in var_level:
        if 'cm' in var_level:
            var_GRIB_lvl_typ = '112'
    elif 'sfc' in var_level:
        var_GRIB_lvl_typ = '1'
    elif 'sigma' in var_level:
        var_GRIB_lvl_typ = '107'
    elif var_level == 'msl':
        var_GRIB_lvl_typ = '102'
    elif var_level == 'column':
        var_GRIB_lvl_typ = '200'
    elif var_level == 'toa':
        var_GRIB_lvl_typ = '8'
    elif var_level == 'pbl':
        if var_name == 'TCDC':
            var_GRIB_lvl_typ = '211'
        else:
            var_GRIB_lvl_typ = '220'
    elif var_level == 'low':
        var_GRIB_lvl_typ = '214'
    elif var_level == 'mid':
        var_GRIB_lvl_typ = '224'
    elif var_level == 'high':
        var_GRIB_lvl_typ = '234'
    elif var_level == 'convective':
        var_GRIB_lvl_typ = '244'
    elif var_level == 'lowcloudbase':
        var_GRIB_lvl_typ = '212'
    elif var_level == 'midcloudbase':
        var_GRIB_lvl_typ = '222'
    elif var_level == 'highcloudbase':
        var_GRIB_lvl_typ = '232'
    elif var_level == 'convectivecloudbase':
        var_GRIB_lvl_typ = '242'
    elif var_level == 'lowcloudtop':
        var_GRIB_lvl_typ = '213'
    elif var_level == 'midcloudtop':
        var_GRIB_lvl_typ = '223'
    elif var_level == 'highcloudtop':
        var_GRIB_lvl_typ = '233'
    elif var_level == 'convectivecloudtop':
        var_GRIB_lvl_typ = '243'
    elif var_level == 'tropopause':
        var_GRIB_lvl_typ = '7'
    elif var_level == 'maxwindlev':
        var_GRIB_lvl_typ = '6'
    elif var_level == 'highesttropfrzlev':
        var_GRIB_lvl_typ = '204'
    # Get settings
    if var_name == '4LFTX': #best (4 layer) lifted index (K)
        cmap = plt.cm.magma
        if var_GRIB_lvl_typ == '1': #surface
            var_info_title = 'Surface Best (4-Layer) Lifted Index (K)'
            levels = np.array([-20,-15,-10,-8,-6,-4,-2,-1,1,2,4,6,8,10,15,20])
            levels_diff = np.array(
                [-3,-2,-1.5,-1,-0.5,-0.1,0,0.1,0.5,1,1.5,2,3]
            )
            var_scale = 1
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'ACPCP': #Convective precipitation (kg m-2)
        cmap = plt.cm.terrain_r
        if var_GRIB_lvl_typ == '1': #surface
            var_info_title = (
                'Surface Convective Precipitation '
                +'(kg 'r'$\mathregular{m^{-2}}$'')'
            )
            levels = np.array([0.1,0.2,0.4,0.6,0.8,1,1.5,2,2.5,3])
            levels_diff = np.array(
                [-1.5,-1.2,-0.9,-0.6,-0.3,-0.1,0,0.1,0.3,0.6,0.9,1.2,1.5]
            )
            var_scale = 1
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'ALBDO': #albedo (%)
        cmap = plt.cm.CMRmap
        if var_GRIB_lvl_typ == '1': #surface
            var_info_title = 'Surface Albedo (%)'
            levels = np.array([5,10,15,20,25,30,35,40,45,50])
            levels_diff = np.array(
                [-3,-2,-1.5,-1,-0.5,-0.1,0,0.1,0.5,1,1.5,2,3]
            )
            var_scale = 1
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'APCP': #total precipitation (kg m-2)
        cmap = plt.cm.terrain_r
        if var_GRIB_lvl_typ == '1': #surface
            var_info_title = (
                'Surface Total Precipitation '
                +'(kg 'r'$\mathregular{m^{-2}}$'')'
            )
            levels = np.array([0.1,0.2,0.4,0.6,0.8,1,1.5,2,2.5,3])
            levels_diff = np.array(
                [-1.5,-1.2,-0.9,-0.6,-0.3,-0.1,0,0.1,0.3,0.6,0.9,1.2,1.5]
            )
            var_scale = 1
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'CAPE': #convective available potential energy (CAPE) (J kg-1)
        cmap = plt.cm.RdPu
        if var_GRIB_lvl_typ == '1': #surface
            var_info_title = (
                'Surface Convective Available Potential Energy '
                +'(J 'r'$\mathregular{kg^{-1}}$'')'
            )
            levels = np.array(
                [100,300,500,700,900,1000,1200,1300,1400,1500,1600,1700,1800]
            )
            levels_diff = np.array(
                [-300,-200,-100,-50,-30,-10,0,10,30,50,100,200,300]
            )
            var_scale = 1
        elif var_GRIB_lvl_typ == '116': #layer between two levels at specified pressure difference from ground to level (hPa)
            var_info_title = (
                var_level.replace('hPaAGL', '')+' hPa Above Ground '
                +'Convective Available Potential Energy '
                +'(J 'r'$\mathregular{kg^{-1}}$'')'
            )
            levels = np.array(
                [100,300,500,700,900,1000,1200,1300,1400,1500,1600,1700,1800]
            )
            levels_diff = np.array(
                [-300,-200,-100,-50,-30,-10,0,10,30,50,100,200,300]
            )
            var_scale = 1
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'CIN': #convective inhibition (CIN)(J kg-1)
        cmap = plt.cm.RdPu_r
        if var_GRIB_lvl_typ == '1': #surface
            var_info_title = (
                'Surface Convective Inhibition '
                +'(J 'r'$\mathregular{kg^{-1}}$'')'
            )
            levels = np.array(
                [-500,-450,-400,-350,-300,-250,-200,-150,-100,-50,-25]
            )
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 1
        elif var_GRIB_lvl_typ == '116': #layer between two levels at specified pressure difference from ground to level (hPa)
            var_info_title = (
                var_level.replace('hPaAGL', '')+' hPa Above Ground '
                +'Convective Inhibition '
                +'(J 'r'$\mathregular{kg^{-1}}$'')'
            )
            levels = np.array(
                [-500,-450,-400,-350,-300,-250,-200,-150,-100,-50,-25]
            )
            levels_diff = np.array(
                [-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30]
            )
            var_scale = 1
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'CLWMR': #cloud water mixing ratio (kg kg-1)
        cmap = plt.cm.Blues
        if var_GRIB_lvl_typ == '100': #isobaric/pressure levels (hPa)
            var_info_title = var_level+' Cloud Water Mixing Ratio (ppmg)'
            levels = np.array([0.5,1,5,10,20,40,60,80,100,120,140])
            levels_diff = np.array(
                [-40,-20,-10,-6,-3,-1,-0.1,0,0.1,1,3,6,10,20,40]
            )
            var_scale = 1000000
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'CWAT': #cloud water (kg m-2)
        cmap = plt.cm.BuGn
        if var_GRIB_lvl_typ == '200': #entire atmosphere/column
            var_info_title = (
                'Atmospheric Column Cloud Water '
                +'(g 'r'$\mathregular{m^{-2}}$'')'
            )
            levels = np.array([20,40,60,80,100,120,140,160,180,200])
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 1000
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'CWORK': #cloud work function (J kg-1)
        cmap = plt.cm.BuGn
        if var_GRIB_lvl_typ == '200': #entire atmosphere/column
            var_info_title = (
                'Atmospheric Column Cloud Work Function '
                +'(J 'r'$\mathregular{kg^{-1}}$'')'
            )
            levels = np.array([10,20,40,60,80,100,120,140,160,180])
            levels_diff = np.array([-30,-25,-20,-15,-10,-5,0,5,10,15,20,25,30])
            var_scale = 1
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'DLWRF': #downward longwave radiation flux (W m-2)
        cmap = plt.cm.gist_heat_r
        if var_GRIB_lvl_typ == '1': #surface
            var_info_title = (
                'Surface Downward Longwave Flux '
                +'(W 'r'$\mathregular{m^{-2}}$'')'
            )
            levels = np.array([5,10,50,100,150,200,250,300,350,400,450,500])
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 1
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'DPT': #dewpoint temperature (K)
        cmap = plt.cm.Greens
        if var_GRIB_lvl_typ == '105': #height level above ground (m)
            var_info_title = (
                var_level.replace('mAGL', '')
                +'m Above Ground Level Dewpoint Temperature (K)'
            )
            levels = np.array(
                [240,245,250,255,260,265,270,275,280,285,290,295,300]
            )
            levels_diff = np.array([-5,-4,-3,-2,-1,-0.5,0,0.5,1,2,3,4,5])
            var_scale = 1
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'DSWRF': #downward shortwave radiation flux (W m-2)
        cmap = plt.cm.gist_heat_r
        if var_GRIB_lvl_typ == '1': #surface
            var_info_title = (
                'Surface Downward Shortwave Flux '
                +'(W 'r'$\mathregular{m^{-2}}$'')'
            )
            levels = np.array([5,10,50,100,150,200,250,300,350,400,450,500])
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 1
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'FLDCP': #field capacity (fraction)
        cmap = plt.cm.PuBuGn
        if var_GRIB_lvl_typ == '1': #surface
            var_info_title = 'Surface Field Capacity (fraction)' 
            levels = np.array([0.01,0.02,0.04,0.06,0.08,0.1,0.2,0.4,0.6,0.8,1])
            levels_diff = np.array(
                [-1,-0.5,-0.1,-0.05,-0.01,0,0.01,0.05,0.1,0.5,1]
            )
            var_scale = 1
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'GFLUX': #ground heat flux (W m-2)
        cmap = plt.cm.PiYG
        if var_GRIB_lvl_typ == '1': #surface
            var_info_title = (
                'Surface Ground Heat Flux (W 'r'$\mathregular{m^{-2}}$'')'
            )
            levels = np.array([-30,-20,-15,-10,-5,-2,2,5,10,15,20,30])
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 1
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'GUST': #wind gust (m s-1)
        cmap = plt.cm.pink_r
        if var_GRIB_lvl_typ == '1': #surface
            var_info_title = (
                'Surface Wind Gust (m 'r'$\mathregular{s^{-1}}$'')'
            )
            levels = np.array([0.5,1,2,4,6,8,10,12,14,16,18,20])
            levels_diff = np.array([-3,-2,-1,-0.5,-0.2,0,0.2,0.5,1,2,3])
            var_scale = 1
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'HGT': #geopotential height (gpm)
        cmap = plt.cm.cubehelix_r
        if var_GRIB_lvl_typ == '1': #surface
            var_info_title = 'Surface Geopotential Height (gpm)'
            levels = np.array(
                [100,500,1000,1500,2000,2500,3000,3500,4000,4500,5000,6000,
                 7000,8000]
            )
            levels_diff = np.array(
                [-400,-200,-100,-50,-20,-10,0,10,20,50,100,200,400]
            )
            var_scale = 1
        elif var_GRIB_lvl_typ == '6': #maximum wind level
            var_info_title = 'Maximum Wind Level Geopotential Height (km)'
            levels = np.array([1,2,3,4,5,6,7,8,9,10,12,14,16,18])
            levels_diff = np.array(
                [-1,-0.8,-0.6,-0.4,-0.2,-0.1,0,0.1,0.2,0.4,0.6,0.8,1]
            )
            var_scale = 0.001
        elif var_GRIB_lvl_typ == '7': #tropopause
            var_info_title = 'Tropopause Geopotential Height (km)'
            levels = np.array([1,2,3,4,5,6,7,8,9,10,12,14,16,18])
            levels_diff = np.array(
                [-1,-0.8,-0.6,-0.4,-0.2,-0.1,0,0.1,0.2,0.4,0.6,0.8,1]
            )
            var_scale = 0.001
        elif var_GRIB_lvl_typ == '100': #isobaric/pressure levels (hPa)
            var_info_title = var_level+' Geopotential Height (gpm)'
            levels = np.nan
            levels_diff = np.array(
                [-120,-80,-40,-20,-10,-5,0,5,10,20,40,80,120]
            )
            var_scale = 1
        elif var_GRIB_lvl_typ == '204': #highest tropospheric freezing level
            var_info_title = (
                'Highest Tropospheric Freezing Level Geopotential Height (gpm)'
            )
            levels = np.array(
                [100,500,1000,1500,2000,2500,3000,3500,
                 4000,4500,5000,6000,7000,8000]
            )
            levels_diff = np.array(
                [-400,-200,-100,-50,-20,-10,0,10,20,50,100,200,400]
            )
            var_scale = 1
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'HINDEX': #haines index (no units)
        cmap = plt.cm.YlOrRd
        if var_GRIB_lvl_typ == '1': #surface
            var_info_title = 'Surface Haines Index'
            levels = np.array([1,2,3,4,5,6,7,8,9])
            levels_diff = np.array(
                [-3,-2,-1,-0.5,-0.1,-0.01,0,0.01,0.1,0.5,1,2,3]
            )
            var_scale = 1
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'HPBL': #planetary boundary layer height (m)
        cmap = plt.cm.cubehelix_r
        if var_GRIB_lvl_typ == '1': #surface
            var_info_title = 'Planetary Boundary Layer Height (m)'
            levels = np.array(
                [300,400,500,600,700,800,900,1000,1100,1200,1400,1600,1800]
            )
            levels_diff = np.array(
                [-600,-400,-200,-100,-50,-20,0,20,50,100,200,400,600]
            )
            var_scale = 1
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'ICAHT': #ICAO standard atmosphere reference height (m)
        cmap = plt.cm.cubehelix_r
        if var_GRIB_lvl_typ == '6': #maximum wind level
            var_info_title = (
                 'Maximum Wind Level '
                 +'ICAO Standard Atmosphere Reference Height (km)'
            )
            levels = np.array([1,2,3,4,5,6,7,8,9,10,12,14,16,18])
            levels_diff = np.array(
                [-1,-0.8,-0.6,-0.4,-0.2,-0.1,0,0.1,0.2,0.4,0.6,0.8,1]
            )
            var_scale = 0.001
        elif var_GRIB_lvl_typ == '7': #tropopause
            var_info_title = (
                 'Tropopause ICAO Standard Atmosphere Reference Height (km)'
            )
            levels = np.array([1,2,3,4,5,6,7,8,9,10,12,14,16,18])
            levels_diff = np.array(
                [-1,-0.8,-0.6,-0.4,-0.2,-0.1,0,0.1,0.2,0.4,0.6,0.8,1]
            )
            var_scale = 0.001
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'ICEC': #ice cover (proportion)
        cmap = plt.cm.Blues
        if var_GRIB_lvl_typ == '1': #surface
            var_info_title = (
                'Surface Ice Concentration (ice=1;no ice=0) (fraction)'
            )
            levels = np.array(
                [0.01,0.02,0.04,0.06,0.08,0.1,0.2,0.4,0.6,0.8,1]
            )
            levels_diff = np.array(
                [-1,-0.5,-0.1,-0.05,-0.01,0,0.01,0.05,0.1,0.5,1]
            )
            var_scale = 1
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'LFTX': #lifted index (K)
        cmap = plt.cm.magma
        if var_GRIB_lvl_typ == '1': #surface
            var_info_title = 'Surface Lifted Index (K)'
            levels = np.array([-20,-15,-10,-8,-6,-4,-2,-1,1,2,4,6,8,10,15,20])
            levels_diff = np.array(
                [-3,-2,-1.5,-1,-0.5,-0.1,0,0.1,0.5,1,1.5,2,3]
            )
            var_scale = 1
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'LHTFL': #latent heat net flux (W m-2)
        cmap = plt.cm.Reds
        if var_GRIB_lvl_typ == '1': #surface
            var_info_title = (
                'Surface Latent Heat Flux (W 'r'$\mathregular{m^{-2}}$'')'
            )
            levels = np.array([5,10,20,40,60,80,100,120,140,160,180,200])
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 1
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'MSLET': #mean sea-level pressure (NAM reduction) (Pa)
        cmap = plt.cm.rainbow
        if var_GRIB_lvl_typ == '102': #mean sea level
            var_info_title = (
                'Membrane Mean Sea Level Pressure, NAM reduction (hPa)'
            )
            levels = np.array(
                [960,965,970,975,980,985,990,995,1000,1005,1010,1015,1020]
            )
            levels_diff = np.array([-10,-5,-4,-3,-2,-1,0,1,2,3,4,5,10])
            var_scale = 0.01
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'O3MR': #ozone mixing ratio (kg kg-1)
        cmap = plt.cm.YlGnBu
        if var_GRIB_lvl_typ == '100': #isobaric/pressure levels (hPa)
            var_info_title = var_level+' Ozone Mixing Ratio (ppmg)'
            levels = np.nan
            levels_diff = np.array(
                [-5,-4,-3,-2,-1,-0.5,0,0.5,1,2,3,4,5]
            )
            var_scale = 1000000
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'PEVPR': #potential evaporation rate (W m-2)
        cmap = plt.cm.copper_r
        if var_GRIB_lvl_typ == '1': #surface
            var_info_title = (
                'Surface Potential Evaporation Rate '
                +'(W 'r'$\mathregular{m^{-2}}$'')'
            )
            levels = np.array([5,10,50,100,150,200,250,300,350,400,450,500])
            levels_diff = np.array(
                [-50,-30,-20,-15,-10,-5,0,5,10,15,20,30,50]
            )
            var_scale = 1
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'POT': #potential temperature (K)
        cmap = plt.cm.rainbow
        if var_GRIB_lvl_typ == '107': #sigma level (sigma value in 1/10000)
            var_info_title = (
                var_level.replace('sigma', '')+' '
                +'Sigma Level Potential Temperature (K)'
            )
            levels = np.array(
                [240,245,250,255,260,265,270,275,280,285,290,295,300]
            )
            levels_diff = np.array([-5,-3,-2,-1,-0.5,-0.1,0,0.1,0.5,1,2,3,5])
            var_scale = 1
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'PRES': #pressure (Pa)
        cmap = plt.cm.Spectral_r
        if var_GRIB_lvl_typ == '1': #surface
            var_info_title = 'Surface Pressure (hPa)'
            levels = np.array(
                [500,550,600,650,700,750,800,850,900,950,1000,1010]
            )
            levels_diff = np.array([-10,-5,-4,-3,-2,-1,0,1,2,3,4,5,10])
            var_scale = 0.01
        elif var_GRIB_lvl_typ == '6': #maximum wind level
            var_info_title = 'Maximum Wind Level Pressure (hPa)'
            levels = np.array(
                [10,50,100,120,140,160,180,200,220,240,260,280,300]
            )
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 0.01
        elif var_GRIB_lvl_typ == '7': #tropopause
            var_info_title = 'Tropopause Pressure (hPa)'
            levels = np.array([100,120,140,160,180,200,220,240,260,280,300])
            levels_diff = np.array([-20,-15,-10,-5,-2,-1,0,1,2,5,10,15,20])
            var_scale = 0.01
        elif var_GRIB_lvl_typ == '212': #low cloud bottom level
            var_info_title = 'Low Cloud Base Pressure (hPa)'
            levels = np.array(
                [780,800,820,840,860,880,900,920,940,960,980,1000,1020]
            )
            levels_diff = np.array([-20,-15,-10,-5,-2,-1,0,1,2,5,10,15,20])
            var_scale = 0.01
        elif var_GRIB_lvl_typ == '213': #low cloud top level
            var_info_title = 'Low Cloud Top Pressure (hPa)'
            levels = np.array(
                [600,620,640,660,680,700,720,740,760,780,800,820,840]
            )
            levels_diff = np.array([-20,-15,-10,-5,-2,-1,0,1,2,5,10,15,20])
            var_scale = 0.01
        elif var_GRIB_lvl_typ == '222': #mid cloud bottom level
            var_info_title = 'Mid Cloud Base Pressure (hPa)'
            levels = np.array(
                [460,480,500,520,540,560,580,600,620,640,660,680,700]
            )
            levels_diff = np.array([-20,-15,-10,-5,-2,-1,0,1,2,5,10,15,20])
            var_scale = 0.01
        elif var_GRIB_lvl_typ == '223': #mid cloud top level
            var_info_title = 'Mid Cloud Top Pressure (hPa)'
            levels = np.array(
                [300,320,340,360,380,400,420,440,460,480,500,520,540]
            )
            levels_diff = np.array([-20,-15,-10,-5,-2,-1,0,1,2,5,10,15,20])
            var_scale = 0.01
        elif var_GRIB_lvl_typ == '232': #high cloud bottom level
            var_info_title = 'High Cloud Base Pressure (hPa)'
            levels = np.array(
                [180,200,220,240,260,280,300,320,340,360,380,400,420]
            )
            levels_diff = np.array([-20,-15,-10,-5,-2,-1,0,1,2,5,10,15,20])
            var_scale = 0.01
        elif var_GRIB_lvl_typ == '233': #high cloud top level
            var_info_title = 'High Cloud Top Pressure (hPa)'
            levels = np.array(
                [80,100,120,140,160,180,200,220,240,260,280,300,320]
            )
            levels_diff = np.array([-20,-15,-10,-5,-2,-1,0,1,2,5,10,15,20])
            var_scale = 0.01
        elif var_GRIB_lvl_typ == '242': #convective cloud bottom level
            var_info_title = 'Convective Cloud Base Pressure (hPa)'
            levels = np.array(
                [780,800,820,840,860,880,900,920,940,960,980,1000,1020]
            )
            levels_diff = np.array([-20,-15,-10,-5,-2,-1,0,1,2,5,10,15,20])
            var_scale = 0.01
        elif var_GRIB_lvl_typ == '243': #convective cloud top level
            var_info_title = 'Convective Cloud Top Pressure (hPa)'
            levels = np.array(
                [150,200,250,300,350,400,450,500,550,600,650,700,800,850]
            )
            levels_diff = np.array([-20,-15,-10,-5,-2,-1,0,1,2,5,10,15,20])
            var_scale = 0.01
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'PRMSL': #pressure reduced to MSL (Pa)
        cmap = plt.cm.rainbow
        if var_GRIB_lvl_typ == '102': #mean sea level
            var_info_title = 'Pressure Reduced to Mean Sea Level (hPa)'
            levels = np.array(
                [960,965,970,975,980,985,990,995,1000,1005,1010,1015,1020]
            )
            levels_diff = np.array([-10,-5,-4,-3,-2,-1,0,1,2,3,4,5,10])
            var_scale = 0.01
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'PWAT': #precipitable water (kg m-2)
        cmap = plt.cm.BuGn
        if var_GRIB_lvl_typ == '200': #entire atmosphere/column
            var_info_title = (
                'Atmospheric Column Precipitable Water '
                +'(kg 'r'$\mathregular{m^{-2}}$'')'
            )
            levels = np.array([5,10,15,20,25,30,35,40,45,50])
            levels_diff = np.array([-10,-5,-4,-3,-2,-1,0,1,2,3,4,5,10])
            var_scale = 1
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'RH': #relative humidity (%)
        cmap = plt.cm.Greens
        if var_GRIB_lvl_typ == '100': #isobaric/pressure levels (hPa)
            var_info_title = var_level+' Relative Humidity (%)'
            levels = np.array([1,5,10,30,50,70,90])
            levels_diff = np.array(
                [-50,-40,-30,-20,-10,-5,0,5,10,20,30,40,50]
            )
            var_scale = 1
        elif var_GRIB_lvl_typ == '105': #height level above ground (m)
            var_info_title = (
                var_level.replace('mAGL', '')
                +'m Above Ground Relative Humidity (%)'
            )
            levels = np.array([10,20,30,40,50,60,70,80,90,100])
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 1
        elif var_GRIB_lvl_typ == '107': #sigma level (sigma value in 1/10000)
            var_info_title = (
                var_level.replace('sigma', '')+' '
                +'Sigma Level Relative Humidity (%)'
            )
            levels = np.array([10,20,30,40,50,60,70,80,90,100])
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 1
        elif var_GRIB_lvl_typ == '200': #entire atmosphere/column
            var_info_title = 'Atmospheric Column Relative Humidity (%)'
            levels = np.array([10,20,30,40,50,60,70,80,90,100])
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 1
        elif var_GRIB_lvl_typ == '204': #highest tropospheric freezing level
            var_info_title = (
                'Highest Tropospheric Freezing Level Relative Humidity (%)'
            )
            levels = np.array([10,20,30,40,50,60,70,80,90,100])
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 1
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'SHTFL': #sensible heat net flux (W m-2)
        cmap = plt.cm.Reds
        if var_GRIB_lvl_typ == '1': #surface
            var_info_title = (
                'Surface Sensible Heat Flux (W 'r'$\mathregular{m^{-2}}$'')'
            )
            levels = np.array([5,10,20,40,60,80,100,120,140,160,180,200])
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 1
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'SNOD': #snow depth (m)
        cmap = plt.cm.Blues
        if var_GRIB_lvl_typ == '1': #surface
            var_info_title = 'Surface Snow Depth (cm)'
            levels = np.array([1,5,10,20,40,60,80,100,150,200,250])
            levels_diff = np.array(
                [-40,-20,-10,-5,-1,-0.1,0,0.1,1,5,10,20,40]
            )
            var_scale = 100
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'SOILW': #volumetric soil moisture content (fraction)
        cmap = plt.cm.summer_r
        if var_GRIB_lvl_typ == '112': #layer between two depths below land surface (cm)
            var_info_title = (
                var_level.replace('cmUGL', '')
                +'cm Under Ground Volumetric Soil Moisture (fraction)'
            )
            levels = np.array([10,20,30,40,50,60,70,80,90,100])
            levels_diff = np.array([-20,-15,-10,-5,-3,-1,0,1,3,5,10,15,20])
            var_scale = 100
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'SPFH': #specific humidity (kg kg-1)
        cmap = plt.cm.Greens
        if var_GRIB_lvl_typ == '105': #height level above ground (m)
            var_info_title = (
                var_level.replace('mAGL', '')
                +'m Above Ground Specific Humidity '
                +'(g 'r'$\mathregular{kg^{-1}}$'')'
            )
            levels = np.array([1,2,4,6,8,10,12,14,16,18])
            levels_diff = np.array(
                [-3,-2,-1,-0.6,-0.3,-0.1,0,0.1,0.3,0.6,1,2,3]
            )
            var_scale = 1000
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'SUNSD': #sunshine Duration (s)
        cmap = plt.cm.YlOrBr
        if var_GRIB_lvl_typ == '1': #surface
            var_info_title = 'Surface Sunshine Duration (hour)'
            levels = np.array([0.01,0.05,0.1,0.5,1,2,3,4,5,6])
            levels_diff = np.array([-2,-1,-0.5,-0.1,0,0.1,0.5,1,2])
            var_scale = (1./360.)
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'TCDC': #total cloud cover (%)
        cmap = plt.cm.Blues
        if var_GRIB_lvl_typ == '200': #entire atmosphere/column
            var_info_title = 'Atmospheric Column Total Cloud Cover (%)'
            levels = np.array([0,10,20,30,40,50,60,80,100])
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30]) 
            var_scale = 1
        elif var_GRIB_lvl_typ == '211': #boundary layer cloud layer
            var_info_title = 'Boundary Layer Total Cloud Cover (%)'
            levels = np.array([0,10,20,30,40,50,60,80,100])
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 1
        elif var_GRIB_lvl_typ == '214': #low layer cloud layer
            var_info_title = 'Low Cloud Layer Total Cloud Cover (%)'
            levels = np.array([0,10,20,30,40,50,60,80,100])
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 1
        elif var_GRIB_lvl_typ == '224': #mid layer cloud layer
            var_info_title = 'Mid Cloud Layer Total Cloud Cover (%)'
            levels = np.array([0,10,20,30,40,50,60,80,100])
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 1
        elif var_GRIB_lvl_typ == '234': #high layer cloud layer
            var_info_title = 'High Cloud Layer Total Cloud Cover (%)'
            levels = np.array([0,10,20,30,40,50,60,80,100])
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 1
        elif var_GRIB_lvl_typ == '244': #convective layer cloud layer
            var_info_title = 'Convective Cloud Layer Total Cloud Cover (%)'
            levels = np.array([0,10,20,30,40,50,60,80,100])
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 1
    elif var_name == 'TMAX': #maximum temperature (K)
        cmap = plt.cm.rainbow
        if var_GRIB_lvl_typ == '105': #height level above ground (m)
            var_info_title = (
                var_level.replace('mAGL', '')
                +'m Above Ground Maximum Temperature (K)'
            )
            levels = np.array(
                [240,245,250,255,260,265,270,275,280,285,290,295,300]
            )
            levels_diff = np.array(
                [-5,-4,-3,-2,-1,-0.5,-0.1,0,0.1,0.5,1,2,3,4,5]
            )
            var_scale = 1
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'TMIN': #minimum temperature (K)
        cmap = plt.cm.rainbow
        if var_GRIB_lvl_typ == '105': #height level above ground (m)
            var_info_title = (
                var_level.replace('mAGL', '')
                +'m Above Ground Minimum Temperature (K)'
            )
            levels = np.array(
                [240,245,250,255,260,265,270,275,280,285,290,295,300]
            )
            levels_diff = np.array(
                [-5,-4,-3,-2,-1,-0.5,-0.1,0,0.1,0.5,1,2,3,4,5]
            )
            var_scale = 1
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'TMP': #temperature (K)
        cmap = plt.cm.rainbow
        if var_GRIB_lvl_typ == '1': #surface
            var_info_title = 'Surface Skin Temperature (K)'
            levels = np.array(
                [240,245,250,255,260,265,270,275,280,285,290,295,300]
            )
            levels_diff = np.array(
                [-5,-4,-3,-2,-1,-0.5,-0.1,0,0.1,0.5,1,2,3,4,5]
            )
            var_scale = 1
        elif var_GRIB_lvl_typ == '6': #maximum wind level
            var_info_title = 'Maximum Wind Level Temperature (K)'
            levels = np.array(
                [160,180,185,190,195,200,205,210,215,220,225,230,235,240]
            )
            levels_diff = np.array([-5,-3,-2,-1,-0.5,-0.1,0,0.1,0.5,1,2,3,5])
            var_scale = 1
        elif var_GRIB_lvl_typ == '7': #tropopause
            var_info_title = 'Tropopause Temperature (K)'
            levels = np.array(
                [160,180,185,190,195,200,205,210,215,220,225,230,235,240]
            )
            levels_diff = np.array([-5,-3,-2,-1,-0.5,-0.1,0,0.1,0.5,1,2,3,5])
            var_scale = 1
        elif var_GRIB_lvl_typ == '100': #isobaric/pressure levels (hPa)
            var_info_title = var_level+' Temperature (K)'
            levels = np.nan
            levels_diff = np.array(
                [-4,-3,-2,-1,-0.5,-0.1,0,0.1,0.5,1,2,3,4]
            )
            var_scale = 1
        elif var_GRIB_lvl_typ == '105': #height level above ground (m)
            var_info_title = (
                var_level.replace('mAGL', '')
                +'m Above Ground Temperature (K)'
            )
            levels = np.array(
                [240,245,250,255,260,265,270,275,280,285,290,295,300]
            )
            levels_diff = np.array(
                [-5,-4,-3,-2,-1,-0.5,-0.1,0,0.1,0.5,1,2,3,4,5]
            )
            var_scale = 1
        elif var_GRIB_lvl_typ == '107': #sigma level (sigma value in 1/10000)
            var_info_title = (
                var_level.replace('sigma', '')+' '
                +'Sigma Level Temperature (K)'
            )
            levels = np.array(
                [240,245,250,255,260,265,270,275,280,285,290,295,300]
            )
            levels_diff = np.array([-5,-3,-2,-1,-0.5,-0.1,0,0.1,0.5,1,2,3,5])
            var_scale = 1
        elif var_GRIB_lvl_typ == '213': #low cloud top level
            var_info_title = 'Low Cloud Top Temperature (K)'
            levels = np.array(
                [220,225,230,235,240,245,250,255,260,265,270,275,280]
            )
            levels_diff = np.array([-5,-3,-2,-1,-0.5,-0.1,0,0.1,0.5,1,2,3,5])
            var_scale = 1
        elif var_GRIB_lvl_typ == '223': #mid cloud top level
            var_info_title = 'Mid Cloud Top Temperature (K)'
            levels = np.array(
                [200,205,210,215,220,225,230,235,240,245,250,255,260]
            )
            levels_diff = np.array([-5,-3,-2,-1,-0.5,-0.1,0,0.1,0.5,1,2,3,5])
            var_scale = 1
        elif var_GRIB_lvl_typ == '233': #high cloud top level
            var_info_title = 'High Cloud Top Temperature (K)'
            levels = np.array(
                [180,185,190,195,200,205,210,215,220,225,230,235,240]
            )
            levels_diff = np.array([-5,-3,-2,-1,-0.5,-0.1,0,0.1,0.5,1,2,3,5])
            var_scale = 1
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'TOZNE': #total ozone (Dobson)
        cmap = plt.cm.summer_r
        if var_GRIB_lvl_typ == '200': #entire atmosphere/column
            var_info_title = 'Atmospheric Column Total Ozone (Dobson)'
            levels = np.array(
                [160,180,200,220,240,260,280,300,320,340,360,380]
            )
            levels_diff = np.array([-10,-5,-4,-3,-2,-1,0,1,2,3,4,5,10])
            var_scale = 1
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'TSOIL': #soil temperature (K)
        cmap = plt.cm.rainbow
        if var_GRIB_lvl_typ == '112': #layer between two depths below land surface (cm)
            var_info_title = (
                var_level.replace('cmUGL', '')
                +'cm Under Ground Soil Temperature (K)'
            )
            levels = np.array(
                [240,245,250,255,260,265,270,275,280,285,290,295,300]
            )
            levels_diff = np.array(
                [-5,-3,-2,-1,-0.5,-0.1,0,0.1,0.5,1,2,3,5]
            )
            var_scale = 1
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'UFLX': #momentum flux, u component (N m-2)
        cmap = plt.cm.PRGn
        if var_GRIB_lvl_typ == '1': #surface
            var_info_title = (
                'Surface Zonal Momentum Flux '
                +'(1000 * N 'r'$\mathregular{m^{-2}}$'')'
            )
            levels = np.array(
                [-200,-160,-120,-80,-40,-10,10,40,80,120,160,200]
            )
            levels_diff = np.array(
                [-100,-50,-30,-20,-10,-5,0,5,10,20,30,50,100]
            )
            var_scale = 1000
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'UGRD': #zonal wind (m s-1)
        cmap = plt.cm.PRGn
        if var_GRIB_lvl_typ == '6': #maximum wind level
            var_info_title = (
                 'Maximum Wind Level Zonal Wind '
                 +'(m 'r'$\mathregular{s^{-1}}$'')'
            )
            levels = np.array(
                [-50,-40,-30,-20,-10,-5,-3,-1,1,3,5,10,20,30,40,50]
            )
            levels_diff = np.array([-20,-10,-5,-3,-2,-1,0,1,2,3,5,10,20])
            var_scale = 1
        elif var_GRIB_lvl_typ == '7': #tropopause
            var_info_title = (
                 'Tropopause Zonal Wind '
                 +'(m 'r'$\mathregular{s^{-1}}$'')'
            )
            levels = np.array(
               [-50,-40,-30,-20,-10,-5,-3,-1,1,3,5,10,20,30,40,50]
            )
            levels_diff = np.array([-10,-5,-3,-2,-1,-0.5,0,0.5,1,2,3,5,10])
            var_scale = 1
        elif var_GRIB_lvl_typ == '100': #isobaric/pressure levels (hPa)
            var_info_title = (
                var_level+' Zonal Wind (m 'r'$\mathregular{s^{-1}}$'')'
            )
            levels = np.array(
                [-100,-70,-50,-30,-20,-10,-5,5,10,20,30,50,70,100]
            )
            levels_diff = np.array(
                [-10,-7,-5,-3,-2,-1,0,1,2,3,5,7,10]
            )
            var_scale = 1
        elif var_GRIB_lvl_typ == '105': #height level above ground (m)
            var_info_title = (
                var_level.replace('mAGL', '')
                +'m Above Ground Zonal Wind (m 'r'$\mathregular{s^{-1}}$'')'
            )
            levels = np.array(
                [-50,-40,-30,-20,-10,-5,-3,-1,1,3,5,10,20,30,40,50]
            )
            levels_diff = np.array([-10,-5,-3,-2,-1,-0.5,0,0.5,1,2,3,5,10])
            var_scale = 1
        elif var_GRIB_lvl_typ == '107': #sigma level (sigma value in 1/10000)
            var_info_title = (
                var_level.replace('sigma', '')+' '
                +'Sigma Level Zonal Wind (m 'r'$\mathregular{s^{-1}}$'')'
            )
            levels = np.array(
                [-50,-40,-30,-20,-10,-5,-3,-1,1,3,5,10,20,30,40,50]
            )
            levels_diff = np.array([-10,-5,-3,-2,-1,-0.5,0,0.5,1,2,3,5,10])
            var_scale = 1
        elif var_GRIB_lvl_typ == '220': #planetary Boundary Layer (derived from Richardson number)
            var_info_title = (
                'Planetary Boundary Layer Level Zonal Wind '
                +'(m 'r'$\mathregular{s^{-1}}$'')'
            )
            levels = np.array(
                [-50,-40,-30,-20,-10,-5,-3,-1,1,3,5,10,20,30,40,50]
            )
            levels_diff = np.array([-10,-5,-3,-2,-1,-0.5,0,0.5,1,2,3,5,10])
            var_scale = 1
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'U-GWD': #zonal flux of gravity wave stress (N m-2)
        cmap = plt.cm.PuRd
        if var_GRIB_lvl_typ == '1': #surface
            var_info_title = (
                'Surface Zonal Gravity Wave Stress '
                +'(1000 * N 'r'$\mathregular{m^{-2}}$'')'
            )
            levels = np.array([5,10,20,40,60,80,100,120,140,160,180])
            levels_diff = np.array(
                [-50,-30,-20,-10,-5,-2,0,2,5,10,20,30,50]
            )
            var_scale = 1000
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'ULWRF': #upward longwave radiation flux (W m-2)
        cmap = plt.cm.gist_heat_r
        if var_GRIB_lvl_typ == '1': #surface
            var_info_title = (
                'Surface Upward Longwave Flux '
                +'(W 'r'$\mathregular{m^{-2}}$'')'
            )
            levels = np.array([5,10,50,100,150,200,250,300,350,400,450,500])
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 1
        elif var_GRIB_lvl_typ == '8': #nominal top of atmosphere
            var_info_title = ( 
                'Top of Atmosphere Upward Longwave Flux '
                +'(W 'r'$\mathregular{m^{-2}}$'')'
            )
            levels = np.array([5,10,50,100,150,200,250,300,350,400,450,500])
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 1
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'USWRF': #upward shortwave radiation flux (W m-2)
        cmap = plt.cm.gist_heat_r
        if var_GRIB_lvl_typ == '1': #surface
            var_info_title = (
                'Surface Upward Shortwave Flux '
                +'(W 'r'$\mathregular{m^{-2}}$'')'
            )
            levels = np.array([5,10,20,40,60,80,100,120,140,160,180,200,300])
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 1
        elif var_GRIB_lvl_typ == '8': #nominal top of atmosphere
            var_info_title = (
                'Top of Atmosphere Upward Shortwave Flux '
                +'(W 'r'$\mathregular{m^{-2}}$'')'
            )
            levels = np.array([5,10,20,40,60,80,100,120,140,160,180,200,300])
            levels_diff = np.array([-30,-20,-15,-10,-5,-2,0,2,5,10,15,20,30])
            var_scale = 1
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'VFLX': #momentum flux, v component (N m-2)
        cmap = plt.cm.PRGn
        if var_GRIB_lvl_typ == '1': #surface
            var_info_title = (
                'Surface Meridional Momentum Flux '
                +'(1000 * N 'r'$\mathregular{m^{-2}}$'')'
            )
            levels = np.array(
                [-200,-160,-120,-80,-40,-10,10,40,80,120,160,200]
            )
            levels_diff = np.array(
                [-100,-50,-30,-20,-10,-5,0,5,10,20,30,50,100]
            )
            var_scale = 1000
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'VGRD': #meridional wind (m s-1)
        cmap = plt.cm.PRGn
        if var_GRIB_lvl_typ == '6': #maximum wind level
            var_info_title = (
                 'Maximum Wind Level Meridional Wind '
                 +'(m 'r'$\mathregular{s^{-1}}$'')'
            )
            levels = np.array(
                [-50,-40,-30,-20,-10,-5,-3,-1,1,3,5,10,20,30,40,50]
            )
            levels_diff = np.array([-20,-10,-5,-3,-2,-1,0,1,2,3,5,10,20])
            var_scale = 1
        elif var_GRIB_lvl_typ == '7': #tropopause
            var_info_title = (
                 'Tropopause Meridional Wind '
                 +'(m 'r'$\mathregular{s^{-1}}$'')'
            )
            levels = np.array(
                [-50,-40,-30,-20,-10,-5,-3,-1,1,3,5,10,20,30,40,50]
            )
            levels_diff = np.array(
                [-10,-5,-3,-2,-1,-0.5,0,0.5,1,2,3,5,10]
            )
            var_scale = 1
        elif var_GRIB_lvl_typ == '100': #isobaric/pressure levels (hPa)
            var_info_title = (
                var_level+' Meridional Wind (m 'r'$\mathregular{s^{-1}}$'')'
            )
            levels = np.array(
                [-50,-30,-20,-10,-5,-1,1,5,10,20,30,50]
            )
            levels_diff = np.array(
                [-10,-7,-5,-3,-2,-1,-0.5,-0.2,0,0.2,0.5,1,2,3,5,7,10]
            )
            var_scale = 1
        elif var_GRIB_lvl_typ == '105': #height level above ground (m)
            var_info_title = (
                var_level.replace('mAGL', '')
                +'m Above Ground Meridional Wind '
                +'(m 'r'$\mathregular{s^{-1}}$'')'
            )
            levels = np.array(
                [-50,-40,-30,-20,-10,-5,-3,-1,1,3,5,10,20,30,40,50]
            )
            levels_diff = np.array([-10,-5,-3,-2,-1,-0.5,0,0.5,1,2,3,5,10])
            var_scale = 1
        elif var_GRIB_lvl_typ == '107': #sigma level (sigma value in 1/10000)
            var_info_title = (
                var_level.replace('sigma', '')+' '
                +'Sigma Level Meridional Wind (m 'r'$\mathregular{s^{-1}}$'')'
            )
            levels = np.array(
                [-50,-40,-30,-20,-10,-5,-3,-1,1,3,5,10,20,30,40,50]
            )
            levels_diff = np.array([-10,-5,-3,-2,-1,-0.5,0,0.5,1,2,3,5,10])
            var_scale = 1
        elif var_GRIB_lvl_typ == '220': #planetary Boundary Layer (derived from Richardson number)
            var_info_title = (
                'Planetary Boundary Layer Level Meridional Wind '
                +'(m 'r'$\mathregular{s^{-1}}$'')'
            )
            levels = np.array(
                [-50,-40,-30,-20,-10,-5,-3,-1,1,3,5,10,20,30,40,50]
            )
            levels_diff = np.array([-10,-5,-3,-2,-1,-0.5,0,0.5,1,2,3,5,10])
            var_scale = 1
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'V-GWD': #meridional flux of gravity wave stress (N m-2)
        cmap = plt.cm.PuRd
        if var_GRIB_lvl_typ == '1': #surface
            var_info_title = (
                'Surface Meridional Gravity Wave Stress '
                +'(1000 * N 'r'$\mathregular{m^{-2}}$'')'
            )
            levels = np.array([5,10,20,40,60,80,100,120,140,160,180])
            levels_diff = np.array([-50,-30,-20,-10,-5,-2,0,2,5,10,20,30,50])
            var_scale = 1000
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'VIS': #visibility (m)
        cmap = plt.cm.gray
        if var_GRIB_lvl_typ == '1': #surface
            var_info_title = 'Surface Visibility (km)'
            levels = np.array([1,2,4,6,8,10,15,20])
            levels_diff = np.array([-4,-3,-2,-1,-0.5,-0.1,0,0.1,0.5,1,2,3,4])
            var_scale = 0.001
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'VRATE': #ventilation Rate (m2 s-1)
        cmap = plt.cm.magma_r
        if var_GRIB_lvl_typ == '220': #planetary Boundary Layer (derived from Richardson number)
            var_info_title = (
                'Planetary Boundaty Layer Level Ventilation Rate '
                +'('r'$\mathregular{km^{2}}$'' 'r'$\mathregular{s^{-1}}$'')'
            )
            levels = np.array([5,10,15,20,25,30,35,40,45])
            levels_diff = np.array([-15,-12,-9,-6,-3,-1,0,1,3,6,9,12,15])
            var_scale = 0.001
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'VVEL': #vertical velocity (Pa s-1)
        cmap = plt.cm.PRGn
        if var_GRIB_lvl_typ == '100': #isobaric/pressure levels (hPa)
            var_info_title = (
                var_level+' Vertical Velocity '
                +'(hPa 'r'$\mathregular{hour^{-1}}$'')'
            )
            levels = np.array([-4,-3,-2,-1,-0.5,-0.1,0.1,0.5,1,2,3,4])
            levels_diff = np.array([-4,-3,-2,-1,-0.5,-0.1,0,0.1,0.5,1,2,3,4])
            var_scale = 36
        elif var_GRIB_lvl_typ == '107': #sigma level (sigma value in 1/10000)
            var_info_title = (
                var_level.replace('sigma', '')+' Vertical Velocity '
                +'(hPa 'r'$\mathregular{hour^{-1}}$'')'
            )
            levels = np.array([-4,-3,-2,-1,-0.5,-0.1,0.1,0.5,1,2,3,4])
            levels_diff = np.array([-4,-3,-2,-1,-0.5,-0.1,0,0.1,0.5,1,2,3,4])
            var_scale = 36
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'VWSH': #vertical speed shear (s-1)
        cmap = plt.cm.PRGn
        if var_GRIB_lvl_typ == '7': #tropopause
            var_info_title = (
                'Tropopsause Vertical Speed Shear '
                +'('r'$\mathregular{hour^{-1}}$'')'
            )
            levels = np.array(
                [-100,-50,-40,-30,-20,-10,-5,-3,3,5,10,20,30,40,50,100]
            )
            levels_diff = np.array([-10,-5,-4,-3,-2,-1,0,1,2,3,4,5,10])
            var_scale = 3600
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'WATR': #water runoff (kg m-2)
        cmap = plt.cm.BuGn
        if var_GRIB_lvl_typ == '1': #surface
            var_info_title = (
                'Surface Water Runoff (kg 'r'$\mathregular{m^{-2}}$'')'
            )
            levels = np.array(
                [0.01,0.02,0.04,0.06,0.08,0.1,0.2,0.4,0.6,0.8,1]
            )
            levels_diff = np.array(
                [-1,-0.5,-0.1,-0.05,-0.01,0,0.01,0.05,0.1,0.5,1]
            )
            var_scale = 1
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'WEASD': #water equiv. of accum. snow depth (kg m-2)
        cmap = plt.cm.Blues
        if var_GRIB_lvl_typ == '1': #surface
            var_info_title = (
                'Surface Water Equivalent of Accum Snow Depth '
                +'(kg 'r'$\mathregular{m^{-2}}$'')'
            )
            levels = np.array([0.1,0.5,1,3,6,10,20,30,40,50,70,90])
            levels_diff = np.array([-8,-6,-4,-2,-1,-0.1,0,0.1,1,2,4,6,8])
            var_scale = 1
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    elif var_name == 'WILT': #wilting point (fraction)
        cmap = plt.cm.YlOrBr
        if var_GRIB_lvl_typ == '1': #surface
            var_info_title = 'Surface Wilting Point (fraction)'
            levels = np.array([0.01,0.02,0.04,0.06,0.08,0.1,0.2,0.4,0.6,0.8,1])
            levels_diff = np.array(
                [-1,-0.5,-0.1,-0.05,-0.01,0,0.01,0.05,0.1,0.5,1]
            )
            var_scale = 1
        else:
            print("ERROR: cannot find plot settings for "+var_name+" "
                  +"at "+var_GRIB_lvl_typ)
            exit(1)
    else:
        print("ERROR: cannot find plot settings for "+var_name)
        exit(1)
    return var_info_title, levels, levels_diff, cmap, var_scale
