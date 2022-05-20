import pandas as pd
import numpy as np
import os
import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Read in environment variables
machine = os.environ['machine']
DATA = os.environ['DATA']
NET = os.environ['NET']
RUN = os.environ['RUN']
USHverif_global = os.environ['USHverif_global']
model_list = os.environ['model_list'].split(' ')
start_date = os.environ['start_date']
end_date = os.environ['end_date']
plot_by = os.environ['plot_by']
anom_truth_name_list = os.environ['g2g2_anom_truth_name_list'].split(' ')
anom_fcyc_list = os.environ['g2g2_anom_fcyc_list'].split(' ')
anom_vhr_list = os.environ['g2g2_anom_vhr_list'].split(' ')
pres_truth_name_list = os.environ['g2g2_pres_truth_name_list'].split(' ')
pres_fcyc_list = os.environ['g2g2_pres_fcyc_list'].split(' ')
pres_vhr_list = os.environ['g2g2_pres_vhr_list'].split(' ')
SEND2WEB = os.environ['SEND2WEB']
webhost = os.environ['webhost']
webhostid = os.environ['webhostid']
webdir = os.environ['webdir']
QUEUESERV = os.environ['QUEUESERV']
ACCOUNT = os.environ['ACCOUNT']
PARTITION_BATCH = os.environ['PARTITION_BATCH']

# Set up job wall time information
web_walltime = '180'
walltime_seconds = datetime.timedelta(minutes=int(web_walltime)) \
        .total_seconds()
walltime = (datetime.datetime.min
           + datetime.timedelta(minutes=int(web_walltime))).time()

# Definitions
def get_day_value(filename, filename_cols, day):
    if os.path.exists(filename):
        nrow = sum(1 for line in open(filename))
        if nrow == 0:
            print(filename+" empty")
            day_value = np.nan
        else:
            filename_data = pd.read_csv(
                filename, sep=' ', header=None,
                names=filename_cols, dtype=str
            )
            filename_data_leads = (
                filename_data.loc[:][filename_cols[0]].tolist()
            )
            filename_data_vals = (
                filename_data.loc[:][filename_cols[1]].tolist()
            )
            day_hr_str = str(int(day)*24)+'0000'
            if day_hr_str in filename_data_leads:
                day_idx = filename_data_leads.index(
                    str(int(day)*24)+'0000'
                )
                if filename_data_vals[day_idx] != '--':
                    day_value = float(filename_data_vals[day_idx])
                else:
                    day_value = np.nan
            else:
                day_value = np.nan
    else:
        print(filename+" does not exist")
        day_value = np.nan
    return day_value

# Scorecard information
model1 = model_list[0]
model2 = model_list[1]
col_region_list = ['PNA', 'NHX', 'SHX', 'TRO']
col_day_list = ['1', '3', '5', '6', '8', '10']
row_stat_var_level_dict = {
   'acc': {
       'HGT': ['P250', 'P500', 'P700', 'P1000'],
       'UGRD_VGRD': ['P250', 'P500', 'P850'],
       'TMP': ['P250', 'P500', 'P850'],
       'PRMSL': ['Z0']
   },
   'rmse': {
       'HGT': ['P10', 'P20', 'P50', 'P100', 'P200', 'P500', 'P700', 'P850',
               'P1000'],
       'UGRD_VGRD': ['P10', 'P20', 'P50', 'P100', 'P200', 'P500', 'P700',
                     'P850', 'P1000'],
       'TMP': ['P10', 'P20', 'P50', 'P100', 'P200', 'P500', 'P700', 'P850',
               'P1000']
   },
   'bias': {
       'HGT': ['P10', 'P20', 'P50', 'P100', 'P200', 'P500', 'P700', 'P850',
               'P1000'],
       'UGRD_VGRD': ['P10', 'P20', 'P50', 'P100', 'P200', 'P500', 'P700',
                     'P850', 'P1000'],
       'TMP': ['P10', 'P20', 'P50', 'P100', 'P200', 'P500', 'P700', 'P850',
               'P1000']
   }
}
avg_file_cols = ['LEADS', 'VALS']
CI_file_cols = ['LEADS', 'CI_VALS']

# Make output directory
scorecard_dir = os.path.join(DATA, RUN, 'scorecard')
if not os.path.exists(scorecard_dir):
    os.makedirs(scorecard_dir)

