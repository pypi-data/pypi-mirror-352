from prismstudio._utils.exceptions import PrismValueError
from ..._common.const import (
    AggregationType as _AggregationType,
    EstimatePeriodType as _PeriodType,
    EstimatePeriodTypeNTM as _NTMPeriodType,
    CurrencyTypeWithReportTrade as _CurrencyTypeWithReportTrade
)
from .._req_builder import _list_dataitem
from ..._prismcomponent.prismcomponent import _PrismComponent, _PrismDataComponent
from ..._utils import _validate_args, _get_params


__all__ = [
    'actual',
    'consensus',
    'guidance',
    'recommendation',
    'revision',
    'surprise',
    'dataitems',
]


_data_category = __name__.split(".")[-1]


class _PrismEstimateComponent(_PrismDataComponent, _PrismComponent):
    _component_category_repr = _data_category

    def __init__(self, **kwargs):
        if (kwargs.get('period_type') == 'NTM') & (kwargs.get('period_forward') != 0):
            raise PrismValueError("NTM period type only takes 0 period_forward.")
        super().__init__(**kwargs)

    @classmethod
    def _dataitems(cls, search: str = None, package: str = None):
        return _list_dataitem(
            datacategoryid=cls.categoryid,
            datacomponentid=cls.componentid,
            search=search,
            package=package,
        )


class actual(_PrismEstimateComponent):
    """
    | Actual financial statement result that can be compared to the consensus estimate data for a data item.
    | Default frequency is quarterly.

    Parameters
    ----------
        dataitemid : int
            | Unique identifier for the different data item. This identifies the type of the value (Revenue, Expense, etc.)

        period_type : str, {'A', 'Annual', 'SA', 'Semi-Annual', 'Quarterly', 'Q'}
            | Actual Period in which the financial statement results are estimated.
            | An actual Period can be of one of the following Period Types:

            - Annual period (A)
            - Semi-Annual (SA)
            - Quarterly period (Q)

        currency : str, {'report', 'trade', ISO3 currency}, default 'report'
            | Desired currency for the pricing data.

            - report : financial reporting currency for a given listing (i.e for Apple - USD, Tencent - CNY)
            - trade : trading currency for a given listing (i.e for Apple - USD, Tencent - HKD)
            - ISO3 currency : desired currency in ISO 4217 format (i.e USD, EUR, JPY, KRW, etc.)

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
        >>> di = ps.estimate.actual.dataitems('revenue')
        >>> di[['dataitemid', 'dataitemname']]
           dataitemid      dataitemname
        0      200032  Revenue - Actual

        >>> rev = ps.estimate.actual(dataitemid=200032, period_type='Q')
        >>> rev_df = rev.get_data(universe='Korea Primary', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
        >>> rev_df
              listingid                 date  period_enddate  calendar_period  fiscal_period  currency  Revenue - Actual   Ticker
        0      52512514  2010-01-11 23:44:17      2009-12-31           2009Q4         2009Q4       KRW      4.400570e+11  A108070
        1      31779183  2010-01-13 05:18:18      2009-12-31           2009Q4         2009Q4       KRW      1.585090e+11  A003670
        2      20215603  2010-01-20 03:38:25      2009-12-31           2009Q4         2009Q4       KRW      7.096620e+11  A033780
        3      20124021  2010-01-20 08:28:00      2009-12-31           2009Q4         2009Q4       KRW      5.925000e+12  A034220
        4      25976486  2010-01-21 04:33:15      2009-12-31           2009Q4         2010Q3       KRW      7.624430e+11  A000060
         ...        ...                  ...             ...              ...            ...       ...               ...      ...
        8917  280450682  2015-11-27 09:09:02      2015-09-30           2015Q3         2015Q3       KRW      7.391120e+09  A189860
        8918  253087680  2015-11-27 09:09:08      2015-09-30           2015Q3         2015Q3       KRW      1.755389e+10  A049080
        8919   31780603  2015-11-27 17:48:00      2015-09-30           2015Q3         2015Q3       KRW      2.364416e+11  A031440
        8920   31780603  2015-11-27 17:48:00      2015-09-30           2015Q3         2015Q3       KRW      2.364416e+11  A031440
        8921   20159041  2015-12-28 15:10:00      2015-09-30           2015Q3         2015Q4       KRW      3.279816e+10  A054050
    """
    @_validate_args
    def __init__(
        self,
        dataitemid: int,
        period_type: _PeriodType,
        currency: _CurrencyTypeWithReportTrade = "report",
    ):
        if period_type in ["NTM", None]:
            raise PrismValueError(
                f"Actual cannot take {period_type} as period_type.",
                valid_list=_PeriodType,
                invalids=["NTM", "None"],
            )
        super().__init__(**_get_params(vars()))

    @classmethod
    @_validate_args
    def dataitems(cls, search: str = None, package: str = None):
        """
        Usable dataitems for the actual datacomponent.

        Parameters
        ----------
            search : str, default None
                | Search word for dataitems name, the search is case-insensitive.

            package : str, default None
                | Search word for package name, the search is case-insensitive.

        Returns
        -------
            pandas.DataFrame
                Data items that belong to cash flow statement data component.

            Columns:
                - *datamodule*
                - *datacomponent*
                - *dataitemid*
                - *datadescription*

        Examples
        --------
            >>> di = ps.estimate.actual.dataitems('net income')
            >>> di[['dataitemid', 'dataitemname']]
            dataitemid                                       dataitemname
            0      200027  Net Income (Excl. Extraordinary Items & Good W...
            1      200028                         Net Income (GAAP) - Actual
            2      200029                     Net Income Normalized - Actual
        """
        return cls._dataitems(search=search, package=package)


