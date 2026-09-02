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

<?php include "rmse_globalvars.php"; ?>

<body>
<div id="pageTitle">
<?php echo $stat_title; ?>
</div>
<div class="page-menu"><div class="table">
        <div class="element">
                <span class="bold">Obs. Type:</span>
                <select id="maptype" onchange="changeMaptype(this.value)"></select>
        </div>
        <div class="element">
                <span class="bold">Valid:</span>
                <select id="validtime" onchange="changeValidtime(this.value);"></select>
        </div>
        <div class="element">
                <span class="bold">Plot Type:</span>
                <select id="type" onchange="changeType(this.value);"></select>
        </div>
        <div class="element">
                <span class="bold">Region:</span>
                <select id="domain" onchange="changeDomain(this.value)"></select>
        </div>
        <div class="element">
                <span class="bold">Forecast Lead:</span>
                <select id="season" onchange="changeSeason(this.value)"></select>
        </div>
        <div class="element">
                <span class="bold">Variable:</span>
                <select id="variable" onchange="changeVariable(this.value)"></select>
        </div>
        <div class="element">
                <span class="bold">Level:</span>
                <select id="level" onchange="changeLevel(this.value)"></select>
        </div>
</div></div>

<!-- Middle menu -->
<div class="page-middle" id="page-middle">
Left/Right arrow keys = Change forecast lead | Up/Down arrow keys = Change level
<br>For information on grid-to-obs verification, <button class="infobutton" id="myBtn">click here</button>
<div id="myModal" class="modal">
  <div class="modal-content">
    <span class="close">&times;</span>
    Grid-to-Obs Verification Information
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
//====================================================================================================
//User-defined variables
//====================================================================================================

//Global variables
var minFrame = 0; //Minimum frame for every variable
var maxFrame = 26; //Maximum frame for every variable
var incrementFrame = 1; //Increment for every frame

var startFrame = 0; //Starting frame

var cycle = 2018100600;

/*
When constructing the URL below, DDD = domain, VVV = variable, LLL = level, SSS = season, PPP = type.
*/
var url = "<?php echo $ADPUPA_url; ?>";

//====================================================================================================
//Add variables & domains
//====================================================================================================

var variables = [];
var domains = [];
var levels = [];
var seasons = [];
var maptypes = [];
var validtimes = [];
var types = [];


domains.push({
        displayName: "Global",
        name: "<?php echo $Global_name; ?>",
});
domains.push({
        displayName: "N. Hemisphere",
        name: "<?php echo $NHem_name; ?>",
});
domains.push({
        displayName: "S. Hemisphere",
        name: "<?php echo $SHem_name; ?>",
});
domains.push({
        displayName: "Tropics",
        name: "<?php echo $Tropics_name; ?>",
});
domains.push({
        displayName: "G236",
        name: "<?php echo $G236_name; ?>",
});
domains.push({
        displayName: "Polar",
        name: "<?php echo $Polar_name; ?>",
});
domains.push({
        displayName: "Arctic",
        name: "<?php echo $Arctic_name; ?>",
});


levels.push({
        displayName: "1 hPa",
        name: "<?php echo $P1_name; ?>",
});
levels.push({
        displayName: "5 hPa",
        name: "<?php echo $P5_name; ?>",
});
levels.push({
        displayName: "10 hPa",
        name: "<?php echo $P10_name; ?>",
});
levels.push({
        displayName: "50 hPa",
        name: "<?php echo $P50_name; ?>",
});
levels.push({
        displayName: "100 hPa",
        name: "<?php echo $P100_name; ?>",
});
levels.push({
        displayName: "150 hPa",
        name: "<?php echo $P150_name; ?>",
});
levels.push({
        displayName: "200 hPa",
        name: "<?php echo $P200_name; ?>",
});
levels.push({
        displayName: "250 hPa",
        name: "<?php echo $P250_name; ?>",
});
levels.push({
        displayName: "300 hPa",
        name: "<?php echo $P300_name; ?>",
});
levels.push({
        displayName: "400 hPa",
        name: "<?php echo $P400_name; ?>",
});
levels.push({
        displayName: "500 hPa",
        name: "<?php echo $P500_name; ?>",
});
levels.push({
        displayName: "700 hPa",
        name: "<?php echo $P700_name; ?>",
});
levels.push({
        displayName: "850 hPa",
        name: "<?php echo $P850_name; ?>",
});
levels.push({
        displayName: "925 hPa",
        name: "<?php echo $P925_name; ?>",
});
levels.push({
        displayName: "1000 hPa",
        name: "<?php echo $P1000_name; ?>",
});


