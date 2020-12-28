import json
import requests
from pyquery import PyQuery as pq
from datetime import datetime
from collections import namedtuple
from dateutil.parser import parse as parse_datetime
from _utility.get_package_dir import get_data_dir

# https://transitfeeds.com/p/transport-for-nsw/237

CASE_LOCATIONS_ALERTS_URL = 'https://www.health.nsw.gov.au/Infectious/covid-19/Pages/case-locations-and-alerts.aspx'
# https://www.health.nsw.gov.au/Infectious/covid-19/Documents/data/venue-data-20201226.js


VenueLocation = namedtuple('VenueLocation', [
    'type', 'venue', 'suburb', 'date', 'time', 'alert', 'long', 'lat'
])

PublicTransportRoutePortion = namedtuple('PublicTransportRoutePortion', [
    'by', 'route', 'date', 'time', 'start_loc', 'end_loc', 'health_advice'
])


class _NSWCaseLocations:
    def __get_new_dir(self):
        revision_id = 0
        while True:
            fmt = f'%%y_%%m_%%d-%03d' % revision_id
            child_dir_name = datetime.now().strftime(fmt)
            path = get_data_dir() / 'nsw' / 'case_locs' / child_dir_name

            if path.exists():
                revision_id += 1
                continue
            else:
                path.mkdir()
                return path

    def get_datapoints(self):
        revision_dir = self.__get_new_dir()
        cla_rq = requests.get(CASE_LOCATIONS_ALERTS_URL)

        with open(revision_dir / 'case_locations_and_alerts.html', 'w', encoding='utf-8') as f:
            f.write(cla_rq.text)

        vd_url = cla_rq.text.split('/Infectious/covid-19/Documents/data/venue-data-')[1].split('.js')[0]
        vd_url = f'https://www.health.nsw.gov.au/Infectious/covid-19/Documents/data/venue-data-{vd_url}.js'
        vd_rq = requests.get(vd_url)

        with open(revision_dir / 'venue-data.js', 'w', encoding='utf-8') as f:
            f.write(vd_rq.text)

        r = []
        r.extend(self.__get_venue_locations(vd_rq))
        r.extend(self.__get_public_transport_route_portions(cla_rq))
        return r

    def __get_public_transport_route_portions(self, cla_rq):
        r = []
        tr_elms = pq(cla_rq.text)('table#tbl-casual-contacts-transport tbody tr')
        for by, route, date, time, start_loc, end_loc, health_advice in tr_elms:
            r.append(PublicTransportRoutePortion(
                by=pq(by).text(),
                route=pq(route).text(),
                date=parse_datetime(pq(date).text(), dayfirst=True),
                time=pq(time).text(),
                start_loc=pq(start_loc).text(),
                end_loc=pq(end_loc).text(),
                health_advice=pq(health_advice).text()
            ))
        return r

    def __get_venue_locations(self, vd_rq):
        r = []

        data = json.loads(vd_rq.text.partition('var venue_data = ')[-1])
        # TODO: What to do with the updated date?
        # date_updated = data['date']

        for k, v in data['data'].items():
            for i in v:
                r.append(VenueLocation(
                    type=k,
                    venue=i['Venue'],
                    suburb=i['Suburb'],
                    date=parse_datetime(i['Date'], dayfirst=True),
                    time=i['Time'],
                    alert=i['Alert'],
                    long=float(i['Lon']),
                    lat=float(i['Lat']),
                ))
        return r


if __name__ == '__main__':
    from pprint import pprint

    #   {
    #     "state": "NSW",
    #     "area": "",
    #     "name": "St Brendan’s Catholic Church Bankstown",
    #     "date": "16/07/20",
    #     "time": "for one hour from 6.30pm",
    #     "description": "St Brendan’s Catholic Church Bankstown for one hour from 6.30pm on July 16",
    #     "coor": [-33.9220903,151.0277432]
    #   },

    out = []
    datapoints = _NSWCaseLocations().get_datapoints()
    for datapoint in datapoints:
        if not isinstance(datapoint, VenueLocation):
            continue

        out.append({
            'state': 'NSW',
            'area': datapoint.suburb,
            'name': f"{datapoint.type.title()}: {datapoint.venue}",
            'date': datapoint.date.strftime('%d/%m/%y'),
            'time': datapoint.time,
            'description': datapoint.alert,
            'coor': [datapoint.lat, datapoint.long]
        })

    print(json.dumps(out, indent=4))
    #pprint(datapoints)
