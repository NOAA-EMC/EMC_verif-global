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

# Do check for RUN_type options
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

# Do some pre-checks on list config variables lengths
check_config_var_list = ['model_dir_list', 'model_stat_dir_list',
                         'model_file_format_list', 'model_hpss_dir_list']
if RUN in ['grid2grid_step2', 'grid2obs_step2', 'precip_step2',
           'satellite_step2', 'maps2d', 'mapda']:
    check_config_var_list.append(RUN_abbrev+'_model_plot_name_list')
if RUN == 'tropcyc':
    check_config_var_list.append(RUN+'_model_atcf_name_list')
    check_config_var_list.append(RUN+'_model_file_format_list')
else:
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        if RUN == 'grid2grid_step1':
            check_config_var_list.append(
                RUN_abbrev_type+'_truth_file_format_list'
            )
        elif RUN == 'grid2grid_step2':
            check_config_var_list.append(
                RUN_abbrev_type+'_truth_name_list'
            )
            check_config_var_list.append(
                RUN_abbrev_type+'_gather_by_list'
            )
        elif RUN == 'grid2obs_step2':
            check_config_var_list.append(
                RUN_abbrev_type+'_gather_by_list'
            )
        elif RUN == 'precip_step1':
            check_config_var_list.append(
                RUN_abbrev_type+'_model_bucket_list'
            )
            check_config_var_list.append(
                RUN_abbrev_type+'_model_varname_list'
            )
            check_config_var_list.append(
                RUN_abbrev_type+'_model_file_format_list'
            )
        elif RUN == 'precip_step2':
            check_config_var_list.append(
                RUN_abbrev_type+'_gather_by_list'
            )
        elif RUN == 'satellite_step2':
            check_config_var_list.append(
                RUN_abbrev_type+'_gather_by_list'
            )
        elif RUN == 'maps2d':
            check_config_var_list.append(
                RUN_abbrev_type+'_anl_file_format_list'
            )
        elif RUN == 'mapsda':
            if RUN_type == 'gdas':
                check_config_var_list.append(
                    RUN_abbrev_type+'_model_file_format_list'
                )
                check_config_var_list.append(
                    RUN_abbrev_type+'_anl_file_format_list'
                )
            if RUN_type == 'ens':
                check_config_var_list.append(
                    RUN_abbrev_type+'_model_dir_list'
                )
                check_config_var_list.append(
                    RUN_abbrev_type+'_netcdf_suffix_list'
                )
for check_config_var in check_config_var_list:
    if len(os.environ[check_config_var].split(' ')) \
            != len(os.environ['model_list'].split(' ')):
     print("ERROR: length of "+check_config_var+" (length="
           +str(len(os.environ[check_config_var].split(' ')))
           +", values="+os.environ[check_config_var]+") not equal to length "
           +"of model_list (length="
           +str(len(os.environ['model_list'].split(' ')))+", values="
           +os.environ['model_list']+")")
     exit(1)

# Do some pre-checks on list config variables values


print("END: "+os.path.basename(__file__))
