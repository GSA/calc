# TO RUN THIS FILE
#   -python manage.py shell
#   -exec(open('custom_scripts/load_bls.py').read())
'''
import pandas as pd
from data_capture.models import (bls_series_wages)
import os


def alterColum(col):
    return col.lower().strip().replace(' ', '_').replace('\n', '_')



#FOR BLS DATA
xlpath = os.path.join(os.getcwd(),'custom_scripts/BLS_Data_for_PET.xlsx')
sheetname = 'MWE_2018'
excell = pd.read_excel(xlpath,sheet_name=sheetname)
#making every column items lowercase
excell.columns = [alterColum(i) for i in excell.columns]


series_id = models.TextField(blank=True, null=True)
    year = models.TextField(blank=True, null=True)
    period = models.TextField(blank=True, null=True)
    value = models.TextField(blank=True, null=True)
    footnote_codes = models.TextField(blank=True, null=True)
    occupation_code = models.TextField(blank=True, null=True)
    occupation_title = models.TextField(blank=True, null=True)
    lcat_id = models.TextField(blank=True, null=True)
    lcat_title = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    commerce_industry = models.TextField(blank=True, null=True)
    measure_data_type = models.TextField(blank=True, null=True)
    created_at = models.TextField(blank=True, null=True)
    updated_at = models.TextField(blank=True, null=True)
    period_name = models.TextField(blank=True, null=True)
    latest = models.TextField(blank=True, null=True)

for index, row in excell.iterrows():
    bls = get_or_create(
        series_id = row['series_id'],
        year = row['series_title'],
        value = row['area_code'],
        footnote_codes = row['area_level'],
        occupation_code = row['area_text'],
        occupation_title = row['occupation_code'],
        occupation_text = row['occupation_text'],
        lcat_id =row['job_characteristic_code'],
        lcat_title = row['job_characteristic_text'],
        city = row['work_level_code'],
        commerce_industry = row['work_level_text'],
        measure_data_type = row['average_hourly_wage'],
        created_at = row['relative_standard_error'],
        updated_at = row['average_hourly_wage_footnote'],
        relative_std_error_footnote = row['relative_standard_error_footnote'],
    )
    bls.save()
    print('INSERTED '+row['series_id'])


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
