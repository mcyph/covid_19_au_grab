#============================================
# Schemas
#============================================

# Kinds of schemas
SCHEMA_ADMIN_0 = 0
SCHEMA_ADMIN_1 = 1  # Values for the whole state
SCHEMA_POSTCODE = 2
SCHEMA_LGA = 3  # Local Government Area
SCHEMA_HHS = 4  # Queensland
SCHEMA_LHD = 5  # NSW Local Health Districts
SCHEMA_THS = 6  # Tasmania Health Services
SCHEMA_SA3 = 7  # SA3 for ACT

# https://covid-19-coronavirus.tools/
SCHEMA_BD_DISTRICT = 22
SCHEMA_BR_CITY = 8
SCHEMA_CO_MUNICIPALITY = 9
SCHEMA_DE_AGS = 10
SCHEMA_ES_MADRID_MUNICIPALITY = 11
SCHEMA_FR_DEPARTMENT = 12
SCHEMA_FR_OVERSEAS_COLLECTIVITY = 13   # TODO: CONSIDER WHETHER TO REMOVE ME!!!
SCHEMA_IN_DISTRICT = 14
SCHEMA_IT_PROVINCE = 15
SCHEMA_JP_CITY = 16
SCHEMA_MY_DISTRICT = 17
SCHEMA_NZ_DHB = 18  # District Health Board
SCHEMA_TH_DISTRICT = 19
SCHEMA_UK_AREA = 20   # TODO: Split into different countries!!! ==========================================
SCHEMA_US_COUNTY = 21

#============================================
# Datatypes
#============================================

# DT_POPULATION???

# Case numbers+patient status
# (Age ranges are given as a separate value)
DT_NEW = 0
DT_NEW_MALE = 1
DT_NEW_FEMALE = 2
DT_TOTAL = 3
DT_TOTAL_MALE = 4
DT_TOTAL_FEMALE = 5

# Totals by status
DT_STATUS_DEATHS = 6
DT_STATUS_HOSPITALIZED = 7
DT_STATUS_ICU = 8
DT_STATUS_ICU_VENTILATORS = 9
DT_STATUS_RECOVERED = 10
DT_STATUS_ACTIVE = 11
DT_STATUS_UNKNOWN = 12

# Totals by source of infection
DT_SOURCE_OVERSEAS = 16  # Overseas, counted separately
DT_SOURCE_CRUISE_SHIP = 17  # Overseas, included in DT_SOURCE_OVERSEAS
DT_SOURCE_INTERSTATE = 18  # Local-transmission from interstate, counted separately
DT_SOURCE_CONFIRMED = 19  # Local-transmission from confirmed cases, counted separately
DT_SOURCE_COMMUNITY = 20  # Local-unknown community transmission, counted separately
DT_SOURCE_UNDER_INVESTIGATION = 21  # "other"
DT_SOURCE_DOMESTIC = 22  # For in-country which may or may not be community transmission (New Zealand data)

# Test numbers
DT_TESTS_TOTAL = 13
DT_TESTS_NEGATIVE = 14
DT_TESTS_POSITIVE = 15  # (Is this necessary?)


def schema_to_name(x):
    for k, v in globals().items():
        if k.startswith('SCHEMA_') and v == x:
            return k[7:].lower()


def constant_to_name(x):
    for k, v in globals().items():
        if k.startswith('DT_') and v == x:
            return k[3:].lower()


def name_to_schema(x):
    return globals()['SCHEMA_'+x.upper()]


def name_to_constant(x):
    return globals()['DT_' + x.upper()]

