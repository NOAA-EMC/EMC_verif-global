'''
Program Name: get_tc_info.py
Contact(s): Mallory Row
Abstract: This script is called by get_data_files.py.
          This gets information of on
          tropical cyclones.
'''

import pandas as pd

def get_all_tc_storms_basin_year(basin, year):
    """! Gather list of all named storms in a given
         basin for a give year
        
         Args:
             basin - string of two letter basin identifier
             year  - string of four number year
 
         Returns:
             basin_year_storm_list - list of strings of
                                     names of storms
    """
    basin_year_names_dict = {}
    ## 2019
    basin_year_names_dict['AL_2019'] = ['ANDREA', 'BARRY', 'CHANTAL', 'DORIAN',
                                        'ERIN', 'FERNAND', 'GABRIELLE',
                                        'HUMBERTO', 'IMELDA', 'JERRY', 'KAREN',
                                        'LORENZO', 'NESTOR', 'OLGA', 'PABLO',
                                        'REBEKAH', 'SEBASTIEN']
    basin_year_names_dict['CP_2019'] = ['']
    basin_year_names_dict['EP_2019'] = ['ALVIN', 'BARBARA', 'COSME',
                                        'DALILA', 'ERICK', 'FLOSSIE', 'GIL',
                                        'HENRIETTE', 'IVO', 'JULIETTE', 'KIKO',
                                        'LORENA', 'MARIO', 'NARDA', 'OCTAVE',
                                        'PRISCILLA', 'RAYMOND']
    basin_year_names_dict['WP_2019'] = ['PABUK', 'WUTIP', 'SEPAT', 'MUN',
                                        'DANAS', 'NARI', 'WIPHA', 'FRANCISCO',
                                        'LEKIMA', 'KROSA', 'BAILU', 'PODUL',
                                        'LINGLING', 'KAJIKI', 'FAXAI',
                                        'PEIPAH', 'TAPAH', 'MITAG', 'HAGIBIS',
                                        'NEOGURI', 'BUALOI', 'MATMO', 'HALONG',
                                        'NAKRI', 'FENGSHEN',  'KALMAEGI',
                                        'FUNG-WONG', 'KAMMURI', 'PHANFONE']
    ## 2018
    basin_year_names_dict['AL_2018'] = ['ALBERTO', 'BERYL', 'CHRIS', 'DEBBY',
                                        'ERNESTO', 'FLORENCE', 'GORDON',
                                        'HELENE', 'ISAAC', 'JOYCE', 'KIRK',
                                        'LESILE', 'MICHAEL', 'NADINE', 'OSCAR']
    basin_year_names_dict['CP_2018'] = ['']
    basin_year_names_dict['EP_2018'] = ['ALETTA', 'BUD', 'CARLOTTA', 'DANIEL',
                                        'EMILIA', 'FABIO', 'GILMA', 'HECTOR',
                                        'ILEANA', 'JOHN', 'KRISTY', 'LANE',
                                        'MIRIAM', 'NORMAN', 'OLIVIA', 'PAUL',
                                        'ROSA', 'SERGIO', 'TARA', 'VICENTE',
                                        'WILLA', 'XAVIER']
    basin_year_names_dict['WP_2018'] = ['BOLAVEN', 'SANBA', 'JELAWAT',
                                        'EWINIAR', 'MALIKSI', 'GAEMI',
                                        'PRAPIROON', 'MARIA', 'SON-TINH',
                                        'AMPIL', 'WUKONG', 'JONGDARI',
                                        'SHANSHAN', 'YAGI', 'LEEPI', 'BEBINCA',
                                        'HECTOR', 'RUMBIA', 'SOULIK',
                                        'CIMARON', 'JEBI', 'MANGKHUT',
                                        'BARIJAT', 'TRAMI', 'KONG-REY', 'YUTU',
                                        'TORAJI', 'MAN-YI', 'USAGI']
    ## 2017
    basin_year_names_dict['AL_2017'] = ['ARLENE', 'BRET', 'CINDY', 'DON',
                                        'EMILY', 'FRANKLIN', 'GERT', 'HARVEY',
                                        'IRMA', 'JOSE', 'KATIA', 'LEE',
                                        'MARIA', 'NATE', 'OPHELIA', 'PHILIPPE',
                                        'RINA']
    basin_year_names_dict['CP_2017'] = ['']
    basin_year_names_dict['EP_2017'] = ['ADRIAN', 'BEATRIZ', 'CALVIN', 'DORA',
                                        'EUGENE', 'FERNANDA', 'GREG', 'HILARY',
                                        'IRWIN', 'JOVA', 'KENNETH', 'LIDIA',
                                        'OTIS', 'MAX', 'NORMA', 'PILAR',
                                        'RAMON', 'SELMA']
    basin_year_names_dict['WP_2017'] = ['MUFIA', 'MERBOK', 'NANMADOL', 'TALAS',
                                        'NORU', 'KULAP', 'ROKE', 'SONCA',
                                        'NESAT', 'HAITANG', 'NALGAE', 'BANYAN',
                                        'HATO', 'PAKHAR', 'SANVU', 'MAWAR',
                                        'GUCHOL', 'TALIM', 'DOKSURI', 'KHANUN',
                                        'LAN', 'SAOLA', 'DAMREY', 'HAIKUI',
                                        'KIROGI', 'KAI-TAK', 'TEMBIN']
    if basin+'_'+year not in list(basin_year_names_dict.keys()):
       print("ERROR: "+basin+" "+year+"is not currently supported at this "
              +"time")
    elif basin_year_names_dict[basin+'_'+year] == ['']:
        print("ERROR: no storms for "+basin+" "+year)
        exit(1)
    else:
        basin_year_storm_list = []
        for name in basin_year_names_dict[basin+'_'+year]:
            basin_year_name = basin+'_'+year+'_'+name
            basin_year_storm_list.append(basin_year_name)
    return basin_year_storm_list

