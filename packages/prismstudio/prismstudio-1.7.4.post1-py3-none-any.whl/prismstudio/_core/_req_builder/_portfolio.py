import logging
from typing import Union

import requests

from ..._common.config import *
from ..._common.const import *
from ._list import _list_dataitem
from .preference import get_quiet_mode
from ..._utils import (
    _validate_args,
    get,
    post,
    patch,
    delete,
    get_sm_attributeid,
    _process_fileresponse,
    _authentication,
    _fetch_and_parse,
    plot_tree,
    are_periods_exclusive,
)
from ..._utils.exceptions import PrismNotFoundError, PrismValueError


__all__ = ["list_portfolio", "get_portfolio", "rename_portfolio", "delete_portfolio", "save_index_as_portfolio"]

logger = logging.getLogger()

@_validate_args
def list_portfolio(search: str = None, tree=False):
    """
    Return the all usable portfolios.

    Parameters
    ----------
        search : str, default None
            | Search word for portfolio name, the search is case-insensitive.
            | If None, the entire list is returned.

        tree : bool, default False
            | If True, the folder structure of the portfolio is visualized in a UNIX-style.

    Returns
    -------
        bool or pandas.DataFrame
            | If tree is True, print file system tree of portfolios.
            | If tree is False, return usable portfolios in DataFrame.
            | Columns:

            - *portfolioid*
            - *portfolioname*
            - *portfoliotype*
            - *startdate*
            - *enddate*

    Examples
    --------
        >>> ps.list_portfolio()
        portfolioid  portfolioname  portfoliotype   startdate     enddate
        0            1        S&P 500          index  1700-01-01  2199-12-31
        1            2            ROA       backtest  1700-01-01  2199-12-31
    """

    portfolio_df = _fetch_and_parse(URL_PORTFOLIOS, "ppt", search)
    if portfolio_df.empty:
        raise PrismNotFoundError("No Portfolios found.")
    if not tree:
        return portfolio_df
    plot_tree(portfolio_df["portfolioname"].tolist(), "portfolio")


@_validate_args
def get_portfolio(portfolio, startdate: str = None, enddate: str = None, shownid: list = None):
    """
    Return the specified portfolio in dictionary of dataframes. The dictionary contains Portfolio Level and Portfolio Value.

    Parameters
    ----------
        portfolio : str or int
            | Portfolio name (str) or portfolio id (int) to get.

        startdate : str, default None
            | Start date of the data. The data includes start date.
            | If None, the start date of the portfolio is used. The same applies when the input is earlier than the portfolio start date.

        enddate : str, default None
            | End date of the data. The data excludes end date.
            | If None, the end date of the portfolio is used. The same applies when the input is later than the portfolio end date.

        shownid : list, default None
            | List of Security Master attributes to display with the data.
            | If None, default attributes set in preferences is shown.
            | If empty list ([]), no attribute is shown.

    Returns
    -------
        dict of pandas.DataFrame
            | Portfolios.
            | Keys:

            - *portfoliovalue*
            - *portfoliolevel*

    Examples
    --------
        >>> ps.list_portfolio()
        portfolioid  portfolioname  portfoliotype   startdate     enddate
        0            1        S&P 500          index  1700-01-01  2199-12-31
        1            2            ROA       backtest  1700-01-01  2199-12-31

        >>> ps.get_portfolio(portfolio="S&P 500")
        {
            'portfoliolevel':              date  leveltypeid        value
                            0      1928-01-03            2    17.760000
                            1      1928-01-04            2    17.720000
                            2      1928-01-05            2    17.550000
                            3      1928-01-06            2    17.660000
                            4      1928-01-07            2    17.680000
                            ...           ...          ...          ...
                            38521  2021-03-23            1  8106.832957
                            38522  2021-03-24            1  8062.996308
                            38523  2021-03-25            1  8105.511314
                            38524  2021-03-26            1  8240.381492
                            38525  2021-03-29            1  8233.244940,
            'portfoliovalue':         listingid        date        value
                            0         90036394  1990-09-20   37654000.0
                            1         90036394  1990-09-21   37654000.0
                            2         90036394  1990-09-24   37654000.0
                            3         90036394  1990-09-25   37654000.0
                            4         90036394  1990-09-26   37654000.0
                            ...            ...         ...          ...
                            4062034  706171023  2021-03-24  377861000.0
                            4062035  706171023  2021-03-25  377861000.0
                            4062036  706171023  2021-03-26  377861000.0
                            4062037  706171023  2021-03-29  377861000.0
                            4062038  706171023  2021-03-30  377861000.0
        }
    """

    portfolioid = parse_portfolios_to_portfolioids([portfolio])[0]
    portfolio_info = get(f"{URL_PORTFOLIOS}/{portfolioid}/info")
    portfolio_startdate = portfolio_info["Start Date"].values[0]
    portfolio_enddate = portfolio_info["End Date"].values[0]

    portfolio_period_violated = are_periods_exclusive(portfolio_startdate, portfolio_enddate, startdate, enddate)

    if portfolio_period_violated:
        raise PrismValueError(
            f'Portfolio query period should overlap with portfolio period ({str(portfolio_startdate).split("T")[0]} ~ {str(portfolio_enddate).split("T")[0]})'
        )

    default_shownid = True
    if (shownid is not None) and (len(shownid) == 0):
        shownid = None
        default_shownid = False
    if shownid is not None:
        shownid = [get_sm_attributeid(a) for a in shownid]

    params = {
        "startdate": startdate,
        "enddate": enddate,
        "shownid": shownid,
        "default_shownid": default_shownid,
    }
    headers = _authentication()
    res = requests.get(URL_PORTFOLIOS + f"/{portfolioid}", params=params, headers=headers)
    ret, _ = _process_fileresponse(res, res.content)
    return list(ret.values())[0]


