#!/bin/sh -xe
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------
## NCEP EMC GLOBAL MODEL VERIFICATION
##
## CONTRIBUTORS: Mallory Row, mallory.row@noaa.gov, NOAA/NWS/NCEP/EMC-VPPGB
## PURPOSE: Used to run the verif_global package in the Global Workflow.
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------

# Set information based on gfs_cyc
if [ $gfs_cyc = 1 ]; then
    export fcyc_list="$cyc"
    export vhr_list="$cyc"
    export cyc2run="$cyc"
elif [ $gfs_cyc = 2 ]; then
    export fcyc_list="00 12"
    export vhr_list="00 12"
    export cyc2run=00
elif [ $gfs_cyc = 4 ]; then
    export fcyc_list="00 06 12 18"
    export vhr_list="00 06 12 18"
    export cyc2run=00
else
    echo "EXIT ERROR: gfs_cyc must be 1, 2 or 4." 
    exit 1
fi

# Map the global workflow environment variables to EMC_verif-global variables
export RUN_GRID2GRID_STEP1=${RUN_GRID2GRID_STEP1:-NO}
export RUN_GRID2OBS_STEP1=${RUN_GRID2OBS_STEP1:-NO}
export RUN_PRECIP_STEP1=${RUN_PRECIP_STEP1:-NO}
export HOMEverif_global=${HOMEverif_global:-${HOMEgfs}/sorc/verif-global.fd}
## INPUT DATA SETTINGS
export model_list=${model:-$PSLOT}
export model_stat_dir_list=${model_stat_dir:-${NOSCRUB}/archive}
export model_file_format_list=${model_file_format:-"pgbf{lead?fmt=%2H}.${CDUMP}.{init?fmt=%Y%m%d%H}.grib2"}
export model_hpss_dir_list=${model_hpss_dir:-/NCEPDEV/$HPSS_PROJECT/1year/$USER/$machine/scratch}
export model_data_run_hpss=${get_data_from_hpss:-"NO"}
export hpss_walltime=${hpss_walltime:-10}
## DATE SETTINGS
export VDATE="${VDATE:-$(echo $($NDATE -${VRFYBACK_HRS} $CDATE) | cut -c1-8)}"
export start_date="$VDATE"
export end_date="$VDATE"
export make_met_data_by=${make_met_data_by:-VALID}
export plot_by="VALID"
## WEB SETTINGS
export SEND2WEB="NO"
export webhost="emcrzdm.ncep.noaa.gov"
export webhostid="$USER"
export webdir="/home/people/emc/www/htdocs/gmb/${webhostid}/METplus_${PSLOT}"
export img_quality="low"
## METPLUS SETTINGS
export MET_version="9.1"
export METplus_version="3.1"
export METplus_verbosity=${METplus_verbosity:-INFO}
export MET_verbosity=${MET_verbosity:-2}
export log_MET_output_to_METplus=${log_MET_output_to_METplus:-yes}
## DATA DIRECTIVE SETTINGS
export SENDARCH=${SENDARCH:-"YES"}
export SENDMETVIEWER=${SENDMETVIEWER:-"NO"}
export KEEPDATA=${KEEPDATA:-"NO"}
export SENDECF=${SENDECF:-"NO"}
export SENDCOM=${SENDCOM:-"NO"}
export SENDDBN=${SENDDBN:-"NO"}
export SENDDBN_NTC=${SENDDBN_NTC:-"NO"}
# GRID2GRID STEP 1
export g2g1_type_list=${g2g1_type_list:-"anom pres sfc"}
export g2g1_anom_truth_name=${g2g1_anom_truth_name:-"self_anl"}
export g2g1_anom_truth_file_format_list=${g2g1_anom_truth_file_format:-"pgbanl.${CDUMP}.{valid?fmt=%Y%m%d%H}.grib2"}
export g2g1_anom_fcyc_list=${fcyc_list}
export g2g1_anom_vhr_list=${vhr_list}
export g2g1_anom_fhr_min=${g2g1_anom_fhr_min:-$FHMIN_GFS}
export g2g1_anom_fhr_max=${g2g1_anom_fhr_max:-$FHMAX_GFS}
export g2g1_anom_grid=${g2g1_anom_grid:-"G002"}
export g2g1_anom_gather_by=${g2g1_anom_gather_by:-"VSDB"}
export g2g1_pres_truth_name=${g2g1_pres_truth_name:-"self_anl"}
export g2g1_pres_truth_file_format_list=${g2g1_pres_truth_file_format:-"pgbanl.${CDUMP}.{valid?fmt=%Y%m%d%H}.grib2"}
export g2g1_pres_fcyc_list=${fcyc_list}
export g2g1_pres_vhr_list=${vhr_list}
export g2g1_pres_fhr_min=${g2g1_pres_fhr_min:-$FHMIN_GFS}
export g2g1_pres_fhr_max=${g2g1_pres_fhr_max:-$FHMAX_GFS}
export g2g1_pres_grid=${g2g1_pres_grid:-"G002"}
export g2g1_pres_gather_by=${g2g1_pres_gather_by:-"VSDB"}
export g2g1_sfc_truth_name=${g2g1_sfc_truth_name:-"self_f00"}
export g2g1_sfc_truth_file_format_list=${g2g1_sfc_truth_file_format:-"pgbf00.${CDUMP}.{valid?fmt=%Y%m%d%H}.grib2"}
export g2g1_sfc_fcyc_list=${fcyc_list}
export g2g1_sfc_vhr_list=${vhr_list}
export g2g1_sfc_fhr_min=${g2g1_sfc_fhr_min:-$FHMIN_GFS}
export g2g1_sfc_fhr_max=${g2g1_sfc_fhr_max:-$FHMAX_GFS}
export g2g1_sfc_grid=${g2g1_sfc_grid:-"G002"}
export g2g1_sfc_gather_by=${g2g1_sfc_gather_by:-"VSDB"}
export g2g1_mv_database_name=${g2g1_mv_database_name:-"mv_${PSLOT}_grid2grid_metplus"}
export g2g1_mv_database_group=${g2g1_mv_database_group:-"NOAA-NCEP"}
export g2g1_mv_database_desc=${g2g1_mv_database_desc:-"Grid-to-grid METplus data for global workflow experiment ${PSLOT}"}
# GRID2OBS STEP 1
export g2o1_type_list=${g2o1_type_list:-"upper_air conus_sfc"}
export g2o1_upper_air_msg_type_list=${g2o1_upper_air_msg_type_list:-"ADPUPA"}
export g2o1_upper_air_fcyc_list=${fcyc_list}
export g2o1_upper_air_vhr_list=${g2o1_upper_air_vhr_list:-"00 06 12 18"}
export g2o1_upper_air_fhr_min=${g2o1_upper_air_fhr_min:-$FHMIN_GFS}
export g2o1_upper_air_fhr_max=${g2o1_upper_air_fhr_max:-$FHMAX_GFS}
export g2o1_upper_air_grid=${g2o1_upper_air_grid:-"G003"}
export g2o1_upper_air_gather_by=${g2o1_upper_air_gather_by:-"VSDB"}
export g2o1_conus_sfc_msg_type_list=${g2o1_conus_sfc_msg_type_list:-"ONLYSF ADPUPA"}
export g2o1_conus_sfc_fcyc_list=${fcyc_list}
export g2o1_conus_sfc_vhr_list=${g2o1_conus_sfc_vhr_list:-"00 03 06 09 12 15 18 21"}
export g2o1_conus_sfc_fhr_min=${g2o1_conus_sfc_fhr_min:-$FHMIN_GFS}
export g2o1_conus_sfc_fhr_max=${g2o1_cnous_sfc_fhr_max:-$FHMAX_GFS}
export g2o1_conus_sfc_grid=${g2o1_conus_sfc_grid:-"G104"}
export g2o1_conus_sfc_gather_by=${g2o1_conus_sfc_gather_by:-"VSDB"}
export g2o1_polar_sfc_msg_type_list=${g2o1_polar_sfc_msg_type_list:-"IABP"}
export g2o1_polar_sfc_fcyc_list=${fcyc_list}
export g2o1_polar_sfc_vhr_list=${g2o1_polar_sfc_vhr_list:-"00 03 06 09 12 15 18 21"}
export g2o1_polar_sfc_fhr_min=${g2o1_polar_sfc_fhr_min:-$FHMIN_GFS}
export g2o1_polar_sfc_fhr_max=${g2o1_polar_sfc_fhr_max:-$FHMAX_GFS}
export g2o1_polar_sfc_grid=${g2o1_polar_sfc_grid:-"G219"}
export g2o1_polar_sfc_gather_by=${g2o1_polar_sfc_gather_by:-"VSDB"}
export g2o1_prepbufr_data_run_hpss=${g2o1_prepbufr_data_run_hpss:-"NO"}
export g2o1_mv_database_name=${g2o1_mv_database_name:-"mv_${PSLOT}_grid2grid_metplus"}
export g2o1_mv_database_group=${g2o1_mv_database_group:-"NOAA-NCEP"}
export g2o1_mv_database_desc=${g2o1_mv_database_desc:-"Grid-to-obs METplus data for global workflow experiment ${PSLOT}"}
# PRECIP STEP 1
export precip1_type_list=${precip1_type_list:-"ccpa_accum24hr"}
export precip1_ccpa_accum24hr_model_bucket_list=${precip1_ccpa_accum24hr_model_bucket:-"06"}
export precip1_ccpa_accum24hr_model_var_list=${precip1_ccpa_accum24hr_model_var:-"APCP"}
export precip1_ccpa_accum24hr_model_file_format_list=${precip1_ccpa_accum24hr_model_file_format:-"pgbf{lead?fmt=%2H}.${CDUMP}.{init?fmt=%Y%m%d%H}.grib2"}
export precip1_ccpa_accum24hr_fcyc_list=${fcyc_list}
export precip1_ccpa_accum24hr_fhr_min=${precip1_ccpa_accum24hr_fhr_min:-$FHMIN_GFS}
export precip1_ccpa_accum24hr_fhr_max=${precip1_ccpa_accum24hr_fhr_max:-$FHMAX_GFS}
export precip1_ccpa_accum24hr_grid=${precip1_ccpa_accum24hr_grid:-"G211"}
export precip1_ccpa_accum24hr_gather_by=${precip1_ccpa_accum24hr_gather_by:-"VSDB"}
export precip1_obs_data_run_hpss=${precip1_obs_data_run_hpss:-"YES"}
export precip1_mv_database_name=${precip1_mv_database_name:-"mv_${PSLOT}_precip_metplus"}
export precip1_mv_database_group=${precip1_mv_database_group:-"NOAA-NCEP"}
export precip1_mv_database_desc=${precip1_mv_database_desc:-"Precip METplus data for global workflow experiment ${PSLOT}"}

