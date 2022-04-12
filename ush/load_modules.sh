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
        module use /gpfs/hps/nco/ops/nwprod/modulefiles
        module load met/9.1.3
        export HOMEMET="/gpfs/hps/nco/ops/nwprod/met.v${MET_version}.3"
        export HOMEMET_bin_exec="exec"
    else
        "ERROR: $MET_version is not supported on $machine"
        exit 1
    fi
    if [ $METplus_version = 3.1 ]; then
        module use /gpfs/hps/nco/ops/nwprod/modulefiles
        module load metplus/3.1.1
        export HOMEMETplus="${METPLUS_PATH}"
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
    module unload python/3.6.3
    module unuse /usrx/local/prod/modulefiles
    module use /usrx/local/dev/modulefiles
    module load NetCDF-intel-sandybridge/4.5.0
    module load python/3.6.3
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
    module use /scratch2/NCEPDEV/nwprod/hpc-stack/libs/hpc-stack/modulefiles/stack
    module load hpc/1.1.0
    module load hpc-intel/18.0.5.274
    module load hpc-impi/2018.0.4
    module load prod_util/1.2.2
    module load grib_util/1.2.2
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
elif [ $machine = S4 ]; then
    source /usr/share/lmod/lmod/init/sh
    module purge
    module load license_intel/S4
    module use /data/prod/hpc-stack/modulefiles/stack
    module load hpc/1.1.0
    module load hpc-intel/18.0.4
    module load hpc-impi/18.0.4
    module load netcdf/4.7.4
    module load hdf5/1.10.6
    module load zlib/1.2.11
    module load png/1.6.35
    module load jasper/2.0.25
    module load wgrib2/2.0.8
    module load bufr/11.4.0
    module load gsl/2.6
    module load hdf/4.2.14
    module load hdfeos2/2.20
    module load g2c/1.6.2
    module load miniconda/3.8-s4
    if [ $MET_version = 9.1 ]; then
        module use /data/prod/glopara/contrib/MET/modulefiles
        module load met/9.1
        export HOMEMET="/data/prod/glopara/contrib/MET/met-9.1.3"
        export HOMEMET_bin_exec="bin"
    else
        "ERROR: $MET_version is not supported on $machine"
        exit 1
    fi
    if [ $METplus_version = 3.1 ]; then
        module use /data/prod/glopara/contrib/METplus/modulefiles
        module load metplus/3.1
        export HOMEMETplus="/data/prod/glopara/contrib/METplus/METplus-3.1.1"
    else
        "ERROR: $METplus_version is not supported on $machine"
        exit 1
    fi
    module load grib_util/1.2.2
    module load prod_util/1.2.1
    module load nco/4.9.3
elif [ $machine = JET ]; then
    source /apps/lmod/lmod/init/sh
    module purge
    module use /lfs4/HFIP/hfv3gfs/nwprod/hpc-stack/libs/modulefiles/stack
    module load hpc/1.1.0
    module load hpc-intel/18.0.5.274
    module load hpc-impi/2018.4.274
    module load wgrib/1.8.1.0b
    module load wgrib2/2.0.8
    module load hpss
    module load nco/4.9.1
    module load prod_util/1.2.2
    module load grib_util/1.2.2
    module load netcdf/4.6.1
    module load hdf5/1.10.4
    module load intel
    module load intelpython/3.6.5
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
        module use /contrib/met/METplus/modulefiles
        module load R/4.0.2        
        module load metplus/3.1.1
        export HOMEMETplus="${METPLUS_PATH}"
    else
        "ERROR: $METplus_version is not supported on $machine"
        exit 1
    fi
elif [ $machine = WCOSS2 ]; then
    source /usr/share/lmod/lmod/init/sh
    module reset
    source ${HOMEverif_global}/versions/run.ver
    export HPC_OPT=/apps/ops/para/libs
    module use ${HOMEverif_global}/modulefiles
    module load emc_verif_global_wcoss2
    if [ $MET_version = 9.1 ]; then
        export HOMEMET="$MET_ROOT"
        export HOMEMET_bin_exec="bin"
    else
        "ERROR: $MET_version is not supported on $machine"
        exit 1
    fi
    if [ $METplus_version = 3.1 ]; then
        export HOMEMETplus="${METPLUS_PATH}"
    else
        "ERROR: $METplus_version is not supported on $machine"
        exit 1
    fi
else
    echo "ERROR: $machine is not supported"
    exit 1
fi
if [ $machine != "ORION" ]; then
    export RM=$(which rm)
    export CUT=$(which cut)
    export TR=$(which tr)
    export CONVERT=$(which convert)
    export NCDUMP=$(which ncdump)
    export NCEA=$(which ncea)
    if [ $machine == "S4" ]; then
        export HTAR="/null/htar"
        export NCAP2="/null/ncap2"
    elif [ $machine == "JET" -o $machine == "WCOSS2" ]; then
        export HTAR=$(which htar)
        export NCAP2="/null/ncap2"
    else
        export HTAR=$(which htar)
        export NCAP2=$(which ncap2)
    fi
fi
if [ $machine = "ORION" ]; then
    export RM=$(which rm | sed 's/rm is //g')
    export CUT=$(which cut | sed 's/cut is //g')
    export TR=$(which tr | sed 's/tr is //g')
    export NCAP2=$(which ncap2 | sed 's/ncap2 is //g')
    export CONVERT=$(which convert | sed 's/convert is //g')
    export NCDUMP=$(which ncdump | sed 's/ncdump is //g')
    export NCEA=$(which ncea | sed 's/ncea is //g')
    export HTAR="/null/htar"
fi

echo "Using HOMEMET=${HOMEMET}"
echo "Using HOMEMETplus=${HOMEMETplus}"

echo "END: load_modules.sh"

module list