# Set alpha values
## alpha1: 95% confidence level
## alpha2: 99% confidence level
## alpha3: 99.9% confidence level
start_date_dt = datetime.datetime.strptime(start_date, '%Y%m%d')
end_date_dt = datetime.datetime.strptime(end_date, '%Y%m%d')
ndays = (end_date_dt - start_date_dt).days + 1
if ndays >= 80:
    alpha1 = 1.960
    alpha2 = 2.576
    alpha3 = 3.291
elif ndays >= 40 and ndays < 80:
    alpha1=2.0
    alpha2=2.66
    alpha3=3.46
elif ndays >= 20 and ndays < 40:
    alpha1=2.042
    alpha2=2.75
    alpha3=3.646
elif ndays < 20:
    alpha1=2.228
    alpha2=3.169
    alpha3=4.587

# Make CSS file
scorecard_css_filename = os.path.join(scorecard_dir, 'scorecard.css')
with open(scorecard_css_filename,'w') as scorecard_css_file:
    scorecard_css_file.write('body {\n')
    scorecard_css_file.write('        margin : 0;\n')
    scorecard_css_file.write('        padding : 0;\n')
    scorecard_css_file.write('        background-color : #ffffff;\n')
    scorecard_css_file.write('        color : #000000;\n')
    scorecard_css_file.write('        }\n')
    scorecard_css_file.write('.first {\n')
    scorecard_css_file.write('        border-collapse: collapse;\n')
    scorecard_css_file.write('        border: 3px solid black;\n')
    scorecard_css_file.write('        }\n')
    scorecard_css_file.write('.second {\n')
    scorecard_css_file.write('        border-collapse: collapse\n')
    scorecard_css_file.write('        border: 1px dashed black;\n')
    scorecard_css_file.write('}\n')
    scorecard_css_file.write('.legend {\n')
    scorecard_css_file.write('        font-size: 0.75em;\n')
    scorecard_css_file.write('}\n')
    scorecard_css_file.write('#bold {\n')
    scorecard_css_file.write('        font: bold 1em Times;\n')
    scorecard_css_file.write('        }\n')
    scorecard_css_file.write('\n')
    scorecard_css_file.write('td {\n')
    scorecard_css_file.write('        border-collapse: collapse;\n')
    scorecard_css_file.write('        border: 2px solid black;\n')
    scorecard_css_file.write('}\n')
    scorecard_css_file.write('th {\n')
    scorecard_css_file.write('        border-collapse: collapse;\n')
    scorecard_css_file.write('        border: 1px solid black;\n')
    scorecard_css_file.write('        color: red;\n')
    scorecard_css_file.write('        font-family: Garamound;\n')
    scorecard_css_file.write('}\n')
    scorecard_css_file.write('#thside {\n')
    scorecard_css_file.write('        color: blue;\n')
    scorecard_css_file.write('        font-family: Garamound;\n')
    scorecard_css_file.write('}\n')

