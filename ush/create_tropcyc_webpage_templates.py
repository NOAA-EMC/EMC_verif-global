'''
Program Name: create_tropcyc_webpage_templates.py
Contact(s): Mallory Row
Abstract: This script is run by ../scripts/extropcyc.sh.
          It creates webpage templates based on user
          requested verification.
'''

import os
import get_tc_info

print("BEGIN: "+os.path.basename(__file__))

def write_template_header(template_filename):
    """! Writes common webpage header information to
         template
        
         Args:
             template_filename - string of the full
                                 file path to write to
 
         Returns:
    """
    template_type = template_filename.split('/')[-1].split('_')[0]
    template_file = open(template_filename, 'w')
    template_file.write(
        '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" '
        +'"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n'
    )
    template_file.write(
        '<html xmlns="http://www.w3.org/1999/xhtml" '
        +'xml:lang="en" lang="en">\n'
    )
    template_file.write('\n')
    template_file.write('<head>\n')
    template_file.write(
        '<meta http-equiv="content-type" content="text/html; '
        +'charset=utf-8" />\n'
    )
    template_file.write('<title>Home</title>\n')
    template_file.write(
        '<link href="../../main.css" rel="stylesheet" type="text/css" '
        +'media="all" />\n'
    )
    template_file.write(
        '<link href="../../fonts.css" rel="stylesheet" type="text/css" '
        +'media="all" />\n'
    )
    template_file.write(
        '<script src="https://d3js.org/d3.v4.min.js"></script>\n'
    )
    template_file.write(
        '<script src="../jquery-3.1.1.min.js"></script>\n'
    )
    template_file.write(
        '<script type="text/javascript" '
        +'src="../functions_metplus.js"></script>\n'
    )
    template_file.write(
        '<meta name="viewport" content="width=device-width, '
        +'initial-scale=1.0">\n'
    )
    template_file.write('</head>\n')
    template_file.write('\n')
    template_file.write('<?php\n')
    template_file.write(
        '$randomtoken = base64_encode( openssl_random_pseudo_bytes(32));\n'
    )
    template_file.write(
        "$_SESSION['csrfToken']=$randomtoken;\n"
    )
    template_file.write('?>\n')
    template_file.write('\n')
    template_file.write(
        '<?php include "'+template_type+'_globalvars.php"; ?>\n'
    )
    template_file.write('\n')
    template_file.close()