seasons.push({
        displayName: "F000",
        name: "<?php echo $Day0_name; ?>",
});
seasons.push({
        displayName: "F024",
        name: "<?php echo $Day1_name; ?>",
});
seasons.push({
        displayName: "F048",
        name: "<?php echo $Day2_name; ?>",
});
seasons.push({
        displayName: "F072",
        name: "<?php echo $Day3_name; ?>",
});
seasons.push({
        displayName: "F096",
        name: "<?php echo $Day4_name; ?>",
});
seasons.push({
        displayName: "F120",
        name: "<?php echo $Day5_name; ?>",
});
seasons.push({
        displayName: "F144",
        name: "<?php echo $Day6_name; ?>",
});
seasons.push({
        displayName: "F168",
        name: "<?php echo $Day7_name; ?>",
});
seasons.push({
        displayName: "F192",
        name: "<?php echo $Day8_name; ?>",
});
seasons.push({
        displayName: "F216",
        name: "<?php echo $Day9_name; ?>",
});
seasons.push({
        displayName: "F240",
        name: "<?php echo $Day10_name; ?>",
});

validtimes.push({
        displayName: "0000 UTC",
        name: "<?php echo $Valid00_name; ?>",
});
validtimes.push({
        displayName: "0600 UTC",
        name: "<?php echo $Valid06_name; ?>",
});
validtimes.push({
        displayName: "1200 UTC",
        name: "<?php echo $Valid12_name; ?>",
});
validtimes.push({
        displayName: "1800 UTC",
        name: "<?php echo $Valid18_name; ?>",
});


variables.push({
        displayName: "Temperature",
        name: "<?php echo $Temp_name; ?>",
});
variables.push({
        displayName: "Relative Humidity",
        name: "<?php echo $RelHum_name; ?>",
});
variables.push({
        displayName: "Vector Wind",
        name: "<?php echo $VectWind_name; ?>",
});
variables.push({
        displayName: "Specific Humidity",
        name: "<?php echo $SpefHum_name; ?>",
});
variables.push({
        displayName: "Geopotential Height",
        name: "<?php echo $GeoHeight_name; ?>",
});


types.push({
        displayName: "Time Series",
        name: "<?php echo $TimeSeries_name; ?>",
});
types.push({
        displayName: "Lead Average",
        name: "<?php echo $LeadMean_name; ?>",
});
types.push({
        displayName: "Vertical Profile",
        name: "<?php echo $VertProf_name; ?>",
});
types.push({
        displayName: "Lead by Level",
        name: "<?php echo $VertProfLead_name; ?>",
});


maptypes.push({
        url: "rmse_ADPUPA.php",
        displayName: "ADPUPA",
        name: "rmse_ADPUPA",
});
maptypes.push({
        url: "rmse_ONLYSF.php",
        displayName: "ONLYSF",
        name: "rmse_ONLYSF",
});
maptypes.push({
        url: "rmse_IABP.php",
        displayName: "IABP",
        name: "rmse_IABP",
});

timeseries_seasons = ["024", "048", "072", "096", "120", "168", "192", "216", "240"]
fhrmean_seasons = ["All"]


vertprof_levels = ["all", "trop", "ltrop", "utrop", "strat"]
vertprof_levels_name = ["All", "Troposphere", "Lower Troposphere", "Upper Troposphere", "Stratosphere"]
non_vertprof_levels = ["p1000", "p925", "p850", "p700", "p500", "p300", "p250", "p200", "p100", "p50", "p20", "p10", "p5"]
non_vertprof_levels_name = ["1000 hPa", "925 hPa", "850 hPa", "700 hPa", "500 hPa", "300 hPa", "250 hPa", "200 hPa", "100 hPa", "50 hPa", "20 hPa", "10 hPa", "5 hPa"]
//====================================================================================================
//Initialize the page
//====================================================================================================

//function for keyboard controls
document.onkeydown = keys;

//Decare object containing data about the currently displayed map
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
                variable: "<?php echo $Temp_name; ?>",
                season: "<?php echo $Day0_name; ?>",
                domain: "<?php echo $NHem_name; ?>",
                level: "<?php echo $P850_name; ?>",
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
       
        //Change variable based on passed argument, if any
        var passed_season = "";
        if(passed_season!=""){
                if(searchByName(passed_season,seasons)>=0){
                        imageObj.season = passed_season;
                }
        } 
        //Populate forecast hour and dprog/dt arrays for this run and frame
        populateMenu('variable');
        populateMenu('domain');
        populateMenu('level');
        populateMenu('season');
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
