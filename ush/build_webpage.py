'''
Program Name: build_webpage.py
Contact(s): Mallory Row
Abstract: This is run at the end of all step2 scripts
          in scripts/.
          This creates a job card to:
              1) if needed, create website from
                 EMC_verif-global template (webpage/)
                 at specified user location on web server
              2) send images to web server
          It then submits to the transfer queue.
'''

import os
import datetime
import glob
import shutil
import verif_global_util as vfg_util

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
KEEPDATA = os.environ['KEEPDATA']
machine = os.environ['machine']
USHverif_global = os.environ['USHverif_global']
DATA = os.environ['DATA']
NET = os.environ['NET']
RUN = os.environ['RUN']
RUN_type = RUN.split('_')[0]
QUEUESERV = os.environ['QUEUESERV']
ACCOUNT = os.environ['ACCOUNT']
PARTITION_BATCH = os.environ['PARTITION_BATCH']
webhost = os.environ['webhost']
webhostid = os.environ['webhostid']
webdir = os.environ['webdir']
tar_archive_dir = os.environ['tar_archive_dir']

if RUN == 'fit2obs_plots':
    DATA = DATA.replace('/fit2obs_plots/data', '')
    webdir = webdir.replace(
        '/fits/horiz/'+os.environ['fit2obs_plots_expnlist'].split(' ')[1], ''
    )
    web_fits_dir = os.path.join(DATA, RUN, 'fit2obs', 'web', 'fits')
    nimages = 0
    for root, dirs, files in os.walk(web_fits_dir, topdown=False):
        nimages = nimages + len(glob.glob(os.path.join(root, '*.png')))
else:
    tar_files = glob.glob(
         os.path.join(tar_archive_dir, f"verif_global_{RUN}_*.tar")
    )
print("Webhost: "+webhost)
print("Webhost location: "+webdir)

# Set up job wall time information
web_walltime = '180'
walltime_seconds = datetime.timedelta(minutes=int(web_walltime)) \
        .total_seconds()
walltime = (datetime.datetime.min
           + datetime.timedelta(minutes=int(web_walltime))).time()

