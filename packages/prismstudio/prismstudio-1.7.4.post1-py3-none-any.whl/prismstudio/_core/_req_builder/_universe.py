import copy
import logging
from io import BytesIO
from typing import Union

import requests
import pandas as pd

from ..._common.config import *
from ..._common.const import UniverseFrequencyType as _UniverseFrequencyType
from ._list import _list_dataitem
from .preference import get_quiet_mode
from ..._utils import (
    _validate_args,
    get,
    post,
    patch,
    delete,
    get_sm_attributeid,
    _authentication,
    _process_response,
    _process_fileresponse,
    _fetch_and_parse,
    plot_tree,
    are_periods_exclusive,
)
from ..._utils.exceptions import PrismNotFoundError, PrismValueError


__all__ = [
    "list_universe",
    "get_universe",
    "upload_timerange_universe",
    "upload_timeseries_universe",
    "save_index_as_universe",
    "combine_universe",
    "rename_universe",
    "delete_universe",
    "get_universe_template",
    "filter_universe",
]

logger = logging.getLogger()

@_validate_args
def list_universe(search: str = None, tree=False):
    """
    Return the all usable universes.

    Parameters
    ----------
        search : str, default None
            | Search word for universe name, the search is case-insensitive.
            | If None, the entire list is returned.

        tree : bool, default False
            | If True, the folder structure of the universes is visualized in a UNIX-style.

    Returns
    -------
        str or pandas.DataFrame
            | If tree is True, print file system tree of universes.
            | If tree is False, return usable universes in DataFrame.
            | Columns:

            - *universeid*
            - *universename*
            - *universetype*
            - *startdate*
            - *enddate*

    Examples
    --------
        >>> ps.list_universe()
        universeid                 universename  universetype   startdate     enddate
        0           1  Korea Stock Price 200 Index         index  1700-01-01  2199-12-31
        1           2                      S&P 500         index  1700-01-01  2199-12-31
        2           3    Russell 3000 Growth Index         index  1700-01-01  2199-12-31
        3           4           Russell 3000 Index         index  1700-01-01  2199-12-31
    """
    universes_df = _fetch_and_parse(URL_UNIVERSES, "puv", search)
    if universes_df.empty:
        raise PrismNotFoundError("No Universes found.")
    if not tree:
        return universes_df
    plot_tree(universes_df["universename"].tolist(), "universe")


