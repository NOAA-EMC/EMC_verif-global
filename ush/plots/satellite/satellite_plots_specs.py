'''
Name: satellite_plots_specs.py
Contact(s): Ho-Chun Huang (ho-chun.huang@noaa.gov)
Abstract: This script defines plotting related settings.
'''
import matplotlib
import matplotlib.pyplot as plt
import datetime
import sys
import os
import numpy as np
import verif_global_util as vfg_util

class PlotSpecs:
    def __init__(self, logger, plot_type):
        """! Initialize PlotSpecs class

             Args:
                 logger    - logger object
                 plot_type - type of graphic being produced (string)

             Returns:
        """
        self.plot_type = plot_type
        self.logger = logger
        self.font_weight = 'bold'
        self.axis_title_weight = 'bold'
        self.axis_title_size = 16
        self.axis_title_pad = 15
        self.axis_title_loc = 'center'
        self.axis_offset = False
        self.axis_label_weight = 'bold'
        self.axis_label_size = 16
        self.axis_label_pad = 10
        self.xtick_label_size = 16
        self.xtick_major_pad = 10
        self.ytick_label_size = 16
        self.ytick_major_pad = 10
        self.fig_title_weight = 'bold'
        self.fig_title_size = 16
        self.fig_subplot_right = 0.95
        self.fig_subplot_left = 0.1
        self.fig_subplot_top = 0.925
        self.fig_subplot_bottom = 0.075
        self.legend_handle_text_pad = 0.25
        self.legend_handle_length = 1.25
        self.legend_border_axis_pad = 0
        self.legend_col_space = 1.0
        self.legend_frame_on = True
        self.legend_bbox = (0,1)
        self.legend_font_size = 13
        self.legend_loc = 'center'
        self.legend_ncol = 1
        self.title_loc = 'center'
        self.fig_size=(16.,16.)
        if self.plot_type =='time_series':
            self.fig_size = (16., 8.)
            self.fig_subplot_top = 0.87
            self.fig_subplot_bottom = 0.1
            self.fig_subplot_right = 0.925
            self.fig_subplot_left = 0.085
            self.axis_label_size = 15
            self.xtick_label_size = 15
            self.ytick_label_size = 15
            self.legend_frame_on = False
            self.legend_bbox = (0.5, 0.05)
            self.legend_ncol = 4
        elif self.plot_type in 'lead_average':
            self.fig_size = (16., 16.)
            self.fig_subplot_top = 0.9
            self.fig_subplot_bottom = 0.05
            self.fig_subplot_right = 0.92
            self.fig_subplot_left = 0.12
            self.legend_frame_on = False
            self.legend_bbox = (0.5, 0.05)
            self.legend_ncol = 5
            self.fig_title_size = 18
        else:
            self.logger.error(f"{self.plot_type} not recognized")
            sys.exit(1)

    def set_up_plot(self):
        """! Set up the matplotlib rcParams

             Args:

             Returns:
        """
        plt.rcParams['font.weight'] = self.font_weight
        plt.rcParams['axes.titleweight'] = self.axis_title_weight
        plt.rcParams['axes.titlesize'] = self.axis_title_size
        plt.rcParams['axes.titlepad'] = self.axis_title_pad
        plt.rcParams['axes.titlelocation'] = self.axis_title_loc
        plt.rcParams['axes.labelweight'] = self.axis_label_weight
        plt.rcParams['axes.labelsize'] = self.axis_label_size
        plt.rcParams['axes.labelpad'] = self.axis_label_pad
        plt.rcParams['axes.formatter.useoffset'] = self.axis_offset
        plt.rcParams['xtick.labelsize'] = self.xtick_label_size
        plt.rcParams['xtick.major.pad'] = self.xtick_major_pad
        plt.rcParams['ytick.labelsize'] = self.ytick_label_size
        plt.rcParams['ytick.major.pad'] = self.ytick_major_pad
        plt.rcParams['figure.subplot.left'] = self.fig_subplot_left
        plt.rcParams['figure.subplot.right'] = self.fig_subplot_right
        plt.rcParams['figure.subplot.top'] = self.fig_subplot_top
        plt.rcParams['figure.subplot.bottom'] = self.fig_subplot_bottom
        plt.rcParams['figure.titleweight'] = self.fig_title_weight
        plt.rcParams['figure.titlesize'] = self.fig_title_size
        plt.rcParams['legend.handletextpad'] = self.legend_handle_text_pad
        plt.rcParams['legend.handlelength'] = self.legend_handle_length
        plt.rcParams['legend.borderaxespad'] = self.legend_border_axis_pad
        plt.rcParams['legend.columnspacing'] = self.legend_col_space
        plt.rcParams['legend.frameon'] = self.legend_frame_on
        img_quality = os.environ['img_quality']
        if img_quality == 'low':
            plt.rcParams['savefig.dpi'] = 50
        elif img_quality == 'medium':
            plt.rcParams['savefig.dpi'] = 75
        if float(matplotlib.__version__[0:3]) >= 3.3:
            plt.rcParams['date.epoch'] = '0000-12-31T00:00:00'

    def get_stat_plot_name(self, stat):
        """! Get the full statistic name that will be
             displayed on the plot

             Args:
                 stat - abbreviated statistic name (string)

             Returns:
                 stat_plot_name - full statistic name that
                                  will be displayed on the plot
                                  (string)
        """
        stat_plot_name_dict = {
            'FBAR_OBAR': 'Forecast and Observation Mean',
            'ME': 'Bias (Mean Error) [Fcst-Obs]',
            'RMSE': 'Root Mean Square Error',
        }
        if stat in list(stat_plot_name_dict.keys()):
            stat_plot_name = stat_plot_name_dict[stat]
        else:
            self.logger.debug(f"{stat} not recognized, using {stat} on plot")
            stat_plot_name = stat
        return stat_plot_name

    def get_var_plot_name(self, var_name, var_level):
        """! Get the full variable information that will be displayed
             on the plot

             Args:
                 var_name   - abbreviated variable name (string)
                 var_level  - abbreviated variable level (string)
             Returns:
                 var_plot_name - full variable information that
                                 will be displayed on the plot
                                 (string)
        """
        var_name_level = var_name+'/'+var_level
        var_plot_name_dict = {
            'ICEC_Z0_mean/Z0': 'Daily Avg Ice Concentration',
            'TMP_Z0_mean/Z0': 'Daily Average Surface/Skin Temperature',
        }
        if var_name_level in list(var_plot_name_dict.keys()):
            var_plot_name = var_plot_name_dict[var_name_level]
        else:
            self.logger.debug(f"{var_name_level} not recognized, "
                              +f"using {var_name_level} on plot")
            var_plot_name = var_name_level
        return var_plot_name

    def get_obs_plot_name(self, ob_name):
        """! Get the full obs source name that will be
             displayed on the plot
             Args:
                 ob_name - abbreviated obs source name (string)
             Returns:
                 obs_plot_name - full obs source name that
                                 will be displayed on the plot
                                 (string)
        """
        obs_plot_name_dict = {
            'ghrsst_ospo': 'GHRSST-OSPO',
        }
        if ob_name in list(obs_plot_name_dict.keys()):
            obs_plot_name = obs_plot_name_dict[ob_name]
        else:
            obs_plot_name = ob_name
        return obs_plot_name

    def get_vx_mask_plot_name(self, vx_mask):
        """! Get the full verification masking information that will
             be displayed on the plot

             Args:
                 vx_mask - abbreviated verification mask name (string)

             Returns:
                 vx_mask_plot_name - full verification mask name that
                                     will be displayed on the plot
                                     (string)
        """
        vx_mask_plot_name_dict = {
            'SEA_ICE_ANTARCTIC': 'Antarctic (60S-90S)',
            'SEA_ICE_ARCTIC': 'Arctic (60N-90N)',
            'SEA_ICE_NH': 'Northern Hemisphere (20N-90N)',
            'SEA_ICE_POLAR': 'Polar (60S-90S and 60N-90N)',
            'SEA_ICE_SH': 'Southern Hemisphere (20S-90S)',
            'WATER_ANTARCTIC': 'Antarctic (60S-90S, Water Only)',
            'WATER_ARCTIC': 'Arctic (60N-90N, Water Only)',
            'WATER_NH': 'Northern Hemisphere (20N-90N, Water Only)',
            'WATER_POLAR': 'Polar (60S-90S and 60N-90N, Water Only)',
            'WATER_SH': 'Southern Hemisphere (20S-90S, Water Only)',
        }
        if vx_mask in list(vx_mask_plot_name_dict.keys()):
            vx_mask_plot_name = vx_mask_plot_name_dict[vx_mask]
        else:
            self.logger.debug(f"{vx_mask} not recognized, "
                              +f"using {vx_mask} on plot")
            vx_mask_plot_name = vx_mask
        return vx_mask_plot_name

    def get_dates_plot_name(self, plot_by, start_date, end_date,
                            plot_by_hr_list, other_hr_list,
                            forecast_hour_list, plot_type):
        """! Get the full date information that will be displayed on the plot

             Args:
                 plot_by            - type of dates
                                      (string, VALID or INIT)
                 start_date         - starting date and hour
                                      (string, YYYYmmdd)
                 end_date           - ending date and hour
                                      (string, YYYYmmdd)
                 plot_by_hr_list    - list of hours for
                                      date_type
                 other_hr_list      - list of hours for
                                      opposite of date_type
                                      (strings)
                 forecast_hour_list - list of forecast hour(s)
                 plot_type          - type of plot (string)

             Returns:
                 date_plot_name - full date information that
                                  will be displayed on the plot
                                  (string)
        """
        date_plot_name = plot_by.lower()+' '
        start_date_dt = datetime.datetime.strptime(start_date, '%Y%m%d')
        end_date_dt = datetime.datetime.strptime(end_date, '%Y%m%d')
        date_plot_name = (date_plot_name
                          +start_date_dt.strftime('%d%b%Y')+'-'
                          +end_date_dt.strftime('%d%b%Y')+' ')
        title_other_hr_list = []
        if plot_by == 'VALID':
            for plot_by_hr in plot_by_hr_list:
                for forecast_hour in forecast_hour_list:
                    other_hr = vfg_util.get_init_hour(
                        int(plot_by_hr.replace('Z', '')),
                        int(forecast_hour)
                    )
                    if str(other_hr).zfill(2)+'Z' not in title_other_hr_list \
                            and str(other_hr).zfill(2)+'Z' in other_hr_list:
                        title_other_hr_list.append(str(other_hr).zfill(2)+'Z')
            title_other_hr_list.sort()
            date_plot_name = (date_plot_name+', '.join(plot_by_hr_list)
                              +', init. hours: '
                              +', '.join(title_other_hr_list))
        elif plot_by == 'INIT':
            for plot_by_hr in plot_by_hr_list:
                for forecast_hour in forecast_hour_list:
                    other_hr = vfg_util.get_valid_hour(
                        int(plot_by_hr.replace('Z', '')),
                        int(forecast_hour)
                    )
                    if str(other_hr).zfill(2)+'Z' not in title_other_hr_list \
                            and str(other_hr).zfill(2)+'Z' in other_hr_list:
                        title_other_hr_list.append(str(other_hr).zfill(2)+'Z')
                    title_other_hr_list.append(str(init_hr).zfill(2)+'Z')
            title_other_hr_list.sort()
            date_plot_name = (date_plot_name+', '.join(plot_by_hr_list)
                              +', valid: '+', '.join(title_other_hr_list))
        if plot_type not in ['lead_average']:
            forecast_day_list = []
            for forecast_hour in forecast_hour_list:
                forecast_day = int(forecast_hour)/24.
                if int(forecast_hour) % 24 == 0:
                    forecast_day_list.append(str(int(forecast_day)))
                else:
                    forecast_day_list.append(str(forecast_day))
            if len(forecast_hour_list) == 1:
                date_plot_name = (date_plot_name
                                  +', Forecast Day '+forecast_day_list[0]+' '
                                  +'(Hour '+forecast_hour_list[0]+')')
            else:
                date_plot_name = (date_plot_name
                                  +'\nForecast Days '
                                  +','.join(forecast_day_list)+' '
                                  +'(Hours '+','.join(forecast_hour_list)+')')
        return date_plot_name

    def get_plot_title(self, plot_info_dict, date_info_dict, units):
        """! Construct the title for the plot

             Args:
                 plot_info_dict  - plot information dictionary (strings)
                 date_info_dict  - date information dictionary (strings)
                 units           - variable units (string)

             Returns:
                 plot_title - full plot title that will be
                              displayed on the plot
                              (string)
        """
        plot_title = (
            self.get_stat_plot_name(plot_info_dict['stat'])+' - '
            +plot_info_dict['grid']+'/'
            +self.get_vx_mask_plot_name(plot_info_dict['vx_mask'])+'\n'
        )
        if date_info_dict['plot_by'] == 'VALID':
            plot_by_hr_list = [
                str(hr).zfill(2)+'Z' \
                for hr in range(int(date_info_dict['valid_hr_start']),
                                int(date_info_dict['valid_hr_end'])
                                +int(date_info_dict['valid_hr_inc']),
                                int(date_info_dict['valid_hr_inc']))
            ]
            other_hr_list = [
                str(hr).zfill(2)+'Z' \
                for hr in range(int(date_info_dict['init_hr_start']),
                                int(date_info_dict['init_hr_end'])
                                +int(date_info_dict['init_hr_inc']),
                                int(date_info_dict['init_hr_inc']))
            ]
        elif date_info_dict['plot_by'] == 'INIT':
            plot_by_hr_list = [
                str(hr).zfill(2)+'Z' \
                for hr in range(int(date_info_dict['init_hr_start']),
                                int(date_info_dict['init_hr_end'])
                                +int(date_info_dict['init_hr_inc']),
                                int(date_info_dict['init_hr_inc']))
            ]
            other_hr_list = [
                str(hr).zfill(2)+'Z' \
                for hr in range(int(date_info_dict['valid_hr_start']),
                                int(date_info_dict['valid_hr_end'])
                                +int(date_info_dict['valid_hr_inc']),
                                int(date_info_dict['valid_hr_inc']))
            ]
        if self.plot_type == 'time_series':
            fhr_for_title = [date_info_dict['forecast_hour']]
        else:
            fhr_for_title = date_info_dict['forecast_hours']
        var_name_for_title = plot_info_dict['fcst_var_name']
        var_level_for_title = plot_info_dict['fcst_var_level']
        var_thresh_for_title = plot_info_dict['fcst_var_thresh']
        plot_title = (plot_title
                      +self.get_var_plot_name(var_name_for_title,
                                              var_level_for_title))
        plot_title = plot_title+' '+'('+units+')'
        #plot_title = plot_title+', '+var_thresh_for_title.replace('||','')+' '+units
        plot_title = (plot_title+'\n'
                      +self.get_dates_plot_name(date_info_dict['plot_by'],
                                                date_info_dict['start_date'],
                                                date_info_dict['end_date'],
                                                plot_by_hr_list, other_hr_list,
                                                fhr_for_title, self.plot_type))
        return plot_title

    def get_savefig_name(self, image_dir, plot_info_dict, date_info_dict):
        """! Construct the full path to save the plot

             Args:
                 image_dir       - full path to directory of where
                                   to save (string)
                 plot_info_dict  - plot information dictionary (strings)
                 date_info_dict  - date information dictionary (strings)

             Returns:
                 image_path - full path of the name the plot will
                              be saved as (string)
        """
        component_savefig_name = plot_info_dict['RUN_CASE']
        metric_savefig_name = plot_info_dict['stat']
        if 'fcst_var_thresh' in list(plot_info_dict.keys()):
            if plot_info_dict['fcst_var_thresh'] != 'NA':
                thresh_symbol, thresh_letter = vfg_util.format_thresh(
                    plot_info_dict['fcst_var_thresh']
                )
        parameter_savefig_name = plot_info_dict['fcst_var_name']
        level_savefig_name = (
            plot_info_dict['fcst_var_level'].replace('-', '_')\
            .replace('.', 'p')
        )
        if self.plot_type == 'time_series':
            plot_type_savefig_name = 'timeseries'
        elif self.plot_type == 'lead_average':
            plot_type_savefig_name = 'fhrmean'
        else:
            plot_type_savefig_name = self.plot_type.replace('_', '')
        if self.plot_type in ['time_series', 'lead_average']:
            plot_type_savefig_name = plot_type_savefig_name+'_valid'
            valid_hr = int(date_info_dict['valid_hr_start'])
            while valid_hr <= int(date_info_dict['valid_hr_end']):
                plot_type_savefig_name = (plot_type_savefig_name
                                          +str(valid_hr).zfill(2))
                valid_hr+=int(date_info_dict['valid_hr_inc'])
            plot_type_savefig_name = plot_type_savefig_name+'Z'
        if self.plot_type == 'time_series':
            plot_type_savefig_name = (
                 plot_type_savefig_name+'_'
                 +'f'+date_info_dict['forecast_hour'].zfill(3)
            )
        grid_savefig_name = plot_info_dict['grid']
        region_savefig_dict = {
            'SEA_ICE_ANTARCTIC': 'antarctic',
            'SEA_ICE_ARCTIC': 'arctic',
            'SEA_ICE_NH': 'nh', 
            'SEA_ICE_POLAR': 'polar',
            'SEA_ICE_SH': 'sh',
            'WATER_ANTARCTIC': 'antarctic',
            'WATER_ARCTIC': 'arctic',
            'WATER_NH': 'nh',
            'WATER_POLAR': 'polar',
            'WATER_SH': 'sh',
        }
        if plot_info_dict['vx_mask'] in list(region_savefig_dict.keys()):
            region_savefig_name = (
                region_savefig_dict[plot_info_dict['vx_mask']]
            )
        else:
            region_savefig_name = plot_info_dict['vx_mask']
        savefig_name = (
            component_savefig_name+'.'
            +metric_savefig_name+'.'
            +parameter_savefig_name+'_'+level_savefig_name+'.'
            +plot_type_savefig_name+'.'
            +grid_savefig_name+'_'+region_savefig_name
            +'.png'
        ).lower()
        image_path = os.path.join(image_dir, savefig_name)
        return image_path

    def get_logo_location(self, position, x_figsize, y_figsize, dpi):
        """! Get locations for the logos

             Args:
                 position  - side of image (string, "left" or "right")
                 x_figsize - image size in x direction (float)
                 y_figsize - image size in y direction(float)
                 dpi       - image dots per inch (float)

             Returns:
                 x_loc - logo position in x direction (float)
                 y_loc - logo position in y direction (float)
                 alpha - alpha value (float)
        """
        alpha = 0.5
        if x_figsize == 8 and y_figsize == 6:
            if position == 'left':
                x_loc = x_figsize * dpi * 0.0
                y_loc = y_figsize * dpi * 0.858
            elif position == 'right':
                x_loc = x_figsize * dpi * 0.9
                y_loc = y_figsize * dpi * 0.858
        elif x_figsize == 16 and y_figsize == 8:
            if position == 'left':
                x_loc = x_figsize * dpi * 0.0
                y_loc = y_figsize * dpi * 0.89
            elif position == 'right':
                x_loc = x_figsize * dpi * 0.948
                y_loc = y_figsize * dpi * 0.89
        elif x_figsize == 16 and y_figsize == 16:
            if position == 'left':
                x_loc = x_figsize * dpi * 0
                y_loc = y_figsize * dpi * 0.945
            elif position == 'right':
                x_loc = x_figsize * dpi * 0.948
                y_loc = y_figsize * dpi * 0.945
        return x_loc, y_loc, alpha

    def get_marker_plot_settings(self):
        """! Get dictionary plot settings for models

             Args:

             Returns:
                 marker_plot_settings_dict - dictionary of
                                             marker plotting specifications
                                             (strings)
        """
        marker_plot_settings_dict = {
            'marker1': {'marker': 'o', 'markersize': 12},
            'marker2': {'marker': 'P', 'markersize': 14},
            'marker3': {'marker': '^', 'markersize': 14},
            'marker4': {'marker': 'X', 'markersize': 14},
            'marker5': {'marker': 's', 'markersize': 12},
            'marker6': {'marker': 'D', 'markersize': 12},
            'marker7': {'marker': 'v', 'markersize': 14},
            'marker8': {'marker': 'p', 'markersize': 14},
            'marker9': {'marker': '<', 'markersize': 14},
            'marker10': {'marker': 'd', 'markersize': 14},
            'marker11': {'marker': r'$\spadesuit$', 'markersize': 14},
            'marker12': {'marker': '>', 'markersize': 14},
            'marker13': {'marker': r'$\clubsuit$', 'markersize': 14},
        }
        return marker_plot_settings_dict

    def get_model_plot_settings(self):
        """! Get dictionary plot settings for models

             Args:

             Returns:
                 model_plot_settings_dict - dictionary of
                                            model plotting specifications
                                            (strings)
        """
        model_plot_settings_dict = {
            'model1': {'color': '#000000',
                       'marker': 'o', 'markersize': 6,
                       'linestyle': 'solid', 'linewidth': 3},
            'model2': {'color': '#fb2020',
                       'marker': '^', 'markersize': 7,
                       'linestyle': 'solid', 'linewidth': 1.5},
            'model3': {'color': '#1e3cff',
                       'marker': 'X', 'markersize': 7,
                       'linestyle': 'solid', 'linewidth': 1.5},
            'model4': {'color': '#00dc00',
                       'marker': 'P', 'markersize': 7,
                       'linestyle': 'solid', 'linewidth': 1.5},
            'model5': {'color': '#e69f00',
                       'marker': 'o', 'markersize': 6,
                       'linestyle': 'solid', 'linewidth': 1.5},
            'model6': {'color': '#56b4e9',
                       'marker': 'o', 'markersize': 6,
                       'linestyle': 'solid', 'linewidth': 1.5},
            'model7': {'color': '#696969',
                       'marker': 's', 'markersize': 6,
                       'linestyle': 'solid', 'linewidth': 1.5},
            'model8': {'color': '#8400c8',
                       'marker': 'D', 'markersize': 6,
                       'linestyle': 'solid', 'linewidth': 1.5},
            'model9': {'color': '#d269c1',
                       'marker': 's', 'markersize': 6,
                       'linestyle': 'solid', 'linewidth': 1.5},
            'model10': {'color': '#f0e492',
                        'marker': 'o', 'markersize': 6,
                        'linestyle': 'solid', 'linewidth': 1.5},
            'obs': {'color': '#aaaaaa',
                    'marker': 'None', 'markersize': 0,
                    'linestyle': 'solid', 'linewidth': 2},
        }
        return model_plot_settings_dict
