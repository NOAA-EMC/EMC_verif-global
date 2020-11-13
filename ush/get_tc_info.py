'''
Program Name: get_tc_info.py
Contact(s): Mallory Row
Abstract: This script is called by get_data_files.py.
          This gets information of on
          tropical cyclones.
'''

import pandas as pd

def get_tc_dict():
    """! Get supported TC dictionary

         Args:

         Returns:
             tc_dict - dictionary of TC's basin_year_name
                       as key and ID as the value
    """
    tc_dict = {}
    ## 2020
    storm_id_dict['AL_2020_ARTHUR'] = 'al012020'
    storm_id_dict['AL_2020_BERTHA'] = 'al022020'
    storm_id_dict['AL_2020_CRISTOBAL'] = 'al032020'
    storm_id_dict['AL_2020_DOLLY'] = 'al042020'
    storm_id_dict['AL_2020_EDOUARD'] = 'al052020'
    storm_id_dict['AL_2020_FAY'] = 'al062020'
    storm_id_dict['AL_2020_GONZALO'] = 'al072020'
    storm_id_dict['AL_2020_HANNA'] = 'al082020'
    storm_id_dict['AL_2020_ISAIAS'] = 'al092020'
    storm_id_dict['AL_2020_TEN'] = 'al102020'
    storm_id_dict['AL_2020_JOSEPHINE'] = 'al112020'
    storm_id_dict['AL_2020_KYLE'] = 'al122020'
    storm_id_dict['AL_2020_LAURA'] = 'al132020'
    storm_id_dict['AL_2020_MARCO'] = 'al142020'
    storm_id_dict['AL_2020_OMAR'] = 'al152020'
    storm_id_dict['AL_2020_NANA'] = 'al162020'
    storm_id_dict['AL_2020_PAULETTE'] = 'al172020'
    storm_id_dict['AL_2020_RENE'] = 'al182020'
    storm_id_dict['AL_2020_SALLY'] = 'al192020'
    storm_id_dict['AL_2020_TEDDY'] = 'al202020'
    storm_id_dict['AL_2020_VICKY'] = 'al212020'
    storm_id_dict['AL_2020_BETA'] = 'al222020'
    storm_id_dict['AL_2020_WILFRED'] = 'al232020'
    storm_id_dict['AL_2020_ALPHA'] = 'al242020'
    storm_id_dict['AL_2020_GAMMA'] = 'al252020'
    storm_id_dict['AL_2020_DELTA'] = 'al262020'
    storm_id_dict['AL_2020_EPSILON'] = 'al272020'
    storm_id_dict['AL_2020_ZETA'] = 'al282020'
    storm_id_dict['AL_2020_ETA'] = 'al292020'
    storm_id_dict['AL_2020_THETA'] = 'al302020'
    storm_id_dict['EP_2020_ONE'] = 'ep012020'
    storm_id_dict['EP_2020_AMANDA'] = 'ep022020'
    storm_id_dict['EP_2020_BORIS'] = 'ep032020'
    storm_id_dict['EP_2020_FOUR'] = 'ep042020'
    storm_id_dict['EP_2020_CRISTINA'] = 'ep052020'
    storm_id_dict['EP_2020_SIX'] = 'ep062020'
    storm_id_dict['EP_2020_SEVEN'] = 'ep072020'
    storm_id_dict['EP_2020_DOUGLAS'] = 'ep082020'
    storm_id_dict['EP_2020_ELIDA'] = 'ep092020'
    storm_id_dict['EP_2020_TEN'] = 'ep102020'
    storm_id_dict['EP_2020_FAUSTO'] = 'ep112020'
    storm_id_dict['EP_2020_GENEVIEVE'] = 'ep122020'
    storm_id_dict['EP_2020_HERNAN'] = 'ep132020'
    storm_id_dict['EP_2020_ISELLE'] = 'ep142020'
    storm_id_dict['EP_2020_JULIO'] = 'ep152020'
    storm_id_dict['EP_2020_KARINA'] = 'ep162020'
    storm_id_dict['EP_2020_LOWELL'] = 'ep172020'
    storm_id_dict['EP_2020_MARIE'] = 'ep182020'
    storm_id_dict['EP_2020_NORBERT'] = 'ep192020'
    storm_id_dict['EP_2020_ODALYS'] = 'ep202020'
    storm_id_dict['WP_2020_VONGFONG'] = 'wp012020'
    storm_id_dict['WP_2020_NURI'] = 'wp022020'
    storm_id_dict['WP_2020_HAGUPIT'] = 'wp032020'
    storm_id_dict['WP_2020_SINLAKU'] = 'wp042020'
    storm_id_dict['WP_2020_JANGMI'] = 'wp052020'
    storm_id_dict['WP_2020_SIX'] = 'wp062020'
    storm_id_dict['WP_2020_MEKKHALA'] = 'wp072020'
    storm_id_dict['WP_2020_HIGOS'] = 'wp082020'
    storm_id_dict['WP_2020_BAVI'] = 'wp092020'
    storm_id_dict['WP_2020_MAYSAK'] = 'wp102020'
    storm_id_dict['WP_2020_HAISHEN'] = 'wp112020'
    storm_id_dict['WP_2020_TWELVE'] = 'wp122020'
    storm_id_dict['WP_2020_NOUL'] = 'wp132020'
    storm_id_dict['WP_2020_DOLPHIN'] = 'wp142020'
    storm_id_dict['WP_2020_KUJIRA'] = 'wp152020'
    storm_id_dict['WP_2020_CHAN-HOM'] = 'wp162020'
    storm_id_dict['WP_2020_LINFA'] = 'wp172020'
    storm_id_dict['WP_2020_NANGKA'] = 'wp182020'
    storm_id_dict['WP_2020_SAUDEL'] = 'wp192020'
    storm_id_dict['WP_2020_TWENTY'] = 'wp202020'
    storm_id_dict['WP_2020_MOLAVE'] = 'wp212020'
    storm_id_dict['WP_2020_GONI'] = 'wp222020'
    storm_id_dict['WP_2020_ATSANI'] = 'wp232020'
    storm_id_dict['WP_2020_ETAU'] = 'wp242020'
    storm_id_dict['WP_2020_VAMCO'] = 'wp252020'
    ## 2019
    tc_dict['AL_2019_ANDREA'] = 'al012019'
    tc_dict['AL_2019_BARRY'] = 'al022019'
    tc_dict['AL_2019_THREE'] = 'al032019'
    tc_dict['AL_2019_CHANTAL'] = 'al042019'
    tc_dict['AL_2019_DORIAN'] = 'al052019'
    tc_dict['AL_2019_ERIN'] = 'al062019'
    tc_dict['AL_2019_FERNAND'] = 'al072019'
    tc_dict['AL_2019_GABRIELLE'] = 'al082019'
    tc_dict['AL_2019_HUMBERTO'] = 'al092019'
    tc_dict['AL_2019_JERRY'] = 'al102019'
    tc_dict['AL_2019_IMELDA'] = 'al112019'
    tc_dict['AL_2019_KAREN'] = 'al122019'
    tc_dict['AL_2019_LORENZO'] = 'al132019'
    tc_dict['AL_2019_MELISSA'] = 'al142019'
    tc_dict['AL_2019_FIFTEEN'] = 'al152019'
    tc_dict['AL_2019_NESTOR'] = 'al162019'
    tc_dict['AL_2019_OLGA'] = 'al172019'
    tc_dict['AL_2019_PABLO'] = 'al182019'
    tc_dict['AL_2019_REBEKAH'] = 'al192019'
    tc_dict['AL_2019_SEBASTIEN'] = 'al202019'
    tc_dict['CP_2019_EMA'] = 'cp012019'
    tc_dict['EP_2019_ALVIN'] = 'ep012019'
    tc_dict['EP_2019_BARBARA'] = 'ep022019'
    tc_dict['EP_2019_COSME'] = 'ep032019'
    tc_dict['EP_2019_FOUR'] = 'ep042019'
    tc_dict['EP_2019_DALILA'] = 'ep052019'
    tc_dict['EP_2019_ERICK'] = 'ep062019'
    tc_dict['EP_2019_FLOSSIE'] = 'ep072019'
    tc_dict['EP_2019_GIL'] = 'ep082019'
    tc_dict['EP_2019_HENRIETTE'] = 'ep092019'
    tc_dict['EP_2019_IVO'] = 'ep102019'
    tc_dict['EP_2019_JULIETTE'] = 'ep112019'
    tc_dict['EP_2019_AKONI'] = 'ep122019'
    tc_dict['EP_2019_KIKO'] = 'ep132019'
    tc_dict['EP_2019_MARIO'] = 'ep142019'
    tc_dict['EP_2019_LORENA'] = 'ep152019'
    tc_dict['EP_2019_NARDA'] = 'ep162019'
    tc_dict['EP_2019_OCTAVE'] = 'ep182019'
    tc_dict['EP_2019_PRISCILLA'] = 'ep192019'
    tc_dict['EP_2019_RAYMOND'] = 'ep202019'
    tc_dict['EP_2019_TWENTY-ONE'] = 'ep212019'
    tc_dict['WP_2019_PABUK'] = 'wp362018'
    tc_dict['WP_2019_ONE'] = 'wp012019'
    tc_dict['WP_2019_WUTIP'] = 'wp022019'
    tc_dict['WP_2019_THREE'] = 'wp032019'
    tc_dict['WP_2019_FOUR'] = 'wp042019'
    tc_dict['WP_2019_MUN'] = 'wp052019'
    tc_dict['WP_2019_DANAS'] = 'wp062019'
    tc_dict['WP_2019_NARI'] = 'wp072019'
    tc_dict['WP_2019_WIPHA'] = 'wp082019'
    tc_dict['WP_2019_FRANCISCO'] = 'wp092019'
    tc_dict['WP_2019_LEKIMA'] = 'wp102019'
    tc_dict['WP_2019_KROSA'] = 'wp112019'
    tc_dict['WP_2019_BAILU'] = 'wp122019'
    tc_dict['WP_2019_PODUL'] = 'wp132019'
    tc_dict['WP_2019_FAXAI'] = 'wp142019'
    tc_dict['WP_2019_LINGLING'] = 'wp152019'
    tc_dict['WP_2019_KAJIKI'] = 'wp162019'
    tc_dict['WP_2019_PEIPAH'] = 'wp172019'
    tc_dict['WP_2019_TAPAH'] = 'wp182019'
    tc_dict['WP_2019_MITAG'] = 'wp192019'
    tc_dict['WP_2019_HAGIBIS'] = 'wp202019'
    tc_dict['WP_2019_NEOGURI'] = 'wp212019'
    tc_dict['WP_2019_BUALOI'] = 'wp222019'
    tc_dict['WP_2019_MATMO'] = 'wp232019'
    tc_dict['WP_2019_HALONG'] = 'wp242019'
    tc_dict['WP_2019_NAKRI'] = 'wp252019'
    tc_dict['WP_2019_FENGSHEN'] = 'wp262019'
    tc_dict['WP_2019_KALMAEGI'] = 'wp272019'
    tc_dict['WP_2019_FUNG-WONG'] = 'wp282019'
    tc_dict['WP_2019_KAMMURI'] = 'wp292019'
    tc_dict['WP_2019_PHANFONE'] = 'wp302019'
    ## 2018
    tc_dict['AL_2018_ALBERTO'] = 'al012018'
    tc_dict['AL_2018_BERYL'] = 'al022018'
    tc_dict['AL_2018_CHRIS'] = 'al032018'
    tc_dict['AL_2018_DEBBY'] = 'al042018'
    tc_dict['AL_2018_ERNESTO'] = 'al052018'
    tc_dict['AL_2018_FLORENCE'] = 'al062018'
    tc_dict['AL_2018_GORDON'] = 'al072018'
    tc_dict['AL_2018_HELENE'] = 'al082018'
    tc_dict['AL_2018_ISAAC'] = 'al092018'
    tc_dict['AL_2018_JOYCE'] = 'al102018'
    tc_dict['AL_2018_ELEVEN'] = 'al112018'
    tc_dict['AL_2018_KIRK'] = 'al122018'
    tc_dict['AL_2018_LESLIE'] = 'al132018'
    tc_dict['AL_2018_MICHAEL'] = 'al142018'
    tc_dict['AL_2018_NADINE']  = 'al152018'
    tc_dict['AL_2018_OSCAR'] = 'al162018'
    tc_dict['CP_2018_WALAKA'] = 'cp012018'
    tc_dict['EP_2018_ONE'] = 'ep012018'
    tc_dict['EP_2018_ALETTA'] = 'ep022018'
    tc_dict['EP_2018_BUD'] = 'ep032018'
    tc_dict['EP_2018_CARLOTTA'] = 'ep042018'
    tc_dict['EP_2018_DANIEL'] = 'ep052018'
    tc_dict['EP_2018_EMILIA'] = 'ep062018'
    tc_dict['EP_2018_FABIO'] = 'ep072018'
    tc_dict['EP_2018_GILMA'] = 'ep082018'
    tc_dict['EP_2018_NINE'] = 'ep092018'
    tc_dict['EP_2018_HECTOR'] = 'ep102018'
    tc_dict['EP_2018_ILEANA'] = 'ep112018'
    tc_dict['EP_2018_JOHN'] = 'ep122018'
    tc_dict['EP_2018_KRISTY'] = 'ep132018'
    tc_dict['EP_2018_LANE'] = 'ep142018'
    tc_dict['EP_2018_MIRIAM'] = 'ep152018'
    tc_dict['EP_2018_NORMAN'] = 'ep162018'
    tc_dict['EP_2018_OLIVIA'] = 'ep172018'
    tc_dict['EP_2018_PAUL'] = 'ep182018'
    tc_dict['EP_2018_NINETEEN'] = 'ep192018'
    tc_dict['EP_2018_ROSA'] = 'ep202018'
    tc_dict['EP_2018_SERGIO'] = 'ep212018'
    tc_dict['EP_2018_TARA'] = 'ep222018'
    tc_dict['EP_2018_VICENTE'] = 'ep232018'
    tc_dict['EP_2018_WILLA'] = 'ep242018'
    tc_dict['EP_2018_XAVIER'] = 'ep252018'
    tc_dict['WP_2018_BOLAVEN'] = 'wp012018'
    tc_dict['WP_2018_SANBA'] = 'wp022018'
    tc_dict['WP_2018_JELAWAT'] = 'wp032018'
    tc_dict['WP_2018_FOUR'] = 'wp042018'
    tc_dict['WP_2018_EWINIAR'] = 'wp052018'
    tc_dict['WP_2018_MALIKSI'] = 'wp062018'
    tc_dict['WP_2018_SEVEN'] = 'wp072018'
    tc_dict['WP_2018_GAEMI'] = 'wp082018'
    tc_dict['WP_2018_PRAPIROON'] = 'wp092018'
    tc_dict['WP_2018_MARIA'] = 'wp102018'
    tc_dict['WP_2018_SON-TINH'] = 'wp112018'
    tc_dict['WP_2018_AMPIL'] = 'wp122018'
    tc_dict['WP_2018_THIRTEEN'] = 'wp132018'
    tc_dict['WP_2018_WUKONG'] = 'wp142018'
    tc_dict['WP_2018_JONGDARI'] = 'wp152018'
    tc_dict['WP_2018_SIXTEEN'] = 'wp162018'
    tc_dict['WP_2018_SHANSHAN'] = 'wp172018'
    tc_dict['WP_2018_YAGI'] = 'wp182018'
    tc_dict['WP_2018_LEEPI'] = 'wp192018'
    tc_dict['WP_2018_BEBINCA'] = 'wp202018'
    tc_dict['WP_2018_HECTOR'] = 'ep102018'
    tc_dict['WP_2018_RUMBIA'] = 'wp212018'
    tc_dict['WP_2018_SOULIK'] = 'wp222018'
    tc_dict['WP_2018_CIMARON'] = 'wp232018'
    tc_dict['WP_2018_TWENTYFOUR'] = 'wp242018'
    tc_dict['WP_2018_JEBI'] = 'wp252018'
    tc_dict['WP_2018_MANGKHUT'] = 'wp262018'
    tc_dict['WP_2018_BARIJAT'] = 'wp272018'
    tc_dict['WP_2018_TRAMI'] = 'wp282018'
    tc_dict['WP_2018_TWENTYNINE'] = 'wp292018'
    tc_dict['WP_2018_KONG-REY'] = 'wp302018'
    tc_dict['WP_2018_YUTU'] = 'wp312018'
    tc_dict['WP_2018_TORAJI'] = 'wp322018'
    tc_dict['WP_2018_USAGI'] = 'wp332018'
    tc_dict['WP_2018_MAN-YI'] = 'wp342018'
    tc_dict['WP_2018_THIRTYFIVE'] = 'wp352018'
    tc_dict['WP_2018_THIRTYSIX'] = 'wp362018'
    return tc_dict

def get_tc_dates(bdeck_file):
    """! Get storm start and end dates for a named storm
         in a given basin for a give year

         Args:
             basin - string of two letter basin identifier
             year  - string of four number year
             name  - string of storm name

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
    storm_TY_list = bdeck_data['TY'].tolist()
    idx = 0
    for storm_TY in storm_TY_list:
        if storm_TY not in ['DB', 'LO', 'WV']:
            break
        else:
            idx+=1
    storm_date_list = bdeck_data['YYYYMMDDHH'].tolist()
    storm_start_date = str(storm_date_list[idx])
    storm_end_date = str(storm_date_list[-1])
    return storm_start_date, storm_end_date
