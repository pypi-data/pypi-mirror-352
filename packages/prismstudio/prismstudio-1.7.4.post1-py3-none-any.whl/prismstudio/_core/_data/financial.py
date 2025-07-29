from ..._common.const import (
    FinancialPeriodType as _PeriodType,
    FinancialPeriodTypeWithLTMQSA as _PeriodTypeLTMQSA,
    FinancialPreliminaryType as _FinancialPreliminaryType,
    CurrencyTypeWithReportTrade as _CurrencyTypeWithReportTrade,
    SegmentClassification as _SegmentClassification,
)
from .._req_builder import _list_dataitem
from ..._prismcomponent.prismcomponent import _PrismDataComponent, _PrismComponent
from ..._utils import _get_params, _validate_args
from ..._utils.exceptions import PrismValueError


__all__ = [
    "balance_sheet",
    "cash_flow",
    "dps",
    "date",
    "eps",
    "income_statement",
    "segment",
    "ratio",
    "commitment",
    "pension",
    "option",
    "dataitems",
]


_data_category = __name__.split(".")[-1]


class _PrismFinancialDataComponent(_PrismDataComponent, _PrismComponent):
    _component_category_repr = _data_category

    @classmethod
    def _dataitems(cls, search : str = None, package : str = None):
        return _list_dataitem(
            datacategoryid=cls.categoryid,
            datacomponentid=cls.componentid,
            search=search,
            package=package,
        )


class balance_sheet(_PrismFinancialDataComponent):
    """
    | Data that pertains to a balance sheet portion in financial statement.
    | Default frequency is aperiodic daily.

    Parameters
    ----------
        dataitemid : int
            Unique identifier for the different data item. This identifies the type of the balance sheet value (Revenue, Expense, etc.)

        period_type : str, {'A', 'Annual', 'SA', 'Semi-Annual', 'Quarterly', 'Q', 'Q-SA'}
            | Financial Period in which the financial statement results are reported.
            | A Financial Period can be of one of the following Period Types:

            - Annual period (A)
            - Quarterly period (Q)
            - Semi-Annual (SA)
            - Quarterly-Semi-Annual (Q-SA)

        period_back : int, default 0
            | Specifies the number of periods to go back from the latest financial data.
            | For example, a value of 0 retrieves the most recently released financial data, while a value of 1 retrieves the financial data from the previous period, and so on.

        preliminary : str, {'keep', 'ignore', 'null'}, default 'keep'
            - keep : keep preliminary data
            - ignore : ignore preliminary data

            .. admonition:: Note
                :class: note

                | If the 'ignore' option is chosen, preliminary reports are disregarded entirely, as if they never existed.
                |
                | Consequently, if a revision occurs on the same day as the preliminary report, the latest period (period 0) will continue to display the previous period of preliminary reporting, and it will not be updated until the official report is released.

            - null : nulled-out preliminary data

        currency : str, {'report', 'trade', ISO3 currency}, default 'report'
            | Desired currency for the financial data.

            - report : financial reporting currency for a given listing (i.e for Apple - USD, Tencent - CNY)
            - trade : trading currency for a given listing (i.e for Apple - USD, Tencent - HKD)
            - ISO3 currency : desired currency in ISO 4217 format (i.e USD, EUR, JPY, KRW, etc.)

            .. admonition:: Warning
                :class: warning

                | If a selected data item is not a currency value (i.e airplanes owned), the currency input will be ignored.
                | It will behave like parameter input currency=None

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
        >>> di = ps.financial.balance_sheet.dataitems('asset')
            dataitemid                                       dataitemname
        0       100003                           Trading Asset Securities
        1       100012              Finance Division Other Current Assets
        2       100013                        Other Current Assets, Total
        3       100015                       Deferred Tax Assets, Current
        4       100017                               Other Current Assets
        ..         ...                                                ...
        10      100033                                      Assets, Total
        ..         ...                                                ...
        59      100349  Right-of-Use Assets - Operating Lease - Accumu...
        60      100350      Right-of-Use Assets - Operating Lease - Gross
        61      100351        Right-of-Use Assets - Operating Lease - Net
        62      100365                           Trading Asset Securities
        63      100366                           Trading Portfolio Assets

        >>> ta = ps.financial.balance_sheet(dataitemid=100033, period_type='Q')
        >>> ta_df = ta.get_data(universe='US Primary', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
        >>> ta_df
             listingid        date  period_enddate  fiscal_period  calendar_period  currency  Assets, Total  Ticker
        0      2602239  2010-01-05      2009-11-29         2010Q2           2009Q4       USD   1.156650e+10     CAG
        1      2628457  2010-01-05      2009-11-26         2010Q2           2009Q4       USD   7.047400e+08     MCS
        2      2654558  2010-01-05      2009-11-27         2010Q3           2009Q4       USD   1.746900e+09     SCS
        3      7909562  2010-01-05      2009-11-30         2009Q4           2009Q4       USD   2.100288e+09     SNX
        4     38011619  2010-01-05      2009-11-30         2010Q1           2009Q4       USD   2.475090e+08     ZEP
        ...        ...         ...             ...            ...              ...       ...            ...     ...
        62570  2654558  2015-12-23      2015-11-27         2016Q3           2015Q4       USD   1.791400e+09     SCS
        62571  2658404  2015-12-23      2015-10-31         2015Q4           2015Q3       USD   1.303658e+09     TTC
        62572  2664585  2015-12-23      2015-11-28         2016Q1           2015Q4       USD   3.543320e+08     WGO
        62573  2609477  2015-12-30      2015-11-30         2016Q3           2015Q4       USD   4.070550e+08     EBF
        62574  2634533  2015-12-30      2015-10-31         2015Q4           2015Q3       USD   2.192866e+06     NRT
    """
    @_validate_args
    def __init__(
        self,
        dataitemid: int,
        period_type: _PeriodType,
        period_back: int = 0,
        preliminary: _FinancialPreliminaryType = "keep",
        currency: _CurrencyTypeWithReportTrade = "report",
    ):
        if period_type in ["YTD", "LTM"]:
            raise PrismValueError(
                f"Balance Sheet cannot take {period_type} as period_type.",
                valid_list=_PeriodType,
                invalids=["YTD", "LTM", "NTM"],
            )
        super().__init__(**_get_params(vars()))

    @classmethod
    @_validate_args
    def dataitems(cls, search : str = None, package : str = None):
        """
        Usable data items for the balance sheet data component.

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
            >>> ps.financial.balance_sheet.dataitems('asset')
                dataitemid  ...                                dataitemdescription
            0       100003  ...  This item represents both debt and equity secu...
            1       100012  ...  This item represents all current assets of a f...
            2       100013  ...                                               None
            3       100015  ...  This item represents the deferred tax conseque...
            4       100017  ...  This item represents current assets other than...
            ..         ...  ...                                                ...
            59      100349  ...                                               None
            60      100350  ...                                               None
            61      100351  ...                                               None
            62      100365  ...                                    Mapped from TAS
            63      100366  ...                                    Mapped from TAP
        """
        return cls._dataitems(search=search, package=package)


