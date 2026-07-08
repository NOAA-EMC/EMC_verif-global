<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">

<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<title>Home</title>
<link href="http://fonts.googleapis.com/css?family=Source+Sans+Pro:200,300,400,600,700,900" rel="stylesheet" />
<link href="../main.css" rel="stylesheet" type="text/css" media="all" />
<link href="../fonts.css" rel="stylesheet" type="text/css" media="all" />
<script src="https://d3js.org/d3.v4.min.js"></script>
</head>

<?php
$randomtoken = base64_encode( openssl_random_pseudo_bytes(32));
$_SESSION['csrfToken']=$randomtoken;
?>

<body>
<li>
Regular partial sums are computed for each model (see <a href="https://met.readthedocs.io/en/latest/Users_Guide/appendixC.html#partial-sums-lines-sl1l2-sal1l2-vl1l2-val1l2" target="_blank">here</a>). Each model's forecast are verified against ONLYSFC (ADPSFC and SFCSHP) surface observations from the NAM PREPBUFR files and ADPUPA upper-air observations from the GDAS PREPBUFR files that fall in a 45 minute window of the valid time. Forecast are also verified against data from the International Arctic Buoy Programme (<a href="http://iabp.apl.washington.edu" targer="_blank">IABP</a>) at their valid time. All data are regridded using bilinear interpolation, if needed, to the <a href=http://www.nco.ncep.noaa.gov/pmb/docs/on388/grids/grid003.gif target="_blank">G003</a> (1x1 degree) grid for upper-air variables, to the <a href=http://www.nco.ncep.noaa.gov/pmb/docs/on388/grids/grid104.gif target="_blank">G104</a> grid for surface variables, and to the grid <a href=http://www.nco.ncep.noaa.gov/pmb/docs/on388/grids/grid223.gif target="_blank">G223</a> for the IABP verifcation.
</li>
<br>
<li>
Verification statistics are computed from the regular partial sums. The equations used to calculate the verification statistics can be found <a href="https://www.emc.ncep.noaa.gov/users/verification/global/gfs/doc/RMSE_decomposition.pdf" target="_blank">here</a>. Statistical signifance is calculated using a student-t test.
</li>
<br>
<li>
The verification regions used for upper-air (ADPUPA observations) are:
                     <a href="http://www.nco.ncep.noaa.gov/pmb/docs/on388/grids/grid003.gif" target="_blank">Global</a>,
                     <a href="../images/vx_masks/NH.png" target="_blank">N. Hemisphere</a>: 20N-90N,
                     <a href="../images/vx_masks/SH.png" target="_blank">S. Hemisphere</a>: 20S-90S,
                     <a href="../images/vx_masks/TRO.png" target="_blank">Tropics</a>: 20S-20N,
                     <a href="../images/vx_masks/G236.png" target="_blank">Grid 236</a>,
                     <a href="../images/vx_masks/POLAR.png" target="_blank">Polar</a>: 60S-90S and 60N-90N, and
                     <a href="../images/vx_masks/ARCTIC.png" target="_blank">Arctic</a>.
</li>
<br>
<li>
The verification regions used for surface (ONLYSF observations) are:
                     <a href=http://www.nco.ncep.noaa.gov/pmb/docs/on388/grids/grid104.gif target="_blank">G104</a>,
                     <a href="../images/vx_masks/WEST.png" target="_blank">West</a>,
                     <a href="../images/vx_masks/EAST.png" target="_blank">East</a>,
                     <a href="../images/vx_masks/NWC.png" target="_blank">Northwest Coast</a>,
                     <a href="../images/vx_masks/SWC.png" target="_blank">Southwest Coast</a>,
                     <a href="../images/vx_masks/NMT.png" target="_blank">Northern Mountain</a>,
                     <a href="../images/vx_masks/GRB.png" target="_blank">Great Basin</a>,
                     <a href="../images/vx_masks/SMT.png" target="_blank">Southern Mountain</a>,
                     <a href="../images/vx_masks/SWD.png" target="_blank">Southwest Desert</a>,
                     <a href="../images/vx_masks/NPL.png" target="_blank">Northern Plains</a>,
                     <a href="../images/vx_masks/SPL.png" target="_blank">Southern Plains</a>,
                     <a href="../images/vx_masks/MDW.png" target="_blank">Midwest</a>,
                     <a href="../images/vx_masks/LMV.png" target="_blank">Lower Mississippi</a>,
                     <a href="../images/vx_masks/APL.png" target="_blank">Appalachians</a>,
                     <a href="../images/vx_masks/NEC.png" target="_blank">Northeast Coast</a>,
                     <a href="../images/vx_masks/SEC.png" target="_blank">Southeast Coast</a>,
                     <a href="../images/vx_masks/GMC.png" target="_blank">Gulf of America Coast</a>,
                     <a href="../images/vx_masks/NAK.png" target="_blank">Northern Alaska</a>, and
                     <a href="../images/vx_masks/SAK.png" target="_blank">Southern Alaska</a>.
</li>
<br>
<li>
The verification region used for IABP observations (limited to the Arctic) is:
                     <a href="../images/vx_masks/ARCTIC.png" target="_blank">Arctic</a>.
</li>
</body>
</html>
