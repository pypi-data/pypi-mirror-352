import copy
import logging
import webbrowser
from typing import List, Union

import requests
import pandas as pd
import pyarrow as pa

from ..._common.config import *
from ..._common.config import URL_TASK, URL_UNIVERSES, URL_UPLOAD
from ..._common.const import (
    RankType as _RankType,
    CurrencyTypeWithReportTrade as _CurrencyTypeWithReportTrade
)
from ..._core._req_builder._universe import parse_universe_to_universeid
from ..._core._req_builder._portfolio import parse_portfolios_to_portfolioids
from ..._core._req_builder._portfolio import should_overwrite_portfolio
from ..._utils import (
    _authentication,
    get,
    _process_fileresponse,
    _validate_args,
    _get_web_authentication_token,
    are_periods_exclusive,
    Loader, post, get, are_periods_exclusive,
)
from ..._utils.exceptions import PrismTaskError, PrismValueError
from ..._prismcomponent import abstract_prismcomponent
from ..._prismcomponent.prismcomponent import _PrismTaskComponent

_data_category = __name__.split(".")[-1]

logger = logging.getLogger()

class PrismBacktestTaskComponent(_PrismTaskComponent):
    _component_category_repr = _data_category

    @classmethod
    def _get_task_result(cls, tasktype, tasktyperepr, resultid: list, data: bool = True, report: bool = True):
        if (data == False) and (report == False):
            raise PrismValueError("Either data or report should be true.")
        if report:
            # Format Definition:
            # Webclient Address/report/report_type/file_id?token=web_auth_token
            url_get_results = [f"{URL_TASK}/{cls.componentid}/report/{i}" for i in resultid]
            fileids = [get(url)["path"].values[0] for url in url_get_results]

            web_auth_token = _get_web_authentication_token()

            logger.info("Fetching link to " + tasktyperepr + " Report...")
            for idx, i in enumerate(fileids):
                link = f"{ROOT_EXT_WEB_URL}/report/{cls.__name__}/{i}"
                logger.info(f"Link to {tasktyperepr} Report {resultid[idx]}:")
                logger.info(link)

            if len(resultid) == 1:
                link = link[:-1] + "?token=" + web_auth_token
                webbrowser.open(link, new=2)

        if data:
            url_get_results = [f"{URL_TASK}/{cls.componentid}/result/{i}" for i in resultid]
            logger.info("Fetching " + tasktyperepr + " Result Data...")
            headers = _authentication()
            ret = {}
            for idx, i in enumerate(resultid):
                res = requests.get(url_get_results[idx], headers=headers)
                ret_dict, _ = _process_fileresponse(res, res.content)
                ret[i] = {k.split(".parquet")[0]: v for k, v in ret_dict.items()}
            return list(ret.values())[0] if len(ret) == 1 else ret


