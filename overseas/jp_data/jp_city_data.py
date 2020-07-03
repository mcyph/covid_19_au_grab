import csv
from covid_19_au_grab.get_package_dir import (
    get_package_dir
)


def get_tokyo_cities_to_en_map():
    r = {}
    with open(get_package_dir() /
              'overseas' /
              'jp_city_data'/
              'tokyo_cities.csv', 'r', encoding='utf-8') as f:

        for item in csv.DictReader(f, delimiter='\t'):
            r[item['ja'].strip()] = item['en'].strip()
            for c in '区町村市島':
                r[item['ja'].strip().rstrip(c)] = item['en'].strip()
    return r



