import copy
import logging
from typing import Union

import requests

import prismstudio
from prismstudio._utils.exceptions import PrismNotFoundError, PrismResponseError, PrismValueError
from ..._common.config import *
from ..._common import const
from ..._core._req_builder import _dataquery
from .preference import get_quiet_mode
from ..._utils import _validate_args, post, patch, delete, _authentication, _fetch_and_parse, plot_tree


__all__ = [
    "list_taskquery",
    "load_taskquery",
    "save_taskquery",
    "delete_taskquery",
    "rename_taskquery",
    "extract_taskquery",
]

logger = logging.getLogger()


@_validate_args
def list_taskquery(search: str = None, tree=False):
    """
    Return the list of all saved task queries available.

    Parameters
    ----------
        search : str, default None
            | Search word for task query name, the search is case-insensitive.
            | If None, the entire list is returned.

        tree : bool, default False
            | If True, the folder structure of the data queries is visualized in a UNIX-style.

    Returns
    -------
        str or pandas.DataFrame
            | If tree is True, print file system tree of task queries.
            | If tree is False, return usable taskqueries in pandas.DataFrame.
            | Columns:

            - *taskqueryid*
            - *taskqueryname*

    Examples
    --------
        >>> ps.list_taskquery()
        taskqueryid  taskqueryname
        0  	         1	       screen
        1	           2	    ex_factor
        2	           3	  ex_strategy
    """

    taskqueries_df = _fetch_and_parse(URL_TASKQUERIES, "ptq", search)
    if taskqueries_df.empty:
        raise PrismNotFoundError("No Taskqueries found.")
    if not tree:
        return taskqueries_df
    plot_tree(taskqueries_df["taskqueryname"].tolist(), "taskquery")


@_validate_args
def load_taskquery(taskquery: Union[str, int]):
    """
    Load specified task queries.

    Parameters
    ----------
        taskquery : str or int
            Task query name (str) or task query id (int) to load.

    Returns
    -------
        prismstudio._PrismComponent
            Return task query component.

    Examples
    --------
        >>> ps.load_taskquery(3)
        === Task Query Structure
    """

    headers = _authentication()
    taskqueryid = parse_taskquery_to_taskqueryid(taskquery)
    res = requests.get(url=URL_TASKQUERIES + f"/{taskqueryid}", headers=headers)
    if not res.ok:
        raise PrismResponseError(res.json()["message"])
    query = res.json()["rescontent"]["data"]["taskquerybody"]
    componentinfo = const.CategoryComponent[
        const.CategoryComponent["componentid"]==query["componentid"]
        & const.CategoryComponent["categoryid"]==query["categoryid"]
    ]
    component_name = componentinfo["component_name_repr"].values[0]
    component = getattr(prismstudio, component_name)
    component_args = query["component_args"]
    for k in copy.deepcopy(list(component_args.keys())):
        if "_dataquery" in k:
            arg_key = k.split("_dataquery")[0]
            dataquery = _dataquery._dataquery_to_component(component_args.pop(k))
            component_args[arg_key] = dataquery
        if k.endswith("id"):
            component_args[k.split("id")[0]] = component_args.pop(k)
        if k == 'newuniversepath':
            component_args.pop('newuniversepath')
    result = component(**component_args)
    return result


@_validate_args
def save_taskquery(component, taskqueryname: str):
    """
    Save task query.

    Parameters
    ----------
        component : prismstudio._PrismComponent
            New PrismComponent to be saved.

        taskqueryname : str
            Name of the new task query.

    Returns
    -------
        status: dict
            Status of save_taskquery.

    Examples
    --------
        >>> ps.list_taskquery()
        taskqueryid  taskqueryname
        0  	         1	       screen
        1	           2	    ex_factor
        2	           3	  ex_strategy

        >>> mcap = ps.market.market_cap()
        >>> marketcap_rule = mcap.cross_sectional_rank() <= 200 # Top 200 market capitalization
        >>> snp_200_screen = ps.screen(
                rule=marketcap_rule,
                universe="S&P 500",
                startdate="2010-01-01",
                enddate="2015-01-01",
                frequency="D",
                )
        >>> ps.save_taskquery(component=snp_200_screen,taskqueryname="mcap_200")
        {
        'status': 'Success',
        'message': 'Taskquery saved',
        'result': [{'resulttype': 'taskqueryid', 'resultvalue': 4}]
        }

        >>> ps.list_taskquery()
        taskqueryid  taskqueryname
        0  	         1	       screen
        1	           2	    ex_factor
        2	           3	  ex_strategy
        3	           4	     mcap_200
    """
    should_overwrite, err_msg = should_overwrite_taskquery(taskqueryname, "saving")
    if not should_overwrite:
        return err_msg
    ret = post(
        URL_TASKQUERIES,
        {
            "path": taskqueryname + ".ptq",
        },
        component._query,
    )
    logger.info(f'{ret["message"]}: {ret["result"][0]["resulttype"]} is {ret["result"][0]["resultvalue"]}')
    return ret


