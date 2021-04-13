#!/bin/sh -xe
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------
## NCEP EMC GLOBAL MODEL VERIFICATION
##
## CONTRIBUTORS: Mallory Row, mallory.row@noaa.gov, NOAA/NWS/NCEP/EMC-VPPGB
## PURPOSE: Load necessary modules
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------

echo "BEGIN: load_modules.sh"

## Check versions are supported in verif_global
if [[ "$MET_version" =~ ^(9.1)$ ]]; then
    echo "Requested MET version: $MET_version"
else
    echo "ERROR: $MET_version is not supported in verif_global"
    exit 1
fi
if [[ "$METplus_version" =~ ^(3.1)$ ]]; then
    echo "Requested METplus version: $METplus_version"
else
    echo "ERROR: $METplus_version is not supported in verif_global"
    exit 1
fi

## Load
if [ $machine = WCOSS_C ]; then
    source /opt/modules/default/init/sh
    module purge
    module load craype-haswell
    if [ $MET_version = 9.1 ]; then
        module use /gpfs/hps3/emc/meso/noscrub/emc.metplus/modulefiles
        module load met/9.1
        export HOMEMET="/gpfs/hps3/emc/meso/noscrub/emc.metplus/met/${MET_version}"
        export HOMEMET_bin_exec="exec"
    else
        "ERROR: $MET_version is not supported on $machine"
        exit 1
    fi
    if [ $METplus_version = 3.1 ]; then
        module use /gpfs/hps3/emc/meso/noscrub/emc.metplus/modulefiles
        module load metplus/3.1.1
        export HOMEMETplus="/gpfs/hps3/emc/meso/noscrub/emc.metplus/METplus/METplus-${METplus_version}.1"
    else
        "ERROR: $METplus_version is not supported on $machine"
        exit 1
    fi
    module load alps
    module load xt-lsfhpc/9.1.3
    module load cfp-intel-sandybridge/1.1.0
    module load hpss/4.1.0.3
    module load prod_util/1.1.2
    module load grib_util/1.1.1
    module load nco-gnu-sandybridge/4.4.4
    module use /usrx/local/dev/modulefiles
    module load NetCDF-intel-sandybridge/4.5.0
elif [ $machine = WCOSS_DELL_P3 ]; then
    source /usrx/local/prod/lmod/lmod/init/sh
    module purge
    if [ $MET_version = 9.1 ]; then
        module use /gpfs/dell1/nco/ops/nwprod/modulefiles/compiler_prod/ips/18.0.1
        module load met/9.1.3
        export HOMEMET="/gpfs/dell1/nco/ops/nwprod/met.v${MET_version}.3"
        export HOMEMET_bin_exec="exec"
    else
        "ERROR: $MET_version is not supported on $machine"
        exit 1
    fi
    if [ $METplus_version = 3.1 ]; then
        module use /gpfs/dell1/nco/ops/nwprod/modulefiles/compiler_prod/ips/18.0.1
        module load metplus/3.1.1
        export HOMEMETplus="${METPLUS_PATH}"
    else
        "ERROR: $METplus_version is not supported on $machine"
        exit 1
    fi
    module load EnvVars/1.0.3
    module load lsf/10.1
    module load ips/18.0.1.163
    module load impi/18.0.1
    module load CFP/2.0.1
    module load HPSS/5.0.2.5
    module load prod_util/1.1.5
    module load grib_util/1.1.1
    module load NetCDF/4.5.0
    module use /usrx/local/dev/modulefiles
    module load compiler_third/ips/18.0.1/NCO/4.7.0
elif [ $machine = HERA ]; then
    source /apps/lmod/lmod/init/sh
    module purge
    module load intel/18.0.5.274
    module use /contrib/anaconda/modulefiles
    module load anaconda/latest
    if [ $MET_version = 9.1 ]; then
        module use /contrib/met/modulefiles
        module load met/9.1
        export HOMEMET="/contrib/met/9.1"
        export HOMEMET_bin_exec="bin"
    else
        "ERROR: $MET_version is not supported on $machine"
        exit 1
    fi
    if [ $METplus_version = 3.1 ]; then
        module use /contrib/METplus/modulefiles
        module load metplus/3.1
        export HOMEMETplus="${METPLUS_PATH}"
    else
        "ERROR: $METplus_version is not supported on $machine"
        exit 1
    fi
    module load impi/2018.4.274
    module load hpss/hpss
    module load netcdf/4.6.1
    module load nco/4.9.1
    module use /scratch2/NCEPDEV/nwprod/NCEPLIBS/modulefiles
    module load prod_util/1.1.0
    module load grib_util/1.1.1
elif [ $machine = ORION ]; then
    source /apps/lmod/lmod/init/sh
    module purge
    module load slurm/19.05.3-2
    module load contrib
    module load intel/2020
    module load intelpython3/2020
    if [ $MET_version = 9.1 ]; then
        module load met/9.1
        export HOMEMET="/apps/contrib/MET/9.1"
        export HOMEMET_bin_exec="bin"
    else
        "ERROR: $MET_version is not supported on $machine"
        exit 1
    fi
    if [ $METplus_version = 3.1 ]; then
        module use /apps/contrib/modulefiles
        module load metplus/3.1
        export HOMEMETplus="${METPLUS_PATH}"
    else
        "ERROR: $METplus_version is not supported on $machine"
        exit 1
    fi
    module load impi/2020
    module load netcdf/4.7.2
    module load nco/4.9.3
    module use /apps/contrib/NCEPLIBS/orion/modulefiles
    module use /apps/contrib/NCEPLIBS/lib/modulefiles
    module load grib_util/1.2.0
    module load prod_util/1.2.0
else
    echo "ERROR: $machine is not supported"
    exit 1
fi
if [ $machine != "ORION" ]; then
    export RM=`which rm`
    export CUT=`which cut`
    export TR=`which tr`
    export NCAP2=`which ncap2`
    export CONVERT=`which convert`
    export NCDUMP=`which ncdump`
    export HTAR=`which htar`
fi
if [ $machine = "ORION" ]; then
    export RM=`which rm | sed 's/rm is //g'`
    export CUT=`which cut | sed 's/cut is //g'`
    export TR=`which tr | sed 's/tr is //g'`
    export NCAP2=`which ncap2 | sed 's/ncap2 is //g'`
    export CONVERT=`which convert | sed 's/convert is //g'`
    export NCDUMP=`which ncdump | sed 's/ncdump is //g'`
    export HTAR="/null/htar"
fi
echo "Using HOMEMET=${HOMEMET}"
echo "Using HOMEMETplus=${HOMEMETplus}"

echo "END: load_modules.sh"

module list
