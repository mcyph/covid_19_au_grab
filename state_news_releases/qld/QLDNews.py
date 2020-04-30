from pyquery import PyQuery as pq
from re import compile, MULTILINE, DOTALL

from covid_19_au_grab.state_news_releases.StateNewsBase import (
    StateNewsBase, bothlistingandstat,
    ALWAYS_DOWNLOAD_LISTING
)
from covid_19_au_grab.state_news_releases.constants import (
    # Only newer data by LGA (not much history)
    SCHEMA_LGA, SCHEMA_HHS,

    # Basic values (including new cases but not totals for old regional data)
    DT_TESTS_TOTAL, DT_CASES_NEW, DT_CASES_TOTAL,
    DT_CASES_TOTAL_MALE, DT_CASES_TOTAL_FEMALE,

    # Older+present data by HHS
    DT_CASES_ACTIVE, DT_CASES_DEATHS, DT_CASES_RECOVERED,
    DT_CASES_HOSPITALIZED,

    # Source of infection by region (LGA)
    DT_SOURCE_INTERSTATE, DT_SOURCE_UNDER_INVESTIGATION,
    DT_SOURCE_COMMUNITY, DT_SOURCE_CONFIRMED,
    DT_SOURCE_OVERSEAS
)
from covid_19_au_grab.state_news_releases.DataPoint import (
    DataPoint
)
from covid_19_au_grab.word_to_number import (
    word_to_number
)
from covid_19_au_grab.URLArchiver import (
    URLArchiver
)


