import logging
from typing import Union

import requests
import orjson

from ..._common.config import *
from ..._common.const import *
from ..._utils import (
    _validate_args,
    _fetch_and_parse,
    plot_tree,
    _authentication,
    _process_fileresponse,
    _process_response,
    download,
    patch,
    delete,
    Loader,
)
from ..._utils.exceptions import PrismNotFoundError, PrismResponseError, PrismValueError


logger = logging.getLogger()


@_validate_args
def list_datafiles(tree=False):
    """
    Return the list of all saved datafiles available.

    Parameters
    ----------
        bool or pandas.DataFrame
            | If tree is True, print file system tree of datafiles.
            | If tree is False, return usable datafiles in pandas.DataFrame.
            | Columns:

            - *dataqueryid*
            - *dataqueryname*

    Returns
    -------
        pandas.DataFrame
            Datafiles.
            Columns:
            - *datafileid*
            - *datafilename*
            - *lastmodified*

    Examples
    --------
        >>> ps.list_dataquery()
             datafileid  datafilename             lastmodified
        0      05bca9b2    open_close  2023-03-08 05:22:42.169
    """

    exported_data_df = _fetch_and_parse(URL_DATA_FILES, "ped")
    if exported_data_df.empty:
        raise PrismNotFoundError("No Exported Data found.")
    if not tree:
        return exported_data_df
    plot_tree(exported_data_df["exportdataname"].tolist(), "exportdata")


@_validate_args
def retrieve_datafiles(datafile: Union[str, int]):
    """
    Retrieve the specified data files in dictionary of dataframes.

    Parameters
    ----------
        datafile: str
            Datafile name or datafile id to get.

    Returns
    -------
        dict
            Dictionary of pandas.DataFrame.

    Examples
    --------
        >>> ps.retrieve_datafiles(open_close)
        Exported Data test_single_q has components: ['close', 'open']
        {'close':
                 listingid       date         Close
        0         20108704 2022-01-03  16188.903172
        1         20108704 2022-01-04  16477.132902
        2         20108704 2022-01-05  16092.826595
        3         20108704 2022-01-06  15468.328847
        4         20108704 2022-01-07  15804.596865
        ...            ...        ...           ...
        666583  1816050654 2023-03-20  31700.000000
        666584  1816050654 2023-03-21  31050.000000
        666585  1816050654 2023-03-22  31800.000000
        666586  1816050654 2023-03-23  34400.000000
        666587  1816050654 2023-03-24  35750.000000
        [666588 rows x 3 columns],
        'open':
                 listingid        date          Open
        0         20108704  2022-01-03  16092.826595
        1         20108704  2022-01-04  16284.979749
        2         20108704  2022-01-05  16477.132902
        3         20108704  2022-01-06  15852.635154
        4         20108704  2022-01-07  15564.405424
        ...            ...         ...           ...
        664804  1816050654  2023-03-20  30300.000000
        664805  1816050654  2023-03-21  33050.000000
        664806  1816050654  2023-03-22  31900.000000
        664807  1816050654  2023-03-23  31350.000000
        664808  1816050654  2023-03-24  35000.000000

    """

    datafileid, datafilename = parse_datafiles_to_datafileid(datafile)

    headers = _authentication()
    with Loader("\rFetching Data...") as l:
        try:
            res = requests.get(URL_DATA_FILES + f"/{datafileid}", headers=headers)
        except:
            l.stop()
            raise PrismResponseError("Request ended with an error!")
        if res.status_code >= 400:
            l.stop()
            return _process_response(res)
    link_and_filename = _process_response(res)
    link_filename = link_and_filename["link"].split(".")[0] + ".zip"
    data_link_presigned = [link_filename]

    datalink = requests.post(url=URL_STATIC, json=data_link_presigned, headers=headers)
    datalink = orjson.loads(datalink.content)["rescontent"]["data"]["url"][0]

    content = download(datalink)
    ret_dict, _ = _process_fileresponse(res, content, file_type='zip')
    ret = {k.split(".parquet")[0]: v for k, v in ret_dict.items()}
    logger.info(f"\n\nExported Data {datafilename} has components: {list(ret.keys())}\n\n")
    return ret


@_validate_args
def rename_datafiles(old: Union[str, int], new: str):
    """
    Rename datafiles. Location of datafile within the folder structure can be changed using the method.

    Parameters
    ----------
        old: str
            Name of existing datafile (str) or datafile id (str) to be renamed.
        new: str
            New name of the datafile.

    Returns
    -------
        status: dict
            Status of rename datafile.

    Examples
    --------
        >>> ps.rename_datafiles("test_single_q", "new_datafile")
        Data File renamed
        {'status': 'Success',
        'message': 'Data File renamed',
        'result': [{'resulttype': 'datafilepath',
        'resultvalue': 'superuser/datafile/new_datafile.ped'}]}

    """
    should_overwrite, err_msg = should_overwrite_datafile(new, "renaming")
    if not should_overwrite:
        return err_msg
    datafileid, _ = parse_datafiles_to_datafileid(old)
    ret = patch(URL_DATA_FILES + f"/{datafileid}", {"newpath": new + ".ped"}, None)
    logger.info(ret["message"])
    return ret


@_validate_args
def delete_datafiles(datafile: Union[str, int]):
    """
    Delete datafile.

    Parameters
    ----------
        datafile : str
            Datafile name (str) or datafile id (str) to delete.

    Returns
    -------
        status: dict
            Status of delete_datafiles.

    Examples
    --------
        >>> ps.delete_datafiles("new_datafile")
        Data file deleted
        {'status': 'Success',
        'message': 'Data file deleted',
        'result': [{'resulttype': 'datafileid', 'resultvalue': '05bca9b2'}]}

    """
    fileid, _ = parse_datafiles_to_datafileid(datafile)
    ret = delete(URL_DATA_FILES + f"/{fileid}")
    logger.info(ret["message"])
    return ret


def parse_datafiles_to_datafileid(datafile: Union[str, int]):
    datafiles_df = _fetch_and_parse(URL_DATA_FILES, "ped")
    if datafiles_df.empty:
        raise PrismNotFoundError("No Exported Data found.")

    datafiles_result = datafiles_df[datafiles_df["datafileid"] == datafile]

    if not datafile:
        raise PrismValueError("Please provide filename or fileid.")
    if datafiles_result.empty:
        datafiles_result = datafiles_df[datafiles_df["datafilename"] == datafile]

    if datafiles_result.empty:
        raise PrismNotFoundError(f"No Exported Data matching: {datafile}", True, None)
    datafileid = datafiles_result["datafileid"].values[0]
    datafilename = datafiles_result["datafilename"].values[0]

    return datafileid, datafilename


def should_overwrite_datafile(datafilename, operation):
    datafiles_df = _fetch_and_parse(URL_DATA_FILES, "ped")
    if datafiles_df.empty:
        return True, None

    if datafilename in datafiles_df["datafilename"].to_list():
        overwrite = input(f"{datafilename} already exists. Do you want to overwrite? (Y/N) \n")
        if overwrite.lower() == "y":
            return True, None
        elif overwrite.lower() == "n":
            return False, f"Not {operation} Export Data."
        else:
            return False, "Please provide a valid input."
    else:
        return True, None