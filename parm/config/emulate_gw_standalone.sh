#!/usr/bin/env bash

# LOOK HERE!!
###################SET YOUR ACCOUNT########################
#SBATCH --account=gfs-cpu
##########################################################

#SBATCH --job-name=metp
#SBATCH --output=metp.out.%j
### Set time longer for G2O
#SBATCH --time=01:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --clusters=c6
#SBATCH --partition=batch
#SBATCH --qos=normal

set -eux

# LOOK HERE!!
##############EDIT THIS SECTION######################
# Set a base working directory.  Subdirectories for each job will be created under this.
export DATAROOT=/gpfs/f6/drsa-precip3/world-shared/${USER}/tmp_metp
# Set the root path to the verif-global package
export HOMEverif_global=/gpfs/f6/drsa-precip3/world-shared/${USER}/EMC_verif-global
export HOMEverif_global=/gpfs/f6/drsa-precip3/world-shared/${USER}/Sat1_PR
# Change COMROOT to the appropriate location
export COMROOT=/gpfs/f6/drsa-precip3/world-shared/${USER}/para_KEEP/COMROOT
# Change PSLOT to the name of your experiment
export PSLOT=gfs_dev
# Set the start and end date of the experiment's GFS cycles
export SDATE_GFS=2024111600
export EDATE_GFS=2024112118
# Set the frequency at which the GFS cycles were run
export INTERVAL_GFS=6
# Set the verification date and cycle of interest
export PDY=20241121
# cyc specifies the last forecast init time to use. 
# If cyc=18 and if INTERVAL_GFS=6, then forecasts inits 0, 6, 12, and 18Z are used
export cyc=18
# Set just one of these at a time to "YES":
export RUN_GRID2GRID_STEP1=NO
export RUN_GRID2OBS_STEP1=NO
export RUN_PRECIP_STEP1=NO   # Note that you need 30 hours of PGB data to run precip step 1
export RUN_SATELLITE_STEP1=YES
# Minimum and maximum forecast hours to verify
export FHMIN_GFS=0
export FHMAX_GFS=120
# Set the machine name
# NOTE for future update - should call "~/ush/get_machine.py" to get
#                        - the definition of $machine for different
#                        - platforms.  Note the output $machine 
#                        - are in capital case, this may have a conflict
#                        - in "export model_hpss_dir_list" which are
#                        - supposed to be the small case
export machine=gaeac6
# Set the location of your online archive
export ARCDIR=/gpfs/f6/ira-sti/world-shared/${USER}/KEEP_archive/${PSLOT}
# NOTE: the location of the statistic files will be one directory up from ARCDIR
#       then appended by /metplus_data/by_VSDB/
#       followed by the validation type (e.g. grid2grid, grid2obs, precip)
#       validation subtype (e.g. pres, sfc, upper_air, conus_sfc, ccpa_accum24hr)
#       then /${cyc}z/${model}/${model}_${PDY}.stat
#
# Whether to keep the temporary working directory or not
export KEEPDATA=YES
##################DO NOT EDIT BELOW THIS LINE######################

# Load the needed modules for METplus
module use /autofs/ncrc-svm1_proj/epic/c6/spack-stack/spack-stack-1.9.1/envs/emc-gv-intel-2023.2.0/install/modulefiles/Core
module load stack-intel
module load stack-cray-mpich
module load stack-python
module load metplus/6.0.0
module load met/12.0.1
module load prod_util/2.1.1
module load wgrib2
module load grib-util
if [[ 1 == 2 && "${RUN_SATELLITE_STEP1}" == "YES" ]]; then
    module load Core/24.11
    module load imagemagick/7.1.1-29
    module load nco/5.2.4
    module swap python/3.11.7 python/3.11
fi

# Set some workflow environment variables
export jobid=$$
export pid=$$
export pgmout="OUTPUT.${pid}"
export pgmerr=errfile
export pgm=metplus
export RUN=gfs
export NET=gfs
export envir=prod
export RUN_ENVIR=emc

# Build the ROTDIR path
export ROTDIR=${COMROOT}/${PSLOT}

# Create and navigate to a temporary working directory in the current directory
export DATA=${DATAROOT}/met.${jobid}
mkdir -p "${DATA}"
cd "${DATA}" || exit 1

# Link in fix files
export FIXgfs=${DATA}
# Ho-Chun - Add support for multiple platforms originated from ~/ush/set_up_verif_global.sh
#         - can not set machine in captial case now because of "export model_hpss_dir_list="
#         - use small case machine in ~/ush/run_verif_global_in_global_workflow.sh
host_machine=$(echo $machine | tr '[a-z]' '[A-Z]')
## Set machine specific fix directory
if [ $host_machine = "WCOSS2" ]; then
    ln -sf /lfs/h2/emc/global/noscrub/emc.global/FIX/fix/verif/20220805 "${FIXgfs}/verif"
