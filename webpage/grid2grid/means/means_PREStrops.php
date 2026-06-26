<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">

<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<title>Home</title>
<link href="../../main.css" rel="stylesheet" type="text/css" media="all" />
<link href="../../fonts.css" rel="stylesheet" type="text/css" media="all" />
<script src="https://d3js.org/d3.v4.min.js"></script>
<script src="../jquery-3.1.1.min.js"></script>
<script type="text/javascript" src="../functions_metplus.js"></script>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>

<?php
$randomtoken = base64_encode( openssl_random_pseudo_bytes(32));
$_SESSION['csrfToken']=$randomtoken;
?>

<?php include "means_globalvars.php"; ?>

<body>
<div id="pageTitle">
<?php echo $stat_title; ?>
</div>
<div class="page-menu"><div class="table">
        <div class="element">
                <span class="bold">Valid:</span>
                <select id="validtime" onchange="changeValidtime(this.value);"></select>
	</div>
        <div class="element">
                <span class="bold">Plot Type:</span>
                <select id="type" onchange="changeType(this.value);"></select>
        </div>
        <div class="element">
                <span class="bold">Forecast Lead:</span>
                <select id="domain" onchange="changeDomain(this.value)"></select>
        </div>
        <div class="element">
                <span class="bold">Region:</span>
                <select id="variable" onchange="changeVariable(this.value)"></select>
        </div>
        <div class="element">
                <span class="bold">Variable:</span>
                <select id="maptype" onchange="changeMaptype(this.value)"></select>
        </div>
        <div class="element">
                <span class="bold">Level:</span>
                <select id="level" onchange="changeLevel(this.value)"></select>
        </div>
</div></div>

<!-- Middle menu -->
<div class="page-middle" id="page-middle">
Left/Right arrow keys = Change forecast lead | Up/Down arrow keys = Change level
<br>For information on grid-to-grid verification, <button class="infobutton" id="myBtn">click here</button>
<div id="myModal" class="modal">
  <div class="modal-content">
    <span class="close">&times;</span>
    Grid-to-Grid Verification Information
    <iframe width=100% height=90% src="../main.php" style="border:none;"></iframe>
  </div>
</div>
<!-- /Middle menu -->
</div>

<div id="loading"><img style="width:100%" src="../../images/loading.png"></div>

<!-- Image -->
<div id="page-map">
        <image name="map" style="width:100%">
</div>

<script type="text/javascript">
// Get the modal
var modal = document.getElementById("myModal");

// Get the button that opens the modal
var btn = document.getElementById("myBtn");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

// When the user clicks the button, open the modal 
btn.onclick = function() {
  modal.style.display = "block";
}

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
  modal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
}
//====================================================================================================^M
//User-defined variables
//====================================================================================================^M

//Global variables
var minFrame = 0; //Minimum frame for every variable
var maxFrame = 26; //Maximum frame for every variable
var incrementFrame = 1; //Increment for every frame

var startFrame = 0; //Starting frame

var cycle = 2018100600;

/*
When constructing the URL below, DDD = domain, VVV = variable, LLL = level, SSS = season, Y = frame number.
For X and Y, labeling one X or Y represents an integer (e.g. 0, 10, 20). Multiple of these represent a string
format (e.g. XX = 00, 06, 12 --- XXX = 000, 006, 012).
*/
var url = "<?php echo $PREStrops_url; ?>";
/* var url = "https://www.emc.ncep.noaa.gov/gmb/yluo/naefs/VRFY_STATS/NCEP_NCEPb/DDDtLLL_VVV_SSS.gif"; */
/* var url = "https://www.emc.ncep.noaa.gov/gmb/STATS_vsdbTTT/allmodel/daily/means/bias_VVV_HGT_LLL_DDD.png";
/* var url = "https://www.emc.ncep.noaa.gov/users/Alicia.Bentley/fv3gefs/2018030100/images/DDD/mean_diff/VVV_Y.png"; */

//====================================================================================================^M
//Add variables & domains
//====================================================================================================^M

var variables = [];
var domains = [];
var levels = [];
var seasons = [];
var maptypes = [];
var validtimes = [];
var types = [];


