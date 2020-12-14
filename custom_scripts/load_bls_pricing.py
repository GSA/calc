# TO RUN THIS FILE
#   -python manage.py shell
#   -exec(open('custom_scripts/load_bls_pricing.py').read())

# import logging
import pandas as pd
import os
from data_capture.models import bls_wage_pricing


def alterColum(col):
    return col.lower().strip().replace(' ', '_').replace('\n', '_')


existingData = bls_wage_pricing.objects.all()
existingData.delete()

xlpath = os.path.join(os.getcwd(), 'custom_scripts/BLS_main_data.xlsx')
sheetname = 'Main_data'
excell = pd.read_excel(xlpath, sheet_name=sheetname)
excell.columns = [alterColum(i) for i in excell.columns]


for index, row in excell.iterrows():
    occupationCode = row['occ_code'].replace('-', '')
    area = row['area_title']
    print(index, area, occupationCode)
    h_mean = row['h_mean']
    h_median_or_pct50 = row['h_median']
    h_pct10 = row['h_pct10']
    h_pct25 = row['h_pct25']
    h_pct75 = row['h_pct75']
    h_pct90 = row['h_pct90']
    if not isinstance(h_mean, float):
        h_mean = h_median_or_pct50 = h_pct10 = h_pct25 = h_pct75 = h_pct90 = 0.00
    blsPriceInstance = bls_wage_pricing(
        occ_code=occupationCode,
        area=area,
        h_mean=h_mean,
        h_median=h_median_or_pct50,
        h_pct10=h_pct10,
        h_pct25=h_pct25,
        h_pct50=h_median_or_pct50,
        h_pct75=h_pct75,
        h_pct90=h_pct90,
    )
    blsPriceInstance.save()
