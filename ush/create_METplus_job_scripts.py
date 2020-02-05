'''
Program Name: create_METplus_job_scripts.py
Contact(s): Mallory Row
Abstract: This script is run by all scripts in scripts/.
          This creates multiple independent job cards. These
          jobs contain all the necessary environment variables 
          and METplus commands to needed to run the specific
          METplus verification use case and types (each job
          could be run independenttly on the command line).
'''

import sys
import os
import datetime
import glob 

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
METplus_version = os.environ['METplus_version']
PARMverif_global = os.environ['PARMverif_global']
USHMETplus = os.environ['USHMETplus']
USHverif_global = os.environ['USHverif_global']
DATA = os.environ['DATA']
RUN = os.environ['RUN']
machine = os.environ['machine']
MPMD = os.environ['MPMD']
nproc = int(os.environ['nproc'])

if RUN == 'grid2grid_step1':
    type_list = os.environ['g2g1_type_list'].split(' ')
    case = 'grid2grid'
if RUN == 'grid2grid_step2':
    type_list = os.environ['g2g2_type_list'].split(' ')
    case = 'grid2grid'
elif RUN == 'grid2obs_step1':
    type_list = os.environ['g2o1_type_list'].split(' ')
    case = 'grid2obs'
elif RUN == 'grid2obs_step2':
    type_list = os.environ['g2o2_type_list'].split(' ')
    case = 'grid2obs'
elif RUN == 'precip_step1':
    type_list = os.environ['precip1_type_list'].split(' ')
    case = 'precip'
elif RUN == 'precip_step2':
    type_list = os.environ['precip2_type_list'].split(' ')
    case = 'precip'
elif RUN == 'maps2d':
    type_list = os.environ['maps2d_type_list'].split(' ')
model_list = os.environ['model_list'].split(' ')
model_arch_dir_list = os.environ['model_arch_dir_list'].split(' ')
start_date = os.environ['start_date']
end_date = os.environ['end_date']
make_met_data_by = os.environ['make_met_data_by']
plot_by = os.environ['plot_by']

# METplus paths
master_metplus = os.path.join(USHMETplus, 'master_metplus.py')
metplus_machine_conf = os.path.join(PARMverif_global, 'metplus_config',
                                    'machine.conf')
metplus_version_conf_dir = os.path.join(PARMverif_global,
                                        'metplus_config',
                                        'metplus_use_cases',
                                        'METplusV'+METplus_version)

# Set up date information
sdate = datetime.datetime(int(start_date[0:4]), int(start_date[4:6]),
                          int(start_date[6:]))
edate = datetime.datetime(int(end_date[0:4]), int(end_date[4:6]),
                          int(end_date[6:]))

def set_job_common_env(job_file):
    """! Writes out environment variables common
         to all METplus job
        
         Args:
             job_file - string of the path of the
                        METplus job card name
 
         Returns:
    """
    env_var_list = [ 'HOMEverif_global', 'USHverif_global', 'HOMEMETplus',
                     'HOMEMET', 'DATA', 'RUN', 'WGRIB2', 'NCAP2', 'NCDUMP',
                     'CONVERT', 'METplus_verbosity', 'MET_verbosity', 
                     'log_MET_output_to_METplus', 'PARMverif_global',
                     'USHMETplus', 'FIXverif_global', 'METplus_version',
                     'MET_version' ]
    job_file.write('#!/bin/sh\n')
    for env_var in env_var_list:
        job_file.write('export '+env_var+'="'+os.environ[env_var]+'"\n')