class cash_flow(_PrismFinancialDataComponent):
    """
    | Data that pertains to a cash flow statement portion in financial statement.
    | Default frequency is aperiodic daily.

    Parameters
    ----------
        dataitemid : int
            | Unique identifier for the different data item. This identifies the type of the balance sheet value (Revenue, Expense, etc.)

        period_type : str, {'A', 'Annual', 'SA', 'Semi-Annual', 'Quarterly', 'Q', 'Q-SA', 'LTM'}
            | Financial Period in which the financial statement results are reported.
            | A Financial Period can be of one of the following Period Types:

            - Annual period (A)
            - Semi-Annual (SA)
            - Quarterly period (Q)
            - Quarterly-Semi-Annual (Q-SA)
            - Last twelve months (LTM)

        period_back : int, default 0
            | Specifies the number of periods to go back from the latest financial data.
            | For example, a value of 0 retrieves the most recently released financial data, while a value of 1 retrieves the financial data from the previous period, and so on.

        preliminary : str, {'keep', 'ignore', 'null'}, default 'keep'
            - keep : keep preliminary data
            - ignore : ignore preliminary data

            .. admonition:: Note
                :class: note

                | If the 'ignore' option is chosen, preliminary reports are disregarded entirely, as if they never existed.
                |
                | Consequently, if a revision occurs on the same day as the preliminary report, the latest period (period 0) will continue to display the previous period of preliminary reporting, and it will not be updated until the official report is released.

            - null : nulled-out preliminary data

        currency : str, {'report', 'trade', ISO3 currency}, default 'report'
            | Desired currency for the financial data.

            - report : financial reporting currency for a given listing (i.e for Apple - USD, Tencent - CNY)
            - trade : trading currency for a given listing (i.e for Apple - USD, Tencent - HKD)
            - ISO3 currency : desired currency in ISO 4217 format (i.e USD, EUR, JPY, KRW, etc.)

            .. admonition:: Warning
                :class: warning

                | If a selected data item is not a currency value (i.e airplanes owned), the currency input will be ignored.
                | It will behave like parameter input currency=None

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
        >>> di = ps.financial.cash_flow.dataitems('capital')
        >>> di[['dataitemid', 'dataitemname']]
             dataitemid                                          dataitemname
        0        100413                                   Capital Expenditure
        1        100458                                Capital Lease Payments
        2        100484                       Changes in Capitalized Software
        3        100540     Tax Benefit on Stock Options - Working Capital...
        4        112915                         Change in Net Working Capital
        5        300162                            Changes in Working Capital
        6        300167                                  Capital Expenditures
        7        300210                        Net Changes in Working Capital

        >>> ce = ps.financial.cash_flow(dataitemid=100413, period_type='LTM')
        >>> ce_df = ce.get_data(universe='US Primary', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
        >>> ce_df
             listingid        date  period_enddate  fiscal_period  calendar_period  currency  Capital Expenditure  Ticker
        0      2602239  2010-01-05      2009-11-29         2010Q2           2009Q4       USD         -462700000.0     CAG
        1      2628457  2010-01-05      2009-11-26         2010Q2           2009Q4       USD          -32082000.0     MCS
        2      2654558  2010-01-05      2009-11-27         2010Q3           2009Q4       USD          -43300000.0     SCS
        3      7909562  2010-01-05      2009-11-30         2009Q4           2009Q4       USD                  NaN     SNX
        4     38011619  2010-01-05      2009-11-30         2010Q1           2009Q4       USD           -6537000.0     ZEP
        ...        ...         ...             ...            ...              ...       ...                  ...     ...
        62876  2654558  2015-12-23      2015-11-27         2016Q3           2015Q4       USD          -98500000.0     SCS
        62877  2658404  2015-12-23      2015-10-31         2015Q4           2015Q3       USD          -56374000.0     TTC
        62878  2664585  2015-12-23      2015-11-28         2016Q1           2015Q4       USD          -17372000.0     WGO
        62879  2609477  2015-12-30      2015-11-30         2016Q3           2015Q4       USD           -5495000.0     EBF
    """
    @_validate_args
    def __init__(
        self,
        dataitemid: int,
        period_type: _PeriodTypeLTMQSA,
        period_back: int = 0,
        preliminary: _FinancialPreliminaryType = "keep",
        currency: _CurrencyTypeWithReportTrade = "report",
    ):
        super().__init__(**_get_params(vars()))

    @classmethod
    @_validate_args
    def dataitems(cls, search: str = None, package: str = None):
        """
        Usable data items for the cash flow statement data component.

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
            >>> ps.financial.cash_flow.dataitems('free cash')
            dataitemid  ...       dataitemdescription
            0      100506  ...                      None
            1      100513  ...    Levered Free Cash Flow
            2      100544  ...  Unlevered Free Cash Flow
        """
        return cls._dataitems(search=search, package=package)


class dps(_PrismFinancialDataComponent):
    """
    | Dividend per share related data.
    | Default frequency is aperiodic daily.

    Parameters
    ----------
        dataitemid : int
            | Unique identifier for the different data item. This identifies the type of the balance sheet value (Revenue, Expense, etc.)

        period_type : str, {'A', 'Annual', 'SA', 'Semi-Annual', 'Quarterly', 'Q', 'Q-SA', 'LTM'}
            | Financial Period in which the financial statement results are reported.
            | A Financial Period can be of one of the following Period Types:

            - Annual period (A)
            - Semi-Annual (SA)
            - Quarterly period (Q)
            - Quarterly-Semi-Annual (Q-SA)
            - Last twelve months (LTM)

        period_back : int, default 0
            | Specifies the number of periods to go back from the latest financial data.
            | For example, a value of 0 retrieves the most recently released financial data, while a value of 1 retrieves the financial data from the previous period, and so on.

        preliminary : str, {'keep', 'ignore', 'null'}, default 'keep'
            - keep : keep preliminary data
            - ignore : ignore preliminary data

            .. admonition:: Note
                :class: note

                | If the 'ignore' option is chosen, preliminary reports are disregarded entirely, as if they never existed.
                |
                | Consequently, if a revision occurs on the same day as the preliminary report, the latest period (period 0) will continue to display the previous period of preliminary reporting, and it will not be updated until the official report is released.

            - null : nulled-out preliminary data

        currency : str, {'report', 'trade', ISO3 currency}, default 'report'
            | Desired currency for the financial data.

            - report : financial reporting currency for a given listing (i.e for Apple - USD, Tencent - CNY)
            - trade : trading currency for a given listing (i.e for Apple - USD, Tencent - HKD)
            - ISO3 currency : desired currency in ISO 4217 format (i.e USD, EUR, JPY, KRW, etc.)

            .. admonition:: Warning
                :class: warning

                | If a selected data item is not a currency value (i.e airplanes owned), the currency input will be ignored.
                | It will behave like parameter input currency=None

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
        >>> di = ps.financial.dps.dataitems()
        >>> di[['dataitemid', 'dataitemname']]
            dataitemid                                       dataitemname
        0       100547                       Distributable Cash Per Share
        1       100548             Distributable Cash Per Share (Diluted)
        2       100549                                 Dividend Per Share
        3       100550                         Dividend Per Share Class A
        4       100551                         Dividend Per Share Class B
        5       100552                         Special Dividend Per Share
        6       100553         Special Dividend Per Share - Non-Recurring
        7       100554             Special Dividend Per Share - Recurring
        8       100555                 Special Dividend Per Share Class A
        9       100556  Special Dividend Per Share Class A - Non-Recur...
        10      100557     Special Dividend Per Share Class A - Recurring
        11      100558                 Special Dividend Per Share Class B
        12      100559  Special Dividend Per Share Class B - Non-Recur...
        13      100560     Special Dividend Per Share Class B - Recurring

        >>> dps = ps.financial.dps(dataitemid=100549, period_type='LTM')
        >>> dps_df = dps.get_data(universe='US Primary', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
        >>> dps_df
            listingid        date  period_enddate  fiscal_period  calendar_period  currency  Dividend Per Share  Ticker
        0      2602239  2010-01-05      2009-11-29         2010Q2           2009Q4       USD              0.7700    CAG
        1      2628457  2010-01-05      2009-11-26         2010Q2           2009Q4       USD              0.3400    MCS
        2      2654558  2010-01-05      2009-11-27         2010Q3           2009Q4       USD              0.2400    SCS
        3      7909562  2010-01-05      2009-11-30         2009Q4           2009Q4       USD                 NaN    SNX
        4     38011619  2010-01-05      2009-11-30         2010Q1           2009Q4       USD              0.1600    ZEP
        ...        ...         ...             ...            ...              ...       ...                 ...    ...
        62876  2654558  2015-12-23      2015-11-27         2016Q3           2015Q4       USD              0.4425    SCS
        62877  2658404  2015-12-23      2015-10-31         2015Q4           2015Q3       USD              0.5000    TTC
        62878  2664585  2015-12-23      2015-11-28         2016Q1           2015Q4       USD              0.3700    WGO
        62879  2609477  2015-12-30      2015-11-30         2016Q3           2015Q4       USD              0.7000    EBF
        62880  2634533  2015-12-30      2015-10-31         2015Q4           2015Q3       USD              1.2700    NRT
    """
    @_validate_args
    def __init__(
        self,
        dataitemid: int,
        period_type: _PeriodTypeLTMQSA,
        period_back: int = 0,
        preliminary: _FinancialPreliminaryType = "keep",
        currency: _CurrencyTypeWithReportTrade = "report",
    ):
        super().__init__(**_get_params(vars()))

    @classmethod
    @_validate_args
    def dataitems(cls, search: str = None, package: str = None):
        """
        Usable data items for the dividend per share data component.

        Parameters
        ----------
            search : str, default None
                | Search word for dataitems name, the search is case-insensitive.

            package : str, default None
                | Search word for package name, the search is case-insensitive.

        Returns
        -------
            pandas.DataFrame
                | Data items that belong to cash flow statement data component.

            Columns:

                - *datamodule*
                - *datacomponent*
                - *dataitemid*
                - *datadescription*

        Examples
        --------
            >>> dpsdi = ps.financial.dps.dataitems()
            >>> dpsdi[['dataitemid', 'dataitemname']]
                dataitemid                                       dataitemname
            0       100547                       Distributable Cash Per Share
            1       100548             Distributable Cash Per Share (Diluted)
            2       100549                                 Dividend Per Share
            3       100550                         Dividend Per Share Class A
            4       100551                         Dividend Per Share Class B
            5       100552                         Special Dividend Per Share
            6       100553         Special Dividend Per Share - Non-Recurring
            7       100554             Special Dividend Per Share - Recurring
            8       100555                 Special Dividend Per Share Class A
            9       100556  Special Dividend Per Share Class A - Non-Recur...
            10      100557     Special Dividend Per Share Class A - Recurring
            11      100558                 Special Dividend Per Share Class B
            12      100559  Special Dividend Per Share Class B - Non-Recur...
            13      100560     Special Dividend Per Share Class B - Recurring
        """
        return cls._dataitems(search=search, package=package)