class QLDNews(StateNewsBase):
    STATE_NAME = 'qld'
    LISTING_URL = (
        'https://www.health.qld.gov.au/'
        'news-events/doh-media-releases',

        'https://www.health.qld.gov.au/news-events/'
        'doh-media-releases?result_707098_result_page=2',

        'https://www.health.qld.gov.au/news-events/'
        'doh-media-releases?result_707098_result_page=3',
    )

    LISTING_HREF_SELECTOR = '.presszebra div h3 a'
    STATS_BY_REGION_URL = 'https://www.qld.gov.au/health/conditions/' \
                          'health-alerts/coronavirus-covid-19/' \
                          'current-status/' \
                          'current-status-and-contact-tracing-alerts'
    STATS_BY_REGION_URL_2 = 'https://www.qld.gov.au/health/conditions/' \
                            'health-alerts/coronavirus-covid-19/' \
                            'current-status/statistics'

    def get_data(self):
        r = []
        ua = URLArchiver(f'{self.STATE_NAME}/current_statistics')
        ua.get_url_data(
            self.STATS_BY_REGION_URL_2,
            cache=False if ALWAYS_DOWNLOAD_LISTING else True
        )

        for period in ua.iter_periods():
            for subperiod_id, subdir in ua.iter_paths_for_period(period):
                path = ua.get_path(subdir)

                with open(path, 'r',
                          encoding='utf-8',
                          errors='ignore') as f:
                    html = f.read()

                cbr = self._get_total_cases_by_region(self.STATS_BY_REGION_URL_2, html)
                if cbr: r.extend(cbr)

                total = self._get_total_cases(self.STATS_BY_REGION_URL_2, html)
                if total: r.append(total)

                new = self._get_total_new_cases(self.STATS_BY_REGION_URL_2, html)
                if new: r.append(new)

                tested = self._get_total_cases_tested(self.STATS_BY_REGION_URL_2, html)
                if tested: r.append(tested)

                age_breakdown = self._get_total_age_breakdown(self.STATS_BY_REGION_URL_2, html)
                if age_breakdown: r.extend(age_breakdown)

                dhr = self._get_total_dhr(self.STATS_BY_REGION_URL_2, html)
                if dhr: r.extend(dhr)

                soi = self._get_total_source_of_infection(self.STATS_BY_REGION_URL_2, html)
                if soi: r.extend(soi)

        r.extend(StateNewsBase.get_data(self))
        return r

    #============================================================#
    #                      Misc Functions                        #
    #============================================================#

    def _infer_missing_info(self, dates_dict):
        # TODO: QLD health now only provides a tally, but previously
        #  gave number of new cases by region. It makes sense to
        #  derive this info as needed.
        pass

    def _get_date(self, href, html):
        return self._extract_date_using_format(
            # e.g. 24 March 2020
            pq(html)('#last-updated').text().split(':')[-1].strip() or
            pq(html)('div#content div h2').text().strip() or
            pq(html)('div#content div h4').text().strip() or
            pq(html)('div#content div h3').text().strip() or
            pq(html)('.qg-content-footer dd').text().strip()   # CHECK ME!!!
        )

    def __get_totals_from_table(self, html):
        # Get the totals from the new table, which has
        # HHS*	Active cases	Recovered cases	Deaths	Total confirmed cases to date
        table = pq(pq(html)('table.table.table-bordered.header-basic'))
        if not table:
            #print("NOT TABLE!!!")
            return None
        table_text = pq(table).text().lower().replace('\n', ' ')

        if (
            not 'total confirmed' in table_text or
            not 'recovered cases' in table_text or
            not 'active cases' in table_text
        ):
            #print("NOT TOTAL:", table.text())
            return None

        tr = pq(table[0])('tr:last')[0]
        ths = pq(tr)('th,td')

        r = {}
        r['active'] = int(pq(ths[1]).text().strip().replace(',', ''))
        r['recovered'] = int(pq(ths[2]).text().strip().replace(',', ''))
        r['deaths'] = int(pq(ths[3]).text().strip().replace(',', ''))
        r['total'] = int(pq(ths[4]).text().strip().strip('*').strip().replace(',', ''))
        return r

    #============================================================#
    #                      General Totals                        #
    #============================================================#

    @bothlistingandstat
    def _get_total_cases(self, href, html):
        if href in (self.STATS_BY_REGION_URL, self.STATS_BY_REGION_URL_2):
            # New format as of 22 April
            cases = pq(html)('.qh-fact-wrapper .cases span')

            if cases:
                return self._extract_number_using_regex(
                    compile('([0-9,]+)'),
                    pq(cases[0]).text().strip(),
                    datatype=DT_CASES_TOTAL,
                    date_updated=self._get_date(href, html),
                    source_url=href
                )
            else:
                return None

        # Use new format from the table if possible
        totals_dict = self.__get_totals_from_table(html)
        if totals_dict:
            return DataPoint(
                datatype=DT_CASES_TOTAL,
                value=totals_dict['total'],
                date_updated=self._get_date(href, html),
                source_url=href,
                text_match=None
            )

        c_html = word_to_number(html)

        return self._extract_number_using_regex(
            (
                compile('state total to ([0-9,]+)'),
                compile('total of ([0-9,]+) (?:people|person)')
            ),
            c_html,
            source_url=href,
            datatype=DT_CASES_TOTAL,
            date_updated=self._get_date(href, html)

        ) or self._extract_number_using_regex(
            compile(
                # Total number changed from being enclosed in a <strong>
                # tag to a <b> tag, so changed to be as broad as NSW
                # <strong>Total</strong></td>
                # <td headers="table59454r1c2"><b>37,334‬</b></td>
                r'<td[^>]*?>(?:<[^</>]+>)?Total(?:</[^<>]+>)?</td>'
                r'[^<]*?<td[^>]*?>.*?([0-9,]+).*?</td>',
                MULTILINE | DOTALL
            ),
            c_html,
            source_url=href,
            datatype=DT_CASES_TOTAL,
            date_updated=self._get_date(href, html)
        )

    @bothlistingandstat
    def _get_total_new_cases(self, href, html):
        if href in (self.STATS_BY_REGION_URL, self.STATS_BY_REGION_URL_2):
            # New format as of 22 April
            new_cases = pq(html)('.qh-fact-wrapper .new span')
            if new_cases:
                return self._extract_number_using_regex(
                    compile('([0-9,]+)'),
                    pq(new_cases[0]).text().strip(),
                    date_updated=self._get_date(href, html),
                    datatype=DT_CASES_NEW,
                    source_url=href
                )
            else:
                return None

        else:
            c_html = word_to_number(html)
            return self._extract_number_using_regex(
                compile('([0-9,]+) new(?: confirmed)? cases?'),
                c_html,
                source_url=href,
                datatype=DT_CASES_NEW,
                date_updated=self._get_date(href, html)
            )

    @bothlistingandstat
    def _get_total_cases_tested(self, href, html):
        #if href in (self.STATS_BY_REGION_URL, self.STATS_BY_REGION_URL_2):

        # New format as of 22 April
        tested = pq(html)('.qh-fact-wrapper .tested span')
        if tested:
            return self._extract_number_using_regex(
                compile('([0-9,]+)'),
                pq(tested[0]).text().strip(),
                date_updated=self._get_date(href, html),
                datatype=DT_TESTS_TOTAL,
                source_url=href
            )

        # NOTE: This is actually a different page to the press releases!
        #  I needed to get some of these from web.archive.org.
        #  Some of the stats may be a day or more old,
        #  so will need to add the date of the stat as well(!)

        value = self._extract_number_using_regex(
            compile(
                'Total samples tested: <strong>([0-9,]+)'
            ),
            html,
            date_updated=self._get_date(href, html),
            datatype=DT_TESTS_TOTAL,
            source_url=href
        )
        if value:
            return value

        # Find the start of the # samples tested table
        th_regex = compile(
            '<th id="table[^"]+">[^<]*?As at ([^<]+)[^<]*?</th>[^<]*'
            '<th id="table[^"]+">[^<]*?(?:Samples|Patients) tested[^<]*?</th>',
            DOTALL | MULTILINE
        )
        match = th_regex.search(html)
        if not match:
            #print("NOT INITIAL MATCH!")
            return None  # WARNING!!!

        # Get the date - it's in format "30 March 2020"
        date_updated = self._extract_date_using_format(
            match.group(1).strip()
        )
        slice_from = match.end(1)  # CHECK ME!
        html = html[slice_from:]

        # Get the # samples total
        value = self._extract_number_using_regex(
            compile(
                # Total number changed from being enclosed in a <strong>
                # tag to a <b> tag, so changed to be as broad as NSW
                # <strong>Total</strong></td>
                # <td headers="table59454r1c2"><b>37,334‬</b></td>
                r'<td[^>]*?>(?:<[^</>]+>)?Total(?:</[^<>]+>)?</td>'
                r'[^<]*?<td[^>]*?>.*?([0-9,]+).*?</td>',
                MULTILINE | DOTALL
            ),
            html,
            date_updated=date_updated,
            datatype=DT_TESTS_TOTAL,
            source_url=href
        )
        if not value:
            #print("NOT SECOND MATCH!")
            return None  # WARNING!
        return value

    #============================================================#
    #                      Age Breakdown                         #
    #============================================================#

    def _get_new_age_breakdown(self, href, html):
        pass

    def _get_total_age_breakdown(self, href, html):
        if href == self.STATS_BY_REGION_URL_2:
            r = []
            table = pq(html)('#QLD_CasesByAgeAndGender')[0][1]

            for tr in table[1:]:
                age_group = pq(tr[0]).text().strip()
                female = int(pq(tr[1]).text())
                male = int(pq(tr[2]).text())
                total = int(pq(tr[3]).text())

                for datatype, value in (
                    (DT_CASES_TOTAL_FEMALE, female),
                    (DT_CASES_TOTAL_MALE, male),
                    (DT_CASES_TOTAL, total)
                ):
                    if value is None:
                        continue
                    r.append(DataPoint(
                        datatype=datatype,
                        agerange=age_group,
                        value=value,
                        date_updated=self._get_date(href, html),
                        source_url=href
                    ))
            return r

    #============================================================#
    #                  Male/Female Breakdown                     #
    #============================================================#

    def _get_total_male_female_breakdown(self, url, html):
        pass

    def _get_new_male_female_breakdown(self, url, html):
        pass

    #============================================================#
    #                     Totals by Region                       #
    #============================================================#

    def _get_total_cases_by_region(self, href, html):
        lga_norm_map = {
            'Locally Acquired—close contact with confirmed case':
                                    DT_SOURCE_CONFIRMED,
            'Locally acquired—no known contact':
                                    DT_SOURCE_COMMUNITY,
            'Locally acquired—contact known':
                                    DT_SOURCE_CONFIRMED,
            'Interstate acquired':  DT_SOURCE_INTERSTATE,
            'Overseas acquired':    DT_SOURCE_OVERSEAS,
            'Under investigation':  DT_SOURCE_UNDER_INVESTIGATION,
            'Total':                DT_CASES_TOTAL,
        }
        hhs_norm_map = {
            'Total cases': DT_CASES_TOTAL,
            'Active cases': DT_CASES_ACTIVE,
            'Total recovered': DT_CASES_RECOVERED,
            'Total deaths': DT_CASES_DEATHS
        }

        if href == self.STATS_BY_REGION_URL_2:
            regions = []

            # Add by HHS table
            # Total cases | Active cases | Total recovered | Total deaths
            table = pq(html)('#QLD_Cases_By_HHS')[0]
            headers = [
                hhs_norm_map[pq(i).text().strip()]
                for i in table[0][0][1:]
            ]
            for tr in table[3]:
                hhs = pq(tr[0]).text().strip()

                for xx, td in enumerate(tr[1:]):
                    value = int(pq(td).text().strip().replace(',', ''))

                    regions.append(DataPoint(
                        schema=SCHEMA_HHS,
                        datatype=headers[xx],
                        region=hhs.title(),
                        value=value,
                        date_updated=self._get_date(href, html),
                        source_url=href
                    ))

            # Add by LGA table
            # Overseas acquired | Locally acquired—contact known |
            # Locally acquired—no known contact | Interstate acquired |
            # Under investigation | Total
            table = pq(html)('table#LGA')[0]

            headers = [
                lga_norm_map[pq(i).text().strip()]
                for i in table[0][0][1:]
            ]
            for tr in table[1][1:]:
                lga = pq(tr[0]).text().split('(')[0].strip()

                for xx, td in enumerate(tr[1:]):
                    value = int(pq(td).text().strip().replace(',', ''))

                    regions.append(DataPoint(
                        schema=SCHEMA_LGA,
                        datatype=headers[xx],
                        region=lga.title(),
                        value=value,
                        date_updated=self._get_date(href, html),
                        source_url=href
                    ))
            return regions

        else:
            table = pq(pq(html)('table.table.table-bordered.header-basic'))
            if not table:
                return None

            if not 'Total confirmed' in pq(table[0]).text().replace('\n', ' ').replace('  ', ' '):
                #print("NOT TOTAL:", table.text())
                return None

            regions = []
            for tr in table('tr'):
                if 'total' in pq(tr).text().lower():
                    continue

                tds = pq(tr)('td')
                for x, td in enumerate(tds):
                    if x == 0:
                        # HACK: one day had "271" prefixed to "North West"
                        hhs_region = pq(td).text().strip().lstrip('271').strip()
                    elif x >= 1:
                        if len(tds) > 2:
                            # New format:
                            # HHS*
                            # Active cases
                            # Recovered cases
                            # Deaths
                            # Total confirmed cases to date
                            datatype = [
                                DT_CASES_ACTIVE,
                                DT_CASES_RECOVERED,
                                DT_CASES_DEATHS,
                                DT_CASES_TOTAL
                            ][x-1]
                        else:
                            datatype = DT_CASES_TOTAL

                        try:
                            value = int(pq(td).text().strip())
                            regions.append(DataPoint(
                                schema=SCHEMA_HHS,
                                datatype=datatype,
                                region=hhs_region.title(),
                                value=value,
                                date_updated=self._get_date(href, html),
                                source_url=href
                            ))
                        except ValueError:
                            # WARNING!!!
                            pass

            return regions

    def _get_new_cases_by_region(self, href, html):
        # TODO: QLD only provided new cases for a few days
        # it might pay to do a tally of some kind!
        ' New confirmed cases'

        table = pq(html)('table.table.table-bordered.header-basic')
        if not table:
            return None

        if not 'New confirmed cases' in pq(table[0]).text():
            return None

        regions = []
        for tr in table('tr'):
            text = pq(tr).text().lower()
            if 'total' in text or 'new confirmed' in text:
                continue

            for x, td in enumerate(pq(tr)('td')):
                if x == 0:
                    hhs_region = pq(td).text().strip()
                elif x == 1:
                    try:
                        value = int(pq(td).text().strip())
                        regions.append(DataPoint(
                            schema=SCHEMA_HHS,
                            datatype=DT_CASES_NEW,
                            region=hhs_region,
                            value=value,
                            date_updated=self._get_date(href, html),
                            source_url=href
                        ))
                    except ValueError:
                        # WARNING!!!
                        pass
                else:
                    FIXME

        return regions

    #============================================================#
    #                     Totals by Source                       #
    #============================================================#

    def _get_new_source_of_infection(self, url, html):
        pass

    def _get_total_source_of_infection(self, url, html):
        norm_map = {
            'Locally Acquired—close contact with confirmed case': DT_SOURCE_CONFIRMED,
            'Locally Acquired—no known contact': DT_SOURCE_COMMUNITY,
            'Interstate acquired': DT_SOURCE_INTERSTATE,
            'Overseas acquired': DT_SOURCE_OVERSEAS,
            'Under investigation': DT_SOURCE_UNDER_INVESTIGATION,
        }

        if url == self.STATS_BY_REGION_URL_2:
            table = pq(html)('#QLD_Cases_Sources_Of_Infection')[0]
            #print(pq(table).html())

            r = []
            for header, value in table[0]:
                header = pq(header).text().strip()
                if header == 'Confirmed cases':
                    continue

                value = pq(value).text().strip()
                r.append(DataPoint(
                    datatype=norm_map[header],
                    value=int(value.replace(',', '')),
                    date_updated=self._get_date(url, html),
                    source_url=url
                ))
            return r
        else:
            return []

    #============================================================#
    #               Deaths/Hospitalized/Recovered                #
    #============================================================#

    @bothlistingandstat
    def _get_total_dhr(self, href, html):
        # Technically, this is a bad idea adding other irrelevant values to
        # DHR here..but separating it everywhere thru this class would be
        # far worse!
        sbr2_map = {
            'Number of confirmed cases': DT_CASES_TOTAL,
            'Last 24 hours': DT_CASES_NEW,
            'Active cases': DT_CASES_ACTIVE,
            'Recovered': DT_CASES_RECOVERED,
            'Current hospitalisations': DT_CASES_HOSPITALIZED,
            'Deaths': DT_CASES_DEATHS
        }

        if href in (self.STATS_BY_REGION_URL,
                    self.STATS_BY_REGION_URL_2):
            # New format as of 22 April
            r = []

            table = pq(html)('#QLD_Cases')
            if table:
                for tr in table[1:]:
                    datatype = sbr2_map[pq(tr[0]).text().strip()]
                    if datatype is None:
                        continue

                    r.append(DataPoint(
                        datatype=datatype,
                        value=int(pq(tr[1]).text().strip()),
                        date_updated=self._get_date(href, html),
                        source_url=href
                    ))

            deaths = pq(html)('.qh-fact-wrapper .lost span')
            if deaths:
                r.append(DataPoint(
                    datatype=DT_CASES_DEATHS,
                    value=int(pq(deaths[0]).text().strip()),
                    date_updated=self._get_date(href, html),
                    source_url=href
                ))
            return r
        else:
            # As of 9th April, the format has added recovered/deaths etc info
            totals_dict = self.__get_totals_from_table(html)
            if not totals_dict:
                return []

            r = []
            r.append(DataPoint(
                datatype=DT_CASES_RECOVERED,
                value=totals_dict['recovered'],
                date_updated=self._get_date(href, html),
                source_url=href
            ))
            r.append(DataPoint(
                datatype=DT_CASES_DEATHS,
                value=totals_dict['deaths'],
                date_updated=self._get_date(href, html),
                source_url=href
            ))
            r.append(DataPoint(
                datatype=DT_CASES_ACTIVE,
                value=totals_dict['active'],
                date_updated=self._get_date(href, html),
                source_url=href
            ))
            return r

    #============================================================#
    #                  Self-Quarantine Notices                   #
    #============================================================#

    def self_quarantine_notices(self):
        # TODO!
        pass


if __name__ == '__main__':
    from pprint import pprint
    qn = QLDNews()
    pprint(qn.get_data())