echo

# Check forecast max hours, adjust if before experiment SDATE_GFS
export SDATE_GFS=${SDATE_GFS:-SDATE}
SDATE_GFS_YYYYMMDDHH=$(echo $SDATE_GFS | cut -c1-10)
g2g1_anom_check_vhour="${g2g1_anom_vhr_list: -2}"
g2g1_anom_fhr_max_idate="$($NDATE -${g2g1_anom_fhr_max} ${VDATE}${g2g1_anom_check_vhour})"
if [ $g2g1_anom_fhr_max_idate -le $SDATE_GFS_YYYYMMDDHH ] ; then
    export g2g1_anom_fhr_max="$(echo $($NHOUR ${VDATE}${g2g1_anom_check_vhour} $SDATE_GFS_YYYYMMDDHH))"
fi
g2g1_pres_check_vhour="${g2g1_pres_vhr_list: -2}"
g2g1_pres_fhr_max_idate="$($NDATE -${g2g1_pres_fhr_max} ${VDATE}${g2g1_pres_check_vhour})"
if [ $g2g1_pres_fhr_max_idate -le $SDATE_GFS_YYYYMMDDHH ] ; then
    export g2g1_pres_fhr_max="$(echo $($NHOUR ${VDATE}${g2g1_pres_check_vhour} $SDATE_GFS_YYYYMMDDHH))"
