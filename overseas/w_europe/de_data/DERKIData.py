# https://experience.arcgis.com/experience/478220a4c454480e823b17327b2bf1d4/page/page_1/

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
from covid_19_au_grab.datatypes.enums import Schemas, DataTypes
from covid_19_au_grab.get_package_dir import (
    get_overseas_dir, get_package_dir
)
from covid_19_au_grab.overseas.w_europe.de_data.DEData import (
    state_to_name
)


name_to_state = {
    state.lower(): name for name, state in state_to_name.items()
}

KREIS_URL = 'https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/RKI_Landkreisdaten/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=cases%20desc&resultOffset=0&resultRecordCount=1000&resultType=standard&cacheHint=true'


class DERKIData(URLBase):
    SOURCE_URL = 'https://experience.arcgis.com/experience/478220a4c454480e823b17327b2bf1d4/page/page_1/'
    SOURCE_DESCRIPTION = ''
    SOURCE_ID = 'de_rki_dash'

    def __init__(self):
        URLBase.__init__(self,
            output_dir=get_overseas_dir() / 'de' / 'data',
            urls_dict={
                'kreis.json': URL(KREIS_URL, static_file=False),
            }
        )
        self.update()

    def get_datapoints(self):
        r = []
        r.extend(self._get_kreis_2_data())
        return r

    def _get_kreis_2_data(self):
        r = []
        base_dir = self.get_path_in_dir('')

        for date in sorted(listdir(base_dir)):
            path = f'{base_dir}/{date}/kreis.json'
            with open(path, 'r', encoding='utf-8') as f:
                data = json.loads(f.read())

            for feature in data['features']:
                attributes = feature['attributes']
                #print(attributes)

                # Only confirmed and deaths are shown in the dashboard
                date = self.convert_date(
                    attributes['last_update'].split()[0]
                                             .strip(',')
                                             .replace('.', '/')
                )
                region_parent = name_to_state[attributes['BL'].lower()]
                region_child = attributes['GEN']
                confirmed = attributes['cases']
                deaths = attributes['deaths']
                recovered = attributes['recovered']

                if 'stadt' in attributes['BEZ'].lower():
                    print(attributes)
                    region_child += ' Städte'

                if confirmed is not None:
                    r.append(DataPoint(
                        region_schema=Schemas.DE_KREIS,
                        region_parent=region_parent,
                        region_child=region_child,
                        datatype=DataTypes.TOTAL,
                        value=int(confirmed),
                        date_updated=date,
                        source_url=self.SOURCE_URL
                    ))

                if deaths is not None:
                    r.append(DataPoint(
                        region_schema=Schemas.DE_KREIS,
                        region_parent=region_parent,
                        region_child=region_child,
                        datatype=DataTypes.STATUS_DEATHS,
                        value=int(deaths),
                        date_updated=date,
                        source_url=self.SOURCE_URL
                    ))

                if recovered is not None:
                    r.append(DataPoint(
                        region_schema=Schemas.DE_KREIS,
                        region_parent=region_parent,
                        region_child=region_child,
                        datatype=DataTypes.STATUS_RECOVERED,
                        value=int(recovered),
                        date_updated=date,
                        source_url=self.SOURCE_URL
                    ))

                if recovered is not None and confirmed is not None and deaths is not None:
                    r.append(DataPoint(
                        region_schema=Schemas.DE_KREIS,
                        region_parent=region_parent,
                        region_child=region_child,
                        datatype=DataTypes.STATUS_ACTIVE,
                        value=int(confirmed)-int(recovered)-int(deaths),
                        date_updated=date,
                        source_url=self.SOURCE_URL
                    ))

        return r


if __name__ == '__main__':
    from pprint import pprint
    from covid_19_au_grab.datatypes.datapoints_thinned_out import datapoints_thinned_out
    datapoints = DERKIData().get_datapoints()
    pprint(datapoints)
