from __future__ import (print_function, division)
import os
import numpy as np
import netCDF4 as netcdf
import re
import plot_util as plot_util
import maps2d_plot_util as maps2d_plot_util
import warnings
import logging
import datetime
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

warnings.filterwarnings('ignore')
plt.rcParams['font.weight'] = 'bold'
plt.rcParams['axes.labelsize'] = 15
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['xtick.labelsize'] = 15
plt.rcParams['ytick.labelsize'] = 15
plt.rcParams['axes.titlesize'] = 15
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.formatter.useoffset'] = False
###import cmocean
###cmap_diff = cmocean.cm.balance
cmap_diff = plt.cm.coolwarm
noaa_logo_img_array = matplotlib.image.imread(
    os.path.join(os.environ['USHverif_global'], 'plotting_scripts', 'noaa.png')
)

# Read in environment variables
DATA = os.environ['DATA']
RUN = os.environ['RUN']
make_met_data_by = os.environ['make_met_data_by']
plot_by = os.environ['plot_by']
START_DATE = os.environ['START_DATE']
END_DATE = os.environ['END_DATE']
forecast_to_plot = os.environ['forecast_to_plot']
hr_beg = os.environ['hr_beg']
hr_end = os.environ['hr_end']
hr_inc = os.environ['hr_inc']
latlon_area = os.environ['latlon_area'].split(' ')
var_group_name = os.environ['var_group_name']
var_name = os.environ['var_name']
var_levels = os.environ['var_levels'].split(', ')
verif_case_type = os.environ['verif_case_type']
if verif_case_type == 'gdas':
    regrid_to_grid = os.environ['regrid_to_grid']
    plot_stats_list = ['bias', 'rmse']
elif verif_case_type == 'ens':
    plot_stats_list = ['mean', 'spread']

# Set up information
py_map_pckg = os.environ['py_map_pckg']
if py_map_pckg == 'cartopy':
    import cartopy.crs as ccrs
    from cartopy.util import add_cyclic_point
    from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
elif py_map_pckg == 'basemap':
    from mpl_toolkits.basemap import Basemap, addcyclic
llcrnrlat_val = float(latlon_area[0])
urcrnrlat_val = float(latlon_area[1])
llcrnrlon_val = float(latlon_area[2])
urcrnrlon_val = float(latlon_area[3])
lat_ticks = np.linspace(llcrnrlat_val, urcrnrlat_val, 7, endpoint=True)
lon_ticks = np.linspace(llcrnrlon_val, urcrnrlon_val, 7, endpoint=True)
env_var_model_list = []
regex = re.compile(r'model(\d+)$')
for key in os.environ.keys():
    result = regex.match(key)
    if result is not None:
        env_var_model_list.append(result.group(0))
env_var_model_list = sorted(env_var_model_list, key=lambda m: m[-1])
nmodels = len(env_var_model_list)
make_met_data_by_hrs = []
hr = int(hr_beg) * 3600
while hr <= int(hr_end)*3600:
    make_met_data_by_hrs.append(str(int(hr/3600)).zfill(2)+'Z')
    hr+=int(hr_inc)
make_met_data_by_hrs_title = ', '.join(make_met_data_by_hrs)
if verif_case_type == 'gdas':
    forecast_to_plot_title = (
        'First Guess Hour '+forecast_to_plot
    )
elif verif_case_type == 'ens':
    forecast_to_plot_title = (
        'Forecast Hour '+forecast_to_plot
    )
else:
    forecast_to_plot_title = forecast_to_plot
START_DATE_dt = datetime.datetime.strptime(START_DATE, '%Y%m%d')
END_DATE_dt = datetime.datetime.strptime(END_DATE, '%Y%m%d')
dates_title = (make_met_data_by.lower()+' '
               +START_DATE_dt.strftime('%d%b%Y')+'-'
               +END_DATE_dt.strftime('%d%b%Y'))

# Get input and output directories
if verif_case_type == 'gdas':
    input_dir = os.path.join(DATA, RUN, 'metplus_output',
                             'make_met_data_by_'+make_met_data_by,
                             'series_analysis', verif_case_type,
                             var_group_name)
elif verif_case_type == 'ens':
     input_dir = os.path.join(DATA, RUN, 'data')
plotting_out_dir_imgs = os.path.join(DATA, RUN, 'metplus_output',
                                     'plot_by_'+plot_by,
                                     verif_case_type, var_group_name,
                                     'imgs')