@_validate_args
def get_universe(
    universe,
    startdate: str = None,
    enddate: str = None,
    frequency: str = None,
    shownid: list = None,
):
    """
    Return the specified universe in dataframe.

    Parameters
    ----------
        universe : str or int
            Universe name (str) or universe id (int) to get.

        startdate : str, default None
            | Start date of the data. The data includes start date.
            | If None, the start date of the universe is used. The same applies when the input is earlier than the universe start date.

        enddate : str, default None
            | End date of the data. The data excludes end date.
            | If None, the end date of the universe is used. The same applies when the input is later than the universe end date.

        frequency : str, {'D', 'W', 'MS', 'SMS', 'SM', 'M', 'Q', 'QS', 'AS', 'A'}, default None
            | Specifies the desired sampling frequency for universe constituents. If not provided, only dates corresponding to changes in the universe will be included.

        shownid : list, default None
            | List of Security Master attributes to display with the data.
            | If None, default attributes set in preferences is shown.
            | If empty list ([]), no attribute is shown.

    Returns
    -------
        pandas.DataFrame
            Universe.
            Columns:
            - *listingid*
            - *date*
            - *attributes provided by the user via 'shownid'*

    Examples
    --------
        >>> ps.list_universe()
           universeid                 universename  universetype   startdate     enddate
        0           1  Korea Stock Price 200 Index         index  1700-01-01  2199-12-31
        1           2                      S&P 500         index  1700-01-01  2199-12-31
        2           3    Russell 3000 Growth Index         index  1700-01-01  2199-12-31
        3           4           Russell 3000 Index         index  1700-01-01  2199-12-31

        >>> ps.get_universe(universe='Russell 3000 Index')
                  listingid        date
        0           2585895  1978-12-29
        1           2586016  1978-12-29
        2           2586064  1978-12-29
        3           2586086  1978-12-29
        4           2586118  1978-12-29
        ...             ...         ...
        10110503  701835357  2199-12-31
        10110504  701932931  2199-12-31
        10110505  703822433  2199-12-31
        10110506  704721046  2199-12-31
        10110507  706171023  2199-12-31

        >>> ps.get_universe('Russell 3000 Index', startdate='2010-01-01', enddate='2015-12-31', shownid=['companyname'])
                listingid        date                   companyname
        0          2585893  2010-01-03                      AAON INC
        1          2585895  2010-01-03                      AAR CORP
        2          2585957  2010-01-03    ADC TELECOMMUNICATIONS INC
        3          2586016  2010-01-03            ABM INDUSTRIES INC
        4          2586068  2010-01-03            AEP INDUSTRIES INC
        ...            ...         ...                           ...
        2194810  325621650  2015-12-27        AVAGO TECHNOLOGIES LTD
        2194811  325832671  2015-12-27                     POZEN INC
        2194812  326004249  2015-12-27  LIBERTY INTERACTV CP QVC GRP
        2194813  344286611  2015-12-27            ITT INDUSTRIES INC
        2194814  365743684  2015-12-27     HERTZ GLOBAL HOLDINGS INC
    """

    universeid, _ = parse_universe_to_universeid(universe)

    universe_info = get(f"{URL_UNIVERSES}/{universeid}/info")
    universe_startdate = universe_info["Start Date"].values[0]
    universe_enddate = universe_info["End Date"].values[0]

    universe_period_violated = are_periods_exclusive(universe_startdate, universe_enddate, startdate, enddate)

    if universe_period_violated:
        raise PrismValueError(
            f'Universe query period should overlap with universe period ({str(universe_startdate).split("T")[0]} ~ {str(universe_enddate).split("T")[0]})'
        )

    if (frequency is not None) and (startdate is None):
        raise PrismValueError(f"Please provide startdate to resample with frequency {frequency}")

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
        "frequency": frequency,
    }
    headers = _authentication()
    res = requests.get(URL_UNIVERSES + f"/{universeid}", params=params, headers=headers)
    ret, _ = _process_fileresponse(res, res.content)
    return list(ret.values())[0]


@_validate_args
def upload_timeseries_universe(
    df: pd.DataFrame,
    universename: str,
    idcolumn: list,
    idtype: list,
    datecolumn: str
):
    """
    Saves a time-series formatted pandas dataframe object as a universe. Multiple IDs can be mapped

    Parameters
    ----------
    df: pd.DataFrame
        Time-series universe pandas dataframe object

    universename : str
        Path of the universe to be created.

    idcolumn : list
        List of columns used for the ID filter.

    idtype : list
        List of attribute types corresponding to the ID columns.

    datecolumn : str
        The name of the column indicating the date.

    Returns
    -------
        status: dict
            Status of upload_universe.

    Examples
    -------

    import pandas as pd

        >>> universe_df = pd.DataFrame(
            [
                {'isin': 'US0378331005', 'date': '2025-01-01'},
                {'isin': 'US0378331005', 'date': '2025-01-02'},
                {'isin': 'US67066G1040', 'date': '2025-01-01'},
                {'isin': 'US67066G1040', 'date': '2025-01-02'},
            ]
        )

        >>> ps.upload_timeseries_universe(universe_df, 'apple_nvidia', ['isin'], ['ISIN'], 'date')
        {'status': 'Success',
         'message': 'Universe saved',
         'result': [{'resulttype': 'universeid', 'resultvalue': 630}]}

        >>> ps.list_universe('apple_nvidia')

           universeid  universename  ...    enddate               lastmodified
        0         630  apple_nvidia  ... 2025-01-02 2025-02-10 08:42:07.107654

    """
    should_overwrite, err_msg = should_overwrite_universe(universename, "uploading")
    if not should_overwrite:
        return err_msg
    filespace = BytesIO()
    df.to_parquet(path=filespace, index=False)
    filespace.seek(0)

    # Prepare the payload to be sent to the server
    params = {"path": universename + ".puv"}
    payload = {
        'idcolumn': idcolumn,
        'idtype': idtype,
        'datecolumn': datecolumn
    }
    files = {
        'universe_file': filespace
    }
    headers = {
        "Authorization": _authentication()["Authorization"],
        "client": "python",
    }

    # Make the POST request using the `post` utility function
    try:
        response = requests.post(url=f"{URL_UNIVERSES}/upload/timeseries", params=params, files=files, data=payload, headers=headers)
        return _process_response(response)
    except Exception as err:
        print(f"An error occurred: {err}")
        return {'status': 'Failure', 'message': str(err)}
    finally:
        filespace.close()