def create_job_script_step1(sdate, edate, model_list, type_list, case):
    """! Writes out job cards based on requested verification
         for step 1 jobs
        
         Args:
             sdate      - datetime object of the verification start
                          date
             edate      - datetime object of the verification end
                          date
             model_list - list of strings of model names
             type_list  - list of strings of the types of the
                          verification use case
             case       - string of the verification use case
 
         Returns:
    """
    njob = 0
    date = sdate
    while date <= edate:
        for model in model_list:
            for type in type_list:
                njob+=1
                # Set up information for environment variables
                if case == 'grid2grid':
                    fhr_list = os.environ['g2g1_fhr_list']
                    gather_by = os.environ['g2g1_gather_by']
                    valid_hr_beg = os.environ['g2g1_valid_hr_beg']
                    valid_hr_end = os.environ['g2g1_valid_hr_end']
                    valid_hr_inc = os.environ['g2g1_valid_hr_inc']
                    init_hr_beg = os.environ['g2g1_init_hr_beg']
                    init_hr_end = os.environ['g2g1_init_hr_end']
                    init_hr_inc = os.environ['g2g1_init_hr_inc']
                    extra_env_info = {}
                    if type == 'sfc':
                        obtype = model+'_f00'
                    else:
                        if os.environ['g2g1_anl_name'] == 'self_anl':
                            obtype = model+'_anl'
                        elif os.environ['g2g1_anl_name'] == 'self_f00':
                            obtype = model+'_f00'
                        elif os.environ['g2g1_anl_name'] == 'gfs_anl':
                            obtype = 'gfs_anl'
                        elif os.environ['g2g1_anl_name'] == 'gfs_f00':
                            obtype = 'gfs_f00'
                        anl_file_list = glob.glob(
                            os.path.join(os.environ['DATA'], 
                                         'grid2grid_step1', 'data', model,
                                         'anl.'+date.strftime('%Y%m%d')+'*')
                        )
                        link_anl_type = []
                        if len(anl_file_list) > 0:
                            for anl_file in anl_file_list:
                                if os.path.islink(anl_file):
                                    if (os.readlink(anl_file) ==
                                            anl_file.replace('anl', 'f00')):
                                        link_anl_type.append('f00')
                                    else:
                                        link_anl_type.append('anl')
                                else:
                                    if os.path.exists(anl_file):
                                        link_anl_type.append('anl')
                            if all(anl == 'f00' for anl in link_anl_type):
                                obtype = obtype.replace('anl', 'f00')
                    extra_env_info['verif_grid'] = os.environ['g2g1_grid']
                elif case == 'grid2obs':
                    gather_by = os.environ['g2o1_gather_by']
                    init_hr_beg = os.environ['g2o1_init_hr_beg']
                    init_hr_end = os.environ['g2o1_init_hr_end']
                    init_hr_inc = os.environ['g2o1_init_hr_inc']
                    extra_env_info = {}
                    if type == 'upper_air':
                        fhr_list = os.environ['g2o1_fhr_list_upper_air']
                        obtype = os.environ['g2o1_obtype_upper_air']
                        valid_hr_beg = (
                            os.environ['g2o1_valid_hr_beg_upper_air']
                        )
                        valid_hr_end = (
                            os.environ['g2o1_valid_hr_end_upper_air']
                        )
                        valid_hr_inc = (
                            os.environ['g2o1_valid_hr_inc_upper_air']
                        )
                        extra_env_info['prepbufr'] = 'gdas'
                        extra_env_info['verif_grid'] = (
                            os.environ['g2o1_grid_upper_air']
                        )
                    elif type == 'conus_sfc':
                        fhr_list = os.environ['g2o1_fhr_list_conus_sfc']
                        obtype = os.environ['g2o1_obtype_conus_sfc']
                        valid_hr_beg = (
                            os.environ['g2o1_valid_hr_beg_conus_sfc']
                        )
                        valid_hr_end = (
                            os.environ['g2o1_valid_hr_end_conus_sfc']
                        )
                        valid_hr_inc = (
                            os.environ['g2o1_valid_hr_inc_conus_sfc']
                        )
                        if int(date.strftime('%Y%m%d')) > 20170319:
                            extra_env_info['prepbufr'] = 'nam'
                        else:
                            extra_env_info['prepbufr'] = 'ndas'
                        extra_env_info['verif_grid'] = (
                            os.environ['g2o1_grid_conus_sfc']
                        )
                elif case == 'precip':
                    gather_by = os.environ['precip1_gather_by']
                    fhr_list = os.environ['precip1_fhr_list']
                    obtype = os.environ['precip1_obtype']
                    valid_hr_beg = os.environ['precip1_valid_hr_beg']
                    valid_hr_end = os.environ['precip1_valid_hr_end']
                    valid_hr_inc = os.environ['precip1_valid_hr_inc']
                    init_hr_beg = os.environ['precip1_init_hr_beg']
                    init_hr_end = os.environ['precip1_init_hr_end']
                    init_hr_inc = os.environ['precip1_init_hr_inc']
                    extra_env_info = {}
                    extra_env_info['verif_grid'] = os.environ['precip1_grid']
                    model_bucket_list = (
                        os.environ['precip1_model_bucket_list'].split(' ')
                    )
                    model_varname_list = (
                        os.environ['precip1_model_varname_list'].split(' ')
                    )
                    model_fileformat_list = (
                        os.environ['precip1_model_fileformat_list'].split(' ')
                    )
                    model_index = model_list.index(model)
                    extra_env_info['model_bucket'] = (
                        model_bucket_list[model_index]
                    )
                    extra_env_info['model_varname'] = (
                        model_varname_list[model_index]
                    )
                    extra_env_info['model_filetype'] = (
                        model_fileformat_list[model_index][0:4]
                    )
                # Create job file
                job_filename = os.path.join(DATA, RUN,
                                            'metplus_job_scripts',
                                            'job'+str(njob))
                job_file = open(job_filename, 'w')
                set_job_common_env(job_file)
                job_file.write('export DATE="'+date.strftime('%Y%m%d')+'"\n')
                job_file.write('export model="'+model+'"\n')
                job_file.write('export obtype="'+obtype+'"\n')
                job_file.write('export make_met_data_by="'+make_met_data_by+'"\n')
                job_file.write('export gather_by="'+gather_by+'"\n')
                job_file.write('export fhr_list="'+fhr_list+'"\n')
                job_file.write('export valid_hr_beg="'+valid_hr_beg+'"\n')
                job_file.write('export valid_hr_end="'+valid_hr_end+'"\n')
                job_file.write('export valid_hr_inc="'+valid_hr_inc+'"\n')
                job_file.write('export init_hr_beg="'+init_hr_beg+'"\n')
                job_file.write('export init_hr_end="'+init_hr_end+'"\n')
                job_file.write('export init_hr_inc="'+init_hr_inc+'"\n')
                for name, value in extra_env_info.items():
                    job_file.write('export '+name+'="'+value+'"\n')
                job_file.write('\n')
                metplus_conf_list = [
                    os.path.join(metplus_version_conf_dir, case,
                                 'make_met_data_by_'+make_met_data_by,
                                 type+'.conf')
                ]
                if case == 'grid2grid' and type == 'anom':
                    metplus_conf_list.append(
                        os.path.join(metplus_version_conf_dir, case,
                                     'make_met_data_by_'+make_met_data_by,
                                     type+'_height.conf')
                    )
                metplus_conf_list.append(
                    os.path.join(metplus_version_conf_dir, case,
                                 'gather_by_'+gather_by,
                                 type+'.conf')
                )
                for metplus_conf in metplus_conf_list:
                    job_file.write(
                        master_metplus+' '
                        +'-c '+metplus_machine_conf+' '
                        +'-c '+metplus_conf+'\n'
                    )
                job_file.close()
        date = date + datetime.timedelta(days=1)

