# TO RUN THIS FILE
#   -python manage.py shell
#   -exec(open('custom_scripts/load_bls.py').read())

import pandas as pd
from data_capture.models import (bls_lcat, bls_occupation_lcat_mapping)
import os


def alterColum(col):
    return col.lower().strip().replace(' ', '_').replace('\n', '_')


'''
#FOR BLS DATA
xlpath = os.path.join(os.getcwd(),'custom_scripts/BLS_Data_for_PET.xlsx')
sheetname = 'MWE_2018'
excell = pd.read_excel(xlpath,sheet_name=sheetname)
#making every column items lowercase
excell.columns = [alterColum(i) for i in excell.columns]

for index, row in excell.iterrows():
    if bls_data.objects.filter(series_id = row['series_id']):
        bls_data.objects.get(series_id = row['series_id']).delete()
        print('DELETED '+row['series_id']+' AND INSERTING AS NEW DATA')
    bls = bls_data(
        series_id = row['series_id'],
        series_title = row['series_title'],
        area_code = row['area_code'],
        area_level = row['area_level'],
        area_text = row['area_text'],
        occupation_code = row['occupation_code'],
        occupation_text = row['occupation_text'],
        job_char_code =row['job_characteristic_code'],
        job_char_text = row['job_characteristic_text'],
        work_level_code = row['work_level_code'],
        work_level_text = row['work_level_text'],
        average_hourly_wage = row['average_hourly_wage'],
        relative_std_error = row['relative_standard_error'],
        average_hourly_wage_footnote = row['average_hourly_wage_footnote'],
        relative_std_error_footnote = row['relative_standard_error_footnote'],
    )
    bls.save()
    print('INSERTED '+row['series_id'])
'''

# FOR LCAT DATA
xlpath = os.path.join(os.getcwd(),
                      'custom_scripts/OASIS_LCAT_CROSSWALK__TITLES_TO_CATS_4.1.2015.xlsx')
sheetname = 'LCAT'
excell = pd.read_excel(xlpath, sheet_name=sheetname)
# making every column items lowercase
excell.columns = [alterColum(i) for i in excell.columns]
for index, row in excell.iterrows():
    lcatName = row['maps_to_oasis_lcat_name']
    occupationCode = row['maps_to_omb_soc'][0:7].replace('-', '')
    lcatInstance = bls_lcat.objects.filter(lcat_title=lcatName)[0]
    if lcatInstance:
        if bls_occupation_lcat_mapping.objects.filter(occupation_code=occupationCode,
                                                      lcat=lcatInstance):
            print('Mapping Already There')
        else:
            mappingInstance = bls_occupation_lcat_mapping(
                occupation_code=occupationCode,
                lcat=lcatInstance
            )
            mappingInstance.save()
            print('Success')
    else:
        print('COULD NOT FIND THE GIVEN LCAT' + lcatName)

'''

# FOR CITY AND STATE

xlpath = os.path.join(os.getcwd(),'custom_scripts/cities.xlsx')
sheetname = 'CITIES'
excell = pd.read_excel(xlpath,sheet_name=sheetname)
# making every column items lowercase
excell.columns = [alterColum(i) for i in excell.columns]
for index, row in excell.iterrows():
    state_code = row['state']
    cityName = row['city']
    if isinstance(state_code, str):
        state_code = state_code.split('-')
        for state in state_code:
            stateInstance = bls_state.objects.filter(state_code = state.strip())
            if stateInstance:
                if not bls_state_city_mapping.objects.filter(state=stateInstance[0],
                                                             city=cityName):
                    stateCityMappingInstance = bls_state_city_mapping(
                        state=stateInstance[0],
                        city=cityName
                    )
                    stateCityMappingInstance.save()
                    print('MAPPED', cityName, state)
                else:
                    print('ALREADY EXISTS', cityName, state)

            else:
                print('-------UNKNOWN STATE' + state)
    else:
        print('*******NOT STRING', state_code)
'''
