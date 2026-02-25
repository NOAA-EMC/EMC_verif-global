#!/bin/sh -xe
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------
## NCEP EMC GLOBAL MODEL VERIFICATION
##
## CONTRIBUTORS: Mallory Row, mallory.row@noaa.gov, NOAA/NWS/NCEP/EMC-VPPGB
## PURPOSE: Set up environment based on user configurations
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------

echo "BEGIN: set_up_verif_global.sh"

export NET="verif_global"
export RUN_ENVIR="emc"
export envir="dev"

## Create output directory and set output related environment variables
if [ -d "$OUTPUTROOT" ] ; then
   echo "OUTPUTROOT ($OUTPUTROOT) ALREADY EXISTS"
   echo "OVERRIDE CURRENT OUTPUTROOT? [yes/no]"
   read override
   case "$override" in
       yes)
           echo "Removing current OUTPUTROOT and making new directory"
           rm -r $OUTPUTROOT
           mkdir -p $OUTPUTROOT
           ;;
       no)
           echo "Please set new OUTPUTROOT"
           exit
           ;;
       *)
           echo "$override is not a valid choice, please choose [yes or no]"
           exit
           ;;
   esac
else
   mkdir -p ${OUTPUTROOT}
fi

echo "Output will be in: $OUTPUTROOT"

## Get machine name
. ${HOMEverif_global}/ush/detect_machine.sh
# Set machine to capitalized MACHINE_ID
machine=${MACHINE_ID^^}

## Load modules, set paths to MET and METplus, and some executables
. $HOMEverif_global/ush/load_modules.sh
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Successfully loaded modules"
echo

export COMROOT="$OUTPUTROOT/com"
export DCOMROOT="$OUTPUTROOT/dcom"
export DATAROOT="$OUTPUTROOT/tmp"
export job=${job:-$LSB_JOBNAME}
export jobid=${jobid:-$$}
export DATA=${DATAROOT}/$NET.$jobid
mkdir -p $COMROOT $DCOMROOT $DATAROOT $DATA
mkdir -p $COMROOT/$NET/$envir
mkdir -p $COMROOT/logs/jlogfiles
mkdir -p $COMROOT/output/$envir/today
mkdir -p $COMROOT/output/$envir/$(date +%Y%m%d)
export DCOM=${DCOM:-$DCOMROOT/$NET}
mkdir -p $DCOM
cd $DATA
echo

## Get machine, set environment variable 'machine', and check that it is a supported machine
python $HOMEverif_global/ush/get_machine.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Successfully ran get_machine.py"
echo

if [ -s config.machine ]; then
    . $DATA/config.machine
    status=$?
    [[ $status -ne 0 ]] && exit $status
    [[ $status -eq 0 ]] && echo "Successfully sourced config.machine"
fi

if [[ "$machine" =~ ^(HERA|URSA|ORION|WCOSS2|HERCULES|GAEAC6)$ ]]; then
   echo
else
    echo "ERROR: $machine is not a supported machine"
    exit 1
fi

## Set paths for verif_global, MET, and METplus
export HOMEverif_global=$HOMEverif_global
export PARMverif_global=$HOMEverif_global/parm
export USHverif_global=$HOMEverif_global/ush
export UTILverif_global=$HOMEverif_global/util
export EXECverif_global=$HOMEverif_global/exec
export HOMEMET=$HOMEMET
export HOMEMETplus=$HOMEMETplus
export PARMMETplus=$HOMEMETplus/parm
export USHMETplus=$HOMEMETplus/ush
export PATH="${USHMETplus}:${PATH}"
export PYTHONPATH="${USHMETplus}:${PYTHONPATH}"

## Set machine specific fix directory
if [ $machine = "WCOSS2" ]; then
    export FIXverif_global="/lfs/h2/emc/global/noscrub/emc.global/FIX/fix/verif/20220805"
elif [ $machine = "HERA" -o $machine = "URSA" ]; then
    export FIXverif_global="/scratch3/NCEPDEV/global/role.glopara/fix/verif/20220805"
elif [ $machine = "ORION" -o $machine = "HERCULES" ]; then
    export FIXverif_global="/work/noaa/global/glopara/fix/verif/20220805"
elif [ $machine = "GAEAC6" ]; then
    export FIXverif_global="/gpfs/f6/drsa-precip3/world-shared/role.glopara/fix/verif/20220805"
fi

## Set machine specific account, queues, and run settings
if [ $machine = "WCOSS2" ]; then
    export ACCOUNT="GFS-DEV"
    export QUEUE="dev"
    export QUEUESHARED="dev_shared"
    export QUEUESERV="dev_transfer"
    export PARTITION_BATCH=""
    export nproc="128"
    export MPMD="YES"
elif [ $machine = "HERA" ]; then
    export ACCOUNT="fv3-cpu"
    export QUEUE="batch"
    export QUEUESHARED="batch"
    export QUEUESERV="service"
    export PARTITION_BATCH=""
    export nproc="40"
    export MPMD="YES"
elif [ $machine = "URSA" ]; then
    export ACCOUNT="fv3-cpu"
    export QUEUE="batch"
    export QUEUESHARED="batch"
    export QUEUESERV="u1-service"
    export PARTITION_BATCH="u1-compute"
    export nproc="192"
    export MPMD="YES"
elif [ $machine = "ORION" ]; then
    export ACCOUNT="fv3-cpu"
    export QUEUE="batch"
    export QUEUESHARED="batch"
    export QUEUESERV="service"
    export PARTITION_BATCH="orion"
    export nproc="40"
    export MPMD="YES"
