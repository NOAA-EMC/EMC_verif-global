'''
Program Name: create_METplus_output_dirs.py
Contact(s): Mallory Row
Abstract: This script is run by all scripts in scripts/.
          This creates the base directories and their subdirectories
          for the METplus verification use cases and their types.
'''

import sys
import os
import datetime

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
DATA = os.environ['DATA']
RUN = os.environ['RUN']
make_met_data_by = os.environ['make_met_data_by']
plot_by = os.environ['plot_by']
model_list = os.environ['model_list'].split(' ')

# Create METplus output base directories
metplus_output_dir = os.path.join(DATA, RUN, 'metplus_output')
metplus_job_scripts_dir = os.path.join(DATA, RUN, 'metplus_job_scripts')
os.makedirs(metplus_output_dir, mode=0775)
os.makedirs(metplus_job_scripts_dir, mode=0775)

# Build information of METplus output subdirectories to create
metplus_output_subdir_list = [ 'confs', 'logs' ]
if RUN == 'grid2grid_step1':
    gather_by = os.environ['g2g1_gather_by']
    for type in os.environ['g2g1_type_list'].split(' '):
       for model in model_list:
           metplus_output_subdir_list.append(
               os.path.join('make_met_data_by_'+make_met_data_by,
                            'grid_stat', type, model)
           )
           metplus_output_subdir_list.append(
               os.path.join('gather_by_'+gather_by,
                            'stat_analysis', type, model)
           ) 
elif RUN == 'grid2grid_step2':
    metplus_output_subdir_list.append(
       os.path.join('plot_by_'+plot_by, 'stat_analysis')
    )
    metplus_output_subdir_list.append(
       os.path.join('plot_by_'+plot_by, 'make_plots')
    )
    metplus_output_subdir_list.append(
       'images'
    )
    if os.environ['g2g2_make_scorecard'] == 'YES':
        metplus_output_subdir_list.append(
           'scorecard'
        )
elif RUN == 'grid2obs_step1':
    gather_by = os.environ['g2o1_gather_by']
    for type in os.environ['g2o1_type_list'].split(' '):
        metplus_output_subdir_list.append(
            os.path.join('make_met_data_by_'+make_met_data_by,
                         'pb2nc',type, 'prepbufr')
        )
        for model in model_list:
            metplus_output_subdir_list.append(
                os.path.join('make_met_data_by_'+make_met_data_by,
                             'point_stat', type, model)
            )
            metplus_output_subdir_list.append(
                os.path.join('gather_by_'+gather_by,
                             'stat_analysis', type, model)
            )
elif RUN == 'grid2obs_step2':
    metplus_output_subdir_list.append(
       os.path.join('plot_by_'+plot_by, 'stat_analysis')
    )
    metplus_output_subdir_list.append(
       os.path.join('plot_by_'+plot_by, 'make_plots')
    )
    metplus_output_subdir_list.append(
       'images'
    )
elif RUN == 'precip_step1':
    gather_by = os.environ['precip1_gather_by'] 
    for type in os.environ['precip1_type_list'].split(' '):
        for model in model_list:
            metplus_output_subdir_list.append(
                os.path.join('make_met_data_by_'+make_met_data_by,
                             'pcp_combine', type, model)
            )
            metplus_output_subdir_list.append(
                os.path.join('make_met_data_by_'+make_met_data_by,
                             'grid_stat', type, model)
            )
            metplus_output_subdir_list.append(
                os.path.join('gather_by_'+gather_by,
                             'stat_analysis', type, model)
            )
elif RUN == 'precip_step2':
    metplus_output_subdir_list.append(
       os.path.join('plot_by_'+plot_by, 'stat_analysis')
    )
    metplus_output_subdir_list.append(
       os.path.join('plot_by_'+plot_by, 'make_plots')
    )
    metplus_output_subdir_list.append(
       'images'
    )
elif RUN == 'tropcyc':
    metplus_output_subdir_list.append(
       'images'
    )
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
    for storm in storm_list:
        basin = storm.split('_')[0]
        metplus_output_subdir_list.append(
            os.path.join('gather',
                         'tc_stat', storm)
        )
        metplus_output_subdir_list.append(
            os.path.join('plot', storm, 'imgs')
        )
        if (os.path.join('gather', 'tc_stat', basin)
                not in metplus_output_subdir_list):
            metplus_output_subdir_list.append(
                os.path.join('gather', 'tc_stat', basin)
            )
        if (os.path.join('plot', basin, 'imgs')
                not in metplus_output_subdir_list):
            metplus_output_subdir_list.append(
                os.path.join('plot', basin, 'imgs')
            )
        for model in model_list:
            metplus_output_subdir_list.append(
                os.path.join('make_met_data',
                             'tc_pairs', storm, model)
            )
elif RUN == 'maps2d':
    make_met_data_by = os.environ['maps2d_make_met_data_by']
    plot_by = make_met_data_by
    metplus_output_subdir_list.append(
       os.path.join('plot_by_'+plot_by)
    )
    metplus_output_subdir_list.append(
       'images'
    )
    for type in os.environ['maps2d_type_list'].split(' '):
        metplus_output_subdir_list.append(
           os.path.join('make_met_data_by_'+make_met_data_by,
                        'series_analysis', type)
        )

# Create METplus output subdirectories
for subdir in metplus_output_subdir_list:
    metplus_output_subdir = os.path.join(metplus_output_dir, subdir)
    os.makedirs(metplus_output_subdir, mode=0775)

print("END: "+os.path.basename(__file__))