if RUN == 'fit2obs_plots':
    exp1 = os.environ['fit2obs_plots_expnlist'].split(' ')[0]
    exp2 = os.environ['fit2obs_plots_expnlist'].split(' ')[1]
    fit2obs_plots_dir = os.path.join(DATA, RUN)
    # Make globalvars.php files
    for stat in ['bias', 'rmse']:
        stat_globvars_filename = os.path.join(fit2obs_plots_dir,
                                              stat+'_globalvars.php')
        with open(stat_globvars_filename, 'a') as stat_globvars_file:
            stat_globvars_file.write("<?php include '../../globalvars.php';\n")
            if stat == 'rmse':
                stat_globvars_file.write("      $stat_title = 'Fit-to-Obs: "
                                         +stat.upper()+"';\n")
            else:
                stat_globvars_file.write("      $stat_title = 'Fit-to-Obs: "
                                         +stat.title()+"';\n")
            stat_globvars_file.write("      $ADPUPA_url = $image_location.'/"
                                     +stat+"_ADPUPA_VVV_LLL_SSS_DDD.png';\n")
            stat_globvars_file.write("      $ADPSFC_url = $image_location.'/"
                                     +stat+"_ADPSFC_VVV_LLL_SSS_DDD.png';\n")
            stat_globvars_file.write("      $SFCSHP_url = $image_location.'/"
                                     +stat+"_SFCSHP_VVV_LLL_SSS_DDD.png';\n")
            stat_globvars_file.write("      $AIRCFT_url = $image_location.'/"
                                     +stat+"_AIRCFT_VVV_LLL_SSS_DDD.png';\n")
            stat_globvars_file.write("      $AIRCAR_url = $image_location.'/"
                                     +stat+"_AIRCAR_VVV_LLL_SSS_DDD.png';\n")
            stat_globvars_file.write("      $horizontal_url = $image_location.'/"
                                     +stat+"_horizontal_VVV_LLL_SSS_DDD.png';\n")
            stat_globvars_file.write("      $vertical_url = $image_location.'/"
                                     +stat+"_vertical_VVV_LLL_SSS_DDD.png';\n")
            stat_globvars_file.write("      $Exp1_name = '"+exp1+"';\n")
            stat_globvars_file.write("      $Exp2_name = '"+exp2+"';\n")
            stat_globvars_file.write("      $Exp1_00_name = '"+exp1+"_00Z';\n")
            stat_globvars_file.write("      $Exp2_00_name = '"+exp2+"_00Z';\n")
            stat_globvars_file.write("      $Exp1_12_name = '"+exp1+"_12Z';\n")
            stat_globvars_file.write("      $Exp2_12_name = '"+exp2+"_12Z';\n")
            stat_globvars_file.write("      $Global_name = 'gl';\n")
            stat_globvars_file.write("      $NHem_name = 'nh';\n")
            stat_globvars_file.write("      $SHem_name = 'sh';\n")
            stat_globvars_file.write("      $Tropics_name = 'tr';\n")
            stat_globvars_file.write("      $NAmer_name = 'na';\n")
            stat_globvars_file.write("      $CONUS_name = 'us';\n")
            stat_globvars_file.write("      $Eur_name = 'eu';\n")
            stat_globvars_file.write("      $Asia_name = 'as';\n")
            stat_globvars_file.write("      $AllReg_name = 'all';\n")
            stat_globvars_file.write("      $Temp_name = 't';\n")
            stat_globvars_file.write("      $Pres_name = 'p';\n")
            stat_globvars_file.write("      $GeoHgt_name = 'z';\n")
            stat_globvars_file.write("      $SpefHum_name = 'q';\n")
            stat_globvars_file.write("      $VectWind_name = 'w';\n")
            stat_globvars_file.write("      $Tropo_name = 't';\n")
            stat_globvars_file.write("      $Strato_name = 's';\n")
            stat_globvars_file.write("      $P20_name = '20';\n")
            stat_globvars_file.write("      $P30_name = '30';\n")
            stat_globvars_file.write("      $P50_name = '50';\n")
            stat_globvars_file.write("      $P70_name = '70';\n")
            stat_globvars_file.write("      $P100_name = '100';\n")
            stat_globvars_file.write("      $P150_name = '150';\n")
            stat_globvars_file.write("      $P200_name = '200';\n")
            stat_globvars_file.write("      $P250_name = '250';\n")
            stat_globvars_file.write("      $P300_name = '300';\n")
            stat_globvars_file.write("      $P400_name = '400';\n")
            stat_globvars_file.write("      $P500_name = '500';\n")
            stat_globvars_file.write("      $P700_name = '700';\n")
            stat_globvars_file.write("      $P850_name = '850';\n")
            stat_globvars_file.write("      $P925_name = '925';\n")
            stat_globvars_file.write("      $P1000_name = '1000';\n")
            stat_globvars_file.write("      $Sfc_name = 'sfc';\n")
            stat_globvars_file.write("      $AnlGes_00_name = 'anl_ges_00Z';"
                                     +"\n")
            stat_globvars_file.write("      $AnlGes_12_name = 'anl_ges_12Z';"
                                     +"\n")
            stat_globvars_file.write("      $Fhr12_Fhr36_name = 'f12_f36';"
                                     +"\n")
            stat_globvars_file.write("      $Fhr24_Fhr48_name = 'f24_f48';"
                                     +"\n")
            stat_globvars_file.write("      $Fhr00Fhr06_name = 'f00af06';"
                                     +"\n")
            stat_globvars_file.write("      $Fhr12Fhr36_name = 'f12af36';"
                                     +"\n")
            stat_globvars_file.write("      $Fhr24Fhr48_name = 'f24af48';"
                                     +"\n")
            stat_globvars_file.write("      $Fhr00_name = 'f00';\n")
            stat_globvars_file.write("      $Fhr06_name = 'f06';\n")
            stat_globvars_file.write("      $Fhr12_name = 'f12';\n")
            stat_globvars_file.write("      $Fhr24_name = 'f24';\n")
            stat_globvars_file.write("      $Fhr36_name = 'f36';\n")
            stat_globvars_file.write("      $Fhr48_name = 'f48';\n")
            stat_globvars_file.write("      $Fhr60_name = 'f60';\n")
            stat_globvars_file.write("      $Fhr72_name = 'f72';\n")
            stat_globvars_file.write("      $Fhr84_name = 'f84';\n")
            stat_globvars_file.write("      $Fhr96_name = 'f96';\n")
            stat_globvars_file.write("      $Fhr108_name = 'f108';\n")
            stat_globvars_file.write("      $Fhr120_name = 'f120';\n")
            stat_globvars_file.write("      $LeadAll_name = 'all';\n")
            stat_globvars_file.write("      $LeadAllExp1_name = 'all-"
                                     +exp1+"';\n")
            stat_globvars_file.write("      $LeadAllExp2_name = 'all-"
                                     +exp2+"';\n")
            stat_globvars_file.write("      $LeadMean_name = 'timeout';?>\n")
            stat_globvars_file.write('<script type="text/javascript">var '
                                     +'exp1 = "<?= $Exp1_name ?>";</script>\n')
            stat_globvars_file.write('<script type="text/javascript">var '
                                     +'exp2 = "<?= $Exp2_name ?>";</script>\n')
            stat_globvars_file.write('<script type="text/javascript" '
                                     +'src="../function_vsdb.js"></script>\n')
    # Rename fit2obs images
    src_images_dir = os.path.join(DATA, RUN, 'fit2obs', 'web', 'fits')
    dest_images_dir = os.path.join(fit2obs_plots_dir, 'images')
    if not os.path.exists(dest_images_dir):
        os.makedirs(dest_images_dir)
    plot_type_list = [exp1, exp2, 'f00af06', 'f12af36', 'f24af48', 'timeout']
    region_list = ['gl', 'nh', 'sh', 'tr', 'na', 'us', 'eu', 'as', 'all']
    ob_type_dict = {
        'ADPUPA': 'adp',
        'ADPSFC': 'sfc',
        'SFCSHP': 'shp',
        'AIRCFT': 'acft',
        'AIRCAR': 'acar'
    }
    for plot_type in plot_type_list:
        src_plot_type_dir = os.path.join(src_images_dir, 'time', plot_type)
        for ob_type in list(ob_type_dict.keys()):
            if ob_type == 'ADPUPA':
                var_list = ['t', 'z', 'q', 'w']
                level_list = ['1000', '925', '850', '700', '500', '400',
                              '300', '250', '200', '150', '100',
                              '70', '50', '30', '20']
            elif ob_type in ['ADPSFC', 'SFCSHP']:
                var_list = ['t', 'p', 'q', 'w']
                level_list = ['sfc']
            elif ob_type in ['AIRCAR', 'AIRCFT']:
                var_list = ['t', 'w']
                level_list = ['1000', '700', '300']
            for var in var_list:
                for level in level_list:
                    if level == 'sfc':
                        level_original = ''
                    else:
                        level_original = level
                    for region in region_list:
                        rmse_src = os.path.join(
                            src_plot_type_dir,
                            var+level_original+'.'+region+'.'
                            +ob_type_dict[ob_type]+'.png'
                        )
                        rmse_dest = os.path.join(
                             dest_images_dir,
                            'rmse_'+ob_type+'_'+var+'_'+level+'_'
                            +plot_type+'_'+region+'.png'
                        )
                        bias_src = os.path.join(
                            src_plot_type_dir,
                            var+'b'+level_original+'.'+region+'.'
                            +ob_type_dict[ob_type]+'.png'
                        )
                        bias_dest = os.path.join(
                             dest_images_dir,
                            'bias_'+ob_type+'_'+var+'_'+level+'_'
                            +plot_type+'_'+region+'.png'
                        )
                        if os.path.exists(rmse_src):
                            shutil.copy(rmse_src, rmse_dest)
                        if os.path.exists(bias_src):
                            shutil.copy(bias_src, bias_dest)
    src_horizontal_dir = os.path.join(src_images_dir, 'horiz')
    plot_type_list = ['f00', 'f06', 'f12', 'f24', 'f36', 'f48',
                      'all-'+exp1, 'all-'+exp2]
    region_list = ['us', 'eu', 'as']
    var_list = ['t', 'z', 'q', 'w']
    level_list = ['925', '850', '700', '500', '200']
    for var in var_list:
        for level in level_list:
            for region in region_list:
                for plot_type in plot_type_list:
                    if plot_type == 'all-'+exp1:
                        src_horizontal_plot_type_dir  = os.path.join(
                            src_horizontal_dir, exp1
                        )
                    else:
                        src_horizontal_plot_type_dir  = os.path.join(
                            src_horizontal_dir, exp2
                        )
                    if 'all' in plot_type:
                        rmse_src = os.path.join(
                            src_horizontal_plot_type_dir,
                            var+level+'.all.'+region+'.rmse.png'
                        )
                        bias_src = os.path.join(
                            src_horizontal_plot_type_dir,
                            var+level+'.all.'+region+'.bias.png'
                        )
                    else:
                        rmse_src = os.path.join(
                            src_horizontal_plot_type_dir,
                            var+level+'.'+plot_type+'.'+region+'.rmse.png'
                        )
                        bias_src = os.path.join(
                            src_horizontal_plot_type_dir,
                            var+level+'.'+plot_type+'.'+region+'.bias.png'
                        )
                    rmse_dest = os.path.join(
                        dest_images_dir,
                        'rmse_horizontal_'+var+'_'+level+'_'
                        +plot_type+'_'+region+'.png'
                    )
                    bias_dest = os.path.join(
                        dest_images_dir,
                        'bias_horizontal_'+var+'_'+level+'_'
                        +plot_type+'_'+region+'.png'
                    )
                    if os.path.exists(rmse_src):
                        shutil.copy(rmse_src, rmse_dest)
                    if os.path.exists(bias_src):
                        shutil.copy(bias_src, bias_dest)
    src_timevrt_dir = os.path.join(src_images_dir, 'time', 'timevrt')
    src_vert_dir = os.path.join(src_images_dir, 'vert')
    plot_type_list = ['f00', 'f12', 'f24', 'f36', 'f48', 'f60', 'f72',
                      'f84', 'f96', 'f108', 'f120', exp1+'_00Z', exp2+'_00Z',
                      exp1+'_12Z', exp2+'_12Z','anl_ges_00Z', 'anl_ges_12Z',
                      'f12_f36', 'f24_f48']
    region_list = ['gl', 'nh', 'sh', 'tr', 'na', 'us', 'eu', 'as', 'all']
    level_list = ['t', 's']
    var_list = ['t', 'z', 'q', 'w']
    for var in var_list:
        for level in level_list:
            for region in region_list:
                for plot_type in plot_type_list:
                    if plot_type[0] == 'f' and len(plot_type.split('_')) == 1:
                        rmse_src = os.path.join(
                            src_timevrt_dir,
                            level+var+'.'+region+'.'+plot_type[1:]+'.png'
                        )
                        bias_src = os.path.join(
                            src_timevrt_dir,
                            level+var+'b.'+region+'.'+plot_type[1:]+'.png'
                        )
                    elif plot_type \
                            in [exp1+'_00Z', exp2+'_00Z', exp1+'_12Z',
                                exp2+'_12Z']:
                        exp = plot_type.split('_')[0]
                        hr = plot_type.split('_')[1]
                        if hr == '00Z':
                            hr_original = '0z'
                        else:
                            hr_original = hr.lower()
                        rmse_src = os.path.join(
                            src_vert_dir, exp,
                            level+var+'.'+hr_original+'.'+region+'.adp.png'
                        )
                        bias_src = os.path.join(
                            src_vert_dir, exp,
                            level+var+'.'+hr_original+'.'+region+'.adp.png'
                        )
                    elif plot_type \
                            in ['anl_ges_00Z', 'anl_ges_12Z', 'f12_f36',
                                'f24_f48']:
                        if 'anl' in plot_type:
                            rmse_src = os.path.join(
                                src_vert_dir, exp1+'-'+exp2,
                                level+var+'.f00.'
                                +plot_type.split('_')[2].lower()
                                +'.'+region+'.adp.png'
                            )
                            bias_src = os.path.join(
                                src_vert_dir, exp1+'-'+exp2,
                                level+var+'.f00.'
                                +plot_type.split('_')[2].lower()
                                +'.'+region+'.adp.png'
                            )
                        else:
                            rmse_src = os.path.join(
                                src_vert_dir, exp1+'-'+exp2,
                                level+var+'.'+plot_type.split('_')[0]
                                +'.'+region+'.adp.png'
                            )
                            bias_src = os.path.join(
                                src_vert_dir, exp1+'-'+exp2,
                                level+var+'.'+plot_type.split('_')[0]
                                +'.'+region+'.adp.png'
                            )
                    rmse_dest = os.path.join(
                        dest_images_dir,
                        'rmse_vertical_'+var+'_'+level+'_'
                        +plot_type+'_'+region+'.png'
                    )
                    bias_dest = os.path.join(
                        dest_images_dir,
                        'bias_vertical_'+var+'_'+level+'_'
                        +plot_type+'_'+region+'.png'
                    )
                    if os.path.exists(rmse_src):
                        shutil.copy(rmse_src, rmse_dest)
                    if os.path.exists(bias_src):
                        shutil.copy(bias_src, bias_dest)