variables.push({
        displayName: "Global",
        name: "<?php echo $Global_name; ?>",
});
variables.push({
        displayName: "N. Hemisphere",
        name: "<?php echo $NHem_name; ?>",
});
variables.push({
        displayName: "S. Hemisphere",
        name: "<?php echo $SHem_name; ?>",
});
variables.push({
        displayName: "Tropics",
        name: "<?php echo $Tropics_name; ?>",
});
variables.push({
        displayName: "60N-90N",
        name: "<?php echo $N60_name; ?>",
});
variables.push({
        displayName: "60S-90S",
        name: "<?php echo $S60_name; ?>",
});
variables.push({
        displayName: "N. Pacific Ocean",
        name: "<?php echo $NPac_name; ?>",
});
variables.push({
        displayName: "S. Pacific Ocean",
        name: "<?php echo $SPac_name; ?>",
});
variables.push({
        displayName: "N. Atlantic Ocean",
        name: "<?php echo $NAtl_name; ?>",
});
variables.push({
        displayName: "S. Atlantic Ocean",
        name: "<?php echo $SAtl_name; ?>",
});
variables.push({
        displayName: "CONUS",
        name: "<?php echo $CONUS_name; ?>",
});


levels.push({
        displayName: "--",
        name: "<?php echo $NoLevel_name; ?>",
});


validtimes.push({
        displayName: "0000 UTC",
        name: "<?php echo $Valid00_name; ?>",
});


domains.push({
        displayName: "F024",
        name: "<?php echo $Day1_name; ?>",
});
domains.push({
        displayName: "F048",
        name: "<?php echo $Day2_name; ?>",
})
domains.push({
        displayName: "F072",
        name: "<?php echo $Day3_name; ?>",
});
domains.push({
        displayName: "F096",
        name: "<?php echo $Day4_name; ?>",
})
domains.push({
        displayName: "F120",
        name: "<?php echo $Day5_name; ?>",
});
domains.push({
        displayName: "F144",
        name: "<?php echo $Day6_name; ?>",
});
domains.push({
        displayName: "F168",
        name: "<?php echo $Day7_name; ?>",
})
domains.push({
        displayName: "F192",
        name: "<?php echo $Day8_name; ?>",
});
domains.push({
        displayName: "F216",
        name: "<?php echo $Day9_name; ?>",
})
domains.push({
        displayName: "F240",
        name: "<?php echo $Day10_name; ?>",
});

types.push({
        displayName: "Time Series",
	name: "<?php echo $TimeSeries_name; ?>",
});
types.push({
        displayName: "Lead Average",
        name: "<?php echo $LeadMean_name; ?>",
});

maptypes.push({
        url: "means_TMP2m.php",
        displayName: "2m Temperature",
        name: "means_TMP2m",
});
maptypes.push({
        url: "means_RH2m.php",
        displayName: "2m Relative Humidity",
        name: "means_RH2m",
});
maptypes.push({
        url: "means_SPFH2m.php",
        displayName: "2m Specific Humidity",
        name: "means_SPFH2m",
});
maptypes.push({
        url: "means_HGTpbl.php",
        displayName: "PBL Height",
        name: "means_HGTpbl",
});
maptypes.push({
        url: "means_PRESsfc.php",
        displayName: "Surface Pressure",
        name: "means_PRESsfc",
});
maptypes.push({
        url: "means_PRMSL.php",
        displayName: "Sea-level Pressure",
        name: "means_PRMSL",
});
maptypes.push({
        url: "means_TMPsfc.php",
        displayName: "Skin Temperature",
        name: "means_TMPsfc",
});
maptypes.push({
        url: "means_UGRD10m.php",
        displayName: "10m Zonal Wind",
        name: "means_UGRD10m",
});
maptypes.push({
        url: "means_VGRD10m.php",
        displayName: "10m Meridional Wind",
        name: "means_VGRD10m",
});
maptypes.push({
        url: "means_WEASD.php",
        displayName: "Accumulated Snow Water Equiv.",
        name: "means_WEASD",
});
maptypes.push({
        url: "means_TSOILtop.php",
        displayName: "Top Layer Soil Temperature",
        name: "means_TSOILtop",
});
maptypes.push({
        url: "means_SOILWtop.php",
        displayName: "Top Layer Vol. Soil Moisture",
        name: "means_SOILWtop",
});
maptypes.push({
        url: "means_CAPE.php",
        displayName: "CAPE",
        name: "means_CAPE",
});
maptypes.push({
        url: "means_CWAT.php",
        displayName: "Cloud Water",
        name: "means_CWAT",
});
maptypes.push({
        url: "means_PWAT.php",
        displayName: "Precipitable Water",
        name: "means_PWAT",
});
maptypes.push({
        url: "means_HGTtrops.php",
        displayName: "Tropopause Height",
        name: "means_HGTtrops",
});
maptypes.push({
        url: "means_TMPtrops.php",
        displayName: "Tropopause Temperature",
        name: "means_TMPtrops",
});
maptypes.push({
        url: "means_PREStrops.php",
        displayName: "Tropopause Pressure",
        name: "means_PREStrops",
});
maptypes.push({
        url: "means_TOZNEclm.php",
        displayName: "Column Total Ozone",
        name: "means_TOZNEclm",
});

