# # TO RUN THIS FILE
# #   -python manage.py shell
# #   -exec(open('custom_scripts/load_bls_main.py').read())

# import logging
# import pandas as pd
# from data_capture.models import (bls_pricing, bls_lcat, bls_occupation_lcat_mapping,
#                                  bls_state_city_mapping, bls_state, bls_occs)
# import os

# logging.basicConfig(level=logging.INFO,
#                     filename='loadDataLog.log', filemode='w',
#                     format='%(asctime)s - %(levelname)s - %(message)s')


# class Loadblsmain():

#     def getCustomStateCode(city):
#         cus_statecode = "".join([c[0] for c in city.upper().split(' ')])[:6]
#         return "CUS_" + cus_statecode

#     def alterColum(col):
#         return col.lower().strip().replace(' ', '_').replace('\n', '_')

#     def getStateCodeFromCity(city):
#         arr = city.split(',')
#         if len(arr) > 1:
#             return arr[1].strip(), arr[0]
#         else:
#             return False, arr[0]

#     def __init__(self):
#         # FOR BLS DATA
#         xlpath = os.path.join(os.getcwd(), 'custom_scripts/BLS_main_data.xlsx')
#         sheetname = 'Main_data'
#         excell = pd.read_excel(xlpath, sheet_name=sheetname)
#         excell.columns = [alterColum(i) for i in excell.columns]

#     # DELETE BASIC TABLES
#     # bls_state_city_mapping.objects.all().delete()
#     # bls_occupation_lcat_mapping.objects.all().delete()
#     # bls_lcat.objects.all().delete()
#     # bls_occs.objects.all().delete()
#     # bls_pricing.objects.all().delete()

#     for index, row in excell.iterrows():
#         # state and city mapping
#         city = row['area_title']
#         stateCode, areaName = getStateCodeFromCity(city)
#         areaInstanceArr = []
#         if stateCode:
#             stateCodeArr = stateCode.split('-')
#             for stateCode in stateCodeArr:
#                 stateInstance = bls_state.objects.filter(state_code=str(stateCode).strip())
#                 if stateInstance:
#                     stateCityMappingInstance = bls_state_city_mapping.objects.filter(
#                         state=stateInstance[0], city=areaName)
#                     if not stateCityMappingInstance:
#                         stateCityMappingInstance = bls_state_city_mapping(
#                             state=stateInstance[0],
#                             city=areaName
#                         )
#                         stateCityMappingInstance.save()
#                         areaInstanceArr.append(stateCityMappingInstance)
#                         # logging.info('MAPPED'+areaName+stateCode)
#                     else:
#                         areaInstanceArr.append(stateCityMappingInstance[0])
#                         # logging.info('ALREADY EXISTS'+areaName+stateCode)
#                 else:
#                     areaInstanceArr.append(None)
#                     # logging.info('-------UNKNOWN STATE IN TABLE'+ stateCode)
#         else:
#             # making city as a state
#             custom_state_code = getCustomStateCode(city)
#             stateInstance = bls_state.objects.filter(
#                 state=str(city).strip()
#             )
#             if not stateInstance:  # creating new state DB  object if not exists
#                 stateInstance = bls_state(
#                     state_code=custom_state_code,
#                     state=str(city).strip()
#                 )
#                 stateInstance.save()
#             else:
#                 stateInstance = stateInstance[0]
#             stateCityMappingInstance = bls_state_city_mapping.objects.filter(state=stateInstance,
#                                                                              city=areaName)
#             if not stateCityMappingInstance:
#                 stateCityMappingInstance = bls_state_city_mapping(
#                     state=stateInstance,
#                     city=areaName
#                 )
#                 stateCityMappingInstance.save()
#                 areaInstanceArr.append(stateCityMappingInstance)
#                 # logging.info('MAPPED'+areaName+stateCode)
#             else:
#                 areaInstanceArr.append(stateCityMappingInstance[0])
#                 # logging.info('ALREADY EXISTS'+areaName+stateCode)
#         # for occupation
#         occupationCode = row['occ_code'].replace('-', '')
#         occupationTitle = str(row['occ_title']).strip()
#         ocupationInstance = bls_occs.objects.filter(occupation_code=occupationCode)
#         if not ocupationInstance:
#             ocupationInstance = bls_occs(occupation_code=occupationCode,
#                                          occupation=occupationTitle)
#             ocupationInstance.save()
#         # for lcat mapping
#         lcatTitle = str(row['oasis_lcats']).strip()
#         if lcatTitle == "":
#             lcatTitle = "ancillary"
#         lcatTitleInstance = bls_lcat.objects.filter(lcat_title=lcatTitle)
#         if not lcatTitleInstance:
#             # adding new lcattitle if not exists
#             lcatTitleInstance = bls_lcat(
#                 lcat_title=lcatTitle
#             )
#             lcatTitleInstance.save()
#         else:
#             lcatTitleInstance = lcatTitleInstance[0]
#         # mapping occs_code aaand lcat_title
#         # (this is only becase to extract the lcat title based on selected occuption)
#         occupationLcatIns = bls_occupation_lcat_mapping.objects.filter
#                             (occupation_code=occupationCode,lcat=lcatTitleInstance)
#         if not occupationLcatIns:
#             occupationLcatIns = bls_occupation_lcat_mapping(occupation_code=occupationCode,
#                                                             lcat=lcatTitleInstance)
#             occupationLcatIns.save()
#         # Main pricing table
#         for areaIns in areaInstanceArr:
#             blsPriceInstance = bls_pricing.objects.filter(
#                 occ_code=occupationCode,
#                 lcat_id=lcatTitleInstance,
#                 area_code=areaIns,
#             )
#             if blsPriceInstance:
#                 blsPriceInstance.delete()

#             h_mean = row['h_mean']
#             h_median_or_pct50 = row['h_median']
#             h_pct10 = row['h_pct10']
#             h_pct25 = row['h_pct25']
#             h_pct75 = row['h_pct75']
#             h_pct90 = row['h_pct90']
#             # making all price to 0 to handel null rows
#             if not isinstance(h_mean, float):
#                 h_mean = h_median_or_pct50 = h_pct10 = h_pct25 = h_pct75 = h_pct90 = 0.00
#             blsPriceInstance = bls_pricing(
#                 occ_code=occupationCode,
#                 lcat_id=lcatTitleInstance,
#                 area_code=areaIns,
#                 h_mean=h_mean,
#                 h_median=h_median_or_pct50,
#                 h_pct10=h_pct10,
#                 h_pct25=h_pct25,
#                 h_pct50=h_median_or_pct50,
#                 h_pct75=h_pct75,
#                 h_pct90=h_pct90,
#             )
#             blsPriceInstance.save()


# if __name__ == '__main__':
#     Loadblsmain()