def write_template_body1(template_filename):
    """! Writes common webpage body information to
         template before the javascript domain
         assignment portion
        
         Args:
             template_filename - string of the full
                                 file path to write to
 
         Returns:
    """
    template_type = template_filename.split('/')[-1].split('_')[0]
    template_file = open(template_filename, 'a')
    template_file.write('<body>\n') 
    template_file.write('<div id="pageTitle">\n')
    template_file.write('<?php echo $stat_title; ?>\n') 
    template_file.write('</div>\n')
    template_file.write('<div class="page-menu"><div class="table">\n')
    template_file.write('        <div class="element">\n')
    template_file.write('                <span class="bold">Basin:</span>\n')
    template_file.write(
        '                <select id="maptype" '
        +'onchange="changeMaptype(this.value)"></select>\n'
    )
    template_file.write('        </div>\n')
    template_file.write('        <div class="element">\n')
    template_file.write('                <span class="bold">Name:</span>\n')
    template_file.write(
        '                <select id="domain" '
        +'onchange="changeDomain(this.value);"></select>\n'
    )
    template_file.write('        </div>\n')
    template_file.write('        <div class="element">\n')
    template_file.write(
        '                <span class="bold">Forecast Lead:</span>\n'
    )
    template_file.write(
        '                <select id="variable" '
        +'onchange="changeVariable(this.value)"></select>\n'
    )
    template_file.write('        </div>\n')
    template_file.write('</div></div>\n')
    template_file.write('\n')
    template_file.write('<!-- Middle menu -->\n')
    template_file.write('<div class="page-middle" id="page-middle">\n')
    template_file.write(
        'Left/Right arrow keys = Change forecast lead | Up/Down arrow keys '
        +'= Change Storm\n'
    )
    template_file.write(
        '<br>For information on tropical cyclone verification, '
        +'<button class="infobutton" id="myBtn">click here</button>\n'
    )
    template_file.write('<div id="myModal" class="modal">\n')
    template_file.write('  <div class="modal-content">\n')
    template_file.write('    <span class="close">&times;</span>\n')
    template_file.write('    Tropical Cyclone Verification Information\n')
    template_file.write(
        '    <embed width=100% height=100% src="../main.php">\n'
    )
    template_file.write('  </div>\n')
    template_file.write('</div>\n')
    template_file.write('<!-- /Middle menu -->\n')
    template_file.write('</div>\n')
    template_file.write('\n')
    template_file.write(
        '<div id="loading"><img style="width:100%" '
        +'src="../../images/loading.png"></div>\n'
    )
    template_file.write('\n')
    template_file.write('<!-- Image -->\n')
    template_file.write('<div id="page-map">\n')
    template_file.write('        <image name="map" style="width:100%">\n')
    template_file.write('</div>\n')
    template_file.write('\n')
    template_file.write('<script type="text/javascript">\n')
    template_file.write('// Get the modal\n')
    template_file.write('var modal = document.getElementById("myModal");\n')
    template_file.write('\n')
    template_file.write('// Get the button that opens the modal\n')
    template_file.write('var btn = document.getElementById("myBtn");\n')
    template_file.write('\n')
    template_file.write('// Get the <span> element that closes the modal\n')
    template_file.write(
        'var span = document.getElementsByClassName("close")[0];\n'
    )
    template_file.write('\n')
    template_file.write(
        '// When the user clicks the button, open the modal\n'
    )
    template_file.write('btn.onclick = function() {\n')
    template_file.write('  modal.style.display = "block";\n')
    template_file.write('}\n')
    template_file.write('\n')
    template_file.write(
        '// When the user clicks on <span> (x), close the modal\n'
    )
    template_file.write('span.onclick = function() {\n')
    template_file.write('  modal.style.display = "none";\n')
    template_file.write('}\n')
    template_file.write('\n')
    template_file.write(
        '// When the user clicks anywhere outside of the modal, close it\n'
    )
    template_file.write('window.onclick = function(event) {\n')
    template_file.write('  if (event.target == modal) {\n')
    template_file.write('    modal.style.display = "none";\n')
    template_file.write('  }\n')
    template_file.write('}\n')
    template_file.write(
        '//======================================================='
        +'=============================================\n'
    )
    template_file.write('//User-defined variables\n')
    template_file.write(
        '//======================================================='
        +'=============================================\n'
    )
    template_file.write('\n')
    template_file.write('//Global variables\n')
    template_file.write(
        'var minFrame = 0; //Minimum frame for every variable\n'
    )
    template_file.write(
        'var maxFrame = 26; //Maximum frame for every variable\n'
    )
    template_file.write(
        'var incrementFrame = 1; //Increment for every frame\n'
    )
    template_file.write('\n')
    template_file.write('var startFrame = 0; //Starting frame\n')
    template_file.write('\n')
    template_file.write('var cycle = 2018100600\n')
    template_file.write('\n')
    template_file.write('/*\n')
    template_file.write(
        'When constructing the URL below, DDD = domain, VVV = variable, '
        +'LLL = level, SSS = season, Y = frame number.\n'
    )
    template_file.write(
        'For X and Y, labeling one X or Y represents an integer '
        +'(e.g. 0, 10, 20). Multiple of these represent a string\n'
    )
    template_file.write(
        'format (e.g. XX = 00, 06, 12 --- XXX = 000, 006, 012).\n'
    )
    template_file.write('*/\n')
    template_file.write(
        'var url = "<?php echo $'+template_type+'_url; ?>";\n'
    )
    template_file.write('\n')
    template_file.write(
        '//======================================================='
        +'=============================================\n'
    )
    template_file.write('//Add variables & domains\n')
    template_file.write(
        '//======================================================='
        +'=============================================\n'
    )
    template_file.write('\n')
    template_file.write('var variables = [];\n')
    template_file.write('var domains = [];\n')
    template_file.write('var levels = [];\n')
    template_file.write('var seasons = [];\n')
    template_file.write('var maptypes = [];\n')
    template_file.write('var validtimes = [];\n')
    template_file.write('\n')
    template_file.write('\n')
    template_file.close()