class consensus(_PrismEstimateComponent):
    """
    | Consensus estimate data item.
    | Default frequency is aperiodic.


    Parameters
    ----------
        dataitemid : int
            | Unique identifier for the different data item. This identifies the type of the estimate value (Revenue, Expense, etc.)

        period_type : str, {'A', 'Annual', 'SA', 'Semi-Annual', 'Quarterly', 'Q', 'Q-SA', 'NTM', None}
            | Estimate Period in which the financial statement results are estimated.
            | An Estimate Period can be of one of the following Period Types:

            - Annual period (A)
            - Semi-Annual (SA)
            - Quarterly period (Q)
            - Quarterly and Semi-Annual period (Q-SA) in quarterly standard
            - Next twelve months (NTM)
            - Non-Periodic (None)

        period_forward : int
            | Determines how far out estimate to fetch.
            | For example, inputting 0 will fetch estimate data for the current period, 1 will fetch estimate for the next period.

        currency : str, {'report', 'trade', ISO3 currency}, default 'report'
            | Desired currency for the pricing data.

            - report : financial reporting currency for a given listing (i.e for Apple - USD, Tencent - CNY)
            - trade : trading currency for a given listing (i.e for Apple - USD, Tencent - HKD)
            - ISO3 currency : desired currency in ISO 4217 format (i.e USD, EUR, JPY, KRW, etc.)


    Returns
    -------
        prismstudio._PrismComponent


    Examples
    --------
        >>> di = ps.estimate.consensus.dataitems('eps')
        >>> di[['dataitemid', 'dataitemname']]
            dataitemid                                       dataitemname
        0       200047               Cash EPS - Consensus, # of Estimates
        1       200048                         Cash EPS - Consensus, High
        2       200049                          Cash EPS - Consensus, Low
        3       200050                         Cash EPS - Consensus, Mean
        4       200051                       Cash EPS - Consensus, Median
        5       200052           Cash EPS - Consensus, Standard Deviation
        6       200119  EPS (Excl. Extraordinary Items & Good Will) - ...
        7       200120  EPS (Excl. Extraordinary Items & Good Will) - ...
        8       200121  EPS (Excl. Extraordinary Items & Good Will) - ...
        9       200122  EPS (Excl. Extraordinary Items & Good Will) - ...
        10      200123  EPS (Excl. Extraordinary Items & Good Will) - ...
        11      200124  EPS (Excl. Extraordinary Items & Good Will) - ...
        12      200125             EPS (GAAP) - Consensus, # of Estimates
        13      200126                       EPS (GAAP) - Consensus, High
        14      200127                        EPS (GAAP) - Consensus, Low
        15      200128                       EPS (GAAP) - Consensus, Mean
        16      200129                     EPS (GAAP) - Consensus, Median
        17      200130         EPS (GAAP) - Consensus, Standard Deviation
        18      200131  EPS Long-Term Growth (%) - Consensus, # of Est...
        19      200132         EPS Long-Term Growth (%) - Consensus, High
        20      200133          EPS Long-Term Growth (%) - Consensus, Low
        21      200134         EPS Long-Term Growth (%) - Consensus, Mean
        22      200135       EPS Long-Term Growth (%) - Consensus, Median
        23      200136  EPS Long-Term Growth (%) - Consensus, Standard...
        24      200137         EPS Normalized - Consensus, # of Estimates
        25      200138                   EPS Normalized - Consensus, High
        26      200139                    EPS Normalized - Consensus, Low
        27      200140                   EPS Normalized - Consensus, Mean
        28      200141                 EPS Normalized - Consensus, Median
        29      200142     EPS Normalized - Consensus, Standard Deviation

        >>> eps = ps.estimate.consensus(dataitemid=200140, period_type='Q')
        >>> eps_df = eps.get_data(universe='Korea Primary', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
        >>> eps_df
              listingid                 date  period_enddate  calendar_period  fiscal_period  currency  EPS Normalized - Consensus, Mean   Ticker
        0      20124021  2010-01-03 20:10:10      2009-12-31           2009Q4         2009Q4       KRW                         928.94329  A034220
        1      20218927  2010-01-04 01:50:00      2009-12-31           2009Q4         2009Q4       KRW                        1185.00000  A000660
        2      20218927  2010-01-04 05:25:00      2009-12-31           2009Q4         2009Q4       KRW                        1180.00000  A000660
        3      31780433  2010-01-04 06:28:00      2009-12-31           2009Q4         2009Q4       KRW                         352.44685  A033640
        4      20124021  2010-01-04 10:15:17      2009-12-31           2009Q4         2009Q4       KRW                         828.36231  A034220
          ...       ...                  ...             ...              ...            ...       ...                               ...      ...
        10029  20188615  2015-12-23 08:31:22      2015-12-31           2015Q4         2015Q4       KRW                        1702.45563  A000270
        10030  20179023  2015-12-24 10:10:00      2015-12-31           2015Q4         2015Q4       KRW                        3199.17559  A001800
        10031  20160778  2015-12-28 11:26:56      2015-12-31           2015Q4         2015Q4       KRW                         380.64061  A002350
        10032  31779391  2015-12-29 01:13:03      2015-12-31           2015Q4         2015Q4       KRW                        9342.00000  A036490
        10033  31780654  2015-12-29 18:18:47      2015-12-31           2015Q4         2015Q4       KRW                         221.71921  A032640
    """
    @_validate_args
    def __init__(
        self,
        dataitemid: int,
        period_type: _NTMPeriodType = None,
        period_forward: int = 0,
        currency: _CurrencyTypeWithReportTrade = "report",
    ):
        super().__init__(**_get_params(vars()))

    @classmethod
    @_validate_args
    def dataitems(cls, search: str = None, package: str = None):
        """
        Usable data items for the estimate consensus data component.

        Parameters
        ----------
            search : str, default None
                | Search word for dataitems name, the search is case-insensitive.

            package : str, default None
                | Search word for package name, the search is case-insensitive.

        Returns
        -------
            pandas.DataFrame
                Data items that belong to cash flow statement data component.

            Columns:
                - *datamodule*
                - *datacomponent*
                - *dataitemid*
                - *datadescription*


        Examples
        --------
            >>> di = ps.estimate.consensus.dataitems('net income')
            >>> di[['dataitemid', 'dataitemname']]
                dataitemid                                       dataitemname
            0       200203  Net Income (Excl. Extraordinary Items & Good W...
            1       200204  Net Income (Excl. Extraordinary Items & Good W...
            2       200205  Net Income (Excl. Extraordinary Items & Good W...
            3       200206  Net Income (Excl. Extraordinary Items & Good W...
            4       200207  Net Income (Excl. Extraordinary Items & Good W...
            5       200208  Net Income (Excl. Extraordinary Items & Good W...
            6       200209      Net Income (GAAP) - Consensus, # of Estimates
            7       200210                Net Income (GAAP) - Consensus, High
            8       200211                 Net Income (GAAP) - Consensus, Low
            9       200212                Net Income (GAAP) - Consensus, Mean
            10      200213              Net Income (GAAP) - Consensus, Median
            11      200214  Net Income (GAAP) - Consensus, Standard Deviation
            12      200215  Net Income Normalized - Consensus, # of Estimates
            13      200216            Net Income Normalized - Consensus, High
            14      200217             Net Income Normalized - Consensus, Low
            15      200218            Net Income Normalized - Consensus, Mean
            16      200219          Net Income Normalized - Consensus, Median
            17      200220  Net Income Normalized - Consensus, Standard De...
        """
        return cls._dataitems(search=search, package=package)


