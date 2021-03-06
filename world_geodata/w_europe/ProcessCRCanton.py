from world_geodata.ProcessGeoJSONBase import (
    ProcessGeoJSONBase, DATA_DIR, OUTPUT_DIR
)
from _utility.normalize_locality_name import (
    normalize_locality_name
)
from world_geodata.LabelsToRegionChild import (
    LabelsToRegionChild
)
from covid_db.datatypes.enums import Schemas

ltrc = LabelsToRegionChild()


class ProcessCRCanton(ProcessGeoJSONBase):
    def __init__(self):
        ProcessGeoJSONBase.__init__(self, 'cr_canton')

    def get_region_parent(self, fnam, feature):
        return ltrc.get_by_label(Schemas.ADMIN_1, 'CR', feature['NAME_1'])

    def get_region_child(self, fnam, feature):
        return normalize_locality_name(feature['NAME_2'])

    def get_region_printable(self, fnam, feature):
        return feature['NAME_2']


if __name__ == '__main__':
    ProcessCRCanton().output_json([
        DATA_DIR / 'cr_canton' / 'cr_canton.geojson'
    ], OUTPUT_DIR, pretty_print=False)