# Make legend
scorecard_legend_filename = os.path.join(scorecard_dir, 'legend.html')
with open(scorecard_legend_filename, 'w') as scorecard_legend_file:
    scorecard_legend_file.write('<link type="text/css" rel="stylesheet" '
                                +'href="scorecard.css"/>\n')
    scorecard_legend_file.write('<div>\n')
    scorecard_legend_file.write('    <table class="second" cellpadding="0.2">'
                                +'\n')
    scorecard_legend_file.write('    <tr>\n')
    scorecard_legend_file.write('       <th colspan=4>Scorecard Symbol '
                                +'Legend</th>\n')
    scorecard_legend_file.write('    </tr>\n')
    scorecard_legend_file.write('    <tr class="legend">\n')
    scorecard_legend_file.write('      <td><font color="#009120">&#9650;'
                                +'</font></td>\n')
    scorecard_legend_file.write('      <td>'+model2+' is better than '
                                +model1+' at the 99.9% significance '
                                +'level</td>\n')
    scorecard_legend_file.write('      <td><font color="#FF0000">&#9660;'
                                +'</font></td>\n')
    scorecard_legend_file.write('      <td>'+model2+' is worse than '
                                +model1+' at the 99.9% significance '
                                +'level\n')
    scorecard_legend_file.write('    </tr>\n')

    scorecard_legend_file.write('    <tr class="legend">\n')
    scorecard_legend_file.write('      <td><font color="#009120">&#9652;'
                                +'</font></td>\n')
    scorecard_legend_file.write('      <td>'+model2+' is better than '
                                +model1+' at the 99% significance '
                                +'level</td>\n')
    scorecard_legend_file.write('      <td><font color="#FF0000">&#9662;'
                                +'</font></td>\n')
    scorecard_legend_file.write('      <td>'+model2+' is worse than '
                                +model1+' at the 99% significance '
                                +'level</td>\n')
    scorecard_legend_file.write('    </tr>\n')
    scorecard_legend_file.write('    <tr class="legend">\n')
    scorecard_legend_file.write('      <td style="background:#A9F5A9"></td>\n')
    scorecard_legend_file.write('      <td>'+model2+' is better than '
                                +model1+' at the 95% significance '
                                +'level</td>\n')
    scorecard_legend_file.write('      <td style="background:#F5A9BC"></td>\n')
    scorecard_legend_file.write('      <td>'+model2+' is worse than '
                                +model1+' at the 95% significance '
                                +'level</td>\n')
    scorecard_legend_file.write('    </tr>\n')
    scorecard_legend_file.write('    <tr class="legend">\n')
    scorecard_legend_file.write('      <td style="background:#BDBDBD"></td>\n')
    scorecard_legend_file.write('      <td>No statistically significant '
                                +'difference between '+model2+' and '
                                +model1+'</td>\n')
    scorecard_legend_file.write('      <td style="background:#58ACFA"</td>\n')
    scorecard_legend_file.write('      <td>Not statistically relevant</td>\n')
    scorecard_legend_file.write('    </tr>\n')
    scorecard_legend_file.write('    <tr>\n')
    scorecard_legend_file.write('      <th colspan=4>Dates: '
                                +start_date+'-'+end_date+' </th>\n')
    scorecard_legend_file.write('    </tr>\n')

# Make column and row multi-index
pd_cols_list = []
for region in col_region_list:
    for day in col_day_list:
        pd_cols_list.append((region, day))
pd_cols = pd.MultiIndex.from_tuples(pd_cols_list)
pd_rows_list = []
for stat in list(row_stat_var_level_dict.keys()):
    var_level_dict = row_stat_var_level_dict[stat]
    for var in list(var_level_dict.keys()):
        for level in var_level_dict[var]:
            pd_rows_list.append((stat, var, level))
pd_rows = pd.MultiIndex.from_tuples(pd_rows_list)

# Make dataframe
scorecard_df = pd.DataFrame(np.nan, index=pd_rows, columns=pd_cols)

