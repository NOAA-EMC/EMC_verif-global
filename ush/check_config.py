'''
Program Name: check_config_settings.py
Contact(s): Mallory Row
Abstract: This script is run by all scripts in scripts/.
          This does a check on the user's settings in
          the passed config file.
'''

import os

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
RUN = os.environ['RUN']
RUN_abbrev = os.environ['RUN_abbrev']
model_list = os.environ['model_list'].split(' ')
model_dir_list = os.environ['model_dir_list'].split(' ')
model_stat_dir_list = os.environ['model_stat_dir_list'].split(' ')
model_file_format_list = os.environ['model_file_format_list'].split(' ')
model_hpss_dir_list = os.environ['model_hpss_dir_list'].split(' ')
make_met_data_by = os.environ['make_met_data_by']
plot_by = os.environ['plot_by']
if RUN != 'tropcyc':
    RUN_type_list = os.environ[RUN_abbrev+'_type_list'].split(' ')

# Do check for valid RUN_type options
valid_RUN_type_opts_dict = {
    'grid2grid_step1': ['anom', 'pres', 'sfc'],
    'grid2grid_step2': ['anom', 'pres', 'sfc'],
    'grid2obs_step1': ['upper_air', 'conus_sfc', 'polar_sfc'],
    'grid2obs_step2': ['upper_air', 'conus_sfc', 'polar_sfc'],
    'precip_step1': ['ccpa_accum24hr'],
    'precip_step2': ['ccpa_accum24hr'],
    'satellite_step1': ['ghrsst_ncei_avhrr_anl', 'ghrsst_ospo_geopolar_anl'],
    'satellite_step2': ['ghrsst_ncei_avhrr_anl', 'ghrsst_ospo_geopolar_anl'],
    'maps2d': ['model2model', 'model2obs'],
    'mapsda': ['gdas', 'ens']
}
if RUN != 'tropcyc':
    for RUN_type in RUN_type_list:
        if RUN_type not in valid_RUN_type_opts_dict[RUN]:
            print("ERROR: "+RUN_type+" not a valid option for "
                  +RUN_abbrev+"_type_list. Valid options are "
                  +', '.join(valid_RUN_type_opts_dict[RUN]))
            exit(1)

# Do check for list config variables lengths
check_config_var_len_list = ['model_dir_list', 'model_stat_dir_list',
                             'model_file_format_list', 'model_hpss_dir_list']
if RUN in ['grid2grid_step2', 'grid2obs_step2', 'precip_step2',
           'satellite_step2', 'maps2d', 'mapda']:
    check_config_var_len_list.append(RUN_abbrev+'_model_plot_name_list')
if RUN == 'tropcyc':
    check_config_var_len_list.append(RUN+'_model_atcf_name_list')
    check_config_var_len_list.append(RUN+'_model_file_format_list')
else:
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        if RUN == 'grid2grid_step1':
            check_config_var_len_list.append(
                RUN_abbrev_type+'_truth_file_format_list'
            )
        elif RUN == 'grid2grid_step2':
            check_config_var_len_list.append(
                RUN_abbrev_type+'_truth_name_list'
            )
            check_config_var_len_list.append(
                RUN_abbrev_type+'_gather_by_list'
            )
        elif RUN == 'grid2obs_step2':
            check_config_var_len_list.append(
                RUN_abbrev_type+'_gather_by_list'
            )
        elif RUN == 'precip_step1':
            check_config_var_len_list.append(
                RUN_abbrev_type+'_model_bucket_list'
            )
            check_config_var_len_list.append(
                RUN_abbrev_type+'_model_varname_list'
            )
            check_config_var_len_list.append(
                RUN_abbrev_type+'_model_file_format_list'
            )
        elif RUN == 'precip_step2':
            check_config_var_len_list.append(
                RUN_abbrev_type+'_gather_by_list'
            )
        elif RUN == 'satellite_step2':
            check_config_var_len_list.append(
                RUN_abbrev_type+'_gather_by_list'
            )
        elif RUN == 'maps2d':
            check_config_var_len_list.append(
                RUN_abbrev_type+'_anl_file_format_list'
            )
        elif RUN == 'mapsda':
            if RUN_type == 'gdas':
                check_config_var_len_list.append(
                    RUN_abbrev_type+'_model_file_format_list'
                )
                check_config_var_len_list.append(
                    RUN_abbrev_type+'_anl_file_format_list'
                )
            if RUN_type == 'ens':
                check_config_var_len_list.append(
                    RUN_abbrev_type+'_model_dir_list'
                )
                check_config_var_len_list.append(
                    RUN_abbrev_type+'_netcdf_suffix_list'
                )