if not os.path.exists(plotting_out_dir_imgs):
    os.makedirs(plotting_out_dir_imgs)

# Sigma pressure levels for 64 levels
# taken from VSDB plot2d/maps2d_ensspread.sh
levsn64p = np.array(
    [1000, 994, 988, 981, 974, 965, 955, 944, 932, 919, 903,
     887, 868, 848, 826, 803, 777, 750, 721, 690, 658, 624,
     590, 555, 520, 484, 449, 415, 381, 349, 317, 288, 260, 234, 209,
     187, 166, 148, 130, 115, 101, 88, 77, 67, 58, 50, 43, 37, 31,
     26, 22, 18, 15, 12, 10, 7.7, 5.8, 4.2, 2.9, 1.9, 1.1, 0.7, 0.3, 0.1]
)

# Loop of variables levels to create
# indivdual level lat-lon plots
for stat in plot_stats_list:
    if stat == 'bias':
        stat_title = 'Bias of GDAS Analysis Increments'
    elif stat == 'rmse':
        stat_title = 'Root Mean Square Error of GDAS Analysis Increments'
    elif stat == 'mean':
        stat_title = 'Ensemble Mean'
    elif stat == 'spread':
        stat_title = 'Ensemble Spread'
    for var_level in var_levels:
        var_info_title, levels, levels_diff, cmap, var_scale = (
            maps2d_plot_util.get_maps2d_plot_settings(var_name, var_level)
        )
        model_num = 0
        print("Working on lat-lon error plots for "+stat+" "
              +var_name+" "+var_level)
        for env_var_model in env_var_model_list:
            model_num+=1
            model = os.environ[env_var_model]
            model_plot_name = os.environ[env_var_model+'_plot_name']
            if verif_case_type == 'gdas':
                model_obtype = os.environ[env_var_model+'_obtype']
                input_file = os.path.join(
                    input_dir, model,
                    forecast_to_plot+'_'+var_name+'_'
                    +var_level.replace(' ', '')+'.nc'
                )
            elif verif_case_type == 'ens':
                model_suffix = os.environ[env_var_model+'_suffix']
                if forecast_to_plot == 'anl':
                    input_file = os.path.join(
                        input_dir, model,
                        'atmanl.ens'+stat+'.nc'
                    )
                else:
                    input_file = os.path.join(
                        input_dir, model,
                        'atmf0'+forecast_to_plot
                        +'.ens'+stat+'.nc'
                    )
            # Set up plot
            if model_num == 1:
                if verif_case_type == 'ens':
                    nsubplots = nmodels
                else:
                    nsubplots = nmodels + 1
                if nsubplots > 8:
                    print("Too many subplots requested. "
                          "Current maximum is 8.")
                    exit(1)
                if nsubplots == 1:
                    fig = plt.figure(figsize=(10,12))
                    gs = gridspec.GridSpec(1,1)
                elif nsubplots == 2:
                    fig = plt.figure(figsize=(10,12))
                    gs = gridspec.GridSpec(2,1)
                    gs.update(hspace=0.2)
                elif nsubplots > 2 and nsubplots <= 4:
                    fig = plt.figure(figsize=(20,12))
                    gs = gridspec.GridSpec(2,2)
                    gs.update(wspace=0.2, hspace=0.2)
                elif nsubplots > 4 and nsubplots <= 6:
                    fig = plt.figure(figsize=(30,12))
                    gs = gridspec.GridSpec(2,3)
                    gs.update(wspace=0.2, hspace=0.2)
                elif nsubplots > 6 and nsubplots <= 9:
                    fig = plt.figure(figsize=(30,18))
                    gs = gridspec.GridSpec(3,3)
                    gs.update(wspace=0.2, hspace=0.2)
                # Set up control analysis subplot map and title for gdas
                if verif_case_type == 'gdas':
                    if py_map_pckg == 'cartopy':
                        ax_cntrl = plt.subplot(gs[0],
                                               projection=ccrs.PlateCarree(
                                                   central_longitude=180
                                               ))
                        if urcrnrlon_val == 360:
                            urcrnrlon_val_adjust = 359.9
                        else:
                            urcrnrlon_val_adjust = urcrnrlon_val
                        ax_cntrl.set_extent(
                            [llcrnrlon_val, urcrnrlon_val_adjust,
                             llcrnrlat_val, urcrnrlat_val],
                            ccrs.PlateCarree()
                        )
                        ax_cntrl.set_global()
                        ax_cntrl.coastlines()
                        ax_cntrl.set_xlabel('Longitude')
                        ax_cntrl.set_xticks(lon_ticks, crs=ccrs.PlateCarree())
                        ax_cntrl.set_ylabel('Latitude')
                        ax_cntrl.set_yticks(lat_ticks, crs=ccrs.PlateCarree())
                        lon_formatter = LongitudeFormatter(
                            zero_direction_label=True
                        )
                        lat_formatter = LatitudeFormatter()
                        ax_cntrl.xaxis.set_major_formatter(lon_formatter)
                        ax_cntrl.yaxis.set_major_formatter(lat_formatter)
                    elif py_map_pckg == 'basemap':
                        ax_cntrl = plt.subplot(gs[0])
                        mc = Basemap(projection='cyl',
                                     llcrnrlat=llcrnrlat_val,
                                     urcrnrlat=urcrnrlat_val,
                                     llcrnrlon=llcrnrlon_val,
                                     urcrnrlon=urcrnrlon_val,
                                     resolution='c', lon_0=180, ax=ax_cntrl)
                        mc.drawcoastlines(linewidth=1.5, color='k', zorder=6)
                        mc.drawmapboundary
                        ax_cntrl.set_xlabel('Longitude')
                        ax_cntrl.set_ylabel('Latitude')
                        mc.drawmeridians(lon_ticks,
                                         labels=[False,False,False,True],
                                         fontsize=15)
                        mc.drawparallels(lat_ticks,
                                         labels=[True,False,False,False],
                                         fontsize=15)
                    ax_cntrl.set_title('A '+model_plot_name, loc='left')
            # Set up model subplot map and title
            if verif_case_type == 'ens':
                subplot_num =  model_num - 1
            else:
                subplot_num =  model_num
            if py_map_pckg == 'cartopy':
                ax = plt.subplot(gs[subplot_num], 
                                 projection=ccrs.PlateCarree(
                                     central_longitude=180
                                 ))
                if urcrnrlon_val == 360:
                    urcrnrlon_val_adjust = 359.9
                else:
                    urcrnrlon_val_adjust = urcrnrlon_val
                ax.set_extent(
                    [llcrnrlon_val, urcrnrlon_val_adjust,
                     llcrnrlat_val, urcrnrlat_val],
                    ccrs.PlateCarree()
                )
                ax.set_global()
                ax.coastlines()
                ax.set_xlabel('Longitude')
                ax.set_xticks(lon_ticks, crs=ccrs.PlateCarree())
                ax.set_ylabel('Latitude')
                ax.set_yticks(lat_ticks, crs=ccrs.PlateCarree())
                lon_formatter = LongitudeFormatter(zero_direction_label=True)
                lat_formatter = LatitudeFormatter()
                ax.xaxis.set_major_formatter(lon_formatter)
                ax.yaxis.set_major_formatter(lat_formatter)
            elif py_map_pckg == 'basemap':
                ax = plt.subplot(gs[subplot_num])
                m = Basemap(projection='cyl', llcrnrlat=llcrnrlat_val,
                            urcrnrlat=urcrnrlat_val, llcrnrlon=llcrnrlon_val,
                            urcrnrlon=urcrnrlon_val, resolution='c', lon_0=180,
                            ax=ax)
                m.drawcoastlines(linewidth=1.5, color='k', zorder=6)
                m.drawmapboundary
                ax.set_xlabel('Longitude')
                ax.set_ylabel('Latitude')
                m.drawmeridians(lon_ticks, labels=[False,False,False,True],
                                fontsize=15)
                m.drawparallels(lat_ticks, labels=[True,False,False,False],
                                fontsize=15)
            if stat == 'bias':
                ax.set_title('(A-B) '+model_plot_name, loc='left')
            elif stat == 'rmse':
                if model_num == 1:
                    model1 = model
                    model1_plot_name = model_plot_name
                    ax.set_title('RMSE(A-B) '+model1_plot_name, loc='left')
                else:
                    ax.set_title('RMSE(A-B) '+model_plot_name
                                 +'-'+model1_plot_name, loc='left')
            elif stat in ['mean', 'spread']:
                ax.set_title(model_plot_name, loc='left')
            # Read data
            if not os.path.exists(input_file):
                print("WARNING: "+input_file+" "
                      +"does not exist")
                if verif_case_type == 'gdas' and model_num == 1:
                    ax_cntrl.set_title(str(np.nan), loc='left') 
                ax.set_title(str(np.nan), loc='left')
            else:
                print(input_file+" exists")
                model_data = netcdf.Dataset(input_file)
                if verif_case_type == 'gdas':
                    model_data_lat = model_data.variables['lat'][:]
                    model_data_lon = model_data.variables['lon'][:]
                    model_data_variable_names = []
                    for var in model_data.variables:
                        model_data_variable_names.append(str(var))
                    if 'series_cnt_FBAR' in model_data_variable_names:
                        model_data_series_cnt_FBAR =  (
                            model_data.variables['series_cnt_FBAR'][:]
                            * var_scale
                        )
                    else:
                        print("WARNING: FBAR values for "+model+" "
                              +"not in file "+input_file
                              +"...setting to NaN")
                        model_data_series_cnt_FBAR = np.full(
                            (len(model_data_lat), len(model_data_lon)), np.nan
                        )
                    if 'series_cnt_OBAR' in model_data_variable_names:
                        model_data_series_cnt_OBAR =  (
                            model_data.variables['series_cnt_OBAR'][:]
                            * var_scale
                        )
                    else:
                        print("WARNING: OBAR values for "+model+" "
                              +"not in file "+input_file
                              +"...setting to NaN")
                        model_data_series_cnt_OBAR = np.full(
                            (len(model_data_lat), len(model_data_lon)), np.nan
                        ) 
                    if np.ma.is_masked(model_data_series_cnt_FBAR):
                        np.ma.set_fill_value(
                            model_data_series_cnt_FBAR, np.nan
                        )
                        model_data_series_cnt_FBAR = (
                            model_data_series_cnt_FBAR.filled()
                        )
                    if np.ma.is_masked(model_data_series_cnt_OBAR):
                        np.ma.set_fill_value(
                            model_data_series_cnt_OBAR, np.nan
                        )
                        model_data_series_cnt_OBAR = (
                            model_data_series_cnt_OBAR.filled()
                        )
                    if stat == 'bias':
                        stat_data = (
                            model_data_series_cnt_OBAR
                            - model_data_series_cnt_FBAR
                        )
                    elif stat == 'rmse':
                        if model_num == 1:
                            stat_data = np.sqrt(
                                (model_data_series_cnt_OBAR
                                 -model_data_series_cnt_FBAR)**2
                            )
                            model1_stat_data = stat_data
                        else:
                            stat_data = np.sqrt(
                                (model_data_series_cnt_OBAR
                                 -model_data_series_cnt_FBAR)**2
                            ) - model1_stat_data
                elif verif_case_type == 'ens':
                    if var_name != 'PRES':
                        # Get closest matching sigma level pressure
                        if model_suffix == 'nc4':
                            model_levels = levsn64p
                        else:
                            model_levels = model_data.variables['pfull'][:]
                        var_level_float = float(var_level.replace('hPa', ''))
                        model_levels_var_level_diff = np.abs(
                            model_levels - var_level_float
                        )
                        model_levels_var_level_diff_min_idx = np.where(
                            model_levels_var_level_diff \
                            == np.min(model_levels_var_level_diff)
                        )[0][0]
                        model_level = (
                            model_levels[model_levels_var_level_diff_min_idx]
                        )
                    # Get index data
                    if model_suffix == 'nc4':
                       model_data_lat = model_data.variables['lat'][:]
                       model_data_lon = model_data.variables['lon'][:]
                       if var_name == 'TMP':
                           model_data_var = (
                               model_data.variables['t']\
                               [model_levels_var_level_diff_min_idx,:,:]
                           )
                       elif var_name == 'UGRD':
                           model_data_var = (
                               model_data.variables['u']\
                               [model_levels_var_level_diff_min_idx,:,:]
                           )
                       elif var_name == 'VGRD':
                           model_data_var = (
                               model_data.variables['v']\
                               [model_levels_var_level_diff_min_idx,:,:]
                           )
                       elif var_name == 'SPFH':
                           model_data_var = (
                               model_data.variables['q']\
                               [model_levels_var_level_diff_min_idx,:,:]
                           )
                       elif var_name == 'CLWMR':
                           model_data_var = (
                               model_data.variables['cw']\
                               [model_levels_var_level_diff_min_idx,:,:]
                           )
                       elif var_name == 'O3MR':
                           model_data_var = (
                               model_data.variables['oz']\
                               [model_levels_var_level_diff_min_idx,:,:]
                           )
                       elif var_name == 'PRES':
                           model_data_var = model_data.variables['ps'][:]
                    elif model_suffix == 'nc':
                       model_data_lat = model_data.variables['grid_yt'][:]
                       model_data_lon = model_data.variables['grid_xt'][:]
                       if var_name == 'PRES':
                           model_data_var = (
                               model_data.variables['pressfsc'][0,:,:]
                           )
                       else:
                           model_data_var = (
                               model_data.variables[var_name.lower()]\
                               [0,model_levels_var_level_diff_min_idx,:,:]
                           )
                    if np.ma.is_masked(model_data_var):
                        np.ma.set_fill_value(model_data_var, np.nan)
                        model_data_var = (
                            model_data_var.filled()
                        )
                    stat_data = model_data_var  * var_scale
                # Plot model data
                # Add cyclic point for data
                if py_map_pckg == 'cartopy':
                    stat_data_cyc, model_data_lon_cyc = add_cyclic_point(
                        stat_data, coord=model_data_lon
                    )
                elif py_map_pckg == 'basemap':
                    stat_data_cyc, model_data_lon_cyc = addcyclic(
                        stat_data, model_data_lon
                    )
                x, y = np.meshgrid(model_data_lon_cyc, model_data_lat)
                if verif_case_type == 'gdas':
                    if model_num == 1:
                        print("Plotting "+model+" analysis")
                        cntrl_area_avg = (
                            maps2d_plot_util.calculate_area_average(
                                model_data_series_cnt_OBAR, model_data_lat,
                                model_data_lon, llcrnrlat_val, urcrnrlat_val,
                                llcrnrlon_val, urcrnrlon_val
                            )
                        )
                        ax_cntrl.set_title(round(cntrl_area_avg, 3),
                                           loc='right')
                        if np.all(np.isnan(levels)):
                            if np.isnan(np.nanmax(model_data_series_cnt_OBAR)):
                                levels_max = 1
                            else:
                                levels_max = int(
                                    np.nanmax(model_data_series_cnt_OBAR)
                                ) + 1
                            if np.isnan(np.nanmin(model_data_series_cnt_OBAR)):
                                levels_min = -1
                            else:
                                levels_min = int(
                                    np.nanmin(model_data_series_cnt_OBAR)
                                ) - 1
                            levels = np.linspace(levels_min, levels_max, 11,
                                                 endpoint=True)
                        # Add cyclic point for model data
                        if py_map_pckg == 'cartopy':
                            (model_data_series_cnt_OBAR_cyc,
                             model_data_lon_cyc) = add_cyclic_point(
                                model_data_series_cnt_OBAR,
                                coord=model_data_lon
                            )
                        elif py_map_pckg == 'basemap':
                            (model_data_series_cnt_OBAR_cyc,
                             model_data_lon_cyc) = addcyclic(
                                model_data_series_cnt_OBAR,
                                model_data_lon
                              )
                        if np.count_nonzero(~np.isnan(
                                model_data_series_cnt_OBAR_cyc
                                )) != 0:
                            if py_map_pckg == 'cartopy':
                                CF1 = ax_cntrl.contourf(
                                    x, y, model_data_series_cnt_OBAR_cyc,
                                    transform=ccrs.PlateCarree(),
                                    levels=levels, cmap=cmap, extend='both'
                                )
                                # matplotlib/cartopy tries to close contour
                                # when using cylic point, so need to plot
                                # contours set contour labels, remove contour
                                # lines and then replot contour lines
                                C1 = ax_cntrl.contour(
                                    x, y, model_data_series_cnt_OBAR_cyc,
                                    transform=ccrs.PlateCarree(),
                                    levels=levels, colors='k',
                                    linewidths=1.0, extend='both'
                                )
                                C1labels = ax_cntrl.clabel(
                                    C1, C1.levels, fmt='%g', colors='k'
                                )
                                for c in C1.collections:
                                    c.set_visible(False)
                                C1 = ax_cntrl.contour(
                                    x, y, model_data_series_cnt_OBAR_cyc,
                                    transform=ccrs.PlateCarree(),
                                    levels=levels, colors='k',
                                    linewidths=1.0, extend='both'
                                )
                            elif py_map_pckg == 'basemap':
                                mcx, mcy = mc(x, y)
                                CF1 = mc.contourf(
                                    mcx, mcy, model_data_series_cnt_OBAR_cyc,
                                    levels=levels, cmap=cmap, extend='both'
                                )
                                C1 = mc.contour(
                                    mcx, mcy, model_data_series_cnt_OBAR_cyc,
                                    levels=levels, colors='k',
                                    linewidths=1.0, extend='both'
                                )
                                C1labels = ax_cntrl.clabel(
                                    C1, C1.levels, fmt='%g', colors='k'
                                )
                if verif_case_type == 'gdas':
                    if stat == 'bias':
                        print("Plotting "+model+" increment bias")
                    elif stat == 'rmse':
                        if model_num == 1:
                            print("Plotting "+model1+" increment RMSE")
                        else:
                            print("Plotting "+model+" - "+model1+" "
                                  +"increment RMSE")
                    if model_num == 1:
                        levels_plot = plot_util.get_clevels(stat_data)
                        cmap_plot = cmap_diff
                elif verif_case_type == 'ens':
                    print("Plotting "+model+" ensemble "+stat)
                    ax.set_title('index='
                                 +str(model_levels_var_level_diff_min_idx)
                                 +',pres='+str(model_level), loc='center')
                    if model_num == 1:
                        if stat == 'mean':
                            cmap_plot = cmap
                            if np.isnan(np.nanmax(stat_data)):
                                levels_max = 1
                            else:
                                levels_max = int(
                                    np.nanmax(stat_data)
                                ) + 1
                            if np.isnan(np.nanmin(stat_data)):
                                levels_min = -1
                            else:
                                levels_min = int(
                                    np.nanmin(stat_data)
                                ) - 1
                            levels_plot = np.linspace(levels_min, levels_max,
                                                      11, endpoint=True)
                        elif stat == 'spread':
                            levels_plot = plot_util.get_clevels(stat_data)
                            cmap_plot = cmap_diff
                stat_data_area_avg = (
                    maps2d_plot_util.calculate_area_average(
                        stat_data, model_data_lat,
                        model_data_lon, llcrnrlat_val, urcrnrlat_val,
                        llcrnrlon_val, urcrnrlon_val
                    )
                )
                ax.set_title(round(stat_data_area_avg, 3),
                             loc='right')
                if np.count_nonzero(~np.isnan(stat_data_cyc)) != 0:
                    if py_map_pckg == 'cartopy':
                        CF = ax.contourf(
                            x, y, stat_data_cyc,
                            transform=ccrs.PlateCarree(),
                            levels=levels_plot, cmap=cmap_plot,
                            extend='both'
                        )
                    elif py_map_pckg == 'basemap':
                        mx, my = m(x, y)
                        CF = ma.contourf(
                             mx, my, stat_data_cyc,
                             levels=levels_plot, cmap=cmap_plot,
                             extend='both'
                        )
        print(levels_plot)
        # Final touches and save plot
        cax = fig.add_axes([0.1, 0.0, 0.8, 0.05])
        cbar = fig.colorbar(CF, cax=cax, orientation='horizontal',
                            ticks=levels_plot)
        if verif_case_type == 'gdas':
            cbar.ax.set_xlabel('Difference')
        elif verif_case_type == 'ens':
            cbar.ax.set_xlabel('Ensemble '+stat.title())
        full_title = (
            stat_title+'\n'+var_info_title+'\n'
            +dates_title+' '+make_met_data_by_hrs_title+', '
            +forecast_to_plot_title
        )
        fig.suptitle(full_title, fontsize=18, fontweight='bold')
        noaa_img_axes = fig.add_axes([-0.01, 0.0, 0.01, 0.01])
        noaa_img_axes.axes.get_xaxis().set_visible(False)
        noaa_img_axes.axes.get_yaxis().set_visible(False)
        noaa_img_axes.axis('off')
        fig.figimage(noaa_logo_img_array, 1, 1, zorder=1, alpha=0.5)
        savefig_name = os.path.join(plotting_out_dir_imgs,
                                    verif_case_type+'_'+stat+'_'+var_group_name
                                    +'_'+var_name+'_'+var_level.replace(' ', '')
                                    +'_new.png')
        print("Saving image as "+savefig_name)
        plt.savefig(savefig_name, bbox_inches='tight')
        plt.close()