fi
g2g1_sfc_check_vhour="${g2g1_sfc_vhr_list: -2}"
g2g1_sfc_fhr_max_idate="$($NDATE -${g2g1_sfc_fhr_max} ${VDATE}${g2g1_sfc_check_vhour})"
if [ $g2g1_sfc_fhr_max_idate -le $SDATE_GFS_YYYYMMDDHH ] ; then
    export g2g1_sfc_fhr_max="$(echo $($NHOUR ${VDATE}${g2g1_sfc_check_vhour} $SDATE_GFS_YYYYMMDDHH))"
fi
g2o1_upper_air_check_vhour="${g2o1_upper_air_vhr_list: -2}"
g2o1_upper_air_fhr_max_idate="$($NDATE -${g2o1_upper_air_fhr_max} ${VDATE}${g2o1_upper_air_check_vhour})"
if [ $g2o1_upper_air_fhr_max_idate -le $SDATE_GFS_YYYYMMDDHH ] ; then
    export g2o1_upper_air_fhr_max="$(echo $($NHOUR ${VDATE}${g2o1_upper_air_check_vhour} $SDATE_GFS_YYYYMMDDHH))"
fi
g2o1_conus_sfc_check_vhour="${g2o1_conus_sfc_vhr_list: -2}"
g2o1_conus_sfc_fhr_max_idate="$($NDATE -${g2o1_conus_sfc_fhr_max} ${VDATE}${g2o1_conus_sfc_check_vhour})"
if [ $g2o1_conus_sfc_fhr_max_idate -le $SDATE_GFS_YYYYMMDDHH ] ; then
    export g2o1_conus_sfc_fhr_max="$(echo $($NHOUR ${VDATE}${g2o1_conus_sfc_check_vhour} $SDATE_GFS_YYYYMMDDHH))"
