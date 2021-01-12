
# # TO RUN THIS FILE
# #   -python manage.py shell
# #   -exec(open('custom_scripts/bls_wages_load.py').read())
# import requests
# import json
# from data_capture.models import bls_series_wages
# from django.db.models import Q


# wageList = bls_series_wages.objects.filter(Q(city__isnull=True) |
#                                            Q(occupation_title__isnull=True))
# print('----------EMPTY-------------', wageList.count())
# # wageList = bls_series_wages.objects.filter(series_id = 'WMU00244201020000001500002506')
# headers = {'Content-type': 'application/json'}
# # a=0
# # b=0
# # c=0
# for wage in wageList:
#     series = [wage.series_id]
#     print(series)
#     dataParam = {"seriesid": series, "startyear": "2000", "endyear": "2020", "catalog": 'true',
#                  "calculations": 'true', "annualaverage": 'true', "aspects": 'true',
#                  "registrationkey": "8cca17e9a81a4f048ae000b023dfcabb"}
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
# '''
#     areatitle = wage

#     b += 1
#     if wage.city:
#         a = a+1
#     else:
#         print(wage.series_id)

#     if wage.occupation_title:
#         c = c+1

# print(a,b,c)
# '''


# print(bls_series_wages.objects.filter(Q(city__isnull=True) |
#                                       Q(occupation_title__isnull=True)).count())