class date(_PrismFinancialDataComponent):
    """
    | Relavent dates in the financial statement.
    | Default frequency is aperiodic daily.

    Parameters
    ----------
        period_type : str, {'A', 'Annual', 'SA', 'Semi-Annual', 'Quarterly', 'Q', 'LTM'}
            | Financial Period in which the financial statement results are reported.
            | A Financial Period can be of one of the following Period Types:

            - Annual period (A)
            - Semi-Annual (SA)
            - Quarterly period (Q)
            - Quarterly-Semi-Annual (Q-SA)
            - Last twelve months (LTM)

    Returns
    -------
        prism._PrismComponent
            =======================     =====================================================================================================================================================================================================================================================================================
            Date Type                   Description
            =======================     =====================================================================================================================================================================================================================================================================================
            Press Release               Preliminary earnings release. This information is usually released by the company prior to the official filing or release of data.
            Original                    Original company filing for period. These numbers were the originally filed numbers (not a press release) for this period. In the U.S., this would be represented by a 10K or 10Q SEC filing.
            Restated                    Results are fundamentally different from the original, i.e., Net Income, Retained Earnings, Total Assets or Cash from Operations are different. Restatements usually happen after an acquisition, divestiture, merger or accounting change.
            No Change from Original     Appearing again in a later filing, but unchanged from original, or not comparable due to different reporting currencies. These numbers were from a subsequent filing and were recollected but they do not represent changes in the financials that would be considered a restatement.
            Reclassified                Results somewhat different from original, but bottom line results are the same.
            =======================     =====================================================================================================================================================================================================================================================================================

    Examples
    --------
        >>> fdate = ps.financial.date('Q')
        >>> fdate_df = fdate.get_data(universe='US Primary', startdate='2018-01-01')
        >>> fdate_df
    	       listingid        date  period_enddate  calendar_period  fiscal_period      datetype  Ticker
        0        2602239  2010-01-05      2008-11-23           2008Q4         2009Q2  Reclassified     CAG
        1        2602239  2010-01-05      2008-11-23           2008Q4         2009Q2  Reclassified     CAG
        2        2602239  2010-01-05      2008-11-23           2008Q4         2009Q2  Reclassified     CAG
        3        2602239  2010-01-05      2008-11-23           2008Q4         2009Q2  Reclassified     CAG
        4        2602239  2010-01-05      2008-11-23           2008Q4         2009Q2  Reclassified     CAG
        ...          ...         ...             ...              ...            ...           ...     ...
        2302563  2634533  2015-12-30      2015-10-31           2015Q3         2015Q4      Original     NRT
        2302564  2634533  2015-12-30      2015-10-31           2015Q3         2015Q4      Original     NRT
        2302565  2634533  2015-12-30      2015-10-31           2015Q3         2015Q4      Original     NRT
        2302566  2634533  2015-12-30      2015-10-31           2015Q3         2015Q4      Original     NRT
        2302567  2634533  2015-12-30      2015-10-31           2015Q3         2015Q4      Original     NRT
    """
    @_validate_args
    def __init__(
        self,
        period_type: _PeriodTypeLTMQSA,
        package : str = None,
    ):
        super().__init__(**_get_params(vars()))


class eps(_PrismFinancialDataComponent):
    """
    | Earnings per share related data.
    | Default frequency is aperiodic daily.

    Parameters
    ----------
        dataitemid : int
            | Unique identifier for the different data item. This identifies the type of the balance sheet value (Revenue, Expense, etc.)

        period_type : str, {'A', 'Annual', 'SA', 'Semi-Annual', 'Quarterly', 'Q', 'Q-SA', 'LTM'}
            | Financial Period in which the financial statement results are reported.
            | A Financial Period can be of one of the following Period Types:

            - Annual period (A)
            - Semi-Annual (SA)
            - Quarterly period (Q)
            - Quarterly-Semi-Annual (Q-SA)
            - Last twelve months (LTM)

        period_back : int, default 0
            | Specifies the number of periods to go back from the latest financial data.
            | For example, a value of 0 retrieves the most recently released financial data, while a value of 1 retrieves the financial data from the previous period, and so on.

        preliminary : str, {'keep', 'ignore', 'null'}, default 'keep'
            - keep : keep preliminary data
            - ignore : ignore preliminary data

            .. admonition:: Note
                :class: note

                | If the 'ignore' option is chosen, preliminary reports are disregarded entirely, as if they never existed.
                |
                | Consequently, if a revision occurs on the same day as the preliminary report, the latest period (period 0) will continue to display the previous period of preliminary reporting, and it will not be updated until the official report is released.

            - null : nulled-out preliminary data

        currency : str, {'report', 'trade', ISO3 currency}, default 'report'
            | Desired currency for the financial data.

            - report : financial reporting currency for a given listing (i.e for Apple - USD, Tencent - CNY)
            - trade : trading currency for a given listing (i.e for Apple - USD, Tencent - HKD)
            - ISO3 currency : desired currency in ISO 4217 format (i.e USD, EUR, JPY, KRW, etc.)

            .. admonition:: Warning
                :class: warning

                | If a selected data item is not a currency value (i.e airplanes owned), the currency input will be ignored.
                | It will behave like parameter input currency=None
    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
        >>> di = ps.financial.eps.dataitems()
        >>> di[['dataitemid', 'dataitemname']]
            dataitemid                                       dataitemname
        0       100561                           Basic Earnings Per Share
        1       100562       Basic Earnings Per Share - Accounting Change
        2       100563   Basic Earnings Per Share - Continuing Operations
        3       100564  Basic Earnings Per Share - Discontinued Operat...
        4       100565     Basic Earnings Per Share - Extraordinary Items
        5       100566  Basic Earnings Per Share - Extraordinary Items...
        6       100567                         Diluted Earnings Per Share
        7       100568     Diluted Earnings Per Share - Accounting Change
        8       100569  Diluted Earnings Per Share - Continuing Operat...
        9       100570  Diluted Earnings Per Share - Discontinued Oper...
        10      100571   Diluted Earnings Per Share - Extraordinary Items
        11      100572  Diluted Earnings Per Share - Extraordinary Ite...
        12      100573                Normalized Basic Earnings Per Share
        13      100574              Normalized Diluted Earnings Per Share
        14      100575                 Reported Basic Earnings Per Share
        15      100576  Reported Basic Earnings Per Share Excl. Extrao...
        16      100577                Reported Diluted Earnings Per Share
        17      100578  Reported Diluted Earnings Per Share Excl. Extr...
        18      100579                                 Revenues Per Share

        >>> eps = ps.financial.eps(dataitemid=100567, period_type='LTM')
        >>> eps_df = eps.get_data(universe='US Primary', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
        >>> eps_df
             listingid        date  period_enddate  fiscal_period  calendar_period  currency  Net EPS - Diluted  Ticker
        0      2602239  2010-01-05      2009-11-29         2010Q2           2009Q4       USD           1.721960     CAG
        1      2628457  2010-01-05      2009-11-26         2010Q2           2009Q4       USD           0.456824     MCS
        2      2654558  2010-01-05      2009-11-27         2010Q3           2009Q4       USD          -0.496169     SCS
        3      7909562  2010-01-05      2009-11-30         2009Q4           2009Q4       USD           2.704926     SNX
        4     38011619  2010-01-05      2009-11-30         2010Q1           2009Q4       USD           0.744766     ZEP
        ...        ...         ...             ...            ...              ...       ...                ...     ...
        62876  2654558  2015-12-23      2015-11-27         2016Q3           2015Q4       USD           0.920032     SCS
        62877  2658404  2015-12-23      2015-10-31         2015Q4           2015Q3       USD           1.775000     TTC
        62878  2664585  2015-12-23      2015-11-28         2016Q1           2015Q4       USD           1.469969     WGO
        62879  2609477  2015-12-30      2015-11-30         2016Q3           2015Q4       USD           1.537342     EBF
        62880  2634533  2015-12-30      2015-10-31         2015Q4           2015Q3       USD           1.260057     NRT
    """
    @_validate_args
    def __init__(
        self,
        dataitemid: int,
        period_type: _PeriodTypeLTMQSA,
        period_back: int = 0,
        preliminary: _FinancialPreliminaryType = "keep",
        currency: _CurrencyTypeWithReportTrade = "report",
    ):
        super().__init__(**_get_params(vars()))

    @classmethod
    @_validate_args
    def dataitems(cls, search: str = None, package: str = None):
        """
        Usable data items for the earnings per share data component.

        Parameters
        ----------
            search : str, default None
                | Search word for dataitems name, the search is case-insensitive.

            package : str, default None
                | Search word for package name, the search is case-insensitive.

        Returns
        -------
            pandas.DataFrame
                | Data items that belong to cash flow statement data component.

            Columns:

                - *datamodule*
                - *datacomponent*
                - *dataitemid*
                - *datadescription*

        Examples
        --------
            >>> epsdi = ps.financial.eps.dataitems()
            >>> epsdi[['dataitemid', 'dataitemname']]
                dataitemid                                       dataitemname
            0       100561                           Basic Earnings Per Share
            1       100562       Basic Earnings Per Share - Accounting Change
            2       100563   Basic Earnings Per Share - Continuing Operations
            3       100564  Basic Earnings Per Share - Discontinued Operat...
            4       100565     Basic Earnings Per Share - Extraordinary Items
            5       100566  Basic Earnings Per Share - Extraordinary Items...
            6       100567                         Diluted Earnings Per Share
            7       100568     Diluted Earnings Per Share - Accounting Change
            8       100569  Diluted Earnings Per Share - Continuing Operat...
            9       100570  Diluted Earnings Per Share - Discontinued Oper...
            10      100571   Diluted Earnings Per Share - Extraordinary Items
            11      100572  Diluted Earnings Per Share - Extraordinary Ite...
            12      100573                Normalized Basic Earnings Per Share
            13      100574              Normalized Diluted Earnings Per Share
            14      100575                 Reported Basic Earnings Per Share
            15      100576  Reported Basic Earnings Per Share Excl. Extrao...
            16      100577                Reported Diluted Earnings Per Share
            17      100578  Reported Diluted Earnings Per Share Excl. Extr...
            18      100579                                 Revenues Per Share
        """
        return cls._dataitems(search=search, package=package)