def write_template_body2(template_filename):
    """! Writes common webpage body information to
         template after the javascript domain
         assignment portion
        
         Args:
             template_filename - string of the full
                                 file path to write to
 
         Returns:
    """
    template_type = template_filename.split('/')[-1].split('_')[0]
    basin = template_filename.split('/')[-1].split('_')[1].replace('.php', '')
    template_file = open(template_filename, 'a')
    template_file.write('domains.push({\n')
    template_file.write('        displayName: "All",\n')
    template_file.write('        name: "'+basin+'",\n')
    template_file.write('});\n')
    template_file.write('\n')
    template_file.write('\n')
    template_file.write('variables.push({\n')
    template_file.write('        displayName: "Mean",\n')
    template_file.write('        name: "<?php echo $LeadMean_name; ?>",\n')
    template_file.write('});\n')
    template_file.write('\n')
    template_file.write('\n')
    template_file.write('maptypes.push({\n')
    template_file.write('        url: "'+template_type+'_AL.php",\n')
    template_file.write('        displayName: "Atlantic",\n')
    template_file.write('        name: "'+template_type+'_AL",\n')
    template_file.write('});\n')
    template_file.write('maptypes.push({\n')
    template_file.write('        url: "'+template_type+'_CP.php",\n')
    template_file.write('        displayName: "Central Pacific",\n')
    template_file.write('        name: "'+template_type+'_CP",\n')
    template_file.write('});\n')
    template_file.write('maptypes.push({\n')
    template_file.write('        url: "'+template_type+'_EP.php",\n')
    template_file.write('        displayName: "Eastern Pacific",\n')
    template_file.write('        name: "'+template_type+'_EP",\n')
    template_file.write('});\n')
    template_file.write('maptypes.push({\n')
    template_file.write('        url: "'+template_type+'_WP.php",\n')
    template_file.write('        displayName: "Western Pacific",\n')
    template_file.write('        name: "'+template_type+'_WP",\n')
    template_file.write('});\n')
    template_file.write('\n')
    template_file.write(
        '//======================================================='
        +'=============================================\n'
    )
    template_file.write('//Initialize the page\n')
    template_file.write(
        '//======================================================='
        +'=============================================\n'
    )
    template_file.write('//function for keyboard controls\n')
    template_file.write('document.onkeydown = keys;\n')
    template_file.write('\n')
    template_file.write(
        '//Decare object containing data about the currently displayed map\n'
    )
    template_file.write('imageObj = {};\n')
    template_file.write('\n')
    template_file.write('//Initialize the page\n')
    template_file.write('initialize();\n')
    template_file.write('\n')
    template_file.write(
        '//Format initialized run date & return in requested format\n'
    )
    template_file.write('function formatDate(offset,format){\n')
    template_file.write('        var newdate = String(cycle);\n')
    template_file.write('        var yyyy = newdate.slice(0,4)\n')
    template_file.write('        var mm = newdate.slice(4,6);\n')
    template_file.write('        var dd = newdate.slice(6,8);\n')
    template_file.write('        var hh = newdate.slice(8,10);\n')
    template_file.write(
        '        var curdate = new Date(yyyy,parseInt(mm)-1,dd,hh)\n'
    )
    template_file.write('\n')
    template_file.write('\n')
    template_file.write('        //Offset by run\n')
    template_file.write(
        '        var newOffset = curdate.getHours() + offset;\n'
    )
    template_file.write('        curdate.setHours(newOffset);\n')
    template_file.write('\n')
    template_file.write(
        '        var yy = String(curdate.getFullYear()).slice(2,4);\n'
    )
    template_file.write('        yyyy = curdate.getFullYear();\n')
    template_file.write('        mm = curdate.getMonth()+1;\n')
    template_file.write('        dd = curdate.getDate();\n')
    template_file.write('        if(dd < 10){dd = "0" + dd;}\n')
    template_file.write('        hh = curdate.getHours();\n')
    template_file.write('        if(hh < 10){hh = "0" + hh;}\n')
    template_file.write('\n')
    template_file.write('        var wkday = curdate.getDay();\n')
    template_file.write(
        '        var day_str = ["Sun", "Mon", "Tue", "Wed", '
        +'"Thu", "Fri", "Sat"];\n'
    )
    template_file.write('\n')
    template_file.write('        //Return in requested format\n')
    template_file.write("        if(format == 'valid'){\n")
    template_file.write('//06Z Thu 03/22/18 (90 h)\n')
    template_file.write(
        'var txt = hh + "Z " + day_str[wkday] + " " + '
        +'mm + "/" + dd + "/" + yy;\n'
    )
    template_file.write('                return txt;\n')
    template_file.write('        }\n')
    template_file.write('}\n')
    template_file.write('\n')
    template_file.write('//Initialize the page\n')
    template_file.write('function initialize(){\n')
    template_file.write('\n')
    template_file.write(
        '        //Set image object based on default variables\n'
    )
    template_file.write('        imageObj = {\n')
    template_file.write(
       '                variable: "<?php echo $LeadMean_name; ?>",\n'
    )
    template_file.write('                domain: "'+basin+'"\n')
    template_file.write('        };\n')
    template_file.write('\n')
    template_file.write(
        '        //Change domain based on passed argument, if any\n'
    )
    template_file.write('        var passed_domain = "";\n')
    template_file.write('        if(passed_domain!=""){\n')
    template_file.write(
        '                if(searchByName(passed_domain,domains)>=0){\n'
    )
    template_file.write(
        '                        imageObj.domain = passed_domain;\n'
    )
    template_file.write('                }\n')
    template_file.write('        }\n')
    template_file.write('\n')
    template_file.write(
        '        //Change variable based on passed argument, if any\n'
    )
    template_file.write('        var passed_variable = "";\n')
    template_file.write('        if(passed_variable!=""){\n')
    template_file.write(
        '                if(searchByName(passed_variable,variables)>=0){\n'
    )
    template_file.write(
        '                        imageObj.variable = passed_variable;\n'
    )
    template_file.write('                }\n')
    template_file.write('        }\n')
    template_file.write('\n')
    template_file.write(
        '        //Populate forecast hour and dprog/dt arrays for this '
        +'run and frame\n'
    )
    template_file.write("        populateMenu('variable');\n")
    template_file.write("        populateMenu('domain');\n")
    template_file.write("        populateMenu('maptype')\n")
    template_file.write('\n')
    template_file.write('        //Populate the frames arrays\n')
    template_file.write('        frames = [];\n')
    template_file.write(
        '        for(i=minFrame;i<=maxFrame;i=i+incrementFrame)'
        +'{frames.push(i);}\n'
    )
    template_file.write('\n')
    template_file.write(
        '        //Predefine empty array for preloading images\n'
    )
    template_file.write('        for(i=0; i<variables.length; i++){\n')
    template_file.write('                variables[i].images = [];\n')
    template_file.write('                variables[i].loaded = [];\n')
    template_file.write('                variables[i].dprog = [];\n')
    template_file.write('        }\n')
    template_file.write('\n')
    template_file.write('        //Preload images and display map\n')
    template_file.write('        preload(imageObj);\n')
    template_file.write('        showImage();\n')
    template_file.write('\n')
    template_file.write('        //Update mobile display for swiping\n')
    template_file.write('        updateMobile();\n')
    template_file.write('\n')
    template_file.write('}\n')
    template_file.write('\n')
    template_file.write('var xInit = null;\n')
    template_file.write('var yInit = null;\n')
    template_file.write('var xPos = null;\n')
    template_file.write('var yPos = null;\n')
    template_file.write('\n')
    template_file.write('</script>\n')
    template_file.write('\n')
    template_file.write('</body>\n')
    template_file.write('</html>\n')
    template_file.close()