class industry(_PrismEstimateComponent):
    """
    | Consensus industry data item.
    | Default frequency is aperiodic.


    Parameters
    ----------
        dataitemid : int
            | Unique identifier for the different data item. This identifies the type of the estimate value (Revenue, Expense, etc.)

        period_type : str, {'A', 'Annual', 'SA', 'Semi-Annual', 'Quarterly', 'Q', 'Q-SA', 'NTM', None}
            | Estimate Period in which the financial statement results are estimated.
            | An Estimate Period can be of one of the following Period Types:

            - Annual period (A)
            - Semi-Annual (SA)
            - Quarterly period (Q)
            - Quarterly and Semi-Annual period (Q-SA) in quarterly standard
            - Next twelve months (NTM)
            - Non-Periodic (None)

        period_forward : int
            | Determines how far out estimate to fetch.
            | For example, inputting 0 will fetch estimate data for the current period, 1 will fetch estimate for the next period.

        currency : str, {'report', 'trade', ISO3 currency}, default 'report'
            | Desired currency for the pricing data.

            - report : financial reporting currency for a given listing (i.e for Apple - USD, Tencent - CNY)
            - trade : trading currency for a given listing (i.e for Apple - USD, Tencent - HKD)
            - ISO3 currency : desired currency in ISO 4217 format (i.e USD, EUR, JPY, KRW, etc.)


    Returns
    -------
        prism._PrismComponent


    Examples
    --------
        >>> di = ps.estimate.consensus.dataitems('eps')
        >>> di[['dataitemid', 'dataitemname']]
            dataitemid	dataitemname
        0       200798	Funds From Operations / Share (REIT) - Guidanc...
        1       200799	Funds From Operations / Share (REIT) - Guidanc...
        2       200800	Funds From Operations / Share (REIT) - Guidanc...
        3       200801	Funds From Operations / Share (REIT) - Consens...
        4       200802	Funds From Operations / Share (REIT) - Revisio...
        ...        ...                                                ...
        4167	500447                                    Unusual Expense
        4168	500449                            Other Asset/Liabilities
        4169	500450                         Changes in Working Capital
        4170	500451                             Exceptional Provisions
        4171	500452                                 Extraordinary Item

        >>> al = ps.estimate.industry(dataitemid=201316, period_type="Q")
        >>> al_df = al.get_data(universe=1, startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
        >>> al_df
             listingid                 date  period_enddate  calendar_period  fiscal_period  currency  Average Loans - Actual  Ticker
        0      2622876  2010-01-15 12:07:37      2009-12-31           2009Q4         2009Q4       USD            6.424060e+11     JPM
        1      9736131  2010-01-19 12:46:10      2009-12-31           2009Q4         2009Q4       USD            1.873700e+10     FHN
        2      2592914  2010-01-20 12:14:09      2009-12-31           2009Q4         2009Q4       USD            9.059130e+11     BAC
        3      2663720  2010-01-20 13:01:02      2009-12-31           2009Q4         2009Q4       USD            8.322940e+11     WFC
        4      2627536  2010-01-20 13:43:22      2009-12-31           2009Q4         2009Q4       USD            5.208700e+10     MTB
        ...        ...                  ...             ...              ...            ...       ...                     ...     ...
        689    2604167  2015-10-28 13:29:07      2015-09-30           2015Q3         2015Q3       USD            1.136200e+10     CFR
        690  145334731  2015-10-28 21:19:29      2015-09-30           2015Q3         2015Q3       USD            6.369849e+09    CUBI
        691    2591283  2015-10-28 23:30:00      2015-09-30           2015Q3         2015Q3       USD            1.139485e+10      AF
        692    4094898  2015-10-29 12:00:00      2015-09-30           2015Q3         2015Q3       USD            3.070384e+09     CPF
        693    2996535  2015-10-29 13:03:02      2015-09-30           2015Q3         2015Q3       USD            5.271293e+09    BANC
    """
    @_validate_args
    def __init__(
        self,
        dataitemid: int,
        period_type: _NTMPeriodType = None,
        period_forward: int = 0,
        currency: _CurrencyTypeWithReportTrade = "report",
        aggregation: _AggregationType = '1 week',
    ):
        super().__init__(**_get_params(vars()))

    @classmethod
    @_validate_args
    def dataitems(cls, search: str = None, package: str = None):
        """
        Usable data items for the estimate industry data component.

        Parameters
        ----------
            search : str, default None
                | Search word for dataitems name, the search is case-insensitive.

            package : str, default None
                | Search word for package name, the search is case-insensitive.

        Returns
        -------
            pandas.DataFrame
                Data items that belong to cash flow statement data component.

            Columns:
                - *datamodule*
                - *datacomponent*
                - *dataitemid*
                - *datadescription*

        Examples
        --------
        """
        return cls._dataitems(search=search, package=package)


