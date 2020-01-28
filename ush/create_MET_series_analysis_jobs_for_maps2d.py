'''
Program Name: create_MET_series_analysis_jobs_for_maps2d.py
Contact(s): Mallory Row
Abstract: This script is run by the maps2d jobs scripts.
          It runs series_analysis, which produces
          netCDF output.
'''

from __future__ import (print_function, division)
import os
import re 

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables 
HOMEMET = os.environ['HOMEMET']
DATA = os.environ['DATA']
RUN = os.environ['RUN']
PARMverif_global = os.environ['PARMverif_global']
WGRIB2 = os.environ['WGRIB2']
MET_verbosity = os.environ['MET_verbosity']
MET_version = os.environ['MET_version']
METplus_version = os.environ['METplus_version']
START_DATE = os.environ['START_DATE']
END_DATE = os.environ['END_DATE']
job_num_id = os.environ['job_num_id']
make_met_data_by = os.environ['make_met_data_by']
forecast_to_plot = os.environ['forecast_to_plot']
hr_beg = os.environ['hr_beg']
hr_end = os.environ['hr_end']
hr_inc = os.environ['hr_inc']
regrid_to_grid = os.environ['regrid_to_grid']
latlon_area = os.environ['latlon_area']
var_group_name = os.environ['var_group_name']
var_name = os.environ['var_name']
var_levels_list = os.environ['var_levels'].split(', ')
forecast_anl_diff = os.environ['forecast_anl_diff']
verif_case_type = os.environ['verif_case_type']
model_regex = re.compile("model(\d+)$")
all_model_dict = {}
for key in list(os.environ.keys()):
    model_regex_match = model_regex.match(key)
    if model_regex_match is not None:
        model_regex_match_dict = {}
        model_regex_match_dict['name'] = (
            os.environ[model_regex_match.group(0)]
        )
        model_regex_match_dict['plot_name'] = (
            os.environ[model_regex_match.group(0)+'_plot_name']
        )
        model_regex_match_dict['obtype'] = (
            os.environ[model_regex_match.group(0)+'_obtype']
        )
        all_model_dict[model_regex_match.group(0)] = model_regex_match_dict
model_list = sorted(list(all_model_dict.keys()))

# Set up series_analysis path and config
series_analysis_path = os.path.join(HOMEMET, 'bin', 'series_analysis')
series_analysis_verbosity = '-v '+MET_verbosity
if any('bucketaccum' in s for s in var_levels_list):
    series_analysis_config = '-config '+os.path.join(PARMverif_global,
                                                     'metplus_config',
                                                     'metplus_use_cases',
                                                     'METplusV'
                                                     +METplus_version,
                                                     'maps2d', 'met_config',
                                                     'metV'+MET_version,
                                                     'SeriesAnalysisConfig'
                                                     +'_time_range_accum')
else:
    series_analysis_config = '-config '+os.path.join(PARMverif_global,
                                                     'metplus_config',
                                                     'metplus_use_cases',
                                                     'METplusV'
                                                     +METplus_version,
                                                     'maps2d', 'met_config',
                                                     'metV'+MET_version,
                                                     'SeriesAnalysisConfig')