def get_tc_storm_id(storm):
    """! Get storm identification for a named storm
         in a given basin for a give year
        
         Args:
             storm - string containing basin, year, and name
                     information of a storm (BB_YYYY_name)
 
         Returns:
             storm_id - string of the storm's identification
    """
    storm_id_dict = {}
    ## 2019
    storm_id_dict['AL_2019_ANDREA'] = 'al012019'
    storm_id_dict['AL_2019_BARRY'] = 'al022019'
    storm_id_dict['AL_2019_CHANTAL'] = 'al042019'
    storm_id_dict['AL_2019_DORIAN'] = 'al052019'
    storm_id_dict['AL_2019_ERIN'] = 'al062019'
    storm_id_dict['AL_2019_FERNAND'] = 'al072019'
    storm_id_dict['AL_2019_GABRIELLE'] = 'al082019'
    storm_id_dict['AL_2019_HUMBERTO'] = 'al092019'
    storm_id_dict['AL_2019_IMELDA'] = 'al112019'
    storm_id_dict['AL_2019_JERRY'] = 'al102019'
    storm_id_dict['AL_2019_KAREN'] = 'al122019'
    storm_id_dict['AL_2019_LORENZO'] = 'al132019'
    storm_id_dict['AL_2019_MELISSA'] = 'al142019'
    storm_id_dict['AL_2019_NESTOR'] = 'al162019'
    storm_id_dict['AL_2019_OLGA'] = 'al172019'
    storm_id_dict['AL_2019_PABLO'] = 'al182019'
    storm_id_dict['AL_2019_REBEKAH'] = 'al192019'
    storm_id_dict['AL_2019_SEBASTIEN'] = 'al202019'
    storm_id_dict['EP_2019_ALVIN'] = 'ep012019'
    storm_id_dict['EP_2019_BARBARA'] = 'ep022019'
    storm_id_dict['EP_2019_COSME'] = 'ep032019'
    storm_id_dict['EP_2019_DALILA'] = 'ep052019'
    storm_id_dict['EP_2019_ERICK'] = 'ep062019'
    storm_id_dict['EP_2019_FLOSSIE'] = 'ep072019'
    storm_id_dict['EP_2019_GIL'] = 'ep082019'
    storm_id_dict['EP_2019_HENRIETTE'] = 'ep092019'
    storm_id_dict['EP_2019_IVO'] = 'ep102019'
    storm_id_dict['EP_2019_JULIETTE'] = 'ep112019'
    storm_id_dict['EP_2019_KIKO'] = 'ep132019'
    storm_id_dict['EP_2019_LORENA'] = 'ep152019'
    storm_id_dict['EP_2019_MARIO'] = 'ep142019'
    storm_id_dict['EP_2019_NARDA'] = 'ep162019'
    storm_id_dict['EP_2019_OCTAVE'] = 'ep182019'
    storm_id_dict['EP_2019_PRISCILLA'] = 'ep192019'
    storm_id_dict['EP_2019_RAYMOND'] = 'ep202019'
    storm_id_dict['WP_2019_PABUK'] = 'wp362018'
    storm_id_dict['WP_2019_WUTIP'] = 'wp022019'
    storm_id_dict['WP_2019_SEPAT'] = 'wp042019'
    storm_id_dict['WP_2019_MUN'] = 'wp052019'
    storm_id_dict['WP_2019_DANAS'] = 'wp062019'
    storm_id_dict['WP_2019_NARI'] = 'wp072019'
    storm_id_dict['WP_2019_WIPHA'] = 'wp082019'
    storm_id_dict['WP_2019_FRANCISCO'] = 'wp092019'
    storm_id_dict['WP_2019_LEKIMA'] = 'wp102019'
    storm_id_dict['WP_2019_KROSA'] = 'wp112019'
    storm_id_dict['WP_2019_BAILU'] = 'wp122019'
    storm_id_dict['WP_2019_PODUL'] = 'wp132019'
    storm_id_dict['WP_2019_LINGLING'] = 'wp152019'
    storm_id_dict['WP_2019_KAJIKI'] = 'wp162019'
    storm_id_dict['WP_2019_FAXAI'] = 'wp142019'
    storm_id_dict['WP_2019_PEIPAH'] = 'wp172019'
    storm_id_dict['WP_2019_TAPAH'] = 'wp182019'
    storm_id_dict['WP_2019_MITAG'] = 'wp192019'
    storm_id_dict['WP_2019_HAGIBIS'] = 'wp202019'
    storm_id_dict['WP_2019_NEOGURI'] = 'wp212019'
    storm_id_dict['WP_2019_BUALOI'] = 'wp222019'
    storm_id_dict['WP_2019_MATMO'] = 'wp232019'
    storm_id_dict['WP_2019_HALONG'] = 'wp242019'
    storm_id_dict['WP_2019_NAKRI'] = 'wp252019'
    storm_id_dict['WP_2019_FENGSHEN'] = 'wp262019'
    storm_id_dict['WP_2019_KALMAEGI'] = 'wp272019'
    storm_id_dict['WP_2019_FUNG-WONG'] = 'wp282019'
    storm_id_dict['WP_2019_KAMMURI'] = 'wp292019'
    storm_id_dict['WP_2019_PHANFONE'] = 'wp302019'
    ## 2018
    storm_id_dict['AL_2018_ALBERTO'] = 'al012018'
    storm_id_dict['AL_2018_BERYL'] = 'al022018'
    storm_id_dict['AL_2018_CHRIS'] = 'al032018'
    storm_id_dict['AL_2018_DEBBY'] = 'al042018'
    storm_id_dict['AL_2018_ERNESTO'] = 'al052018'
    storm_id_dict['AL_2018_FLORENCE'] = 'al062018'
    storm_id_dict['AL_2018_GORDON'] = 'al072018'
    storm_id_dict['AL_2018_HELENE'] = 'al082018'
    storm_id_dict['AL_2018_ISAAC'] = 'al092018'
    storm_id_dict['AL_2018_JOYCE'] = 'al102018'
    storm_id_dict['AL_2018_KIRK'] = 'al122018'
    storm_id_dict['AL_2018_LESILE'] = 'al132018'
    storm_id_dict['AL_2018_MICHAEL'] = 'al142018'
    storm_id_dict['AL_2018_NADINE']  = 'al152018'
    storm_id_dict['AL_2018_OSCAR'] = 'al162018'
    storm_id_dict['EP_2018_ALETTA'] = 'ep022018'
    storm_id_dict['EP_2018_BUD'] = 'ep032018'
    storm_id_dict['EP_2018_CARLOTTA'] = 'ep042018'
    storm_id_dict['EP_2018_DANIEL'] = 'ep052018'
    storm_id_dict['EP_2018_EMILIA'] = 'ep062018'
    storm_id_dict['EP_2018_FABIO'] = 'ep072018'
    storm_id_dict['EP_2018_GILMA'] = 'ep082018'
    storm_id_dict['EP_2018_HECTOR'] = 'ep102018'
    storm_id_dict['EP_2018_ILEANA'] = 'ep112018'
    storm_id_dict['EP_2018_JOHN'] = 'ep122018'
    storm_id_dict['EP_2018_KRISTY'] = 'ep132018'
    storm_id_dict['EP_2018_LANE'] = 'ep142018'
    storm_id_dict['EP_2018_MIRIAM'] = 'ep152018'
    storm_id_dict['EP_2018_NORMAN'] = 'ep162018'
    storm_id_dict['EP_2018_OLIVIA'] = 'ep172018'
    storm_id_dict['EP_2018_PAUL'] = 'ep182018'
    storm_id_dict['EP_2018_ROSA'] = 'ep202018'
    storm_id_dict['EP_2018_SERGIO'] = 'ep212018'
    storm_id_dict['EP_2018_TARA'] = 'ep222018'
    storm_id_dict['EP_2018_VICENTE'] = 'ep232018'
    storm_id_dict['EP_2018_WILLA'] = 'ep242018'
    storm_id_dict['EP_2018_XAVIER'] = 'ep252018'
    storm_id_dict['WP_2018_BOLAVEN'] = 'wp012018'
    storm_id_dict['WP_2018_SANBA'] = 'wp022018'
    storm_id_dict['WP_2018_JELAWAT'] = 'wp032018'
    storm_id_dict['WP_2018_EWINIAR'] = 'wp052018'
    storm_id_dict['WP_2018_MALIKSI'] = 'wp062018'
    storm_id_dict['WP_2018_GAEMI'] = 'wp082018'
    storm_id_dict['WP_2018_PRAPIROON'] = 'wp092018'
    storm_id_dict['WP_2018_MARIA'] = 'wp102018'
    storm_id_dict['WP_2018_SON-TINH'] = 'wp112018'
    storm_id_dict['WP_2018_AMPIL'] = 'wp122018'
    storm_id_dict['WP_2018_WUKONG'] = 'wp142018'
    storm_id_dict['WP_2018_JONGDARI'] = 'wp152018'
    storm_id_dict['WP_2018_SHANSHAN'] = 'wp172018'
    storm_id_dict['WP_2018_YAGI'] = 'wp182018'
    storm_id_dict['WP_2018_LEEPI'] = 'wp192018'
    storm_id_dict['WP_2018_BEBINCA'] = 'wp202018'
    storm_id_dict['WP_2018_HECTOR'] = 'ep102018'
    storm_id_dict['WP_2018_RUMBIA'] = 'wp212018'
    storm_id_dict['WP_2018_SOULIK'] = 'wp222018'
    storm_id_dict['WP_2018_CIMARON'] = 'wp232018'
    storm_id_dict['WP_2018_JEBI'] = 'wp252018'
    storm_id_dict['WP_2018_MANGKHUT'] = 'wp262018'
    storm_id_dict['WP_2018_BARIJAT'] = 'wp272018'
    storm_id_dict['WP_2018_TRAMI'] = 'wp282018'
    storm_id_dict['WP_2018_KONG-REY'] = 'wp302018'
    storm_id_dict['WP_2018_YUTU'] = 'wp312018'
    storm_id_dict['WP_2018_TORAJI'] = 'wp322018'
    storm_id_dict['WP_2018_MAN-YI'] = 'wp342018'
    storm_id_dict['WP_2018_USAGI'] = 'wp332018'
    ## 2017
    storm_id_dict['AL_2017_ARLENE'] = 'al012017'
    storm_id_dict['AL_2017_BRET'] = 'al022017'
    storm_id_dict['AL_2017_CINDY'] = 'al032017'
    storm_id_dict['AL_2017_DON'] = 'al052017'
    storm_id_dict['AL_2017_EMILY'] = 'al062017'
    storm_id_dict['AL_2017_FRANKLIN'] = 'al072017'
    storm_id_dict['AL_2017_GERT'] = 'al082017'
    storm_id_dict['AL_2017_HARVEY'] = 'al092017'
    storm_id_dict['AL_2017_IRMA'] = 'al112017'
    storm_id_dict['AL_2017_JOSE'] = 'al122017'
    storm_id_dict['AL_2017_KATIA'] = 'al132017'
    storm_id_dict['AL_2017_LEE'] = 'al142017'
    storm_id_dict['AL_2017_MARIA'] = 'al152017'
    storm_id_dict['AL_2017_NATE'] = 'al162017'
    storm_id_dict['AL_2017_OPHELIA'] = 'al172017'
    storm_id_dict['AL_2017_PHILIPPE'] = 'al182017'
    storm_id_dict['AL_2017_RINA'] = 'al192017'
    storm_id_dict['EP_2017_ADRIAN'] = 'ep012017'
    storm_id_dict['EP_2017_BEATRIZ'] = 'ep022017'
    storm_id_dict['EP_2017_CALVIN'] = 'ep032017'
    storm_id_dict['EP_2017_DORA'] = 'ep042017'
    storm_id_dict['EP_2017_EUGENE'] = 'ep052017'
    storm_id_dict['EP_2017_FERNANDA'] = 'ep062017'
    storm_id_dict['EP_2017_GREG'] = 'ep072017'
    storm_id_dict['EP_2017_HILARY'] = 'ep092017'
    storm_id_dict['EP_2017_IRWIN'] = 'ep102017'
    storm_id_dict['EP_2017_JOVA'] = 'ep122017'
    storm_id_dict['EP_2017_KENNETH'] = 'ep132017'
    storm_id_dict['EP_2017_LIDIA'] = 'ep142017'
    storm_id_dict['EP_2017_OTIS'] = 'ep152017'
    storm_id_dict['EP_2017_MAX'] = 'ep162017'
    storm_id_dict['EP_2017_NORMA'] = 'ep172017'
    storm_id_dict['EP_2017_PILAR'] = 'ep182017'
    storm_id_dict['EP_2017_RAMON'] = 'ep192018'
    storm_id_dict['EP_2017_SELMA'] = 'ep202017'
    storm_id_dict['WP_2017_MUFIA'] = 'wp032017'
    storm_id_dict['WP_2017_MERBOK'] = 'wp042017'
    storm_id_dict['WP_2017_NANMADOL'] = 'wp052017'
    storm_id_dict['WP_2017_TALAS'] = 'wp062017'
    storm_id_dict['WP_2017_NORU'] = 'wp072017'
    storm_id_dict['WP_2017_KULAP'] = 'wp092017'
    storm_id_dict['WP_2017_ROKE'] = 'wp102017'
    storm_id_dict['WP_2017_SONCA'] = 'wp082017'
    storm_id_dict['WP_2017_NESAT'] = 'wp112017'
    storm_id_dict['WP_2017_HAITANG'] = 'wp122017'
    storm_id_dict['WP_2017_NALGAE'] = 'wp132017'
    storm_id_dict['WP_2017_BANYAN'] = 'wp142017'
    storm_id_dict['WP_2017_HATO'] = 'wp152017'
    storm_id_dict['WP_2017_PAKHAR'] = 'wp162017'
    storm_id_dict['WP_2017_SANVU'] = 'wp172017'
    storm_id_dict['WP_2017_MAWAR'] = 'wp182017'
    storm_id_dict['WP_2017_GUCHOL'] = 'wp192017'
    storm_id_dict['WP_2017_TALIM'] = 'wp202017'
    storm_id_dict['WP_2017_DOKSURI'] = 'wp212017'
    storm_id_dict['WP_2017_KHANUN'] = 'wp242017'
    storm_id_dict['WP_2017_LAN'] = 'wp252017'
    storm_id_dict['WP_2017_SAOLA'] = 'wp272017'
    storm_id_dict['WP_2017_DAMREY'] = 'wp282017'
    storm_id_dict['WP_2017_HAIKUI'] = 'wp302017'
    storm_id_dict['WP_2017_KIROGI'] = 'wp312017'
    storm_id_dict['WP_2017_KAI-TAK'] = 'wp322017'
    storm_id_dict['WP_2017_TEMBIN'] = 'wp332017'
    if storm not in list(storm_id_dict.keys()):
       print("ERROR: "+storm+" is not currently supported at this "
              +"time")
       exit(1)
    else:
       storm_id = storm_id_dict[storm]
    return storm_id