class factor_backtest(PrismBacktestTaskComponent):
    """
    Enables users to quickly test and identify factors which may predict future return.

    Parameters
    ----------

        factor : Union[abstract_prismcomponent._AbstractPrismComponent]
            The factor to be backtested. Can be an abstract prism component.

        universe : Union[int, str]
            The universe of securities to analyze. Can be provided as an integer ID or a string name.

        frequency : str
            Desired sampling frequency for resampling.
            Format: 'XBF-S' where:
                - X: Resampling interval (optional, default is 1)
                - B: Business frequency (optional)
                - F: Frequency type (D, W, M, Q, SA, A)
                - S: Specific aspect of the frequency (optional)
            Examples:
                - '3M-25': Resample every 3 months on the 25th day of the month.
                - '2W-Fri': Resample every 2 weeks on Fridays.
                - 'A-12/15': Resample every year on December 15th.

        bins : int
            | Number of quantile portfolio the universe generate. Should be bigger than 1 and smaller than or equal to 20.
            | If specified, this will overwrite bins parameter in the task component.

            .. admonition: Note
                :class: note

                Bins are assigned to the factor score in descending order. Meaning the largest factor score will be assigned 1st bin

        startdate : str, optional, default=None
            Start date for the analysis period. Overrides the startdate parameter in the task component if specified.

        enddate : str, optional, default=None
            End date for the analysis period. Overrides the enddate parameter in the task component if specified.

        weekend : str, default="Sat-Sun"
            Defines the weekend days, which may vary depending on the region or market.

        holiday_country : str, optional, default=None
            Specifies the country for determining holidays, used for adjusting resampling and analysis schedules.

        max_days : int, optional, default=None
            Maximum number of days to consider for each backtesting window. If None, it is inferred from the rebalancing frequency.

        rank_method : str, {'standard', 'modified', 'dense', 'ordinal', 'fractional'}, default='standard'
            Specifies how equal values are assigned ranks:
                - 'standard': Ranks equal values using their position in the sorted order (e.g., 1 2 2 4).
                - 'modified': Ranks equal values with the next rank skipped (e.g., 1 3 3 4).
                - 'dense': Ranks equal values without skipping (e.g., 1 2 2 3).
                - 'ordinal': Assigns unique ranks in the order of appearance (e.g., 1 2 3 4).
                - 'fractional': Uses fractional ranking (e.g., 1 2.5 2.5 4).


    Returns
    -------
        status : dict
            Status of factorbacktest run.

    Examples
    --------
        >>> ni = ps.financial.income_statement(dataitemid=100639, periodtype='LTM')
        >>> mcap = ps.market.market_cap()
        >>> ep = ni / mcap
        >>> fb_ep = ps.factor_backtest(
                factor=ep,
                universe='Russell 3000 Index',
                frequency='Q',
                bins=5,
                startdate='2010-01-01',
                enddate='2015-01-01'
            )
        >>> fb_price_mom.run(jobname="factor_backtest_ep")
        factor_backtest is added to worker queue!: jobid is 1

        >>> ps.job_manager()
        >>> # Wait for the job 1 in GUI until its status changed to 'Completed'

        >>> ps.factor_backtest.get_result(1)
        Done!
        factor_backtest Completed: factorbacktestid is 1
        Fetching A Link to Factor Backtest Report...
        Link to Factor Backtest Report:
        https://ext.prism39.com/report/factor_backtest/my_username_1_afc7730c-55e6-41a8-ad4f-77df20caecc9/
    """
    @_validate_args
    def __init__(
        self,
        factor: Union[abstract_prismcomponent._AbstractPrismComponent, pd.DataFrame],
        universe: Union[int, str],
        frequency: str,
        bins: int,
        startdate: str = None,
        enddate: str = None,
        weekend: str = "Sat-Sun",
        holiday_country: str = None,
        max_days: int = None,
        rank_method: _RankType = "standard",
    ):
        if (bins < 2) or (bins > 20):
            PrismValueError("The number of bins should be between 2 and 20")

        if not isinstance(factor, list):
            factor = [factor]
        factor_ = []
        for f in factor:
            if isinstance(f, pd.DataFrame):
                if len(set(f.columns) & {"date", "listingid", "value"}) != 3:
                    raise PrismValueError("Columns should be: date, listingid, value")
                if f.empty:
                    raise PrismValueError("Dataframe should not be empty")
                factor_.append(f)
            elif isinstance(f, abstract_prismcomponent._AbstractPrismComponent):
                factor_.append(f._query)
            else:
                raise PrismValueError("Factor should be either prism component or a pandas dataframe")

        universeid, _ = parse_universe_to_universeid(universe)

        universe_info = get(f"{URL_UNIVERSES}/{universeid}/info")
        universe_startdate = universe_info["Start Date"].values[0]
        universe_enddate = universe_info["End Date"].values[0]

        universe_period_violated = are_periods_exclusive(universe_startdate, universe_enddate, startdate, enddate)

        if universe_period_violated:
            raise PrismValueError(
                f'Factor Backtest period should overlap with universe period ({str(universe_startdate).split("T")[0]} ~ {str(universe_enddate).split("T")[0]})'
            )

        return super().__init__(
            factor_dataquery=factor_,
            universeid=int(universeid),
            frequency=frequency,
            bins=bins,
            rank_method=rank_method,
            max_days=max_days,
            startdate=startdate,
            enddate=enddate,
            weekend=weekend,
            holiday_country=holiday_country,
        )

    @_validate_args
    def run(
        self,
        jobname: Union[str, list] = None,
        frequency: str = None,
        bins: int = None,
        startdate: str = None,
        enddate: str = None,
        weekend: str = None,
        holiday_country: str = None,
        max_days: int = None,
        rank_method: str = None,
    ):
        """
        Enables users to quickly test and identify factors which may predict future return.

        Parameters
        ----------
            jobname : str
                | Name of the job when the task component is run.
                | If None, the default job name sets to factorbacktest_{jobid}.

            frequency : str
                | Desired sampling frequency to resample.
                |
                | Frequency Format
                | Description: The 'frequency format' combines all the elements of the 'frequency' parameter, providing a comprehensive way to specify the resampling frequency.
                | Format: XBF-S
                |
                | Elements of the frequency Parameter
                | X: Resampling Interval (Optional, If not given, it is defaults to be 1, meaning resampling occurs every data point)
                | Description: The 'X' element represents the number at which resampling should be operated. It determines how often data should be resampled.
                |
                | B: Business Frequency (Optional, If not given, it is assumed to be a non-business frequency)
                | Description: The 'B' element indicates whether the resampling frequency should align with business days. If 'B' is included, it signifies a business frequency; otherwise, it's not considered.
                |
                | F: Frequency Type
                | Description: The 'F' element specifies the frequency type, which defines the unit of time for resampling. It can take on one of the following values: [D, W, M, Q, SA, A].
                |
                | S: Specific Part of Frequency (Optional)
                | Description: The 'S' element is an optional part of the 'frequency' parameter, and its presence depends on the chosen frequency type ('F'). It allows you to specify a particular aspect of the resampling frequency.
                |

                    | Specific Part for Each Frequency Type
                    | A (Annual) Frequency - MM/dd (Months and Day)
                    |    Example: A-12/15 (Resample every year on December 15th)
                    |
                    | M (Monthly), Q (Quarterly), SA (Semi-Annual) Frequencies - dd (Day of the Month)
                    |    Example: 3M-25 (Resample every 3 months on the 25th day of the month)
                    |
                    | W (Weekly) Frequency - Day of the Week (Case Insensitive)
                    |    Example: 2W-Fri (Resample every 2 weeks on Fridays)
                    |
                    | D (Daily) Frequency - N/A (If specific part is given it will raise an error)

                .. admonition:: Note
                    :class: note

                    | Result for certain frequencies
                    |
                    | For Q (Quarterly) frequency, the resampled results can only be for the months of March, June, September, and December.
                    | For SA (Semi-Annual) frequency, the resampled results can only be for the months of June and December.
                    | For dynamic months, use 3M instead of Q and 6M instead of SA.

                | Example
                - 3M-25: Resample every 3 months on the 25th day of the month.
                - 3D: Resample every 3 days.
                - 2BM-15: Resample every 2 months on the 15th day of the month, considering business days.
                - A-12/15: Resample every year on December 15th.
                - 2BQ-3: Resample every 2 quarters, on the 3rd day of the month, considering business days.

            lookback : int
                The periods to lookback are defined by the resampling frequency parameter. For example, if resampling to Monthly data, this will lookback *lookback* Months.

                .. admonition:: Note
                    :class: note

                    | When up-sampling, the lookback input parameter must be specified properly.
                    |
                    | For example, if resampling from Quarterly data to Monthly data, the lookback should be at least '3' or larger.
                    | If set to only '1', then the lookback will not look far enough back to fill in every month and missing values will be left in the output time-series.
                    | If no input is supplied, it will go back to the last data available and fill in every missing value in between.


            bins : int
                | Number of quantile portfolio the universe generate. Should be bigger than 1 and smaller than or equal to 20.
                | If specified, this will overwrite bins parameter in the task component.

                .. admonition: Note
                    :class: note

                    Bins are assigned to the factor score in descending order. Meaning the largest factor score will be assigned 1st bin

            startdate : str, default None
                | Startdate of the time period for which to load data or the window in time in which to run a task.
                | If specified, this will overwrite startdate parameter in the task component.

            enddate : str, default None
                | Enddate of the time period for which to load data or the window in time in which to run a task.
                | If specified, this will overwrite enddate parameter in the task component.

            max_days : int, default None
                | If None, default max days is induced from rebalancing frequency.
                | If specified, this will overwrite max_days parameter in the task component.

            rank_method : str {'standard', 'modified', 'dense', 'ordinal', 'fractional'}, default 'standard'
                | Method for how equal values are assigned a rank.

                - standard : 1 2 2 4
                - modified : 1 3 3 4
                - dense : 1 2 2 3
                - ordinal : 1 2 3 4
                - fractional : 1 2.5 2.5 4

                | Desired rebalancing frequency to run screen.
                | If specified, this will overwrite rank_method parameter in the task component.

        Returns
        -------
            status : dict
                Status of factorbacktest run.

        Examples
        --------
            >>> ni = ps.financial.income_statement(dataitemid=100639, periodtype='LTM')
            >>> mcap = ps.market.market_cap()
            >>> ep = ni / mcap
            >>> fb_ep = ps.factor_backtest(
                    factor=ep,
                    universe='Russell 3000 Index',
                    frequency='Q',
                    bins=5,
                    startdate='2010-01-01',
                    enddate='2015-01-01'
                    )
            >>> fb_price_mom.run(jobname="factor_backtest_ep")
            factor_backtest is added to worker queue!: jobid is 1

            >>> ps.job_manager()
            >>> # Wait for the job 1 in GUI until its status changed to 'Completed'

            >>> ps.factor_backtest.get_result(1)
            Done!
            factor_backtest Completed: factorbacktestid is 1
            Fetching A Link to Factor Backtest Report...
            Link to Factor Backtest Report:
            https://ext.prism39.com/report/factor_backtest/my_username_1_afc7730c-55e6-41a8-ad4f-77df20caecc9/
        """
        component_args = copy.deepcopy(self._query["component_args"])
        universeid = component_args.pop("universeid")
        component_args["universeid"] = int(universeid)

        universe_info = get(f"{URL_UNIVERSES}/{universeid}/info")
        universe_startdate = universe_info["Start Date"].values[0]
        universe_enddate = universe_info["End Date"].values[0]

        if frequency is not None:
            component_args["frequency"] = frequency
        if bins is not None:
            component_args["bins"] = bins
        if rank_method is not None:
            component_args["rank_method"] = rank_method
        if max_days is not None:
            component_args["max_days"] = max_days
        if startdate is not None:
            component_args["startdate"] = startdate
        if enddate is not None:
            component_args["enddate"] = enddate
        if weekend is not None:
            component_args["weekend"] = weekend
        if holiday_country is not None:
            component_args["holiday_country"] = holiday_country

        universe_period_violated = are_periods_exclusive(
            universe_startdate, universe_enddate, component_args.get("startdate"), component_args.get("enddate")
        )

        if universe_period_violated:
            raise PrismValueError(
                f'Factor Backtest period should overlap with universe period ({str(universe_startdate).split("T")[0]} ~ {str(universe_enddate).split("T")[0]})'
            )

        if (component_args["bins"] < 2) or (component_args["bins"] > 20):
            PrismValueError("The number of bins should be between 2 and 20")
        for i in range(len(component_args["factor_dataquery"])):
            if isinstance(component_args["factor_dataquery"][i], pd.DataFrame):
                headers = {"Authorization": _authentication()["Authorization"], "client": "python"}
                batch = pa.record_batch(component_args["factor_dataquery"][i])
                sink = pa.BufferOutputStream()
                with pa.ipc.new_stream(sink, batch.schema) as writer:
                    writer.write_batch(batch)
                res = requests.post(URL_UPLOAD, files={"file": sink.getvalue()}, headers=headers)
                if res.ok:
                    path = res.json()["rescontent"]["data"]["url"]

                component_args["factor_dataquery"][i] = path
        query = {
            "component_type": self._query["component_type"],
            "componentid": self._query["componentid"],
            "component_args": component_args,
        }
        custom_data = [isinstance(f, str) for f in component_args["factor_dataquery"]]

        rescontent = None
        with Loader("Factor Backtest Running... ") as l:
            try:
                rescontent = post(
                    f"{URL_TASK}/{self.componentid}",
                    params={"jobname": jobname, "custom_data": custom_data},
                    body=query,
                )
            except:
                l.stop()
                raise PrismTaskError("Factor Backtest has failed.")
            if rescontent["status"] != "Pending":
                l.stop()
                raise PrismTaskError("Factor Backtest has failed.")

        logger.info(
            f'{rescontent["message"]}: {rescontent["result"][0]["resulttype"]} is {rescontent["result"][0]["resultvalue"]}'
        )

        logger.info(f'{rescontent["message"]}')
        return rescontent

    @classmethod
    @_validate_args
    def get_result(cls, fbid: Union[list, int], data=True, report=False):
        """
        Return factor backtested result.

        Parameters
        ----------
            fbid: int
                | Specify the factor backtest id.

            data: bool, default True
                | Include dataframe in returned value.

            report: bool, default False
                | Open interactive GUI report in web browser at the end of the process.

                .. admonition:: Warning
                    :class: warning

                    Either data or report should be True.

        Returns
        -------
            report = True
                Open interactive Factor Backtest Report.

            data = True
                | data : dictionary of dataframes

                - *summary: summary of factorbacktest job*
                - *ar: annual return*
                - *counts: number of securities in each bin*
                - *ic: information coefficient*
                - *pnl: profit & losses*
                - *qr: quantile return*
                - *to: turnover*


        Examples
        --------
            >>> ps.factor_backtest.list_job()
            jobid            jobname  jobstatus  ...  factorbacktestid  avg_turnover    avg_ic  top_bottom_spread  frequency  bins  max_days  rank_method  description                   period
            0      1  factor_backtest_1  Completed  ...                 1      0.475282  0.017800          -0.000383          Q  10.0      93.0     standard         None  2013-01-01 ~ 2015-01-01

            >>> ps.factor_backtest.get_result(1, report=True)
            Fetching A Link to Factor Backtest Report...
            Link to Factor Backtest Report:
            https://ext.prism39.com/report/factor_backtest/my_username_1_14798b70-4a7a-4606-8179-44f6932f34e6/
            Fetching Factor Backtest Result Data...
            {
                'ar':
                    Top-Bottom Spread     Bin 1     Bin 2     Bin 3     Bin 4     Bin 5     Bin 6     Bin 7    Bin 8     Bin 9    Bin 10
                    0          -0.000383  0.002693  0.001911  0.001745  0.001602  0.001693  0.001987  0.001952  0.00193  0.002166  0.002148,
                'counts':
                                date  Bin 1  Bin 2  Bin 3  Bin 4  Bin 5  Bin 6  Bin 7  Bin 8  Bin 9  Bin 10
                        0  2013-03-31     49     50     50     50     50     49     50     50     50      50
                        1  2013-06-30     49     49     50     49     50     49     49     50     49      50
                        2  2013-09-30     49     50     50     49     50     50     49     50     50      50
                        3  2013-12-31     49     49     49     49     49     49     49     49     49      50
                        4  2014-03-31     49     50     50     50     50     50     50     50     50      50
                        5  2014-06-30     50     50     50     50     50     50     50     50     50      50
                        6  2014-09-30     49     50     50     50     50     49     50     50     50      50
                        7  2014-12-31     49     50     50     50     50     49     50     50     50      50,
                'ic':        date         ic
                    0  2013-03-31   0.109810
                    1  2013-06-30  -0.024280
                    2  2013-09-30   0.073506
                    3  2013-12-31  -0.007544
                    4  2014-03-31  -0.034033
                    5  2014-06-30  -0.035701
                    6  2014-09-30   0.042841,
                'pnl':       date  Top-Bottom Spread     Bin 1     Bin 2     Bin 3     Bin 4     Bin 5     Bin 6     Bin 7     Bin 8     Bin 9    Bin 10
                    0  2013-03-31          -0.026218  0.107641  0.025149  0.020147  0.029949  0.025136  0.030979  0.047745  0.050728  0.053055  0.081424
                    1  2013-06-30          -0.040646  0.198980  0.095820  0.069968  0.070595  0.093182  0.100881  0.102511  0.113004  0.111119  0.154577
                    2  2013-09-30          -0.017259  0.327730  0.210149  0.150424  0.158664  0.203366  0.209441  0.189935  0.221166  0.229827  0.306704
                    3  2013-12-31          -0.041429  0.406996  0.233885  0.190352  0.175839  0.225944  0.246494  0.231905  0.218980  0.286169  0.352579
                    4  2014-03-31          -0.077449  0.530770  0.313009  0.254870  0.254214  0.268607  0.292174  0.316257  0.289976  0.334870  0.420739
                    5  2014-06-30          -0.097823  0.533991  0.319311  0.267409  0.233913  0.252408  0.294491  0.305149  0.266159  0.332309  0.392353
                    6  2014-09-30          -0.076550  0.539356  0.382519  0.349352  0.320580  0.338911  0.397894  0.390694  0.386452  0.433719  0.430054,
                'qr':        date  Top-Bottom Spread     Bin 1     Bin 2     Bin 3      Bin 4      Bin 5     Bin 6      Bin 7      Bin 8      Bin 9     Bin 10
                    0  2013-03-31          -0.026218  0.107641  0.025149  0.020147   0.029949   0.025136  0.030979   0.047745   0.050728   0.053055   0.081424
                    1  2013-06-30          -0.014817  0.082462  0.068937  0.048838   0.039464   0.066378  0.067802   0.052270   0.059269   0.055138   0.067646
                    2  2013-09-30           0.024377  0.107383  0.104332  0.075195   0.082261   0.100792  0.098611   0.079295   0.097180   0.106836   0.131760
                    3  2013-12-31          -0.024594  0.059701  0.019615  0.034707   0.014824   0.018762  0.030637   0.035272  -0.001790   0.045813   0.035107
                    4  2014-03-31          -0.037578  0.087971  0.064125  0.054201   0.066654   0.034799  0.036646   0.068472   0.058242   0.037865   0.050393
                    5  2014-06-30          -0.022083  0.002104  0.004800  0.009992  -0.016187  -0.012769  0.001793  -0.008439  -0.018463  -0.001919  -0.019980
                    6  2014-09-30           0.023579  0.003497  0.047910  0.064654   0.070238   0.069069  0.079880   0.065544   0.095006   0.076116   0.027077,
                'summary':    username  universename   startdate     enddate frequency  bins  avg_turnover  avg_ic  top_bottom_spread
                        0  my_username       S&P 500  2013-01-01  2015-01-01         Q    10      0.475282  0.0178          -0.000383,
                'to':       date  turnover
                    0 2013-03-31  0.437751
                    1 2013-06-30  0.459514
                    2 2013-09-30  0.476861
                    3 2013-12-31  0.549898
                    4 2014-03-31  0.428858
                    5 2014-06-30  0.452000
                    6 2014-09-30  0.522088
            }
        """
        if isinstance(fbid, int):
            fbid = [fbid]
        return cls._get_task_result(cls.__class__.__name__, "Factor Backtest", fbid, data, report)

    @classmethod
    def list_job(cls):
        """
        List all factor backtest jobs and their detail.

        Returns
        -------
            pandas.DataFrame
                All factor backtest jobs.
            Columns
                - *jobid*
                - *jobname*
                - *jobstatus*
                - *starttime*
                - *endtime*
                - *universeid*
                - *universepath*
                - *factorbacktestid*
                - *avg_turnover*
                - *avg_ic*
                - *top_bottom_spread*
                - *frequency*
                - *bins*
                - *max_days*
                - *rank_method*
                - *description*
                - *period*

        Examples
        --------
        >>> ps.factor_backtest.list_job()
        jobid  jobstatus                   starttime                     endtime  ...  factorbacktestid  avg_turnover     avg_ic  top_bottom_spread  frequency  bins                   period
        0	   4  Completed  2022-06-29 17:48:41.023456  2022-06-29 17:52:03.637405  ...                 4      0.854072  -0.016881          -0.000389          Q    10  2000-01-01 ~ 2020-01-01
        1      3  Completed  2022-06-29 10:22:29.928233  2022-06-29 10:22:35.714741  ...                 3      0.388650  -0.009124          -0.000291          M     5  2015-01-01 ~ 2020-12-31
        2      2  Completed  2022-06-29 08:55:55.268231  2022-06-29 08:56:03.530062  ...                 2      0.380334  -0.022625          -0.000524          M     5  2015-01-01 ~ 2020-12-31
        3      1  Completed  2022-06-27 18:08:36.775176  2022-06-27 18:09:00.530742  ...                 1      0.879670  -0.074594          -0.000771          Q    10  2010-01-01 ~ 2011-01-01
        """
        return cls._list_job()


