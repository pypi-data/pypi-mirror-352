import pandas as pd

from .._req_builder import _list_dataitem, _dataquery
from ..._prismcomponent.prismcomponent import _PrismComponent, _PrismDataComponent
from ..._utils import _validate_args, _get_params, _req_call

__all__ = [
    "share",
    "weight",
    "level",
    "universe_dataitems",
    "portfolio_dataitems",
    "dataitems",
]


_data_category = __name__.split(".")[-1]


class _PrismIndexComponent(_PrismDataComponent, _PrismComponent):
    _component_category_repr = _data_category

    @classmethod
    def _dataitems(cls, search: str = None, package: str = None):
        ret = _list_dataitem(
            datacategoryid=cls.categoryid,
            datacomponentid=cls.componentid,
            search=search,
            package=package,
        )
        ret = ret.drop(["dataitemdescription"], axis=1, errors="ignore")
        return ret

    @_validate_args
    @_req_call(_dataquery)
    def get_data(self, startdate: str = None, enddate: str = None, shownid = None, name = None,) -> pd.DataFrame:
        pass


class share(_PrismIndexComponent):
    """
    | Index constituent share data.
    | Default frequency is business daily.

    Parameters
    ----------
        dataitemid : int
            | Unique identifier for the different data item. This identifies the type of the index (S&P 500, FTSE 200, etc.)

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
        >>> di = ps.index.share.dataitems("Russell 3000 Index")
        >>> di[["dataitemid", "dataitemname"]]
           dataitemid        dataitemname
        0     4000099  Russell 3000 Index

        >>> rus = ps.index.share(4000099)
        >>> rus_df = rus.get_data(startdate='2010-01-01', enddate='2020-12-31', shownid=["Company Name"])
        >>> rus_df
                 listingid        date	     value	         Company Name
        0          2598345  2012-06-25  15863000.0  CARRIAGE SERVICES INC
        1          2598345  2012-06-26  15863000.0  CARRIAGE SERVICES INC
        2          2598345  2012-06-27  15863000.0  CARRIAGE SERVICES INC
        3          2598345  2012-06-28  15863000.0  CARRIAGE SERVICES INC
        4          2598345  2012-06-29  15863000.0  CARRIAGE SERVICES INC
        ...            ...         ...         ...                    ...
        2810518  403068703  2014-06-30  16860000.0   TRI POINTE HOMES INC
        2810519  403068703  2014-07-01  16860000.0   TRI POINTE HOMES INC
        2810520  403068703  2014-07-02  16860000.0   TRI POINTE HOMES INC
        2810521  403068703  2014-07-03  16860000.0   TRI POINTE HOMES INC
        2810522  403068703  2014-07-07  16860000.0   TRI POINTE HOMES INC
    """
    @_validate_args
    def __init__(self, dataitemid: int):
        return super().__init__(**_get_params(vars()))

    @classmethod
    @_validate_args
    def dataitems(cls, search: str = None, package: str = None):
        """
        Usable data items for the share data component.

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

            Columns :
                - *datamodule*
                - *datacomponent*
                - *dataitemid*
                - *datadescription*


        Examples
        --------
            >>> di = ps.index.share.dataitems("Russell 3000 Index")
            >>> di[["dataitemid", "dataitemname"]]
            dataitemid        dataitemname
            0     4000099  Russell 3000 Index
        """
        return cls._dataitems(search=search, package=package)


class weight(_PrismIndexComponent):
    """
    | Index constituent weight data.
    | Default frequency is business daily.

    Parameters
    ----------
        dataitemid : int
            | Unique identifier for the different data item. This identifies the type of the index (S&P 500, FTSE 200, etc.)

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
        >>> di = ps.index.weight.dataitems("Russell 3000 Index")
        >>> di[["dataitemid", "dataitemname"]]
           dataitemid        dataitemname
        0     4000099  Russell 3000 Index

        >>> rus = ps.index.weight(4000099)
        >>> rus_df = rus.get_data(startdate='2010-01-01', enddate='2020-12-31', shownid=["Company Name"])
        >>> rus_df
                 listingid        date     value           Company Name
        0          2598345  2012-06-25  0.000009  CARRIAGE SERVICES INC
        1          2598345  2012-06-26  0.000009  CARRIAGE SERVICES INC
        2          2598345  2012-06-27  0.000009  CARRIAGE SERVICES INC
        3          2598345  2012-06-28  0.000009  CARRIAGE SERVICES INC
        4          2598345  2012-06-29  0.000009  CARRIAGE SERVICES INC
        ...            ...         ...       ...                    ...
        5989430  692043613  2020-12-23  0.000013         MEDIAALPHA INC
        5989431  692043613  2020-12-24  0.000013         MEDIAALPHA INC
        5989432  692043613  2020-12-28  0.000012         MEDIAALPHA INC
        5989433  692043613  2020-12-29  0.000011	     MEDIAALPHA INC
        5989434  692043613  2020-12-30  0.000011	     MEDIAALPHA INC
    """
    @_validate_args
    def __init__(self, dataitemid: int):
        return super().__init__(**_get_params(vars()))

    @classmethod
    @_validate_args
    def dataitems(cls, search: str = None, package: str = None):
        """
        Usable data items for the weight data component.

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

            Columns :
                - *datamodule*
                - *datacomponent*
                - *dataitemid*
                - *datadescription*

        Examples
        --------
            >>> di = ps.index.weight.dataitems("Russell 3000 Index")
            >>> di[["dataitemid", "dataitemname"]]
            dataitemid        dataitemname
            0     4000099  Russell 3000 Index
        """
        return cls._dataitems(search=search, package=package)


