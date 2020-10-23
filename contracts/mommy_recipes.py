from model_mommy.recipe import Recipe, seq
from contracts.models import Contract
from itertools import cycle

SCHEDULES = ('MOBIS', 'PES')
SINS = ('541-4B, 541-4BRC', '871 3')
piid = seq('123')


def get_contract_recipe(schedule=None, sin=None):
    return Recipe(
        Contract,
        idv_piid=seq('ABC123'),
        vendor_name=seq("CompanyName"),
        labor_category="Business Analyst II",
        schedule=schedule or cycle(SCHEDULES),
        sin=sin or cycle(SINS),
        min_years_experience=seq(5),
        hourly_rate_year1=seq('2'),
        current_price=seq('2'),
        next_year_price=seq('3'),
        second_year_price=seq('4'),
    )
