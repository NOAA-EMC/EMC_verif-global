'''
Program Name: set_init_valid_fhr_info.py 
Contact(s): Mallory Row
Abstract: This script is run by all scripts in scripts/.
          This sets up the necessary environment variables
          for valid dates and times information, initialization
          dates and times information, and forecast hour
          information. This is written to a file and sourced
          by the scripts.
'''

import os
import numpy as np

print("BEGIN: "+os.path.basename(__file__))

# Set RUN abbreviation dictionary and set abbreviation
RUN_abbrev_dict = {
    'grid2grid_step1': 'g2g1',
    'grid2grid_step2': 'g2g2',
    'grid2obs_step1': 'g2o1',
    'grid2obs_step2': 'g2o2',
    'precip_step1': 'precip1',
    'precip_step2': 'precip2',
    'satellite_step1': 'sat1',
    'satellite_step2': 'sat2',
    'tropcyc': 'tropcyc',
    'maps2d': 'maps2d',
    'mapsda': 'mapsda'
}

# Get environment variables
RUN = os.environ['RUN']
RUN_abbrev = RUN_abbrev_dict[RUN]
if RUN != 'tropcyc':
    RUN_type_list = os.environ[RUN_abbrev+'_type_list'].split(' ')

def get_hr_list_info(hr_list):
    """! This get the beginning hour, end hour, and
         increment for cycle or valid hour list

         Args:
             hr_list - list of strings of two digit hours

         Returns:
             hr_beg - two digit string of the first hour
             hr_end - two digit string of the end hour
             hr_inc - string of the increment of the
                       hours in the list in seconds
    """
    hr_beg = (hr_list[0]).zfill(2)
    hr_end = (hr_list[-1]).zfill(2)
    hr_inc = str(int((24/len(hr_list))*3600))
    return hr_beg, hr_end, hr_inc

def get_forecast_hours(fcyc_list, vhr_list, fhr_min_str, fhr_max_str):
    """! This creates a list of forecast hours to be
         considered

         Args:
             fcyc_list   - list of strings of two digit cycle hours
             vhr_list    - list of strings of two digit valid hours
             fhr_min_str - string of the first forecast hour
             fhr_max_str - string of the last forecast hour

         Returns:
             fhr_list - string of all forecast hours
                        to be considered in the verification
    """
    fhr_min = float(fhr_min_str)
    fhr_max = float(fhr_max_str)
    nfcyc = len(fcyc_list)
    nvhr = len(vhr_list)
    if nfcyc > nvhr:
        fhr_intvl = int(24/nfcyc)
    else:
        fhr_intvl = int(24/nvhr)
    nfhr = fhr_max/fhr_intvl
    fhr_max = int(nfhr*fhr_intvl)
    fhr_list = []
    fhr = fhr_min
    while fhr <= fhr_max:
        fhr_list.append(str(int(fhr)).zfill(2))
        fhr+=fhr_intvl
    fhr_list_str = ', '.join(fhr_list)
    return fhr_list_str