timeseries_domains = ["024", "048", "072", "096", "120", "168", "192", "216", "240"]
fhrmean_domains = ["All"]
non_vertprof_levels = ["_"]
non_vertprof_levels_name = ["--"]




//====================================================================================================^M
//Initialize the page
//====================================================================================================^M

//function for keyboard controls
document.onkeydown = keys;

//Decare object containing data about the currently displayed map^M
imageObj = {};

//Initialize the page
initialize();

//Format initialized run date & return in requested format
function formatDate(offset,format){
        var newdate = String(cycle);
        var yyyy = newdate.slice(0,4);
        var mm = newdate.slice(4,6);
        var dd = newdate.slice(6,8);
        var hh = newdate.slice(8,10);
        var curdate = new Date(yyyy,parseInt(mm)-1,dd,hh);

        
        //Offset by run
        var newOffset = curdate.getHours() + offset;
        curdate.setHours(newOffset);
        
        var yy = String(curdate.getFullYear()).slice(2,4);
        yyyy = curdate.getFullYear();
        mm = curdate.getMonth()+1;
        dd = curdate.getDate();
        if(dd < 10){dd = "0" + dd;}
        hh = curdate.getHours();
        if(hh < 10){hh = "0" + hh;}
        
        var wkday = curdate.getDay();
        var day_str = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
        
        //Return in requested format
        if(format == 'valid'){
                //06Z Thu 03/22/18 (90 h)
                var txt = hh + "Z " + day_str[wkday] + " " + mm + "/" + dd + "/" + yy;
                return txt;
        }
}

//Initialize the page
function initialize(){
        
        //Set image object based on default variables
        imageObj = {
                domain: "<?php echo $Day5_name; ?>",
                variable: "<?php echo $NHem_name; ?>",
                level: "<?php echo $NoLevel_name; ?>",
		validtime: "<?php echo $Valid00_name; ?>",
                type: "<?php echo $TimeSeries_name; ?>",
        };
        
        //Change domain based on passed argument, if any
        var passed_domain = "";
        if(passed_domain!=""){
                if(searchByName(passed_domain,domains)>=0){
                        imageObj.domain = passed_domain;
                }
        }

        //Change variable based on passed argument, if any
        var passed_variable = "";
        if(passed_variable!=""){
                if(searchByName(passed_variable,variables)>=0){
                        imageObj.variable = passed_variable;
                }
        }
        
        //Populate forecast hour and dprog/dt arrays for this run and frame
        populateMenu('variable');
        populateMenu('domain');
        populateMenu('level');
	populateMenu('validtime');
	populateMenu('type');
	populateMenu('maptype');        

        //Populate the frames arrays
        frames = [];
        for(i=minFrame;i<=maxFrame;i=i+incrementFrame){frames.push(i);}
        
        //Predefine empty array for preloading images
        for(i=0; i<variables.length; i++){
                variables[i].images = [];
                variables[i].loaded = [];
                variables[i].dprog = [];
        }
        
        //Preload images and display map
        preload(imageObj);
        showImage();

        //Update mobile display for swiping
        updateMobile();

}

var xInit = null;                                                        
var yInit = null;                  
var xPos = null;
var yPos = null;

</script>
 
</body>
</html>