def create_job_script_step2(sdate, edate, model_list, type_list, case):
    """! Writes out job cards based on requested verification
         for step 2 jobs
        
         Args:
             sdate      - datetime object of the verification start
                          date
             edate      - datetime object of the verification end
                          date
             model_list - list of strings of model names
             type_list  - list of strings of the types of the
                          verification use case
             case       - string of the verification use case
 
         Returns:
    """
    njob = 0
    for type in type_list:
        # Set up information for environment variables
        if case == 'grid2grid':
            model_plot_name_list = (
                os.environ['g2g2_model_plot_name_list'].split(' ')
            )
            anl_name_list = os.environ['g2g2_anl_name_list'].split(' ')
            if len(model_plot_name_list) != len(model_list):
                print(
                    "model_list and g2g2_model_plot_name_list "
                    +"not of equal length"
                )
                exit(1)
            if len(anl_name_list) != len(model_list):
                print(
                    "model_list and g2g2_anl_name_list not of equal length"
                )
                exit(1)
            fhr_list = os.environ['g2g2_fhr_list']
            valid_hr_beg = os.environ['g2g2_valid_hr_beg']
            valid_hr_end = os.environ['g2g2_valid_hr_end']
            valid_hr_inc = os.environ['g2g2_valid_hr_inc']
            init_hr_beg = os.environ['g2g2_init_hr_beg']
            init_hr_end = os.environ['g2g2_init_hr_end']
            init_hr_inc = os.environ['g2g2_init_hr_inc']
            event_equalization = os.environ['g2g2_event_eq']
            interp = 'NEAREST'
            extra_env_info = {}
            extra_env_info['verif_grid'] = os.environ['g2g2_grid']
            if type == 'anom':
                line_type = 'SAL1L2, VAL1L2'
                plot_stats_list = 'acc'
                vx_mask_list = ['G002', 'NHX', 'SHX', 
                                'PNA', 'TRO']
                vars_and_levels_dict = {
                    'HGT': ['P1000', 'P700', 'P500', 'P250'],
                    'TMP': ['P850', 'P500', 'P250'],
                    'UGRD': ['P850', 'P500', 'P250'],
                    'VGRD': ['P850', 'P500', 'P250'],
                    'UGRD_VGRD': ['P850', 'P500', 'P250'],
                    'PRMSL': ['Z0']
                }
            elif type == 'pres':
                line_type = 'SL1L2, VL1L2'
                plot_stats_list = (
                    'bias, rmse, msess, rsd, rmse_md, rmse_pv'
                )
                vx_mask_list = ['G002', 'NHX', 'SHX',
                                'PNA', 'TRO']
                vars_and_levels_dict = {
                    'HGT': ['P1000', 'P850', 'P700', 
                            'P500', 'P200', 'P100', 
                             'P50', 'P20', 'P10'],
                    'TMP': ['P1000', 'P850', 'P700',
                            'P500', 'P200', 'P100',
                            'P50', 'P20', 'P10'],
                    'UGRD': ['P1000', 'P850', 'P700',
                             'P500', 'P200', 'P100',
                             'P50', 'P20', 'P10'],
                    'VGRD': ['P1000', 'P850', 'P700',
                             'P500', 'P200', 'P100',
                             'P50', 'P20', 'P10'],
                    'UGRD_VGRD': ['P1000', 'P850', 'P700',
                                  'P500', 'P200', 'P100',
                                  'P50', 'P20', 'P10'],
                    'O3MR': ['P100', 'P70', 'P50', 
                             'P30', 'P20', 'P10']
                }
            elif type == 'sfc':
                line_type = 'SL1L2, VL1L2'
                plot_stats_list = 'fbar'
                vx_mask_list = ['G002', 'NHX', 'SHX', 
                                'N60', 'S60', 'TRO',
                                'NPO', 'SPO', 'NAO',
                                'SAO', 'CONUS']
                vars_and_levels_dict = {
                    'TMP': ['Z2', 'Z0', 'L0'],
                    'RH': ['Z2'],
                    'SPFH': ['Z2'],
                    'HPBL': ['L0'],
                    'PRES': ['Z0', 'L0'],
                    'PRMSL': ['Z0'],
                    'UGRD': ['Z10'],
                    'VGRD': ['Z10'],
                    'TSOIL': ['Z10-0'],
                    'SOILW': ['Z10-0'],
                    'WEASD': ['Z0'],
                    'CAPE': ['Z0'],
                    'PWAT': ['L0'],
                    'CWAT': ['L0'],
                    'HGT': ['L0'],
                    'TOZNE': ['L0']
                }
            model_info = {}
            nmodels = int(len(model_list))
            if nmodels > 8:
                print(
                    "Too many models listed in model_list. "
                    +"Current maximum is 8."
                )
                exit(1)
            for model in model_list:
                index = model_list.index(model)
                model_num = index + 1
                model_info['model'+str(model_num)] = model
                model_info['model'+str(model_num)+'_plot_name'] = (
                         model_plot_name_list[index]
                )
                if (len(model_arch_dir_list) != len(model_list) 
                        and len(model_arch_dir_list) > 1):
                    print(
                        "model_arch_dir_list and model_list not of "
                        +"equal length"
                    )
                    exit(1)
                elif (len(model_arch_dir_list) != len(model_list) 
                        and len(model_arch_dir_list) == 1):
                    model_info['model'+str(model_num)+'_arch_dir'] = (
                        model_arch_dir_list[0]
                    )
                else:
                    model_info['model'+str(model_num)+'_arch_dir'] = (
                        model_arch_dir_list[index]
                    )
                if type == 'sfc':
                    obtype = model+'_f00'
                else:
                    anl_name = anl_name_list[index]
                    if anl_name == 'self_anl':
                        obtype = model+'_anl'
                    elif anl_name == 'self_f00':
                        obtype = model+'_f00'
                    elif anl_name == 'gfs_anl':
                        obtype = 'gfs_anl'
                    elif anl_name == 'gfs_f00':
                        obtype = 'gfs_f00'
                model_info['model'+str(model_num)+'_obtype'] = obtype
        elif case == 'grid2obs':
            model_plot_name_list = (
                os.environ['g2o2_model_plot_name_list'].split(' ')
            )
            if len(model_plot_name_list) != len(model_list):
                print(
                    "model_list and g2o2_model_plot_name_list "
                    +"are not of equal length"
                )
                exit(1)
            init_hr_beg = os.environ['g2o2_init_hr_beg']
            init_hr_end = os.environ['g2o2_init_hr_end']
            init_hr_inc = os.environ['g2o2_init_hr_inc']
            event_equalization = os.environ['g2o2_event_eq']
            interp = 'BILIN'
            line_type = 'SL1L2, VL1L2'
            plot_stats_list = 'bias, rmse, fbar_obar'
            extra_env_info = {}
            if type == 'upper_air':
                fhr_list = os.environ['g2o2_fhr_list_upper_air']
                obtype = os.environ['g2o2_obtype_upper_air']
                valid_hr_beg = (
                    os.environ['g2o2_valid_hr_beg_upper_air']
                )
                valid_hr_end = (
                    os.environ['g2o2_valid_hr_end_upper_air']
                )
                valid_hr_inc = (
                    os.environ['g2o2_valid_hr_inc_upper_air']
                )
                extra_env_info['verif_grid'] = (
                    os.environ['g2o2_grid_upper_air']
                )
                vx_mask_list = ['G003', 'NH', 'SH', 'TRO', 'G236']
                vars_and_levels_dict = {
                    'TMP': ['P1000', 'P925', 'P850', 'P700', 'P500', 'P400',
                            'P300', 'P250', 'P200', 'P150', 'P100', 'P50'],
                    'RH': ['P1000', 'P925', 'P850', 'P700', 'P500', 'P400',
                           'P300'],
                    'UGRD_VGRD': ['P1000', 'P925', 'P850', 'P700', 'P500',
                                  'P400', 'P300', 'P250', 'P200', 'P150',
                                   'P100', 'P50']
                }
            elif type == 'conus_sfc':
                fhr_list = os.environ['g2o2_fhr_list_conus_sfc']
                obtype = os.environ['g2o2_obtype_conus_sfc']
                valid_hr_beg = (
                    os.environ['g2o2_valid_hr_beg_conus_sfc']
                )
                valid_hr_end = (
                    os.environ['g2o2_valid_hr_end_conus_sfc']
                )
                valid_hr_inc = (
                    os.environ['g2o2_valid_hr_inc_conus_sfc']
                )
                extra_env_info['verif_grid'] = (
                    os.environ['g2o2_grid_conus_sfc']
                )
                vx_mask_list = ['G104', 'WEST', 'EAST', 'MDW', 'NPL', 'SPL',
                                'NEC', 'SEC', 'NWC', 'SWC', 'NMT', 'SMT',
                                'SWD', 'GRB', 'LMV', 'GMC', 'APL', 'NAK',
                                'SAK']
                vars_and_levels_dict = {
                    'TMP': ['Z2'],
                    'RH': ['Z2'],
                    'DPT': ['Z2'],
                    'UGRD_VGRD': ['Z10'],
                    'TCDC': ['L0'],
                    'PRMSL': ['Z0']
                }
            model_info = {}
            nmodels = int(len(model_list))
            if nmodels > 8:
                print(
                    "Too many models listed in model_list. "
                    +"Current maximum is 8."
                )
                exit(1)
            for model in model_list:
                index = model_list.index(model)
                model_num = index + 1
                model_info['model'+str(model_num)] = model
                model_info['model'+str(model_num)+'_plot_name'] = (
                         model_plot_name_list[index]
                )
                if (len(model_arch_dir_list) != len(model_list)
                        and len(model_arch_dir_list) > 1):
                    print(
                        "model_arch_dir_list and model_list not of "
                        +"equal length"
                    )
                    exit(1)
                elif (len(model_arch_dir_list) != len(model_list)
                        and len(model_arch_dir_list) == 1):
                    model_info['model'+str(model_num)+'_arch_dir'] = (
                        model_arch_dir_list[0]
                    )
                else:
                    model_info['model'+str(model_num)+'_arch_dir'] = (
                        model_arch_dir_list[index]
                    )
                model_info['model'+str(model_num)+'_obtype'] = obtype
        elif case == 'precip':
            model_plot_name_list = (
                os.environ['precip2_model_plot_name_list'].split(' ')
            )
            if len(model_plot_name_list) != len(model_list):
                print(
                    "model_list and precip2_model_plot_name_list "
                    +"not of equal length"
                )
                exit(1)
            obtype = os.environ['precip2_obtype'] 
            fhr_list = os.environ['precip2_fhr_list']
            valid_hr_beg = os.environ['precip2_valid_hr_beg']
            valid_hr_end = os.environ['precip2_valid_hr_end']
            valid_hr_inc = os.environ['precip2_valid_hr_inc']
            init_hr_beg = os.environ['precip2_init_hr_beg']
            init_hr_end = os.environ['precip2_init_hr_end']
            init_hr_inc = os.environ['precip2_init_hr_inc']
            event_equalization = os.environ['precip2_event_eq']
            interp = 'NEAREST'
            line_type = 'CTC'
            plot_stats_list = 'bias, ets'
            vx_mask_list = ['G211']
            extra_env_info = {}
            extra_env_info['verif_grid'] = os.environ['precip2_grid']
            extra_env_info['var_thresholds'] = (
                'ge0.2, ge2, ge5, ge10, ge15, ge25, ge35, ge50, ge75'
            )
            extra_env_info['PYTHONPATH'] = os.environ['PYTHONPATH']
            if type == 'ccpa_accum24hr':
                vars_and_levels_dict = {
                    'APCP_24': ['A24']
                }
            model_info = {}
            nmodels = int(len(model_list))
            if nmodels > 8:
                print(
                    "Too many models listed in model_list. "
                    +"Current maximum is 8."
                )
                exit(1)
            for model in model_list:
                index = model_list.index(model)
                model_num = index + 1
                model_info['model'+str(model_num)] = model
                model_info['model'+str(model_num)+'_plot_name'] = (
                         model_plot_name_list[index]
                )
                if (len(model_arch_dir_list) != len(model_list)
                        and len(model_arch_dir_list) > 1):
                    print(
                        "model_arch_dir_list and model_list not of "
                        +"equal length"
                    )
                    exit(1)
                elif (len(model_arch_dir_list) != len(model_list)
                        and len(model_arch_dir_list) == 1):
                    model_info['model'+str(model_num)+'_arch_dir'] = (
                        model_arch_dir_list[0]
                    )
                else:
                    model_info['model'+str(model_num)+'_arch_dir'] = (
                        model_arch_dir_list[index]
                    )
                model_info['model'+str(model_num)+'_obtype'] = obtype
        for var_name, var_levels in vars_and_levels_dict.items():
            for vx_mask in vx_mask_list:
                njob+=1
                # Create job file
                job_filename = os.path.join(DATA, RUN,
                                            'metplus_job_scripts',
                                            'job'+str(njob))
                job_file = open(job_filename, 'w')
                set_job_common_env(job_file)
                job_file.write('export START_DATE="'
                               +sdate.strftime('%Y%m%d')+'"\n')
                job_file.write('export END_DATE="'
                               +edate.strftime('%Y%m%d')+'"\n')
                job_file.write('export plot_by="'+plot_by+'"\n')
                job_file.write('export fhr_list="'+fhr_list+'"\n')
                job_file.write('export valid_hr_beg="'+valid_hr_beg+'"\n')
                job_file.write('export valid_hr_end="'+valid_hr_end+'"\n')
                job_file.write('export valid_hr_inc="'+valid_hr_inc+'"\n')
                job_file.write('export init_hr_beg="'+init_hr_beg+'"\n')
                job_file.write('export init_hr_end="'+init_hr_end+'"\n')
                job_file.write('export init_hr_inc="'+init_hr_inc+'"\n')
                job_file.write('export var_name="'+var_name+'"\n')
                job_file.write('export var_levels="'
                               +' '.join(var_levels).replace(' ', ', ')+'"\n')
                job_file.write('export vx_mask="'+vx_mask+'"\n')
                job_file.write('export line_type="'+line_type+'"\n')
                job_file.write('export plot_stats_list="'
                               +plot_stats_list+'"\n')
                job_file.write('export event_equalization="'
                               +event_equalization+'"\n')
                job_file.write('export interp="'+interp+'"\n')
                job_file.write('export verif_case_type="'+type+'"\n')
                for name, value in model_info.items():
                    job_file.write('export '+name+'="'+value+'"\n')
                for name, value in extra_env_info.items():
                    job_file.write('export '+name+'="'+value+'"\n')
                job_file.write('\n')
                job_file.write('python '
                               +os.path.join(USHverif_global,
                                             'prune_stat_files.py\n\n'))
                if (case == 'grid2grid' and type == 'anom'
                        and var_name == 'HGT'):
                    metplus_conf = os.path.join(metplus_version_conf_dir,
                                                case, 'plot_by_'+plot_by,
                                                type+'_height_nmodels'
                                                +str(nmodels)+'.conf\n')
                else:
                    metplus_conf = os.path.join(metplus_version_conf_dir,
                                                case, 'plot_by_'+plot_by,
                                                type+'_nmodels'
                                                +str(nmodels)+'.conf\n')
                job_file.write(
                    master_metplus+' '
                    +'-c '+metplus_machine_conf+' '
                    +'-c '+metplus_conf+'\n'
                )
                if case == 'precip':
                    job_file.write(
                        os.path.join(USHverif_global, 'plotting_scripts',
                                     'make_plots_wrapper_precip.py')+' '
                        +'-c '+metplus_machine_conf+' '
                        +'-c '+metplus_conf+'\n'
                )
                job_file.write('nimgs=$(ls '
                               +os.path.join(DATA, RUN, 'metplus_output',
                                             'plot_by_'+plot_by, 'make_plots',
                                              var_name+'_'+vx_mask, case, type,
                                             'imgs', '*')
                               +' |wc -l)\n')
                job_file.write('if [ $nimgs -ne 0 ]; then\n')
                job_file.write(
                        '    ln -sf '
                        +os.path.join(DATA, RUN, 'metplus_output',
                                      'plot_by_'+plot_by, 'make_plots',
                                      var_name+'_'+vx_mask, case, type,
                                      'imgs', '*')+' '
                        +os.path.join(DATA, RUN, 'metplus_output',
                                      'images/.')+'\n'
                )
                job_file.write('fi')
                job_file.close()

