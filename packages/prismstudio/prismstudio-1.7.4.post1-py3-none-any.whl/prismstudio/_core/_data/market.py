import re

import pandas as pd

from .._req_builder import _list_dataitem, _dataquery
from ..._common.const import (
    DilutionType as _DilutionType,
    CurrencyTypeWithReportTrade as _CurrencyTypeWithReportTrade
)
from ..._prismcomponent.prismcomponent import _PrismComponent, _PrismDataComponent
from ..._utils import _get_params, _validate_args, _req_call
from ..._utils.exceptions import PrismValueError


__all__ = [
    'open',
    'close',
    'high',
    'low',
    'bid',
    'ask',
    'vwap',
    'totalreturnindex',
    'market_cap',
    'volume',
    'dividend',
    'exchange_rate',
    'short_interest',
    'split',
    'split_adjustment_factor',
    'dividend_adjustment_factor',
    'shares_outstanding',
    'enterprise_value',
    'diluted_market_cap',
    'beta',
    'dataitems',
]


_data_category = __name__.split(".")[-1]


class _PrismMarketComponent(_PrismDataComponent, _PrismComponent):
    _component_category_repr = _data_category


class open(_PrismMarketComponent):
    """
    | Daily open pricing history for equity securities.
    | Default frequency is business daily.

    Parameters
    ----------
        adjustment : bool, default True
            | Whether to apply split adjustment for pricing data.

        currency : str {'trade', 'report', ISO3 currency}, default 'trade'
            | Desired currency for the pricing data.

            - trade : trading currency for a given listing (i.e for Apple - USD, Tencent - HKD)
            - report : financial reporting currency for a given listing (i.e for Apple - USD, Tencent - CNY)
            - ISO3 currency : desired currency in ISO 4217 format (i.e USD, EUR, JPY, KRW, etc.)

        package : str {'Datastream 2', 'CIQ Market', 'MI Integrated Market', 'Compustat'}
            | Desired data package in where the pricing data outputs from.

            .. admonition:: Warning
                :class: warning

                If an invalid package is entered without a license, an error will be generated as output.

    Returns
    -------
        prismstudio._PrismComponent: Historical time-series of daily open prices for stocks

    Examples
    --------
        >>> open_prc = ps.market.open(adjustment=True, package='Prism Market')
        >>> open_df = ps.get_data([open_prc], 'US Primary', startdate='2015-01-01', enddate='2020-12-31', shownid=['ticker'])
        >>> open_df
                 listingid        date    Open  Ticker
        0          2585895  2019-01-02  36.700     AIR
        1          2586016  2019-01-02  31.510     ABM
        2          2586086  2019-01-02  44.590     AFL
        3          2586108  2019-01-02  54.960    AGCO
        4          2586130  2019-01-02  14.270     AES
        ...            ...         ...     ...     ...
        674006  1802037081  2020-12-31  10.180    LVWR
        674007  1805964301  2020-12-31  10.164    GRNT
        674008  1823326675  2020-12-31  76.510   CR.WI
        674009  1836807464  2020-12-31  26.510     CLB
        674010  1864533284  2020-12-31  41.860     LAZ
    """
    @_validate_args
    def __init__(
        self,
        adjustment: bool = True,
        currency: _CurrencyTypeWithReportTrade = 'trade',
        package : str = None,
    ):
        super().__init__(**_get_params(vars()))


class close(_PrismMarketComponent):
    """
    | Daily close pricing history for equity securities.
    | Default frequency is business daily.

    Parameters
    ----------
        adjustment : bool, default True
            | Whether to apply split adjustment for pricing data.

        currency : str {'trade', 'report', ISO3 currency}, default 'trade'
            | Desired currency for the pricing data.

            - trade : trading currency for a given listing (i.e for Apple - USD, Tencent - HKD)
            - report : financial reporting currency for a given listing (i.e for Apple - USD, Tencent - CNY)
            - ISO3 currency : desired currency in ISO 4217 format (i.e USD, EUR, JPY, KRW, etc.)

        package : str {'Datastream 2', 'CIQ Market', 'MI Integrated Market', 'Compustat'}
            | Desired data package in where the pricing data outputs from.

            .. admonition:: Warning
                :class: warning

                If an invalid package is entered without a license, an error will be generated as output.

    Returns
    -------
        prismstudio._PrismComponent: Historical time-series of daily close prices for stocks

    Examples
    --------
        Obtain daily closing prices for a specific security:

        >>> close = ps.market.close(adjustment=True, package='Prism Market')
        >>> close_df = ps.get_data([close], 'US Primary', startdate='2015-01-01', enddate='2020-12-31', shownid=['ticker'])
        >>> close_df
                 listingid        date   Close  Ticker
        0          2585895  2019-01-02  37.450     AIR
        1          2586016  2019-01-02  31.280     ABM
        2          2586086  2019-01-02  45.520     AFL
        3          2586108  2019-01-02  55.540    AGCO
        4          2586130  2019-01-02  14.180     AES
        ...            ...         ...     ...     ...
        674006  1802037081  2020-12-31  10.100    LVWR
        674007  1805964301  2020-12-31  10.012    GRNT
        674008  1823326675  2020-12-31  77.660   CR.WI
        674009  1836807464  2020-12-31  26.510     CLB
        674010  1864533284  2020-12-31  42.300     LAZ
    """
    @_validate_args
    def __init__(
        self,
        adjustment: bool = True,
        currency: _CurrencyTypeWithReportTrade = 'trade',
        package : str = None,
    ):
        super().__init__(**_get_params(vars()))


