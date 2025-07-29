import numpy as np
import pandas as pd
from enum import Enum


__all__ = [
    # true const
    'BEGINNING_DATE',
    'ACTIVE_DATE',
    'PrismComponentType',
    'SMValues',
    'CategoryComponent',
    'PACKAGE_NAME',
    'SPECIALVALUEMAP',
    'FILEEXTENSION',
    # param types
    'PreferenceType',
    'FrequencyType',
    'ScreenFrequencyType',
    'FBFrequencyType',
    'UniverseFrequencyType',
    'FinancialPeriodType',
    'FinancialPeriodTypeWithLTMQSA',
    'EstimatePeriodTypeNTM',
    'EstimatePeriodType',
    'DilutionType',
    'RankType',
    'DateType',
    'AggregationType',
    'FinancialPreliminaryType',
    'FillnaMethodType',
    'CompanyRelAttributeType',
]


BEGINNING_DATE = pd.to_datetime('1700-01-01')
ACTIVE_DATE = pd.to_datetime('2199-12-31')
SMValues = None
PreferenceType = None
CategoryComponent = None
FunctionComponents = None
TaskComponents = None
DataComponents = None
SMAttributemap = None

class PrismComponentType(str, Enum):
    FUNCTION_COMPONENT = 'functioncomponent'
    DATA_COMPONENT = 'datacomponent'
    TASK_COMPONENT = 'taskcomponent'
    MODEL_COMPONENT = 'modelcomponent'


class CompanyRelAttributeType(Enum):
    COMPANYNAME = "companyname"
    LISTINGID = "listingid"
    COMPANYID = "companyid"


class DilutionType(Enum):
    ALL = "all"
    PARTNER = "partner"
    EXERCISABLE = "exercisable"


class FrequencyType(str, Enum):
    NANOSECONDS = 'N'
    MICROSECONDS = 'U'
    MICROSECONDS_ALIAS = 'us'
    MILISECONDS = 'L'
    MILISECONDS_ALIAS = 'ms'
    SECONDS = 'S'
    MINUTES = 'T'
    MINUTES_ALIAS = 'min'
    HOURS = 'H'
    BUSINESS_HOURS = 'BH'
    CALENDAR_DAY = 'D'
    BUSINESS_DAY = 'BD'
    WEEKS = 'W'
    MONTH_START = 'MS'
    BUSINESS_MONTH_START = 'BMS'
    SEMI_MONTH_START = 'SMS'
    SEMI_MONTH_END = 'SM'
    BUSINESS_MONTH_END = 'BM'
    MONTH_END = 'M'
    QUARTER_END = 'Q'
    QUARTER_START = 'QS'
    BUSINESS_QUARTER_END = 'BQ'
    BUSINESS_QUARTER_START = 'BQS'
    YEAR_START = 'AS'
    YEAR_END = 'A'


class ResampleFrequencyType(str, Enum):
    CALENDAR_DAY = 'D'
    BUSINESS_DAY = 'BD'
    WEEKS = 'W'
    BUSINESS_MONTH_END = 'BM'
    MONTH_END = 'M'
    QUARTER_END = 'Q'
    YEAR_END = 'A'


class ScreenFrequencyType(str, Enum):
    CALENDAR_DAY = 'D'
    BUSINESS_DAY = 'BD'
    WEEKS = 'W'
    BUSINESS_MONTH_END = 'BM'
    MONTH_END = 'M'
    QUARTER_END = 'Q'
    YEAR_END = 'A'


class FBFrequencyType(str, Enum):
    CALENDAR_DAY = 'D'
    BUSINESS_DAY = 'BD'
    WEEKS = 'W'
    BUSINESS_MONTH_END = 'BM'
    MONTH_END = 'M'
    QUARTER_END = 'Q'
    YEAR_END = 'A'


class UniverseFrequencyType(str, Enum):
    CALENDAR_DAY = 'D'
    WEEKS = 'W'
    MONTH_START = 'MS'
    SEMI_MONTH_START = 'SMS'
    SEMI_MONTH_END = 'SM'
    MONTH_END = 'M'
    QUARTER_END = 'Q'
    QUARTER_START = 'QS'
    YEAR_START = 'AS'
    YEAR_END = 'A'


