from covid_19_au_grab.geojson_data.ProcessGeoJSONBase import (
    ProcessGeoJSONBase, DATA_DIR, OUTPUT_DIR
)
from covid_19_au_grab.normalize_locality_name import (
    normalize_locality_name
)
from covid_19_au_grab.geojson_data.LabelsToRegionChild import (
    LabelsToRegionChild
)
from covid_19_au_grab.datatypes.constants import (
    SCHEMA_ADMIN_1
)
ltrc = LabelsToRegionChild()


class ProcessCUMunicipality(ProcessGeoJSONBase):
    def __init__(self):
        ProcessGeoJSONBase.__init__(self, 'cu_municipality')

    def get_region_parent(self, fnam, feature):
        return ltrc.get_by_label(SCHEMA_ADMIN_1, 'CU', feature['province'])

    def get_region_child(self, fnam, feature):
        return normalize_locality_name(feature['municipality'])

    def get_region_printable(self, fnam, feature):
        return feature['municipality']


if __name__ == '__main__':
    ProcessCUMunicipality().output_json([
        DATA_DIR / 'cu_municipality' / 'municipios.geojson'
    ], OUTPUT_DIR, pretty_print=False)