class high(_PrismMarketComponent):
    """
    | Daily high pricing history for equity securities.
    | Default frequency is business daily.

    Parameters
    ----------
        adjustment : bool, default True
            | Whether to apply split adjustment for pricing data.

        currency : str {'trade', 'report', ISO3 currency}, default 'trade'
            | Desired currency for the pricing data.

            - trade : trading currency for a given listing (i.e for Apple - USD, Tencent - HKD)
            - report : financial reporting currency for a given listing (i.e for Apple - USD, Tencent - CNY)
            - ISO3 currency : desired currency in ISO 4217 format (i.e USD, EUR, JPY, KRW, etc.)

        package : str {'Datastream 2', 'CIQ Market', 'MI Integrated Market', 'Compustat'}
            | Desired data package in where the pricing data outputs from.

            .. admonition:: Warning
                :class: warning

                If an invalid package is entered without a license, an error will be generated as output.

    Returns
    -------
        prismstudio._PrismComponent: Historical time-series of daily high prices for stocks

    Examples
    --------
        >>> high = ps.market.high(adjustment=True, package='Prism Market')
        >>> high_df = ps.get_data([high], 'US Primary', startdate='2015-01-01', enddate='2020-12-31', shownid=['ticker'])
        >>> high_df
                 listingid        date     High  Ticker
        0          2585895  2019-01-02  37.4500     AIR
        1          2586016  2019-01-02  31.6300     ABM
        2          2586086  2019-01-02  45.5800     AFL
        3          2586108  2019-01-02  55.9500    AGCO
        4          2586130  2019-01-02  14.3100     AES
        ...            ...         ...      ...     ...
        674006  1802037081  2020-12-31  10.2000    LVWR
        674007  1805964301  2020-12-31  10.1800    GRNT
        674008  1823326675  2020-12-31  78.0700   CR.WI
        674009  1836807464  2020-12-31  27.0000     CLB
        674010  1864533284  2020-12-31  42.6987     LAZ
    """
    @_validate_args
    def __init__(
        self,
        adjustment: bool = True,
        currency: _CurrencyTypeWithReportTrade = 'trade',
        package : str = None,
    ):
        super().__init__(**_get_params(vars()))


class low(_PrismMarketComponent):
    """
    | Daily low pricing history for equity securities.
    | Default frequency is business daily.

    Parameters
    ----------
        adjustment : bool, default True
            | Whether to apply split adjustment for pricing data.

        currency : str, {'trade', 'report', ISO3 currency}, default 'trade'
            | Desired currency for the pricing data.

            - trade : trading currency for a given listing (i.e for Apple - USD, Tencent - HKD)
            - report : financial reporting currency for a given listing (i.e for Apple - USD, Tencent - CNY)
            - ISO3 currency : desired currency in ISO 4217 format (i.e USD, EUR, JPY, KRW, etc.)

        package : str, {'Datastream 2', 'CIQ Market', 'MI Integrated Market', 'Compustat'}
            | Desired data package in where the pricing data outputs from.

            .. admonition:: Warning
                :class: warning

                If an invalid package is entered without a license, an error will be generated as output.

    Returns
    -------
        prismstudio._PrismComponent: Historical time-series of daily low prices for stocks

    Examples
    --------
        >>> low = ps.market.low(adjustment=True, package='Prism Market')
        >>> low_df = ps.get_data([low], 'US Primary', startdate='2015-01-01', enddate='2020-12-31', shownid=['ticker'])
        >>> low_df
                 listingid        date    Low  Ticker
        0          2585895  2019-01-02  36.49     AIR
        1          2586016  2019-01-02  30.66     ABM
        2          2586086  2019-01-02  44.53     AFL
        3          2586108  2019-01-02  54.40    AGCO
        4          2586130  2019-01-02  14.10     AES
        ...            ...         ...    ...     ...
        674006  1802037081  2020-12-31  10.10    LVWR
        674007  1805964301  2020-12-31   9.88    GRNT
        674008  1823326675  2020-12-31  76.08   CR.WI
        674009  1836807464  2020-12-31  26.04     CLB
        674010  1864533284  2020-12-31  41.85     LAZ
    """
    @_validate_args
    def __init__(
        self,
        adjustment: bool = True,
        currency: _CurrencyTypeWithReportTrade = 'trade',
        package : str = None,
    ):
        super().__init__(**_get_params(vars()))


