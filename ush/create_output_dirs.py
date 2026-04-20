'''
Program Name: create_output_dirs.py
Contact(s): Mallory Row
Abstract: This script is run by all scripts in scripts/.
          This creates the base directories and their subdirectories
          for the job.
'''

import os

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
DATA = os.environ['DATA']
RUN = os.environ['RUN']
make_met_data_by = os.environ['make_met_data_by']
plot_by = os.environ['plot_by']
model_list = os.environ['model_list'].split(' ')
RUN_abbrev = os.environ['RUN_abbrev']
RUN_type_list = os.environ[RUN_abbrev+'_type_list'].split(' ')

# Create output base directories
if 'step2' in RUN:
    base_output_dir = os.path.join(DATA, RUN, 'plot_output')
    base_job_scripts_dir = os.path.join(DATA, RUN, 'plot_job_scripts')
else:
    base_output_dir = os.path.join(DATA, RUN, 'metplus_output')
    base_job_scripts_dir = os.path.join(DATA, RUN, 'metplus_job_scripts')
os.makedirs(base_output_dir, mode=0o755)
os.makedirs(base_job_scripts_dir, mode=0o755)

# Build information of METplus output subdirectories to create
base_output_subdir_list = [ 'confs', 'logs', 'tmp' ]
if 'step2' in RUN:
    base_output_subdir_list.append(
       os.path.join('plot_by_'+plot_by, 'condense_stats')
    )
    base_output_subdir_list.append(
       os.path.join('plot_by_'+plot_by, 'filter_stats')
    )
    base_output_subdir_list.append(
        os.path.join('plot_by_'+plot_by,'make_plots')
    )
    base_output_subdir_list.append('images')
    if RUN == 'grid2grid_step2':
        if os.environ[RUN_abbrev+'_make_scorecard'] == 'YES':
            base_output_subdir_list.append('scorecard')
elif RUN in ['grid2grid_step1', 'satellite_step1']:
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        gather_by = os.environ[RUN_abbrev_type+'_gather_by']
        for model in model_list:
            base_output_subdir_list.append(
                os.path.join('make_met_data_by_'+make_met_data_by,
                             'grid_stat', RUN_type, model)
            )
            base_output_subdir_list.append(
                os.path.join('gather_by_'+gather_by, 'stat_analysis',
                             RUN_type, model)
            )
elif RUN == 'grid2obs_step1':
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        gather_by = os.environ[RUN_abbrev_type+'_gather_by']
        if RUN_type in ['upper_air', 'conus_sfc']:
           met_2nc_tool = 'pb2nc'
           obs_file = 'prepbufr'
        elif RUN_type == 'polar_sfc':
           met_2nc_tool = 'ascii2nc'
           obs_file = 'iabp'
        base_output_subdir_list.append(
            os.path.join('make_met_data_by_'+make_met_data_by,
                         met_2nc_tool, RUN_type, obs_file)
        )
        for model in model_list:
            base_output_subdir_list.append(
                os.path.join('make_met_data_by_'+make_met_data_by,
                             'point_stat', RUN_type, model)
            )
            base_output_subdir_list.append(
                os.path.join('gather_by_'+gather_by, 'stat_analysis',
                             RUN_type, model)
            )
elif RUN == 'precip_step1':
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        gather_by = os.environ[RUN_abbrev_type+'_gather_by']
        for model in model_list:
            base_output_subdir_list.append(
                os.path.join('make_met_data_by_'+make_met_data_by,
                             'pcp_combine', RUN_type, model)
            )
            base_output_subdir_list.append(
                os.path.join('make_met_data_by_'+make_met_data_by,
                             'grid_stat', RUN_type, model)
            )
            base_output_subdir_list.append(
                os.path.join('gather_by_'+gather_by, 'stat_analysis',
                             RUN_type, model)
            )
elif RUN in ['maps2d', 'mapsda']:
    base_output_subdir_list.append('images')
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        make_met_data_by = os.environ[RUN_abbrev_type
                                     +'_make_met_data_by']
        plot_by = make_met_data_by
        base_output_subdir_list.append(os.path.join('plot_by_'+plot_by))
        if RUN == 'maps2d' or RUN_type == 'gdas':
            base_output_subdir_list.append(
                os.path.join('make_met_data_by_'+make_met_data_by,
                             'series_analysis', RUN_type)
            )

# Create METplus output subdirectories
for subdir in base_output_subdir_list:
    base_output_subdir = os.path.join(base_output_dir, subdir)
    if not os.path.exists(base_output_subdir):
        os.makedirs(base_output_subdir, mode=0o755)

print("END: "+os.path.basename(__file__))