class income_statement(_PrismFinancialDataComponent):
    """
    | Data that pertains to a income statement portion in financial statement.
    | Default frequency is aperiodic daily.

    Parameters
    ----------
        dataitemid : int
            | Unique identifier for the different data item. This identifies the type of the balance sheet value (Revenue, Expense, etc.)

        period_type : str, {'A', 'Annual', 'SA', 'Semi-Annual', 'Quarterly', 'Q', 'Q-SA', 'LTM'}
            | Financial Period in which the financial statement results are reported.
            | A Financial Period can be of one of the following Period Types:

            - Annual period (A)
            - Semi-Annual (SA)
            - Quarterly period (Q)
            - Quarterly-Semi-Annual (Q-SA)
            - Last twelve months (LTM)

        period_back : int, default 0
            | Specifies the number of periods to go back from the latest financial data.
            | For example, a value of 0 retrieves the most recently released financial data, while a value of 1 retrieves the financial data from the previous period, and so on.

        preliminary : str, {'keep', 'ignore', 'null'}, default 'keep'
            - keep : keep preliminary data
            - ignore : ignore preliminary data

            .. admonition:: Note
                :class: note

                | If the 'ignore' option is chosen, preliminary reports are disregarded entirely, as if they never existed.
                |
                | Consequently, if a revision occurs on the same day as the preliminary report, the latest period (period 0) will continue to display the previous period of preliminary reporting, and it will not be updated until the official report is released.

            - null : nulled-out preliminary data

        currency : str, {'report', 'trade', ISO3 currency}, default 'report'
            | Desired currency for the financial data.

            - report : financial reporting currency for a given listing (i.e for Apple - USD, Tencent - CNY)
            - trade : trading currency for a given listing (i.e for Apple - USD, Tencent - HKD)
            - ISO3 currency : desired currency in ISO 4217 format (i.e USD, EUR, JPY, KRW, etc.)

            .. admonition:: Warning
                :class: warning

                | If a selected data item is not a currency value (i.e airplanes owned), the currency input will be ignored.
                | It will behave like parameter input currency=None

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
        >>> di = ps.financial.income_statement.dataitems('net income')
            dataitemid                             dataitemname
        0       100637                    Net Income to Company
        1       100639                               Net Income
        2       100644          Other Adjustments to Net Income
        3       100645  Net Income Allocable to General Partner
        4       100646   Net Income to Common Incl. Extra Items
        5       100647   Net Income to Common Excl. Extra Items
        6       100703                       Diluted Net Income
        7       100829                               Net Income
        8       100830               Net Income as per SFAS 123
        9       100831  Net Income from Discontinued Operations
        10      100842                    Normalized Net Income

        >>> ni = ps.financial.income_statement(dataitemid=100639, period_type='LTM')
        >>> ni_df = ni.get_data(universe='US Primary', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
        >>> ni_df
             listingid        date  period_enddate  fiscal_period  calendar_period  currency  Net Income - (Income Statement)  Ticker
        0      2602239  2010-01-05      2009-11-29         2010Q2           2009Q4       USD                      773500000.0     CAG
        1      2628457  2010-01-05      2009-11-26         2010Q2           2009Q4       USD                       13766000.0     MCS
        2      2654558  2010-01-05      2009-11-27         2010Q3           2009Q4       USD                      -65700000.0     SCS
        3      7909562  2010-01-05      2009-11-30         2009Q4           2009Q4       USD                       92088000.0     SNX
        4     38011619  2010-01-05      2009-11-30         2010Q1           2009Q4       USD                       16225000.0     ZEP
        ...        ...         ...             ...            ...              ...       ...                              ...     ...
        62876  2654558  2015-12-23      2015-11-27         2016Q3           2015Q4       USD                      115600000.0     SCS
        62877  2658404  2015-12-23      2015-10-31         2015Q4           2015Q3       USD                      201591000.0     TTC
        62878  2664585  2015-12-23      2015-11-28         2016Q1           2015Q4       USD                       39873000.0     WGO
        62879  2609477  2015-12-30      2015-11-30         2016Q3           2015Q4       USD                       39489000.0     EBF
        62880  2634533  2015-12-30      2015-10-31         2015Q4           2015Q3       USD                       11580673.0     NRT
    """
    @_validate_args
    def __init__(
        self,
        dataitemid: int,
        period_type: _PeriodTypeLTMQSA,
        period_back: int = 0,
        preliminary: _FinancialPreliminaryType = "keep",
        currency: _CurrencyTypeWithReportTrade = "report",
    ):
        super().__init__(**_get_params(vars()))

    @classmethod
    @_validate_args
    def dataitems(cls, search: str = None, package: str = None):
        """
        Usable data items for the income statement data component.

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
            >>> ps.financial.income_statement.dataitems('income')
                dataitemid  ...                                dataitemdescription
            0       100586  ...  This item represents the interest and investme...
            1       100588  ...  This item represents fee from non-fund based a...
            2       100607  ...  This item represents all other operating expen...
            3       100610  ...  This item represents the difference between th...
            4       100612  ...  This item represents the interest and investme...
            ..         ...  ...                                                ...
            71      100902  ...                                               None
            72      100903  ...  This item represents the total sub-lease incom...
            73      100904  ...  This item represents Taxes other than excise a...
            74      100905  ...  This item represents all taxes other than inco...
            75      100906  ...  This item represents refund of any tax amount ...
        """
        return cls._dataitems(search=search, package=package)