class ask(_PrismMarketComponent):
    """
    | End of day ask pricing history for equity securities.
    | Default frequency is business daily.

    Parameters
    ----------
        adjustment : bool, default True
            | Whether to apply split adjustment for pricing data.

        currency : str, {'trade', 'report', ISO3 currency}, default 'trade'
            | Desired currency for the pricing data.

            - trade : trading currency for a given listing (i.e for Apple - USD, Tencent - HKD)
            - report : financial reporting currency for a given listing (i.e for Apple - USD, Tencent - CNY)
            - ISO3 currency : desired currency in ISO 4217 format (i.e USD, EUR, JPY, KRW, etc.)

        package : str, {'Datastream 2', 'CIQ Market', 'MI Integrated Market'}
            | Desired data package in where the pricing data outputs from.

            .. admonition:: Warning
                :class: warning

                If an invalid package is entered without a license, an error will be generated as output.

    Returns
    -------
        prismstudio._PrismComponent: Historical time-series of daily end of day ask prices for stocks

    Examples
    --------
        >>> ask = ps.market.ask(adjustment=True, package='Prism Market')
        >>> ask_df = ps.get_data([ask], 'KOSPI 200 Index', startdate='2015-01-01', enddate='2020-12-31', shownid=['ticker'])
        >>> ask_df
                 listingid        date     Ask  Ticker
        0          2585895  2019-01-02  37.450     AIR
        1          2586016  2019-01-02  31.280     ABM
        2          2586086  2019-01-02  45.520     AFL
        3          2586108  2019-01-02  55.570    AGCO
        4          2586130  2019-01-02  14.200     AES
        ...            ...         ...     ...     ...
        677477  1802037081  2020-12-31  10.170    LVWR
        677478  1805964301  2020-12-31  10.144    GRNT
        677479  1823326675  2020-12-31  77.670   CR.WI
        677480  1836807464  2020-12-31  26.510     CLB
        677481  1864533284  2020-12-31  42.310     LAZ
    """
    @_validate_args
    def __init__(
        self,
        adjustment: bool = True,
        currency: _CurrencyTypeWithReportTrade = 'trade',
        package : str = None,
    ):
        super().__init__(**_get_params(vars()))


class bid(_PrismMarketComponent):
    """
    | End of day bid pricing history for equity securities.
    | Default frequency is business daily.

    Parameters
    ----------
        adjustment : bool, default True
            | Whether to apply split adjustment for pricing data.

        currency : str, {'trade', 'report', ISO3 currency}, default 'trade'
            | Desired currency for the pricing data.

            - trade : trading currency for a given listing (i.e for Apple - USD, Tencent - HKD)
            - report : financial reporting currency for a given listing (i.e for Apple - USD, Tencent - CNY)
            - ISO3 currency : desired currency in ISO 4217 format (i.e USD, EUR, JPY, KRW, etc.)

        package : str, {'Datastream 2', 'CIQ Market', 'MI Integrated Market'}
            | Desired data package in where the pricing data outputs from.

            .. admonition:: Warning
                :class: warning

                If an invalid package is entered without a license, an error will be generated as output.

    Returns
    -------
        prismstudio._PrismComponent: Historical time-series of daily end of day ask prices for stocks

    Examples
    --------
        >>> bid = ps.market.bid(adjustment=True, package='Prism Market')
        >>> bid_df = ps.get_data([bid], 'KOSPI 200 Index', startdate='2015-01-01', enddate='2020-12-31', shownid=['ticker'])
        >>> bid_df
                 listingid        date    Bid  Ticker
        0          2585895  2019-01-02  37.43     AIR
        1          2586016  2019-01-02  31.27     ABM
        2          2586086  2019-01-02  45.51     AFL
        3          2586108  2019-01-02  55.55    AGCO
        4          2586130  2019-01-02  14.19     AES
        ...            ...         ...    ...     ...
        677479  1802037081  2020-12-31  10.11    LVWR
        677480  1805964301  2020-12-31  10.00    GRNT
        677481  1823326675  2020-12-31  77.66   CR.WI
        677482  1836807464  2020-12-31  26.47     CLB
        677483  1864533284  2020-12-31  42.30     LAZ
    """
    @_validate_args
    def __init__(
        self,
        adjustment: bool = True,
        currency: _CurrencyTypeWithReportTrade = 'trade',
        package : str = None,
    ):
        super().__init__(**_get_params(vars()))


class vwap(_PrismMarketComponent):
    """
    | Daily VWAP pricing history for equity securities.
    | Default frequency is business daily.

    Parameters
    ----------
        adjustment : bool, default True
            | Whether to apply split adjustment for pricing data.

        currency : str, {'trade', 'report', ISO3 currency}, default 'trade'
            | Desired currency for the pricing data.

            - trade : trading currency for a given listing (i.e for Apple - USD, Tencent - HKD)
            - report : financial reporting currency for a given listing (i.e for Apple - USD, Tencent - CNY)
            - ISO3 currency : desired currency in ISO 4217 format (i.e USD, EUR, JPY, KRW, etc.)

        package : str, {'Datastream 2', 'CIQ Market'}
            | Desired data package in where the pricing data outputs from.

            .. admonition:: Warning
                :class: warning

                If an invalid package is entered without a license, an error will be generated as output.

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
        >>> vwap = ps.market.vwap(adjustment=True, package='CIQ Market')
        >>> vwap_df = ps.get_data([vwap], 'KOSPI 200 Index', startdate='2019-01-01', enddate='2020-12-31', shownid=['ticker'])
        >>> vwap_df
                 listingid        date   VWAP  Ticker
        0          2585895  2019-01-02  37.00     AIR
        1          2586016  2019-01-02  31.18     ABM
        2          2586086  2019-01-02  45.25     AFL
        3          2586108  2019-01-02  55.46    AGCO
        4          2586130  2019-01-02  14.19     AES
        ...            ...         ...    ...     ...
        674214  1802037081  2020-12-31  10.14    LVWR
        674215  1805964301  2020-12-31  25.27    GRNT
        674216  1823326675  2020-12-31  77.55   CR.WI
        674217  1836807464  2020-12-31  26.59     CLB
        674218  1864533284  2020-12-31  42.33     LAZ
    """
    @_validate_args
    def __init__(
        self,
        adjustment: bool = True,
        currency: _CurrencyTypeWithReportTrade = 'trade',
        package : str = None,
    ):
        super().__init__(**_get_params(vars()))