fi
g2o1_polar_sfc_check_vhour="${g2o1_polar_sfc_vhr_list: -2}"
g2o1_polar_sfc_fhr_max_idate="$($NDATE -${g2o1_polar_sfc_fhr_max} ${VDATE}${g2o1_polar_sfc_check_vhour})"
if [ $g2o1_polar_sfc_fhr_max_idate -le $SDATE_GFS_YYYYMMDDHH ] ; then
    export g2o1_polar_sfc_fhr_max="$(echo $($NHOUR ${VDATE}${g2o1_polar_sfc_check_vhour} $SDATE_GFS_YYYYMMDDHH))"
fi
precip1_ccpa_accum24hr_check_vhour="12"
precip1_ccpa_accum24hr_fhr_max_idate="$($NDATE -${precip1_ccpa_accum24hr_fhr_max} ${VDATE}${precip1_ccpa_accum24hr_check_vhour})"
if [ $precip1_ccpa_accum24hr_fhr_max_idate -le $SDATE_GFS_YYYYMMDDHH ] ; then
    export precip1_ccpa_accum24hr_fhr_max="$(echo $($NHOUR ${VDATE}${precip1_ccpa_accum24hr_check_vhour} $SDATE_GFS_YYYYMMDDHH))"
fi

echo

## Output set up
export pid=${pid:-$$}
export jobid=${job}.${pid}
export DATAROOT=${DATAROOT:-"$RUNDIR/$CDATE/$CDUMP/metp.${jobid}"}
export OUTPUTROOT=${DATAROOT}
export DATA=$OUTPUTROOT
mkdir -p $DATA
cd $DATA

## Get machine
python $HOMEverif_global/ush/get_machine.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Succesfully ran get_machine.py"
echo

if [ -s config.machine ]; then
    . $DATA/config.machine
    status=$?
    [[ $status -ne 0 ]] && exit $status
    [[ $status -eq 0 ]] && echo "Succesfully sourced config.machine"
fi

if [[ "$machine" =~ ^(HERA|ORION|S4|JET|WCOSS2)$ ]]; then
   echo
else
    echo "ERROR: $machine is not a supported machine"
    exit 1
fi

## Load modules and set machine specific paths
. $HOMEverif_global/ush/load_modules.sh
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Succesfully loaded modules"
echo

## Account and queues for machines
export ACCOUNT=${ACCOUNT:-"GFS-DEV"}
export QUEUE=${QUEUE:-"dev"}
export QUEUESHARED=${QUEUE_SHARED:-"dev_shared"}
export QUEUESERV=${QUEUE_SERVICE:-"dev_transfer"}
export PARTITION_BATCH=${PARTITION_BATCH:-""}

## Run settings for machines
export MPMD="YES"
export nproc=${npe_node_metp_gfs:-1}

## Set paths for verif_global, MET, and METplus
export HOMEverif_global=$HOMEverif_global
export PARMverif_global=$HOMEverif_global/parm
export FIXverif_global=$FIXgfs/fix_verif
export USHverif_global=$HOMEverif_global/ush
export UTILverif_global=$HOMEverif_global/util
export EXECverif_global=$HOMEverif_global/exec
export HOMEMET=$HOMEMET
export HOMEMETplus=$HOMEMETplus
export PARMMETplus=$HOMEMETplus/parm
export USHMETplus=$HOMEMETplus/ush
export PATH="${USHMETplus}:${PATH}"
export PYTHONPATH="${USHMETplus}:${PYTHONPATH}"

## Set machine and user specific directories
if [ $machine = "WCOSS2" ]; then
    export global_archive="/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/global/archive/model_data"
    export prepbufr_arch_dir="/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/global/archive/obs_data/prepbufr"
    export ccpa_24hr_arch_dir="/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/global/archive/obs_data/ccpa_accum24hr"
elif [ $machine = "HERA" ]; then
    export global_archive="/scratch1/NCEPDEV/global/Mallory.Row/archive"
    export prepbufr_arch_dir="/scratch1/NCEPDEV/global/Mallory.Row/prepbufr"
    export ccpa_24hr_arch_dir="/scratch1/NCEPDEV/global/Mallory.Row/obdata/ccpa_accum24hr"
