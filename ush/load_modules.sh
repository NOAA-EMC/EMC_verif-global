#!/bin/sh -xe
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------
## NCEP EMC GLOBAL MODEL VERIFICATION
##
## CONTRIBUTORS: Mallory Row, mallory.row@noaa.gov, NOAA/NWS/NCEP/EMC-VPPGB
## PURPOSE: Load necessary modules
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------

machine=${1}
MET_version=${2}
METplus_version=${3}

echo "BEGIN: load_modules.sh"

## Check versions are supported in verif_global
if [[ "$MET_version" =~ ^(7.0|8.0|8.1)$ ]]; then
    echo "Requested MET version: $MET_version"
else
    echo "ERROR: $MET_version is not supported in verif_global"
    exit 1
fi
if [[ "$METplus_version" =~ ^(2.1)$ ]]; then
    echo "Requested METplus version: $METplus_version"
else
    echo "ERROR: $METplus_version is not supported in verif_global"
    exit 1
fi

## Load
if [ $machine = WCOSS_C ]; then
    source /opt/modules/default/init/sh
    module use /usrx/local/prod/modulefiles
    module use /usrx/local/dev/modulefiles
    module load xt-lsfhpc/9.1.3 
    module load alps 
    module load cfp-intel-sandybridge/1.1.0 
    module load prod_util 
    module load grib_util/1.1.0 
    module load util_shared/1.0.7 
    module load nco-gnu-sandybridge/4.4.4 
    module load NetCDF-intel-sandybridge/4.2 
    module load hpss 
    module load python/2.7.14 
    if [ $MET_version = 8.1 ]; then
        module load met/$MET_version 
        export HOMEMET="/usrx/local/dev/met/${MET_version}"
    elif [ $MET_version = 7.0 -o $MET_version = 8.0 ]; then
        module use /gpfs/hps3/emc/global/noscrub/Julie.Prestopnik/modulefiles 
        module load met/$MET_version 
        export HOMEMET="/gpfs/hps3/emc/global/noscrub/Julie.Prestopnik/met/${MET_version}"
    else
        "ERROR: $MET_version is not supported on $machine"
        exit 1
    fi
    if [ $METplus_version = 2.1 ]; then
        module load metplus/2.1
        export HOMEMETplus="/usrx/local/dev/met/METplus/METplus-$METplus_version"
    else
        "ERROR: $METplus_version is not supported on $machine"
        exit 1
    fi
elif [ $machine = WCOSS_DELL_P3 ]; then
    source /usrx/local/prod/lmod/lmod/init/sh
    module load EnvVars/1.0.2
    module load lsf/10.1 
    module load ips/18.0.1.163 
    module load impi/18.0.1 
    module load prod_util/1.1.0 
    module load grib_util/1.0.6 
    module load NCO/4.7.0 
    module load NetCDF/4.5.0
    module load HPSS/5.0.2.5  
    module load CFP/2.0.1
    module use /usrx/local/dev/modulefiles
    module load python/2.7.14
    module load imagemagick/6.9.9-25 
    if [ $MET_version = 8.1 ]; then
        module load met/$MET_version 
        export HOMEMET="/usrx/local/dev/packages/met/${MET_version}"
    elif [ $MET_version = 7.0 -o $MET_version = 8.0 ]; then
        module use /gpfs/dell2/emc/verification/noscrub/Julie.Prestopnik/modulefiles 
        module load met/$MET_version 
        export HOMEMET="/gpfs/dell2/emc/verification/noscrub/Julie.Prestopnik/met/${MET_version}"
    else
        "ERROR: $MET_version is not supported on $machine"
        exit 1
    fi
    if [ $METplus_version = 2.1 ]; then
        module load metplus/2.1
        export HOMEMETplus="/usrx/local/dev/packages/met/METplus/METplus-$METplus_version"
    else
        "ERROR: $METplus_version is not supported on $machine"
        exit 1
    fi
elif [ $machine = HERA ]; then
    source /apps/lmod/lmod/init/sh
    module load intel
    module load impi
    module load hpss/hpss
    module load netcdf
    module load nco
    module use -a /scratch2/NCEPDEV/nwprod/NCEPLIBS/modulefiles
    module load prod_util/1.1.0
    module load grib_util/1.1.1
    module use -a /contrib/anaconda/modulefiles
    module load anaconda/anaconda2-4.4.0
    if [ $MET_version = 7.0 -o $MET_version = 8.0 -o $MET_version = 8.1 ]; then
        module use -a /contrib/met/modulefiles
        module load met/$MET_version
        export HOMEMET="/contrib/met/${MET_version}"
    else
        "ERROR: $MET_version is not supported on $machine"
        exit 1
    fi
    if [ $METplus_version = 2.1 ]; then
        export HOMEMETplus="/contrib/METplus/METplus-$METplus_version"
    else
        "ERROR: $METplus_version is not supported on $machine"
        exit 1
    fi
    module switch anaconda/anaconda2
elif [ $machine = ORION ]; then
    source /apps/lmod/lmod/init/sh
    module load contrib
    module use /apps/contrib/NCEPLIBS/orion/modulefiles
    module use /apps/contrib/NCEPLIBS/lib/modulefiles
    module load intel/2020
    module load impi/2020
    module load grib_util/1.2.0
    module load prod_util/1.2.0
    module load nco/4.8.1
    module load netcdf/4.7.2
    module load intelpython2/2019.5
    if [ $MET_version = 8.1 ]; then
        module use /work/noaa/ovp/jprestop/MET/modulefiles
        module load met/$MET_version
        export HOMEMET="/work/noaa/ovp/jprestop/MET/${MET_version}"
    else
        "ERROR: $MET_version is not supported on $machine"
        exit 1
    fi
    if [ $METplus_version = 2.1 ]; then
        export HOMEMETplus="/work/noaa/ovp/jprestop/METplus/METplus-$METplus_version"
    else
        "ERROR: $METplus_version is not supported on $machine"
        exit 1
    fi
else
    echo "ERROR: $machine is not supported"
    exit 1
fi
if [ $machine != "ORION" ]; then
    export NCAP2=`which ncap2`
    export NCDUMP=`which ncdump`
    export HTAR=`which htar`
    export CONVERT=`which convert`
fi
if [ $machine = "ORION" ]; then
    export NCAP2=`which ncap2 | sed 's/ncap2 is //g'`
    export NCDUMP=`which ncdump | sed 's/ncdump is //g'`
    export CONVERT=`which convert | sed 's/convert is //g'`
fi
echo "Using HOMEMET=${HOMEMET}"
echo "Using HOMEMETplus=${HOMEMETplus}"

echo "END: load_modules.sh"

module list