def get_var_grib1_info(var_name, var_level):
    """! This returns special GRIB1 variable information to use
         with MET's series_analysis.
         Information from:
             https://www.nco.ncep.noaa.gov/pmb/docs/on388/table2.html
             https://www.nco.ncep.noaa.gov/pmb/docs/on388/table3.html

         Args:
             var_name          - string of the grib file variable
                                 name
             var_level         - string of the description for
                                 the variable GRIB level
             
         Returns:
             var_GRIB_lvl_typ  - string of the GRIB level type number
             var_GRIB_lvl_val1 - string of the GRIB level 1 number
             var_GRIB_lvl_val2 - string of the GRIB level 2 number
             var_GRIB1_ptv     - string of the GRIB1 parameter table
                                 where the variable is defined
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
    else:
        print("ERROR: Unable to speificy GRIB level type "
              +"from variable level info "+var_level)
        exit(1)
    # Define 1st and 2nd GRIB level
    var_level_nums = ''
    for v in var_level:
        if v.isdigit() or v == '-' or v == '.':
            var_level_nums = var_level_nums + v
    if var_level_nums != '':
       if '-' in var_level_nums:
           var_GRIB_lvl_val1 = var_level_nums.split('-')[0]
           var_GRIB_lvl_val2 = var_level_nums.split('-')[1]
       elif 'sigma' in var_level:
           var_GRIB_lvl_val1 = str(
               int(float(var_level_nums)*1000)
           ).ljust(4, '0')
           var_GRIB_lvl_val2 = str(
               int(float(var_level_nums)*1000)
           ).ljust(4, '0')
       else:
           var_GRIB_lvl_val1 = var_level_nums
           var_GRIB_lvl_val2 = var_level_nums
    else:
       var_GRIB_lvl_val1 = '0'
       var_GRIB_lvl_val2 = '0'
    # Define GRIB1 parameter table
    if var_name in ['VRATE', 'HINDEX', 'DUVB', 'CDUVB']:
        var_GRIB1_ptv = '129'
    elif var_name in ['WILT', 'FLDCP']:
        var_GRIB1_ptv = '130'
    elif var_name in ['SUNSD']:
        var_GRIB1_ptv = '133'
    else:
        var_GRIB1_ptv = '2'
    # Define time range accumulation
    if 'bucketaccum' in var_level:
        var_time_range_accum = 'A'
        for v in var_level:
            if v.isdigit():
                var_time_range_accum = var_time_range_accum + v
    else:
        var_time_range_accum = '0'
    return (var_GRIB_lvl_typ, var_GRIB_lvl_val1,
            var_GRIB_lvl_val2, var_GRIB1_ptv, var_time_range_accum)

# Run for models
for model in model_list:
    model_dict = all_model_dict[model]
    model_name = model_dict['name']
    model_plot_name = model_dict['plot_name']
    model_obtype = model_dict['obtype']
    # Set up input information
    if verif_case_type == 'model2model':
        if forecast_anl_diff == 'YES' and forecast_to_plot != 'anl':
            series_analysis_fcst_files = (
                '-fcst '+os.path.join (DATA, RUN, 'data', model_name,
                                       model_name+'_'+forecast_to_plot
                                       +'_file_list.txt')
            )
            series_analysis_obs_files = (
                '-obs '+os.path.join (DATA, RUN, 'data', model_name,
                                      model_name+'_'+forecast_to_plot
                                      +'_anl_file_list.txt')
            )
            series_analysis_files = (series_analysis_fcst_files
                                     +' '+series_analysis_obs_files)
        else:
            series_analysis_files = (
                '-both '+os.path.join (DATA, RUN, 'data', model_name,
                                       model_name+'_'+forecast_to_plot
                                       +'_file_list.txt')
            )
    # Set up shell script for series_analysis job
    series_analysis_job_filename = os.path.join (DATA, RUN,
                                                 'metplus_job_scripts',
                                                 'series_analysis_'
                                                 +'job'+job_num_id+'_'
                                                 +model_name+'.sh')
    if os.path.exists(series_analysis_job_filename):
        os.remove(series_analysis_job_filename)
    print("Creating job file "+series_analysis_job_filename)
    series_analysis_job_file = open(series_analysis_job_filename, 'w')
    series_analysis_job_file.write('#!/bin/sh\n')
    series_analysis_job_file.write('\n')
    series_analysis_job_file.write('export model="'+model_name+'"\n')
    series_analysis_job_file.write('export obtype="'+model_obtype+'"\n')
    series_analysis_job_file.write('export regrid_grid="'
                                   +regrid_to_grid+'"\n')
    series_analysis_job_file.write('export var_name="'+var_name+'"\n')
    # For series_analysis to create the series of all the files,
    # it needs to be run separately for each level
    for var_level in var_levels_list:
        series_analysis_out = (
            '-out '+os.path.join (DATA, RUN, 'metplus_output',
                                  'make_met_data_by_'+make_met_data_by,
                                  'series_analysis', verif_case_type,
                                  var_group_name, model_name,
                                  forecast_to_plot+'_'+var_name+'_'
                                  +var_level.replace(' ', '')+'.nc')
        )
        series_analysis_log = (
            '-log '+os.path.join (DATA, RUN, 'metplus_output', 'logs',
                                  'series_analysis_'+verif_case_type+'_'
                                  +var_group_name+'_'+model_name+'_'
                                  +forecast_to_plot+'_'+var_name+'_'
                                  +var_level.replace(' ', '')+'.log')
        )
        series_analysis_job_file.write('export var_level="'+var_level+'"\n')
        # extract special grib file information
        (var_GRIB_lvl_typ, var_GRIB_lvl_val1,
            var_GRIB_lvl_val2, var_GRIB1_ptv, var_time_range_accum) = (
                get_var_grib1_info(var_name, var_level)
        )
        series_analysis_job_file.write('export var_GRIB_lvl_typ="'
                                       +var_GRIB_lvl_typ+'"\n')
        series_analysis_job_file.write('export var_GRIB_lvl_val1="'
                                       +var_GRIB_lvl_val1+'"\n')
        series_analysis_job_file.write('export var_GRIB_lvl_val2="'
                                       +var_GRIB_lvl_val2+'"\n')
        series_analysis_job_file.write('export var_GRIB1_ptv="'
                                       +var_GRIB1_ptv+'"\n')
        if var_time_range_accum != '0':
            series_analysis_job_file.write('export var_time_range_accum="'
                                           +var_time_range_accum+'"\n')
        series_analysis_job_file.write(series_analysis_path+' '
                                       +series_analysis_verbosity+' '
                                       +series_analysis_files+' '
                                       +'-paired '
                                       +series_analysis_log+' '
                                       +series_analysis_out+' '
                                       +series_analysis_config+'\n')
    series_analysis_job_file.close()
    os.chmod(series_analysis_job_filename, 0o755)

print("END: "+os.path.basename(__file__))