class segment(_PrismFinancialDataComponent):
    """
    | Data that pertains to a specific segment or division within a company.
    | Default frequency is aperiodic daily.

    Parameters
    ----------
        dataitemid : int
            | Unique identifier for the different data item.

        period_type : str, {'A', 'Annual', 'SA', 'Semi-Annual', 'Quarterly', 'Q', 'Q-SA', 'LTM'}
            | Financial Period in which the financial statement results are reported.
            | A Financial Period can be of one of the following Period Types:

            - Annual period (A)
            - Semi-Annual (SA)
            - Quarterly period (Q)
            - Quarterly-Semi-Annual (Q-SA)
            - Last twelve months (LTM)

        period_back : int, default 0
            | Specifies the number of periods to go back from the latest financial data.
            | For example, a value of 0 retrieves the most recently released financial data, while a value of 1 retrieves the financial data from the previous period, and so on.

        preliminary : str, {'keep', 'ignore', 'null'}, default 'keep'
            - keep : keep preliminary data
            - ignore : ignore preliminary data

            .. admonition:: Note
                :class: note

                | If the 'ignore' option is chosen, preliminary reports are disregarded entirely, as if they never existed.
                |
                | Consequently, if a revision occurs on the same day as the preliminary report, the latest period (period 0) will continue to display the previous period of preliminary reporting, and it will not be updated until the official report is released.

            - null : nulled-out preliminary data

        currency : str, {'report', 'trade', ISO3 currency}, default 'report'
            | Desired currency for the financial data.

            - report : financial reporting currency for a given listing (i.e for Apple - USD, Tencent - CNY)
            - trade : trading currency for a given listing (i.e for Apple - USD, Tencent - HKD)
            - ISO3 currency : desired currency in ISO 4217 format (i.e USD, EUR, JPY, KRW, etc.)

            .. admonition:: Warning
                :class: warning

                | If a selected data item is not a currency value (i.e airplanes owned), the currency input will be ignored.
                | It will behave like parameter input currency=None

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
        >>> segment = ps.financial.segment.dataitems()
        >>> segment[['dataitemid', 'dataitemname']]
           dataitemid                                     dataitemname
        0      104729                        Business Segments - CAPEX
        1      104730  Business Segments - Depreciation & Amortization
        2      104731                       Business Segments - EBITDA
        3      104732                          Business Segments - EBT
        4      104733                 Business Segments - Gross Profit
        5      104734           Business Segments - Income Tax Expense
        6      104735             Business Segments - Interest Expense
        7      104736                        Business Segments - NOPAT
        8      104737                   Business Segments - Net Income
        >>> seg = ps.financial.segment(104731, period_type='Q', segment_classification='NAICS)
        >>> seg.get_data(universe='US Primary', startdate='2010-01-01', enddate='2015-01-01', shownid=['ticker'])
                listingid        date               segment  period_enddate  fiscal_period  calendar_period  currency  External Revenue   naics  Ticker
        0       407721464  2020-01-03    Consolidated Total      2019-11-24         2020Q2           2019Q4       USD          1019.200       5     LW
        1       407721464  2020-01-03                Retail      2019-11-24         2020Q2           2019Q4       USD           132.100  424420     LW
        2       407721464  2020-01-03                Global      2019-11-24         2020Q2           2019Q4       USD           539.600  424420     LW
        3       407721464  2020-01-03                 Other      2019-11-24         2020Q2           2019Q4       USD            42.600       2     LW
        4       407721464  2020-01-03         Segment Total      2019-11-24         2020Q2           2019Q4       USD          1019.200       1     LW
        ...           ...         ...                   ...             ...            ...              ...       ...               ...     ...    ...
        197964  313185297  2024-06-20         Segment Total      2024-04-30         2024Q4           2024Q1       USD          1413.029       1    GMS
        197965  313185297  2024-06-20  Geographic divisions      2024-04-30         2024Q4           2024Q1       USD          1381.533  238310    GMS
        197966  313185297  2024-06-20                 Other      2024-04-30         2024Q4           2024Q1       USD            31.496       2    GMS
        197967  313185297  2024-06-20    Consolidated Total      2024-04-30         2024Q4           2024Q1       USD          1413.029       5    GMS
        197968  313185297  2024-06-20  Geographic divisions      2024-04-30         2024Q4           2024Q1       USD          1381.533  423310    GMS
    """
    @_validate_args
    def __init__(
        self,
        dataitemid: int,
        period_type: _PeriodTypeLTMQSA,
        period_back: int = 0,
        preliminary: _FinancialPreliminaryType = "keep",
        currency: _CurrencyTypeWithReportTrade = "report",
        segment_classification: _SegmentClassification = None,
    ):
        super().__init__(**_get_params(vars()))

    @classmethod
    @_validate_args
    def dataitems(cls, search: str = None, package: str = None):
        """
        Usable data items for the segment data component.

        Parameters
        ----------
            search : str, default None
                | Search word for dataitems name, the search is case-insensitive.

            package : str, default None
                | Search word for package name, the search is case-insensitive.

        Returns
        -------
            pandas.DataFrame
                | Data items that belong to segment data component.

            Columns:

                - *datamodule*
                - *datacomponent*
                - *dataitemid*
                - *datadescription*

        Examples
        --------
            >>> segdi = ps.financial.segment.dataitems()
            >>> segdi[['dataitemid', 'dataitemname']]
            dataitemid                                     dataitemname
            0      104729                        Business Segments - CAPEX
            1      104730  Business Segments - Depreciation & Amortization
            2      104731                       Business Segments - EBITDA
            3      104732                          Business Segments - EBT
            4      104733                 Business Segments - Gross Profit
            5      104734           Business Segments - Income Tax Expense
            6      104735             Business Segments - Interest Expense
            7      104736                        Business Segments - NOPAT
            8      104737                   Business Segments - Net Income
        """
        return cls._dataitems(search=search, package=package)


class industry(_PrismFinancialDataComponent):
    """
    | Data that pertains to companies in specific indusry.
    | Default frequency is aperiodic daily.

    Parameters
    ----------
        dataitemid : int
            | Unique identifier for the different data item.

        period_type : str, {'A', 'Annual', 'SA', 'Semi-Annual', 'Quarterly', 'Q', 'Q-SA', 'LTM'}
            | Financial Period in which the financial statement results are reported.
            | A Financial Period can be of one of the following Period Types:

            - Annual period (A)
            - Semi-Annual (SA)
            - Quarterly period (Q)
            - Quarterly-Semi-Annual (Q-SA)
            - Last twelve months (LTM)

        period_back : int, default 0
            | Specifies the number of periods to go back from the latest financial data.
            | For example, a value of 0 retrieves the most recently released financial data, while a value of 1 retrieves the financial data from the previous period, and so on.

        preliminary : str, {'keep', 'ignore', 'null'}, default 'keep'
            - keep : keep preliminary data
            - ignore : ignore preliminary data

            .. admonition:: Note
                :class: note

                | If the 'ignore' option is chosen, preliminary reports are disregarded entirely, as if they never existed.
                |
                | Consequently, if a revision occurs on the same day as the preliminary report, the latest period (period 0) will continue to display the previous period of preliminary reporting, and it will not be updated until the official report is released.

            - null : nulled-out preliminary data

        currency : str, {'report', 'trade', ISO3 currency}, default 'report'
            | Desired currency for the financial data.

            - report : financial reporting currency for a given listing (i.e for Apple - USD, Tencent - CNY)
            - trade : trading currency for a given listing (i.e for Apple - USD, Tencent - HKD)
            - ISO3 currency : desired currency in ISO 4217 format (i.e USD, EUR, JPY, KRW, etc.)

            .. admonition:: Warning
                :class: warning

                | If a selected data item is not a currency value (i.e airplanes owned), the currency input will be ignored.
                | It will behave like parameter input currency=None

    Returns
    -------
        prism._PrismComponent

    Examples
    --------
        >>> industry = prism.financial.industry.dataitems()
        >>> industry[['dataitemid', 'dataitemname']]
           dataitemid                                     dataitemname
        0      104729                        Business Segments - CAPEX
        1      104730  Business Segments - Depreciation & Amortization
        2      104731                       Business Segments - EBITDA
        3      104732                          Business Segments - EBT
        4      104733                 Business Segments - Gross Profit
        5      104734           Business Segments - Income Tax Expense
        6      104735             Business Segments - Interest Expense
        7      104736                        Business Segments - NOPAT
        8      104737                   Business Segments - Net Income
        >>> seg = prism.financial.industry(104731, period_type='Q')
        >>> seg.get_data(universe='US Primary', startdate='2010-01-01', enddate='2015-01-01', shownid=['ticker'])
	          listingid        date  period_enddate  fiscal_period  calendar_period  currency  Average Price Per Backlog Order - Semiconductors  Ticker
        0	    2602239  2010-01-05      2009-11-29         2010Q2           2009Q4       USD                                              None     CAG
        1	    2628457  2010-01-05      2009-11-26         2010Q2           2009Q4       USD                                              None     MCS
        2	    2654558  2010-01-05      2009-11-27         2010Q3           2009Q4       USD                                              None     SCS
        3	    7909562  2010-01-05      2009-11-30         2009Q4           2009Q4       USD                                              None     SNX
        4	   38011619  2010-01-05      2009-11-30         2010Q1           2009Q4       USD                                              None     ZEP
        ...         ...         ...             ...            ...              ...       ...                                               ...     ...
        62570   2654558  2015-12-23      2015-11-27         2016Q3           2015Q4       USD                                              None     SCS
        62571   2658404  2015-12-23      2015-10-31         2015Q4           2015Q3       USD                                              None     TTC
        62572   2664585  2015-12-23      2015-11-28         2016Q1           2015Q4       USD                                              None     WGO
        62573   2609477  2015-12-30      2015-11-30         2016Q3           2015Q4       USD                                              None     EBF
        62574   2634533  2015-12-30      2015-10-31         2015Q4           2015Q3       USD                                              None     NRT
    """
    @_validate_args
    def __init__(
        self,
        dataitemid: int,
        period_type: _PeriodTypeLTMQSA,
        period_back: int = 0,
        preliminary: _FinancialPreliminaryType = "keep",
        currency: _CurrencyTypeWithReportTrade = "report",
    ):
        super().__init__(**_get_params(vars()))

    @classmethod
    @_validate_args
    def dataitems(cls, search: str = None, package: str = None):
        """
        Usable data items for the industry data component.

        Parameters
        ----------
            search : str, default None
                | Search word for dataitems name, the search is case-insensitive.

            package : str, default None
                | Search word for package name, the search is case-insensitive.

        Returns
        -------
            pandas.DataFrame
                | Data items that belong to industry data component.

            Columns:

                - *datamodule*
                - *datacomponent*
                - *dataitemid*
                - *datadescription*

        Examples
        --------
            >>> segdi = prism.financial.industry.dataitems()
            >>> segdi[['dataitemid', 'dataitemname']]
            dataitemid                                     dataitemname
            0      104729                        Business Segments - CAPEX
            1      104730  Business Segments - Depreciation & Amortization
            2      104731                       Business Segments - EBITDA
            3      104732                          Business Segments - EBT
            4      104733                 Business Segments - Gross Profit
            5      104734           Business Segments - Income Tax Expense
            6      104735             Business Segments - Interest Expense
            7      104736                        Business Segments - NOPAT
            8      104737                   Business Segments - Net Income
        """
        return cls._dataitems(search=search, package=package)