# Create job card
web_job_filename = os.path.join(DATA, '..', 'jobs',
                                NET+'_'+RUN+'_web.sh')
if os.path.exists(web_job_filename):
    os.remove(web_job_filename)
with open(web_job_filename, 'a') as web_job_file:
        web_job_file.write('#!/bin/sh'+'\n')
        web_job_file.write('set -x'+'\n')
        if machine == 'WCOSS2':
            web_job_file.write('cd $PBS_O_WORKDIR\n')
        web_job_file.write('ssh -q -l '+webhostid+' '+webhost+' " ls -l '
                           +webdir+' "'+'\n')
        web_job_file.write('if [ $? -ne 0 ]; then'+'\n')
        web_job_file.write('    echo "Making directory '+webdir+'"'+'\n')
        web_job_file.write('    ssh -q -l '+webhostid+' '+webhost
                           +' "mkdir -p '+webdir+' "'+'\n')
        web_job_file.write('    sleep 30\n')
        web_job_file.write('    scp -rq '+os.path.join(USHverif_global,
                                                      'webpage/*')+'  '
                           +webhostid+'@'+webhost+':'+webdir+'/.'+'\n')
        web_job_file.write('fi'+'\n')
        web_job_file.write('\n')
        if RUN == 'fit2obs_plots':
            web_job_file.write('scp -r '+ os.path.join(DATA, RUN, 'images')
                               +' '+webhostid+'@'+webhost+':'
                               +os.path.join(webdir, RUN_type, '.')+'\n')
        else:
            for tar_file in tar_files:
                if RUN == "satellite_step2":
                    case_type = (
                        tar_file.rpartition("/")[2].replace(
                            "verif_global_satellite_step2_", ""
                        ).replace(
                            ".tar", ""
                        )
                    )
                    web_image_dir = os.path.join(
                        webdir, RUN_type, 'images', case_type
                    )
                else:
                    web_image_dir = os.path.join(
                        webdir, RUN_type, 'images'
                    )
                web_job_file.write('ssh -q -l '+webhostid+' '+webhost
                                   +' "mkdir -p "'+web_image_dir+'\n')
                web_job_file.write(f"scp "+tar_file
                                   +' '+webhostid+'@'+webhost+':'
                                   +web_image_dir+'\n')
                web_job_file.write('ssh -q -l '+webhostid+' '+webhost
                                   +' "cd '+web_image_dir+' ; tar -xvf '
                                   +tar_file.rpartition("/")[2]+' "'+'\n')
            if RUN == 'grid2grid_step2':
                scorecard_dir = os.path.join(DATA, RUN, 'scorecard')
                if os.path.exists(scorecard_dir):
                    web_job_file.write('scp -r '+scorecard_dir+'/*'
                                       +' '+webhostid+'@'+webhost+':'
                                       +os.path.join(webdir, 'scorecard',
                                                     '.')+'\n')
        if RUN == 'fit2obs_plots':
            for stat in ['bias', 'rmse']:
                web_job_file.write('scp -r '+os.path.join(DATA, RUN,
                                                          stat
                                                          +'_globalvars.php')
                                   +' '+webhostid+'@'+webhost+':'
                                   +os.path.join(webdir, RUN_type, stat, '.\n')
                )