@_validate_args
def save_index_as_portfolio(
    dataitemid: int,
    startdate: str = None,
    enddate: str = None,
    portfolioname: str = None,
):
    """
    Create a new portfolio containing the constituents of an index.

    Parameters
    ----------
        dataitemid : int
            | Unique identifier for the different data item. This identifies the index.

        startdate : str, default None
            | Start date of the portfolio. The data includes start date.
            | If None, the earliest available date of the index is used. The same applies when the input is earlier than the earliest available date of the index.

        enddate : str, default None
            | End date of the portfolio. The data excludes end date.
            | If None, the latest available date of the index is used. The same applies when the input is later than the latest available date of the index.

        universename : str, default None
            | Name of the portfolio to be saved from the index.
            | If None, the index name is used.


    Returns
    -------
        status: dict
            Status of save_index_as_portfolio.

    Examples
    --------
        >>> ps.index.portfolio_dataitems("S&P 500")
            dataitemid                                       dataitemname    datamodule       package
        0       4006682                                            S&P 500  S&P US Index  S&P US Index
        1       4006683           S&P 500 - Alternative Carriers (Sub Ind)  S&P US Index  S&P US Index
        2       4006684                 S&P 500 - Biotechnology (Industry)  S&P US Index  S&P US Index
        3       4006685                  S&P 500 - Biotechnology (Sub Ind)  S&P US Index  S&P US Index
        4       4006686                   S&P 500 - Broadcasting (Sub Ind)  S&P US Index  S&P US Index
        ...	        ...	                                               ...           ...           ...
        308     4006990                  S&P 500 Water Utilities (Sub Ind)  S&P US Index  S&P US Index
        309     4006991  S&P 500 Wireless Telecommunication Services (I...  S&P US Index  S&P US Index
        310     4006992  S&P 500 Wireless Telecommunication Services (S...  S&P US Index  S&P US Index
        311     4006993                      S&P 500 Oil (Composite) Index  S&P US Index  S&P US Index
        312     4006994  S&P 500 Semiconductors (Sub Ind)(30-APR-03) In...  S&P US Index  S&P US Index

        >>> ps.save_index_as_portfolio(dataitemid=4006682)
        {'status': 'Success',
        'message': 'Portfolio saved',
        'result': [{'resulttype': 'portfolioid', 'resultvalue': 1}]}

        >>> ps.list_portfolio()
        portfolioid  portfolioname  portfoliotype   startdate     enddate
        0            1        S&P 500          index  1700-01-01  2199-12-31
    """
    if portfolioname is None:
        indices = _list_dataitem(
            datacategoryid = 3,
            datacomponentid = 16,
        )
        portfolioname = indices[indices["dataitemid"] == dataitemid]["dataitemname"].values[0]

    should_overwrite, err_msg = should_overwrite_portfolio(portfolioname, "saving")
    if not should_overwrite:
        return err_msg
    params = {
        "dataitemid": dataitemid,
        "startdate": startdate,
        "enddate": enddate,
        "path": portfolioname + ".ppt",
    }
    ret = post(URL_PORTFOLIOS + f"/index", params, None)
    logger.info(f'{ret["message"]}: {ret["result"][0]["resulttype"]} is {ret["result"][0]["resultvalue"]}')
    return ret


