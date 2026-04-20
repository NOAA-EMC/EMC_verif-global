'''
Name: satellite_plots.py
Contact(s): Ho-Chun Huang (ho-chun.huang@noaa.gov)
Abstract: This is the driver script for creating plots.
Run By: individual plotting job scripts generated through
        ush/plots/satellite/step2_satellite_create_job_scripts.py
'''

import os
import sys
import logging
import datetime
import glob
import itertools
import shutil
import verif_global_util as vfg_util
from satellite_plots_specs import PlotSpecs

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
DATA = os.environ['DATA']
job_DATA_dir = os.environ['job_DATA_dir']
RUN = os.environ['RUN']
RUN_CASE = os.environ['RUN_CASE']
USHverif_global = os.environ['USHverif_global']
FIXverif_global = os.environ['FIXverif_global']
JOB_GROUP = os.environ['JOB_GROUP']
MET_ROOT = os.environ['HOMEMET']
met_ver = os.environ['MET_version']
start_date = os.environ['start_date']
end_date = os.environ['end_date']
plot_by = os.environ['plot_by']
plot_verbosity = os.environ['plot_verbosity']
CASE_TYPE = os.environ['CASE_TYPE']
job_id = os.environ['job_id']
if JOB_GROUP == 'condense_stats':
    line_type = os.environ['line_type']
    fcst_var_name = os.environ['fcst_var_name']
    obs_var_name = os.environ['obs_var_name']
    vx_mask = os.environ['vx_mask']
    model_list = os.environ['model_list'].split(', ')
    model_plot_name_list = os.environ['model_plot_name_list'].split(', ')
    obs_list = os.environ['obs_list'].split(', ')
    fcst_var_level = os.environ['fcst_var_level']
    obs_var_level = os.environ['obs_var_level']
elif JOB_GROUP == 'filter_stats':
    line_type = os.environ['line_type']
    fcst_var_name = os.environ['fcst_var_name']
    obs_var_name = os.environ['obs_var_name']
    vx_mask = os.environ['vx_mask']
    model_list = os.environ['model_list'].split(', ')
    model_plot_name_list = os.environ['model_plot_name_list'].split(', ')
    obs_list = os.environ['obs_list'].split(', ')
    valid_hr_start = os.environ['valid_hr_start']
    valid_hr_end = os.environ['valid_hr_end']
    valid_hr_inc = os.environ['valid_hr_inc']
    init_hr_start = os.environ['init_hr_start']
    init_hr_end = os.environ['init_hr_end']
    init_hr_inc = os.environ['init_hr_inc']
    fhr_list = os.environ['fhr_list']
    grid = os.environ['grid']
    event_equalization = os.environ['event_eq']
    interp_method = os.environ['interp_method']
    interp_points = os.environ['interp_points']
    fcst_var_level = os.environ['fcst_var_level']
    fcst_var_thresh = os.environ['fcst_var_thresh']
    obs_var_level = os.environ['obs_var_level']
    obs_var_thresh = os.environ['obs_var_thresh']
elif JOB_GROUP == 'make_plots':
    line_type = os.environ['line_type']
    fcst_var_name = os.environ['fcst_var_name']
    obs_var_name = os.environ['obs_var_name']
    vx_mask = os.environ['vx_mask']
    model_list = os.environ['model_list'].split(', ')
    model_plot_name_list = os.environ['model_plot_name_list'].split(', ')
    obs_list = os.environ['obs_list'].split(', ')
    valid_hr_start = os.environ['valid_hr_start']
    valid_hr_end = os.environ['valid_hr_end']
    valid_hr_inc = os.environ['valid_hr_inc']
    init_hr_start = os.environ['init_hr_start']
    init_hr_end = os.environ['init_hr_end']
    init_hr_inc = os.environ['init_hr_inc']
    fhr_list = os.environ['fhr_list']
    grid = os.environ['grid']
    event_equalization = os.environ['event_eq']
    interp_method = os.environ['interp_method']
    interp_points = os.environ['interp_points']
    fcst_var_level_list = os.environ['fcst_var_level_list'].split(', ')
    fcst_var_thresh_list = os.environ['fcst_var_thresh_list'].split(', ')
    obs_var_level_list = os.environ['obs_var_level_list'].split(', ')
    obs_var_thresh_list = os.environ['obs_var_thresh_list'].split(', ')
    stat = os.environ['stat']
    plot = os.environ['plot']