class ratio(_PrismFinancialDataComponent):
    """
    | Data that pertains to a ratio data in financial statement.
    | Default frequency is aperiodic daily.

    Parameters
    ----------
        dataitemid : int
            | Unique identifier for the different data item.

        period_type : str, {'A', 'Annual', 'SA', 'Semi-Annual', 'Quarterly', 'Q', 'Q-SA', 'LTM'}
            | Financial Period in which the financial statement results are reported.
            | A Financial Period can be of one of the following Period Types:

            - Annual period (A)
            - Semi-Annual (SA)
            - Quarterly period (Q)
            - Quarterly-Semi-Annual (Q-SA)
            - Last twelve months (LTM)

        period_back : int, default 0
            | Specifies the number of periods to go back from the latest financial data.
            | For example, a value of 0 retrieves the most recently released financial data, while a value of 1 retrieves the financial data from the previous period, and so on.

        preliminary : str, {'keep', 'ignore', 'null'}, default 'keep'
            - keep : keep preliminary data
            - ignore : ignore preliminary data

            .. admonition:: Note
                :class: note

                | If the 'ignore' option is chosen, preliminary reports are disregarded entirely, as if they never existed.
                |
                | Consequently, if a revision occurs on the same day as the preliminary report, the latest period (period 0) will continue to display the previous period of preliminary reporting, and it will not be updated until the official report is released.

            - null : nulled-out preliminary data

        currency : str, {'report', 'trade', ISO3 currency}, default 'report'
            | Desired currency for the financial data.

            - report : financial reporting currency for a given listing (i.e for Apple - USD, Tencent - CNY)
            - trade : trading currency for a given listing (i.e for Apple - USD, Tencent - HKD)
            - ISO3 currency : desired currency in ISO 4217 format (i.e USD, EUR, JPY, KRW, etc.)

            .. admonition:: Warning
                :class: warning

                | If a selected data item is not a currency value (i.e airplanes owned), the currency input will be ignored.
                | It will behave like parameter input currency=None

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
        >>> ratdi = ps.financial.ratio.dataitems()
        >>> ratdi[['dataitemid', 'dataitemname']]
             dataitemid                                       dataitemname
        0        104934                       Annualized Dividend Payout %
        1        104935                      Annualized Dividend Per Share
        2        104936                        Annualized Dividend Yield %
        3        104937    3 Yr. Compound Net Capital Expenditure Growth %
        4        104938    5 Yr. Compound Net Capital Expenditure Growth %
        ...         ...                                                ...
        303      112907                        Liabilities / Assets, Total
        304      113691                Net Working Capital / Total Revenue
        305      113692                 Net Working Capital / Total Assets
        306      113695                           Working Capital Turnover
        307      114803  Altman Z Score Using the Average Stock Informa...
        >>> rat = ps.financial.ratio(112907, period_type='Q')
        >>> rat.get_data(universe='US Primary', startdate='2010-01-01', enddate='2015-01-01', shownid=['ticker'])
              listingid        date  period_enddate  fiscal_period  calendar_period  Liabilities / Assets, Total  Ticker
        0       2602239  2010-01-05      2009-11-29         2010Q2           2009Q4                      56.6792     CAG
        1       2628457  2010-01-05      2009-11-26         2010Q2           2009Q4                      52.6851     MCS
        2       2654558  2010-01-05      2009-11-27         2010Q3           2009Q4                      57.4446     SCS
        3       7909562  2010-01-05      2009-11-30         2009Q4           2009Q4                      60.5395     SNX
        4      38011619  2010-01-05      2009-11-30         2010Q1           2009Q4                      52.7782     ZEP
        ...         ...         ...             ...            ...              ...                          ...     ...
        62570   2654558  2015-12-23      2015-11-27         2016Q3           2015Q4                      60.5615     SCS
        62571   2658404  2015-12-23      2015-10-31         2015Q4           2015Q3                      64.5486     TTC
        62572   2664585  2015-12-23      2015-11-28         2016Q1           2015Q4                      31.1913     WGO
        62573   2609477  2015-12-30      2015-11-30         2016Q3           2015Q4                      26.3062     EBF
        62574   2634533  2015-12-30      2015-10-31         2015Q4           2015Q3                      96.3959     NRT
    """
    @_validate_args
    def __init__(
        self,
        dataitemid: int,
        period_type: _PeriodTypeLTMQSA,
        period_back: int = 0,
        preliminary: _FinancialPreliminaryType = "keep",
        currency: _CurrencyTypeWithReportTrade = "report",
    ):
        super().__init__(**_get_params(vars()))

    @classmethod
    @_validate_args
    def dataitems(cls, search: str = None, package: str = None):
        """
        Usable data items for the ratio data component.

        Parameters
        ----------
            search : str, default None
                | Search word for dataitems name, the search is case-insensitive.

            package : str, default None
                | Search word for package name, the search is case-insensitive.

        Returns
        -------
            pandas.DataFrame
                | Data items that belong to ratio data component.

            Columns:

                - *datamodule*
                - *datacomponent*
                - *dataitemid*
                - *datadescription*

        Examples
        --------
            >>> ratdi = ps.financial.segment.dataitems()
            >>> ratdi[['dataitemid', 'dataitemname']]
                dataitemid                                       dataitemname
            0        104934                       Annualized Dividend Payout %
            1        104935                      Annualized Dividend Per Share
            2        104936                        Annualized Dividend Yield %
            3        104937    3 Yr. Compound Net Capital Expenditure Growth %
            4        104938    5 Yr. Compound Net Capital Expenditure Growth %
            ...         ...                                                ...
            303      112907                        Liabilities / Assets, Total
            304      113691                Net Working Capital / Total Revenue
            305      113692                 Net Working Capital / Total Assets
            306      113695                           Working Capital Turnover
            307      114803  Altman Z Score Using the Average Stock Informa...
        """
        return cls._dataitems(search=search, package=package)