class totalreturnindex(_PrismMarketComponent):
    """
    | Total Return Index.
    | Default frequency is business daily.

    Parameters
    ----------
        currency : str, {'trade', 'report', ISO3 currency}, default 'trade'
            | Desired currency for the pricing data.

            - trade : trading currency for a given listing (i.e for Apple - USD, Tencent - HKD)
            - report : financial reporting currency for a given listing (i.e for Apple - USD, Tencent - CNY)
            - ISO3 currency : desired currency in ISO 4217 format (i.e USD, EUR, JPY, KRW, etc.)
        package : str, {'Datastream 2', 'CIQ Market'}
            | Desired data package in where the pricing data outputs from.

            .. admonition:: Warning
                :class: warning

                If an invalid package is entered without a license, an error will be generated as output.

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
        >>> tri = ps.market.totalreturnindex(package='CIQ Market')
        >>> tri_df = ps.get_data([tri], 'US Primary', startdate='2019-01-01', enddate='2020-12-31', shownid=['ticker'])
        >>> tri_df
                 listingid        date  TotalReturnIndex  Ticker
        0          2585895  2019-01-02         36.953489     AIR
        1          2586016  2019-01-02         28.216722     ABM
        2          2586086  2019-01-02         39.831779     AFL
        3          2586108  2019-01-02         46.698283    AGCO
        4          2586130  2019-01-02         11.959990     AES
        ...            ...         ...               ...     ...
        674006  1802037081  2020-12-31         10.100000    LVWR
        674007  1805964301  2020-12-31          8.931607    GRNT
        674008  1823326675  2020-12-31         47.849145   CR.WI
        674009  1836807464  2020-12-31         26.344193     CLB
        674010  1864533284  2020-12-31         35.244537     LAZ
    """
    @_validate_args
    def __init__(
        self,
        currency: _CurrencyTypeWithReportTrade = 'trade',
        package : str = None,
    ):
        super().__init__(**_get_params(vars()))


class market_cap(_PrismMarketComponent):
    """
    | Market capitalization history for equity securities aggregated to the company level.
    | Default frequency is daily.

    Parameters
    ----------

        currency : str {'trade', 'report', ISO3 currency}, default 'trade'
            | Desired currency for the pricing data.

            - trade : trading currency for a given listing (i.e for Apple - USD, Tencent - HKD)
            - report : financial reporting currency for a given listing (i.e for Apple - USD, Tencent - CNY)
            - ISO3 currency : desired currency in ISO 4217 format (i.e USD, EUR, JPY, KRW, etc.)

        package : str {'Datastream 2', 'CIQ Market'}
            | Desired data package in where the pricing data outputs from.

            .. admonition:: Warning
                :class: warning

                If an invalid package is entered without a license, an error will be generated as output.


    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
        >>> mcap = ps.market.market_cap()
        >>> mcap_df = mcap.get_data(universe=1, startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
        >>> mcap_df
                 listingid        date     marketcap  currency  Ticker
        0          2585895  2019-01-01  1.282838e+09       USD     AIR
        1          2586016  2019-01-01  2.120207e+09       USD     ABM
        2          2586086  2019-01-01  3.468389e+10       USD     AFL
        3          2586108  2019-01-01  4.358080e+09       USD    AGCO
        4          2586130  2019-01-01  9.576822e+09       USD     AES
        ...            ...         ...           ...       ...     ...
        987451  1823326675  2020-12-31  4.512671e+09       USD   CR.WI
        987452  1836807464  2020-12-31  1.179554e+09       USD     CLB
        987453  1847213170  2020-12-31  8.280520e+08       USD     DBD
        987454  1863468819  2020-12-31  2.923089e+09       USD    BANC
        987455  1864533284  2020-12-31  4.442852e+09       USD     LAZ
    """
    @_validate_args
    def __init__(
        self,
        currency: _CurrencyTypeWithReportTrade = 'trade',
        package : str = None,
    ):
        super().__init__(**_get_params(vars()))


class volume(_PrismMarketComponent):
    """
    | Daily volume for equity securities.
    | Default frequency is business daily.

    Parameters
    ----------
        adjustment : bool, default True
            | Whether to apply split adjustment for pricing data.

        package : str, {'Datastream 2', 'CIQ Market', 'MI Integrated Market', 'Compustat'}
            | Desired data package in where the pricing data outputs from.

            .. admonition:: Warning
                :class: warning

                If an invalid package is entered without a license, an error will be generated as output.

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
        >>> volume = ps.market.volume(package='MI Integrated Market')
        >>> volume_df = ps.get_data([volume], 'KOSPI 200 Index', startdate='2019-01-01', enddate='2020-12-31', shownid=['ticker'])
        >>> volume_df
                 listingid        date     volume  Ticker
        0          2585895  2019-01-02   425243.0     AIR
        1          2586016  2019-01-02  1039294.0     ABM
        2          2586086  2019-01-02  4022076.0     AFL
        3          2586108  2019-01-02   771259.0    AGCO
        4          2586130  2019-01-02  5577757.0     AES
        ...            ...         ...        ...     ...
        673685  1802037081  2020-12-31   257811.0    LVWR
        673686  1805964301  2020-12-31   174765.0    GRNT
        673687  1823326675  2020-12-31   221021.0   CR.WI
        673688  1836807464  2020-12-31   276963.0     CLB
        673689  1864533284  2020-12-31   322238.0     LAZ
    """
    @_validate_args
    def __init__(
        self,
        adjustment: bool = True,
        package : str = None,
    ):
        super().__init__(**_get_params(vars()))


