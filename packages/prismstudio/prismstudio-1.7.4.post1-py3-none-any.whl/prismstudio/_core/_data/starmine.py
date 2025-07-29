from ..._prismcomponent.prismcomponent import _PrismDataComponent, _PrismComponent
from .._req_builder import _list_dataitem
from ..._utils import _validate_args, _get_params
from ..._common.const import StarminePeriodType as _PeriodType


__all__ = ['analyst_revision', 'earnings_quality', 'intrinsic_value', 'price_momentum', 'smart_holding', 'dataitems']


_data_category = __name__.split(".")[-1]


class _PrismStarMineComponent(_PrismDataComponent, _PrismComponent):
    _component_category_repr = _data_category

    @classmethod
    def _dataitems(cls, search : str = None, package : str = None):
        return _list_dataitem(
            datacategoryid=cls.categoryid,
            datacomponentid=cls.componentid,
            search=search,
            package=package,
        )


class analyst_revision(_PrismStarMineComponent):
    """
    The StarMine Analyst Revisions Model predicts future changes in analyst sentiment by incorporating StarMine’s proprietary SmartEstimate service, multiple fiscal periods, other financial measures beyond earnings, and analyst recommendation changes.
    It places greater weight on the most accurate analysts and the most recent revisions, combining multiple dimensions of analyst activity to provide a more holistic portrait of sentiment.

    Parameters
    ----------
        dataitemid : int
            | Unique identifier for the different data item. This identifies the type of the value.

        period_type : str, {'A', 'Q', 'NTM', None}
            | Estimate Period in which the StarMine used to calculate its dataitems.
            | analyst_revision's period_type can be of one of the followings:

            - Annual period (A)
            - Quarterly period (Q)
            - Next twelve months (NTM)
            - Non-Periodic (None)

        period_forward : int
            | Determines how far out estimate to fetch.
            | For example, inputting 0 will fetch estimate data for the current period, 1 will fetch estimate for the next period.

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
    """
    @_validate_args
    def __init__(self, dataitemid: int, period_type: _PeriodType=None, period_forward: int = None): super().__init__(**_get_params(vars()))

    @classmethod
    @_validate_args
    def dataitems(cls, search: str = None):
        return cls._dataitems(search=search, package=None)


class earnings_quality(_PrismStarMineComponent):
    """
    The StarMine Earnings Quality Model uses a multi-factor approach to determine how sustainable a company’s earnings are, incorporating measures such as accruals, cash flow, operating efficiency, and the alignment between pro-forma and GAAP earnings.
    By emphasizing earnings backed by solid cash flow and penalizing those driven by less sustainable factors, the model more reliably predicts the persistence of earnings.
    This framework provides an objective comparison of a company’s earnings quality relative to its peers.

    Parameters
    ----------
        dataitemid : int
            | Unique identifier for the different data item. This identifies the type of the value.

        period_type : str, {'A', 'Q', 'LTM'}
            | Fiscal Period in which StarMine used to calculate the factor in the financial statement results are reported.
            | earnings_quality's period_type can be of one of the followings:

            - Annual period (A)
            - Quarterly period (Q)
            - Last twelve months (LTM)

        period_back : int, default 0
            | Specifies the number of periods to go back from the latest starmine(financial) data.
            | For example, a value of 0 retrieves the most recently released starmine(financial) data, while a value of 1 retrieves the starmine(financial) data from the previous period, and so on.

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
    """

    @_validate_args
    def __init__(self, dataitemid: int, period_type: _PeriodType=None, period_back: int = None): super().__init__(**_get_params(vars()))

    @classmethod
    @_validate_args
    def dataitems(cls, search: str = None):
        return cls._dataitems(search=search, package=None)


class intrinsic_value(_PrismStarMineComponent):
    """
    The StarMine Analyst Revisions Model predicts future changes in analyst sentiment by incorporating StarMine’s proprietary SmartEstimate service, multiple fiscal periods, other financial measures beyond earnings, and analyst recommendation changes.
    It places greater weight on the most accurate analysts and the most recent revisions, combining multiple dimensions of analyst activity to provide a more holistic portrait of sentiment.

    Parameters
    ----------
        dataitemid : int
            | Unique identifier for the different data item. This identifies the type of the value.

        period_type : str, {'A', 'Q', 'NTM', None}
            | Estimate Period in which the StarMine used to calculate its dataitems.
            | analyst_revision's period_type can be of one of the followings:

            - Annual period (A)
            - Quarterly period (Q)
            - Next twelve months (NTM)
            - Non-Periodic (None)

        period_forward : int
            | Determines how far out estimate to fetch.
            | For example, inputting 0 will fetch estimate data for the current period, 1 will fetch estimate for the next period.

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
    """

    @_validate_args
    def __init__(self, dataitemid: int, period_type: _PeriodType=None, period_forward: int = None): super().__init__(**_get_params(vars()))

    @classmethod
    @_validate_args
    def dataitems(cls, search: str = None):
        return cls._dataitems(search=search, package=None)


class price_momentum(_PrismStarMineComponent):
    """
    The StarMine Price Momentum Model captures both the tendency of long-term price trends to continue and the tendency of short-term trends to revert.
    It combines short-, mid-, and long-term momentum indicators, accounts for industry-level price movement, and factors in consistency or volatility of returns.
    This balanced approach provides a more nuanced view of price trends and makes the model responsive to turnaround situations.

    Parameters
    ----------
        dataitemid : int
            | Unique identifier for the different data item. This identifies the type of the value.

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
    """
    @_validate_args
    def __init__(self, dataitemid: int): super().__init__(**_get_params(vars()))

    @classmethod
    @_validate_args
    def dataitems(cls, search: str = None):
        return cls._dataitems(search=search, package=None)


class smart_holding(_PrismStarMineComponent):
    """
    The StarMine Smart Holdings Model predicts future changes in institutional ownership by identifying which fundamental factors are driving fund managers’ current buying and selling decisions.
    Through reverse-engineering each manager’s purchasing profile and blending peer information, it pinpoints which stocks are increasingly aligned or misaligned with prevailing preferences.
    By moving beyond delayed regulatory filings and incorporating real-time data, it more accurately forecasts upcoming increases or decreases in institutional holdings.

    Parameters
    ----------
        dataitemid : int
            | Unique identifier for the different data item. This identifies the type of the value.

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
    """

    @_validate_args
    def __init__(self, dataitemid: int): super().__init__(**_get_params(vars()))

    @classmethod
    @_validate_args
    def dataitems(cls, search: str = None):
        return cls._dataitems(search=search, package=None)


@_validate_args
def dataitems(search: str = None):
    return _list_dataitem(
        datacategoryid=_PrismStarMineComponent.categoryid,
        datacomponentid=None,
        search=search,
        package=None,
    )