class commitment(_PrismFinancialDataComponent):
    """
    | Data that pertains to a commitment related data (such as operating leases etc.) in financial statement.
    | Default frequency is aperiodic daily.

    Parameters
    ----------
        dataitemid : int
            | Unique identifier for the different data item.

        period_type : str, {'A', 'Annual', 'SA', 'Semi-Annual', 'Quarterly', 'Q', 'Q-SA', 'LTM'}
            | Financial Period in which the financial statement results are reported.
            | A Financial Period can be of one of the following Period Types:

            - Annual period (A)
            - Semi-Annual (SA)
            - Quarterly period (Q)
            - Quarterly-Semi-Annual (Q-SA)
            - Last twelve months (LTM)

        period_back : int, default 0
            | Specifies the number of periods to go back from the latest financial data.
            | For example, a value of 0 retrieves the most recently released financial data, while a value of 1 retrieves the financial data from the previous period, and so on.

        preliminary : str, {'keep', 'ignore', 'null'}, default 'keep'
            - keep : keep preliminary data
            - ignore : ignore preliminary data

            .. admonition:: Note
                :class: note

                | If the 'ignore' option is chosen, preliminary reports are disregarded entirely, as if they never existed.
                |
                | Consequently, if a revision occurs on the same day as the preliminary report, the latest period (period 0) will continue to display the previous period of preliminary reporting, and it will not be updated until the official report is released.

            - null : nulled-out preliminary data

        currency : str, {'report', 'trade', ISO3 currency}, default 'report'
            | Desired currency for the financial data.

            - report : financial reporting currency for a given listing (i.e for Apple - USD, Tencent - CNY)
            - trade : trading currency for a given listing (i.e for Apple - USD, Tencent - HKD)
            - ISO3 currency : desired currency in ISO 4217 format (i.e USD, EUR, JPY, KRW, etc.)

            .. admonition:: Warning
                :class: warning

                | If a selected data item is not a currency value (i.e airplanes owned), the currency input will be ignored.
                | It will behave like parameter input currency=None

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
        >>> comdi = ps.financial.commitment.dataitems()
        >>> comdi[['dataitemid', 'dataitemname']]
             dataitemid                               dataitemname
        0        104830     Capital Lease Payment Due, Current Yr.
        1        104831  Capital Lease Payment Due, Current Yr. +1
        2        104832  Capital Lease Payment Due, Current Yr. +2
        3        104833  Capital Lease Payment Due, Current Yr. +3
        4        104834  Capital Lease Payment Due, Current Yr. +4
        ...         ...                                        ...
        117      500282                     Year 1 - (Annual Only)
        118      500283                     Year 2 - (Annual Only)
        119      500284                     Year 3 - (Annual Only)
        120      500285                     Year 4 - (Annual Only)
        121      500286                     Year 5 - (Annual Only)

        >>> com = ps.financial.commitment(104830, period_type='Q')
        >>> com.get_data(universe='US Primary', startdate='2010-01-01', enddate='2015-01-01', shownid=['ticker'])
             listingid        date  period_enddate  fiscal_period  calendar_period  currency  Long Term Debt Maturing in 4-5 Years  Ticker
        0      2619773  2010-01-05      2009-11-30         2010Q2           2009Q4       USD                                   NaN     IGL
        1      7909562  2010-01-05      2009-11-30         2009Q4           2009Q4       USD                                   NaN     SNX
        2     38011619  2010-01-05      2009-11-30         2010Q1           2009Q4       USD                                   NaN     ZEP
        3      2586910  2010-01-06      2009-11-30         2010Q1           2009Q4       USD                                   NaN     AYI
        4      2611056  2010-01-06      2009-11-28         2010Q1           2009Q4       USD                                   NaN     FDO
        ...        ...         ...             ...            ...              ...       ...                                   ...     ...
        34337  2602239  2015-12-22      2015-11-29         2016Q2           2015Q4       USD                           775000000.0     CAG
        34338  2609477  2015-12-22      2015-11-30         2016Q3           2015Q4       USD                                   NaN     EBF
        34339  2634146  2015-12-22      2015-11-30         2016Q2           2015Q4       USD                                   NaN     NKE
        34340  2626876  2015-12-23      2015-11-30         2016Q1           2015Q4       USD                              416000.0     LNN
        34341  2639161  2015-12-23      2015-10-31         2015Q4           2015Q3       USD                                   NaN     PNY
    """
    @_validate_args
    def __init__(
        self,
        dataitemid: int,
        period_type: _PeriodTypeLTMQSA,
        period_back: int = 0,
        preliminary: _FinancialPreliminaryType = "keep",
        currency: _CurrencyTypeWithReportTrade = "report",
    ):
        super().__init__(**_get_params(vars()))

    @classmethod
    @_validate_args
    def dataitems(cls, search: str = None, package: str = None):
        """
        Usable data items for the commitment data component.

        Parameters
        ----------
            search : str, default None
                | Search word for dataitems name, the search is case-insensitive.

            package : str, default None
                | Search word for package name, the search is case-insensitive.

        Returns
        -------
            pandas.DataFrame
                | Data items that belong to commitment data component.

            Columns:

                - *datamodule*
                - *datacomponent*
                - *dataitemid*
                - *datadescription*

        Examples
        --------
            >>> comdi = ps.financial.commitment.dataitems()
            >>> comdi[['dataitemid', 'dataitemname']]
                dataitemid                               dataitemname
            0        104830     Capital Lease Payment Due, Current Yr.
            1        104831  Capital Lease Payment Due, Current Yr. +1
            2        104832  Capital Lease Payment Due, Current Yr. +2
            3        104833  Capital Lease Payment Due, Current Yr. +3
            4        104834  Capital Lease Payment Due, Current Yr. +4
            ...         ...                                        ...
            117      500282                     Year 1 - (Annual Only)
            118      500283                     Year 2 - (Annual Only)
            119      500284                     Year 3 - (Annual Only)
            120      500285                     Year 4 - (Annual Only)
            121      500286                     Year 5 - (Annual Only)
        """
        return cls._dataitems(search=search, package=package)


class pension(_PrismFinancialDataComponent):
    """
    | Data that pertains to a pension related data in financial statement.
    | Default frequency is aperiodic daily.

    Parameters
    ----------
        dataitemid : int
            | Unique identifier for the different data item.

        period_type : str, {'A', 'Annual', 'SA', 'Semi-Annual', 'Quarterly', 'Q', 'Q-SA', 'LTM'}
            | Financial Period in which the financial statement results are reported.
            | A Financial Period can be of one of the following Period Types:

            - Annual period (A)
            - Semi-Annual (SA)
            - Quarterly period (Q)
            - Quarterly-Semi-Annual (Q-SA)
            - Last twelve months (LTM)

        period_back : int, default 0
            | Specifies the number of periods to go back from the latest financial data.
            | For example, a value of 0 retrieves the most recently released financial data, while a value of 1 retrieves the financial data from the previous period, and so on.

        preliminary : str, {'keep', 'ignore', 'null'}, default 'keep'
            - keep : keep preliminary data
            - ignore : ignore preliminary data

            .. admonition:: Note
                :class: note

                | If the 'ignore' option is chosen, preliminary reports are disregarded entirely, as if they never existed.
                |
                | Consequently, if a revision occurs on the same day as the preliminary report, the latest period (period 0) will continue to display the previous period of preliminary reporting, and it will not be updated until the official report is released.

            - null : nulled-out preliminary data

        currency : str, {'report', 'trade', ISO3 currency}, default 'report'
            | Desired currency for the financial data.

            - report : financial reporting currency for a given listing (i.e for Apple - USD, Tencent - CNY)
            - trade : trading currency for a given listing (i.e for Apple - USD, Tencent - HKD)
            - ISO3 currency : desired currency in ISO 4217 format (i.e USD, EUR, JPY, KRW, etc.)

            .. admonition:: Warning
                :class: warning

                | If a selected data item is not a currency value (i.e airplanes owned), the currency input will be ignored.
                | It will behave like parameter input currency=None

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
        >>> pendi = ps.financial.pension.dataitems()
        >>> pendi[['dataitemid', 'dataitemname']]
             dataitemid                                       dataitemname
        0        100299                          Minimum Pension Liability
        1        100370    Un-funded Vested Pension Liabilities - Domestic
        2        100371     Un-funded Vested Pension Liabilities - Foreign
        3        100741  Expected Rate of Return on Pension Assets - Do...
        4        100742  Expected Rate of Return on Pension Assets - Fo...
        ...         ...                                                ...
        592      500346              Net Liability/(Asset) - (Annual Only)
        593      500347               Unfunded Liabilities - (Annual Only)
        594      500348     Expected Return on Plan Assets - (Annual Only)
        595      500349       Actual Return on Plan Assets - (Annual Only)
        596      500350  Expected LT Return Rate on Plan Assets (%) - (...
        >>> pen = ps.financial.pension(100370, period_type='Q')
        >>> pen.get_data(universe='US Primary', startdate='2010-01-01', enddate='2015-01-01', shownid=['ticker'])
             listingid        date  period_enddate  fiscal_period  calendar_period  currency  Un-funded Vested Pension Liabilities - Domestic  Ticker
        0      2602239  2010-01-05      2009-11-29         2010Q2           2009Q4       USD                                              NaN     CAG
        1      2628457  2010-01-05      2009-11-26         2010Q2           2009Q4       USD                                              NaN     MCS
        2      2654558  2010-01-05      2009-11-27         2010Q3           2009Q4       USD                                              NaN     SCS
        3      7909562  2010-01-05      2009-11-30         2009Q4           2009Q4       USD                                              NaN     SNX
        4     38011619  2010-01-05      2009-11-30         2010Q1           2009Q4       USD                                              NaN     ZEP
        ...        ...         ...             ...            ...              ...       ...                                              ...     ...
        62570  2654558  2015-12-23      2015-11-27         2016Q3           2015Q4       USD                                              NaN     SCS
        62571  2658404  2015-12-23      2015-10-31         2015Q4           2015Q3       USD                                              NaN     TTC
        62572  2664585  2015-12-23      2015-11-28         2016Q1           2015Q4       USD                                              NaN     WGO
        62573  2609477  2015-12-30      2015-11-30         2016Q3           2015Q4       USD                                              NaN     EBF
        62574  2634533  2015-12-30      2015-10-31         2015Q4           2015Q3       USD                                              NaN     NRT
    """
    @_validate_args
    def __init__(
        self,
        dataitemid: int,
        period_type: _PeriodTypeLTMQSA,
        period_back: int = 0,
        preliminary: _FinancialPreliminaryType = "keep",
        currency: _CurrencyTypeWithReportTrade = "report",
    ):
        super().__init__(**_get_params(vars()))

    @classmethod
    @_validate_args
    def dataitems(cls, search: str = None, package: str = None):
        """
        Usable data items for the pension data component.

        Parameters
        ----------
            search : str, default None
                | Search word for dataitems name, the search is case-insensitive.

            package : str, default None
                | Search word for package name, the search is case-insensitive.

        Returns
        -------
            pandas.DataFrame
                | Data items that belong to pension data component.

            Columns:

                - *datamodule*
                - *datacomponent*
                - *dataitemid*
                - *datadescription*

        Examples
        --------
            >>> pendi = ps.financial.pension.dataitems()
            >>> pendi[['dataitemid', 'dataitemname']]
                dataitemid                                       dataitemname
            0        100299                          Minimum Pension Liability
            1        100370    Un-funded Vested Pension Liabilities - Domestic
            2        100371     Un-funded Vested Pension Liabilities - Foreign
            3        100741  Expected Rate of Return on Pension Assets - Do...
            4        100742  Expected Rate of Return on Pension Assets - Fo...
            ...         ...                                                ...
            592      500346              Net Liability/(Asset) - (Annual Only)
            593      500347               Unfunded Liabilities - (Annual Only)
            594      500348     Expected Return on Plan Assets - (Annual Only)
            595      500349       Actual Return on Plan Assets - (Annual Only)
            596      500350  Expected LT Return Rate on Plan Assets (%) - (...
        """
        return cls._dataitems(search=search, package=package)