elif [ $machine = "ORION" ]; then
    export global_archive="/work/noaa/ovp/mrow/archive"
    export prepbufr_arch_dir="/work/noaa/ovp/mrow/prepbufr"
    export ccpa_24hr_arch_dir="/work/noaa/ovp/mrow/obdata/ccpa_accum24hr"
elif [ $machine = "S4" ]; then
    export global_archive="/data/prod/glopara/MET_data/archive"
    export prepbufr_arch_dir="/data/prod/glopara/MET_data/prepbufr"
    export ccpa_24hr_arch_dir="/data/prod/glopara/MET_data/obdata/ccpa_accum24hr"
elif [ $machine = "JET" ]; then
    export global_archive="/lfs4/HFIP/hfv3gfs/Mallory.Row/archive"
    export prepbufr_arch_dir="/lfs4/HFIP/hfv3gfs/Mallory.Row/prepbufr"
    export ccpa_24hr_arch_dir="/lfs4/HFIP/hfv3gfs/Mallory.Row/obdata/ccpa_accum24hr"
fi

## Set operational directories
source ${HOMEverif_global}/versions/run.ver
export prepbufr_prod_upper_air_dir="/lfs/h1/ops/prod/com/obsproc/${obsproc_ver}"
export prepbufr_prod_conus_sfc_dir="/lfs/h1/ops/prod/com/obsproc/${obsproc_ver}"
export ccpa_24hr_prod_dir="/lfs/h1/ops/prod/com/verf_precip/${verf_precip_ver}"
## Some online sites
export iabp_ftp="http://iabp.apl.washington.edu/Data_Products/Daily_Full_Res_Data"

## Do checks on switches to run verification for
if [ $METPCASE = g2g1 ]; then
    RUN_GRID2OBS_STEP1=NO
    RUN_PRECIP_STEP1=NO
    emc_verif_switch_name="RUN_GRID2GRID_STEP1"
    export emc_verif_name="g2g1"
fi
if [ $METPCASE = g2o1 ]; then
    RUN_GRID2GRID_STEP1=NO
    RUN_PRECIP_STEP1=NO
    emc_verif_switch_name="RUN_GRID2OBS_STEP1"
    export emc_verif_name="g2o1"
fi
if [ $METPCASE = pcp1 ]; then
    RUN_GRID2GRID_STEP1=NO
    RUN_GRID2OBS_STEP1=NO
    emc_verif_switch_name="RUN_PRECIP_STEP1"
    export emc_verif_name="precip1"
fi
if [ ${start_date}${cyc2run} -lt $SDATE_GFS_YYYYMMDDHH ]; then
    RUN_GRID2GRID_STEP1=NO
    RUN_GRID2OBS_STEP1=NO
    RUN_PRECIP_STEP1=NO
fi
for fcyc in $fcyc_list; do
    if [ ${start_date}${fcyc} -lt $SDATE_GFS_YYYYMMDDHH ]; then
         RUN_GRID2GRID_STEP1=NO
         RUN_GRID2OBS_STEP1=NO
         RUN_PRECIP_STEP1=NO
    fi
done
for precip1_type in $precip1_type_list; do
    precip1_accum_length=$(echo $precip1_type | sed 's/[^0-9]*//g')
    precip_back_hours=$((VRFYBACK_HRS + precip1_accum_length))
    precip_check_date="$(echo $($NDATE -${precip_back_hours} $CDATE) | cut -c1-8)"
    if [ ${precip_check_date}${cyc2run} -lt $SDATE_GFS_YYYYMMDDHH ]; then
        RUN_PRECIP_STEP1=NO
    fi
    for fcyc in $fcyc_list; do
        if [ ${precip_check_date}${fcyc} -lt $SDATE_GFS_YYYYMMDDHH ]; then
            RUN_PRECIP_STEP1=NO
        fi
    done
done
RUN_METPCASE=${!emc_verif_switch_name}
export METPCASE_type_list=$(eval echo \${${emc_verif_name}_type_list})