class dividend(_PrismMarketComponent):
    """
    | Dividend history for equity securities.
    | Default frequency is aperiodic daily.

    Parameters
    ----------
        adjustment : bool, default True
            | Whether to apply split adjustment for dividend data.

        currency : str, {'trade', 'report', ISO3 currency}, default 'trade'
            | Desired currency for the pricing data.

            - trade : trading currency for a given listing (i.e for Apple - USD, Tencent - HKD)
            - report : financial reporting currency for a given listing (i.e for Apple - USD, Tencent - CNY)
            - ISO3 currency : desired currency in ISO 4217 format (i.e USD, EUR, JPY, KRW, etc.)
            - None : dividend payment currency

        aggregate: bool, default True
            | Desired aggregation for dividend. If True, dividends are aggregated based on listingid and exdate.

            - If `True`, paymentdate and dividendtype column will be dropped
            - If `True`, and currency is `None`, the currency will be automatically set to `trade`

        package : str, {'Datastream 2', 'CIQ Market', 'Compustat'}
            | Desired data package in where the pricing data outputs from.

            .. admonition:: Warning
                :class: warning

                If an invalid package is entered without a license, an error will be generated as output.

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
        >>> dividend = ps.market.dividend(package='CIQ Market')
        >>> dividend _df = ps.get_data([dividend], 'US Primary', startdate='2019-01-01', enddate='2020-12-31', shownid=['ticker'])
        >>> dividend _df
	        listingid        date  currency  dividend  Ticker
        0     2586016  2019-01-02       USD     0.180     ABM
        1     2610173  2019-01-02       USD     0.080     ESE
        2     2615302  2019-01-02       USD     0.130     GLT
        3     2618177  2019-01-02       USD     0.070     HEI
        4     2642205  2019-01-02       USD     0.510     RJF
        ...       ...         ...       ...       ...     ...
        6150  2642876  2020-12-31       USD     0.425     RSG
        6151  2654494  2020-12-31       USD     0.520     STT
        6152  2657915  2020-12-31       USD     0.410     THO
        6153  2664785  2020-12-31       USD     0.100     WWW
        6154  4931722  2020-12-31       USD     0.280     EHC
    """
    @_validate_args
    def __init__(
        self,
        adjustment: bool = True,
        currency: _CurrencyTypeWithReportTrade = 'trade',
        aggregate: bool = True,
        package : str = None,
    ):
        super().__init__(**_get_params(vars()))


class dividend_adjustment_factor(_PrismMarketComponent):
    """
    | Dividend adjustment factor history for equity securities.
    | Default frequency is daily.

    Parameters
    ----------
    package : str, {'Datastream 2', 'CIQ Market'}
        | Desired data package in where the pricing data outputs from.

        .. admonition:: Warning
            :class: warning

            If an invalid package is entered without a license, an error will be generated as output.

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
        >>> divadj = ps.market.dividend_adjustment_factor()
        >>> divadj_df = divadj.get_data()
                  listingid        date       adj  Ticker
        0           2585895  2019-01-01  0.986742     AIR
        1           2586086  2019-01-01  0.875039     AFL
        2           2586108  2019-01-01  0.840805    AGCO
        3           2586118  2019-01-01  1.000000     GAS
        4           2586122  2019-01-01  1.000000     ASV
        ...             ...         ...       ...     ...
        1653553  1774529164  2020-12-31  0.918087    DINO
        1653554  1805964301  2020-12-31  0.892090    GRNT
        1653555  1823326675  2020-12-31  0.616136   CR.WI
        1653556  1836807464  2020-12-31  0.993745     CLB
        1653557  1864533284  2020-12-31  0.833204     LAZ
    """
    @_validate_args
    def __init__(self, package : str = None):
        super().__init__(**_get_params(vars()))


class split(_PrismMarketComponent):
    """
    | Return the split history for equity securities.
    | Default frequency is aperiodic daily.

    Parameters
    ----------
    package : str, {'Datastream 2', 'CIQ Market', 'Compustat'}
        | Desired data package in where the pricing data outputs from.

        .. admonition:: Warning
            :class: warning

            If an invalid package is entered without a license, an error will be generated as output.

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
        >>> split = ps.market.split()
        >>> split_df = split.get_data(universe=1, startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
        >>> split_df
            listingid        date     split   Ticker
        0    20126254  2015-07-29  1.350000  A014830
        1    20158335  2013-04-30  0.100000  A008000
        2    20158445  2015-01-01  0.620935  A004150
        3    20158447  2010-12-29  1.030000  A001060
        4    20158758  2012-10-19  0.142857  A001440
        ..        ...         ...       ...      ...
        60  104646533  2014-09-01  0.478239  A060980
        61  107478344  2012-12-27  1.050000  A128940
        62  107478344  2014-02-10  1.050000  A128940
        63  107478344  2014-12-29  1.050000  A128940
        64  107478344  2015-12-29  1.020000  A128940
    """
    @_validate_args
    def __init__(self, package : str = None):
        super().__init__(**_get_params(vars()))


class split_adjustment_factor(_PrismMarketComponent):
    """
    | Split adjustment factor history for equity securities.
    | Default frequency is daily.

    Parameters
    ----------
    package : str, {'Datastream 2', 'CIQ Market', 'Compustat'}
        | Desired data package in where the pricing data outputs from.

        .. admonition:: Warning
            :class: warning

            If an invalid package is entered without a license, an error will be generated as output.

    Returns
    -------
        prismstudio._PrismComponent
    """
    @_validate_args
    def __init__(self, package : str = None):
        super().__init__(**_get_params(vars()))


