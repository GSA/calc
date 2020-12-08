from datetime import datetime

from contracts.models import Contract

FEDERAL_MIN_CONTRACT_RATE = 10.20


class Region10Loader(object):
    @classmethod
    def make_contract(cls, line, upload_source=None):
        if line[0]:
            # create contract record, unique to vendor, labor cat
            idv_piid = line[11]
            vendor_name = line[10]
            labor_category = line[0].strip().replace('\n', ' ')

            contract = Contract()
            contract.idv_piid = idv_piid
            contract.labor_category = labor_category
            contract.vendor_name = vendor_name

            contract.education_level = contract.get_education_code(
                line[6]
            )
            contract.schedule = line[12]
            contract.business_size = line[8]
            current_contract_year = int(float(line[14]))
            contract.contract_year = current_contract_year
            contract.sin = line[13]

            if line[15] != '':
                contract.contract_start = datetime.strptime(
                    line[15], '%m/%d/%Y').date()
            if line[16] != '':
                contract.contract_end = datetime.strptime(
                    line[16], '%m/%d/%Y').date()

            if line[7].strip() != '':
                contract.min_years_experience = int(float(line[7]))
            else:
                contract.min_years_experience = 0

            if line[1] and line[1] != '':
                contract.hourly_rate_year1 = contract.normalize_rate(
                    line[1]
                )
            else:
                # there's no pricing info
                raise ValueError('missing price')

            for count, rate in enumerate(line[2:6]):
                if rate and rate.strip() != '':
                    setattr(contract, 'hourly_rate_year' +
                            str(count + 2),
                            contract.normalize_rate(rate))

            if line[14] and line[14] != '':
                price_fields = {
                    'current_price': getattr(contract,
                                             'hourly_rate_year' +
                                             str(current_contract_year), 0)
                }
                # we have up to five years of rate data
                if current_contract_year < 5:
                    price_fields['next_year_price'] = getattr(
                        contract, 'hourly_rate_year' +
                        str(current_contract_year + 1), 0
                    )
                    if current_contract_year < 4:
                        price_fields['second_year_price'] = getattr(
                            contract, 'hourly_rate_year' +
                            str(current_contract_year + 2), 0
                        )

                # don't create display prices for records where the
                # rate is under the federal minimum contract rate
                for field in price_fields:
                    price = price_fields.get(field)
                    if price and price >= FEDERAL_MIN_CONTRACT_RATE:
                        setattr(contract, field, price)

            contract.contractor_site = line[9]

            if upload_source:
                contract.upload_source = upload_source

            return contract
        else:
            raise ValueError('missing labor category')
