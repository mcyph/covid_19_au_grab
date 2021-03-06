from world_geodata.ProcessGeoJSONBase import (
    ProcessGeoJSONBase, DATA_DIR, OUTPUT_DIR
)
from _utility.normalize_locality_name import (
    normalize_locality_name
)


place_map = dict([i.split('\t')[::-1] for i in """
TH-10	Krung Thep Maha Nakhon
TH-10	Bangkok
TH-S	Phatthaya
TH-37	Amnat Charoen
TH-15	Ang Thong
TH-38	Bueng Kan
TH-31	Buri Ram
TH-24	Chachoengsao
TH-18	Chai Nat
TH-36	Chaiyaphum
TH-22	Chanthaburi
TH-50	Chiang Mai
TH-57	Chiang Rai
TH-20	Chon Buri
TH-86	Chumphon
TH-46	Kalasin
TH-62	Kamphaeng Phet
TH-71	Kanchanaburi
TH-40	Khon Kaen
TH-81	Krabi
TH-52	Lampang
TH-51	Lamphun
TH-42	Loei
TH-16	Lop Buri
TH-58	Mae Hong Son
TH-44	Maha Sarakham
TH-49	Mukdahan
TH-26	Nakhon Nayok
TH-73	Nakhon Pathom
TH-48	Nakhon Phanom
TH-30	Nakhon Ratchasima
TH-60	Nakhon Sawan
TH-80	Nakhon Si Thammarat
TH-55	Nan
TH-96	Narathiwat
TH-39	Nong Bua Lam Phu
TH-43	Nong Khai
TH-12	Nonthaburi
TH-13	Pathum Thani
TH-94	Pattani
TH-82	Phangnga
TH-93	Phatthalung
TH-56	Phayao
TH-67	Phetchabun
TH-76	Phetchaburi
TH-66	Phichit
TH-65	Phitsanulok
TH-54	Phrae
TH-14	Phra Nakhon Si Ayutthaya
TH-83	Phuket
TH-25	Prachin Buri
TH-77	Prachuap Khiri Khan
TH-85	Ranong
TH-70	Ratchaburi
TH-21	Rayong
TH-45	Roi Et
TH-27	Sa Kaeo
TH-47	Sakon Nakhon
TH-11	Samut Prakan
TH-74	Samut Sakhon
TH-75	Samut Songkhram
TH-19	Saraburi
TH-91	Satun
TH-17	Sing Buri
TH-33	Si Sa Ket
TH-90	Songkhla
TH-64	Sukhothai
TH-72	Suphan Buri
TH-84	Surat Thani
TH-32	Surin
TH-63	Tak
TH-92	Trang
TH-23	Trat
TH-34	Ubon Ratchathani
TH-41	Udon Thani
TH-61	Uthai Thani
TH-53	Uttaradit
TH-95	Yala
TH-35	Yasothon 
""".strip().split('\n')])


class ProcessTHDistrict(ProcessGeoJSONBase):
    def __init__(self):
        ProcessGeoJSONBase.__init__(self, 'th_district')

    def get_region_parent(self, fnam, feature):
        return place_map[feature['ADM1_EN']]

    def get_region_child(self, fnam, feature):
        return normalize_locality_name(feature['ADM2_EN'])  # TODO: CHECK THIS MATCHES UP!!!! ==========================

    def get_region_printable(self, fnam, feature):
        # Unfortunately, QGIS seems to corrupt the thai
        # chars when simplifying, and it's too big for mapshaper..
        # should eventually include native versions ==================================================================
        r = {
            'th': feature['ADM2_TH'],
            'en': feature['ADM2_EN']
        }

        if feature['ADM2ALT1EN']:
            r['en1'] = feature['ADM2ALT1EN']
        if feature['ADM2ALT2EN']:
            r['en2'] = feature['ADM2ALT1EN']
        if feature['ADM2ALT1TH']:
            r['th1'] = feature['ADM2ALT1EN']
        if feature['ADM2ALT2TH']:
            r['th2'] = feature['ADM2ALT1EN']

        return r


if __name__ == '__main__':
    ProcessTHDistrict().output_json([
        DATA_DIR / 'th_district' / 'th_districts.json'
    ], OUTPUT_DIR, pretty_print=False)