env_var_dict = {}
env_var_dict['RUN_abbrev'] = RUN_abbrev
if RUN in ['grid2grid_step1', 'grid2grid_step2',
           'grid2obs_step1', 'grid2obs_step2',
           'precip_step1', 'precip_step2',
           'satellite_step1', 'satellite_step2']:
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        # Process forecast initialization cycles
        RUN_abbrev_type_fcyc_list = (
            os.environ[RUN_abbrev_type+'_fcyc_list'].split(' ')
        )
        (RUN_abbrev_type_fcyc_beg,
         RUN_abbrev_type_fcyc_end,
         RUN_abbrev_type_fcyc_inc) = \
            get_hr_list_info(RUN_abbrev_type_fcyc_list)
        env_var_dict[RUN_abbrev_type+'_init_hr_beg'] = RUN_abbrev_type_fcyc_beg
        env_var_dict[RUN_abbrev_type+'_init_hr_end'] = RUN_abbrev_type_fcyc_end
        env_var_dict[RUN_abbrev_type+'_init_hr_inc'] = RUN_abbrev_type_fcyc_inc
        # Process valid hours
        # note: precip and satellite require special processing
        if 'precip' in RUN:
            if RUN_type == 'ccpa_accum24hr':
                RUN_abbrev_type_vhr_list = [ '12' ]
                RUN_abbrev_type_obs_daily_file = 'True'
        elif 'satellite' in RUN:
            if RUN_type in ['ghrsst_ncei_avhrr_anl',
                            'ghrsst_ospo_geopolar_anl']:
                RUN_abbrev_type_vhr_list = [ '00' ]
                RUN_abbrev_type_obs_daily_file = 'True'
        else:
            RUN_abbrev_type_vhr_list = (
                os.environ[RUN_abbrev_type+'_vhr_list'].split(' ')
            )
        (RUN_abbrev_type_vhr_beg,
         RUN_abbrev_type_vhr_end,
         RUN_abbrev_type_vhr_inc) = get_hr_list_info(RUN_abbrev_type_vhr_list)
        env_var_dict[RUN_abbrev_type+'_valid_hr_beg'] = RUN_abbrev_type_vhr_beg
        env_var_dict[RUN_abbrev_type+'_valid_hr_end'] = RUN_abbrev_type_vhr_end
        env_var_dict[RUN_abbrev_type+'_valid_hr_inc'] = RUN_abbrev_type_vhr_inc
        if RUN in ['precip_step1', 'satellite_step1']:
            env_var_dict[RUN_abbrev_type+'_obs_daily_file'] = (
                RUN_abbrev_type_obs_daily_file
            )
        # Process forecast hours
        # note: precip and satellite require special processing
        RUN_abbrev_type_fhr_min = os.environ[RUN_abbrev_type+'_fhr_min']
        RUN_abbrev_type_fhr_max = os.environ[RUN_abbrev_type+'_fhr_max']
        if 'precip' in RUN or 'satellite' in RUN:
            if 'precip' in RUN:
                RUN_abbrev_type_accum_length = (
                    RUN_type.split('accum')[1].replace('hr','')
                )
            elif 'satellite' in RUN:
                if RUN_type in ['ghrsst_ncei_avhrr_anl',
                                'ghrsst_ospo_geopolar_anl']:
                    RUN_abbrev_type_accum_length = '24'
            if int(RUN_abbrev_type_fhr_min) \
                    < int(RUN_abbrev_type_accum_length):
                RUN_abbrev_type_fhr_min = RUN_abbrev_type_accum_length
            RUN_abbrev_type_fhr_min_vhr_fcyc_list = []
            for vhr in RUN_abbrev_type_vhr_list:
                for fcyc in RUN_abbrev_type_fcyc_list:
                    fhr_min_vhr_fcyc = (
                        int(RUN_abbrev_type_fhr_min)
                        + (int(vhr) - int(fcyc))
                    )
                    print(vhr+' '+fcyc+' '+str(fhr_min_vhr_fcyc))
                    if fhr_min_vhr_fcyc < int(RUN_abbrev_type_accum_length):
                        fhr_min_vhr_fcyc+=int(RUN_abbrev_type_accum_length)
                    RUN_abbrev_type_fhr_min_vhr_fcyc_list.append(
                        fhr_min_vhr_fcyc
                    )
            RUN_abbrev_type_fhr_min = np.amin(
                np.array(RUN_abbrev_type_fhr_min_vhr_fcyc_list)
            )
        RUN_abbrev_type_fhr_list_str = get_forecast_hours(
            RUN_abbrev_type_fcyc_list, RUN_abbrev_type_vhr_list,
            RUN_abbrev_type_fhr_min, RUN_abbrev_type_fhr_max
        )
        env_var_dict[RUN_abbrev_type+'_fhr_list'] = (
            RUN_abbrev_type_fhr_list_str
        )