## Get data for temporary archive directory for model_stat_dir_list
export DATAROOT=$OUTPUTROOT
export tmp_archive_dir=$OUTPUTROOT/tmp_archive
mkdir -p $tmp_archive_dir/$PSLOT
export model_dir_list=$tmp_archive_dir
cat >tmp_archive_dir_get_data.py <<END
import os
import datetime
def format_filler(unfilled_file_format, dt_valid_time, dt_init_time, str_lead):
    filled_file_format = ''
    format_opt_list = ['lead', 'valid', 'init', 'cycle']
    for filled_file_format_chunk in unfilled_file_format.split('/'):
        for format_opt in format_opt_list:
            nformat_opt = (
                filled_file_format_chunk.count('{'+format_opt+'?fmt=')
            )
            if nformat_opt > 0:
               format_opt_count = 1
               while format_opt_count <= nformat_opt:
                   format_opt_count_fmt = (
                       filled_file_format_chunk \
                       .partition('{'+format_opt+'?fmt=')[2] \
                       .partition('}')[0]
                   )
                   if format_opt == 'valid':
                       replace_format_opt_count = dt_valid_time.strftime(
                           format_opt_count_fmt
                       )
                   elif format_opt == 'lead':
                       if format_opt_count_fmt == '%1H':
                           if int(str_lead) < 10:
                               replace_format_opt_count = str_lead[1]
                           else:
                               replace_format_opt_count = str_lead
                       elif format_opt_count_fmt == '%2H':
                           replace_format_opt_count = str_lead.zfill(2)
                       elif format_opt_count_fmt == '%3H':
                           replace_format_opt_count = str_lead.zfill(3)
                       else:
                           replace_format_opt_count = str_lead
                   elif format_opt in ['init', 'cycle']:
                       replace_format_opt_count = dt_init_time.strftime(
                           format_opt_count_fmt
                       )
                   filled_file_format_chunk = (
                       filled_file_format_chunk.replace(
                           '{'+format_opt+'?fmt='
                           +format_opt_count_fmt+'}',
                           replace_format_opt_count
                       )
                   )
                   format_opt_count+=1
        filled_file_format = os.path.join(filled_file_format,
                                          filled_file_format_chunk)
    return filled_file_format
def link_files(tmp_file, ARCDIR_file, ROTDIR_file):
    if not os.path.exists(tmp_file):
        if os.path.exists(ARCDIR_file):
            os.system(os.environ['NLN']+' '+ARCDIR_file+' '+tmp_file)
        else:
            if os.path.exists(ROTDIR_file):
                os.system(os.environ['NLN']+' '+ROTDIR_file+' '+tmp_file)