@_validate_args
def upload_timerange_universe(
    df: pd.DataFrame,
    universename: str,
    idcolumn: list,
    idtype: list,
    startdatecolumn: str,
    enddatecolumn: str
):
    """
    Saves a time range formatted pandas dataframe object as a universe. Multiple IDs can be mapped

    Parameters
    ----------
    universename : str
        Path of the universe to be created.

    df: pd.DataFrame
        Time-series universe pandas dataframe object

    idcolumn : list
        List of columns used for the ID filter.

    idtype : list
        List of attribute types corresponding to the ID columns.

    startdatecolumn : str
        The name of the column indicating the start date.

    enddatecolumn : str
        The name of the column indicating the end date.

    Returns
    -------
        status: dict
            Status of upload_universe.

    Examples
    --------
        import pandas as pd

        >>> universe_df = pd.DataFrame(
            [
                {'isin': 'US0378331005', 'startdate': '1800-01-01', 'enddate': '2199-12-31'},
                {'isin': 'US67066G1040', 'startdate': '1800-01-01', 'enddate': '2199-12-31'},
            ]
        )

        >>> ps.upload_timerange_universe(universe_df, 'apple_nvidia_range', ['isin'], ['ISIN'], 'startdate', 'enddate')
        {'status': 'Success',
         'message': 'Universe saved',
         'result': [{'resulttype': 'universeid', 'resultvalue': 630}]}

        >>> ps.list_universe('apple_nvidia_range')

           universeid        universename  ...    enddate               lastmodified
        0         633  apple_nvidia_range  ... 2199-12-31 2025-02-10 08:45:33.062585

    """
    should_overwrite, err_msg = should_overwrite_universe(universename, "uploading")
    if not should_overwrite:
        return err_msg
    filespace = BytesIO()
    df.to_parquet(path=filespace, index=False)
    filespace.seek(0)

    # Prepare the payload to be sent to the server
    params = {"path": universename + ".puv"}
    payload = {
        'idcolumn': idcolumn,
        'idtype': idtype,
        'startdatecolumn': startdatecolumn,
        'enddatecolumn': enddatecolumn
    }
    files = {
        'universe_file': filespace
    }
    headers = {
        "Authorization": _authentication()["Authorization"],
        "client": "python",
    }

    # Make the POST request using the `post` utility function
    try:
        response = requests.post(url=f"{URL_UNIVERSES}/upload/timerange", params=params, files=files, data=payload, headers=headers)
        return _process_response(response)
    except Exception as err:
        print(f"An error occurred: {err}")
        return {'status': 'Failure', 'message': str(err)}
    finally:
        filespace.close()