class segment(_PrismEstimateComponent):
    """
    | Consensus segment data item.
    | Default frequency is aperiodic.


    Parameters
    ----------
        dataitemid : int
            | Unique identifier for the different data item. This identifies the type of the estimate value (Revenue, Expense, etc.)

        period_type : str, {'A', 'Annual', 'SA', 'Semi-Annual', 'Quarterly', 'Q', 'Q-SA', 'NTM', None}
            | Estimate Period in which the financial statement results are estimated.
            | An Estimate Period can be of one of the following Period Types:

            - Annual period (A)
            - Semi-Annual (SA)
            - Quarterly period (Q)
            - Quarterly and Semi-Annual period (Q-SA) in quarterly standard
            - Next twelve months (NTM)
            - Non-Periodic (None)

        period_forward : int
            | Determines how far out estimate to fetch.
            | For example, inputting 0 will fetch estimate data for the current period, 1 will fetch estimate for the next period.

        currency : str, {'report', 'trade', ISO3 currency}, default 'report'
            | Desired currency for the pricing data.

            - report : financial reporting currency for a given listing (i.e for Apple - USD, Tencent - CNY)
            - trade : trading currency for a given listing (i.e for Apple - USD, Tencent - HKD)
            - ISO3 currency : desired currency in ISO 4217 format (i.e USD, EUR, JPY, KRW, etc.)


    Returns
    -------
        prism._PrismComponent


    Examples
    --------
        >>> di = ps.estimate.segment.dataitems('eps')
        >>> di[['dataitemid', 'dataitemname']]
            dataitemid                                       dataitemname
        0       321098    Earnings Before Tax - Consensus, # of Estimates
        1       321099  Earnings Before Tax - Consensus, Standard Devi...
        2       321100            Earnings Before Tax - Consensus, Median
        3       321101              Earnings Before Tax - Consensus, Mean
        4       321102               Earnings Before Tax - Consensus, Low
        ...        ...                                                ...
        238     321336                       Subscribers - Consensus, Low
        239     321337                      Subscribers - Consensus, High
        240     321338                               Subscribers - Actual
        241     321339                 Subscribers - Surprise, Difference
        242     321340                    Subscribers - Surprise, Percent

        >>> sales = ps.estimate.segment(dataitemid=321254, period_type="Q")
        >>> sales_df = sales.get_data(universe='US Primary', startdate='2020-01-01', enddate='2024-06-23', shownid=['ticker'])
        >>> sales_df
                listingid                     date                                    segment  period_enddate  calendar_period  fiscal_period         value  Ticker
        0         2649360  2020-01-01 17:20:00.000                             Ocean Services      2019-12-31           2019Q4         2019Q4  1.058500e+08     CKH
        1       105602778  2020-01-01 19:21:00.000                      Theme Park Admissions      2019-12-31           2019Q4         2019Q4  1.593113e+08     SIX
        2       105602778  2020-01-01 19:21:00.000     Theme Park Food, Merchandise And Other      2019-12-31           2019Q4         2019Q4  1.060476e+08     SIX
        3       105602778  2020-01-01 19:21:00.000  Sponsorship, Licensing And Accommodations      2019-12-31           2019Q4         2019Q4  2.109400e+07     SIX
        4        83018482  2020-01-01 21:08:05.310                           Auction Services      2019-12-31           2019Q4         2019Q4  8.870000e+07     KAR
        ...           ...                      ...                                        ...             ...              ...            ...           ...     ...
        140988  711956483  2024-06-21 16:26:00.000                                    Service      2024-06-30           2024Q2         2024Q2  2.021500e+07    PWSC
        140989  711956483  2024-06-21 16:26:00.000                          License and other      2024-06-30           2024Q2         2024Q2  3.297500e+06    PWSC
        140990   29618826  2024-06-23 18:42:00.000                             Health & Civil      2024-06-30           2024Q2         2024Q2  1.194333e+09    LDOS
        140991   29618826  2024-06-23 18:42:00.000                 Commercial & International      2024-06-30           2024Q2         2024Q2  5.430000e+08    LDOS
        140992   29618826  2024-06-23 18:42:00.000                            Defense Systems      2024-06-30           2024Q2         2024Q2  4.646667e+08    LDOS
    """
    @_validate_args
    def __init__(
        self,
        dataitemid: int,
        period_type: _NTMPeriodType = None,
        period_forward: int = 0,
        currency: _CurrencyTypeWithReportTrade = "report",
    ):
        super().__init__(**_get_params(vars()))

    @classmethod
    @_validate_args
    def dataitems(cls, search: str = None, package: str = None):
        """
        Usable data items for the estimate segment data component.

        Parameters
        ----------
            search : str, default None
                | Search word for dataitems name, the search is case-insensitive.

            package : str, default None
                | Search word for package name, the search is case-insensitive.

        Returns
        -------
            pandas.DataFrame
                Data items that belong to cash flow statement data component.

            Columns:
                - *datamodule*
                - *datacomponent*
                - *dataitemid*
                - *datadescription*


        Examples
        --------
        """
        return cls._dataitems(search=search, package=package)