# Fill scorecard
row_count = 0
for pd_row in pd_rows_list:
    stat = pd_row[0]
    var = pd_row[1]
    level = pd_row[2]
    row_count+=1
    print("Row "+str(row_count)+": "+stat+" "+var+" "+level)
    if stat == 'acc':
        verif_type = 'anom'
        model1_truth_name = anom_truth_name_list[1].replace('self', model1)
        model2_truth_name = anom_truth_name_list[1].replace('self', model2)
        valid_hour_start = anom_vhr_list[0].zfill(2)
        valid_hour_end = anom_vhr_list[-1].zfill(2)
        init_hour_start = anom_fcyc_list[0].zfill(2)
        init_hour_end = anom_fcyc_list[-1].zfill(2)
        if var == 'UGRD_VGRD':
            line_type = 'VAL1L2'
        else:
            line_type = 'SAL1L2'
    else:
        verif_type = 'pres'
        model1_truth_name = pres_truth_name_list[1].replace('self', model1)
        model2_truth_name = pres_truth_name_list[1].replace('self', model2)
        valid_hour_start = pres_vhr_list[0].zfill(2)
        valid_hour_end = pres_vhr_list[-1].zfill(2)
        init_hour_start = pres_fcyc_list[0].zfill(2)
        init_hour_end = pres_fcyc_list[-1].zfill(2)
        if var == 'UGRD_VGRD':
            line_type = 'VL1L2'
        else:
            line_type = 'SL1L2'
    for pd_col in pd_cols_list:
        region = pd_col[0]
        day = pd_col[1]
        print("-- > Working on region: "+region+" day "+day)
        model1_avg_file = os.path.join(
            DATA, RUN, 'metplus_output', 'plot_by_'+plot_by, 'make_plots',
            line_type+'_'+var+'_'+region, RUN.split('_')[0], verif_type,
            'data', stat+'_'+model1+'_'+model1_truth_name+'_valid'
            +start_date+'to'+end_date+'_valid'+valid_hour_start+'00to'
            +valid_hour_end+'00Z_init'+init_hour_start+'00to'+init_hour_end
            +'00Z_fcst_lead_avgs_fcst'+var+level+'_obs'+var+level
            +'_vxmask'+region+'.txt'
        )
        print("Model 1 average file: "+model1_avg_file)
        model1_avg_value = get_day_value(model1_avg_file, avg_file_cols, day)
        print("Model 1 average value: "+str(model1_avg_value))
        model2_avg_file = os.path.join(
            DATA, RUN, 'metplus_output', 'plot_by_'+plot_by, 'make_plots',
            line_type+'_'+var+'_'+region, RUN.split('_')[0], verif_type,
            'data', stat+'_'+model2+'_'+model2_truth_name+'_valid'
            +start_date+'to'+end_date+'_valid'+valid_hour_start+'00to'
            +valid_hour_end+'00Z_init'+init_hour_start+'00to'+init_hour_end
            +'00Z_fcst_lead_avgs_fcst'+var+level+'_obs'+var+level
            +'_vxmask'+region+'.txt'
        )
        print("Model 2 average file: "+model2_avg_file)
        model2_avg_value = get_day_value(model2_avg_file, avg_file_cols, day)
        print("Model 2 average value: "+str(model2_avg_value))
        model2_CI_file = os.path.join(
            DATA, RUN, 'metplus_output', 'plot_by_'+plot_by, 'make_plots',
            line_type+'_'+var+'_'+region, RUN.split('_')[0], verif_type,
            'data', stat+'_'+model2+'_'+model2_truth_name+'_valid'
            +start_date+'to'+end_date+'_valid'+valid_hour_start+'00to'
            +valid_hour_end+'00Z_init'+init_hour_start+'00to'+init_hour_end
            +'00Z_fcst_lead_avgs_fcst'+var+level+'_obs'+var+level
            +'_vxmask'+region+'_CI_EMC.txt'
        )
        print("Model 2 CI file: "+model2_CI_file)
        model2_CI_value = get_day_value(model2_CI_file, CI_file_cols, day)
        print("Model 2 CI value: "+str(model2_CI_value))
        if not np.isnan(model1_avg_value) and not np.isnan(model2_avg_value) \
                and not np.isnan(model2_CI_value):
            if stat == 'bias':
                ds = np.abs(
                    model1_avg_value - model2_avg_value
                )/model2_CI_value
                sss = np.abs(model1_avg_value) - np.abs(model2_avg_value)
                if sss < 0:
                    ds = -1 * ds
            elif stat == 'rmse':
                ds = (model1_avg_value - model2_avg_value)/model2_CI_value
            else:
                ds = (model2_avg_value - model1_avg_value)/model2_CI_value
        else:
            ds = np.nan
        if not np.isnan(ds):
            ds95 = ds
            ds99 = ds * alpha1/alpha2
            ds999 = ds * alpha1/alpha3
            if ds999 >= 1:
                print(model2+" is better than "+model1+" at the "
                      +"99.9% significance level")
                symbol = '<td style="width:30px"><font color="#009120">&#9650;</font></td>'
            elif ds999 < 1 and ds99 >= 1:
                print(model2+" is better than "+model1+" at the "
                      +"99% significance level")
                symbol = '<td style="width:30px"><font color="#009120">&#9652;</font></td>'
            elif ds99 < 1 and ds95 >= 1:
                print(model2+" is better than "+model1+" at the "
                      +"95% significance level")
                symbol = '<td style="background:#A9F5A9;width:30px"></td>'
            elif ds95 > -1 and ds95 < 1:
                print("No statistically significant difference between "
                      +model2+" and "+model1)
                symbol = '<td style="background:#BDBDBD;width:30px"></td>'
            elif ds95 <= -1 and ds99 > -1:
                print(model2+" is worse than "+model1+" at the "
                      +"95% significance level")
                symbol = '<td style="background:#F5A9BC;width:30px"></td>'
            elif ds99 <= -1 and ds999 > -1:
                print(model2+" is worse than "+model1+" at the "
                      +"99% significance level")
                symbol =  '<td style="width:30px"><font color="#FF0000">&#9662;</font></td>'
            elif ds999 <= -1:
                print(model2+" is worse than "+model1+" at the "
                      +"99.9% significance level")
                symbol = '<td style="width:30px"><font color="#FF0000">&#9660;</font></td>'
        else:
            symbol = '<td style="width:30px">M</td>'
        if stat == 'acc' and region == 'TRO':
            symbol = '<td style="background:#58ACFA;width:30px"></td>'
        scorecard_df.loc[pd_row, (region, day)] = symbol