class exchange_rate(_PrismMarketComponent):
    """
    | Daily exchange rate history.
    | Default frequency is daily.

    Parameters
    ----------
        currency : list of ISO3 currency
            | Desired exchange rates.
        to_convert : bool, default False
            | True: daily
            | False : business daily

        package : str, {'Datastream 2', 'CIQ Market', 'Compustat'}
            | Desired data package in where the pricing data outputs from.

            .. admonition:: Warning
                :class: warning

                If an invalid package is entered without a license, an error will be generated as output.

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
        >>> exrt = ps.market.exchange_rate(currency=['USD', 'KRW'])
        >>> exrt_df = exrt.get_data(startdate='2010-01-01', enddate='2015-12-31')
        >>> exrt_df
            currency        date       exrt
        0         KRW  2010-01-01  1881.5000
        1         KRW  2010-01-02  1881.5000
        2         KRW  2010-01-03  1881.5000
        3         KRW  2010-01-04  1854.5000
        4         KRW  2010-01-05  1826.1000
        ...       ...         ...        ...
        3873      USD  2015-12-27     1.4933
        3874      USD  2015-12-28     1.4903
        3875      USD  2015-12-29     1.4795
        3876      USD  2015-12-30     1.4833
        3877      USD  2015-12-31     1.4740
    """
    @_validate_args
    def __init__(self, currency: list, to_convert: bool = False, package : str = None):
        super().__init__(**_get_params(vars()))

    @_validate_args
    @_req_call(_dataquery)
    def get_data(self, startdate: str = None, enddate: str = None, name = None,) -> pd.DataFrame: ...


class short_interest(_PrismMarketComponent):
    """
    | Short interest dataitems for equity securities and global data coverage.
    | Default frequency is business daily.

    Parameters
    ----------
    dataitemid : int
        | Unique identifier for the different dataitem. This identifies the type of the value (Revenue, Expense, etc.)

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
        >>> ps.market.short_interest.dataitems(search='short')
           dataitemid                               dataitemname  ...  datamodule                packagename
        0     1100035                Broker Short Interest Value  ...        None  IHS Markit Short Interest
        1     1100055        Short Interest Ratio (Day to Cover)  ...        None  IHS Markit Short Interest
        2     1100056                      Short Interest Tenure  ...        None  IHS Markit Short Interest
        3     1100057                       Short Interest Value  ...        None  IHS Markit Short Interest
        4     1100058          Short Interest as % Of Free Float  ...        None  IHS Markit Short Interest
        5     1100059  Short Interest as % Of Shares Outstanding  ...        None  IHS Markit Short Interest
        6     1100060                                Short Score  ...        None  IHS Markit Short Interest
        7     1100063           Supply Side Short Interest Value  ...        None  IHS Markit Short Interest

        >>> short = ps.market.short_interest(dataitemid=1100057)
        >>> short_df = short.get_data(universe=1, startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
        >>> short_df
                listingid        date  shortinterestvalue   Ticker
        0        20108718  2010-06-11        1.288440e+08  A004430
        1        20108718  2010-06-14        1.288440e+08  A004430
        2        20108718  2010-06-15        1.298000e+08  A004430
        3        20108718  2010-06-16        1.309800e+08  A004430
        4        20108718  2010-06-17        6.660000e+07  A004430
        ...           ...         ...                 ...      ...
        305527  278631846  2015-12-25        7.331920e+10  A028260
        305528  278631846  2015-12-28        7.045744e+10  A028260
        305529  278631846  2015-12-29        7.223796e+10  A028260
        305530  278631846  2015-12-30        6.464626e+10  A028260
        305531  278631846  2015-12-31        6.800626e+10  A028260
    """
    @_validate_args
    def __init__(self, dataitemid: int, currency: _CurrencyTypeWithReportTrade = 'trade', package : str = None):
        super().__init__(**_get_params(vars()))

    @classmethod
    @_validate_args
    def dataitems(cls, search : str = None, package : str = None):
        """
        | Usable data items for the short_interest data component.

        Parameters
        ----------
            search : str, default None
                | Search word for data items name, the search is case-insensitive.
            package : str, default None
                | Search word for package name, the search is case-insensitive.

        Returns
        -------
            pandas.DataFrame
                Data items that belong to short_interest data component.

            Columns:
                - *dataitemid : int*
                - *dataitemname : str*
                - *dataitemdescription : str*
                - *datamodule : str*
                - *datacomponent : str*
                - *packagename : str*

        Examples
        --------
            >>> ps.market.short_interest.dataitems(search='short')
            dataitemid                                  dataitemname  ...  datamodule                packagename
            0     1100035                Broker Short Interest Value  ...        None  IHS Markit Short Interest
            1     1100055        Short Interest Ratio (Day to Cover)  ...        None  IHS Markit Short Interest
            2     1100056                      Short Interest Tenure  ...        None  IHS Markit Short Interest
            3     1100057                       Short Interest Value  ...        None  IHS Markit Short Interest
            4     1100058          Short Interest as % Of Free Float  ...        None  IHS Markit Short Interest
            5     1100059  Short Interest as % Of Shares Outstanding  ...        None  IHS Markit Short Interest
            6     1100060                                Short Score  ...        None  IHS Markit Short Interest
            7     1100063           Supply Side Short Interest Value  ...        None  IHS Markit Short Interest
        """
        return _list_dataitem(
            datacategoryid=cls.categoryid,
            datacomponentid=cls.componentid,
            search=search,
            package=package,
        )