class recommendation(_PrismEstimateComponent):
    """
    | Recommnedation Data for a data item.
    | Default frequency is quarterly.

    Parameters
    ----------
        dataitemid : int
            | Unique identifier for the different data item. This identifies the type of the value (Score, Buy, etc.)

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
        >>> df = ps.estimate.recommendation.dataitems('Score')
        >>> df[['dataitemid', 'dataitemname']]
           dataitemid                     dataitemname
        0      200631           Recommendation - Score
        1      200637  Industry Recommendation - Score
        2      601998           Recommendation - Score
        >>> rec = ps.estimate.recommendation(dataitemid=200631)
        >>> rec.get_data("US Primary", "2022-01-01", shownid=['companyname'])
                listingid                 date  Recommendation - Score  Ticker
        0         2594352  2020-01-01 00:00:19                 2.70000     BIG
        1         2586910  2020-01-01 03:32:25                 2.54545     AYI
        2         2587927  2020-01-01 03:32:25                 1.66667    MATX
        3         2611328  2020-01-01 03:32:25                 2.28571     FDX
        4         2623613  2020-01-01 03:32:25                 2.00000     KSU
        ...           ...                  ...                     ...     ...
        719154   10779524  2023-12-30 19:18:52                 2.09091     DPZ
        719155  270906752  2023-12-30 19:22:22                 1.68750    HUBS
        719156  279843842  2023-12-30 19:26:13                 1.97059     QSR
        719157  117075824  2023-12-30 19:28:11                 2.00000     FLT
        719158  606806721  2023-12-30 19:30:09                 2.09091      PD
    """
    @_validate_args
    def __init__(
        self,
        dataitemid: int,
    ):
        super().__init__(**_get_params(vars()))

    @classmethod
    @_validate_args
    def dataitems(cls, search: str = None, package: str = None):
        """
        Usable data items for the recommendation data component.

        Parameters
        ----------
            search : str, default None
                | Search word for dataitems name, the search is case-insensitive.

            package : str, default None
                | Search word for package name, the search is case-insensitive.

        Returns
        -------
            pandas.DataFrame
                Data items that belong to cash flow statement data component.

            Columns:
                - *datamodule*
                - *datacomponent*
                - *dataitemid*
                - *datadescription*

        Examples
        --------
            >>> di = ps.estimate.recommendation.dataitems()
            >>> di[['dataitemid', 'dataitemname']]
            dataitemid                                         dataitemname
            0      200625    Recommendation - # of Analysts Buy Recommendation
            1      200626    Recommendation - # of Analysts Hold Recommenda...
            2      200627    Recommendation - # of Analysts No Opinion Reco...
            3      200628    Recommendation - # of Analysts Outperform Reco...
            4      200629    Recommendation - # of Analysts Sell Recommenda...
            5      200630    Recommendation - # of Analysts Underperform Re...
            6      200631    Recommendation - Score
            7      200632    Industry Recommendation - # of Analysts Buy Re...
            8      200633    Industry Recommendation - # of Analysts Hold R...
            9      200634    Industry Recommendation - # of Analysts Outper...
            10     200635    Industry Recommendation - # of Analysts Sell R...
            11     200636    Industry Recommendation - # of Analysts Underp...
            12     200637    Industry Recommendation - Score
            13     601991    Recommendation - # of Analysts Buy Recommendation
            14     601993    Recommendation - # of Analysts Hold Recommenda...
            15     601995    Recommendation - # of Analysts Sell Recommenda...
            16     601996    Recommendation - # of Analysts No Opinion Reco...
            17     601997    Recommendation - # of Analysts Total Recommend...
            18     601998    Recommendation - Score
            19     602197    Recommendation - # of Analysts Overweight Reco...
            20     602198    Recommendation - # of Analysts Underweight Rec...
        """
        return cls._dataitems(search=search, package=package)