class RankType(str, Enum):
    STANDARD = 'standard'
    MODIFIED = 'modified'
    DENSE = 'dense'
    ORDINAL = 'ordinal'
    FRACTIONAL = 'fractional'


class DateType(str, Enum):
    ENTEREDDATE = 'entereddate'
    ANNOUNCEDDATE = 'announceddate'


class FinancialPeriodType(str, Enum):
    ANNUAL = 'Annual'
    A = 'A'
    SEMI_ANNUAL = 'Semi-Annual'
    SA = 'SA'
    QUARTERLY = 'Quarterly'
    Q = 'Q'


class FinancialPeriodTypeWithLTMQSA(str, Enum):
    ANNUAL = 'Annual'
    A = 'A'
    SEMI_ANNUAL = 'Semi-Annual'
    SA = 'SA'
    QUARTERLY = 'Quarterly'
    Q = 'Q'
    LTM = 'LTM'
    QSA = 'Q-SA'


class EstimatePeriodType(str, Enum):
    ANNUAL = 'Annual'
    A = 'A'
    SEMI_ANNUAL = 'Semi-Annual'
    SA = 'SA'
    QUARTERLY = 'Quarterly'
    Q = 'Q'
    NONE = None
    QSA = 'Q-SA'


class EstimatePeriodTypeNTM(str, Enum):
    ANNUAL = 'Annual'
    A = 'A'
    SEMI_ANNUAL = 'Semi-Annual'
    SA = 'SA'
    QUARTERLY = 'Quarterly'
    Q = 'Q'
    NONE = None
    QSA = 'Q-SA'
    NTM = 'NTM'

class StarminePeriodType(str, Enum):
    ANNUAL = 'Annual'
    A = 'A'
    SEMI_ANNUAL = 'Semi-Annual'
    SA = 'SA'
    QUARTERLY = 'Quarterly'
    Q = 'Q'
    NONE = None
    QSA = 'Q-SA'
    NTM = 'NTM'


class SegmentClassification(str, Enum):
    SIC = 'SIC'
    NAICS = 'NAICS'
    sic = 'sic'
    naics = 'naics'
    NONE = None


class WeekEndType(str, Enum):
    SATSUN = 'Sat-Sun'
    FRISAT = 'Fri-Sat'
    THUFRI = 'Thu-Fri'
    FRI = 'Fri'


class AggregationType(str, Enum):
    ONEDAY = '1 day'
    ONEWEEK = '1 week'
    ONEMONTH = '1 month'
    TWOMONTH = '2 month'
    THREEMONTH = '3 month'
    THREEMONTHLATEST = '3 month latest'


class FinancialPreliminaryType(str, Enum):
    KEEP = 'keep'
    IGNORE = 'ignore'
    NULL = 'null'


class FillnaMethodType(str, Enum):
    BACKFILL = 'backfill'
    BFILL = 'bfill'
    PAD = 'pad'
    FFILL = 'ffill'
    NONE = None


FILEEXTENSION = {'pdq': 'dataquery', 'ptq': 'taskquery', 'pws': 'workspace', 'puv': 'universe', 'ppt': 'portfolio', 'ped': 'datafile'}


# PACKAGE_NAME = 'p3s9'
PACKAGE_NAME = 'prism'


SPECIALVALUEMAP = {
    np.nan: "\x01NaN",
    np.inf: "\x01inf",
    -np.inf: "\x01ninf",  # Use -np.inf instead of np.NINF
}


DaysRepr = [
    'm',
    'mon',
    'monday',
    't',
    'tu',
    'tue',
    'tues',
    'tuesday',
    'w',
    'wed',
    'wednesday',
    'r',
    'th',
    'thu',
    'thurs',
    'thursday',
    'f',
    'fr',
    'fri',
    'friday',
    's',
    'sa',
    'sat',
    'saturday',
    'u',
    'su',
    'sun',
    'sunday'
]

