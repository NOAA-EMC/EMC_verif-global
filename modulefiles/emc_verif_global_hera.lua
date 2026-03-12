help([[
Load environment to run EMC_verif-global on Hera using Intel
]])

hpss_ver=os.getenv("hpss_ver") or "hpss"
load(pathJoin("hpss", hpss_ver))

grads_ver=os.getenv("grads_ver","2.2.3")
load(pathJoin("grads",grads_ver))

imagemagick_ver=os.getenv("imagemagick_ver","7.1.1-11")
load(pathJoin("imagemagick",imagemagick_ver))

prepend_path("MODULEPATH", "/contrib/spack-stack/spack-stack-1.9.3/envs/ue-oneapi-2024.2.1/install/modulefiles/Core")

stack_oneapi_ver=os.getenv("stack_oneapi_ver") or "2024.2.1"
load(pathJoin("stack-oneapi", stack_oneapi_ver))

stack_impi_ver=os.getenv("stack_impi_ver") or "2021.13"
load(pathJoin("stack-intel-oneapi-mpi", stack_mpi_ver))

netcdf_c_ver=os.getenv("netcdf_c_ver") or "4.9.2"
load(pathJoin("netcdf-c", netcdf_c_ver))

prod_util_ver=os.getenv("prod_util_ver") or "2.1.1"
load(pathJoin("prod_util", prod_util_ver))

libjpeg_ver=os.getenv("libjpeg_ver") or "2.1.0"
load(pathJoin("libjpeg", libjpeg_ver))

libpng_ver=os.getenv("libpng_ver") or "1.6.37"
load(pathJoin("libpng", libpng_ver))

zlib_ver=os.getenv("zlib_ver") or "1.2.11"
load(pathJoin("zlib", zlib_ver))

jasper_ver=os.getenv("jasper_ver") or "2.0.32"
load(pathJoin("jasper", jasper_ver))

udunits_ver=os.getenv("udunits_ver") or "2.2.28"
load(pathJoin("udunits", udunits_ver))

grib_util_ver=os.getenv("grib_util_ver") or "1.4.0"
load(pathJoin("grib-util", grib_util_ver))

wgrib2_ver=os.getenv("wgrib2_ver") or "3.6.0"
load(pathJoin("wgrib2", wgrib2_ver))

nco_ver=os.getenv("nco_ver") or "5.2.4"
load(pathJoin("nco", nco_ver))

met_ver=os.getenv("met_ver") or "12.0.1"
load(pathJoin("met", met_ver))

metplus_ver=os.getenv("metplus_ver") or "6.0.0"
load(pathJoin("metplus", metplus_ver))

bufr_ver=os.getenv("bufr_ver") or "12.1.0"
load(pathJoin("bufr", bufr_ver))

cdo_ver=os.getenv("cdo_ver") or "2.3.0"
load(pathJoin("cdo", cdo_ver))