@_validate_args
def save_index_as_universe(
    dataitemid: int,
    startdate: str = None,
    enddate: str = None,
    universename: str = None,
):
    """
    Create a new universe containing the constituents of an index.

    Parameters
    ----------
        dataitemid : int
            Unique identifier for the different data item. This identifies the index.
        startdate: str, default None
            Start date of the data. The data includes start date.
            If None, the start date of the universe is used. The same applies when the input is earlier than the universe start date.
        enddate: str, default None
            End date of the data. The data excludes end date.
            If None, the end date of the universe is used. The same applies when the input is later than the universe end date.
        universename: str, default None
            Name of the universe to be saved from the index.
            If None, the index name is used.


    Returns
    -------
        status: dict
            Status of save_index_as_universe.

    Examples
    --------
        >>> ps.index.universe_dataitems("S&P 500")
            dataitemid                                       dataitemname    datamodule       package
        0       4006682                                            S&P 500  S&P US Index  S&P US Index
        1       4006683           S&P 500 - Alternative Carriers (Sub Ind)	S&P US Index  S&P US Index
        2       4006684                 S&P 500 - Biotechnology (Industry)	S&P US Index  S&P US Index
        3       4006685                  S&P 500 - Biotechnology (Sub Ind)	S&P US Index  S&P US Index
        4       4006686                   S&P 500 - Broadcasting (Sub Ind)  S&P US Index  S&P US Index
        ...	        ...	                                               ...           ...           ...
        308     4006990                  S&P 500 Water Utilities (Sub Ind)	S&P US Index  S&P US Index
        309     4006991  S&P 500 Wireless Telecommunication Services (I...  S&P US Index  S&P US Index
        310     4006992  S&P 500 Wireless Telecommunication Services (S...  S&P US Index  S&P US Index
        311     4006993                      S&P 500 Oil (Composite) Index	S&P US Index  S&P US Index
        312     4006994  S&P 500 Semiconductors (Sub Ind)(30-APR-03) In...  S&P US Index  S&P US Index

        >>> ps.save_index_as_universe(dataitemid=4006682)
        {'status': 'Success',
        'message': 'Universe saved',
        'result': [{'resulttype': 'universeid', 'resultvalue': 1}]}

        >>> ps.list_universe()
        universeid  universename  universetype   startdate     enddate
        0           1       S&P 500         index  1700-01-01  2199-12-31
    """

    if universename is None:
        indices = _list_dataitem(
            datacategoryid = 3,
            datacomponentid = 17,
        )
        universename = indices[indices["dataitemid"] == dataitemid]["dataitemname"].values[0]

    should_overwrite, err_msg = should_overwrite_universe(universename, "combining")
    if not should_overwrite:
        return err_msg
    params = {
        "dataitemid": dataitemid,
        "startdate": startdate,
        "enddate": enddate,
        "path": universename + ".puv",
    }
    ret = post(URL_UNIVERSES + f"/index", params, None)
    logger.info(f'{ret["message"]}: {ret["result"][0]["resulttype"]} is {ret["result"][0]["resultvalue"]}')
    return ret


@_validate_args
def combine_universe(universes: list, newuniversename: str):
    """
    Create a new universe by combining existing universes.

    Parameters
    ----------
        universes: list of int or list of str
            List of universe id (int) or universe name (str) to combine.
        newuniversename: str
            Name of the universe to be created.

    Returns
    -------
        status: dict
            Status of combine universe.

    Examples
    --------
        >>> ps.list_universe()
        universeid                 universename  universetype   startdate     enddate
        0           1  Korea Stock Price 200 Index         index  1700-01-01  2199-12-31
        1           2                      S&P 500         index  1700-01-01  2199-12-31
        2           3    Russell 3000 Growth Index         index  1700-01-01  2199-12-31
        3           4           Russell 3000 Index         index  1700-01-01  2199-12-31

        >>> ps.combine_universe(["Korea Stock Price 200 Index", "S&P 500"], newuniversename="kospi_snp")
        {'status': 'Success',
        'message': 'Universe saved',
        'result': [{'resulttype': 'universeid', 'resultvalue': 1}]}

        >>> ps.list_universe()
        universeid                 universename  universetype   startdate     enddate
        0           1  Korea Stock Price 200 Index         index  1700-01-01  2199-12-31
        1           2                      S&P 500         index  1700-01-01  2199-12-31
        2           3    Russell 3000 Growth Index         index  1700-01-01  2199-12-31
        3           4           Russell 3000 Index         index  1700-01-01  2199-12-31
        4           5                    kospi_snp        custom  1700-01-01  2199-12-31

    """
    if len(universes) < 2:
        SystemExit("Please provide more than 2 universes to combine.")
    should_overwrite, err_msg = should_overwrite_universe(newuniversename, "saving")
    if not should_overwrite:
        return err_msg
    universeids = parse_universes_to_universeids(universes)
    params = {"universeids": universeids, "path": newuniversename + ".puv"}
    ret = post(URL_UNIVERSES + f"/combine", params, None)
    logger.info(f'{ret["message"]}: {ret["result"][0]["resulttype"]} is {ret["result"][0]["resultvalue"]}')
    return ret