# Submit job card
os.chmod(web_job_filename, 0o755)
web_job_output = os.path.join(DATA, '..', 'logs',
                              NET+'_'+RUN+'_web.out')
web_job_name = web_job_filename.rpartition('/')[2].replace('.sh', '')
print("Submitting "+web_job_filename+" to "+QUEUESERV)
print("Output sent to "+web_job_output)
if machine == 'WCOSS2':
    vfg_util.run_shell_command(
        ['qsub', '-l', 'walltime='+walltime.strftime('%H:%M:%S'),
         '-q', QUEUESERV, '-A', ACCOUNT, '-o', web_job_output,
         '-e', web_job_output, '-N', web_job_name,
         '-l', 'select=1:ncpus=1', web_job_filename]
    )
elif machine == 'HERA':
    vfg_util.run_shell_command(
        ['sbatch', '--ntasks=1', '--time='+walltime.strftime('%H:%M:%S'),
         '--partition='+QUEUESERV, '--account='+ACCOUNT,
         '--output='+web_job_output, '--job-name='+web_job_name,
         web_job_filename]
    )
elif machine == 'GAEAC6':
    CLUSTERS = os.environ['CLUSTERS']
    vfg_util.run_shell_command(
        ['sbatch', '--ntasks=1', '--time='+walltime.strftime('%H:%M:%S'),
         '--clusters='+CLUSTERS, '--account='+ACCOUNT,
         '--output='+web_job_output, '--job-name='+web_job_name,
         web_job_filename]
    )
elif machine in ["ORION", "HERCULES", "GAEAC6"]:
    if webhost == 'emcrzdm.ncep.noaa.gov':
        print("ERROR: Currently " + machine + " cannot connect to "+webhost)
    else:
        vfg_util.run_shell_command(
            ['sbatch', '--ntasks=1', '--time='+walltime.strftime('%H:%M:%S'),
             '--partition='+QUEUESERV, '--account='+ACCOUNT,
             '--output='+web_job_output, '--job-name='+web_job_name,
             web_job_filename]
        )

print("END: "+os.path.basename(__file__))