# Set variables
start_date_dt = datetime.datetime.strptime(start_date, '%Y%m%d')
end_date_dt = datetime.datetime.strptime(end_date, '%Y%m%d')
now = datetime.datetime.now()

# Set up directory paths
logo_dir = os.path.join(USHverif_global, 'plots', 'logos')
RUN_dir = os.path.join(DATA, RUN)
stat_base_dir = os.path.join(RUN_dir, 'data')
logging_dir = os.path.join(DATA, RUN, 'plot_output', 'logs')
vfg_util.make_dir(logging_dir)

# Set up logging
job_logging_file = os.path.join(logging_dir, 'verif_global_'+RUN+'_'
                                +CASE_TYPE+'_'
                                +JOB_GROUP+'_'+job_id+'_runon'
                                +now.strftime('%Y%m%d%H%M%S')+'.log')
logger = logging.getLogger(job_logging_file)
logger.setLevel(plot_verbosity)
formatter = logging.Formatter(
    '%(asctime)s.%(msecs)03d (%(filename)s:%(lineno)d) %(levelname)s: '
    + '%(message)s',
    '%m/%d %H:%M:%S'
)
file_handler = logging.FileHandler(job_logging_file, mode='a')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger_info = f"Log file: {job_logging_file}"
print(logger_info)
logger.info(logger_info)

# Set up model information dictionary
original_model_info_dict = {}
for model_idx in range(len(model_list)):
    model_num = model_idx + 1
    original_model_info_dict['model'+str(model_num)] = {
        'name': model_list[model_idx],
        'plot_name': model_plot_name_list[model_idx],
        'obs_name': obs_list[model_idx]
    }

# Set up date information dictionary
original_date_info_dict = {
    'plot_by': plot_by,
    'start_date': start_date,
    'end_date': end_date
}
if JOB_GROUP in ['filter_stats', 'make_plots']:
    original_date_info_dict['init_hr_start'] = init_hr_start
    original_date_info_dict['init_hr_end'] = init_hr_end
    original_date_info_dict['init_hr_inc'] = init_hr_inc
    valid_hrs = list(range(int(valid_hr_start),
                           int(valid_hr_end)+int(valid_hr_inc),
                           int(valid_hr_inc)))
    init_hrs = list(range(int(init_hr_start),
                          int(init_hr_end)+int(init_hr_inc),
                          int(init_hr_inc)))
    fhrs = [int(i) for i in fhr_list.split(', ')]

# Set up plot information dictionary
original_plot_info_dict = {
    'line_type': line_type,
    'vx_mask': vx_mask,
    'ob_name': obs_list[0]
}
if JOB_GROUP in ['filter_stats', 'make_plots']:
    original_plot_info_dict['RUN_CASE'] = RUN_CASE
    original_plot_info_dict['grid'] = grid
    original_plot_info_dict['interp_method'] = interp_method
    original_plot_info_dict['interp_points'] = interp_points
    original_plot_info_dict['event_equalization'] = event_equalization
    if JOB_GROUP == 'filter_stats':
        original_plot_info_dict['fcst_var_name'] = fcst_var_name
        original_plot_info_dict['fcst_var_level'] = fcst_var_level
        original_plot_info_dict['fcst_var_thresh'] = fcst_var_thresh
        original_plot_info_dict['obs_var_name'] = obs_var_name
        original_plot_info_dict['obs_var_level'] = obs_var_level
        original_plot_info_dict['obs_var_thresh'] = obs_var_thresh
    elif JOB_GROUP == 'make_plots':
        original_plot_info_dict['stat'] = stat
        fcst_var_prod = list(
            itertools.product([fcst_var_name], fcst_var_level_list,
                              fcst_var_thresh_list)
        )
        obs_var_prod = list(
            itertools.product([obs_var_name], obs_var_level_list,
                              obs_var_thresh_list)
        )
        if len(fcst_var_prod) == len(obs_var_prod):
            var_info = []
            for v in range(len(fcst_var_prod)):
                var_info.append((fcst_var_prod[v], obs_var_prod[v]))
        else:
            logger.error("Forecast and observation variable information not "
                         +"the same length")
            sys.exit(1)