elif [ $host_machine = "HERA" ]; then
    ln -sf /scratch1/NCEPDEV/global/glopara/fix/verif/20220805 "${FIXgfs}/verif"
elif [ $host_machine = "ORION" -o $host_machine = "HERCULES" ]; then
    ln -sf /work/noaa/global/glopara/fix/verif/20220805 "${FIXgfs}/verif"
elif [ $host_machine = "S4" ]; then
    ln -sf /data/prod/glopara/fix/verif/20220805 "${FIXgfs}/verif"
elif [ $host_machine = "JET" ]; then
    ln -sf /lfs4/HFIP/hfv3gfs/glopara/git/fv3gfs/fix/verif/20220805 "${FIXgfs}/verif"
elif [ $host_machine = "GAEAC5" ]; then
    ln -sf /gpfs/f5/nggps_emc/world-shared/role.glopara/FIX/fix/verif/20220805 "${FIXgfs}/verif"
elif [ $host_machine = "GAEAC6" ]; then
    ln -sf /gpfs/f6/drsa-precip3/world-shared/role.glopara/fix/verif/20220805 "${FIXgfs}/verif"
fi

# Check if more than one verification type is set to YES and exit if so
count=0
if [[ "${RUN_GRID2GRID_STEP1}" == "YES" ]]; then
	count=$((count + 1))
fi
if [[ "${RUN_GRID2OBS_STEP1}" == "YES" ]]; then
	count=$((count + 1))
fi
if [[ "${RUN_PRECIP_STEP1}" == "YES" ]]; then
	count=$((count + 1))
fi
if [[ "${RUN_SATELLITE_STEP1}" == "YES" ]]; then
	count=$((count + 1))
fi
if [[ ${count} -ne 1 ]]; then
	echo "Error: Exactly one verification type must be selected. Set only one of RUN_GRID2GRID_STEP1, RUN_GRID2OBS_STEP1, RUN_PRECIP_STEP1, or RUN_SATELLITE_STEP1 to YES."
	exit 1
fi

# Set the METPCASE based on the type of verification to be done
if [[ "${RUN_GRID2GRID_STEP1}" == "YES" ]]; then
	export METPCASE=g2g1
elif [[ "${RUN_GRID2OBS_STEP1}" == "YES" ]]; then
	export METPCASE=g2o1
elif [[ "${RUN_PRECIP_STEP1}" == "YES" ]]; then
	export METPCASE=pcp1
elif [[ "${RUN_SATELLITE_STEP1}" == "YES" ]]; then
        # reset cyc for SATELLITE where cyc=00 is the default
        # export cyc=00      
        # export PDY=20241123
	export METPCASE=sat1
fi

################################################
# Set the variables normally set in config.metp
echo "BEGIN: config.metp"

export ntasks=1
export tasks_per_node=1
export memory="80G"

export nproc=${tasks_per_node:-1}