class strategy_backtest(PrismBacktestTaskComponent):
    @_validate_args
    def __init__(
        self,
        trade: abstract_prismcomponent._AbstractPrismComponent,
        universe: Union[int, str],
        market_impact: str,
        commission_fee: str,
        short_loan_fee: str,
        risk_free_rate: str,
        margin_rate: str,
        cash_interest_rate: str,
        initial_position_type: str,
        initial_position_value: int,
        benchmark: List[Union[int, str]],
        currency: _CurrencyTypeWithReportTrade,
        market_impact_value: float = None,
        commission_fee_value: float = None,
        short_loan_fee_value: float = None,
        risk_free_rate_value: float = None,
        margin_rate_value: float = None,
        cash_interest_rate_value: float = None,
        currency_hedge: bool = False,
        startdate: str = None,
        enddate: str = None,
        unpaid_dividend=None,
    ):
        assert initial_position_type in ["cash", "portfolio"], "Initial Position Type should be one of: cash, portfolio"
        if not isinstance(benchmark, list):
            benchmark = [benchmark]
        benchmark = parse_portfolios_to_portfolioids(benchmark)
        universeid, _ = parse_universe_to_universeid(universe)

        universe_info = get(f"{URL_UNIVERSES}/{universeid}/info")
        universe_startdate = universe_info["Start Date"].values[0]
        universe_enddate = universe_info["End Date"].values[0]

        universe_period_violated = are_periods_exclusive(universe_startdate, universe_enddate, startdate, enddate)

        if universe_period_violated:
            raise PrismValueError(
                f'Strategy Backtest period should overlap with universe period ({str(universe_startdate).split("T")[0]} ~ {str(universe_enddate).split("T")[0]})'
            )

        return super().__init__(
            trade_dataquery=trade._query,
            universeid=int(universeid),
            market_impact=market_impact,
            market_impact_value=market_impact_value,
            commission_fee=commission_fee,
            commission_fee_value=commission_fee_value,
            short_loan_fee=short_loan_fee,
            short_loan_fee_value=short_loan_fee_value,
            risk_free_rate=risk_free_rate,
            risk_free_rate_value=risk_free_rate_value,
            margin_rate=margin_rate,
            margin_rate_value=margin_rate_value,
            cash_interest_rate=cash_interest_rate,
            cash_interest_rate_value=cash_interest_rate_value,
            initial_position_type=initial_position_type,
            initial_position_value=initial_position_value,
            benchmark=benchmark,
            currency=currency,
            currency_hedge=currency_hedge,
            startdate=startdate,
            enddate=enddate,
            unpaid_dividend=unpaid_dividend,
        )


    @_validate_args
    def run(self, portfolioname: str, jobname: str = None, report: bool = True):
        should_overwrite, err_msg = should_overwrite_portfolio(portfolioname, "constructing")
        if not should_overwrite:
            logger.info(f"{err_msg}")
            return
        component_args = copy.deepcopy(self._query["component_args"])
        universeid = component_args.pop("universeid")
        benchmark = component_args.pop("benchmark")

        market_impact = {
            "model": component_args.pop("market_impact"),
            "model_value": component_args.pop("market_impact_value"),
        }
        commission_fee = {
            "model": component_args.pop("commission_fee"),
            "model_value": component_args.pop("commission_fee_value"),
        }
        short_loan_fee = {
            "model": component_args.pop("short_loan_fee"),
            "model_value": component_args.pop("short_loan_fee_value"),
        }
        risk_free_rate = {
            "model": component_args.pop("risk_free_rate"),
            "model_value": component_args.pop("risk_free_rate_value"),
        }
        margin_rate = {
            "model": component_args.pop("margin_rate"),
            "model_value": component_args.pop("margin_rate_value"),
        }
        cash_interest_rate = {
            "model": component_args.pop("cash_interest_rate"),
            "model_value": component_args.pop("cash_interest_rate_value"),
        }
        initial_position = {
            "position_type": component_args.pop("initial_position_type"),
            "position_value": component_args.pop("initial_position_value"),
        }

        task_params = {
            "portfoliopath": portfolioname + ".ppt",
            "universeid": universeid,
            "trade_value_type": "trade",
            "market_impact": market_impact,
            "commission_fee": commission_fee,
            "short_loan_fee": short_loan_fee,
            "risk_free_rate": risk_free_rate,
            "margin_rate": margin_rate,
            "cash_interest_rate": cash_interest_rate,
            "benchmark": benchmark,
            "initial_position": initial_position,
        }
        task_params.update(component_args)
        query = {
            "component_type": "taskcomponent",
            "componentid": self.componentid,
            "component_args": task_params,
        }

        rescontent = None
        with Loader("Strategy Backtest Running... ") as l:
            try:
                rescontent = post(
                    f"{URL_TASK}/{self.componentid}",
                    params={"jobname": jobname},
                    body=query,
                )
            except:
                l.stop()
                raise PrismTaskError("Strategy Backtest has failed.")
            if rescontent["status"] != "Pending":
                l.stop()
                raise PrismTaskError("Strategy Backtest has failed.")

        logger.info(
            f'{rescontent["message"]}: {rescontent["result"][0]["resulttype"]} is {rescontent["result"][0]["resultvalue"]}'
        )

    @classmethod
    @_validate_args
    def get_result(cls, sbid: Union[list, int], data=True, report=False):
        if isinstance(sbid, int):
            sbid = [sbid]
        return cls._get_task_result(cls.__class__.__name__, "Strategy Backtest", sbid, data, report)