elif RUN == 'tropcyc':
    # Process forecast initialization cycles
    RUN_abbrev_fcyc_list = os.environ[RUN_abbrev+'_fcyc_list'].split(' ')
    RUN_abbrev_fcyc_beg, RUN_abbrev_fcyc_end, RUN_abbrev_fcyc_inc = (
        get_hr_list_info(RUN_abbrev_fcyc_list)
    )
    env_var_dict[RUN_abbrev+'_init_hr_beg'] = RUN_abbrev_fcyc_beg
    env_var_dict[RUN_abbrev+'_init_hr_end'] = RUN_abbrev_fcyc_end
    env_var_dict[RUN_abbrev+'_init_hr_inc'] = RUN_abbrev_fcyc_inc
    # Process valid hours
    RUN_abbrev_vhr_list = os.environ[RUN_abbrev+'_vhr_list'].split(' ')
    RUN_abbrev_vhr_beg, RUN_abbrev_vhr_end, RUN_abbrev_vhr_inc = (
        get_hr_list_info(RUN_abbrev_vhr_list)
    )
    env_var_dict[RUN_abbrev+'_valid_hr_beg'] = RUN_abbrev_vhr_beg
    env_var_dict[RUN_abbrev+'_valid_hr_end'] = RUN_abbrev_vhr_end
    env_var_dict[RUN_abbrev+'_valid_hr_inc'] = RUN_abbrev_vhr_inc
    # Process forecast hours
    RUN_abbrev_fhr_min = os.environ[RUN_abbrev+'_fhr_min']
    RUN_abbrev_fhr_max = os.environ[RUN_abbrev+'_fhr_max']
    RUN_abbrev_fhr_list_str = get_forecast_hours(
        RUN_abbrev_fcyc_list, RUN_abbrev_vhr_list,
        RUN_abbrev_fhr_min, RUN_abbrev_fhr_max
    )
    env_var_dict[RUN_abbrev+'_fhr_list'] = RUN_abbrev_fhr_list_str
elif RUN in ['maps2d', 'mapsda']:
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        # Process hour information
        RUN_abbrev_type_make_met_data_by = (
            os.environ[RUN_abbrev_type+'_make_met_data_by']
        )
        RUN_abbrev_type_hr_list = (
            os.environ[RUN_abbrev_type+'_hour_list'].split(' ')
        )
        (RUN_abbrev_type_hr_beg,
         RUN_abbrev_type_hr_end,
         RUN_abbrev_type_hr_inc) = get_hr_list_info(RUN_abbrev_type_hr_list)
        env_var_dict[RUN_abbrev_type+'_hr_beg'] = RUN_abbrev_type_hr_beg
        env_var_dict[RUN_abbrev_type+'_hr_end'] = RUN_abbrev_type_hr_end
        env_var_dict[RUN_abbrev_type+'_hr_inc'] = RUN_abbrev_type_hr_inc
        env_var_dict[RUN_abbrev_type+'_make_met_data_by'] = (
            RUN_abbrev_type_make_met_data_by
        )
        # Process forecast hours
        if RUN == 'maps2d':
            RUN_abbrev_type_forecast_to_plot_list = (
                os.environ[RUN_abbrev_type+'_forecast_to_plot_list'].split(' ')
            )
            RUN_abbrev_type_fhr_list_str = ', '.join(
                RUN_abbrev_type_forecast_to_plot_list
            )
            env_var_dict[RUN_abbrev_type+'_fhr_list'] = (
                RUN_abbrev_type_fhr_list_str
            )
        elif RUN == 'mapsda':
            RUN_abbrev_type_guess_hour = (
                os.environ[RUN_abbrev_type+'_guess_hour']
            )
            env_var_dict[RUN_abbrev_type+'_guess_hour'] = (
               RUN_abbrev_type_guess_hour.zfill(2)
            )

# Create file with environment variables to source
with open('python_gen_env_vars.sh', 'a') as file:
    file.write('#!/bin/sh\n')
    file.write('echo BEGIN: python_gen_env_vars.sh\n')
    for name, value in env_var_dict.items():
        file.write('export '+name+'='+'"'+value+'"\n')
    file.write('echo END: python_gen_env_vars.sh')

print("END: "+os.path.basename(__file__))