@_validate_args
def rename_universe(old: Union[str, int], new: str):
    """
    Rename universe. Location of universe within the folder structure can be changed using the method.

    Parameters
    ----------
        old: str or int
            Name of existing universe (str) or universe id (int) to be renamed.
        new: str
            New name of the universe.

    Returns
    -------
        status: dict
            Status of rename universe.

    Examples
    --------
        >>> ps.list_universe()
        universeid                 universename  universetype   startdate     enddate
        0           1  Korea Stock Price 200 Index         index  1700-01-01  2199-12-31
        1           2                      S&P 500         index  1700-01-01  2199-12-31
        2           3    Russell 3000 Growth Index         index  1700-01-01  2199-12-31
        3           4           Russell 3000 Index         index  1700-01-01  2199-12-31

        >>> ps.rename_universe(old='S&P 500', new='newname_snp')
        {'status': 'Success',
        'message': 'Universe renamed',
        'result': [{'resulttype': 'universeid', 'resultvalue': 2}]}

        >>> ps.list_universe()
        universeid                 universename  universetype   startdate     enddate
        0           1  Korea Stock Price 200 Index         index  1700-01-01  2199-12-31
        1           2                  newname_snp         index  1700-01-01  2199-12-31
        2           3    Russell 3000 Growth Index         index  1700-01-01  2199-12-31
        3           4           Russell 3000 Index         index  1700-01-01  2199-12-31

    """
    universeid, _ = parse_universe_to_universeid(old)
    should_overwrite, err_msg = should_overwrite_universe(new, "renaming")
    if not should_overwrite:
        return err_msg
    ret = patch(URL_UNIVERSES + f"/{universeid}", {"newpath": new + ".puv"}, None)
    logger.info(ret["message"])
    return ret


@_validate_args
def delete_universe(universe: Union[str, int]):
    """
    Delete universe.

    Parameters
    ----------
        universe : str or int
            Universe name (str) or universe id (int) to delete.

    Returns
    -------
        status: dict
            Status of delete_universe.

    Examples
    --------
        >>> ps.list_universe()
        universeid                 universename  universetype   startdate     enddate
        0           1  Korea Stock Price 200 Index         index  1700-01-01  2199-12-31
        1           2                      S&P 500         index  1700-01-01  2199-12-31
        2           3    Russell 3000 Growth Index         index  1700-01-01  2199-12-31
        3           4           Russell 3000 Index         index  1700-01-01  2199-12-31

        >>> ps.delete_universe(universe='Russell 3000 Growth Index')
        {'status': 'Success',
        'message': 'Universe deleted',
        'result': [{'resulttype': 'universeid', 'resultvalue': 3}]}

        >>> ps.list_universe()
        universeid                 universename  universetype   startdate     enddate
        0           1  Korea Stock Price 200 Index         index  1700-01-01  2199-12-31
        1           2                      S&P 500         index  1700-01-01  2199-12-31
        2           4           Russell 3000 Index         index  1700-01-01  2199-12-31
    """
    universeid, universename = parse_universe_to_universeid(universe)
    status, msg = should_overwrite_universe(universename, "delete")
    if status:
        ret = delete(URL_UNIVERSES + f"/{universeid}")
        logger.info(ret["message"])
        return ret
    logger.info(msg)


def get_universe_template():
    """
    Get list of columns required for prismstudio.upload_universe.

    Returns
    -------
        columns : list of str
            List of columns required for csv file to be uploaded.

    Examples
    --------
        >>> ps.get_universe_template()
        valuetype, value, startdate, enddate
    """
    res = requests.get(url=URL_UNIVERSES + "/template", headers=_authentication())
    return res.text


