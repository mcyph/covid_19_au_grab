# https://www.data.gouv.fr/fr/organizations/sante-publique-france/
# https://www.data.gouv.fr/fr/datasets/donnees-relatives-aux-resultats-des-tests-virologiques-covid-19/#_

# article:contains(...) footer div a:contains(Télécharger)
# 'sp-pos-quot-dep-2020-07-03-19h15.csv'
# 'sp-pos-quot-reg-2020-07-03-19h15.csv'
# 'sp-pos-quot-fra-2020-07-03-19h15.csv'

# Colonne	Type 	Description_FR	Description_EN	Exemple
# dep	String	Departement	State	01
# reg	String	Region	region	2.0
# fra	String	France	France	FR
# jour	Date	Jour	Day	2020-05-13
# week	Date	Semaine	Week	2020-S21
# pop	integer	Population de reference (du departement, de la région, nationale)	Reference population (department, region, national)	656955.0
# t	integer	Nombre de test réalisés	Number of tests performed	2141.0
# cl_age90	integer	Classe d'age	Age class	09
# p	integer	Nombre de test positifs	Number of positive tests	34.0
# p_h	integer	Nombre de test positif chez les hommes	Number of positive test in men	1688.0
# t_h	integer	Nombre de test effectués chez les hommes	Number of tests performed on men	93639.0
# p_f	integer	Nombre de test positif chez les femmes	Number of positive test in women	2415.0
# t_f	integer	Nombre de test effectués chez les femmes	Number of tests performed on women	122725.0


import csv
import json
import datetime
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
    SCHEMA_ADMIN_0, SCHEMA_ADMIN_1,
    DT_TESTS_TOTAL, DT_TOTAL,
    DT_STATUS_RECOVERED, DT_STATUS_DEATHS, DT_STATUS_ACTIVE
)
from covid_19_au_grab.get_package_dir import (
    get_overseas_dir, get_package_dir
)


class FRGovData(URLBase):
    SOURCE_URL = 'https://www.data.gouv.fr/fr/organizations/sante-publique-france/'
    SOURCE_DESCRIPTION = ''
    SOURCE_ID = 'fr_sante_publique'

    def __init__(self):
        URLBase.__init__(self,
            output_dir=get_overseas_dir() / 'fr' / 'govdata',
            urls_dict=self.__get_urls_dict()
        )
        self.update()

    def __get_urls_dict(self):
        _URL = 'https://www.data.gouv.fr/fr/datasets/donnees-relatives-aux-resultats-des-tests-virologiques-covid-19/'
        html = pq(_URL)
        r = {}

        for typ, key in (
            (
                'Taux de positivité - quotidien - département',
                'daily_positive_by_department.csv'
            ),
            (
                'Taux de positivité - quotidien - région',
                'daily_positive_by_region.csv'
            ),
            (
                'Taux de positivité - quotidien - france',
                'daily_positive_national.csv'
            ),
        ):
            r[key] = URL(
                html(f'article:contains("{typ}") '
                     f'footer '
                     f'div '
                     f'a:contains("Télécharger")').attr('href'),
                static_file=False
            )

        return r

    def get_datapoints(self):
        r = []
        r.extend(self._get_positive_by_department())
        return r

    def _get_positive_by_department(self):
        # dep	jour	P	T	cl_age90
        # 1	2020-05-13	0	16	9
        # 1	2020-05-13	1	17	19
        r = []
        f = self.get_file('daily_positive_by_department.csv',
                          include_revision=True)

        positive_totals = Counter()
        tests_totals = Counter()
        above_90_years_totals = Counter()

        for item in csv.DictReader(f, delimiter=';'):
            date = self.convert_date(item['jour'])
            try:
                region_child = 'FR-%02d' % int(item['dep'])
            except ValueError:
                # e.g. 2A
                region_child = 'FR-%s' % item['dep']

            positive_totals[region_child] += int(item['P'])
            tests_totals[region_child] += int(item['T'])
            above_90_years_totals[region_child] += int(item['cl_age90'])

            r.append(DataPoint(
                region_schema=SCHEMA_ADMIN_1,
                region_parent='FR',
                region_child=region_child,
                datatype=DT_TOTAL,
                value=positive_totals[region_child],
                date_updated=date,
                source_url=self.SOURCE_URL
            ))

            r.append(DataPoint(
                region_schema=SCHEMA_ADMIN_1,
                region_parent='FR',
                region_child=region_child,
                datatype=DT_TESTS_TOTAL,
                value=tests_totals[region_child],
                date_updated=date,
                source_url=self.SOURCE_URL
            ))

        return r


if __name__ == '__main__':
    from pprint import pprint
    pprint(FRGovData().get_datapoints())