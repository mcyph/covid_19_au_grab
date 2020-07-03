import json
from pyquery import PyQuery as pq
from os import listdir
from collections import Counter

from covid_19_au_grab.overseas.URLBase import (
    URL, URLBase
)
from covid_19_au_grab.datatypes.DataPoint import (
    DataPoint
)
from covid_19_au_grab.datatypes.constants import (
    SCHEMA_ADMIN_1, DT_TESTS_TOTAL,
    DT_TOTAL, DT_STATUS_RECOVERED, DT_STATUS_DEATHS
)
from covid_19_au_grab.get_package_dir import (
    get_overseas_dir, get_package_dir
)

# الخرطوم
# الجزيرة
# القضارف
# شمال كردفان
# سنار
# كسلا
# جنوب دارفور
# شمال دارفور
# النيل الابيض
# غرب دارفور
# نهر النيل
# شرق دارفور
# الشمالية
# غرب كردفان
# البحر الأحمر
# النيل الأزرق
# جنوب كردفان
# وسط دارفور

# Khartoum
# Al Jazeera
# Gedaref
# North Kordofan
# Sennar
# ???
# South Darfur
# North Darfur
# White Nile
# West Darfur
# The Nile River
# East Darfur
# North
# West Kordofan
# The Red Sea
# Blue Nile
# South Kordofan
# Central Darfur

region_map = {
    'الخرطوم': 'SD-KH',
    'الجزيرة': 'SD-GZ',
    'القضارف': 'SD-GD',
    'شمال كردفان': 'SD-KN',
    'سنار': 'SD-SI',
    'كسلا': 'SD-KA',
    'جنوب دارفور': 'SD-DS',
    'شمال دارفور': 'SD-DN',
    'النيل الابيض': 'SD-NW',
    'غرب دارفور': 'SD-DW',
    'نهر النيل': 'SD-NR',
    'شرق دارفور': 'SD-DE',
    'الشمالية': 'SD-NO',
    'غرب كردفان': 'SD-GK',
    'البحر الأحمر': 'SD-RS',
    'النيل الأزرق': 'SD-NB',
    'جنوب كردفان': 'SD-KS',
    'وسط دارفور': 'SD-DC',
}


class SDData(URLBase):
    SOURCE_URL = 'https://covid19.sd/'
    SOURCE_DESCRIPTION = ''
    SOURCE_ID = 'sd_gov'

    def __init__(self):
        URLBase.__init__(self,
            output_dir=get_overseas_dir() / 'sd' / 'data',
            urls_dict={
                'index.html': URL('https://covid19.sd/',
                                  static_file=False)
            }
        )
        self.update()

    def get_datapoints(self):
        r = []
        r.extend(self._get_recovered_sum())
        return r

    def _get_recovered_sum(self):
        r = []
        base_dir = self.get_path_in_dir('')

        for date in sorted(listdir(base_dir)):
            path = f'{base_dir}/{date}/index.html'
            with open(path, 'r', encoding='utf-8') as f:
                html = f.read()

            for region, total in pq(html)('#DataTables_Table_0 tbody:contains("الخرطوم") tr'):
                region = pq(region).text().strip()
                total = int(pq(total).text().strip())

                r.append(DataPoint(
                    region_schema=SCHEMA_ADMIN_1,
                    region_parent='SD',
                    region_child=region_map[region],
                    datatype=DT_TOTAL,
                    value=total,
                    date_updated=date,
                    source_url=self.SOURCE_URL
                ))

        return r


if __name__ == '__main__':
    from pprint import pprint
    pprint(SDData().get_datapoints())
