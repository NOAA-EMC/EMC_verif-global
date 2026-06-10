'''
Program Name: step2_satellite_create_job_scripts.py
Contact(s): Ho-Chun Huang (ho-chun.huang@noaa.gov)
Abstract: This script is run by exsatellite_step2.sh in scripts/.
          This creates multiple independent job cards. These
          jobs contain all the necessary environment variables
          and commands needed to run the specific
          plot verification use case and types (each job
          could be run independently on the command line).
'''

import sys
import os
import datetime
import glob
import itertools
import numpy as np
import subprocess
import copy
import verif_global_util as vfg_util

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
DATA = os.environ['DATA']
RUN = os.environ['RUN']
RUN_CASE = (RUN.split('_')[0])
JOB_GROUP = os.environ['JOB_GROUP']
machine = os.environ['machine']
MPMD = os.environ['MPMD']
nproc = int(os.environ['nproc'])
start_date = os.environ['start_date']
end_date = os.environ['end_date']
plot_by = os.environ['plot_by']
RUN_abbrev = os.environ['RUN_abbrev']
case_type_list = os.environ[RUN_abbrev+'_type_list'].split(' ')
met_ver = os.environ['MET_version']
MET_ROOT = os.environ['HOMEMET']

njobs = 0
JOB_GROUP_jobs_dir = os.path.join(DATA, RUN,
                                  'plot_job_scripts', JOB_GROUP)
vfg_util.make_dir(JOB_GROUP_jobs_dir)

# Set up base plotting information dictionary
base_plot_jobs_info_dict = {
    'ghrsst_ncei_avhrr_anl': {
        'SST': {'vx_masks': ['NH', 'SH', 'POLAR', 'ARCTIC', 'SEA_ICE',
                             'SEA_ICE_FREE', 'SEA_ICE_POLAR',
                             'SEA_ICE_FREE_POLAR'],
                'fcst_var_dict': {'name': 'TMP_Z0_mean',
                                  'levels': ['Z0'] },
                'obs_var_dict': {'name': 'analysed_sst',
                                 'levels': ['0,*,*'] }},
        'ICEC': {'vx_masks': ['NH', 'SH', 'POLAR', 'ARCTIC', 'SEA_ICE',
                              'SEA_ICE_FREE', 'SEA_ICE_POLAR',
                              'SEA_ICE_FREE_POLAR'],
                 'fcst_var_dict': {'name': 'ICEC_Z0_mean',
                                   'levels': ['Z0'] },
                 'obs_var_dict': {'name': 'sea_ice_fraction',
                                  'levels': ['0,*,*'] }}
    },
    'ghrsst_ospo_geopolar_anl': {
        'SST': {'vx_masks': ['NH', 'SH', 'POLAR', 'ARCTIC', 'SEA_ICE',
                             'SEA_ICE_FREE', 'SEA_ICE_POLAR',
                             'SEA_ICE_FREE_POLAR'],
                'fcst_var_dict': {'name': 'TMP_Z0_mean',
                                  'levels': ['Z0'] },
                'obs_var_dict': {'name': 'analysed_sst',
                                 'levels': ['0,*,*'] }},
        'ICEC': {'vx_masks': ['NH', 'SH', 'POLAR', 'ARCTIC', 'SEA_ICE',
                             'SEA_ICE_FREE', 'SEA_ICE_POLAR',
                             'SEA_ICE_FREE_POLAR'],
                'fcst_var_dict': {'name': 'ICEC_Z0_mean',
                                  'levels': ['Z0'] },
                'obs_var_dict': {'name': 'sea_ice_fraction',
                                 'levels': ['0,*,*'] }}
    }
}

# condense_stats jobs
condense_stats_jobs_dict = copy.deepcopy(base_plot_jobs_info_dict)
# ghrsst_ncei_avhrr_anl
for avhrr_job in list(condense_stats_jobs_dict['ghrsst_ncei_avhrr_anl'].keys()):
    condense_stats_jobs_dict['ghrsst_ncei_avhrr_anl'][avhrr_job]['line_types'] = (
        ['SL1L2']
    )
# ghrsst_ospo_geopolar_anl
for ospo_job in list(condense_stats_jobs_dict['ghrsst_ospo_geopolar_anl'].keys()):
    condense_stats_jobs_dict['ghrsst_ospo_geopolar_anl'][ospo_job]['line_types'] = (
        ['SL1L2']
    )
if JOB_GROUP == 'condense_stats':
    JOB_GROUP_dict = condense_stats_jobs_dict