PSLOT = os.environ['PSLOT']
tmp_archive_dir = os.environ['tmp_archive_dir']
VDATE = os.environ['VDATE']
METPCASE = os.environ['METPCASE']
emc_verif_name = os.environ['emc_verif_name']
METPCASE_type_list = os.environ['METPCASE_type_list'].split(' ')
for METPCASE_type in METPCASE_type_list:
    if METPCASE == 'pcp1':
        if METPCASE_type == 'ccpa_accum24hr':
            METPCASE_type_vhr_list = ['12']
        METPCASE_model_file_format = os.environ[emc_verif_name+'_'+METPCASE_type+'_model_file_format']
    else:
        METPCASE_type_vhr_list = os.environ[emc_verif_name+'_'+METPCASE_type+'_vhr_list'].split(' ')
        METPCASE_model_file_format = os.environ['model_file_format']
    if 'pgbq' in METPCASE_model_file_format:
        ROTDIR_fhr_file_format = os.path.join(os.environ['CDUMP']+'.{init?fmt=%Y%m%d}', '{init?fmt=%H}', 'atmos', os.environ['CDUMP']+'.t{init?fmt=%H}z.sfluxgrbf{lead?fmt=%3H}.grib2')
        ARCDIR_fhr_file_format = 'pgbq{lead?fmt=%2H}.'+os.environ['CDUMP']+'.{init?fmt=%Y%m%d%H}.grib2'
    elif 'pgbf' in METPCASE_model_file_format:
        ROTDIR_fhr_file_format = os.path.join(os.environ['CDUMP']+'.{init?fmt=%Y%m%d}', '{init?fmt=%H}', 'atmos', os.environ['CDUMP']+'.t{init?fmt=%H}z.pgrb2.1p00.f{lead?fmt=%3H}')
        ARCDIR_fhr_file_format = 'pgbf{lead?fmt=%2H}.'+os.environ['CDUMP']+'.{init?fmt=%Y%m%d%H}.grib2'
    METPCASE_type_fcyc_list = os.environ[emc_verif_name+'_'+METPCASE_type+'_fcyc_list'].split(' ')
    METPCASE_type_fhr_min = os.environ[emc_verif_name+'_'+METPCASE_type+'_fhr_min']
    METPCASE_type_fhr_max = os.environ[emc_verif_name+'_'+METPCASE_type+'_fhr_max']
    FHOUT_GFS = os.environ['FHOUT_GFS']
    for vhr in METPCASE_type_vhr_list:
        valid_time_dt = datetime.datetime.strptime(VDATE+vhr, '%Y%m%d%H')
        if METPCASE == 'g2g1':
            METPCASE_type_truth_name = os.environ[emc_verif_name+'_'+METPCASE_type+'_truth_name']
            if METPCASE_type_truth_name in ['self_anl', 'self_f00']:
                if METPCASE_type_truth_name == 'self_anl':
                    tmp_archive_anl_file = os.path.join(tmp_archive_dir, PSLOT, format_filler(os.environ[emc_verif_name+'_'+METPCASE_type+'_truth_file_format'], valid_time_dt, valid_time_dt, 'anl'))
                    tmp_archive_fhr00_file = os.path.join(tmp_archive_dir, PSLOT, format_filler(METPCASE_model_file_format, valid_time_dt, valid_time_dt, '00'))
                    ROTDIR_anl_file_format = os.path.join(os.environ['CDUMP']+'.{valid?fmt=%Y%m%d}', '{valid?fmt=%H}', 'atmos', os.environ['CDUMP']+'.t{valid?fmt=%H}z.pgrb2.1p00.anl')
                    ARCDIR_anl_file_format = 'pgbanl.'+os.environ['CDUMP']+'.{valid?fmt=%Y%m%d%H}.grib2'
                    if 'pgbq' in METPCASE_model_file_format:
                        ROTDIR_fhr00_file_format = os.path.join(os.environ['CDUMP']+'.{valid?fmt=%Y%m%d}', '{valid?fmt=%H}', 'atmos', os.environ['CDUMP']+'.t{valid?fmt=%H}z.sfluxgrbf000.grib2')
                        ARCDIR_fhr00_file_format = 'pgbq00.'+os.environ['CDUMP']+'.{valid?fmt=%Y%m%d%H}.grib2'
                    elif 'pgbf' in METPCASE_model_file_format:
                        ROTDIR_fhr00_file_format = os.path.join(os.environ['CDUMP']+'.{valid?fmt=%Y%m%d}', '{valid?fmt=%H}', 'atmos', os.environ['CDUMP']+'.t{valid?fmt=%H}z.pgrb2.1p00.f000')
                        ARCDIR_fhr00_file_format = 'pgbf00.'+os.environ['CDUMP']+'.{valid?fmt=%Y%m%d%H}.grib2'
                    ROTDIR_anl_file = os.path.join(os.environ['ROTDIR'], format_filler(ROTDIR_anl_file_format, valid_time_dt, valid_time_dt, 'anl'))
                    ROTDIR_fhr00_file = os.path.join(os.environ['ROTDIR'], format_filler(ROTDIR_fhr00_file_format, valid_time_dt, valid_time_dt, '00'))
                    ARCDIR_anl_file = os.path.join(os.environ['ARCDIR'], format_filler(ARCDIR_anl_file_format, valid_time_dt, valid_time_dt, 'anl'))
                    ARCDIR_fhr00_file = os.path.join(os.environ['ARCDIR'], format_filler(ARCDIR_fhr00_file_format, valid_time_dt, valid_time_dt, '00'))
                    link_files(tmp_archive_anl_file, ARCDIR_anl_file, ROTDIR_anl_file)
                    if not os.path.exists(tmp_archive_anl_file):
                        link_files(tmp_archive_fhr00_file, ARCDIR_fhr00_file, ROTDIR_fhr00_file)
                elif METPCASE_type_truth_name == 'self_f00':
                    tmp_archive_fhr00_file = os.path.join(tmp_archive_dir, PSLOT, format_filler(os.environ[emc_verif_name+'_'+METPCASE_type+'_truth_file_format'], valid_time_dt, valid_time_dt, '00'))
                    if 'pgbq' in os.environ[emc_verif_name+'_'+METPCASE_type+'_truth_file_format']:
                        ROTDIR_fhr00_file_format = os.path.join(os.environ['CDUMP']+'.{valid?fmt=%Y%m%d}', '{valid?fmt=%H}', 'atmos', os.environ['CDUMP']+'.t{valid?fmt=%H}z.sfluxgrbf000.grib2')
                        ARCDIR_fhr00_file_format = 'pgbq00.'+os.environ['CDUMP']+'.{valid?fmt=%Y%m%d%H}.grib2'
                    elif 'pgbf' in os.environ[emc_verif_name+'_'+METPCASE_type+'_truth_file_format']:
                        ROTDIR_fhr00_file_format = os.path.join(os.environ['CDUMP']+'.{valid?fmt=%Y%m%d}', '{valid?fmt=%H}', 'atmos', os.environ['CDUMP']+'.t{valid?fmt=%H}z.pgrb2.1p00.f000')
                        ARCDIR_fhr00_file_format = 'pgbf00.'+os.environ['CDUMP']+'.{valid?fmt=%Y%m%d%H}.grib2'
                    ROTDIR_fhr00_file = os.path.join(os.environ['ROTDIR'], format_filler(ROTDIR_fhr00_file_format, valid_time_dt, valid_time_dt, '00'))
                    ARCDIR_fhr00_file = os.path.join(os.environ['ARCDIR'], format_filler(ARCDIR_fhr00_file_format, valid_time_dt, valid_time_dt, '00'))
                    link_files(tmp_archive_fhr00_file, ARCDIR_fhr00_file, ROTDIR_fhr00_file)
        fhr = int(METPCASE_type_fhr_min)
        while fhr <= int(METPCASE_type_fhr_max):
            init_time_dt = valid_time_dt - datetime.timedelta(hours=int(fhr))
            if init_time_dt.strftime('%H').zfill(2) in METPCASE_type_fcyc_list:
                tmp_archive_fhr_file = os.path.join(tmp_archive_dir, PSLOT, format_filler(METPCASE_model_file_format, valid_time_dt, init_time_dt, str(fhr)))
                ROTDIR_fhr_file = os.path.join(os.environ['ROTDIR'], format_filler(ROTDIR_fhr_file_format, valid_time_dt, init_time_dt, str(fhr)))
                ARCDIR_fhr_file = os.path.join(os.environ['ARCDIR'], format_filler(ARCDIR_fhr_file_format, valid_time_dt, init_time_dt, str(fhr)))
                link_files(tmp_archive_fhr_file, ARCDIR_fhr_file, ROTDIR_fhr_file)
                if METPCASE == 'pcp1':
                    METPCASE_type_accum_length = METPCASE_type.split('accum')[1].replace('hr','')
                    METPCASE_type_model_bucket = os.environ[emc_verif_name+'_'+METPCASE_type+'_model_bucket']
                    fhr_in_accum_list = []
                    fhr_end = fhr
                    if METPCASE_type_model_bucket == 'continuous':
                        nfiles_in_accum = 2
                        fhr_in_accum_list.append(str(fhr_end))
                        fhr_start = fhr_end-int(METPCASE_type_accum_length)
                        if fhr_start > 0:
                            fhr_in_accum_list.append(str(fhr_start))
                    else:
                        nfiles_in_accum = int(METPCASE_type_accum_length)/int(METPCASE_type_model_bucket)
                        nf = 1
                        while nf <= nfiles_in_accum:
                            fhr_now = int(fhr_end)-((nf-1)*int(METPCASE_type_model_bucket))
                            if fhr_now >= 0:
                                fhr_in_accum_list.append(str(fhr_now))
                            nf+=1
                    for accum_fhr in fhr_in_accum_list:
                        tmp_archive_accum_fhr_file = os.path.join(tmp_archive_dir, PSLOT, format_filler(METPCASE_model_file_format, valid_time_dt, init_time_dt, accum_fhr))
                        ROTDIR_accum_fhr_file = os.path.join(os.environ['ROTDIR'], format_filler(ROTDIR_fhr_file_format, valid_time_dt, init_time_dt, accum_fhr))
                        ARCDIR_accum_fhr_file = os.path.join(os.environ['ARCDIR'], format_filler(ARCDIR_fhr_file_format, valid_time_dt, init_time_dt, accum_fhr))
                        link_files(tmp_archive_accum_fhr_file, ARCDIR_accum_fhr_file, ROTDIR_accum_fhr_file)
            fhr+=int(FHOUT_GFS)
END
python tmp_archive_dir_get_data.py

## Run METplus
echo "=============== RUNNING METPLUS ==============="
if [ $RUN_GRID2GRID_STEP1 = YES ] ; then
    echo
    echo "===== RUNNING GRID-TO-GRID STEP 1 VERIFICATION  ====="
    echo "===== creating partial sum data for grid-to-grid verifcation using METplus ====="
    export RUN="grid2grid_step1"
    $HOMEverif_global/scripts/exgrid2grid_step1.sh
fi

if [ $RUN_GRID2OBS_STEP1 = YES ] ; then
    echo
    echo "===== RUNNING GRID-TO-OBSERVATIONS STEP 1 VERIFICATION  ====="
    echo "===== creating partial sum data for grid-to-observations verifcation using METplus ====="
    export RUN="grid2obs_step1"
    $HOMEverif_global/scripts/exgrid2obs_step1.sh
fi

if [ $RUN_PRECIP_STEP1 = YES ] ; then
    echo
    echo "===== RUNNING PRECIPITATION STEP 1 VERIFICATION  ====="
    echo "===== creating partial sum data for precipitation verifcation using METplus ====="
    export RUN="precip_step1"
    $HOMEverif_global/scripts/exprecip_step1.sh
fi
