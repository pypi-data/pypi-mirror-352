from .._req_builder import _list_dataitem
from ..._common.const import CompanyRelAttributeType as _CompanyRelAttributeType
from ..._prismcomponent.prismcomponent import _PrismComponent, _PrismDataComponent
from ..._utils import _get_params, _validate_args
from ..._utils.exceptions import PrismValueError


__all__ = [
    "economics"
]

_data_category = __name__.split(".")[-1]

class _PrismEconomicsComponent(_PrismDataComponent, _PrismComponent):
    _component_category_repr = _data_category

    @classmethod
    def _dataitems(cls, search : str = None, package : str = None):
        return _list_dataitem(
            datacategoryid=cls.categoryid,
            datacomponentid=cls.componentid,
            search=search,
            package=package,
        )


class economics(_PrismEconomicsComponent):
    """
    | Data that pertains to a balance sheet portion in financial statement.
    | Default frequency is aperiodic daily.

    Parameters
    ----------
        dataitemid : int or list of int
            Unique identifier for the different data item. This identifies the type of the economic indicator.

        period_back : int, default 0
            | Specifies the number of periods to go back from the latest economic release.
            | For example, a value of 0 retrieves the most recently released economic data, while a value of 1 retrieves the economic data from the previous period, and so on.

    Notes
    -----
    **Warning:** Providing a list of dataitemid or setting period_back=None will result in an inoperable query. Such a query can only be used with the get_data function.

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
        >>> unit_labor_cost = ps.economics.economics(dataitemid=4137231, period_back=0)
        >>> ulc_df = unit_labor_cost.get_data('2010-01-01')
        >>>  ulc_df
                  date period_enddate    value   unit
        0   2010-02-04     2009-10-01  124.438  Index
        1   2010-03-04     2009-10-01  122.089  Index
        2   2010-05-06     2010-01-01  121.702  Index
        3   2010-06-03     2010-01-01  121.085  Index
        4   2010-08-10     2010-04-01  103.724  Index
        ..         ...            ...      ...    ...
        121 2024-08-01     2024-04-01  120.394  Index
        122 2024-09-05     2024-04-01  120.245  Index
        123 2024-09-06     2024-04-01  120.245  Index
        124 2024-11-07     2024-07-01  121.983  Index
        125 2024-11-13     2024-07-01  121.983  Index
    """
    @_validate_args
    def __init__(
        self,
        dataitemid: int | list,
        period_back: int = 0
    ):
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
            >>> ps.economics.economics.dataitems('UNIT LABOR')
                 dataitemid  ...                                dataitemdescription
            0       4000996  ...  Dataitem Type: Price index, NSA\nSource: Inter...
            1       4000997  ...  Dataitem Type: Price index, NSA\nSource: Inter...
            2       4000998  ...  Dataitem Type: Price index, NSA\nSource: Inter...
            3       4001068  ...  Dataitem Type: Price index, NSA\nSource: Inter...
            4       4001069  ...  Dataitem Type: Price index, NSA\nSource: Inter...
            ..          ...  ...                                                ...
            241     4194139  ...  Dataitem Type: Price index, NSA\nSource: Inter...
            242     4194273  ...  Dataitem Type: Price index, NSA\nSource: Inter...
            243     4195068  ...  Dataitem Type: Price index, NSA\nSource: Inter...
            244     4195123  ...  Dataitem Type: Price index, NSA\nSource: Inter...
            245     4195345  ...  Dataitem Type: Price index, NSA\nSource: Inter...

        """
        return cls._dataitems(search=search, package=package)
