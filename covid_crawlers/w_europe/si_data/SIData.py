# https://api.sledilnik.org/api/municipalities
# https://covid-19.sledilnik.org/sl/stats
import json
from os import listdir

from _utility.cache_by_date import cache_by_date
from covid_crawlers._base_classes.URLBase import URL, URLBase
from covid_db.datatypes.StrictDataPointsFactory import StrictDataPointsFactory, MODE_STRICT
from covid_db.datatypes.enums import Schemas, DataTypes
from _utility.get_package_dir import get_overseas_dir
from covid_db.datatypes.DatapointMerger import DataPointMerger

region_map = dict([i.split('\t')[::-1] for i in """
SI-001	Ajdovščina
SI-213	Ankaran
SI-195	Apače
SI-002	Beltinci
SI-148	Benedikt
SI-149	Bistrica ob Sotli
SI-003	Bled
SI-150	Bloke
SI-004	Bohinj
SI-005	Borovnica
SI-006	Bovec
SI-151	Braslovče
SI-007	Brda
SI-008	Brezovica
SI-009	Brežice
SI-152	Cankova
SI-011	Celje
SI-012	Cerklje na Gorenjskem
SI-013	Cerknica
SI-014	Cerkno
SI-153	Cerkvenjak
SI-196	Cirkulane
SI-015	Črenšovci
SI-016	Črna na Koroškem
SI-017	Črnomelj
SI-018	Destrnik
SI-019	Divača
SI-154	Dobje
SI-020	Dobrepolje
SI-155	Dobrna
SI-021	Dobrova-Polhov Gradec
SI-156	Dobrovnik
SI-022	Dol pri Ljubljani
SI-157	Dolenjske Toplice
SI-023	Domžale
SI-024	Dornava
SI-025	Dravograd
SI-026	Duplek
SI-027	Gorenja vas-Poljane
SI-028	Gorišnica
SI-207	Gorje
SI-029	Gornja Radgona
SI-030	Gornji Grad
SI-031	Gornji Petrovci
SI-158	Grad
SI-032	Grosuplje
SI-159	Hajdina
SI-160	Hoče-Slivnica
SI-161	Hodoš
SI-162	Horjul
SI-034	Hrastnik
SI-035	Hrpelje-Kozina
SI-036	Idrija
SI-037	Ig
SI-038	Ilirska Bistrica
SI-039	Ivančna Gorica
SI-040	Izola
SI-041	Jesenice
SI-163	Jezersko
SI-042	Juršinci
SI-043	Kamnik
SI-044	Kanal
SI-045	Kidričevo
SI-046	Kobarid
SI-047	Kobilje
SI-048	Kočevje
SI-049	Komen
SI-164	Komenda
SI-050	Koper
SI-197	Kosanjevica na Krki
SI-165	Kostel
SI-051	Kozje
SI-052	Kranj
SI-053	Kranjska Gora
SI-166	Križevci
SI-054	Krško
SI-055	Kungota
SI-056	Kuzma
SI-057	Laško
SI-058	Lenart
SI-059	Lendava
SI-060	Litija
SI-061	Ljubljana
SI-062	Ljubno
SI-063	Ljutomer
SI-208	Log-Dragomer
SI-064	Logatec
SI-065	Loška Dolina
SI-066	Loški Potok
SI-167	Lovrenc na Pohorju
SI-067	Luče
SI-068	Lukovica
SI-069	Majšperk
SI-198	Makole
SI-070	Maribor
SI-168	Markovci
SI-071	Medvode
SI-072	Mengeš
SI-073	Metlika
SI-074	Mežica
SI-169	Miklavž na Dravskem Polju
SI-075	Miren-Kostanjevica
SI-212	Mirna
SI-170	Mirna Peč
SI-076	Mislinja
SI-199	Mokronog-Trebelno
SI-077	Moravče
SI-078	Moravske Toplice
SI-079	Mozirje
SI-080	Murska Sobota
SI-081	Muta
SI-082	Naklo
SI-083	Nazarje
SI-084	Nova Gorica
SI-085	Novo Mesto
SI-086	Odranci
SI-171	Oplotnica
SI-087	Ormož
SI-088	Osilnica
SI-089	Pesnica
SI-090	Piran
SI-091	Pivka
SI-092	Podčetrtek
SI-172	Podlehnik
SI-093	Podvelka
SI-200	Poljčane
SI-173	Polzela
SI-094	Postojna
SI-174	Prebold
SI-095	Preddvor
SI-175	Prevalje
SI-096	Ptuj
SI-097	Puconci
SI-098	Rače-Fram
SI-099	Radeče
SI-100	Radenci
SI-101	Radlje ob Dravi
SI-102	Radovljica
SI-103	Ravne na Koroškem
SI-176	Razkrižje
SI-209	Rečica ob Savinji
SI-201	Renče-Vogrsko
SI-104	Ribnica
SI-177	Ribnica na Pohorju
SI-106	Rogaška Slatina
SI-105	Rogašovci
SI-107	Rogatec
SI-108	Ruše
SI-178	Selnica ob Dravi
SI-109	Semič
SI-110	Sevnica
SI-111	Sežana
SI-112	Slovenj Gradec
SI-113	Slovenska Bistrica
SI-114	Slovenske Konjice
SI-179	Sodražica
SI-180	Solčava
SI-202	Središče ob Dravi
SI-115	Starše
SI-203	Straža
SI-181	Sveta Ana
SI-204	Sveta Trojica v Slovenskih Goricah
SI-182	Sveti Andraž v Slovenskih Goricah
SI-116	Sveti Jurij
SI-210	Sveti Jurij v Slovenskih Goricah
SI-116	sveti jurij ob ščavnici
SI-205	Sveti Tomaž
SI-033	Šalovci
SI-183	Šempeter-Vrtojba
SI-117	Šenčur
SI-118	Šentilj
SI-119	Šentjernej
SI-120	Šentjur
SI-211	Šentrupert
SI-121	Škocjan
SI-122	Škofja Loka
SI-123	Škofljica
SI-124	Šmarje pri Jelšah
SI-206	Šmarješke Toplice
SI-125	Šmartno ob Paki
SI-194	Šmartno pri Litiji
SI-126	Šoštanj
SI-127	Štore
SI-184	Tabor
SI-010	Tišina
SI-128	Tolmin
SI-129	Trbovlje
SI-130	Trebnje
SI-185	Trnovska Vas
SI-186	Trzin
SI-131	Tržič
SI-132	Turnišče
SI-133	Velenje
SI-187	Velika Polana
SI-134	Velike Lašče
SI-188	Veržej
SI-135	Videm
SI-136	Vipava
SI-137	Vitanje
SI-138	Vodice
SI-139	Vojnik
SI-139	Vojnki
SI-189	Vransko
SI-140	Vrhnika
SI-141	Vuzenica
SI-142	Zagorje ob Savi
SI-143	Zavrč
SI-144	Zreče
SI-190	Žalec
SI-146	Železniki
SI-191	Žetale
SI-147	Žiri
SI-192	Žirovnica
SI-193	Žužemberk
SI-197	Kostanjevica na Krki
SI-088	Osilnica
Other	tujina
""".lower().strip().split('\n')])


