import csv
from collections import Counter

from covid_19_au_grab.overseas.URLBase import (
    URL, URLBase
)
from covid_19_au_grab.get_package_dir import (
    get_overseas_dir
)
from covid_19_au_grab.state_news_releases.DataPoint import (
    DataPoint
)
from covid_19_au_grab.state_news_releases.constants import (
    SCHEMA_CO_MUNICIPALITY,
    SCHEMA_ADMIN_0, SCHEMA_ADMIN_1,
    DT_TOTAL, DT_TOTAL_MALE, DT_TOTAL_FEMALE,
    DT_STATUS_DEATHS, DT_STATUS_RECOVERED,
    DT_SOURCE_OVERSEAS, DT_SOURCE_CONFIRMED,
    DT_SOURCE_UNDER_INVESTIGATION
)


class COData(URLBase):
    SOURCE_URL = 'https://data.humdata.org/dataset/positive-cases-of-covid-19-in-colombia'
    SOURCE_LICENSE = ''

    GEO_DIR = ''
    GEO_URL = ''
    GEO_LICENSE = ''

    def __init__(self):
        # Only raw_data4.json is currently being updated,
        # so won't download the others every day
        URLBase.__init__(self,
             output_dir=get_overseas_dir() / 'co' / 'data',
             urls_dict={
                 'co_data.csv': URL(
                     'https://proxy.hxlstandard.org/data.csv?'
                     'dest=data_edit&tagger-match-all=on&tagger-01-header=id+de+caso&'
                     'tagger-01-tag=%23meta+%2Bid&tagger-02-header=fecha+de+notificacion&'
                     'tagger-02-tag=%23date+%2Bnotification&tagger-03-header=codigo+divipola&'
                     'tagger-03-tag=%23code&tagger-04-header=ciudad+de+ubicacion&tagger-04-tag=%23adm3+%2Bname&'
                     'tagger-05-header=departamento+o+distrito&tagger-05-tag=%23adm2+%2Bname&'
                     'tagger-06-header=atencion&tagger-06-tag=%23indicator+%2Binfected+%2Btype&'
                     'tagger-07-header=edad&tagger-07-tag=%23indicator+%2Binfected+%2Bage&'
                     'tagger-08-header=sexo&tagger-08-tag=%23indicator+%2Binfected+%2Bsex&'
                     'tagger-10-header=estado&tagger-10-tag=%23indicator+%2Binfected+%2Bstatus&'
                     'tagger-11-header=pais+de+procedencia&tagger-11-tag=%23indicator+%2Binfected+%2Borigin&'
                     'tagger-13-header=fecha+de+muerte&tagger-13-tag=%23date+%2Breported+%2Bdeath&'
                     'tagger-14-header=fecha+diagnostico&tagger-14-tag=%23date+%2Breported+%2Bnotification&'
                     'tagger-15-header=fecha+recuperado&tagger-15-tag=%23date+%2Breported+%2Brecovered&'
                     'tagger-16-header=fecha+reporte+web&tagger-16-tag=%23date+%2Breported&header-row=1&'
                     'url=https%3A%2F%2Fwww.datos.gov.co%2Fapi%2Fviews%2Fgt2j-8ykr%2Frows.csv%3FaccessType%3DDOWNLOAD',
                     static_file=False
                 ),
             }
        )
        self.update()

    def get_datapoints(self):
        r = []
        r.extend(self._get_co_data())
        return r

    def _get_co_data(self):
        r = []
        
        # # https://proxy.hxlstandard.org/data.csv?dest=data_edit&tagger-match-all=on&tagger-01-header=id+de+caso&tagger-01-tag=%23meta+%2Bid&tagger-02-header=fecha+de+notificacion&tagger-02-tag=%23date+%2Bnotification&tagger-03-header=codigo+divipola&tagger-03-tag=%23code&tagger-04-header=ciudad+de+ubicacion&tagger-04-tag=%23adm3+%2Bname&tagger-05-header=departamento+o+distrito&tagger-05-tag=%23adm2+%2Bname&tagger-06-header=atencion&tagger-06-tag=%23indicator+%2Binfected+%2Btype&tagger-07-header=edad&tagger-07-tag=%23indicator+%2Binfected+%2Bage&tagger-08-header=sexo&tagger-08-tag=%23indicator+%2Binfected+%2Bsex&tagger-10-header=estado&tagger-10-tag=%23indicator+%2Binfected+%2Bstatus&tagger-11-header=pais+de+procedencia&tagger-11-tag=%23indicator+%2Binfected+%2Borigin&tagger-13-header=fecha+de+muerte&tagger-13-tag=%23date+%2Breported+%2Bdeath&tagger-14-header=fecha+diagnostico&tagger-14-tag=%23date+%2Breported+%2Bnotification&tagger-15-header=fecha+recuperado&tagger-15-tag=%23date+%2Breported+%2Brecovered&tagger-16-header=fecha+reporte+web&tagger-16-tag=%23date+%2Breported&header-row=1&url=https%3A%2F%2Fwww.datos.gov.co%2Fapi%2Fviews%2Fgt2j-8ykr%2Frows.csv%3FaccessType%3DDOWNLOAD
        # #
        # # ID de caso,Fecha de notificación,Codigo DIVIPOLA,Ciudad de ubicación,
        # # Departamento o Distrito ,atención,Edad,Sexo,Tipo,Estado,País de procedencia,
        # # FIS,Fecha de muerte,Fecha diagnostico,Fecha recuperado,fecha reporte web
        # #
        # # #meta+id,#date+notification,#code,#adm3+name,#adm2+name,#indicator+infected+type,
        # # #indicator+infected+age,#indicator+infected+sex,,#indicator+infected+status,
        # # #indicator+infected+origin,,#date+reported+death,#date+reported+notification,
        # # #date+reported+recovered,#date+reported
        # #
        # # 1,2020-03-02T00:00:00.000,11001,Bogotá D.C.,Bogotá D.C.,Recuperado,19,F,Importado,Recuperado,Italia,2020-02-27T00:00:00.000,-   -,2020-03-06T00:00:00.000,2020-03-13T00:00:00.000,2020-03-06T00:00:00.000
        # # 2,2020-03-06T00:00:00.000,76111,Guadalajara de Buga,Valle del Cauca,Recuperado,34,M,Importado,Recuperado,España,2020-03-04T00:00:00.000,-   -,2020-03-09T00:00:00.000,2020-03-19T00:00:00.000,2020-03-09T00:00:00.000
        # # 3,2020-03-07T00:00:00.000,5001,Medellín,Antioquia,Recuperado,50,F,Importado,Recuperado,España,2020-02-29T00:00:00.000,-   -,2020-03-09T00:00:00.000,2020-03-15T00:00:00.000,2020-03-09T00:00:00.000
        # # 4,2020-03-09T00:00:00.000,5001,Medellín,Antioquia,Recuperado,55,M,Relacionado,Recuperado,Colombia,2020-03-06T00:00:00.000,-   -,2020-03-11T00:00:00.000,2020-03-26T00:00:00.000,2020-03-11T00:00:00.000

        by_admin1 = Counter()
        by_municipality = Counter()

        by_age = Counter()
        by_status = Counter()  # And source of infection

        by_admin1_age = Counter()
        by_admin1_status = Counter()

        by_municipality_age = Counter()
        by_municipality_status = Counter()

        first_item = True
        f = self.get_file('co_data.csv', include_revision=True)

        for item in csv.DictReader(f):
            if first_item:
                first_item = False
                continue

            print(item)
            case_id = item['ID de caso']
            notification_date = self.convert_date(item['Fecha de notificación'].split('T')[0])
            divipola = item['Codigo DIVIPOLA']
            municipality = item['Ciudad de ubicación']
            admin1 = item['Departamento o Distrito ']
            attention = item['atención']
            age = self._age_to_range(item['Edad'])
            gender = {
                'M': DT_TOTAL_MALE,
                'F': DT_TOTAL_FEMALE
            }[item['Sexo']]
            source_of_infection = {
                'Importado': DT_SOURCE_OVERSEAS,
                'Relacionado': DT_SOURCE_CONFIRMED,
                'En estudio': DT_SOURCE_UNDER_INVESTIGATION
            }[item['Tipo']]
            state = item['Estado']
            country_of_origin = item['País de procedencia']  # TODO: Add support for this!! ============================

            #date_reported = self.convert_date(item['FIS'])
            #date_diagnosed = self.convert_date(item['Fecha diagnostico'])
            #date_web_report = self.convert_date(item['fecha reporte web'])

            by_admin1[notification_date, admin1] += 1
            by_municipality[notification_date, admin1, municipality] += 1

            if item['Fecha de muerte'].strip('-').strip():
                date_death = self.convert_date(item['Fecha de muerte'].split('T')[0])
                by_status[date_death, DT_STATUS_DEATHS] += 1
                by_admin1_status[date_death, admin1, DT_STATUS_DEATHS] += 1
                by_municipality_status[date_death, admin1, municipality, DT_STATUS_DEATHS] += 1

            if item['Fecha recuperado'].strip('-').strip():
                date_recovered = self.convert_date(item['Fecha recuperado'].split('T')[0])
                by_status[date_recovered, DT_STATUS_RECOVERED] += 1
                by_admin1_status[date_recovered, admin1, DT_STATUS_RECOVERED] += 1
                by_municipality_status[date_recovered, admin1, municipality, DT_STATUS_RECOVERED] += 1

            by_status[notification_date, source_of_infection] += 1
            by_admin1_status[notification_date, admin1, source_of_infection] += 1
            by_municipality_status[notification_date, admin1, municipality, source_of_infection] += 1

            by_status[notification_date, gender] += 1
            by_admin1_status[notification_date, admin1, gender] += 1
            by_municipality_status[notification_date, admin1, municipality, gender] += 1

            by_status[notification_date, DT_TOTAL] += 1
            by_admin1_status[notification_date, admin1, DT_TOTAL] += 1
            by_municipality_status[notification_date, admin1, municipality, DT_TOTAL] += 1

            by_age[notification_date, age] += 1
            by_admin1_age[notification_date, admin1, age] += 1
            by_municipality_age[notification_date, admin1, municipality, age] += 1

        cumulative = Counter()
        for (notification_date, admin1), value in sorted(by_admin1.items()):
            cumulative[notification_date, admin1] += value
            r.append(DataPoint(
                region_schema=SCHEMA_ADMIN_1,
                region_parent='Colombia',
                region_child=admin1,
                datatype=DT_TOTAL,
                value=cumulative[notification_date, admin1],
                date_updated=notification_date,
                source_url=self.SOURCE_URL
            ))

        cumulative = Counter()
        for (notification_date, admin1, municipality), value in sorted(by_municipality.items()):
            cumulative[notification_date, admin1] += value
            r.append(DataPoint(
                region_schema=SCHEMA_CO_MUNICIPALITY,
                region_parent=admin1,
                region_child=municipality,
                datatype=DT_TOTAL,
                value=cumulative[notification_date, admin1],
                date_updated=notification_date,
                source_url=self.SOURCE_URL
            ))

        cumulative = Counter()
        for (notification_date, age), value in sorted(by_age.items()):
            cumulative[notification_date, age] += value
            r.append(DataPoint(
                region_schema=SCHEMA_ADMIN_0,
                region_child='Colombia',
                datatype=DT_TOTAL,
                agerange=age,
                value=cumulative[notification_date, age],
                date_updated=notification_date,
                source_url=self.SOURCE_URL
            ))

        cumulative = Counter()
        for (notification_date, status), value in sorted(by_status.items()):
            cumulative[notification_date, status] += value
            r.append(DataPoint(
                region_schema=SCHEMA_ADMIN_0,
                region_child='Colombia',
                datatype=status,
                value=cumulative[notification_date, status],
                date_updated=notification_date,
                source_url=self.SOURCE_URL
            ))

        cumulative = Counter()
        for (notification_date, admin1, age), value in sorted(by_admin1_age.items()):
            cumulative[notification_date, admin1, age] += value
            r.append(DataPoint(
                region_schema=SCHEMA_ADMIN_1,
                region_parent='Colombia',
                region_child=admin1,
                agerange=age,
                datatype=DT_TOTAL,
                value=cumulative[notification_date, admin1, age],
                date_updated=notification_date,
                source_url=self.SOURCE_URL
            ))

        cumulative = Counter()
        for (notification_date, admin1, status), value in sorted(by_admin1_status.items()):
            cumulative[notification_date, admin1, status] += value
            r.append(DataPoint(
                region_schema=SCHEMA_ADMIN_1,
                region_parent='Colombia',
                region_child=admin1,
                datatype=status,
                value=cumulative[notification_date, admin1, status],
                date_updated=notification_date,
                source_url=self.SOURCE_URL
            ))

        cumulative = Counter()
        for (notification_date, admin1, municipality, age), value in sorted(by_municipality_age.items()):
            cumulative[notification_date, admin1, municipality, age] += value
            r.append(DataPoint(
                region_schema=SCHEMA_CO_MUNICIPALITY,
                region_parent=admin1,
                region_child=municipality,
                agerange=age,
                datatype=DT_TOTAL,
                value=cumulative[notification_date, admin1, municipality, age],
                date_updated=notification_date,
                source_url=self.SOURCE_URL
            ))

        cumulative = Counter()
        for (notification_date, admin1, municipality, status), value in sorted(by_municipality_status.items()):
            cumulative[notification_date, admin1, municipality, status] += value
            r.append(DataPoint(
                region_schema=SCHEMA_CO_MUNICIPALITY,
                region_parent=admin1,
                region_child=municipality,
                datatype=status,
                value=cumulative[notification_date, admin1, municipality, status],
                date_updated=notification_date,
                source_url=self.SOURCE_URL
            ))

        return r

    def _age_to_range(self, age):
        age = int(age)
        for x in range(0, 110, 10):
            if x <= age <= x+9:
                return f'{x}-{x+9}'
        raise Exception(age)


if __name__ == '__main__':
    from pprint import pprint
    pprint(COData().get_datapoints())