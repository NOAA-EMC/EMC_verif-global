help([[
Load environment to run EMC_verif-global on S4 using Intel
]])

load("license_intel/S4")

prepend_path("MODULEPATH", "/data/prod/hpc-stack/modulefiles/stack")

--
-- Get module version from the environment or set default
--
local met_ver = os.getenv("MET_version") or "9.1"
local metplus_ver = os.getenv("METplus_version") or "3.1"
--
local       hpc_ver = os.getenv("hpc_ver") or "1.1.0"
local hpc_intel_ver = os.getenv("hpc_intel_ver") or "18.0.4"
local  hpc_impi_ver = os.getenv("hpc_impi_ver") or "18.0.4"
local    netcdf_ver = os.getenv("netcdf_ver") or "4.7.4"
local      hdf5_ver = os.getenv("hdf5_ver") or "1.10.6"
local      zlib_ver = os.getenv("zlib_ver") or "1.2.11"
local       png_ver = os.getenv("png_ver") or "1.6.35"
local    jasper_ver = os.getenv("jasper_ver") or "2.0.25"
local    wgrib2_ver = os.getenv("wgrib2_ver") or "2.0.8"
local      bufr_ver = os.getenv("bufr_ver") or "11.4.0"
local       gsl_ver = os.getenv("gsl_ver") or "2.6"
local       hdf_ver = os.getenv("hdf_ver") or "4.2.14"
local   hdfeos2_ver = os.getenv("hdfeos2_ver") or "2.20"
local       g2c_ver = os.getenv("g2c_ver") or "1.6.2"
local miniconda_ver = os.getenv("miniconda_ver") or "3.8-s4"
local     grads_ver = os.getenv("grads_ver") or "2.2.1"
--
local grib_util_ver = os.getenv("1.2.2")
local prod_util_ver = os.getenv("1.2.1")
local       nco_ver = os.getenv("4.9.3")
--
-- Load modules
--
load(pathJoin(      "hpc",       hpc_ver))
load(pathJoin("hpc-intel", hpc_intel_ver))
load(pathJoin( "hpc-impi",  hpc_impi_ver))
load(pathJoin(   "netcdf",    netcdf_ver))
load(pathJoin(     "hdf5",      hdf5_ver))
load(pathJoin(     "zlib",      zlib_ver))
load(pathJoin(      "png",       png_ver))
load(pathJoin(   "jasper",    jasper_ver))
load(pathJoin(   "wgrib2",    wgrib2_ver))
load(pathJoin(     "bufr",      bufr_ver))
load(pathJoin(      "gsl",       gsl_ver))
load(pathJoin(      "hdf",       hdf_ver))
load(pathJoin(  "hdfeos2",   hdfeos2_ver))
load(pathJoin(      "g2c",       g2c_ver))
load(pathJoin("miniconda", miniconda_ver))
load(pathJoin(    "grads",     grads_ver))
-- 
prepend_path("MODULEPATH", "/data/prod/glopara/contrib/METplus/modulefiles")
load(pathJoin("metplus", metplus_ver))
-- 
load(pathJoin("grib_util", grib_util_ver))
load(pathJoin("prod_util", prod_util_ver))
load(pathJoin(      "nco",       nco_ver))

