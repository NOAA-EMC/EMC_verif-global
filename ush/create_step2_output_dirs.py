'''
Program Name: create_step2_output_dirs.py
Contact(s): Mallory Row
Abstract: This script is run by step2 scripts in scripts/.
          This creates the base directories and their subdirectories
          for the plot verification use cases and their types.
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

# Create plot output base directories
plot_output_dir = os.path.join(DATA, RUN, 'plot_output')
plot_job_scripts_dir = os.path.join(DATA, RUN, 'plot_job_scripts')
os.makedirs(plot_output_dir, mode=0o755)
os.makedirs(plot_job_scripts_dir, mode=0o755)

# Build information of plot output subdirectories to create
plot_output_subdir_list = [ 'confs', 'logs', 'tmp' ]
if 'step2' in RUN:
    plot_output_subdir_list.append(
        os.path.join('plot_by_'+plot_by, 'condense_stats')
    )
    plot_output_subdir_list.append(
       os.path.join('plot_by_'+plot_by, 'filter_stats')
    )
    plot_output_subdir_list.append(
        os.path.join('plot_by_'+plot_by,'make_plots')
    )
    plot_output_subdir_list.append('images')
    if RUN == 'grid2grid_step2':
        if os.environ[RUN_abbrev+'_make_scorecard'] == 'YES':
            plot_output_subdir_list.append('scorecard')

# Create plot output subdirectories
for subdir in plot_output_subdir_list:
    plot_output_subdir = os.path.join(plot_output_dir, subdir)
    if not os.path.exists(plot_output_subdir):
        os.makedirs(plot_output_subdir, mode=0o755)

print("END: "+os.path.basename(__file__))
