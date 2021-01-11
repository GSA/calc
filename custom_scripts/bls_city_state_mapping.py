# # TO RUN THIS FILE
# #   -python manage.py shell
# #   -exec(open('custom_scripts/bls_city_state_mapping.py').read())

# # import logging
# # import pandas as pd
# # import os
# from calc.data_capture.models import (bls_series_wages,
#                                  bls_wage_states_area_relation, bls_wage_states, bls_state)
# from django.db.models import Q


# def getStateCodeFromCity(city):
#     arr = city.split(',')
#     if len(arr) > 1:
#         return arr[1].strip().split('-'), arr[0]
#     else:
#         return False, arr[0]


# allPricingData = bls_series_wages.objects.filter(Q(city__isnull=False))


# for eachrow in allPricingData:
#     city = eachrow.city
#     stateCode, cityName = getStateCodeFromCity(city)
#     if not stateCode:
#         stateCode = [cityName]
#     for code in stateCode:
#         stateOldInstance = bls_state.objects.filter(state_code=code)
#         if stateOldInstance:
#             stateName = stateOldInstance[0].state
#         else:
#             stateName = code  # for metropolitan areas
#         print(stateName)
#         statetInstance, created = bls_wage_states.objects.get_or_create(state_code=code.strip(),
#                                                                         state=stateName.strip())
#         if statetInstance:
#             relationship = bls_wage_states_area_relation(
#                 city=eachrow,
#                 state=statetInstance
#             )
#             relationship.save()
