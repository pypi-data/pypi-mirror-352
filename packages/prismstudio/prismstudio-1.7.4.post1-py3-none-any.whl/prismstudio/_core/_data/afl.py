from ..._prismcomponent.prismcomponent import _PrismComponent, _PrismDataComponent
from .._req_builder import _list_dataitem
from ..._utils import _validate_args, _get_params

__all__ = ['analyst_expectations', 'capital_efficiency', 'historical_growth', 'valuation', 'volatility', 'size', 'capital_efficiency', 'price_momentum','dataitems']


_data_category = __name__.split(".")[-1]

class _PrismAFLComponent(_PrismDataComponent, _PrismComponent):
    _component_category_repr = _data_category

    @classmethod
    def _dataitems(cls, search : str = None, package : str = None):
        return _list_dataitem(
            datacategoryid=cls.categoryid,
            datacomponentid=cls.componentid,
            search=search,
            package=package,
        )


@_validate_args
class analyst_expectations(_PrismAFLComponent):
    """
    | Pre-calculated factor dataset provided by S&P Global Market Intelligence.
    | Default frequency is monthly.

    Parameters
    ----------
        dataitemid : int
            | Unique identifier for the different data item. This identifies the type of the value (Revenue, Expense, etc.)

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
    """

    _component_category_repr = _data_category

    @_validate_args
    def __init__(self, dataitemid: int): super().__init__(**_get_params(vars()))

    @classmethod
    @_validate_args
    def dataitems(cls, search: str = None):
        return cls._dataitems(search=search, package=None)


@_validate_args
class capital_efficiency(_PrismComponent, _PrismDataComponent):
    """
    | Pre-calculated factor dataset provided by S&P Global Market Intelligence.
    | Default frequency is monthly.


    Parameters
    ----------
        dataitemid : int
            | Unique identifier for the different data item. This identifies the type of the value (Revenue, Expense, etc.)

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
    """

    _component_category_repr = _data_category

    @_validate_args
    def __init__(self, dataitemid: int): super().__init__(**_get_params(vars()))

    @classmethod
    @_validate_args
    def dataitems(cls, search: str = None):
        return cls._dataitems(search=search, package=None)


@_validate_args
class historical_growth(_PrismComponent, _PrismDataComponent):
    """
    | Pre-calculated factor dataset provided by S&P Global Market Intelligence.
    | Default frequency is monthly.


    Parameters
    ----------
        dataitemid : int
            | Unique identifier for the different data item. This identifies the type of the value (Revenue, Expense, etc.)

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
    """

    _component_category_repr = _data_category

    @_validate_args
    def __init__(self, dataitemid: int): super().__init__(**_get_params(vars()))

    @classmethod
    @_validate_args
    def dataitems(cls, search: str = None):
        return cls._dataitems(search=search, package=None)


@_validate_args
class price_momentum(_PrismComponent, _PrismDataComponent):
    """
    | Pre-calculated factor dataset provided by S&P Global Market Intelligence.
    | Default frequency is monthly.


    Parameters
    ----------
        dataitemid : int
            | Unique identifier for the different data item. This identifies the type of the value (Revenue, Expense, etc.)

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
    """

    _component_category_repr = _data_category

    @_validate_args
    def __init__(self, dataitemid: int): super().__init__(**_get_params(vars()))

    @classmethod
    @_validate_args
    def dataitems(cls, search: str = None):
        return cls._dataitems(search=search, package=None)


@_validate_args
class earnings_quality(_PrismComponent, _PrismDataComponent):
    """
    | Pre-calculated factor dataset provided by S&P Global Market Intelligence.
    | Default frequency is monthly.


    Parameters
    ----------
        dataitemid : int
            | Unique identifier for the different data item. This identifies the type of the value (Revenue, Expense, etc.)

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
    """

    _component_category_repr = _data_category

    @_validate_args
    def __init__(self, dataitemid: int): super().__init__(**_get_params(vars()))

    @classmethod
    @_validate_args
    def dataitems(cls, search: str = None):
        return cls._dataitems(search=search, package=None)


@_validate_args
class size(_PrismComponent, _PrismDataComponent):
    """
    | Pre-calculated factor dataset provided by S&P Global Market Intelligence.
    | Default frequency is monthly.


    Parameters
    ----------
        dataitemid : int
            | Unique identifier for the different data item. This identifies the type of the value (Revenue, Expense, etc.)

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
    """

    _component_category_repr = _data_category

    @_validate_args
    def __init__(self, dataitemid: int): super().__init__(**_get_params(vars()))

    @classmethod
    @_validate_args
    def dataitems(cls, search: str = None):
        return cls._dataitems(search=search, package=None)


@_validate_args
class valuation(_PrismComponent, _PrismDataComponent):
    """
    | Pre-calculated factor dataset provided by S&P Global Market Intelligence.
    | Default frequency is monthly.


    Parameters
    ----------
        dataitemid : int
            | Unique identifier for the different data item. This identifies the type of the value (Revenue, Expense, etc.)

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
    """

    _component_category_repr = _data_category

    @_validate_args
    def __init__(self, dataitemid: int): super().__init__(**_get_params(vars()))

    @classmethod
    @_validate_args
    def dataitems(cls, search: str = None):
        return cls._dataitems(search=search, package=None)


@_validate_args
class volatility(_PrismComponent, _PrismDataComponent):
    """
    | Pre-calculated factor dataset provided by S&P Global Market Intelligence.
    | Default frequency is quarterly.


    Parameters
    ----------
        dataitemid : int
            | Unique identifier for the different data item. This identifies the type of the value (Revenue, Expense, etc.)

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
    """

    _component_category_repr = _data_category

    @_validate_args
    def __init__(self, dataitemid: int): super().__init__(**_get_params(vars()))

    @classmethod
    @_validate_args
    def dataitems(cls, search: str = None):
        return cls._dataitems(search=search, package=None)


def dataitems(search: str = None):
    """
    Usable data items for the Alpha Factor Library data category.

    Parameters
    ----------
        search : str, default None
            | Search word for dataitems name, the search is case-insensitive.

    Returns
    -------
        pandas.DataFrame
            Data items that belong to alpha factor library data components.

        Columns:
            - *datamodule*
            - *datacomponent*
            - *dataitemid*
            - *datadescription*

    Examples
    --------
        >>> di = ps.afl.dataitems("Debt")
        >>> di[['dataitemid', 'dataitemname']]
           dataitemid                                       dataitemname
        0      900033  1-Year Change in Long Term Debt to Avg Total A...
        1      900059                           1Y Chg in Debt to Assets
        2      900145       5 Yr Hist Rel Long Term Debt to Assets Ratio
        3      900279                               Debt to Assets Ratio
        4      900366                   Ind Grp Rel Debt to Assets Ratio
        5      900388         Ind Grp Rel Long Term Debt to Assets Ratio
        6      900389         Ind Grp Rel Long Term Debt to Equity Ratio
        7      900425    Ind Grp Rel Year over Year Change of Total Debt
        8      900451                     Long Term Debt to Assets Ratio
        9      900452                     Long Term Debt to Equity Ratio
        10     900644                Year over Year Change of Total Debt
    """
    return _list_dataitem(
        datacategoryid=_PrismAFLComponent.categoryid,
        datacomponentid=None,
        search=search,
        package=None,
    )