@_validate_args
def rename_taskquery(old: Union[str, int], new: str):
    """
    Rename task query. Location of task query within the folder structure can be changed using the method.

    Parameters
    ----------
        old : str or int
            Name of existing task query (str) or task query id (int) to be renamed.

        new : str
            New name of the task query.

    Returns
    -------
        status: dict
            Status of rename_taskquery.

    Examples
    --------
        >>> ps.list_taskquery()
        taskqueryid  taskqueryname
        0  	         1	       screen
        1	           2	    ex_factor
        2	           3	  ex_strategy

        >>> ps.rename_taskquery(old="screen", name="new_screen")
        {
        'status': 'Success',
        'message': 'Taskquery renamed',
        'result': [{'resulttype': 'taskqueryid', 'resultvalue': 1}]
        }

        >>> ps.list_taskquery()
        taskqueryid  taskqueryname
        0  	         1	   new_screen
        1	           2	    ex_factor
        2	           3	  ex_strategy
    """
    should_overwrite, err_msg = should_overwrite_taskquery(new, "renaming")
    if not should_overwrite:
        return err_msg
    taskqueryid = parse_taskquery_to_taskqueryid(old)
    ret = patch(URL_TASKQUERIES + f"/{taskqueryid}", {"newpath": new + ".ptq"}, None)
    logger.info(ret["message"])
    return ret


@_validate_args
def delete_taskquery(taskquery: Union[str, int]):
    """
    Delete task query.


    Parameters
    ----------
        taskquery : str or int
            Task query name (str) or task query id (int) to delete.

    Returns
    -------
        status: dict
            Status of delete_taskquery.

    Examples
    --------
        >>> ps.list_taskquery()
        taskqueryid  taskqueryname
        0  	         1	       screen
        1	           2	    ex_factor
        2	           3	  ex_strategy

        >>> ps.delete_taskquery(1)
        Taskquery deleted
        {
        'status': 'Success',
        'message': 'Taskquery deleted',
        'result': [{'resulttype': 'taskqueryid', 'resultvalue': 1}]
        }

        >>> ps.list_taskquery()
        taskqueryid  taskqueryname
        0	           2	    ex_factor
        1	           3	  ex_strategy

        >>> ps.delete_taskquery("ex_factor")
        Taskquery deleted
        {
        'status': 'Success',
        'message': 'Taskquery deleted',
        'result': [{'resulttype': 'taskqueryid', 'resultvalue': 2}]
        }

        >>> ps.list_taskquery()
        taskqueryid  taskqueryname
        0	           3	  ex_strategy
    """
    dataqueryid = parse_taskquery_to_taskqueryid(taskquery)
    ret = delete(URL_TASKQUERIES + f"/{dataqueryid}")
    logger.info(ret["message"])
    return ret


@_validate_args
def extract_taskquery(component, return_code=False):
    """
    Generate code which reproduces the task query provided by the component. If return_code is False, the method returns None and prints the code.

    Parameters
    ----------
        component : PrismComponent
            PrismComponent whose task query is to be extracted. Task component should be provided.

        return_code : bool, default False
            If True, the method returns the code. Else the code is printed as system output, returning None.

    Returns
    -------
        str or None
            | If return_code is True, return code in string.
            | If return_code is False, return None.

    Examples
    --------
        >>> mcap = ps.market.market_cap()
        >>> marketcap_rule = mcap.cross_sectional_rank() <= 200 # Top 200 market capitalization
        >>> snp_200_screen = ps.screen(
                rule=marketcap_rule,
                universe="S&P 500",
                startdate="2010-01-01",
                enddate="2015-01-01",
                frequency="D",
                )

        >>> ps.extract_dataquery(snp_200_screen)
        x0= prismstudio.market.market_cap()
        x1 = x0.cross_sectional_rank() <= 200
        x2 = prismstudio.screen(
                        rule=x1,
                universe="S&P 500",
                startdate="2010-01-01",
                enddate="2015-01-01",
                frequency="D",
                )
    """
    code = post(URL_TASKQUERIES + '/extract', {'dialect': 'python'}, component._query)
    if return_code:
        return code
    else:
        logger.info(code)


@_validate_args
def parse_taskquery_to_taskqueryid(taskquery: Union[str, int]):
    taskqueries_df = _fetch_and_parse(URL_TASKQUERIES, "ptq")
    if taskqueries_df.empty:
        raise PrismNotFoundError("No Taskquery found.")

    if isinstance(taskquery, int):
        taskqueries_df = taskqueries_df[taskqueries_df["taskqueryid"] == taskquery]
    elif isinstance(taskquery, str):
        taskqueries_df = taskqueries_df[taskqueries_df["taskqueryname"] == taskquery]
    else:
        raise PrismValueError("Please provide taskquery path or taskquery id for taskquery.")

    if taskqueries_df.empty:
        raise PrismNotFoundError(f"No taskquery matching: {taskquery}")

    taskqueryid = taskqueries_df["taskqueryid"].values[0]
    return taskqueryid


def should_overwrite_taskquery(taskqueryname, operation):
    if get_quiet_mode():
        return True, None
    taskqueries_df = _fetch_and_parse(URL_TASKQUERIES, "ptq")
    if taskqueries_df.empty:
        return True, None

    if taskqueryname in taskqueries_df["taskqueryname"].to_list():
        overwrite = input(f"{taskqueryname} already exists. Do you want to overwrite? (Y/N) \n")
        if overwrite.lower() == "y":
            return True, None
        elif overwrite.lower() == "n":
            return False, f"Not {operation} taskquery."
        else:
            return False, "Please provide a valid input."
    else:
        return True, None