class guidance(_PrismEstimateComponent):
    """
    | Company guidance data for a data item.
    | Default frequency is aperiodic.

    Parameters
    ----------
        dataitemid : int
            | Unique identifier for the different data item. This identifies the type of the value (Revenue, Expense, etc.)

        period_type : str, {'A', 'Annual', 'SA', 'Semi-Annual', 'Quarterly', 'Q', 'Q-SA', 'NTM', None}
            | Estimate Period in which the financial statement results are estimated.
            | An Estimate Period can be of one of the following Period Types:

            - Annual period (A)
            - Semi-Annual (SA)
            - Quarterly period (Q)
            - Quarterly and Semi-Annual period (Q-SA) in quarterly standard
            - Next twelve months (NTM)
            - Non-Periodic (None)

        period_forward : int
            | Determines how far out estimate to fetch.
            | For example, inputting 0 will fetch estimate data for the current period, 1 will fetch estimate for the next period.

        currency : str, {'report', 'trade', ISO3 currency}, default 'report'
            | Desired currency for the pricing data.

            - report : financial reporting currency for a given listing (i.e for Apple - USD, Tencent - CNY)
            - trade : trading currency for a given listing (i.e for Apple - USD, Tencent - HKD)
            - ISO3 currency : desired currency in ISO 4217 format (i.e USD, EUR, JPY, KRW, etc.)

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
        >>> di = ps.estimate.guidance.dataitems('eps')
        >>> di[['dataitemid', 'dataitemname']]
            dataitemid                                       dataitemname
        0       200299                          Cash EPS - Guidance, High
        1       200300                           Cash EPS - Guidance, Low
        2       200301                           Cash EPS - Guidance, Mid
        3       200335  EPS (Excl. Extraordinary Items & Good Will) - ...
        4       200336  EPS (Excl. Extraordinary Items & Good Will) - ...
        5       200337  EPS (Excl. Extraordinary Items & Good Will) - ...
        6       200338                        EPS (GAAP) - Guidance, High
        7       200339                         EPS (GAAP) - Guidance, Low
        8       200340                         EPS (GAAP) - Guidance, Mid
        9       200341                    EPS Normalized - Guidance, High
        10      200342                     EPS Normalized - Guidance, Low
        11      200343                     EPS Normalized - Guidance, Mid

        >>> eps = ps.estimate.guidance(dataitemid=200293, period_type='Q')
        >>> eps_df = eps.get_data(universe='US Primary', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
        >>> eps_df
            listingid                 date  period_enddate  calendar_period  fiscal_period  currency  Book Value / Share - Guidance, High  Ticker
        0    34204761  2010-01-11 21:10:00      2009-12-31           2009Q4         2009Q4       USD                         1.531250e+07     KFN
        1     2658956  2011-09-19 13:15:32      2011-09-30           2011Q3         2011Q3       USD                         7.000100e+01     TRH
        2     2629202  2012-10-18 20:06:00      2012-09-30           2012Q3         2012Q3       USD                         1.147000e+01     MIG
    """
    @_validate_args
    def __init__(
        self,
        dataitemid: int,
        period_type: _NTMPeriodType = None,
        period_forward: int = 0,
        currency: _CurrencyTypeWithReportTrade = "report",
    ):
        super().__init__(**_get_params(vars()))

    @classmethod
    @_validate_args
    def dataitems(cls, search: str = None, package: str = None):
        """
        Usable data items for the guidance data component.


        Parameters
        ----------
            search : str, default None
                | Search word for dataitems name, the search is case-insensitive.

            package : str, default None
                | Search word for package name, the search is case-insensitive.


        Returns
        -------
            pandas.DataFrame
                Data items that belong to cash flow statement data component.

            Columns:
                - *datamodule*
                - *datacomponent*
                - *dataitemid*
                - *datadescription*

        Examples
        --------
            >>> di = ps.estimate.guidance.dataitems('net income')
            >>> di[['dataitemid', 'dataitemname']]
            dataitemid                                       dataitemname
            0      200368  Net Income (Excl. Extraordinary Items & Good W...
            1      200369  Net Income (Excl. Extraordinary Items & Good W...
            2      200370  Net Income (Excl. Extraordinary Items & Good W...
            3      200371                 Net Income (GAAP) - Guidance, High
            4      200372                  Net Income (GAAP) - Guidance, Low
            5      200373                  Net Income (GAAP) - Guidance, Mid
            6      200374             Net Income Normalized - Guidance, High
            7      200375              Net Income Normalized - Guidance, Low
            8      200376              Net Income Normalized - Guidance, Mid
        """
        return cls._dataitems(search=search, package=package)