# Set up MET information dictionary
original_met_info_dict = {
    'root': MET_ROOT,
    'version': met_ver
}

# Condense .stat files
if JOB_GROUP == 'condense_stats':
    for model_idx in range(len(model_list)):
        model = model_list[model_idx]
        obs_name = obs_list[model_idx]
        stat_input_dir = os.path.join(stat_base_dir, model, CASE_TYPE)
        condensed_model_stat_file = os.path.join(
            job_DATA_dir, f"condensed_stats_{model.lower()}_{line_type.lower()}_"
            +f"{fcst_var_name.lower()}_"
            +f"{fcst_var_level.lower().replace('.','p').replace('-', '_')}_"
            +f"{vx_mask.lower()}.stat"
        )
        if not os.path.exists(condensed_model_stat_file):
            vfg_util.condense_model_stat_files(
                logger, stat_input_dir, job_DATA_dir, model, obs_name, vx_mask,
                fcst_var_name, fcst_var_level, obs_var_name, obs_var_level,
                line_type
            )
elif JOB_GROUP == 'filter_stats':
    model_info_dict = original_model_info_dict.copy()
    date_info_dict = original_date_info_dict.copy()
    plot_info_dict = original_plot_info_dict.copy()
    met_info_dict = original_met_info_dict.copy()
    for filter_info in list(itertools.product(valid_hrs, fhrs)):
        date_info_dict['valid_hr_start'] = str(filter_info[0])
        date_info_dict['valid_hr_end'] = str(filter_info[0])
        date_info_dict['valid_hr_inc'] = '24'
        date_info_dict['forecast_hour'] = str(filter_info[1])
        init_hr = vfg_util.get_init_hour(
            int(date_info_dict['valid_hr_start']),
            int(date_info_dict['forecast_hour'])
        )
        if init_hr in init_hrs:
            valid_dates, init_dates = vfg_util.get_plot_dates(
                logger, date_info_dict['plot_by'],
                date_info_dict['start_date'],
                date_info_dict['end_date'],
                date_info_dict['valid_hr_start'],
                date_info_dict['valid_hr_end'],
                date_info_dict['valid_hr_inc'],
                date_info_dict['init_hr_start'],
                date_info_dict['init_hr_end'],
                date_info_dict['init_hr_inc'],
                date_info_dict['forecast_hour']
            )
            format_valid_dates = [valid_dates[d].strftime('%Y%m%d_%H%M%S') \
                                  for d in range(len(valid_dates))]
            if len(valid_dates) == 0:
                plot_dates = np.arange(
                    datetime.datetime.strptime(
                        date_info_dict['start_date']
                        +date_info_dict['valid_hr_start'],
                        '%Y%m%d%H'
                    ),
                    datetime.datetime.strptime(
                        date_info_dict['end_date']
                        +date_info_dict['valid_hr_end'],
                        '%Y%m%d%H'
                    )
                    +datetime.timedelta(
                        hours=int(date_info_dict['valid_hr_inc'])
                    ),
                    datetime.timedelta(
                        hours=int(date_info_dict['valid_hr_inc'])
                    )
                ).astype(datetime.datetime)
            else:
                plot_dates = valid_dates
            for model_num in list(model_info_dict.keys()):
                model_dict = model_info_dict[model_num]
                filter_stats_model_file = os.path.join(
                    job_DATA_dir,
                    ('fcst'+model_dict['name']+'_'
                     +plot_info_dict['fcst_var_name']
                     +plot_info_dict['fcst_var_level']
                     +plot_info_dict['fcst_var_thresh']+'_'
                     +'obs'+model_dict['obs_name']+'_'
                     +plot_info_dict['obs_var_name']
                     +plot_info_dict['obs_var_level']
                     +plot_info_dict['obs_var_thresh']+'_'
                     +'linetype'+plot_info_dict['line_type']+'_'
                     +'grid'+plot_info_dict['grid']+'_'
                     +'vxmask'+plot_info_dict['vx_mask']+'_'
                     +'interp'+plot_info_dict['interp_method']
                     +plot_info_dict['interp_points']+'_'
                     +date_info_dict['plot_by'].lower()
                     +valid_dates[0].strftime('%Y%m%d%H%M%S')+'to'
                     +valid_dates[-1].strftime('%Y%m%d%H%M%S')+'_'
                     +'fhr'+str(date_info_dict['forecast_hour']).zfill(3))\
                    .lower().replace('.','p').replace('-', '_')\
                    .replace('&&', 'and').replace('||', 'or')\
                    .replace('0,*,*', '').replace('*,*', '')\
                    +'.stat'
                )
                job_input_dir = os.path.join(DATA, RUN, 'plot_output',
                                             'plot_by_'+plot_by,
                                             'condense_stats', CASE_TYPE)
                if not os.path.exists(filter_stats_model_file):
                    all_model_df = vfg_util.build_df(
                        JOB_GROUP, logger, job_input_dir, job_DATA_dir,
                        model_info_dict, met_info_dict,
                        plot_info_dict['fcst_var_name'],
                        plot_info_dict['fcst_var_level'],
                        plot_info_dict['fcst_var_thresh'],
                        plot_info_dict['obs_var_name'],
                        plot_info_dict['obs_var_level'],
                        plot_info_dict['obs_var_thresh'],
                        plot_info_dict['line_type'],
                        plot_info_dict['grid'],
                        plot_info_dict['vx_mask'],
                        plot_info_dict['interp_method'],
                        plot_info_dict['interp_points'],
                        date_info_dict['plot_by'],
                        valid_dates, format_valid_dates,
                        str(date_info_dict['forecast_hour'])
                    )