def create_job_script_tropcyc(model_list, storm_list):
    """! Writes out job cards based on requested verification
         for tropical cyclone verification
        
         Args:
             model_list - list of strings of model names
             storm_list - list of strings of the basin, year,
                          and storm name
 
         Returns:
    """
    METplus_tropcyc_process = os.environ['METplus_tropcyc_process']
    model_atcf_name_list = (
        os.environ['tropcyc_model_atcf_name_list'].split(' ')
    )
    if METplus_tropcyc_process == 'tc_pairs':
        njob = 0
    else:
        njob = len(glob.glob(
            os.path.join(DATA, RUN, 'metplus_job_scripts','job*')
        ))
        os.environ['njob_from_tc_pairs'] = str(njob)
        npoe = len(glob.glob(
            os.path.join(DATA, RUN, 'metplus_job_scripts','poe*')
        ))
        os.environ['npoe_from_tc_pairs'] = str(npoe)
    basin_list = []
    for storm in storm_list:
        basin = storm.split('_')[0]
        year = storm.split('_')[1]
        name = storm.split('_')[2]
        if basin not in basin_list:
            basin_list.append(basin)
        if storm == 'WP_2018_HECTOR':
            basin = 'EP'
        storm_id =  get_tc_info.get_tc_storm_id(storm)
        bdeck_data_dir = os.path.join(os.getcwd(), 'data', 'bdeck')
        bdeck_filename = 'b'+storm_id+'.dat'
        bdeck_file = os.path.join(bdeck_data_dir, bdeck_filename)
        storm_start_date, storm_end_date = get_tc_info.get_tc_storm_dates(
            bdeck_file
        )
        if METplus_tropcyc_process == 'tc_pairs':
            for model in model_list:
                njob+=1
                index = model_list.index(model)
                model_atcf_abbrv = model_atcf_name_list[index]
                if model == 'gfs' and model_atcf_abbrv != 'GFSO':
                    print("Using operational GFS...using ATCF name as GFSO "
                          +"to comply with MET")
                    model_atcf_abbrv = 'GFSO'
                # Create job file
                job_filename = os.path.join(DATA, RUN,
                                            'metplus_job_scripts',
                                            'job'+str(njob))
                job_file = open(job_filename, 'w')
                set_job_common_env(job_file)
                job_file.write('export START_DATE="'+storm_start_date+'"\n')
                job_file.write('export END_DATE="'+storm_end_date+'"\n')
                job_file.write('export model="'+model+'"\n')
                job_file.write('export model_atcf_abbrv="'+model_atcf_abbrv
                               +'"\n')
                job_file.write('export storm="'+storm+'"\n')
                job_file.write('export basin="'+basin+'"\n')
                job_file.write('export year="'+year+'"\n')
                job_file.write('export name="'+name+'"\n')
                job_file.write('export storm_id="'+storm_id.upper()+'"\n')
                job_file.write('export storm_num="'+storm_id[2:4]+'"\n')
                job_file.write('\n')
                metplus_conf_list = [
                    os.path.join(metplus_version_conf_dir, 'tropcyc',
                                 'make_met_data',
                                 'storm.conf')
                ]
                for metplus_conf in metplus_conf_list:
                    job_file.write(
                        master_metplus+' '
                        +'-c '+metplus_machine_conf+' '
                        +'-c '+metplus_conf+'\n'
                    )
                job_file.close()
        else:
            njob+=1
            # Set up information for environment variables
            fhr_list = os.environ['tropcyc_fhr_list'].replace(' ','')
            init_hour_list = ','.join(
                os.environ['tropcyc_fcyc_list'].split(' ')
            )
            valid_hour_list = ','.join(
                os.environ['tropcyc_vhr_list'].split(' ')
            )
            # Create job file
            job_filename = os.path.join(DATA, RUN,
                                        'metplus_job_scripts',
                                        'job'+str(njob))
            job_file = open(job_filename, 'w')
            set_job_common_env(job_file)
            job_file.write('export START_DATE="'+storm_start_date+'"\n')
            job_file.write('export END_DATE="'+storm_end_date+'"\n')
            job_file.write('export storm="'+storm+'"\n')
            job_file.write('export basin="'+basin+'"\n')
            job_file.write('export year="'+year+'"\n')
            job_file.write('export name="'+name+'"\n')
            job_file.write('export storm_id="'+storm_id.upper()+'"\n')
            job_file.write('export storm_num="'+storm_id[2:4]+'"\n')
            job_file.write('export fhr_list="'+fhr_list+'"\n')
            job_file.write('export init_hour_list="'+init_hour_list+'"\n')
            job_file.write('export valid_hour_list="'+valid_hour_list+'"\n')
            job_file.write('export model_atcf_name_list="'
                           +', '.join(model_atcf_name_list)+'"\n')
            job_file.write('\n')
            metplus_conf_list = [
                os.path.join(metplus_version_conf_dir, 'tropcyc',
                            'gather',
                            'storm.conf')
            ]
            for metplus_conf in metplus_conf_list:
                job_file.write(
                    master_metplus+' '
                    +'-c '+metplus_machine_conf+' '
                    +'-c '+metplus_conf+'\n'
                )
            job_file.write('python '
                           +os.path.join(USHverif_global, 'plotting_scripts',
                                         'plot_tc_errors_lead_mean.py')+' '
                           +storm+'\n')
            job_file.write('nimgs=$(ls '
                           +os.path.join(DATA, RUN, 'metplus_output','plot',
                                         storm, 'imgs', '*')
                           +' |wc -l)\n')
            job_file.write('if [ $nimgs -ne 0 ]; then\n')
            job_file.write(
                '    ln -sf '
                +os.path.join(DATA, RUN, 'metplus_output',
                              'plot', storm, 'imgs', '*')+' '
                +os.path.join(DATA, RUN, 'metplus_output',
                              'images/.')+'\n'
            )
            job_file.write('fi')
            job_file.close()
    if METplus_tropcyc_process == 'tc_stat':
        for basin in basin_list:
            njob+=1
            basin = basin.split('_')[0]
            # Set up information for environment variables
            fhr_list = os.environ['tropcyc_fhr_list'].replace(' ','')
            init_hour_list = ','.join(
                os.environ['tropcyc_fcyc_list'].split(' ')
            )
            valid_hour_list = ','.join(
                os.environ['tropcyc_vhr_list'].split(' ')
            )
            # Create job file
            job_filename = os.path.join(DATA, RUN,
                                        'metplus_job_scripts',
                                        'job'+str(njob))
            job_file = open(job_filename, 'w')
            set_job_common_env(job_file)
            job_file.write('export basin="'+basin+'"\n')
            job_file.write('export fhr_list="'+fhr_list+'"\n')
            job_file.write('export init_hour_list="'+init_hour_list+'"\n')
            job_file.write('export valid_hour_list="'+valid_hour_list+'"\n')
            job_file.write('export model_atcf_name_list="'
                           +', '.join(model_atcf_name_list)+'"\n')
            job_file.write('\n')
            metplus_conf_list = [
                os.path.join(metplus_version_conf_dir, 'tropcyc',
                            'gather',
                            'basin.conf')
            ]
            for metplus_conf in metplus_conf_list:
                job_file.write(
                    master_metplus+' '
                    +'-c '+metplus_machine_conf+' '
                    +'-c '+metplus_conf+'\n'
                )
            job_file.write('python '
                           +os.path.join(USHverif_global, 'plotting_scripts',
                                         'plot_tc_errors_lead_mean.py')+' '
                           +basin+'\n')
            job_file.write('nimgs=$(ls '
                           +os.path.join(DATA, RUN, 'metplus_output','plot',
                                         basin, 'imgs', '*')
                           +' |wc -l)\n')
            job_file.write('if [ $nimgs -ne 0 ]; then\n')
            job_file.write(
                '    ln -sf '
                +os.path.join(DATA, RUN, 'metplus_output',
                              'plot', basin, 'imgs', '*')+' '
                +os.path.join(DATA, RUN, 'metplus_output',
                              'images/.')+'\n'
            )
            job_file.write('fi')
            job_file.close()