CURRENCYLIST = [
    "AAD",
    "ADP",
    "AED",
    "AFA",
    "AFN",
    "ALL",
    "AMD",
    "ANG",
    "AOA",
    "AON",
    "ARS",
    "ATS",
    "AUD",
    "AWG",
    "AZM",
    "AZN",
    "BAM",
    "BBD",
    "BDT",
    "BEF",
    "BGL",
    "BGN",
    "BHD",
    "BIF",
    "BMD",
    "BND",
    "BOB",
    "BRL",
    "BSD",
    "BTN",
    "BWP",
    "BYN",
    "BYR",
    "BZD",
    "CAD",
    "CDF",
    "CHF",
    "CLF",
    "CLP",
    "CNH",
    "CNY",
    "COP",
    "CRC",
    "CSD",
    "CUP",
    "CVE",
    "CYP",
    "CZK",
    "DDM",
    "DEM",
    "DJF",
    "DKK",
    "DOP",
    "DZD",
    "ECS",
    "EEK",
    "EGP",
    "ERN",
    "ESP",
    "ETB",
    "EUR",
    "FIM",
    "FJD",
    "FKP",
    "FRF",
    "GBP",
    "GBX",
    "GEL",
    "GHC",
    "GHS",
    "GIP",
    "GMD",
    "GNF",
    "GRD",
    "GTQ",
    "GWP",
    "GYD",
    "HKD",
    "HNL",
    "HRK",
    "HTG",
    "HUF",
    "IDN",
    "IDR",
    "IEP",
    "ILA",
    "ILS",
    "INR",
    "IQD",
    "IRR",
    "ISK",
    "ITL",
    "JMD",
    "JOD",
    "JPY",
    "KES",
    "KGS",
    "KHR",
    "KMF",
    "KPW",
    "KRW",
    "KWD",
    "KWF",
    "KYD",
    "KZT",
    "LAK",
    "LBP",
    "LKR",
    "LRD",
    "LSL",
    "LTL",
    "LUF",
    "LVL",
    "LYD",
    "MAD",
    "MDL",
    "MGA",
    "MGF",
    "MKD",
    "MMK",
    "MNT",
    "MOP",
    "MRO",
    "MRU",
    "MTL",
    "MUR",
    "MVR",
    "MWK",
    "MXN",
    "MXV",
    "MYR",
    "MZM",
    "MZN",
    "NAD",
    "NGN",
    "NIO",
    "NLG",
    "NOK",
    "NPR",
    "NZD",
    "OMR",
    "PAB",
    "PEN",
    "PGK",
    "PHP",
    "PKR",
    "PLN",
    "PPP",
    "PTE",
    "PYG",
    "QAR",
    "ROL",
    "RON",
    "RSD",
    "RUB",
    "RUR",
    "RWF",
    "SAC",
    "SAR",
    "SBD",
    "SCR",
    "SDD",
    "SDG",
    "SDP",
    "SEK",
    "SGD",
    "SHP",
    "SIT",
    "SKK",
    "SLL",
    "SOS",
    "SRD",
    "SRG",
    "STD",
    "SVC",
    "SYP",
    "SZL",
    "THB",
    "TJR",
    "TJS",
    "TMM",
    "TMT",
    "TND",
    "TOF",
    "TOP",
    "TPE",
    "TRL",
    "TRY",
    "TTD",
    "TWD",
    "TZS",
    "UAH",
    "UGX",
    "USD",
    "USX",
    "UYU",
    "UZS",
    "VEB",
    "VEF",
    "VES",
    "VND",
    "VUV",
    "WST",
    "XAF",
    "XBA",
    "XBB",
    "XCD",
    "XDR",
    "XEU",
    "XOF",
    "XPF",
    "XUA",
    "YER",
    "YUM",
    "ZAC",
    "ZAR",
    "ZMK",
    "ZMW",
    "ZWD",
    "ZWL",
]

CurrencyType = Enum('CurrencyType', [(c, c) for c in CURRENCYLIST], type=str)

CurrencyTypeWithReportTrade = Enum('CurrencyTypeWithReportTrade', [(c, c) for c in ["report", "trade",] + CURRENCYLIST], type=str)

class TaskStatusType(str, Enum):
    PENDING = "Pending"
    RUNNING = "Running"
    COMPLETED = "Completed"
    FAILED = "Failed"
    CANCELED = "Canceled"