for config_var in check_config_var_len_list:
    if len(os.environ[config_var].split(' ')) \
            != len(os.environ['model_list'].split(' ')):
     print("ERROR: length of "+config_var+" (length="
           +str(len(os.environ[config_var].split(' ')))+", values="
           +os.environ[config_var]+") not equal to length of model_list "
           +"(length="+str(len(os.environ['model_list'].split(' ')))+", "
           +"values="+os.environ['model_list']+")")
     exit(1)

# Do check for valid list config variable options
valid_config_var_values_dict = {
    'model_data_run_hpss': ['YES', 'NO'],
    'make_met_data_by': ['VALID', 'INIT'],
    'plot_by': ['VALID', 'INIT'],
    'SEND2WEB': ['YES', 'NO'],
    'METplus_verbosity': ['DEBUG', 'INFO', 'WARN', 'ERORR'],
    'MET_verbosity': ['0', '1', '2', '3', '4', '5'],
    'log_MET_output_to_METplus': ['yes', 'no'],
    'SENDARCH': ['YES', 'NO'],
    'SENDMETVIEWER': ['YES', 'NO'],
    'KEEPDATA': ['YES', 'NO'],
    'SENDARCH': ['YES', 'NO'],
    'SENDECF': ['YES', 'NO'],
    'SENDCOM': ['YES', 'NO'],
    'SENDDBN': ['YES', 'NO'],
    'SENDDBN_NTC': ['YES', 'NO']
}
if RUN == 'grid2grid_step1':
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        valid_config_var_values_dict[RUN_abbrev_type+'_truth_name'] = [
            'self_anl', 'self_f00', 'gfs_anl', 'gfs_f00'
        ]
        valid_config_var_values_dict[RUN_abbrev_type+'_gather_by'] = [
            'VALID', 'INIT', 'VSDB'
        ]
elif RUN == 'grid2grid_step2':
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        valid_config_var_values_dict[RUN_abbrev_type+'_truth_name_list'] = [
            'self_anl', 'self_f00', 'gfs_anl', 'gfs_f00'
        ]
        valid_config_var_values_dict[RUN_abbrev_type+'_gather_by_list'] = [
            'VALID', 'INIT', 'VSDB'
        ]
        valid_config_var_values_dict[RUN_abbrev_type+'_event_eq'] = [
            'True', 'False'
        ]
#elif RUN == 'grid2obs_step1':
#elif RUN == 'grid2obs_step2':
#elif RUN == 'precip_step1':
#elif RUN == 'precip_step2':
#elif RUN == 'satellite_step1':
#elif RUN == 'satellite_step2':
#elif RUN == 'tropcyc':
#elif RUN == 'maps2d':
#elif RUN == 'mapsda':
for config_var in list(valid_config_var_values_dict.keys()):
    if 'list' in config_var:
        for list_item in os.environ[config_var].split(' '):
            if list_item not in valid_config_var_values_dict[config_var]:
                config_var_pass = False
                failed_config_value = list_item
                break
            else:
                config_var_pass = True
    else:
        if os.environ[config_var] \
                not in valid_config_var_values_dict[config_var]:
            config_var_pass = False
            failed_config_value = os.environ[config_var]
        else:
            config_var_pass = True
    if not config_var_pass:
        print("ERROR: value of "+failed_config_value+" for "
              +config_var+" not a valid option. Valid options are "
              +', '.join(valid_config_var_values_dict[config_var]))
        exit(1)

print("END: "+os.path.basename(__file__))