def create_job_script_maps2d(sdate, edate, model_list, type_list):
    """! Writes out job cards based on requested verification
         for maps2d verification

         Args:
             sdate      - datetime object of the verification start
                          date
             edate      - datetime object of the verification end
                          date
             model_list - list of strings of model names
             type_list  - list of strings of the types of the
                          verification use case

         Returns:
    """
    model_plot_name_list = (
        os.environ['maps2d_model_plot_name_list'].split(' ')
    )
    if len(model_plot_name_list) != len(model_list):
        print("model_list and maps2_model_plot_name_list "
              +"not of equal length")
        exit(1)
    make_met_data_by = os.environ['maps2d_make_met_data_by']
    plot_by = make_met_data_by
    hr_beg = os.environ['maps2d_hr_beg']
    hr_end = os.environ['maps2d_hr_end']
    hr_inc = os.environ['maps2d_hr_inc']
    forecast_to_plot_list = (
        os.environ['maps2d_forecast_to_plot_list'].split(' ')
    )
    forecast_anl_diff = os.environ['maps2d_forecast_anl_diff']
    anl_name = os.environ['maps2d_anl_name']
    regrid_to_grid = os.environ['map2d_regrid_to_grid']
    latlon_area = os.environ['maps2d_latlon_area']
    model_info = {}
    nmodels = int(len(model_list))
    if forecast_anl_diff == 'YES':
        nmodels = nmodels * 2
    if nmodels > 8:
        if forecast_anl_diff == 'YES':
            print("Too many models listed, including analysis "
                  +"(len(model_list)*2). Current maximum is 8.")
        else:
            print("Too many models listed in model_list. "
                  +"Current maximum is 8.")
        exit(1)
    for model in model_list:
        index = model_list.index(model)
        model_num = index + 1
        model_info['model'+str(model_num)] = model
        model_info['model'+str(model_num)+'_plot_name'] = (
            model_plot_name_list[index]
        )
    njob = 0
    for type in type_list:
        extra_env_info = {}
        extra_env_info['verif_case_type'] = type
        if type == 'model2model':
            extra_env_info['forecast_anl_diff'] = forecast_anl_diff
            # Save extended levels
            #['1000hPa', '850hPa', '700hPa', '500hPa', '200hPa',
            # '100hPa', '70hPa', '50hPa', '10hPa', '5hPa', '1hPa',
            # '0.5hPa', '0.1hPa', '0.05hPa', '0.01hPa']
            vars_preslevs_dict = {
                'TMP': ['1000hPa', '850hPa', '700hPa', '500hPa', '200hPa',
                        '100hPa', '70hPa', '50hPa', '10hPa', '5hPa', '1hPa'],
                'HGT': ['1000hPa', '850hPa', '700hPa', '500hPa', '200hPa', 
                        '100hPa', '70hPa', '50hPa', '10hPa', '5hPa', '1hPa'],
                'UGRD': ['1000hPa', '850hPa', '700hPa', '500hPa', '200hPa', 
                         '100hPa', '70hPa', '50hPa', '10hPa', '5hPa', '1hPa'],
                'VGRD': ['1000hPa', '850hPa', '700hPa', '500hPa', '200hPa', 
                         '100hPa', '70hPa', '50hPa', '10hPa', '5hPa', '1hPa'],
                'VVEL': ['1000hPa', '850hPa', '700hPa', '500hPa', '200hPa', 
                         '100hPa', '70hPa', '50hPa', '10hPa', '5hPa', '1hPa'],
                'RH': ['1000hPa', '850hPa', '700hPa', '500hPa', '200hPa', 
                       '100hPa', '70hPa', '50hPa', '10hPa', '5hPa', '1hPa'],
                'CLWMR': ['1000hPa', '850hPa', '700hPa', '500hPa', '200hPa', 
                          '100hPa', '70hPa', '50hPa', '10hPa', '5hPa', '1hPa'],
                'O3MR': ['1000hPa', '850hPa', '700hPa', '500hPa', '200hPa', 
                         '100hPa', '70hPa', '50hPa', '10hPa', '5hPa', '1hPa']
            }
            vars_sfc_dict = {
                'TMP': ['2mAGL', 'sfc'],
                'TMAX': ['2mAGL'],
                'TMIN': ['2mAGL'],
                'DPT': ['2mAGL'],
                'RH': ['2mAGL'],
                'SPFH': ['2mAGL'],
                'UGRD': ['10mAGL'],
                'VGRD': ['10mAGL'],
                'GUST': ['sfc'],
                'PRES': ['sfc'],
                'MSLET': ['msl'],
                'PRMSL': ['msl'],
                'LFTX': ['sfc'],
                '4LFTX': ['sfc'],
                'VIS': ['sfc'],
                'HGT': ['sfc'],
                'HINDEX': ['sfc'],
                'ICEC': ['sfc'],
                'U-GWD': ['sfc'],
                'V-GWD': ['sfc'],
                'UFLX': ['sfc'],
                'VFLX': ['sfc'],
                'ALBDO': ['sfc'],
                'LHTFL': ['sfc'],
                'SHTFL': ['sfc'],
                'GFLUX': ['sfc']
            }
            vars_totcol_dict = {
                'PWAT': ['column'],
                'CWAT': ['column'],
                'TOZNE': ['column'],
                'CWORK': ['column'],
                'RH': ['column']
            }
            vars_precip_dict = {
                'APCP': ['sfc_bucketaccum6hr'],
                'ACPCP': ['sfc_bucketaccum6hr'],
                'SNOD': ['sfc'],
                'WEASD': ['sfc'],
                'WATR': ['sfc']
            }
            vars_cloudsrad_dict = {
                'DLWRF': ['sfc'],
                'ULWRF': ['sfc', 'toa'],
                'DSWRF': ['sfc'],
                'USWRF': ['sfc', 'toa'],
                'ALBDO': ['sfc'],
                'SUNSD': ['sfc'],
                'TCDC': ['column', 'pbl', 'low',
                         'mid', 'high', 'convective'],
                'PRES': ['lowcloudbase', 'midcloudbase',
                         'highcloudbase', 'convectivecloudbase',
                         'lowcloudtop', 'midcloudtop',
                         'highcloudtop', 'convectivecloudtop'],
                'TMP': ['lowcloudtop', 'midcloudtop',
                        'highcloudtop'],
                'CWAT': ['column'],
                'CWORK': ['column'],
            }
            vars_capecin_dict = {
                'CAPE': ['sfc', '255-0hPaAGL', '180-0hPaAGL'],
                'CIN': ['sfc', '255-0hPaAGL', '180-0hPaAGL']
            }
            vars_pbl_dict = {
                'HPBL': ['sfc'],
                'VRATE': ['pbl'],
                'UGRD': ['pbl'],
                'VGRD': ['pbl'],
                'TCDC': ['pbl']
            }
            vars_groundsoil_dict = {
                'TMP': ['sfc'],
                'TSOIL': ['0-10cmUGL', '10-40cmUGL',
                          '40-100cmUGL', '100-200cmUGL'],
                'SOILW': ['0-10cmUGL', '10-40cmUGL',
                          '40-100cmUGL', '100-200cmUGL'],
                'LHTFL': ['sfc'],
                'SHTFL': ['sfc'],
                'GFLUX': ['sfc'],
                'WATR': ['sfc'],
                'PEVPR': ['sfc'],
                'FLDCP': ['sfc'],
                'WILT': ['sfc'],
            }
            vars_tropopause_dict = {
                'HGT': ['tropopause'],
                'TMP': ['tropopause'],
                'PRES': ['tropopause'],
                'UGRD': ['tropopause'],
                'VGRD': ['tropopause'],
                'VWSH': ['tropopause'],
                'ICAHT': ['tropopause'],
            }
            vars_sigma0995_dict = {
                'TMP': ['0.995sigma'],
                'POT': ['0.995sigma'],
                'UGRD': ['0.995sigma'],
                'VGRD': ['0.995sigma'],
                'VVEL': ['0.995sigma'],
                'RH': ['0.995sigma']
            }
            vars_maxwindlev_dict = {
                'TMP': ['maxwindlev'],
                'PRES': ['maxwindlev'],
                'HGT': ['maxwindlev'],
                'UGRD': ['maxwindlev'],
                'VGRD': ['maxwindlev'],
                'ICAHT': ['maxwindlev']
            }     
            vars_highesttropfrzlev_dict = {
                'HGT': ['highesttropfrzlev'],
                'RH': ['highesttropfrzlev']
            }
            all_vars_dict = {
                'preslevs': vars_preslevs_dict,
                'sfc': vars_sfc_dict,
                'totcol': vars_totcol_dict,
                'precip': vars_precip_dict,
                'cloudsrad': vars_cloudsrad_dict,
                'capecin': vars_capecin_dict,
                'pbl': vars_pbl_dict,
                'groundsoil': vars_groundsoil_dict,
                'tropopause': vars_tropopause_dict,
                'sigma0995': vars_sigma0995_dict,
                'maxwindlev': vars_maxwindlev_dict,
                'highesttropfrzlev': vars_highesttropfrzlev_dict
            }
        elif type == 'model2obs':
            extra_env_info = {}
            extra_env_info['forecast_anl_diff'] = 'NO'
            vars_cloudsrad_dict = {
                'DLWRF': ['sfc'],
                'ULWRF': ['sfc', 'toa'],
                'DSWRF': ['sfc'],
                'USWRF': ['sfc', 'toa'],
                'ALBDO': ['sfc'],
                'TCDC': ['column', 'low', 'mid', 'high'],
            }
            vars_sfc_dict = {
                'TMP': ['2m agl']
            }
            vars_precip_dict = {
                'APCP': ['sfc_acumm6hr']
            }
            vars_totcol_dict = {
                'PWAT': ['column'],
                'CWAT': ['column']
            }
            all_vars_dict = {
                'cloudsrad': vars_cloudsrad_dict,
                'sfc': vars_sfc_dict,
                'precip': vars_precip_dict,
                'totcol': vars_totcol_dict,
            }
        for vars_dict in list(all_vars_dict.keys()):
            # Set up image directories
            var_group_name_plot_out_dir = os.path.join(
                DATA, RUN, 'metplus_output',
                'plot_by_'+plot_by, type, vars_dict, 'imgs'
            )
            if not os.path.exists(var_group_name_plot_out_dir):
                os.makedirs(var_group_name_plot_out_dir)
            for var_name, var_levels in all_vars_dict[vars_dict].items():
                # Set maps2d_type obtypes
                for model in model_list:
                    index = model_list.index(model)
                    model_num = index + 1
                    # Set up output directories
                    var_group_name_make_met_out_dir = os.path.join(
                        DATA, RUN, 'metplus_output',
                        'make_met_data_by_'+make_met_data_by,
                        'series_analysis', type, vars_dict, model
                    )
                    if not os.path.exists(var_group_name_make_met_out_dir):
                        os.makedirs(var_group_name_make_met_out_dir)
                    if type == 'model2model':
                        if forecast_anl_diff == 'YES':
                            if anl_name == 'self_anl':
                                obtype = model+'_anl'
                            elif anl_name == 'self_f00':
                                obtype = model+'_f00'
                            elif anl_name == 'gfs_anl':
                                obtype = 'gfs_anl'
                            elif anl_name == 'gfs_f00':
                                obtype = 'gfs_f00'
                        else:
                            obtype = model
                    elif type == 'model2obs':
                        if vars_dict == 'cloudsrad':
                            obtype = 'ceres'
                        elif vars_dict == 'sfc':
                            obtype = 'ghcn_cams'
                        elif vars_dict == 'precip':
                            obtype = 'gpcp'
                        elif vars_dict == 'totcol':
                            obtype = 'ceres'
                    model_info['model'+str(model_num)+'_obtype'] = obtype
                for forecast_to_plot in forecast_to_plot_list:
                    njob+=1
                    # Create job file
                    job_filename = os.path.join(DATA, RUN,
                                                'metplus_job_scripts',
                                                'job'+str(njob))
                    job_file = open(job_filename, 'w')
                    set_job_common_env(job_file)
                    job_file.write('export START_DATE="'
                                   +sdate.strftime('%Y%m%d')+'"\n')
                    job_file.write('export END_DATE="'
                                   +edate.strftime('%Y%m%d')+'"\n')
                    job_file.write('export job_num_id="'+str(njob)+'"\n')
                    job_file.write('export make_met_data_by="'
                                   +make_met_data_by+'"\n')
                    job_file.write('export plot_by="'+plot_by+'"\n')
                    job_file.write('export forecast_to_plot="'
                                   +forecast_to_plot+'"\n')
                    job_file.write('export hr_beg="'+hr_beg+'"\n')
                    job_file.write('export hr_end="'+hr_end+'"\n')
                    job_file.write('export hr_inc="'+hr_inc+'"\n')
                    job_file.write('export regrid_to_grid="'
                                   +regrid_to_grid+'"\n')
                    job_file.write('export latlon_area="'
                                   +latlon_area+'"\n')
                    job_file.write('export var_group_name="'
                                   +vars_dict+'"\n')
                    job_file.write('export var_name="'+var_name+'"\n')
                    job_file.write('export var_levels="'
                                   +' '.join(var_levels).replace(' ', ', ')
                                   +'"\n')
                    for name, value in model_info.items():
                        job_file.write('export '+name+'="'+value+'"\n')
                    for name, value in extra_env_info.items():
                        job_file.write('export '+name+'="'+value+'"\n')
                    job_file.write('\n')
                    job_file.write(
                        'python '
                        +os.path.join(
                            USHverif_global,
                           'create_MET_series_analysis_jobs_for_maps2d.py\n'
                        )
                    )
                    for model in model_list:
                        job_file.write(os.path.join(DATA, RUN,
                                                    'metplus_job_scripts',
                                                    'series_analysis_'
                                                    +'job'+str(njob)+'_'
                                                    +model+'.sh')+'\n')
                    # Need to switch python modules to use Basemap
                    if machine == 'WCOSS_C' or machine == 'WCOSS_DELL_P3':
                        job_file.write(
                            'module switch python/3.6.3\n'
                        )
                        job_file.write(
                            'export py_map_pckg="cartopy"\n'
                        )
                    else:
                        job_file.write(
                            'export py_map_pckg="basemap"\n'
                        )
                    job_file.write(
                        'python '+os.path.join(USHverif_global,
                                               'plotting_scripts',
                                               'plot_maps2d_lat_lon_errors'
                                               +'.py\n')
                    )
                    if vars_dict == 'preslevs':
                        job_file.write(
                            'python '
                            +os.path.join(USHverif_global,
                                          'plotting_scripts',
                                          'plot_maps2d_zonal_mean_errors'
                                          +'.py\n')
                        )
                    job_file.write('nimgs=$(ls '
                           +os.path.join(DATA, RUN, 'metplus_output',
                                         'plot_by_'+plot_by, type, vars_dict,
                                         'imgs', '*')
                           +' |wc -l)\n')
                    job_file.write('if [ $nimgs -ne 0 ]; then\n')
                    job_file.write(
                         '    ln -sf '
                         +os.path.join(DATA, RUN, 'metplus_output',
                                       'plot_by_'+plot_by, type, vars_dict,
                                       'imgs', '*')+' '
                         +os.path.join(DATA, RUN, 'metplus_output',
                                       'images/.')+'\n'
                    )
                    job_file.write('fi')
                    job_file.close()