class SIData(URLBase):
    SOURCE_URL = 'https://covid-19.sledilnik.org/sl/stats'
    SOURCE_DESCRIPTION = ''
    SOURCE_ID = 'si_sledilnik'

    def __init__(self):
        URLBase.__init__(self,
             output_dir=get_overseas_dir() / 'si' / 'data',
             urls_dict={
                 # Points for each county w/stats
                 'municipalities.json': URL('https://api.sledilnik.org/api/municipalities',
                                            static_file=False),
            }
        )
        self.sdpf = StrictDataPointsFactory(
            region_mappings={
                ('admin_1', 'si', 'si-010'): None,
                ('admin_1', 'si', 'si-142'): None,
                ('admin_1', 'si', 'si-207'): None,
                ('admin_1', 'si', 'si-199'): None,
                ('admin_1', 'si', 'si-206'): None,
                ('admin_1', 'si', 'si-212'): None,
                ('admin_1', 'si', 'si-211'): None,
                ('admin_1', 'si', 'si-208'): None,
                ('admin_1', 'si', 'si-201'): None,
                ('admin_1', 'si', 'si-196'): None,
                ('admin_1', 'si', 'si-197'): None,
                ('admin_1', 'si', 'si-209'): None,
                ('admin_1', 'si', 'si-204'): None,
                ('admin_1', 'si', 'si-213'): None,
                ('admin_1', 'si', 'si-200'): None,
                ('admin_1', 'si', 'si-205'): None,
                ('admin_1', 'si', 'si-203'): None,
                ('admin_1', 'si', 'si-198'): None,
                ('admin_1', 'si', 'si-202'): None,
                ('admin_1', 'si', 'si-088'): None,
                ('admin_1', 'si', 'si-210'): None,
            },
            mode=MODE_STRICT
        )
        self.update()

    def get_datapoints(self):
        r = []
        dpm = DataPointMerger()
        # [{"year":2020,"month":3,"day":4,"regions":{"mb":{"benedikt":{"activeCases":null,"confirmedToDate":null,"deceasedToDate":0},
        base_dir = self.get_path_in_dir('')

        for date in self.iter_nonempty_dirs(base_dir):
            print(date)
            r.extend(self._get_municipalities_data(date, dpm))
        return r

    @cache_by_date(source_id=SOURCE_ID)
    def _get_municipalities_data(self, date, dpm):
        r = self.sdpf()
        base_dir = self.get_path_in_dir('')
        path = f'{base_dir}/{date}/municipalities.json'

        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.loads(f.read())
        except UnicodeDecodeError:
            import brotli
            with open(path, 'rb') as f:
                data = json.loads(brotli.decompress(f.read()).decode('utf-8'))

        for i_data in data:
            for region, region_dict in i_data['regions'].items():
                for sub_region, sub_region_dict in region_dict.items():
                    region_child = region_map[sub_region.replace('_', ' ').lower()]
                    #print(region, sub_region, sub_region_dict)
                    date = '%04d_%02d_%02d' % (
                        i_data['year'], i_data['month'], i_data['day']
                    )

                    if sub_region_dict.get('activeCases') is not None:
                        r.append(
                            region_schema=Schemas.ADMIN_1,
                            region_parent='SI',
                            region_child=region_child,
                            datatype=DataTypes.STATUS_ACTIVE,
                            value=sub_region_dict['activeCases'],
                            source_url=self.SOURCE_URL,
                            date_updated=date
                        )

                    if sub_region_dict.get('confirmedToDate') is not None:
                        r.append(
                            region_schema=Schemas.ADMIN_1,
                            region_parent='SI',
                            region_child=region_child,
                            datatype=DataTypes.TOTAL,
                            value=sub_region_dict['confirmedToDate'],
                            source_url=self.SOURCE_URL,
                            date_updated=date
                        )

                    if sub_region_dict.get('deceasedToDate') is not None:
                        r.append(
                            region_schema=Schemas.ADMIN_1,
                            region_parent='SI',
                            region_child=region_child,
                            datatype=DataTypes.STATUS_DEATHS,
                            value=sub_region_dict['deceasedToDate'],
                            source_url=self.SOURCE_URL,
                            date_updated=date
                        )

        return dpm.extend(r)


if __name__ == '__main__':
    from pprint import pprint
    pprint(SIData().get_datapoints())
