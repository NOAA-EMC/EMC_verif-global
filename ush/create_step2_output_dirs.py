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
if RUN != 'tropcyc':
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
elif RUN == 'tropcyc':
    plot_output_subdir_list.append('images')
    import get_tc_info
    tc_dict = get_tc_info.get_tc_dict()
    RUN_abbrev_tc_list = []
    for config_storm in os.environ[RUN_abbrev+'_storm_list'].split(' '):
        config_storm_basin = config_storm.split('_')[0]
        config_storm_year = config_storm.split('_')[1]
        config_storm_name = config_storm.split('_')[2]
        if config_storm_name == 'ALLNAMED':
            for byn in list(tc_dict.keys()):
                if config_storm_basin+'_'+config_storm_year in byn:
                    RUN_abbrev_tc_list.append(byn)
        else:
            RUN_abbrev_tc_list.append(config_storm)
    for tc in RUN_abbrev_tc_list:
        basin = tc.split('_')[0]
        plot_output_subdir_list.append(
            os.path.join('gather', 'tc_stat', tc)
        )
        plot_output_subdir_list.append(
            os.path.join('gather', 'tc_stat',
                         'all_storms_dump_row')
        )
        plot_output_subdir_list.append(
            os.path.join('plot', tc, 'images')
        )
        if (os.path.join('gather', 'tc_stat', basin)
                not in plot_output_subdir_list):
            plot_output_subdir_list.append(
                os.path.join('gather', 'tc_stat', basin)
            )
        if (os.path.join('plot', basin, 'imgs')
                not in plot_output_subdir_list):
            plot_output_subdir_list.append(
                os.path.join('plot', basin, 'imgs')
            )
        for model in model_list:
            plot_output_subdir_list.append(
                os.path.join('make_met_data', 'tc_pairs', tc, model)
            )
elif RUN == 'maps2d':
    plot_output_subdir_list.append('images')
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        make_met_data_by = os.environ[RUN_abbrev_type
                                     +'_make_met_data_by']
        plot_by = make_met_data_by
        plot_output_subdir_list.append(os.path.join('plot_by_'+plot_by))
        plot_output_subdir_list.append(
           os.path.join('make_met_data_by_'+make_met_data_by,
                        'series_analysis', RUN_type)
        )
elif RUN == 'mapsda':
    plot_output_subdir_list.append('images')
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        make_met_data_by = os.environ[RUN_abbrev_type
                                      +'_make_met_data_by']
        plot_by = make_met_data_by
        plot_output_subdir_list.append(os.path.join('plot_by_'+plot_by))
        if type == 'gdas':
            plot_output_subdir_list.append(
               os.path.join('make_met_data_by_'+make_met_data_by,
                            'series_analysis', RUN_type)
            )

# Create plot output subdirectories
for subdir in plot_output_subdir_list:
    plot_output_subdir = os.path.join(plot_output_dir, subdir)
    if not os.path.exists(plot_output_subdir):
        os.makedirs(plot_output_subdir, mode=0o755)

print("END: "+os.path.basename(__file__))