# filter_stats jobs
filter_stats_jobs_dict = copy.deepcopy(condense_stats_jobs_dict)
# ghrsst_ncei_avhrr_anl
for avhrr_job in list(filter_stats_jobs_dict['ghrsst_ncei_avhrr_anl'].keys()):
    if avhrr_job == "SST":
        (filter_stats_jobs_dict['ghrsst_ncei_avhrr_anl'][avhrr_job]\
         ['fcst_var_dict']['threshs']) = ['NA']
        (filter_stats_jobs_dict['ghrsst_ncei_avhrr_anl'][avhrr_job]\
         ['obs_var_dict']['threshs']) = ['NA']
    elif ospo_job == "ICEC":
        (filter_stats_jobs_dict['ghrsst_ncei_avhrr_anl'][avhrr_job]\
         ['fcst_var_dict']['threshs']) = ['>=0.15||']
        (filter_stats_jobs_dict['ghrsst_ncei_avhrr_anl'][avhrr_job]\
         ['obs_var_dict']['threshs']) = ['>=0.15']
    filter_stats_jobs_dict['ghrsst_ncei_avhrr_anl'][avhrr_job]['interps'] = ['NEAREST/1']
# ghrsst_ospo_geopolar_anl
for ospo_job in list(filter_stats_jobs_dict['ghrsst_ospo_geopolar_anl'].keys()):
    if ospo_job == "SST":
        (filter_stats_jobs_dict['ghrsst_ospo_geopolar_anl'][ospo_job]\
         ['fcst_var_dict']['threshs']) = ['NA']
        (filter_stats_jobs_dict['ghrsst_ospo_geopolar_anl'][ospo_job]\
         ['obs_var_dict']['threshs']) = ['NA']
    elif ospo_job == "ICEC":
        (filter_stats_jobs_dict['ghrsst_ospo_geopolar_anl'][ospo_job]\
         ['fcst_var_dict']['threshs']) = ['>=0.15||']
        (filter_stats_jobs_dict['ghrsst_ospo_geopolar_anl'][ospo_job]\
         ['obs_var_dict']['threshs']) = ['>=0.15']
    filter_stats_jobs_dict['ghrsst_ospo_geopolar_anl'][ospo_job]['interps'] = ['NEAREST/1']
if JOB_GROUP == 'filter_stats':
    JOB_GROUP_dict = filter_stats_jobs_dict

# make_plots jobs
make_plots_jobs_dict = copy.deepcopy(filter_stats_jobs_dict)
# ghrsst_ncei_avhrr_anl
for avhrr_job in list(make_plots_jobs_dict['ghrsst_ncei_avhrr_anl'].keys()):
    del make_plots_jobs_dict['ghrsst_ncei_avhrr_anl'][avhrr_job]['line_types']
    make_plots_jobs_dict['ghrsst_ncei_avhrr_anl'][avhrr_job]['line_type_stats'] = [
        'SL1L2/FBAR_OBAR', 'SL1L2/ME', 'SL1L2/RMSE' 
    ]
    make_plots_jobs_dict['ghrsst_ncei_avhrr_anl'][avhrr_job]['plots'] = [
        'time_series', 'lead_average'
    ]
# pres
# ghrsst_ospo_geopolar_anl
for ospo_job in list(make_plots_jobs_dict['ghrsst_ospo_geopolar_anl'].keys()):
    del make_plots_jobs_dict['ghrsst_ospo_geopolar_anl'][ospo_job]['line_types']
    make_plots_jobs_dict['ghrsst_ospo_geopolar_anl'][ospo_job]['line_type_stats'] = [
        'SL1L2/FBAR_OBAR', 'SL1L2/ME', 'SL1L2/RMSE' 
    ]
    make_plots_jobs_dict['ghrsst_ospo_geopolar_anl'][ospo_job]['plots'] = [
        'time_series', 'lead_average'
    ]
if JOB_GROUP == 'make_plots':
    JOB_GROUP_dict = make_plots_jobs_dict