class shares_outstanding(_PrismMarketComponent):
    """
    | The total number of shares of a security that are currently held by all its shareholders and are available for trading on a specific stock exchange.
    | Default frequency is daily.

    Parameters
    ----------
    adjustment : bool, default True
        | Whether to apply split adjustment for pricing data.

    package : str, {'Datastream 2', 'CIQ Market', 'Compustat'}
        | Desired data package in where the pricing data outputs from.

        .. admonition:: Warning
            :class: warning

            If an invalid package is entered without a license, an error will be generated as output.

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
        >>> shares_out = ps.market.shares_outstanding()
        >>> shares_out.get_data("Semiconductor", "2020-01-01", shownid=['Company Name'])
                  listingid        date      shares                                       Company Name
        0           2586491  2020-01-01    39521782                                          AXT, Inc.
        1           2587243  2020-01-01    22740986                                  Aehr Test Systems
        2           2587303  2020-01-01  1138599272                       Advanced Micro Devices, Inc.
        3           2587347  2020-01-01    38308569                   Advanced Energy Industries, Inc.
        4           2589783  2020-01-01   239783075                             Amkor Technology, Inc.
        ...             ...         ...         ...                                                ...
        1168126  1831385562  2023-07-26     7501500                                        SEALSQ Corp
        1168127  1833187092  2023-07-26    12675758                                  GigaVis Co., Ltd.
        1168128  1833609849  2023-07-26  7021800000  Semiconductor Manufacturing Electronics (Shaox...
        1168129  1834641950  2023-07-26   452506348     Smarter Microelectronics (Guangzhou) Co., Ltd.
        1168130  1838168164  2023-07-26    37844925              Integrated Solutions Technology, Inc.
    """
    @_validate_args
    def __init__(self, adjustment: bool = True, package : str = None):
        super().__init__(**_get_params(vars()))


class enterprise_value(_PrismMarketComponent):
    """
    | Represents the total value of a company, taking into account its market capitalization, outstanding debt, cash, and other financial assets.
    | It is used to determine the true cost of acquiring a company and is calculated as market capitalization plus total debt minus cash and cash equivalents.
    | Default frequency is daily.

    Parameters
    ----------
    currency : str, {'trade', 'report', ISO3 currency}, default None
            | Desired currency for the enterprise value data.

            - trade : trading currency for a given listing (i.e for Apple - USD, Tencent - HKD)
            - report : financial reporting currency for a given listing (i.e for Apple - USD, Tencent - CNY)
            - ISO3 currency : desired currency in ISO 4217 format (i.e USD, EUR, JPY, KRW, etc.)
            - None : dividend payment currency

    package : str, {'CIQ Market'}
        | Desired data package in where the pricing data outputs from.

        .. admonition:: Warning
            :class: warning

            If an invalid package is entered without a license, an error will be generated as output.

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
        >>> ent_val = ps.market.enterprise_value(currency='trade')
        >>> ent_val.get_data("Semi", "2020-01-01", shownid=['Company Name'])
                  listingid        date           tev  currency                                       Company Name
        0           2586491  2020-01-01  1.546798e+08       USD                                          AXT, Inc.
        1           2587243  2020-01-01  4.288797e+07       USD                                  Aehr Test Systems
        2           2587303  2020-01-01  5.211816e+10       USD                       Advanced Micro Devices, Inc.
        3           2587347  2020-01-01  2.842980e+09       USD                   Advanced Energy Industries, Inc.
        4           2589783  2020-01-01  3.988825e+09       USD                             Amkor Technology, Inc.
        ...             ...         ...           ...       ...                                                ...
        1167719  1831385562  2023-07-25  1.645610e+08       USD                                        SEALSQ Corp
        1167720  1833187092  2023-07-25           NaN       KRW                                  GigaVis Co., Ltd.
        1167721  1833609849  2023-07-25  5.481000e+10       CNY  Semiconductor Manufacturing Electronics (Shaox...
        1167722  1834641950  2023-07-25  9.114210e+09       CNY     Smarter Microelectronics (Guangzhou) Co., Ltd.
        1167723  1838168164  2023-07-25           NaN       TWD              Integrated Solutions Technology, Inc.
    """
    @_validate_args
    def __init__(self, currency: _CurrencyTypeWithReportTrade = None, package : str = None):
        super().__init__(**_get_params(vars()))


class diluted_market_cap(_PrismMarketComponent):
    """
    | Theoretical total value of a company's outstanding shares, including potential dilution from stock options and other equity-based compensation plans.
    | Default frequency is daily.

    Parameters
    ----------
    dilution : str, {'all', 'partner', 'exercisable'}, default 'all'
            | Options whether to include which potential dilution from stock options and other equity-based compensation plans.

    currency : str, {'trade', 'report', ISO3 currency}, default None
            | Desired currency for the pricing data.

            - trade : trading currency for a given listing (i.e for Apple - USD, Tencent - HKD)
            - report : financial reporting currency for a given listing (i.e for Apple - USD, Tencent - CNY)
            - ISO3 currency : desired currency in ISO 4217 format (i.e USD, EUR, JPY, KRW, etc.)
            - None : dividend payment currency

    package : str, {'CIQ Market'}
        | Desired data package in where the pricing data outputs from.

        .. admonition:: Warning
            :class: warning

            If an invalid package is entered without a license, an error will be generated as output.

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
        >>> immcap = ps.market.diluted_market_cap()
        >>> immcap.get_data("US Primary", "2019-01-01", "2020-12-31", shownid=["ticker"])
                listingid        date  diluted_marketcap  currency   Ticker
        0         2593644  2019-01-01       2.895668e+08       USD     ESTE
        1         9857898  2019-01-01       5.011717e+08       USD     GHL
        2        22472345  2019-01-01       6.720182e+08       USD     TLP
        3        24111616  2019-01-01       5.537839e+08       USD     GLP
        4        28638206  2019-01-01       3.269872e+09       USD     EVR
        ...           ...         ...                ...       ...     ...
        26506   676049212  2020-12-31       4.018368e+10       USD     RKT
        26507   686184361  2020-12-31       2.662519e+09       USD     UTZ
        26508   692043613  2020-12-31       2.293612e+09       USD     MAX
        26509   697654886  2020-12-31       4.433758e+09       USD     RSI
        26510  1771912571  2020-12-31       3.328586e+09       USD  BRBR.WI


    """
    @_validate_args
    def __init__(self, dilution: _DilutionType = 'all', currency: _CurrencyTypeWithReportTrade = None, package : str = None):
        super().__init__(**_get_params(vars()))