#----------------------------------------------------------
# METplus: Verify grid-to-grid, grid-to-obs, precipitation options
#----------------------------------------------------------
## EMC_VERIF_GLOBAL SETTINGS
export VERIF_GLOBALSH=${HOMEverif_global}/ush/run_verif_global_in_global_workflow.sh
## INPUT DATA SETTINGS
export model=gfs
export model_file_format="pgbf{lead?fmt=%2H}.${RUN}.{init?fmt=%Y%m%d%H}.grib2"
### DBH Note -- I don't think this is needed for this script
##export model_hpss_dir=${ATARDIR}/..
export model_dir=${ARCDIR}
export get_data_from_hpss="NO"
export hpss_walltime="10"
## OUTPUT SETTINGS
export model_stat_dir=${ARCDIR}/..
export make_met_data_by="VALID"
export SENDMETVIEWER="NO"
## DATE SETTINGS
export VRFYBACK_HRS="0"
## METPLUS SETTINGS
export METplus_verbosity="INFO"
export MET_verbosity="2"
export log_MET_output_to_METplus="yes"
# GRID-TO-GRID STEP 1: gfsmetpg2g1
export g2g1_type_list="anom pres sfc"
export g2g1_anom_truth_name="self_anl"
export g2g1_anom_truth_file_format="pgbanl.${RUN}.{valid?fmt=%Y%m%d%H}.grib2"
export g2g1_anom_fhr_min=${FHMIN_GFS}
export g2g1_anom_fhr_max=${FHMAX_GFS}
export g2g1_anom_grid="G002"
export g2g1_anom_gather_by="VALID"
export g2g1_pres_truth_name="self_anl"
export g2g1_pres_truth_file_format="pgbanl.${RUN}.{valid?fmt=%Y%m%d%H}.grib2"
export g2g1_pres_fhr_min=${FHMIN_GFS}
export g2g1_pres_fhr_max=${FHMAX_GFS}
export g2g1_pres_grid="G002"
export g2g1_pres_gather_by="VALID"
export g2g1_sfc_truth_name="self_f00"
export g2g1_sfc_truth_file_format="pgbf00.${RUN}.{valid?fmt=%Y%m%d%H}.grib2"
export g2g1_sfc_fhr_min=${FHMIN_GFS}
export g2g1_sfc_fhr_max=${FHMAX_GFS}
export g2g1_sfc_grid="G002"
export g2g1_sfc_gather_by="VALID"
export g2g1_mv_database_name="mv_${PSLOT}_grid2grid_metplus"
export g2g1_mv_database_group="NOAA NCEP"
export g2g1_mv_database_desc="Grid-to-grid METplus data for global workflow experiment ${PSLOT}"
# GRID-TO-OBS STEP 1: gfsmetpg2o1
export g2o1_type_list="upper_air conus_sfc"
export g2o1_upper_air_msg_type_list="ADPUPA"
export g2o1_upper_air_vhr_list="00 06 12 18"
export g2o1_upper_air_fhr_min=${FHMIN_GFS}
export g2o1_upper_air_fhr_max="240"
export g2o1_upper_air_grid="G003"
export g2o1_upper_air_gather_by="VALID"
export g2o1_conus_sfc_msg_type_list="ONLYSF ADPUPA"
export g2o1_conus_sfc_vhr_list="00 03 06 09 12 15 18 21"
export g2o1_conus_sfc_fhr_min=${FHMIN_GFS}
export g2o1_conus_sfc_fhr_max="240"
export g2o1_conus_sfc_grid="G104"
export g2o1_conus_sfc_gather_by="VALID"
export g2o1_polar_sfc_msg_type_list="IABP"
export g2o1_polar_sfc_vhr_list="00 03 06 09 12 15 18 21"
export g2o1_polar_sfc_fhr_min=${FHMIN_GFS}
export g2o1_polar_sfc_fhr_max="240"
export g2o1_polar_sfc_grid="G219"
export g2o1_polar_sfc_gather_by="VALID"
export g2o1_prepbufr_data_run_hpss="NO"
export g2o1_mv_database_name="mv_${PSLOT}_grid2obs_metplus"
export g2o1_mv_database_group="NOAA NCEP"
export g2o1_mv_database_desc="Grid-to-obs METplus data for global workflow experiment ${PSLOT}"
# PRECIP STEP 1: gfsmetppcp1
export precip1_type_list="ccpa_accum24hr"
export precip1_ccpa_accum24hr_model_bucket="06"
export precip1_ccpa_accum24hr_model_var="APCP"
export precip1_ccpa_accum24hr_model_file_format="pgbf{lead?fmt=%2H}.${RUN}.{init?fmt=%Y%m%d%H}.grib2"
# If no forecast files are missing, precip1_ccpa_accum24hr_fhr_min="24" and
# precip1_ccpa_accum24hr_fhr_max="XXX" (XXX = the longest forecast hour)
export precip1_ccpa_accum24hr_fhr_min="24"
export precip1_ccpa_accum24hr_fhr_max="384"
export precip1_ccpa_accum24hr_grid="G211"
export precip1_ccpa_accum24hr_gather_by="VALID"
export precip1_obs_data_run_hpss="NO"
export precip1_mv_database_name="mv_${PSLOT}_precip_metplus"
export precip1_mv_database_group="NOAA NCEP"
export precip1_mv_database_desc="Precip METplus data for global workflow experiment ${PSLOT}"
# SATELLITE STEP 1: gfsmetpsat1
# First check available observation file in $sat1_obs_dir defined below
#    or ghrsst_ospo_geopolar_anl in https://www.ncei.noaa.gov/data/oceans/ghrsst/L4/GLOB/OSPO/Geo_Polar_Blended/YYYY/JDAY
#       ghrsst_ncei_avhrr_anl    in https://www.ncei.noaa.gov/data/oceans/ghrsst/L4/GLOB/NCEI/AVHRR_OI/YYYY/JDAY
# export sat1_type_list="ghrsst_ncei_avhrr_anl ghrsst_ospo_geopolar_anl"
export sat1_type_list="ghrsst_ospo_geopolar_anl"
# Overwrite fcyc_list in VERIF_GLOBALSH and use only nit = 00 and fhr_list='24, 48, 72, 96, 120, 144, 168'
export sat1_ghrsst_ncei_avhrr_anl_fcyc_list="00"
export sat1_ghrsst_ncei_avhrr_anl_fhr_min=${FHMIN_GFS}
export sat1_ghrsst_ncei_avhrr_anl_fhr_max="168"
export sat1_ghrsst_ncei_avhrr_anl_grid="G219"
export sat1_ghrsst_ncei_avhrr_anl_gather_by="VALID"
export sat1_ghrsst_ncei_avhrr_anl_sea_ice_thresh="0.15"
# Overwrite fcyc_list in VERIF_GLOBALSH and use only nit = 00 and fhr_list='24, 48, 72, 96, 120, 144, 168'
export sat1_ghrsst_ospo_geopolar_anl_fcyc_list="00"
export sat1_ghrsst_ospo_geopolar_anl_fhr_min=${FHMIN_GFS}
export sat1_ghrsst_ospo_geopolar_anl_fhr_max="168"
export sat1_ghrsst_ospo_geopolar_anl_grid="G219"
export sat1_ghrsst_ospo_geopolar_anl_gather_by="VALID"
export sat1_ghrsst_ospo_geopolar_anl_sea_ice_thresh="0.15"
export sat1_mv_database_name="mv_${PSLOT}_satellite_metplus_TEST"
export sat1_mv_database_group="NOAA NCEP"
export sat1_mv_database_desc="Satellite METplus data for global workflow experiment ${PSLOT}"
export sat1_obs_dir="/gpfs/f6/drsa-precip3/world-shared/Ho-Chun.Huang/obs_archive/"