# Set up model environment variables in dictionary
model_list = os.environ['model_list'].split(' ')
for case_type in case_type_list:
    print("----> Making job scripts for "+RUN+" "
          +case_type+" for job group "+JOB_GROUP)
    RUN_abbrev_type = RUN_abbrev+'_'+case_type
    model_plot_name_list = (
        os.environ[RUN_abbrev+'_model_plot_name_list'].split(' ')
    )
    case_type_plot_jobs_dict = JOB_GROUP_dict[case_type]
    for case_type_job in list(case_type_plot_jobs_dict.keys()):
        # Initialize job environment dictionary
        job_env_dict = vfg_util.initialize_job_env_dict(
            case_type, JOB_GROUP,
            RUN_abbrev_type, case_type_job
        )
        job_env_dict['RUN_CASE'] = RUN_CASE
        job_env_dict['start_date'] = start_date
        job_env_dict['end_date'] = end_date
        job_env_dict['plot_by'] = plot_by
        case_type_env_list = ['grid', 'event_eq']
        for case_type_env in case_type_env_list:
            job_env_dict[case_type_env] = (
                os.environ[RUN_abbrev_type+'_'+case_type_env]
            )
        if JOB_GROUP in ['filter_stats', 'make_plots']:
            valid_hr_start = int(job_env_dict['valid_hr_start'])
            valid_hr_end = int(job_env_dict['valid_hr_end'])
            valid_hr_inc = int(job_env_dict['valid_hr_inc'])
            valid_hrs = list(range(valid_hr_start,
                                   valid_hr_end+valid_hr_inc,
                                   valid_hr_inc))
        try:
            obs_list = os.environ[RUN_abbrev_type + '_truth_name_list'].split(' ')
        except KeyError:
            obs_list = []

        for data_name in ['fcst', 'obs']:
            job_env_dict[data_name+'_var_name'] =  (
                case_type_plot_jobs_dict[case_type_job]\
                [data_name+'_var_dict']['name']
            )
        if JOB_GROUP == 'condense_stats':
            JOB_GROUP_case_type_job_product_loops = list(itertools.product(
                case_type_plot_jobs_dict[case_type_job]['line_types'],
                case_type_plot_jobs_dict[case_type_job]['fcst_var_dict']['levels'],
                case_type_plot_jobs_dict[case_type_job]['vx_masks'],
                model_list
            ))
        elif JOB_GROUP == 'filter_stats':
            JOB_GROUP_case_type_job_product_loops = list(itertools.product(
                case_type_plot_jobs_dict[case_type_job]['line_types'],
                case_type_plot_jobs_dict[case_type_job]['fcst_var_dict']['levels'],
                case_type_plot_jobs_dict[case_type_job]['vx_masks'],
                model_list,
                case_type_plot_jobs_dict[case_type_job]['fcst_var_dict']['threshs'],
                case_type_plot_jobs_dict[case_type_job]['interps'],
                valid_hrs
            ))
        elif JOB_GROUP == 'make_plots':
            JOB_GROUP_case_type_job_product_loops = list(itertools.product(
                case_type_plot_jobs_dict[case_type_job]['line_type_stats'],
                case_type_plot_jobs_dict[case_type_job]['plots'],
                case_type_plot_jobs_dict[case_type_job]['vx_masks'],
                case_type_plot_jobs_dict[case_type_job]['interps']
            ))
        for loop_info in JOB_GROUP_case_type_job_product_loops:
            if JOB_GROUP in ['condense_stats', 'filter_stats']:
                job_env_dict['fcst_var_level'] = loop_info[1]
                job_env_dict['obs_var_level'] = (
                    case_type_plot_jobs_dict[case_type_job]\
                    ['obs_var_dict']['levels'][
                        case_type_plot_jobs_dict[case_type_job]\
                        ['fcst_var_dict']['levels'].index(loop_info[1])
                    ]
                )
                job_env_dict['model_list'] = loop_info[3]
                job_env_dict['model_plot_name_list'] = (
                    model_plot_name_list[model_list.index(loop_info[3])]
                )
                if obs_list:
                    # If list is not empty, look up the index
                    job_env_dict['obs_list'] = obs_list[model_list.index(loop_info[3])]
                else:
                    # Otherwise set to a null string
                    job_env_dict['obs_list'] = ""
                job_env_dict['line_type'] = loop_info[0]
                job_env_dict['vx_mask'] = loop_info[2]
                if JOB_GROUP == 'filter_stats':
                    job_env_dict['fcst_var_thresh'] = loop_info[4]
                    job_env_dict['obs_var_thresh'] = (
                        case_type_plot_jobs_dict[case_type_job]\
                        ['obs_var_dict']['threshs'][
                            case_type_plot_jobs_dict[case_type_job]\
                            ['fcst_var_dict']['threshs'].index(loop_info[4])
                        ]
                    )
                    job_env_dict['interp_method'] = loop_info[5].split('/')[0]
                    job_env_dict['interp_points'] = loop_info[5].split('/')[1]
                # Set up output directories
                njobs+=1
                job_env_dict['job_id'] = 'job'+str(njobs)
                job_DATA_dir = os.path.join(DATA, RUN, 'plot_output',
                                            'plot_by_'+plot_by,
                                            JOB_GROUP, case_type)
                job_env_dict['job_DATA_dir'] = job_DATA_dir
                vfg_util.make_dir(job_env_dict['job_DATA_dir'])
                # Create job file
                job_file = os.path.join(JOB_GROUP_jobs_dir,
                                        'job'+str(njobs))
                print("Creating job script: "+job_file)
                job = open(job_file, 'w')
                job.write('#!/bin/bash\n')
                job.write('set -x\n')
                job.write('\n')
                # Write environment variables
                for name, value in job_env_dict.items():
                    job.write('export '+name+'="'+value+'"\n')
                job.write('\n')
                job.write(
                    vfg_util.python_command(RUN_CASE, f"{RUN_CASE}_plots.py", [])
                    +'\n'
                )
                job.close()
            elif JOB_GROUP == 'make_plots':
                job_env_dict['model_list'] = ', '.join(model_list)
                job_env_dict['model_plot_name_list'] = (
                    ', '.join(model_plot_name_list)
                )
                if obs_list:
                    job_env_dict['obs_list'] = ', '.join(obs_list)
                else:
                    job_env_dict['obs_list'] = ""
                job_env_dict['line_type'] = loop_info[0].split('/')[0]
                job_env_dict['stat'] = loop_info[0].split('/')[1]
                job_env_dict['plot'] = loop_info[1]
                job_env_dict['vx_mask'] = loop_info[2]
                job_env_dict['interp_method'] = loop_info[3].split('/')[0]
                job_env_dict['interp_points'] = loop_info[3].split('/')[1]
                if job_env_dict['plot'] == 'valid_hour_average':
                    plot_valid_hrs_loop = [valid_hrs]
                else:
                    plot_valid_hrs_loop = valid_hrs
                if job_env_dict['plot'] in ['threshold_average',
                                            'performance_diagram']:
                    plot_fcst_threshs_loop = [
                        case_type_plot_jobs_dict[case_type_job]\
                        ['fcst_var_dict']['threshs']
                    ]

                else:
                    plot_fcst_threshs_loop = (
                        case_type_plot_jobs_dict[case_type_job]\
                        ['fcst_var_dict']['threshs']
                    )
                if job_env_dict['plot'] in ['stat_by_level', 'lead_by_level',
                                            'date_by_level']:
                    if case_type_plot_jobs_dict[case_type_job]\
                            ['fcst_var_dict']['name'] == 'O3MR':
                        plot_fcst_levels_loop = ['all']
                    else:
                        plot_fcst_levels_loop = ['all', 'trop', 'strat',
                                                 'ltrop', 'utrop']
                else:
                    plot_fcst_levels_loop = (
                        case_type_plot_jobs_dict[case_type_job]\
                        ['fcst_var_dict']['levels']
                    )
                for plot_loop_info in list(
                    itertools.product(plot_valid_hrs_loop,
                                      plot_fcst_threshs_loop,
                                      plot_fcst_levels_loop)
                ):
                    if job_env_dict['plot'] == 'valid_hour_average':
                        job_env_dict['valid_hr_start'] = str(
                            plot_loop_info[0][0]
                        ).zfill(2)
                        job_env_dict['valid_hr_end'] = str(
                            plot_loop_info[0][-1]
                        ).zfill(2)
                        job_env_dict['valid_hr_inc'] = str(valid_hr_inc)
                    else:
                        job_env_dict['valid_hr_start'] = str(
                            plot_loop_info[0]
                        ).zfill(2)
                        job_env_dict['valid_hr_end'] = str(
                            plot_loop_info[0]
                        ).zfill(2)
                        job_env_dict['valid_hr_inc'] = str(valid_hr_inc)
                    if job_env_dict['plot'] in ['threshold_average',
                                                'performance_diagram']:
                        job_env_dict['fcst_var_thresh_list'] = ', '.join(
                            plot_loop_info[1]
                        )
                        job_env_dict['obs_var_thresh_list'] = ', '.join(
                            case_type_plot_jobs_dict[case_type_job]\
                            ['obs_var_dict']['threshs']
                        )
                    else:
                        job_env_dict['fcst_var_thresh_list'] = (
                            plot_loop_info[1]
                        )
                        job_env_dict['obs_var_thresh_list'] = (
                            case_type_plot_jobs_dict[case_type_job]\
                            ['obs_var_dict']['threshs']\
                            [case_type_plot_jobs_dict[case_type_job]\
                             ['fcst_var_dict']['threshs']\
                             .index(plot_loop_info[1])]
                        )
                    if job_env_dict['plot'] in ['stat_by_level',
                                                'lead_by_level',
                                                'date_by_level']:
                        job_env_dict['vert_profile'] = plot_loop_info[2]
                        job_env_dict['fcst_var_level_list'] = ', '.join(
                            case_type_plot_jobs_dict[case_type_job]\
                            ['fcst_var_dict']['levels']
                        )
                        job_env_dict['obs_var_level_list'] = ', '.join(
                            case_type_plot_jobs_dict[case_type_job]\
                            ['obs_var_dict']['levels']
                        )
                    else:
                        job_env_dict['fcst_var_level_list'] = plot_loop_info[2]
                        job_env_dict['obs_var_level_list'] = (
                            case_type_plot_jobs_dict[case_type_job]\
                            ['obs_var_dict']['levels']\
                            [case_type_plot_jobs_dict[case_type_job]\
                             ['fcst_var_dict']['levels']\
                             .index(plot_loop_info[2])]
                        )
                    run_verif_global_plots = ['plots']
                    for run_verif_global_plot in run_verif_global_plots:
                        # Set up output directories
                        njobs+=1
                        job_env_dict['job_id'] = 'job'+str(njobs)
                        job_DATA_dir = os.path.join(DATA, RUN, 'plot_output',
                                                    'plot_by_'+plot_by,
                                                    JOB_GROUP, case_type)
                        job_env_dict['job_DATA_dir'] = job_DATA_dir
                        vfg_util.make_dir(job_env_dict['job_DATA_dir'])
                        # Create job file
                        job_file = os.path.join(JOB_GROUP_jobs_dir,
                                                'job'+str(njobs))
                        print("Creating job script: "+job_file)
                        job = open(job_file, 'w')
                        job.write('#!/bin/bash\n')
                        job.write('set -x\n')
                        job.write('\n')
                        # Write environment variables
                        job_env_dict['job_id'] = 'job'+str(njobs)
                        for name, value in job_env_dict.items():
                            job.write('export '+name+'="'+value+'"\n')
                        job.write('\n')
                        job.write(
                            vfg_util.python_command(RUN_CASE, f"{RUN_CASE}_plots.py", [])
                            +'\n'
                        )
                        job.close()