class revision(_PrismEstimateComponent):
    """
    | Revision in consensus estimate a data item.
    | Default frequency is aperiodic.

    Parameters
    ----------
        dataitemid : int
            | Unique identifier for the different data item. This identifies the type of the value (Revenue, Expense, etc.)

        period_type : str, {'A', 'Annual', 'SA', 'Semi-Annual', 'Quarterly', 'Q',  None}
            | Estimate Period in which the financial statement results are estimated.
            | An Estimate Period can be of one of the following Period Types:

            - Annual period (A)
            - Quarterly period (Q)
            - Semi-Annual (SA)
            - Non-Periodic (None)

        period_forward : int
            | Determines how far out estimate to fetch.
            | For example, inputting 0 will fetch estimate data for the current period, 1 will fetch estimate for the next period.

        aggregation : str, {'1 day', '1 week', '1 month', '2 month', '3 month', '3 month latest'}, default '1 day'
            | Aggregation time periods covered in the revisions calculations.

            .. admonition:: Warning
                :class: warning

                | If the input is **'1 week'** the resulting revision Data Component will contain data values that are sum of revision within 1 week of the data dates.
                |
                | If the input is  **'3 month latest'**, it will only account for latest revision of the same analyst. Therefore, if a same analyst revises his/her estimate more than one time within the 3 month period, only one will be counted towards calculating the revision number

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
        >>> di = ps.estimate.revision.dataitems('eps')
        >>> di[['dataitemid', 'dataitemname']]
            dataitemid                                       dataitemname
        0       200408                 Cash EPS - Revision, # of Analysts
        1       200409                          Cash EPS - Revision, Down
        2       200410                     Cash EPS - Revision, No Change
        3       200411      Cash EPS - Revision, Unfiltered # of Analysts
        4       200412               Cash EPS - Revision, Unfiltered Down
        5       200413          Cash EPS - Revision, Unfiltered No Change
        6       200414                 Cash EPS - Revision, Unfiltered Up
        7       200415                            Cash EPS - Revision, Up
        8       200472  EPS (Excl. Extraordinary Items & Good Will) - ...
        9       200473  EPS (Excl. Extraordinary Items & Good Will) - ...
        10      200474  EPS (Excl. Extraordinary Items & Good Will) - ...
        11      200475  EPS (Excl. Extraordinary Items & Good Will) - ...
        12      200476  EPS (Excl. Extraordinary Items & Good Will) - ...
        13      200477  EPS (Excl. Extraordinary Items & Good Will) - ...
        14      200478  EPS (Excl. Extraordinary Items & Good Will) - ...
        15      200479  EPS (Excl. Extraordinary Items & Good Will) - ...
        16      200480               EPS (GAAP) - Revision, # of Analysts
        17      200481                        EPS (GAAP) - Revision, Down
        18      200482                   EPS (GAAP) - Revision, No Change
        19      200483    EPS (GAAP) - Revision, Unfiltered # of Analysts
        20      200484             EPS (GAAP) - Revision, Unfiltered Down
        21      200485        EPS (GAAP) - Revision, Unfiltered No Change
        22      200486               EPS (GAAP) - Revision, Unfiltered Up
        23      200487                          EPS (GAAP) - Revision, Up
        24      200488           EPS Normalized - Revision, # of Analysts
        25      200489                    EPS Normalized - Revision, Down
        26      200490               EPS Normalized - Revision, No Change
        27      200491  EPS Normalized - Revision, Unfiltered # of Ana...
        28      200492         EPS Normalized - Revision, Unfiltered Down
        29      200493    EPS Normalized - Revision, Unfiltered No Change
        30      200494           EPS Normalized - Revision, Unfiltered Up
        31      200495                      EPS Normalized - Revision, Up

        >>> eps = ps.estimate.revision(dataitemid=200569, period_type='Q')
        >>> eps_df = eps.get_data(universe='US Primary', startdate='2020-01-01', enddate='2023-12-31', shownid=['ticker'])
        >>> eps_df
        listingid	date	period_enddate	calendar_period	fiscal_period	Revenue - Revision, Down	Ticker
        0	2586533	2020-01-01	2019-12-31	2019Q4	2019Q4	1	ABT
        1	2588654	2020-01-01	2019-12-31	2019Q4	2019Q4	0	AEE
        2	2592914	2020-01-01	2019-12-31	2019Q4	2019Q4	0	BAC
        3	2597248	2020-01-01	2019-12-31	2019Q4	2019Q4	0	CPE
        4	2600628	2020-01-01	2019-12-31	2019Q4	2019Q4	1	C
        ...	...	...	...	...	...	...	...
        156755	26591431	2023-12-29	2023-12-31	2023Q4	2023Q4	1	DUK
        156756	222487131	2023-12-29	2023-12-31	2023Q4	2023Q4	0	HOUS
        156757	247648457	2023-12-29	2023-12-31	2023Q4	2023Q4	0	AR
        156758	412297487	2023-12-29	2023-12-31	2023Q4	2024Q3	0	LGF.A
        156759	558575947	2023-12-29	2023-12-31	2023Q4	2023Q4	0	NVT
    """
    @_validate_args
    def __init__(
        self,
        dataitemid: int,
        period_type: _PeriodType = None,
        period_forward: int = 0,
        aggregation: _AggregationType = '1 week',
    ):
        if period_type in ["NTM"]:
            raise PrismValueError(
                f"Revision cannot take {period_type} as period_type.",
                valid_list=_PeriodType,
                invalids=["NTM"],
            )
        super().__init__(**_get_params(vars()))

    @classmethod
    @_validate_args
    def dataitems(cls, search: str = None, package: str = None):
        """
        Usable data items for the revision data component.


        Parameters
        ----------
            search : str, default None
                | Search word for dataitems name, the search is case-insensitive.
            package : str, default None
                | Search word for package name, the search is case-insensitive.

        Returns
        -------
            pandas.DataFrame
                Data items that belong to cash flow statement data component.

            Columns:
                - *datamodule*
                - *datacomponent*
                - *dataitemid*
                - *datadescription*

        Examples
        --------
            >>> di = ps.estimate.revision.dataitems('net income')
            >>> di[['dataitemid', 'dataitemname']]
                dataitemid                                       dataitemname
            0       200528  Net Income (Excl. Extraordinary Items & Good W...
            1       200529  Net Income (Excl. Extraordinary Items & Good W...
            2       200530  Net Income (Excl. Extraordinary Items & Good W...
            3       200531  Net Income (Excl. Extraordinary Items & Good W...
            4       200532  Net Income (Excl. Extraordinary Items & Good W...
            5       200533  Net Income (Excl. Extraordinary Items & Good W...
            6       200534  Net Income (Excl. Extraordinary Items & Good W...
            7       200535  Net Income (Excl. Extraordinary Items & Good W...
            8       200536        Net Income (GAAP) - Revision, # of Analysts
            9       200537                 Net Income (GAAP) - Revision, Down
            10      200538            Net Income (GAAP) - Revision, No Change
            11      200539  Net Income (GAAP) - Revision, Unfiltered # of ...
            12      200540      Net Income (GAAP) - Revision, Unfiltered Down
            13      200541  Net Income (GAAP) - Revision, Unfiltered No Ch...
            14      200542        Net Income (GAAP) - Revision, Unfiltered Up
            15      200543                   Net Income (GAAP) - Revision, Up
            16      200544    Net Income Normalized - Revision, # of Analysts
            17      200545             Net Income Normalized - Revision, Down
            18      200546        Net Income Normalized - Revision, No Change
            19      200547  Net Income Normalized - Revision, Unfiltered #...
            20      200548  Net Income Normalized - Revision, Unfiltered Down
            21      200549  Net Income Normalized - Revision, Unfiltered N...
            22      200550    Net Income Normalized - Revision, Unfiltered Up
            23      200551               Net Income Normalized - Revision, Up
        """
        return cls._dataitems(search=search, package=package)