@_validate_args
def rename_portfolio(old: Union[str, int], new: str):
    """
    Rename portfolio. Location of portfolio within the folder structure can be changed using the method.

    Parameters
    ----------
        old : str
            Name of the existing portfolio to be renamed.

        new : str
            Name of the portfolio after rename.

    Returns
    -------
        status: dict
            Status of rename_portfolio.

    Examples
    --------
        >>> ps.list_portfolio()
        portfolioid                portfolioname  portfoliotype   startdate     enddate
        0            1  Korea Stock Price 200 Index          index  1700-01-01  2199-12-31
        1            2                      S&P 500          index  1700-01-01  2199-12-31
        2            3    Russell 3000 Growth Index          index  1700-01-01  2199-12-31
        3            4           Russell 3000 Index          index  1700-01-01  2199-12-31

        >>> ps.rename_portfolio(old='S&P 500', new='newname_snp')
        {'status': 'Success',
        'message': 'Portfolio renamed',
        'result': [{'resulttype': 'portfolioid', 'resultvalue': 2}]}

        >>> ps.list_portfolio()
        portfolioid                portfolioname  portfoliotype   startdate     enddate
        0            1  Korea Stock Price 200 Index          index  1700-01-01  2199-12-31
        1            2                  newname_snp          index  1700-01-01  2199-12-31
        2            3    Russell 3000 Growth Index          index  1700-01-01  2199-12-31
        3            4           Russell 3000 Index          index  1700-01-01  2199-12-31
    """
    should_overwrite, err_msg = should_overwrite_portfolio(new, "renaming")
    if not should_overwrite:
        return err_msg
    portfolioid = parse_portfolios_to_portfolioids([old])[0]
    ret = patch(URL_PORTFOLIOS + f"/{portfolioid}", {"newpath": new + ".ppt"}, None)
    logger.info(ret["message"])
    return ret


@_validate_args
def delete_portfolio(portfolio: Union[str, int]):
    """
    Delete portfolio.

    Parameters
    ----------
        portfolio : str or int
            Portfolio name (str) or portfolio id (int) to delete.


    Returns
    -------
        status: dict
            Status of delete_portfolio.

    Examples
    --------
        >>> ps.list_portfolio()
        portfolioid  portfolioname  portfoliotype   startdate     enddate
        0            1        S&P 500          index  1700-01-01  2199-12-31
        1            2            ROA       backtest  1700-01-01  2199-12-31

        >>> ps.delete_portfolio(portfolio='S&P 500')
        {'status': 'Success',
        'message': 'Universe deleted',
        'result': [{'resulttype': 'portfolioid', 'resultvalue': 1}]}

        >>> ps.list_portfolio()
        portfolioid  portfolioname  portfoliotype   startdate     enddate
        0            2            ROA       backtest  1700-01-01  2199-12-31
    """
    portfolioid = parse_portfolios_to_portfolioids([portfolio])[0]
    ret = delete(URL_PORTFOLIOS + f"/{portfolioid}")
    logger.info(ret["message"])
    return ret


def parse_portfolios_to_portfolioids(portfolios: list):
    portfolios_df = _fetch_and_parse(URL_PORTFOLIOS, "ppt")
    if portfolios_df.empty:
        raise PrismNotFoundError("No portfolio Found.")

    portfolionames = []
    portfolioids = []
    for p in portfolios:
        if isinstance(p, int):
            portfolioids.append(p)
        elif isinstance(p, str):
            portfolionames.append(p)
        else:
            raise PrismValueError("Please provide portfolio name or portfolio id for portfolio.")

    ret_portfolioids = set()
    if len(portfolionames) != 0:
        matching_portfolios_df = portfolios_df[portfolios_df["portfolioname"].isin(portfolionames)]
        if len(matching_portfolios_df) != len(portfolionames):
            not_matched = list(set(portfolionames) - set(matching_portfolios_df["portfolioname"].tolist()))
            raise PrismNotFoundError(f"No portfolio matching: {not_matched}")
        ret_portfolioids.update(matching_portfolios_df["portfolioid"].tolist())

    if len(portfolioids) != 0:
        matching_portfolios_df = portfolios_df[portfolios_df["portfolioid"].isin(portfolioids)]
        if len(matching_portfolios_df) != len(portfolioids):
            not_matched = list(set(portfolioids) - set(matching_portfolios_df["portfolioid"].tolist()))
            raise PrismNotFoundError(f"No portfolio matching: {not_matched}")
        ret_portfolioids.update(matching_portfolios_df["portfolioid"].tolist())
    return list(ret_portfolioids)


def should_overwrite_portfolio(portfolioname, operation):
    if get_quiet_mode():
        return True, None
    portfolios_df = _fetch_and_parse(URL_PORTFOLIOS, "ppt")
    if portfolios_df.empty:
        return True, None

    if portfolioname in portfolios_df["portfolioname"].to_list():
        overwrite = input(f"{portfolioname} already exists. Do you want to overwrite? (Y/N) \n")
        if overwrite.lower() == "y":
            return True, None
        elif overwrite.lower() == "n":
            return False, f"Abort {operation} portfolio."
        else:
            return False, "Please provide a valid input."
    else:
        return True, None
