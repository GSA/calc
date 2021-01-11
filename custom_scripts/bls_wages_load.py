
# # TO RUN THIS FILE
# #   -python manage.py shell
# #   -exec(open('custom_scripts/bls_wages_load.py').read())
# import requests
# import json
# from data_capture.models import bls_series_wages

# wageList = bls_series_wages.objects.filter(id__gte="337931")
# headers = {'Content-type': 'application/json'}
# for wage in wageList:
#     series = [wage.series_id]
#     print(series)
#     dataParam = {"seriesid": series, "startyear": "2000", "endyear": "2020", "catalog": 'true',
#                  "calculations": 'true', "annualaverage": 'true', "aspects": 'true',
#                  "registrationkey": "0a1f266b053b44a799d95f936b28a871"}
#     inputdata = json.dumps(dataParam)
#     res = requests.post('https://api.bls.gov/publicAPI/v1/timeseries/data/',
#                         data=inputdata, headers=headers)
#     data = res.json()

#     area_code = ''
#     occu_title = ''

#     if data['status'] and data['status'].lower() == 'request_succeeded':
#         if data['Results'] and len(data['Results']):
#             area_code = data['Results']['series'][0]['catalog']['area']
#             occu_title = data['Results']['series'][0]['catalog']['occupation']
#     if area_code != '':
#         wage.city = area_code

#     if occu_title != '':
#         wage.occupation_title = occu_title

#     wage.save()