class beta(_PrismMarketComponent):
    """
    | The beta calculates the beta value for a given universe, where the index is based on market capitalization weighting.

    Parameters
    ----------
    data_interval : str
            | data_interval is a format for specifying data intervals, represented as XI.
            | It's important to note that prior to any calculations, the data undergoes resampling based on the frequency indicated by the interval type. Subsequently, calculations use all data within the specified interval. For example, with a '6M' data interval for beta calculation, the pricing data is first resampled to a monthly frequency, and then the beta is calculated using all data from a 6-month period.

            X - represents the numerical part of the period. When paired with the interval type 'I', it indicates the duration of data used for each calculation. If 'X' is not specified, it automatically defaults to 1.
            I - denotes the unit of time for the data interval. It can be one of the following options: D (Daily), W (Weekly), M (Monthly), Q (Quarterly), Y (Yearly).

    min_sample : int
            | Sets the minimum number of observations required within the data_interval to generate a value. If the observations for a company at any beta calculation point are fewer than the min_sample, the resulting beta will be None for that period.

    total_return : bool, default True
            | Options whether to use dividend adjusted return when calculating beta against the market index.

    reference_currency : str, {ISO3 currency}, default USD
            | Desired reference currency for the calculating market-capitalization based index for the universe.

            ISO3 currency : desired currency in ISO 4217 format (i.e USD, EUR, JPY, KRW, etc.)

    package : str, {'Datastream 2', 'CIQ Market'}
        | Desired data package in where the pricing data outputs from.

        .. admonition:: Warning
            :class: warning

            If an invalid package is entered without a license, an error will be generated as output.

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
        >>> beta = ps.market.beta(data_interval='365D', min_sample=240, total_return=True, reference_currency='USD')
        >>> beta.get_data("Semi", "2020-01-01", shownid=['Company Name'])
                 listingid        date      beta   Ticker
        0          2585895  2019-01-01  1.114764      AIR
        1          2586016  2019-01-01  1.070112      ABM
        2          2586086  2019-01-01  0.814956      AFL
        3          2586108  2019-01-01  0.975493     AGCO
        4          2586130  2019-01-01  0.673107      AES
        ...            ...         ...       ...      ...
        959063  1771912571  2020-12-31  0.664183  BRBR.WI
        959064  1774529164  2020-12-31  1.464179     DINO
        959065  1823326675  2020-12-31  1.441870    CR.WI
        959066  1836807464  2020-12-31  1.547879      CLB
        959067  1864533284  2020-12-31  1.266058      LAZ
    """
    @_validate_args
    def __init__(self, data_interval: str, min_sample: int, total_return: bool = True, reference_currency: _CurrencyTypeWithReportTrade = "USD", package : str = None):
        super().__init__(**_get_params(vars()))


@_validate_args
def dataitems(search : str = None, package : str = None):
    """
    | Usable dataitems for the market data categories.

    Parameters
    ----------
        search : str, default None
            | Search word for Data Items name, the search is case-insensitive.
        package : str, default None
            | Search word for package name, the search is case-insensitive.

    Returns
    -------
        pandas.DataFrame
            Data items that belong to market data categories.

        Columns:
            - *dataitemid : int*
            - *dataitemname : str*
            - *dataitemdescription : str*
            - *datamodule : str*
            - *datacomponent : str*
            - *packagename : str*

    Examples
    --------
        >>> ps.market.dataitems(search='short')
            dataitemid                               dataitemname  ...   datacomponent                packagename
        0     1100035                Broker Short Interest Value  ...  Short Interest  IHS Markit Short Interest
        1     1100055        Short Interest Ratio (Day to Cover)  ...  Short Interest  IHS Markit Short Interest
        2     1100056                      Short Interest Tenure  ...  Short Interest  IHS Markit Short Interest
        3     1100057                       Short Interest Value  ...  Short Interest  IHS Markit Short Interest
        4     1100058          Short Interest as % Of Free Float  ...  Short Interest  IHS Markit Short Interest
        5     1100059  Short Interest as % Of Shares Outstanding  ...  Short Interest  IHS Markit Short Interest
        6     1100060                                Short Score  ...  Short Interest  IHS Markit Short Interest
        7     1100063           Supply Side Short Interest Value  ...  Short Interest  IHS Markit Short Interest
    """
    return _list_dataitem(
        datacategory=_PrismMarketComponent.categoryid,
        datacomponent=None,
        search=search,
        package=package,
    )