echo "END: config.metp"
#######################################################

###############################################################
## Abstract:
## Inline METplus verification and diagnostics driver script
## HOMEgfs   : /full/path/to/workflow
## EXPDIR : /full/path/to/config/files
## CDATE  : current analysis date (YYYYMMDDHH)
## PDY    : current date (YYYYMMDD)
## RUN    : cycle name (gdas / gfs)
## cyc    : current cycle (HH)
## SDATE_GFS  : first date of GFS cycle (YYYYMMDDHHMM)
## METPCASE : METplus verification use case (g2g1 | g2o1 | pcp1)
###############################################################

VDATE=$(date --utc +%Y%m%d%H -d "${PDY} ${cyc} - ${VRFYBACK_HRS} hours")
export VDATE=${VDATE:0:8}

##### Declare the declare_from_tmpl function
function declare_from_tmpl() {
    set +x
    local opts="-g"
    local OPTIND=1
    while getopts "rx" option; do
        opts="${opts}${option}"
    done
    shift $((OPTIND-1))

    for input in "$@"; do
        IFS=':' read -ra args <<< "${input}"
        local com_var="${args[0]}"
        local template
        local value
        if (( ${#args[@]} > 1 )); then
            template="${args[1]}"
        else
            template="${com_var}_TMPL"
        fi
        if [[ ! -v "${template}" ]]; then
            echo "FATAL ERROR in declare_from_tmpl: Requested template ${template} not defined!"
            exit 2
        fi
        value=$(echo "${!template}" | envsubst)
        declare ${opts} "${com_var}"="${value}"
        echo "declare_from_tmpl :: ${com_var}=${value}"
    done
    set -x
}

# Set the template to be ued for verif-global COM
COM_BASE='${ROTDIR}/${RUN}.${YMD}/${HH}/${MEMDIR}'
declare -rx COM_ATMOS_GRIB_TMPL=${COM_BASE}'/products/atmos/grib2'
declare -rx COM_ATMOS_GRIB_GRID_TMPL=${COM_ATMOS_GRIB_TMPL}'/${GRID}'

# Since this is currently a one-element list, shellcheck things we would rather run this as a command
# shellcheck disable=SC2041
for grid in '1p00'; do
  prod_dir="COM_ATMOS_GRIB_${grid}"
  GRID=${grid} YMD=${PDY} HH=${cyc} declare_from_tmpl -rx "${prod_dir}:COM_ATMOS_GRIB_GRID_TMPL"
done

# TODO: If none of these are on, why are we running this job?
if [[ "${RUN_GRID2GRID_STEP1}" == "YES" || "${RUN_GRID2OBS_STEP1}" == "YES" || "${RUN_PRECIP_STEP1}" == "YES" || "${RUN_SATELLITE_STEP1}" == "YES" ]]; then
    bash -x "${VERIF_GLOBALSH}"
    err=$?
    if [[ ${err} -ne 0 ]]; 
        then exit "${err}"
    fi
fi

if [[ ${KEEPDATA:-"NO"} = "NO" ]] ; then rm -rf "${DATAROOT}" ; fi  # TODO: This should be $DATA