elif JOB_GROUP == 'make_plots':
    if len(model_list) > 10:
        logger.error("Too many models requested ("+str(len(model_list))
                     +", ["+', '.join(model_list)+"]), maximum is 10")
        sys.exit(1)
    plot_specs = PlotSpecs(logger, plot)
    model_info_dict = original_model_info_dict.copy()
    date_info_dict = original_date_info_dict.copy()
    plot_info_dict = original_plot_info_dict.copy()
    met_info_dict = original_met_info_dict.copy()
    make_plots_input_dir = os.path.join(DATA, RUN, 'plot_output',
                                        'plot_by_'+plot_by,
                                        'filter_stats', CASE_TYPE)
    if plot == 'time_series':
        import plot_time_series as p_ts
        for ts_info in \
                list(itertools.product(valid_hrs, fhrs, var_info)):
            date_info_dict['valid_hr_start'] = str(ts_info[0])
            date_info_dict['valid_hr_end'] = str(ts_info[0])
            date_info_dict['valid_hr_inc'] = '24'
            date_info_dict['forecast_hour'] = str(ts_info[1])
            plot_info_dict['fcst_var_name'] = ts_info[2][0][0]
            plot_info_dict['fcst_var_level'] = ts_info[2][0][1]
            plot_info_dict['fcst_var_thresh'] = ts_info[2][0][2]
            plot_info_dict['obs_var_name'] = ts_info[2][1][0]
            plot_info_dict['obs_var_level'] = ts_info[2][1][1]
            plot_info_dict['obs_var_thresh'] = ts_info[2][1][2]
            init_hr = vfg_util.get_init_hour(
                int(date_info_dict['valid_hr_start']),
                int(date_info_dict['forecast_hour'])
            )
            job_DATA_image_name = plot_specs.get_savefig_name(
                job_DATA_dir, plot_info_dict, date_info_dict
            )
            job_input_dir = make_plots_input_dir
            if init_hr in init_hrs \
                    and not os.path.exists(job_DATA_image_name):
                make_ts = True
            else:
                make_ts = False
            if plot_info_dict['stat'] == 'FBAR_OBAR' \
                    and str(date_info_dict['forecast_hour']) not in \
                    ['24', '72', '120']:
                make_ts = False
            if make_ts:
                plot_ts = p_ts.TimeSeries(logger, job_input_dir,
                                          job_DATA_dir, model_info_dict,
                                          date_info_dict, plot_info_dict,
                                          met_info_dict, logo_dir)
                plot_ts.make_time_series()
    elif plot == 'lead_average':
        import plot_lead_average as p_la
        for la_info in list(itertools.product(valid_hrs, var_info)):
            date_info_dict['valid_hr_start'] = str(la_info[0])
            date_info_dict['valid_hr_end'] = str(la_info[0])
            date_info_dict['valid_hr_inc'] = '24'
            date_info_dict['forecast_hours'] = fhrs
            plot_info_dict['fcst_var_name'] = la_info[1][0][0]
            plot_info_dict['fcst_var_level'] = la_info[1][0][1]
            plot_info_dict['fcst_var_thresh'] = la_info[1][0][2]
            plot_info_dict['obs_var_name'] = la_info[1][1][0]
            plot_info_dict['obs_var_level'] = la_info[1][1][1]
            plot_info_dict['obs_var_thresh'] = la_info[1][1][2]
            job_DATA_image_name = plot_specs.get_savefig_name(
                job_DATA_dir, plot_info_dict, date_info_dict
            )
            job_input_dir = make_plots_input_dir
            if not os.path.exists(job_DATA_image_name) \
                    and plot_info_dict['stat'] != 'FBAR_OBAR':
                if len(date_info_dict['forecast_hours']) <= 1:
                    logger.warning("No span of forecast hours to plot, "
                                   +"given 1 forecast hour, skipping "
                                   +"lead_average plots")
                    make_la = False
                else:
                    make_la = True
            else:
                make_la = False
            if make_la:
                plot_la = p_la.LeadAverage(logger, job_input_dir,
                                           job_DATA_dir, model_info_dict,
                                           date_info_dict, plot_info_dict,
                                           met_info_dict, logo_dir)
                plot_la.make_lead_average()
    elif plot == 'lead_by_date':
        import plot_lead_by_date as p_lbd
        for lbd_info in list(itertools.product(valid_hrs, var_info)):
            date_info_dict['valid_hr_start'] = str(lbd_info[0])
            date_info_dict['valid_hr_end'] = str(lbd_info[0])
            date_info_dict['valid_hr_inc'] = '24'
            date_info_dict['forecast_hours'] = fhrs
            plot_info_dict['fcst_var_name'] = lbd_info[1][0][0]
            plot_info_dict['fcst_var_level'] = lbd_info[1][0][1]
            plot_info_dict['fcst_var_thresh'] = lbd_info[1][0][2]
            plot_info_dict['obs_var_name'] = lbd_info[1][1][0]
            plot_info_dict['obs_var_level'] = lbd_info[1][1][1]
            plot_info_dict['obs_var_thresh'] = lbd_info[1][1][2]
            job_DATA_image_name = plot_specs.get_savefig_name(
                job_DATA_dir, plot_info_dict, date_info_dict
            )
            job_input_dir = make_plots_input_dir
            if not os.path.exists(job_DATA_image_name) \
                    and plot_info_dict['stat'] != 'FBAR_OBAR':
                if len(date_info_dict['forecast_hours']) <= 1:
                    logger.warning("No span of forecast hours to plot, "
                                   +"given 1 forecast hour, skipping "
                                   +"lead_by_date plots")
                    make_lbd = False
                else:
                    make_lbd = True
            else:
                make_lbd = False
            if make_lbd:
                plot_lbd = p_lbd.LeadByDate(logger, job_input_dir,
                                            job_DATA_dir, model_info_dict,
                                            date_info_dict, plot_info_dict,
                                            met_info_dict, logo_dir)
                plot_lbd.make_lead_by_date()
    elif plot == 'lead_by_level':
        import plot_lead_by_level as p_lbl
        fhrs_lbl = fhrs
        vert_profiles = [os.environ['vert_profile']]
        for lbl_info in list(itertools.product(valid_hrs, vert_profiles)):
            date_info_dict['valid_hr_start'] = str(lbl_info[0])
            date_info_dict['valid_hr_end'] = str(lbl_info[0])
            date_info_dict['valid_hr_inc'] = '24'
            date_info_dict['forecast_hours'] = fhrs_lbl
            plot_info_dict['fcst_var_name'] = fcst_var_name
            plot_info_dict['obs_var_name'] = obs_var_name
            plot_info_dict['vert_profile'] = lbl_info[1]
            plot_info_dict['fcst_var_level'] = lbl_info[1]
            plot_info_dict['obs_var_level'] = lbl_info[1]
            for t in range(len(fcst_var_thresh_list)):
                plot_info_dict['fcst_var_thresh'] = fcst_var_thresh_list[t]
                plot_info_dict['obs_var_thresh'] = obs_var_thresh_list[t]
                job_DATA_image_name = plot_specs.get_savefig_name(
                    job_DATA_dir, plot_info_dict, date_info_dict
                )
                job_input_dir = make_plots_input_dir
                if not os.path.exists(job_DATA_image_name) \
                        and plot_info_dict['stat'] != 'FBAR_OBAR':
                    if len(date_info_dict['forecast_hours']) <= 1:
                        logger.warning("No span of forecast hours to plot, "
                                       +"given 1 forecast hour, skipping "
                                       +"lead_by_level plots")
                        make_lbl = False
                    else:
                        make_lbl = True
                else:
                    make_lbl = False
                del plot_info_dict['fcst_var_level']
                del plot_info_dict['obs_var_level']
                if make_lbl:
                    plot_lbl = p_lbl.LeadByLevel(logger,
                                                 job_input_dir,
                                                 job_DATA_dir,
                                                 model_info_dict,
                                                 date_info_dict,
                                                 plot_info_dict,
                                                 met_info_dict, logo_dir)
                    plot_lbl.make_lead_by_level()
    elif plot == 'date_by_level':
        import plot_date_by_level as p_dbl
        vert_profiles = [os.environ['vert_profile']]
        for dbl_info in list(itertools.product(valid_hrs, fhrs, vert_profiles)):
            date_info_dict['valid_hr_start'] = str(dbl_info[0])
            date_info_dict['valid_hr_end'] = str(dbl_info[0])
            date_info_dict['valid_hr_inc'] = '24'
            date_info_dict['forecast_hour'] = str(dbl_info[1])
            plot_info_dict['fcst_var_name'] = fcst_var_name
            plot_info_dict['obs_var_name'] = obs_var_name
            plot_info_dict['vert_profile'] = dbl_info[2]
            plot_info_dict['fcst_var_level'] = dbl_info[2]
            plot_info_dict['obs_var_level'] = dbl_info[2]
            for t in range(len(fcst_var_thresh_list)):
                plot_info_dict['fcst_var_thresh'] = fcst_var_thresh_list[t]
                plot_info_dict['obs_var_thresh'] = obs_var_thresh_list[t]
                job_DATA_image_name = plot_specs.get_savefig_name(
                    job_DATA_dir, plot_info_dict, date_info_dict
                )
                job_input_dir = make_plots_input_dir
                if not os.path.exists(job_DATA_image_name) \
                        and plot_info_dict['stat'] != 'FBAR_OBAR':
                    make_dbl = True
                else:
                    make_dbl = False
                del plot_info_dict['fcst_var_level']
                del plot_info_dict['obs_var_level']
                if make_dbl:
                    plot_dbl = p_dbl.DateByLevel(logger,
                                                 job_input_dir,
                                                 job_DATA_dir,
                                                 model_info_dict,
                                                 date_info_dict,
                                                 plot_info_dict,
                                                 met_info_dict, logo_dir)
                    plot_dbl.make_date_by_level()
    else:
        logger.error(plot+" not recognized")
        sys.exit(1)

print("END: "+os.path.basename(__file__))
