from os.path import exists
from datetime import datetime

from covid_db.datatypes.enums import Schemas, DataTypes
from covid_crawlers.africa.west_africa_data.WestAfricaPowerBI import WestAfricaPowerBI, get_globals
from covid_db.datatypes.DataPoint import DataPoint
from covid_crawlers.oceania.au_data.PowerBIDataReader import PowerBIDataReader
from world_geodata.LabelsToRegionChild import LabelsToRegionChild


class _WestAfricaPowerBI(PowerBIDataReader):
    def __init__(self, base_path, source_url):
        self.base_path = base_path
        self.source_url = source_url
        PowerBIDataReader.__init__(self, base_path, get_globals())
        self.ltrc = LabelsToRegionChild()

    def get_powerbi_data(self):
        r = []
        for updated_date, rev_id, response_dict in self._iter_all_dates():
            subdir = f'{self.base_path}/{updated_date}-{rev_id}'
            print("PROCESSING:", subdir)

            # Only use most revision if there isn't
            # a newer revision ID for a given day!
            next_id = rev_id + 1
            next_subdir = f'{self.base_path}/{updated_date}-{next_id}'
            if exists(next_subdir):
                print(f"West Africa PowerBI ignoring {subdir}")
                continue

            r.extend(self._get_regions_data(updated_date, response_dict))
        return r

    def _to_int(self, i):
        if not isinstance(i, str):
            return i
        return int(i.rstrip('L'))

    def _get_updated_date(self, updated_date, response_dict):
        ts = response_dict['updated_date'][1]
        ts = ts['result']['data']['dsr']['DS'][0]['PH'][0]['DM0'][0]['M0']

        if ts < 1000:
            # FIXME!! ==================================================================================================
            return None
        else:
            return datetime.fromtimestamp(ts/1000).strftime('%Y_%m_%d')

    def _get_regions_data(self, updated_date, response_dict):
        r = []
        data = response_dict['country_data'][1]

        previous_value = None
        SOURCE_URL = 'https://app.powerbi.com/view?r=eyJrIjoiZTRkZDhmMDctM2NmZi00NjRkLTgzYzMtYzI1MDMzNWI3NTRhIiwidCI6IjBmOWUzNWRiLTU0NGYtNGY2MC1iZGNjLTVlYTQxNmU2ZGM3MCIsImMiOjh9'

        def get_index(name):
            for x, i_dict in enumerate(data['result']['data']['descriptor']['Select']):
                i_name = i_dict['Name']
                if name.lower() in i_name.lower():
                    return x
            return None

        mappings = {
            #'admin0Name',
            #'admin1Name',
            'cas_confirm': DataTypes.TOTAL,
            'd\u00e9c\u00e8s': DataTypes.STATUS_DEATHS,
            'en_traitement': DataTypes.STATUS_HOSPITALIZED,
            'Gueris': DataTypes.STATUS_RECOVERED,
            'Femmes': DataTypes.TOTAL_FEMALE,
            'Hommes': DataTypes.TOTAL_MALE,

            #'Contacts_suivis': ,
            'Tests_effectues': DataTypes.TESTS_TOTAL,
            'cas_confirm\u00e9s': DataTypes.TOTAL,
        }

        mappings = {
            k: (v, get_index(k))
            for k, v in mappings.items()
            if get_index(k) is not None
        }

        #print(data['result']['data']['dsr']['DS'][0])
        region_dicts = data['result']['data']['dsr']['DS'][0]['PH'][1]['DM1']

        for region_dict in region_dicts:
            #print(region_dict, previous_value)
            value, previous_value = self.process_powerbi_value(region_dict, previous_value, data)

            if isinstance(value[0], int):
                value[0] = data['result']['data']['dsr']['DS'][0]['ValueDicts']['D0'][value[0]]

            if isinstance(value[1], int):
                value[1] = data['result']['data']['dsr']['DS'][0]['ValueDicts']['D1'][value[1]]

            while len(value) != 8:
                value.append(None)
            
            admin_0, admin_1 = value[:2]

            admin_0 = {
                'democratic republic of congo': 'cd',
                'republic of congo': 'cg',
                'guinea bissau': 'gw',
            }.get(admin_0.lower(), admin_0)

            #print(admin_0)

            for _, (datatype, index) in mappings.items():
                cases = value[index]

                if cases is not None:
                    r.append(DataPoint(
                        region_schema=Schemas.OCHA_ADMIN_1,
                        region_parent=self.ltrc.get_by_label(Schemas.ADMIN_0, '', admin_0, admin_0),
                        region_child=admin_1,
                        datatype=datatype,
                        value=int(cases),
                        date_updated=updated_date,
                        source_url=SOURCE_URL
                    ))
        return r


def get_powerbi_data():
    apb = _WestAfricaPowerBI(
        WestAfricaPowerBI.PATH_PREFIX,
        WestAfricaPowerBI.POWERBI_URL
    )
    return apb.get_powerbi_data()


if __name__ == '__main__':
    from pprint import pprint
    pprint(get_powerbi_data())