# Read in environment variables
config_storm_list = os.environ['tropcyc_storm_list'].split(' ')
DATA = os.environ['DATA']
RUN = os.environ['RUN']

# Check storm_list to see if all storms for basin and year
# requested
storm_list = []
for storm in config_storm_list:
    basin = storm.split('_')[0]
    year = storm.split('_')[1]
    name = storm.split('_')[2]
    if name == 'ALLNAMED':
        all_storms_in_basin_year_list = (
            get_tc_info.get_all_tc_storms_basin_year(basin, year)
        )
        for byn in all_storms_in_basin_year_list:
            storm_list.append(byn)
    else:
        storm_list.append(storm)

# Group storms by basin
AL_storm_list, CP_storm_list, EP_storm_list, WP_storm_list = [], [], [], []
for storm in storm_list:
    basin = storm.split('_')[0]
    if basin == 'AL':
        AL_storm_list.append(storm)
    elif basin == 'CP':
        CP_storm_list.append(storm) 
    elif basin == 'EP':
        EP_storm_list.append(storm)
    elif basin == 'WP':
        WP_storm_list.append(storm) 
basin_storms_dict = {
    'AL': AL_storm_list,
    'CP': CP_storm_list,
    'EP': EP_storm_list,
    'WP': WP_storm_list
}

