import copy
import logging
from typing import Union

from ..._common.config import URL_TASK, URL_UNIVERSES
from ..._common import const
from ..._core._req_builder._universe import should_overwrite_universe, parse_universe_to_universeid
from ..._prismcomponent import prismcomponent as pcmpt, abstract_prismcomponent
from ..._prismcomponent.prismcomponent import _PrismTaskComponent
from ..._utils import (
    get as _get,
    _validate_args,
    are_periods_exclusive as _are_periods_exclusive,
    Loader, post as _post,
)
from ..._utils.exceptions import PrismTaskError, PrismValueError, PrismTypeError


_data_category = __name__.split(".")[-1]

logger = logging.getLogger()


class screen(_PrismTaskComponent):
    """
    Enables users to quickly construct custom time-variant universes through user defined rules to evaluate over the specified startdate and endddate.

    Parameters
    ----------
        rule : abstract_prismcomponent._AbstractPrismComponent
            A boolean-type query in time series used to define the screening rule.

        universe : Union[int, str]
            The universe of securities to evaluate. Can be specified as a string (name of the universe)
            or an integer (universe ID).

        frequency : str
            Desired sampling frequency for resampling.
            Format: 'XBF-S', where:
                - X: Resampling interval (optional, defaults to 1).
                - B: Business frequency (optional, aligns with business days if specified).
                - F: Frequency type (D, W, M, Q, SA, A).
                - S: Specific aspect of the frequency (optional, depends on F).

            Frequency Examples:
                - '3M-25': Resample every 3 months on the 25th day of the month.
                - '2W-Fri': Resample every 2 weeks on Fridays.
                - 'A-12/15': Resample every year on December 15th.

            Notes:
                - For quarterly (Q) frequency, resampling results occur in March, June, September, and December.
                - For semi-annual (SA) frequency, resampling results occur in June and December.
                - Use '3M' or '6M' for dynamic months instead of 'Q' or 'SA'.

        startdate : str
            Start date of the time period to load data or run the task. If specified, it overrides the
            startdate parameter in the task component.

        enddate : str, optional, default=None
            End date of the time period to load data or run the task. If None it will run the screen upto today.

    Returns
    -------
        status : dict
            | Returns 'Pending' status.
            | Screening task is added to system task queue.

    Examples
    --------
        >>> ps.list_universe()
        universeid                 universename  universetype   startdate     enddate
        0           1  Korea Stock Price 200 Index         index  1700-01-01  2199-12-31
        1           2                      S&P 500         index  1700-01-01  2199-12-31
        2           3    Russell 3000 Growth Index         index  1700-01-01  2199-12-31
        3           4           Russell 3000 Index         index  1700-01-01  2199-12-31

        >>> mcap = ps.market.market_cap()
        >>> marketcap_rule = mcap.cross_sectional_rank() <= 200 # Top 200 market capitalization
        >>> snp_200_screen = ps.screen(
                rule=marketcap_rule,
                universename="S&P 500",
                startdate="2010-01-01",
                enddate="2015-01-01",
                frequency="D",
            )
        >>> snp_200_screen.run(newuniversename="snp_200")
        {'status': 'Pending',
        'message': 'screen pending',
        'result': [{'resulttype': 'jobid', 'resultvalue': 5}]}

        >>> ps.job_manager()
        >>> # Wait for the job 5 in GUI until its status changed to 'Completed'

        >>> ps.list_universe()
        universeid                 universename  universetype   startdate     enddate
        0           1  Korea Stock Price 200 Index         index  1700-01-01  2199-12-31
        1           2                      S&P 500         index  1700-01-01  2199-12-31
        2           3    Russell 3000 Growth Index         index  1700-01-01  2199-12-31
        3           4           Russell 3000 Index         index  1700-01-01  2199-12-31
        4           5                      snp_200         index  2010-01-01  2015-01-01
    """
    _component_category_repr = _data_category

    @_validate_args
    def __init__(
        self,
        rule: abstract_prismcomponent._AbstractPrismComponent,
        universe: Union[int, str],
        frequency: str,
        startdate: str = None,
        enddate: str = None,
    ):
        if isinstance(rule, pcmpt._PrismDataComponent) or const.FunctionComponents[const.FunctionComponents["componentid"]==rule.componentid]["categoryname"].values[0] != "Logical":
            raise PrismTypeError("screen task only available to boolean operations.")
        universeid, _ = parse_universe_to_universeid(universe)

        universe_info = _get(f"{URL_UNIVERSES}/{universeid}/info")
        universe_startdate = universe_info["Start Date"].values[0]
        universe_enddate = universe_info["End Date"].values[0]

        universe_period_violated = _are_periods_exclusive(universe_startdate, universe_enddate, startdate, enddate)

        if universe_period_violated:
            raise PrismValueError(
                f'Screen period should overlap with universe period ({str(universe_startdate).split("T")[0]} ~ {str(universe_enddate).split("T")[0]})'
            )

        super().__init__(
            rule_dataquery=[rule._query],
            universeid=int(universeid),
            frequency=frequency,
            startdate=startdate,
            enddate=enddate,
        )

    @_validate_args
    def run(
        self,
        newuniversename: str,
        jobname: str = None,
        frequency: str = None,
        startdate: str = None,
        enddate: str = None,
    ):
        """
        Enables users to quickly construct custom time-variant universes through user defined rules to evaluate over the specified startdate and endddate.

        Parameters
        ----------
            newuniversename : str
                Name of the universe to be created.

        """
        should_overwrite, err_msg = should_overwrite_universe(newuniversename, "screening")
        if not should_overwrite:
            logger.info(f"{err_msg}")
            return
        component_args = copy.deepcopy(self._query["component_args"])
        universeid = component_args.pop("universeid")
        component_args.update({"universeid": int(universeid)})

        universe_info = _get(f"{URL_UNIVERSES}/{universeid}/info")
        universe_startdate = universe_info["Start Date"].values[0]
        universe_enddate = universe_info["End Date"].values[0]
        component_args.update({"newuniversepath": newuniversename + ".puv"})

        if frequency is not None:
            component_args["frequency"] = frequency
        if startdate is not None:
            component_args["startdate"] = startdate
        if enddate is not None:
            component_args["enddate"] = enddate

        universe_period_violated = _are_periods_exclusive(
            universe_startdate, universe_enddate, component_args.get("startdate"), component_args.get("enddate")
        )

        if universe_period_violated:
            raise PrismValueError(
                f'Screen period should overlap with universe period ({str(universe_startdate).split("T")[0]} ~ {str(universe_enddate).split("T")[0]})'
            )

        query = {
            "component_type": self._query["component_type"],
            "componentid": self._query["componentid"],
            "component_args": component_args,
        }

        rescontent = None
        with Loader("Screen Running... ") as l:
            try:
                rescontent = _post(f"{URL_TASK}/{self.componentid}", params={"jobname": jobname}, body=query)
            except:
                l.stop()
                raise PrismTaskError("Screen has failed.")
            if rescontent["status"] != "Pending":
                l.stop()
                raise PrismTaskError("Screen has failed.")

        logger.info(f'{rescontent["message"]}')
        return rescontent

    @classmethod
    def list_job(cls):
        """
        List all screen jobs.

        Returns
        -------
            pandas.DataFrame
                All screen jobs.
            Columns
                - *jobid*
                - *jobname*
                - *jobstatus*
                - *starttime*
                - *endtime*
                - *frequency*
                - *screeneduniverseid*
                - *screeneduniversepath*
                - *universepath*
                - *universeid*
                - *description*
                - *period*

        Examples
        --------
        >>> ps.screen_jobs()
        jobid  jobname  jobstatus                starttime                        endtime  frequency  screeneduniverseid  ...  universeid  description                   period
        0      1     None  Completed  2022-06-30 03:51:13.630  2022-06-30 03:51:18.388999936          Q                 9.0  ...         7.0         None  2010-01-01 ~ 2015-01-01
        1      2     None  Completed  2022-06-30 03:49:24.680  2022-06-30 03:49:28.556000000          Q                 8.0  ...	     7.0         None  2010-01-01 ~ 2015-01-01
        2      3     None  Completed  2022-06-27 17:37:27.386  2022-06-27 17:37:51.248000000          Q                 9.0  ...         7.0         None  2010-01-01 ~ 2015-01-01
        """
        return cls._list_job()
