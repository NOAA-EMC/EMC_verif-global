'''
Program Name: step2_grid2grid_create_job_scripts.py
Contact(s): Shannon Shields
Abstract: This script is run by exgrid2grid_step2.sh in scripts/.
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
CI_METHOD = os.environ["g2g2_scorecard_ci_method"]
AVERAGE_METHOD = os.environ["g2g2_scorecard_average_method"]

njobs = 0
JOB_GROUP_jobs_dir = os.path.join(DATA, RUN,
                                  'plot_job_scripts', JOB_GROUP)
vfg_util.make_dir(JOB_GROUP_jobs_dir)

# Set up base plotting information dictionary
base_plot_jobs_info_dict = {
    'anom': {
        'HGT': {'vx_masks': ['G002', 'NHX', 'SHX', 'PNA', 'TRO'],
                'fcst_var_dict': {'name': 'HGT',
                                  'levels': ['P1000', 'P700',
                                             'P500', 'P250']},
                'obs_var_dict': {'name': 'HGT',
                                 'levels': ['P1000', 'P700',
                                            'P500', 'P250']}},
        'HGT_WV1_0-20': {'vx_masks': ['G002', 'NHX', 'SHX', 'PNA', 'TRO'],
                         'fcst_var_dict': {'name': 'HGT',
                                           'levels': ['P1000', 'P700',
                                                      'P500', 'P250']},
                         'obs_var_dict': {'name': 'HGT',
                                          'levels': ['P1000', 'P700',
                                                     'P500', 'P250']}},
        'HGT_WV1_0-3': {'vx_masks': ['G002', 'NHX', 'SHX', 'PNA', 'TRO'],
                        'fcst_var_dict': {'name': 'HGT',
                                          'levels': ['P1000', 'P700',
                                                     'P500', 'P250']},
                        'obs_var_dict': {'name': 'HGT',
                                         'levels': ['P1000', 'P700',
                                                    'P500', 'P250']}},
        'HGT_WV1_4-9': {'vx_masks': ['G002', 'NHX', 'SHX', 'PNA', 'TRO'],
                        'fcst_var_dict': {'name': 'HGT',
                                          'levels': ['P1000', 'P700',
                                                     'P500', 'P250']},
                        'obs_var_dict': {'name': 'HGT',
                                         'levels': ['P1000', 'P700',
                                                    'P500', 'P250']}},
        'HGT_WV1_10-20': {'vx_masks': ['G002', 'NHX', 'SHX', 'PNA', 'TRO'],
                          'fcst_var_dict': {'name': 'HGT',
                                            'levels': ['P1000', 'P700',
                                                       'P500', 'P250']},
                          'obs_var_dict': {'name': 'HGT',
                                           'levels': ['P1000', 'P700',
                                                      'P500', 'P250']}},
        'TMP': {'vx_masks': ['G002', 'NHX', 'SHX', 'PNA', 'TRO'],
                'fcst_var_dict': {'name': 'TMP',
                                  'levels': ['P850', 'P500', 'P250']},
                'obs_var_dict': {'name': 'TMP',
                                 'levels': ['P850', 'P500', 'P250']}},
        'UGRD': {'vx_masks': ['G002', 'NHX', 'SHX', 'PNA', 'TRO'],
                 'fcst_var_dict': {'name': 'UGRD',
                                   'levels': ['P850', 'P500', 'P250']},
                 'obs_var_dict': {'name': 'UGRD',
                                  'levels': ['P850', 'P500', 'P250']}},
        'VGRD': {'vx_masks': ['G002', 'NHX', 'SHX', 'PNA', 'TRO'],
                 'fcst_var_dict': {'name': 'VGRD',
                                   'levels': ['P850', 'P500', 'P250']},
                 'obs_var_dict': {'name': 'VGRD',
                                  'levels': ['P850', 'P500', 'P250']}},
        'PRMSL': {'vx_masks': ['G002', 'NHX', 'SHX', 'PNA', 'TRO'],
                  'fcst_var_dict': {'name': 'PRMSL',
                                    'levels': ['Z0']},
                  'obs_var_dict': {'name': 'PRMSL',
                                   'levels': ['Z0']}},
        'UGRD_VGRD': {'vx_masks': ['G002', 'NHX', 'SHX', 'PNA', 'TRO'],
                      'fcst_var_dict': {'name': 'UGRD_VGRD',
                                        'levels': ['P850', 'P500', 'P250']},
                      'obs_var_dict': {'name': 'UGRD_VGRD',
                                       'levels': ['P850', 'P500', 'P250']}},
    },
    'pres': {
        'HGT': {'vx_masks': ['G002', 'NHX', 'SHX', 'PNA', 'TRO'],
                'fcst_var_dict': {'name': 'HGT',
                                  'levels': ['P1000', 'P850', 'P700',
                                             'P500', 'P200', 'P100',
                                             'P50', 'P20', 'P10',
                                             'P5', 'P1']},
                'obs_var_dict': {'name': 'HGT',
                                 'levels': ['P1000', 'P850', 'P700',
                                            'P500', 'P200', 'P100',
                                            'P50', 'P20', 'P10',
                                            'P5', 'P1']}},
        'TMP': {'vx_masks': ['G002', 'NHX', 'SHX', 'PNA', 'TRO'],
                'fcst_var_dict': {'name': 'TMP',
                                  'levels': ['P1000', 'P850', 'P700',
                                             'P500', 'P200', 'P100',
                                             'P50', 'P20', 'P10',
                                             'P5', 'P1']},
                'obs_var_dict': {'name': 'TMP',
                                 'levels': ['P1000', 'P850', 'P700',
                                            'P500', 'P200', 'P100',
                                            'P50', 'P20', 'P10',
                                            'P5', 'P1']}},
        'UGRD': {'vx_masks': ['G002', 'NHX', 'SHX', 'PNA', 'TRO'],
                 'fcst_var_dict': {'name': 'UGRD',
                                   'levels': ['P1000', 'P850', 'P700',
                                              'P500', 'P200', 'P100',
                                              'P50', 'P20', 'P10',
                                              'P5', 'P1']},
                 'obs_var_dict': {'name': 'UGRD',
                                  'levels': ['P1000', 'P850', 'P700',
                                             'P500', 'P200', 'P100',
                                             'P50', 'P20', 'P10',
                                             'P5', 'P1']}},
        'VGRD': {'vx_masks': ['G002', 'NHX', 'SHX', 'PNA', 'TRO'],
                 'fcst_var_dict': {'name': 'VGRD',
                                   'levels': ['P1000', 'P850', 'P700',
                                              'P500', 'P200', 'P100',
                                              'P50', 'P20', 'P10',
                                              'P5', 'P1']},
                 'obs_var_dict': {'name': 'VGRD',
                                  'levels': ['P1000', 'P850', 'P700',
                                             'P500', 'P200', 'P100',
                                             'P50', 'P20', 'P10',
                                             'P5', 'P1']}},
        'O3MR': {'vx_masks': ['G002', 'NHX', 'SHX', 'PNA', 'TRO'],
                 'fcst_var_dict': {'name': 'O3MR',
                                   'levels': ['P100', 'P70', 'P50',
                                              'P30', 'P20', 'P10',
                                              'P5', 'P1']},
                 'obs_var_dict': {'name': 'O3MR',
                                  'levels': ['P100', 'P70', 'P50',
                                             'P30', 'P20', 'P10',
                                             'P5', 'P1']}},
        'UGRD_VGRD': {'vx_masks': ['G002', 'NHX', 'SHX', 'PNA', 'TRO'],
                      'fcst_var_dict': {'name': 'UGRD_VGRD',
                                        'levels': ['P1000', 'P850', 'P700',
                                                   'P500', 'P200', 'P100',
                                                   'P50', 'P20', 'P10',
                                                   'P5', 'P1']},
                      'obs_var_dict': {'name': 'UGRD_VGRD',
                                       'levels': ['P1000', 'P850', 'P700',
                                                  'P500', 'P200', 'P100',
                                                  'P50', 'P20', 'P10',
                                                  'P5', 'P1']}},
    },
    'sfc': {
        'TMP2m': {'vx_masks': ['G002', 'NHX', 'SHX', 'N60', 'S60', 'TRO', 'NPO',
                               'SPO', 'NAO', 'SAO', 'CONUS'],
                  'fcst_var_dict': {'name': 'TMP',
                                    'levels': ['Z2']},
                  'obs_var_dict': {'name': 'TMP',
                                   'levels': ['Z2']}},
        'TMPsfc': {'vx_masks': ['G002', 'NHX', 'SHX', 'N60', 'S60', 'TRO', 'NPO',
                                'SPO', 'NAO', 'SAO', 'CONUS'],
                   'fcst_var_dict': {'name': 'TMP',
                                     'levels': ['Z0']},
                   'obs_var_dict': {'name': 'TMP',
                                    'levels': ['Z0']}},
        'TMPtrops': {'vx_masks': ['G002', 'NHX', 'SHX', 'N60', 'S60', 'TRO', 'NPO',
                                  'SPO', 'NAO', 'SAO', 'CONUS'],
                     'fcst_var_dict': {'name': 'TMP',
                                       'levels': ['L0']},
                     'obs_var_dict': {'name': 'TMP',
                                      'levels': ['L0']}},
        'RH2m': {'vx_masks': ['G002', 'NHX', 'SHX', 'N60', 'S60', 'TRO', 'NPO',
                              'SPO', 'NAO', 'SAO', 'CONUS'],
                 'fcst_var_dict': {'name': 'RH',
                                   'levels': ['Z2']},
                 'obs_var_dict': {'name': 'RH',
                                  'levels': ['Z2']}},
        'SPFH2m': {'vx_masks': ['G002', 'NHX', 'SHX', 'N60', 'S60', 'TRO', 'NPO',
                                'SPO', 'NAO', 'SAO', 'CONUS'],
                   'fcst_var_dict': {'name': 'SPFH',
                                     'levels': ['Z2']},
                   'obs_var_dict': {'name': 'SPFH',
                                    'levels': ['Z2']}},
        'HPBL': {'vx_masks': ['G002', 'NHX', 'SHX', 'N60', 'S60', 'TRO', 'NPO',
                              'SPO', 'NAO', 'SAO', 'CONUS'],
                 'fcst_var_dict': {'name': 'HPBL',
                                   'levels': ['L0']},
                 'obs_var_dict': {'name': 'HPBL',
                                  'levels': ['L0']}},
        'PRESsfc': {'vx_masks': ['G002', 'NHX', 'SHX', 'N60', 'S60', 'TRO', 'NPO',
                                 'SPO', 'NAO', 'SAO', 'CONUS'],
                    'fcst_var_dict': {'name': 'PRES',
                                      'levels': ['Z0']},
                    'obs_var_dict': {'name': 'PRES',
                                     'levels': ['Z0']}},
        'PREStrops': {'vx_masks': ['G002', 'NHX', 'SHX', 'N60', 'S60', 'TRO', 'NPO',
                                   'SPO', 'NAO', 'SAO', 'CONUS'],
                      'fcst_var_dict': {'name': 'PRES',
                                        'levels': ['L0']},
                      'obs_var_dict': {'name': 'PRES',
                                       'levels': ['L0']}},
        'PRMSL': {'vx_masks': ['G002', 'NHX', 'SHX', 'N60', 'S60', 'TRO', 'NPO',
                               'SPO', 'NAO', 'SAO', 'CONUS'],
                  'fcst_var_dict': {'name': 'PRMSL',
                                    'levels': ['Z0']},
                  'obs_var_dict': {'name': 'PRMSL',
                                   'levels': ['Z0']}},
        'UGRD10m': {'vx_masks': ['G002', 'NHX', 'SHX', 'N60', 'S60', 'TRO', 'NPO',
                                 'SPO', 'NAO', 'SAO', 'CONUS'],
                    'fcst_var_dict': {'name': 'UGRD',
                                      'levels': ['Z10']},
                    'obs_var_dict': {'name': 'UGRD',
                                     'levels': ['Z10']}},
        'VGRD10m': {'vx_masks': ['G002', 'NHX', 'SHX', 'N60', 'S60', 'TRO', 'NPO',
                                 'SPO', 'NAO', 'SAO', 'CONUS'],
                    'fcst_var_dict': {'name': 'VGRD',
                                      'levels': ['Z10']},
                    'obs_var_dict': {'name': 'VGRD',
                                     'levels': ['Z10']}},
        'TSOILtop': {'vx_masks': ['G002', 'NHX', 'SHX', 'N60', 'S60', 'TRO', 'NPO',
                                  'SPO', 'NAO', 'SAO', 'CONUS'],
                     'fcst_var_dict': {'name': 'TSOIL',
                                       'levels': ['Z0.1-0']},
                     'obs_var_dict': {'name': 'TSOIL',
                                      'levels': ['Z0.1-0']}},
        'SOILWtop': {'vx_masks': ['G002', 'NHX', 'SHX', 'N60', 'S60', 'TRO', 'NPO',
                                  'SPO', 'NAO', 'SAO', 'CONUS'],
                     'fcst_var_dict': {'name': 'SOILW',
                                       'levels': ['Z0.1-0']},
                     'obs_var_dict': {'name': 'SOILW',
                                      'levels': ['Z0.1-0']}},
        'WEASD': {'vx_masks': ['G002', 'NHX', 'SHX', 'N60', 'S60', 'TRO', 'NPO',
                               'SPO', 'NAO', 'SAO', 'CONUS'],
                  'fcst_var_dict': {'name': 'WEASD',
                                    'levels': ['Z0']},
                  'obs_var_dict': {'name': 'WEASD',
                                   'levels': ['Z0']}},
        'CAPE': {'vx_masks': ['G002', 'NHX', 'SHX', 'N60', 'S60', 'TRO', 'NPO',
                              'SPO', 'NAO', 'SAO', 'CONUS'],
                 'fcst_var_dict': {'name': 'CAPE',
                                   'levels': ['Z0']},
                 'obs_var_dict': {'name': 'CAPE',
                                  'levels': ['Z0']}},
        'PWAT': {'vx_masks': ['G002', 'NHX', 'SHX', 'N60', 'S60', 'TRO', 'NPO',
                              'SPO', 'NAO', 'SAO', 'CONUS'],
                 'fcst_var_dict': {'name': 'PWAT',
                                   'levels': ['L0']},
                 'obs_var_dict': {'name': 'PWAT',
                                  'levels': ['L0']}},
        'CWAT': {'vx_masks': ['G002', 'NHX', 'SHX', 'N60', 'S60', 'TRO', 'NPO',
                              'SPO', 'NAO', 'SAO', 'CONUS'],
                 'fcst_var_dict': {'name': 'CWAT',
                                   'levels': ['L0']},
                 'obs_var_dict': {'name': 'CWAT',
                                  'levels': ['L0']}},
        'HGTtrops': {'vx_masks': ['G002', 'NHX', 'SHX', 'N60', 'S60', 'TRO', 'NPO',
                                  'SPO', 'NAO', 'SAO', 'CONUS'],
                     'fcst_var_dict': {'name': 'HGT',
                                       'levels': ['L0']},
                     'obs_var_dict': {'name': 'HGT',
                                      'levels': ['L0']}},
        'TOZNEclm': {'vx_masks': ['G002', 'NHX', 'SHX', 'N60', 'S60', 'TRO', 'NPO',
                                  'SPO', 'NAO', 'SAO', 'CONUS'],
                     'fcst_var_dict': {'name': 'TOZNE',
                                       'levels': ['L0']},
                     'obs_var_dict': {'name': 'TOZNE',
                                      'levels': ['L0']}},
    }
}

# condense_stats jobs
condense_stats_jobs_dict = copy.deepcopy(base_plot_jobs_info_dict)
# anom
for anom_job in list(condense_stats_jobs_dict['anom'].keys()):
    if anom_job == 'UGRD_VGRD':
        anom_job_line_types = ['VAL1L2']
    else:
        anom_job_line_types = ['SAL1L2']
    condense_stats_jobs_dict['anom'][anom_job]['line_types'] = (
        anom_job_line_types
    )
# pres
for pres_job in list(condense_stats_jobs_dict['pres'].keys()):
    if pres_job == 'UGRD_VGRD':
        pres_job_line_types = ['VL1L2']
    else:
        pres_job_line_types = ['SL1L2']
    condense_stats_jobs_dict['pres'][pres_job]['line_types'] = (
        pres_job_line_types
    )
# sfc
for sfc_job in list(condense_stats_jobs_dict['sfc'].keys()):
    condense_stats_jobs_dict['sfc'][sfc_job]['line_types'] = ['SL1L2']
if JOB_GROUP == 'condense_stats':
    JOB_GROUP_dict = condense_stats_jobs_dict

# filter_stats jobs
filter_stats_jobs_dict = copy.deepcopy(condense_stats_jobs_dict)
# anom
for anom_job in list(filter_stats_jobs_dict['anom'].keys()):
    (filter_stats_jobs_dict['anom'][anom_job]\
     ['fcst_var_dict']['threshs']) = ['NA']
    (filter_stats_jobs_dict['anom'][anom_job]\
     ['obs_var_dict']['threshs']) = ['NA']
    if anom_job == 'HGT_WV1_0-20':
        anom_job_interps = ['WV1_0-20/NA']
    elif anom_job == 'HGT_WV1_0-3':
        anom_job_interps = ['WV1_0-3/NA']
    elif anom_job == 'HGT_WV1_4-9':
        anom_job_interps = ['WV1_4-9/NA']
    elif anom_job == 'HGT_WV1_10-20':
        anom_job_interps = ['WV1_10-20/NA']
    else:
        anom_job_interps = ['NEAREST/1']
    filter_stats_jobs_dict['anom'][anom_job]['interps'] = (
        anom_job_interps
    )
# pres
for pres_job in list(filter_stats_jobs_dict['pres'].keys()):
    (filter_stats_jobs_dict['pres'][pres_job]\
     ['fcst_var_dict']['threshs']) = ['NA']
    (filter_stats_jobs_dict['pres'][pres_job]\
     ['obs_var_dict']['threshs']) = ['NA']
    filter_stats_jobs_dict['pres'][pres_job]['interps'] = ['NEAREST/1']
# sfc
for sfc_job in list(filter_stats_jobs_dict['sfc'].keys()):
    (filter_stats_jobs_dict['sfc'][sfc_job]\
     ['fcst_var_dict']['threshs']) = ['NA']
    (filter_stats_jobs_dict['sfc'][sfc_job]\
     ['obs_var_dict']['threshs']) = ['NA']
    filter_stats_jobs_dict['sfc'][sfc_job]['interps'] = ['NEAREST/1']
if JOB_GROUP == 'filter_stats':
    JOB_GROUP_dict = filter_stats_jobs_dict

# scorecard_avg_ci jobs
scorecard_avg_ci_jobs_dict = copy.deepcopy(filter_stats_jobs_dict)

# anom
for anom_job in list(scorecard_avg_ci_jobs_dict['anom'].keys()):
    scorecard_avg_ci_jobs_dict['anom'][anom_job]['metric'] = ['acc']
# pres
for pres_job in list(scorecard_avg_ci_jobs_dict['pres'].keys()):
    scorecard_avg_ci_jobs_dict['pres'][pres_job]['metric'] = [
        'bias', 'rmse'
    ]
# sfc
del scorecard_avg_ci_jobs_dict['sfc']

# Assign the final dictionary to JOB_GROUP_dict for return
if JOB_GROUP == 'scorecard_avg_ci':
    JOB_GROUP_dict = scorecard_avg_ci_jobs_dict

# make_plots jobs
make_plots_jobs_dict = copy.deepcopy(filter_stats_jobs_dict)
# anom
for anom_job in list(make_plots_jobs_dict['anom'].keys()):
    del make_plots_jobs_dict['anom'][anom_job]['line_types']
    if anom_job == 'UGRD_VGRD':
        anom_job_line_type_stats = ['VAL1L2/ACC']
    else:
        anom_job_line_type_stats = ['SAL1L2/ACC']
    make_plots_jobs_dict['anom'][anom_job]['line_type_stats'] = (
        anom_job_line_type_stats
    )
    make_plots_jobs_dict['anom'][anom_job]['plots'] = [
        'time_series', 'lead_average', 'lead_by_date'
    ]
# pres
for pres_job in list(make_plots_jobs_dict['pres'].keys()):
    del make_plots_jobs_dict['pres'][pres_job]['line_types']
    if pres_job == 'UGRD_VGRD':
        pres_job_line_type_stats = [
            'VL1L2/ME', 'VL1L2/RMSE', 'VL1L2/MSESS', 'VL1L2/RSD',
            'VL1L2/RMSE_MD', 'VL1L2/RMSE_PV'
        ]
    else:
        pres_job_line_type_stats = [
            'SL1L2/ME', 'SL1L2/RMSE', 'SL1L2/MSESS', 'SL1L2/RSD',
            'SL1L2/RMSE_MD', 'SL1L2/RMSE_PV'
        ]
    make_plots_jobs_dict['pres'][pres_job]['line_type_stats'] = (
        pres_job_line_type_stats
    )
    make_plots_jobs_dict['pres'][pres_job]['plots'] = [
        'time_series', 'lead_average', 'lead_by_level', 'date_by_level'
    ]
# sfc
for sfc_job in list(make_plots_jobs_dict['sfc'].keys()):
    del make_plots_jobs_dict['sfc'][sfc_job]['line_types']
    make_plots_jobs_dict['sfc'][sfc_job]['line_type_stats'] = [
        'SL1L2/FBAR'
    ]
    make_plots_jobs_dict['sfc'][sfc_job]['plots'] = [
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
    if JOB_GROUP == 'scorecard_avg_ci' and case_type == 'sfc':
        continue
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
        case_type_env_list = ['grid', 'event_eq', 'fhr_list', 'valid_hr_list',
                              'valid_hr_beg', 'valid_hr_end', 'valid_hr_inc',
                              'init_hr_list', 'init_hr_beg', 'init_hr_end',
                              'init_hr_inc']
        for case_type_env in case_type_env_list:
            job_env_dict[case_type_env] = (
                os.environ[RUN_abbrev_type+'_'+case_type_env]
            )
        if JOB_GROUP in ['filter_stats', 'scorecard_avg_ci', 'make_plots']:
            valid_hr_start = int(job_env_dict['valid_hr_beg'])
            valid_hr_end = int(job_env_dict['valid_hr_end'])
            valid_hr_inc = int(job_env_dict['valid_hr_inc'])
            valid_hr_inc = valid_hr_inc // 3600
            valid_hrs = list(range(valid_hr_start,
                                   valid_hr_end+valid_hr_inc,
                                   valid_hr_inc))
        config_obs_list = (
            os.environ[RUN_abbrev_type+'_truth_name_list']\
            .split(' ')
        )
        obs_list = []
        for idx in range(len(config_obs_list)):
            cobs = config_obs_list[idx]
            obs_list.append(cobs.replace('self', model_list[idx]))
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
        elif JOB_GROUP == 'scorecard_avg_ci':
            JOB_GROUP_case_type_job_product_loops = list(itertools.product(
                case_type_plot_jobs_dict[case_type_job]['line_types'],
                case_type_plot_jobs_dict[case_type_job]['fcst_var_dict']['levels'],
                case_type_plot_jobs_dict[case_type_job]['vx_masks'],
                case_type_plot_jobs_dict[case_type_job]['fcst_var_dict']['threshs'],
                case_type_plot_jobs_dict[case_type_job]['interps'],
                case_type_plot_jobs_dict[case_type_job]['metric']
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
                job_env_dict['obs_list'] = (
                    obs_list[model_list.index(loop_info[3])]
                )
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
                job_file = os.path.join(JOB_GROUP_jobs_dir, 'job'+str(njobs))
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
                    vfg_util.python_command('grid2grid', 'grid2grid_plots.py',[])
                    +'\n'
                )
                job.close()
            elif JOB_GROUP == 'scorecard_avg_ci':
                job_env_dict['line_type'] = loop_info[0]
                job_env_dict['fcst_var_level'] = loop_info[1]
                job_env_dict['obs_var_level'] = (
                    case_type_plot_jobs_dict[case_type_job]\
                    ['obs_var_dict']['levels'][
                        case_type_plot_jobs_dict[case_type_job]\
                        ['fcst_var_dict']['levels'].index(loop_info[1])
                    ]
                )
                job_env_dict['vx_mask'] = loop_info[2]
                job_env_dict['fcst_var_thresh'] = loop_info[3]
                job_env_dict['obs_var_thresh'] = (
                    case_type_plot_jobs_dict[case_type_job]\
                    ['obs_var_dict']['threshs'][
                        case_type_plot_jobs_dict[case_type_job]\
                        ['fcst_var_dict']['threshs'].index(loop_info[3])
                    ]
                )
                job_env_dict['interp_method'] = loop_info[4].split('/')[0]
                job_env_dict['interp_points'] = loop_info[4].split('/')[1]
                job_env_dict['metric'] = loop_info[5]
                job_env_dict['valid_hr_list'] = "00"
                job_env_dict['init_hr_list'] = "00"
                job_env_dict['model_list'] = ', '.join(model_list)
                job_env_dict['obs_list'] = ', '.join(obs_list)
                job_env_dict['fhr_list'] = "24, 48, 72, 96, 120, 144, 168, 192, 216, 240"
                job_env_dict['CI_METHOD'] = CI_METHOD
                job_env_dict['AVERAGE_METHOD'] = AVERAGE_METHOD
                # Set up output directories
                njobs+=1
                job_env_dict['job_id'] = 'job'+str(njobs)
                job_DATA_dir = os.path.join(DATA, RUN, 'plot_output',
                                            'plot_by_'+plot_by,
                                            JOB_GROUP)
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
                    vfg_util.python_command('grid2grid', 'scorecard_avg_ci.py',[])
                    +'\n'
                )
                job.close()
            elif JOB_GROUP == 'make_plots':
                job_env_dict['model_list'] = ', '.join(model_list)
                job_env_dict['model_plot_name_list'] = (
                    ', '.join(model_plot_name_list)
                )
                job_env_dict['obs_list'] = ', '.join(obs_list)
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
                    run_verif_global_g2g_plots = ['plots']
                    for run_verif_global_g2g_plot in run_verif_global_g2g_plots:
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
                            vfg_util.python_command('grid2grid', 'grid2grid_plots.py',[])
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