# Create track and intensity error templates
trackerr_template_dir = os.path.join(DATA, RUN, 'create_webpage_templates',
                                    'trackerr')
if not os.path.exists(trackerr_template_dir):
    os.makedirs(trackerr_template_dir)
intensityerr_template_dir = os.path.join(DATA, RUN,
                                         'create_webpage_templates',
                                         'intensityerr')
if not os.path.exists(intensityerr_template_dir):
    os.makedirs(intensityerr_template_dir)
for basin in list(basin_storms_dict.keys()):
    basin_trackerr_filename = os.path.join(trackerr_template_dir,
                                           'trackerr_'+basin+'.php')
    basin_intensityerr_filename = os.path.join(intensityerr_template_dir,
                                              'intensityerr_'+basin+'.php')
    write_template_header(basin_trackerr_filename)
    write_template_header(basin_intensityerr_filename)
    write_template_body1(basin_trackerr_filename)
    write_template_body1(basin_intensityerr_filename)
    basin_trackerr_file = open(basin_trackerr_filename, 'a')
    basin_intensityerr_file = open(basin_intensityerr_filename, 'a')
    for storm in basin_storms_dict[basin]:
        basin = storm.split('_')[0]
        year = storm.split('_')[1]
        name = storm.split('_')[2]
        basin_trackerr_file.write('domains.push({\n')
        basin_trackerr_file.write(
            '        displayName: "'+name.title()+' ('+year+')",\n'
        )
        basin_trackerr_file.write('        name: "'+storm+'",\n')
        basin_trackerr_file.write('});\n')
        basin_intensityerr_file.write('domains.push({\n')
        basin_intensityerr_file.write(
            '        displayName: "'+name.title()+' ('+year+')",\n'
        )
        basin_intensityerr_file.write('        name: "'+storm+'",\n')
        basin_intensityerr_file.write('});\n')
    basin_trackerr_file.close()
    basin_intensityerr_file.close()
    write_template_body2(basin_trackerr_filename) 
    write_template_body2(basin_intensityerr_filename)   
 
print("END: "+os.path.basename(__file__))