# Make header html
header_html_filename = os.path.join(scorecard_dir, 'header.html')
with open(header_html_filename, 'w') as header_html_file:
    header_html_file.write('<link type="text/css" rel="stylesheet" '
                           +'href="scorecard.css"/>\n')
    header_html_file.write('<table class="first" cellpadding="0.2">\n')
    header_html_file.write(' <tbody align="center">\n')
    header_html_file.write('  <!--Regions-->\n')
    header_html_file.write('  <tr>\n')
    header_html_file.write('   <th></th>\n')
    header_html_file.write('   <th></th>\n')
    header_html_file.write('   <th></th>\n')
    for region in col_region_list:
        if region == 'G002':
            region_header_name = 'Globe'
        elif region == 'NHX':
            region_header_name = 'N. Hemisphere'
        elif region == 'SHX':
            region_header_name = 'S. Hemisphere'
        elif region == 'TRO':
            region_header_name = 'Tropics'
        elif region == 'PNA':
            region_header_name = 'N. America'
        else:
            print("ERROR: Do not recognize region "+region)
            sys.exit(1)
        header_html_file.write('    <th colspan='+str(len(col_day_list))
                               +' >'+region_header_name+'</th>\n')
    header_html_file.write('  </tr>\n')
    header_html_file.write('  <!--Days-->\n')
    header_html_file.write('   <tr>\n')
    header_html_file.write('    <td style="width:150px"></td>\n')
    header_html_file.write('    <td style="width:75px"></td>\n')
    header_html_file.write('    <td style="width:75px"></td>\n')
    for region in col_region_list:
        for day in col_day_list:
            day_idx = col_day_list.index(day)
            if (day_idx % 2) == 0:
                 day_header_bg_color = '#FFFFFF'
            else:
                 day_header_bg_color = '#E6E6E6'
            header_html_file.write('    <td style="background:'
                                   +day_header_bg_color+';width:30px">Day '+day
                                   +'</td>\n')
    header_html_file.write('   </tr>\n')
    header_html_file.write(' </tbody>\n')
    header_html_file.write('</table>\n')

# Make scorecard html
scorecard_html_filename = os.path.join(scorecard_dir, 'scorecard.html')
with open(scorecard_html_filename, 'w') as scorecard_html_file:
    scorecard_html_file.write('<link type="text/css" rel="stylesheet" '
                              +'href="scorecard.css"/>\n')
    scorecard_html_file.write('<table class="first" cellpadding="0.2">\n')
    scorecard_html_file.write(' <tbody align="center">\n')
    for stat in list(row_stat_var_level_dict.keys()):
        stat_span = 0
        var_level_dict = row_stat_var_level_dict[stat]
        for var in list(var_level_dict.keys()):
            for level in var_level_dict[var]:
                stat_span+=1
        if stat == 'acc':
            stat_scorecard_name = 'Anomaly Correlation Coefficient'
        elif stat == 'rmse':
            stat_scorecard_name = 'RMSE'
        elif stat == 'bias':
            stat_scorecard_name = 'Bias'
        else:
            print("ERROR: Do not recognize stat "+stat)
            sys.exit(1)
        scorecard_html_file.write('   <tr>\n')
        scorecard_html_file.write('    <th id="thside" rowspan="'
                                  +str(stat_span)+'" style="width:150px">'
                                  +stat_scorecard_name+'</th>\n')
        for var in list(var_level_dict.keys()):
            var_span = str(len(var_level_dict[var]))
            if var == 'HGT':
                var_scorecard_name = 'Heights'
            elif var == 'PRMSL':
                var_scorecard_name = 'MSLP'
            elif var == 'TMP':
                var_scorecard_name = 'Temp'
            elif var == 'UGRD':
                var_scorecard_name = 'U-Wind'
            elif var == 'VGRD':
                var_scorecard_name = 'V-Wind'
            elif var == 'UGRD_VGRD':
                if stat == 'bias':
                    var_scorecard_name = 'Wind Speed'
                else:
                    var_scorecard_name = 'Vector Wind'
            else:
                print("ERROR: Do not recognize variable "+var)
                sys.exit(1)
            scorecard_html_file.write('     <td rowspan="'+var_span+'" '
                                      +'style="width:75px">'
                                      +var_scorecard_name+'</td>\n')
            for level in var_level_dict[var]:
                if level[0] == 'P':
                    level_scorecard_name = level[1:]+'hPa'
                elif var == 'PRMSL':
                    level_scorecard_name = 'MSL'
                else:
                    print("ERROR: Do not recognize level "+level)
                    sys.exit(1)
                scorecard_html_file.write('     <td style="width:75px">'
                                          +level_scorecard_name+'</td>\n')
                for pd_col in pd_cols_list:
                    region = pd_col[0]
                    day = pd_col[1]
                    scorecard_html_file.write('       '+scorecard_df.loc[
                                                  (stat, var, level),
                                                  (region, day)
                                              ]+'\n')
                scorecard_html_file.write('   </tr>\n')
                scorecard_html_file.write('\n')
                scorecard_html_file.write('   <tr>\n')
    scorecard_html_file.write(' </tbody>\n')
    scorecard_html_file.write('</table>\n')