# Run job creation function
if RUN in ['grid2grid_step1', 'grid2obs_step1', 'precip_step1']:
    create_job_script_step1(sdate, edate, model_list, type_list, case)   
elif RUN in ['grid2grid_step2', 'grid2obs_step2', 'precip_step2']:
    create_job_script_step2(sdate, edate, model_list, type_list, case)
elif RUN in ['tropcyc']:
    import get_tc_info
    config_storm_list = os.environ['tropcyc_storm_list'].split(' ')
    # Check storm_list to see if all storms for basin and year
    # requested
    storm_list = []
    for storm in config_storm_list:
        basin = storm.split('_')[0]
        year = storm.split('_')[1]
        name = storm.split('_')[2]
        if name == 'ALLNAMED':
            all_storms_in_basin_year_list = (
                get_tc_info.get_all_tc_storms_basin_year(basin, year)
            )
            for byn in all_storms_in_basin_year_list:
                storm_list.append(byn)
        else:
            storm_list.append(storm)
    create_job_script_tropcyc(model_list, storm_list)
elif RUN in ['maps2d']:
    create_job_script_maps2d(sdate, edate, model_list, type_list)

# If running MPMD, create POE scripts
if MPMD == 'YES':
    job_files = glob.glob(
        os.path.join(DATA, RUN, 'metplus_job_scripts', 'job*')
    )
    njob_files = len(job_files)
    if RUN == 'tropcyc':
        METplus_tropcyc_process = os.environ['METplus_tropcyc_process']
        if METplus_tropcyc_process == 'tc_pairs':
            njob, iproc = 1, 0
            node = 1
        else:
            njob_from_tc_pairs = int(os.environ['njob_from_tc_pairs'])
            npoe_from_tc_pairs = int(os.environ['npoe_from_tc_pairs'])
            njob = njob_from_tc_pairs + 1
            iproc = 0
            node = npoe_from_tc_pairs + 1
    else:
        njob, iproc = 1, 0
        node = 1
    while njob <= njob_files:
        job = 'job'+str(njob)
        if machine == 'HERA':
            if iproc >= nproc:
                poe_file.close()
                iproc = 0
                node+=1
        poe_filename = os.path.join(DATA, RUN, 'metplus_job_scripts',
                                        'poe_jobs'+str(node))
        if iproc == 0:
            poe_file = open(poe_filename, 'w')
        iproc+=1
        if machine == 'HERA':
            poe_file.write(
                str(iproc-1)+' '
                +os.path.join(DATA, RUN, 'metplus_job_scripts', job)+'\n'
            )
        else:
            poe_file.write(
                os.path.join(DATA, RUN, 'metplus_job_scripts', job)+'\n'
            )
        njob+=1
    poe_file.close()
    # If at final record and have not reached the
    # final processor then write echo's to
    # poe script for remaining processors
    poe_file = open(poe_filename, 'a')
    iproc+=1
    while iproc <= nproc:
        if machine == 'HERA':
            poe_file.write(
                str(iproc-1)+' /bin/echo '+str(iproc)+'\n'
            )
        else:
            poe_file.write(
                '/bin/echo '+str(iproc)+'\n'
            )
        iproc+=1
poe_file.close()

print("END: "+os.path.basename(__file__))
