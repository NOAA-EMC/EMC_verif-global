help([[
Load environment to run EMC_verif-global on Jet using Intel
]])

hpss_ver=os.getenv("hpss_ver") or ""
load(pathJoin("hpss", hpss_ver))

gnu_ver=os.getenv("gnu_ver") or "9.2.0b"
load(pathJoin("gnu", gnu_ver))

intel_ver=os.getenv("intel_ver") or "2023.2.0"
load(pathJoin("intel", intel_ver))

intelpython_ver=os.getenv("intelpython_ver") or "3.6.5"
load(pathJoin("intelpython", intelpython_ver))

nco_ver=os.getenv("nco_ver") or "4.9.1"
load(pathJoin("nco", nco_ver))

wgrib_ver=os.getenv("wgrib_ver") or "1.8.1.0b"
load(pathJoin("wgrib", wgrib_ver))

wgrib2_ver=os.getenv("wgrib2_ver") or "2.0.8"
load(pathJoin("wgrib2", wgrib2_ver))

R_ver=os.getenv("R_ver") or "4.0.2"
load(pathJoin("R", R_ver))

imagemagick_ver=os.getenv("imagemagick_ver","7.1.1-11")
load(pathJoin("imagemagick",imagemagick_ver))

grads_ver=os.getenv("grads_ver") or "2.2.1"
load(pathJoin("grads", grads_ver))

prepend_path("MODULEPATH", "/contrib/met/modulefiles")
met_ver=os.getenv("met_ver") or "9.1"
load(pathJoin("met", met_ver))

prepend_path("MODULEPATH", "/contrib/met/METplus/modulefiles")
metplus_ver=os.getenv("metplus_ver") or "3.1.1"
load(pathJoin("metplus", metplus_ver))

prepend_path("MODULEPATH", "/mnt/lfs4/HFIP/hfv3gfs/role.epic/hpc-stack/libs/intel-2022.1.2/modulefiles/stack")

hpc_ver=os.getenv("hpc_ver") or "1.2.0"
load(pathJoin("hpc", hpc_ver))

hpc_intel_ver=os.getenv("hpc_intel_ver") or "2022.1.2"
load(pathJoin("hpc-intel", hpc_intel_ver))

hpc_impi_ver=os.getenv("hpc_impi_ver") or "2022.1.2"
load(pathJoin("hpc-impi", impi_ver))

prod_util_ver=os.getenv("prod_util_ver") or "1.2.2"
load(pathJoin("prod_util", prod_util_ver))

grib_util_ver=os.getenv("grib_util_ver") or "1.2.4"
load(pathJoin("grib_util", grib_util_ver))

--unload(pathJoin("intelpython", intelpython_ver))
--prepend_path("MODULEPATH", "/mnt/lfs4/HFIP/hfv3gfs/role.epic/miniconda3/modulefiles")
--miniconda3_ver=os.getenv("miniconda3_ver") or "4.12.0"
--load(pathJoin("miniconda3", miniconda3_ver))

-- activate ufswm on load, deactivate on unload
--if (mode() == "load") then
--  local load_cmd = "conda activate ufswm"
--  execute{cmd=load_cmd, modeA={"load"}}
--else
--  if (mode() == "unload") then
--    local unload_cmd = "conda deactivate"
--    execute{cmd=unload_cmd, modeA={"unload"}}
--  end
--end