class surprise(_PrismEstimateComponent):
    """
    | Differences in consensus estimate and the actual for a data item.
    | Default frequency is quarterly.

    Parameters
    ----------
        dataitemid : int
            | Unique identifier for the different data item. This identifies the type of the value (Revenue, Expense, etc.)

        period_type : str, {'A', 'Annual', 'SA', 'Semi-Annual', 'Quarterly', 'Q'}
            | Surprise Period in which the financial statement results are estimated.
            | An Suprise Period can be of one of the following Period Types:

            - Annual period (A)
            - Quarterly period (Q)
            - Semi-Annual (SA)

        currency : str, {'report', 'trade', ISO3 currency}, default 'report'
            | Desired currency for the pricing data.

            - report : financial reporting currency for a given listing (i.e for Apple - USD, Tencent - CNY)
            - trade : trading currency for a given listing (i.e for Apple - USD, Tencent - HKD)
            - ISO3 currency : desired currency in ISO 4217 format (i.e USD, EUR, JPY, KRW, etc.)

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
        >>> di = ps.estimate.surprise.dataitems('revenue')
        >>> di[['dataitemid', 'dataitemname']]
           dataitemid                   dataitemname
        0      200618  Revenue - Surpise, Difference
        1      200619     Revenue - Surpise, Percent

        >>> rev = ps.estimate.surprise(dataitemid=200618, period_type='Q')
        >>> rev_df = rev.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
        >>> rev_df
             listingid        date  period_enddate  calendar_period  fiscal_period  currency  Revenue - Surpise, Difference  Ticker
        0      7909562  2010-01-05      2009-11-30           2009Q4         2009Q4       USD                     90770000.0     SNX
        1     38011619  2010-01-05      2009-11-30           2009Q4         2010Q1       USD                      3300000.0     ZEP
        2    133184870  2010-01-05      2009-11-30           2009Q4         2010Q2       USD                     32940000.0  MOS.WI
        3      2586910  2010-01-06      2009-11-30           2009Q4         2010Q1       USD                     10200000.0     AYI
        4      2611056  2010-01-06      2009-11-30           2009Q4         2010Q1       USD                    -36410000.0     FDO
          ...      ...         ...             ...              ...            ...       ...                            ...     ...
        31502  2654558  2015-12-21      2015-11-30           2015Q4         2016Q3       USD                    -25250000.0     SCS
        31503  2602239  2015-12-22      2015-11-30           2015Q4         2016Q2       USD                    -24620000.0     CAG
        31504  2634146  2015-12-22      2015-11-30           2015Q4         2016Q2       USD                   -122980000.0     NKE
        31505  2626876  2015-12-23      2015-11-30           2015Q4         2016Q1       USD                     -6080000.0     LNN
        31506  2639161  2015-12-23      2015-10-31           2015Q3         2015Q4       USD                    -12000000.0     PNY
    """
    @_validate_args
    def __init__(
        self,
        dataitemid: int,
        period_type: _PeriodType,
        currency: _CurrencyTypeWithReportTrade = "report",
    ):
        if period_type in ["NTM", None]:
            raise PrismValueError(
                f"Surprise cannot take {period_type} as period_type.",
                valid_list=_PeriodType,
                invalids=["NTM", "None"],
            )
        super().__init__(**_get_params(vars()))

    @classmethod
    @_validate_args
    def dataitems(cls, search: str = None, package: str = None):
        """
        Usable data items for the surprise data component.


        Parameters
        ----------
            search : str, default None
                | Search word for dataitems name, the search is case-insensitive.

            package : str, default None
                | Search word for package name, the search is case-insensitive.

        Returns
        -------
            pandas.DataFrame
                Data items that belong to cash flow statement data component.

            Columns:
                - *datamodule*
                - *datacomponent*
                - *dataitemid*
                - *datadescription*

        Examples
        --------
            >>> di = ps.estimate.surprise.dataitems('net income')
            >>> di[['dataitemid', 'dataitemname']]
            dataitemid                                       dataitemname
            0      200612  Net Income (Excl. Extraordinary Items & Good W...
            1      200613  Net Income (Excl. Extraordinary Items & Good W...
            2      200614            Net Income (GAAP) - Surpise, Difference
            3      200615               Net Income (GAAP) - Surpise, Percent
            4      200616        Net Income Normalized - Surpise, Difference
            5      200617           Net Income Normalized - Surpise, Percent
        """
        return cls._dataitems(search=search, package=package)


@_validate_args
def dataitems(search: str = None, package: str = None):
    """
    Usable data items for the estimate data category.

    Parameters
    ----------
        search : str, default None
            | Search word for dataitems name, the search is case-insensitive.

        package : str, default None
            | Search word for package name, the search is case-insensitive.

    Returns
    -------
        pandas.DataFrame
            Data items that belong to cash flow statement data component.

        Columns:
            - *datamodule*
            - *datacomponent*
            - *dataitemid*
            - *datadescription*


    Examples
    --------
        >>> di = ps.estimate.dataitems('net income')
        >>> di[['dataitemid', 'dataitemname']]
            dataitemid                                       dataitemname
        0       200027  Net Income (Excl. Extraordinary Items & Good W...
        1       200028                         Net Income (GAAP) - Actual
        2       200029                     Net Income Normalized - Actual
        3       200203  Net Income (Excl. Extraordinary Items & Good W...
        4       200204  Net Income (Excl. Extraordinary Items & Good W...
        5       200205  Net Income (Excl. Extraordinary Items & Good W...
        6       200206  Net Income (Excl. Extraordinary Items & Good W...
        7       200207  Net Income (Excl. Extraordinary Items & Good W...
        8       200208  Net Income (Excl. Extraordinary Items & Good W...
        9       200209      Net Income (GAAP) - Consensus, # of Estimates
        10      200210                Net Income (GAAP) - Consensus, High
        11      200211                 Net Income (GAAP) - Consensus, Low
        12      200212                Net Income (GAAP) - Consensus, Mean
        13      200213              Net Income (GAAP) - Consensus, Median
    """
    return _list_dataitem(
        datacategoryid=_PrismEstimateComponent.categoryid,
        datacomponentid=None,
        search=search,
        package=package,
    )