# Send to website
if SEND2WEB == 'YES':
    print("Webhost: "+webhost)
    print("Webhost location: "+webdir)
    # Create job card
    web_job_filename = os.path.join(DATA, 'batch_jobs',
                                    NET+'_'+RUN
                                    +'_scorecard_web.sh')
    with open(web_job_filename, 'a') as web_job_file:
        web_job_file.write('#!/bin/sh'+'\n')
        if machine == 'WCOSS2':
            web_job_file.write('cd $PBS_O_WORKDIR\n')
        web_job_file.write('ssh -q -l '+webhostid+' '+webhost+' " ls -l '
                           +webdir+' "'+'\n')
        web_job_file.write('if [ $? -ne 0 ]; then'+'\n')
        web_job_file.write('    echo "Making directory '+webdir+'"'+'\n')
        web_job_file.write('    ssh -q -l '+webhostid+' '+webhost
                           +' "mkdir -p '+webdir+' "'+'\n')
        web_job_file.write('    sleep 30\n')
        web_job_file.write('    scp -q '+os.path.join(USHverif_global,
                                                      'webpage.tar')+'  '
                           +webhostid+'@'+webhost+':'+webdir+'/.'+'\n')
        web_job_file.write('    ssh -q -l '+webhostid+' '+webhost
                           +' "cd '+webdir+' ; tar -xvf webpage.tar "'+'\n')
        web_job_file.write('    ssh -q -l '+webhostid+' '+webhost
                           +' "rm '+os.path.join(webdir, 'webpage.tar')
                           +' "'+'\n')
        web_job_file.write('fi'+'\n')
        web_job_file.write('\n')
        web_job_file.write('scp -r '+os.path.join(DATA, RUN,
                                                  'scorecard', '*')
                           +' '+webhostid+'@'+webhost+':'
                           +os.path.join(webdir, 'scorecard', '.'))
    # Submit job card
    os.chmod(web_job_filename, 0o755)
    web_job_output = web_job_filename.replace('.sh', '.out')
    web_job_name = web_job_filename.rpartition('/')[2].replace('.sh', '')
    print("Submitting "+web_job_filename+" to "+QUEUESERV)
    print("Output sent to "+web_job_output)
    if machine == 'WCOSS2':
        os.system('qsub -V -l walltime='+walltime.strftime('%H:%M:%S')+' '
                  +'-q '+QUEUESERV+' -A '+ACCOUNT+' -o '+web_job_output+' '
                  +'-e '+web_job_output+' -N '+web_job_name+' '
                  +'-l select=1:ncpus=1 '+web_job_filename)
    elif machine in ['HERA', 'ORION', 'S4']:
        os.system('sbatch --ntasks=1 --time='+walltime.strftime('%H:%M:%S')+' '
                  +'--partition='+QUEUESERV+' --account='+ACCOUNT+' '
                  +'--output='+web_job_output+' '
                  +'--job-name='+web_job_name+' '+web_job_filename)

