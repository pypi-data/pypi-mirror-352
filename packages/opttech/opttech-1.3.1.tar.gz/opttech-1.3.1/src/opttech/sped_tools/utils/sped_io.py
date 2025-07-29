import os
import json
from ...parameters.sped.constants import *
from ...parameters.constants import ENCODING


def load_sped_dictionary( sped : str, version : str, sped_by_version : str, competencia : str = '' ) -> dict:

    # GET FILE_NAME
    if sped != 'ECD':
        file_name = f'{sped} - LEIAUTE_{version}.json'

    elif sped == 'ECD':
        file_name = None
        if competencia == '':
            for year in sped_by_version:
                if year == version:
                    file_name = f"{sped} - LEIAUTE_{sped_by_version[year]['version']} - VERSAO_{year}.json"
                    break
        else:
            file_name = f'{sped} - LEIAUTE_{version} - VERSAO_{competencia}.json'

    # else:
    #     file_name = f'{sped} - LEIAUTE_{sped_by_version[version]["version"]} - VERSAO_{version}.json'

    file_path = os.path.join(SPED_RULES_FOLDER, file_name)

    if os.path.isfile(file_path) is False:
        return False

    f_in = open(file_path, mode='r', encoding=ENCODING, newline='')
    sped_dict = json.loads(f_in.read())
    f_in.close()

    # FATHER
    for reg in sped_dict:
        if 'pai' not in sped_dict[reg]:
            sped_dict[reg]['pai'] = ''

    return sped_dict