@_validate_args
def filter_universe(condition: list, universename: str, active: bool=False):
    """
    Create a new universe from the entire Security Master using simple filter rules applied on Security Master attribute.

    Parameters
    ----------
        condition : list of dict
            List of security conditions to apply as filter. Each dictionary contains two required keys and one optional key: "attribute", "value", "isnot". Value must be a list

            - attribute: Security Master attribute to condition on.
            - value: Value of Security Master attribute to condition on.
            - isnot (optional): bool = False

        universename : str
            Name of the universe to be created.

        active : bool, default False
            Whether to apply the `active` attribute. It makes the filtered universe fully historical.

    Returns
    -------
        status: dict
            Status of filter_universe.

    Examples
    --------
        >>> condition = [
            {'attribute': 'country', 'value': ['AU', 'NZ', 'HK', 'SG', 'JP', 'IN', 'ID', 'KR', 'MY', 'PH', 'TW', 'TH']},
            {'attribute': 'CIQ primary', 'value': ['primary']}
        ]
        >>> ps.filter_universe(condition=condition, universename="APAC_primary")
        {'status': 'Success',
        'message': 'Universe saved',
        'result': [{'resulttype': 'universeid', 'resultvalue': 1}]}

        >>> ps.list_universe()
        universeid  universename  universetype   startdate     enddate
        0           1  APAC_primary         index  1700-01-01  2199-12-31
    """
    if len(condition) == 0:
        raise PrismValueError("At least one condition must be provided.")
    should_overwrite, err_msg = should_overwrite_universe(universename, "filtering")
    if not should_overwrite:
        return err_msg
    condition_copy = copy.deepcopy(condition)
    for i in range(len(condition)):
        assert isinstance(condition[i], dict), "condition must be list of dicts"
        assert set(condition[i].keys()) - {"isnot"} == {
            "attribute",
            "value"
        }, 'Valid arguments are "attribute", "value", and "isnot"'
        if not isinstance(condition[i]["value"], list):
            raise PrismValueError("Value must be a list")
        condition_copy[i]["attributeid"] = get_sm_attributeid(condition_copy[i]["attribute"])
        condition_copy[i].pop("attribute")
        condition_copy[i]["isnot"] = condition[i].get("isnot", False)

    ret = post(URL_UNIVERSES + "/filter", {"path": universename + ".puv", "active": active}, condition_copy)
    logger.info(f'{ret["message"]}: {ret["result"][0]["resulttype"]} is {ret["result"][0]["resultvalue"]}')
    return ret


@_validate_args
def parse_universe_to_universeid(universe: Union[str, int]):
    universes_df = _fetch_and_parse(URL_UNIVERSES, "puv")
    if universes_df.empty:
        raise PrismNotFoundError("No universe found.")

    if isinstance(universe, int):
        universes_df = universes_df[universes_df["universeid"] == universe]
    elif isinstance(universe, str):
        universes_df = universes_df[universes_df["universename"] == universe]
    else:
        raise PrismValueError("Please provide universe name or universe id for universe.")

    if universes_df.empty:
        raise PrismNotFoundError(f"No universe matching: {universe}", True, None)
    universeid = universes_df["universeid"].values[0]
    universename = universes_df["universename"].values[0]

    return universeid, universename


def parse_universes_to_universeids(universes: list):
    universes_df = _fetch_and_parse(URL_UNIVERSES, "puv")
    if universes_df.empty:
        raise PrismNotFoundError("No universe found.")

    universenames = []
    universeids = []
    for u in universes:
        if isinstance(u, int):
            universeids.append(u)
        elif isinstance(u, str):
            universenames.append(u)
        else:
            raise PrismValueError("Please provide universe name or universe id for universe.")

    ret_universeids = set()
    if len(universenames) != 0:
        matching_universes_df = universes_df[universes_df["universename"].isin(universenames)]
        if len(matching_universes_df) != len(universenames):
            not_matched = list(set(universenames) - set(matching_universes_df["universename"].tolist()))
            raise PrismNotFoundError(f"No universe matching: {not_matched}")
        universeids_from_universenames = matching_universes_df["universeid"].tolist()
        ret_universeids.update(universeids_from_universenames)

    if len(universeids) != 0:
        matching_universes_df = universes_df[universes_df["universeid"].isin(universeids)]
        if len(matching_universes_df) != len(universeids):
            not_matched = list(set(universeids) - set(matching_universes_df["universeid"].tolist()))
            raise PrismNotFoundError(f"No universe matching: {not_matched}")
        existing_universeids = matching_universes_df["universeid"].tolist()
        ret_universeids.update(existing_universeids)
    return list(ret_universeids)


def should_overwrite_universe(universename, operation):
    if get_quiet_mode():
        return True, None
    universes_df = _fetch_and_parse(URL_UNIVERSES, "puv", universename)
    if universes_df.empty:
        return True, None

    if universename in universes_df["universename"].to_list():
        if operation == 'delete':
            overwrite = input(f"Do you want to delete? (Y/N) \n")
        else:
            overwrite = input(f"{universename} already exists. Do you want to overwirte? (Y/N) \n")
        if overwrite.lower() == "y":
            return True, None
        elif overwrite.lower() == "n":
            return False, f"Not {operation} universe."
        else:
            return False, "Please provide a valid input."
    else:
        return True, None