def get_tc_storm_dates(bdeck_file):
    """! Get storm start and end dates for a named storm
         in a given basin for a give year
        
         Args: 
             basin - string of two letter basin identifier
             year  - string of four number year
             name  - strinf of storm name
 
         Returns:
             storm_start_date - string of the storm's start
                                date (YYYYMMDD)
             storm_end_date   - string of the storm's end
                                date (YYYYMMDD)
    """
    # Per NHC verification, verification only done for
    # tropical or subtropical, excludes tropical waves,
    # [remnant] low, and extratropical
    bdeck_cols = ['BASIN', 'CY', 'YYYYMMDDHH', 'TECHNUM/MIN', 'TECH', 'TAU',
                  'LatN/S', 'LonE/W', 'VMAX', 'MSLP', 'TY', 'RAD', 'WINDCODE',
                  'RAD1', 'RAD2', 'RAD3', 'RAD4', 'POUTER', 'ROUTER', 'RMW',
                  'GUSTS', 'EYE', 'SUBREGION', 'MAXSEAS', 'INITIALS', 'DIR',
                  'SPEED', 'STORMNAME', 'DEPTH', 'SEAS', 'SEASCODE', 'SEAS1',
                  'SEAS2', 'SEAS3', 'SEAS4', 'USERDEFINED1', 'userdata1',
                  'USERDEFINED2', 'userdata2', 'USERDEFINED3', 'userdata3',
                  'USERDEFINED4', 'userdata4', 'USERDEFINED5', 'userdata5',
                  'misc']
    bdeck_data = pd.read_csv(
        bdeck_file, sep=",",
        skipinitialspace=True, header=None,
        names=bdeck_cols
    )
    storm_date_list = bdeck_data['YYYYMMDDHH'].tolist()
    storm_start_date = str(storm_date_list[0])
    storm_end_date = str(storm_date_list[-1])
    return storm_start_date, storm_end_date
