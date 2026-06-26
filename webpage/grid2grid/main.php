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
Regular and anomalous partial sums are computed for each model (see <a href="https://met.readthedocs.io/en/latest/Users_Guide/appendixC.html#partial-sums-lines-sl1l2-sal1l2-vl1l2-val1l2" target="_blank">here</a>). Each model's forecasts are verified using its own analysis as truth. All data are regridded using bilinear interpolation, if needed, to the <a href=http://www.nco.ncep.noaa.gov/pmb/docs/on388/grids/grid002.gif target="_blank">G002</a> (2.5x2.5 degree) grid. A 40-year (1959-1998) climatology of the NCEP/NCAR reanalysis is used for computing anomalous partial sums.
</li>
<br>
<li>
Verification statistics are computed from the regular and anomalous partial sums. The equations used to calculate the verification statistics can be found <a href=https://www.emc.ncep.noaa.gov/users/verification/global/gfs/doc/RMSE_decomposition.pdf target="_blank">here</a>. Statistical signifance is calculated using a student-t test.
</li>
<br>
<li>
The wave breakdown for heights is done using Fourier Decomposition.
</li>
<br>
<li>
The verification regions used are:
                     <a href="http://www.nco.ncep.noaa.gov/pmb/docs/on388/grids/grid002.gif" target="_blank">Global</a>,
                     <a href="../images/vx_masks/NHX.png" target="_blank">N. Hemisphere</a>: 20N-80N,
                     <a href="../images/vx_masks/SHX.png" target="_blank">S. Hemisphere</a>: 20S-80S,
                     <a href="../images/vx_masks/TRO.png" target="_blank">Tropics</a>: 20S-20N,
                     <a href="../images/vx_masks/PNA.png" target="_blank">PNA</a>: 180E-320E, 20N-75N, 
                     <a href="../images/vx_masks/N60.png" target="_blank">60N-90N</a>,
                     <a href="../images/vx_masks/S60.png" target="_blank">60S-90S</a>,
                     <a href="../images/vx_masks/NPO.png" target="_blank">N. Pacific Ocean</a>,
                     <a href="../images/vx_masks/SPO.png" target="_blank">S. Pacific Ocean</a>,
                     <a href="../images/vx_masks/NAO.png" target="_blank">N. Atlantic Ocean</a>,
                     <a href="../images/vx_masks/SAO.png" target="_blank">S. Atlantic Ocean</a>, and
                     <a href="../images/vx_masks/CONUS.png" target="_blank">CONUS</a>.
                  
</li>
</body>
</html>