elif [ $machine = "HERCULES" ]; then
    export ACCOUNT="fv3-cpu"
    export QUEUE="batch"
    export QUEUESHARED="batch"
    export QUEUESERV="service"
    export PARTITION_BATCH="hercules"
    export nproc="80"
    export MPMD="YES"
elif [ $machine = "GAEAC6" ]; then
    export ACCOUNT="ira-sti"
    export QUEUE="normal"
    export QUEUESHARED="normal"
    export QUEUESERV="service"
    export CLUSTERS="c6"
    export PARTITION_BATCH="batch"
    export CLUSTERS_DTN="es"
    export PARTITION_DTN="dtn_f5_f6"
    export nproc="192"
    export MPMD="YES"
fi

## Set machine and user specific directories
if [ $machine = "WCOSS2" ]; then
    export NWROOT=${NWROOT:-"/lfs/h1/ops/prod"}
    export HOMEDIR="/lfs/h2/emc/global/noscrub/$USER"
    export STMP="/lfs/h2/emc/stmp/$USER"
    export PTMP="/lfs/h2/emc/ptmp/$USER"
    export NOSCRUB="$HOMEDIR"
    export global_archive="/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/global/archive/model_data"
    export prepbufr_arch_dir="/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/global/archive/obs_data/prepbufr"
    export obdata_dir="/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/global/archive/obs_data"
    export ccpa_24hr_arch_dir="/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/global/archive/obs_data/ccpa_accum24hr"
elif [ $machine = "HERA" -o $machine = "URSA" ]; then
    export NWROOT="/scratch3/NCEPDEV/global/role.glopara/nwpara"
    export HOMEDIR="/scratch3/NCEPDEV/global/$USER"
    export STMP="/scratch3/NCEPDEV/stmp/$USER"
    export PTMP="/scratch3/NCEPDEV/stmp/$USER"
    export NOSCRUB="/scratch3/NCEPDEV/global/$USER"
    export global_archive="/scratch3/NCEPDEV/global/role.glopara/data/metplus.data/archive"
    export prepbufr_arch_dir="/scratch3/NCEPDEV/global/role.glopara/data/metplus.data/prepbufr"
    export obdata_dir="/scratch3/NCEPDEV/global/role.glopara/data/metplus.data/obdata"
    export ccpa_24hr_arch_dir="/scratch3/NCEPDEV/global/role.glopara/data/metplus.data/obdata/ccpa_accum24hr"
elif [ $machine = "ORION" ] || [ $machine = "HERCULES" ]; then
    export NWROOT=${NWROOT:-"/work/noaa/global/glopara/nwpara"}
    export HOMEDIR="/work/noaa/nems/$USER"
    export STMP="/work/noaa/stmp/$USER"
    export PTMP="/work/noaa/stmp/$USER"
    export NOSCRUB="/work/noaa/nems/$USER"
    export global_archive="/work2/noaa/global/role-global/data/metplus.data/archive"
    export prepbufr_arch_dir="/work2/noaa/global/role-global/data/metplus.data/prepbufr"
    export obdata_dir="/work2/noaa/global/role-global/data/metplus.data/obdata"
    export ccpa_24hr_arch_dir="/work2/noaa/global/role-global/data/metplus.data/obdata/ccpa_accum24hr"
elif [ $machine = "GAEAC6" ]; then
    export NWROOT="/gpfs/f6/${ACCOUNT}/world-shared/global/glopara/data/nwpara"
    export HOMEDIR="/gpfs/f6/${ACCOUNT}/scratch/${USER}"
    export STMP="/gpfs/f6/${ACCOUNT}/scratch/${USER}/stmp2"
    export PTMP="/gpfs/f6/${ACCOUNT}/scratch/${USER}/stmp4"
    export NOSCRUB="/gpfs/f6/${ACCOUNT}/scratch/${USER}/noscrub"
    export global_archive="/gpfs/f6/drsa-precip3/world-shared/role.glopara/data/metplus.data/archive"
    export prepbufr_arch_dir="/gpfs/f6/drsa-precip3/world-shared/role.glopara/data/metplus.data/prepbufr"
    export obdata_dir="/gpfs/f6/drsa-precip3/world-shared/role.glopara/data/metplus.data/obdata"
    export ccpa_24hr_arch_dir="/gpfs/f6/drsa-precip3/world-shared/role.glopara/data/metplus.data/obdata/ccpa_accum24hr"
fi

## Set operational directories
if [ $machine = "WCOSS2" ]; then
    source ${HOMEverif_global}/versions/run.ver
    export ccpa_24hr_prod_dir="/lfs/h1/ops/prod/com/verf_precip/${verf_precip_ver}"
    export prepbufr_prod_upper_air_dir="/lfs/h1/ops/prod/com/obsproc/${obsproc_ver}"
    export prepbufr_prod_conus_sfc_dir="/lfs/h1/ops/prod/com/obsproc/${obsproc_ver}"
fi

## Set online and FTP sites
export iabp_ftp="http://iabp.apl.washington.edu/Data_Products/Daily_Full_Res_Data"
export ghrsst_ncei_avhrr_anl_ftp="https://www.ncei.noaa.gov/data/oceans/ghrsst/L4/GLOB/NCEI/AVHRR_OI"
export ghrsst_ospo_geopolar_anl_ftp="https://www.ncei.noaa.gov/data/oceans/ghrsst/L4/GLOB/OSPO/Geo_Polar_Blended"
echo "END: set_up_verif_global.sh"
