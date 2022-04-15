help([[
Load environment to run EMC_verif-global on Orion using Intel
]])

slurm_ver=os.getenv("slurm_ver") or "19.05.3-2"
load(pathJoin("slurm", slurm_ver))

prepend_path("MODULEPATH", "/apps/contrib/NCEP/libs/hpc-stack/modulefiles/stack")

hpc_ver=os.getenv("hpc_ver") or "1.1.0"
load(pathJoin("hpc", hpc_ver))

hpc_intel_ver=os.getenv("hpc_intel_ver") or "2018.4"
load(pathJoin("hpc-intel", hpc_intel_ver))

hpc_impi_ver=os.getenv("hpc_impi_ver") or "2018.4"
load(pathJoin("hpc-impi", impi_ver))

netcdf_ver=os.getenv("netcdf_ver") or "4.7.4"
load(pathJoin("netcdf", netcdf_ver))

nco_ver=os.getenv("nco_ver") or "4.9.3"
load(pathJoin("nco", nco_ver))

prod_util_ver=os.getenv("prod_util_ver") or "1.2.2"
load(pathJoin("prod_util", prod_util_ver))

grib_util_ver=os.getenv("grib_util_ver") or "1.2.2"
load(pathJoin("grib_util", grib_util_ver))

grads_ver=os.getenv("grads_ver") or "2.2.1"
load(pathJoin("grads", grads_ver))

contrib_ver=os.getenv("contrib_ver") or ""
load(pathJoin("contrib", contrib_ver))

intel_ver = os.getenv("intel_ver") or "2020"
load(pathJoin("intel", intel_ver))

intelpython3_ver = os.getenv("intelpython3_ver") or "2020"
load(pathJoin("intelpython3", intelpython3_ver))

met_ver=os.getenv("met_ver") or "9.1"
load(pathJoin("met", met_ver))

prepend_path("MODULEPATH", "/apps/contrib/modulefiles")

metplus_ver=os.getenv("metplus_ver") or "3.1"
load(pathJoin("metplus", metplus_ver))