class option(_PrismFinancialDataComponent):
    """
    | Data that pertains to a options and warrants related data in financial statement.
    | Default frequency is aperiodic daily.

    Parameters
    ----------
        dataitemid : int
            | Unique identifier for the different data item.

        period_type : str, {'A', 'Annual', 'SA', 'Semi-Annual', 'Quarterly', 'Q', 'Q-SA', 'LTM'}
            | Financial Period in which the financial statement results are reported.
            | A Financial Period can be of one of the following Period Types:

            - Annual period (A)
            - Semi-Annual (SA)
            - Quarterly period (Q)
            - Quarterly-Semi-Annual (Q-SA)
            - Last twelve months (LTM)

        period_back : int, default 0
            | Specifies the number of periods to go back from the latest financial data.
            | For example, a value of 0 retrieves the most recently released financial data, while a value of 1 retrieves the financial data from the previous period, and so on.

        preliminary : str, {'keep', 'ignore', 'null'}, default 'keep'
            - keep : keep preliminary data
            - ignore : ignore preliminary data

            .. admonition:: Note
                :class: note

                | If the 'ignore' option is chosen, preliminary reports are disregarded entirely, as if they never existed.
                |
                | Consequently, if a revision occurs on the same day as the preliminary report, the latest period (period 0) will continue to display the previous period of preliminary reporting, and it will not be updated until the official report is released.

            - null : nulled-out preliminary data

        currency : str, {'report', 'trade', ISO3 currency}, default 'report'
            | Desired currency for the financial data.

            - report : financial reporting currency for a given listing (i.e for Apple - USD, Tencent - CNY)
            - trade : trading currency for a given listing (i.e for Apple - USD, Tencent - HKD)
            - ISO3 currency : desired currency in ISO 4217 format (i.e USD, EUR, JPY, KRW, etc.)

            .. admonition:: Warning
                :class: warning

                | If a selected data item is not a currency value (i.e airplanes owned), the currency input will be ignored.
                | It will behave like parameter input currency=None

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
        >>> optdi = ps.financial.option.dataitems()
        >>> optdi[['dataitemid', 'dataitemname']]
             dataitemid                                       dataitemname
        0        100668                       Average Price paid per Share
        1        100883                  Shares Purchased - Quarter, Total
        2        104885                       Stock Options Exercise Price
        3        104886                          Stock Options Grant Price
        4        104898  Stock Options Outstanding At The Beginning of ...
        ...         ...                                                ...
        109      107688    Exercisable Warrants W / Average Exercise Price
        110      107689  Exercisable Warrants W / Average Remaining Lif...
        111      107690     Outstanding Warrants Aggregate Intrinsic Value
        112      107691     Exercisable Warrants Aggregate Intrinsic Value
        113      107693                             Stock Option Plan Name
        >>> opt = ps.financial.option(100668, period_type='Q')
        >>> opt.get_data(universe=1, startdate='2010-01-01', enddate='2015-01-01', shownid=['ticker'])
             listingid        date  period_enddate  fiscal_period  calendar_period  Number of Exercisable Options  Ticker
        0      2602239  2010-01-05      2009-11-29         2010Q2           2009Q4                           None     CAG
        1      2628457  2010-01-05      2009-11-26         2010Q2           2009Q4                           None     MCS
        2      2654558  2010-01-05      2009-11-27         2010Q3           2009Q4                           None     SCS
        3      7909562  2010-01-05      2009-11-30         2009Q4           2009Q4                           None     SNX
        4     38011619  2010-01-05      2009-11-30         2010Q1           2009Q4                           None     ZEP
        ...        ...         ...             ...            ...              ...                            ...     ...
        62570  2654558  2015-12-23      2015-11-27         2016Q3           2015Q4                           None     SCS
        62571  2658404  2015-12-23      2015-10-31         2015Q4           2015Q3                           None     TTC
        62572  2664585  2015-12-23      2015-11-28         2016Q1           2015Q4                           None     WGO
        62573  2609477  2015-12-30      2015-11-30         2016Q3           2015Q4                           None     EBF
        62574  2634533  2015-12-30      2015-10-31         2015Q4           2015Q3                           None     NRT
    """
    @_validate_args
    def __init__(
        self,
        dataitemid: int,
        period_type: _PeriodTypeLTMQSA,
        period_back: int = 0,
        preliminary: _FinancialPreliminaryType = "keep",
        currency: _CurrencyTypeWithReportTrade = "report",
    ):
        super().__init__(**_get_params(vars()))

    @classmethod
    @_validate_args
    def dataitems(cls, search: str = None, package: str = None):
        """
        Usable data items for the option data component.

        Parameters
        ----------
            search : str, default None
                | Search word for dataitems name, the search is case-insensitive.

            package : str, default None
                | Search word for package name, the search is case-insensitive.

        Returns
        -------
            pandas.DataFrame
                | Data items that belong to option data component.

            Columns:

                - *datamodule*
                - *datacomponent*
                - *dataitemid*
                - *datadescription*

        Examples
        --------
            >>> optdi = ps.financial.option.dataitems()
            >>> optdi[['dataitemid', 'dataitemname']]
                dataitemid                                       dataitemname
            0        100668                       Average Price paid per Share
            1        100883                  Shares Purchased - Quarter, Total
            2        104885                       Stock Options Exercise Price
            3        104886                          Stock Options Grant Price
            4        104898  Stock Options Outstanding At The Beginning of ...
            ...         ...                                                ...
            109      107688    Exercisable Warrants W / Average Exercise Price
            110      107689  Exercisable Warrants W / Average Remaining Lif...
            111      107690     Outstanding Warrants Aggregate Intrinsic Value
            112      107691     Exercisable Warrants Aggregate Intrinsic Value
            113      107693                             Stock Option Plan Name
        """
        return cls._dataitems(search=search, package=package)


@_validate_args
def dataitems(search: str = None, package: str = None):
    """
    Usable data items for the financial data category.

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
    >>> ps.financial.dataitems('revenue')
        dataitemid  ...                                dataitemdescription
    0       100044  ...  This item represents revenues, which are recei...
    1       100053  ...  This item represents revenues which are receiv...
    2       100196  ...  This item represents revenues relating to peri...
    3       100228  ...  This item represents the portion of realized r...
    4       100263  ...  This item represents the bonds which are issue...
    5       100408  ...  This item represents change in revenues relati...
    6       100483  ...                                From AP Tag CFURXNC
    7       100579  ...                                  Revenue Per Share
    8       100580  ...  This item represents the total revenues that a...
    9       100581  ...                                               None
    10      100582  ...  This item represents the revenues generated by...
    11      100583  ...  This item represents revenues generated by the...
    """
    return _list_dataitem(
            datacategoryid=_PrismFinancialDataComponent.categoryid,
            datacomponentid=None,
            search=search,
            package=package,
        )