# If running MPMD, create POE scripts
if MPMD == 'YES':
    job_files = glob.glob(os.path.join(JOB_GROUP_jobs_dir, 'job*'))
    njob_files = len(job_files)
    if njob_files == 0:
        print("NOTE: No job files created in "+JOB_GROUP_jobs_dir)
    poe_files = glob.glob(os.path.join(JOB_GROUP_jobs_dir, 'poe*'))
    npoe_files = len(poe_files)
    if npoe_files > 0:
        for poe_file in poe_files:
            os.remove(poe_file)
    njob, iproc, node = 1, 0, 1
    while njob <= njob_files:
        job = 'job'+str(njob)
        if machine in ['HERA', 'ORION', 'HERCULES', 'GAEAC6']:
            if iproc >= nproc:
                poe_file.close()
                iproc = 0
                node+=1
        poe_filename = os.path.join(JOB_GROUP_jobs_dir,
                                    'poe_jobs'+str(node))
        if iproc == 0:
            poe_file = open(poe_filename, 'w')
        iproc+=1
        if machine in ['HERA', 'ORION', 'HERCULES', 'GAEAC6']:
            poe_file.write(
                str(iproc-1)+' '
                +os.path.join(JOB_GROUP_jobs_dir,job)+'\n'
            )
        else:
            poe_file.write(
                os.path.join(JOB_GROUP_jobs_dir, job)+'\n'
            )
        njob+=1
    poe_file.close()
    # If at final record and have not reached the
    # final processor then write echo's to
    # poe script for remaining processors
    poe_filename = os.path.join(JOB_GROUP_jobs_dir,
                                f"poe_jobs{str(node)}")
    poe_file = open(poe_filename, 'a')
    iproc+=1
    if machine == 'WCOSS2':
        nselect = subprocess.run(
            f"cat {poe_filename} | wc -l",
            shell=True, capture_output=True, encoding="utf8"
        ).stdout.replace('\n', '')
        nnp = int(nselect) * int(nproc)
    while iproc <= nproc:
        if machine in ['HERA', 'ORION', 'HERCULES', 'GAEAC6']:
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