class level(_PrismIndexComponent):
    """
    | Index level data.
    | Default frequency is business daily.

    Parameters
    ----------
        dataitemid : int
            | Unique identifier for the different data item. This identifies the type of the index (S&P 500, FTSE 200, etc.)

        leveltype : str, default None, {'Price Return', 'Total Return Gross'}
            | Default value None gives all leveltype.

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
        >>> di = ps.index.level.dataitems("Russell 3000 Index")
        >>> di[["dataitemid", "dataitemname"]]
           dataitemid        dataitemname
        0     4000099  Russell 3000 Index

        >>> rus = ps.index.level(4000099)
        >>> rus_df = rus.get_data(startdate='2010-01-01', enddate='2020-12-31')
        >>> rus_df
                     date           leveltype       value
        0      2010-01-04  Total Return Gross  2925.36135
        1      2010-01-05  Total Return Gross  2933.81744
        2      2010-01-06  Total Return Gross  2937.46528
        3      2010-01-07  Total Return Gross  2949.90064
        4      2010-01-08  Total Return Gross  2959.37327
        ...           ...                 ...         ...
        11067  2020-12-23    Total Return Net  3243.92347
        11068  2020-12-24    Total Return Net  3252.86186
        11069  2020-12-28    Total Return Net  3270.69819
        11070  2020-12-29    Total Return Net  3257.80733
        11071  2020-12-30    Total Return Net  3266.55282
    """
    @_validate_args
    def __init__(self, dataitemid: int):
        return super().__init__(**_get_params(vars()))

    @classmethod
    @_validate_args
    def dataitems(cls, search: str = None, package: str = None):
        """
        Usable data items for the level data component.

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

            Columns :
                - *datamodule*
                - *datacomponent*
                - *dataitemid*
                - *datadescription*

        Examples
        --------
            >>> di = ps.index.level.dataitems("Russell 3000 Index")
            >>> di[["dataitemid", "dataitemname"]]
            dataitemid        dataitemname
            0     4000099  Russell 3000 Index
        """
        return cls._dataitems(search=search, package=package)

    @_validate_args
    @_req_call(_dataquery)
    def get_data(self, startdate: str = None, enddate: str = None, name = None,) -> pd.DataFrame:
        pass


@_validate_args
def universe_dataitems(search: str = None, package: str = None):
    """
    Usable data items for the index data category, which can be used to create universe in prismstudio.save_index_as_universe()

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
    >>> di = ps.index.universe_dataitems("Korea Stock Price 200 Index")
    >>> di[["dataitemid", "dataitemname"]]
       dataitemid                 dataitemname
    0     6000034  Korea Stock Price 200 Index
    1     6000034  Korea Stock Price 200 Index
    """
    ret = _list_dataitem(datacategoryid=_PrismIndexComponent.categoryid, datacomponentid=17, search=search, package=package)
    ret = ret.drop(["dataitemdescription"], axis=1, errors="ignore")
    return ret


@_validate_args
def portfolio_dataitems(search: str = None, package: str = None):
    """
    Usable data items for the index data category, which can be used to create portfolio in prismstudio.save_index_as_portfolio().

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
        >>> di = ps.index.portfolio_dataitems("Russell 3000 Index")
        >>> di[["dataitemid", "dataitemname"]]
           dataitemid        dataitemname
        0     4000099  Russell 3000 Index
    """
    ret = _list_dataitem(datacategoryid=_PrismIndexComponent.categoryid, datacomponentid=16, search=search, package=package)
    ret = ret.drop(["dataitemdescription"], axis=1, errors="ignore")
    return ret


@_validate_args
def dataitems(search: str = None, package: str = None):
    """
    Usable data items for the index data category.

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
    >>> di = ps.index.dataitems("Korea Stock Price 200 Index")
    >>> di[["dataitemid", "dataitemname"]]
       dataitemid                 dataitemname
    0     6000034  Korea Stock Price 200 Index
    1     6000034  Korea Stock Price 200 Index
    """
    ret = _list_dataitem(
        datacategoryid=_PrismIndexComponent.categoryid,
        datacomponentid=None,
        search=search,
        package=package,
    )
    ret = ret.drop(["dataitemdescription"], axis=1, errors="ignore")
    return ret
