import numbers
import requests
import warnings
from abc import ABC
from functools import wraps
from typing import Union

from .._prismcomponent.abstract_prismcomponent import _AbstractPrismComponent
from .._common.config import URL_DATAQUERIES, URL_JOBS
from .._common import const
from .._core._req_builder import _taskquery
from .._utils import _validate_args, _authentication, get as _get
from .._utils.exceptions import PrismAuthError, PrismResponseError, PrismTypeError, PrismValueError


def binary_operation(func):
    @wraps(func)
    def wrapper(**kwargs):
        func(**kwargs)
        s_op = const.FunctionComponents[const.FunctionComponents["component_name_repr"]==func.__name__]["componentname"].values[0]
        obj = kwargs.get("self")
        other = kwargs.get("other")
        if other is None:
            raise PrismTypeError(f"{s_op} missing 1 required positional argument")

        if isinstance(other, numbers.Real) or isinstance(other, str):
            other = const.SPECIALVALUEMAP.get(other, other)
            other_node = _PrismValue(data=other)
        elif isinstance(other, _PrismComponent):
            other_node = other
        elif (obj._component_category_repr == "securitymaster") & isinstance(other, str):
            other = const.SPECIALVALUEMAP.get(other, other)
            other_node = _PrismValue(data=other)
        else:
            raise PrismTypeError(f"unsupported operand type(s) for {s_op}: {type(obj)}, {type(other)}")

        component_name = func.__name__
        component_args = {}
        ret = _functioncomponent_builder(component_name, component_args, obj, other_node)
        return ret
    return wrapper


def operation(func):
    @wraps(func)
    def wrapper(**kwargs):
        func(**kwargs)
        component_args = kwargs.copy()
        obj = component_args.pop("self")
        component_name = func.__name__
        ret = _functioncomponent_builder(component_name, component_args, obj)
        return ret
    return wrapper


def sample_operation(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        n = kwargs.get('n')
        if "shift" in func.__name__:
            if n < 1:
                raise PrismValueError("n must be a positive integer")
        return func(*args, **kwargs)
    return wrapper


def cross_sectional_operation(func):
    return operation(func)


def group_operation(func):
    @wraps(func)
    def wrapper(**kwargs):
        func(**kwargs)
        component_args = kwargs.copy()
        obj = component_args.pop("self")
        other = kwargs.get("group")
        if other is None:
            raise PrismTypeError("Operation needs two inputs.")
        ret = _functioncomponent_builder(func.__name__, component_args, obj, other)
        return ret
    return wrapper


def _functioncomponent_builder(component_name, component_args, *args):
    if len(args) < 1: raise PrismValueError("need children (can be empty)")
    query = {"component_args": component_args, "children": args}
    if const.FunctionComponents is None:
        raise PrismAuthError("Please Login First")
    class _PrismFunctionComponent(_PrismComponent):
        component_type = const.PrismComponentType.FUNCTION_COMPONENT
    _PrismFunctionComponent.__name__ = component_name
    return _PrismFunctionComponent(**query)


class _PrismComponent(_AbstractPrismComponent, ABC):
    # simple operations
    @_validate_args
    @binary_operation
    def __add__(self, other):
        ...

    @_validate_args
    @binary_operation
    def __radd__(self, other):
        ...

    @_validate_args
    @binary_operation
    def __sub__(self, other):
        ...

    @_validate_args
    @binary_operation
    def __rsub__(self, other):
        ...

    @_validate_args
    @binary_operation
    def __mul__(self, other):
        ...

    @_validate_args
    @binary_operation
    def __rmul__(self, other):
        ...

    @_validate_args
    @binary_operation
    def __truediv__(self, other):
        ...

    @_validate_args
    @binary_operation
    def __rtruediv__(self, other):
        ...

    @_validate_args
    @binary_operation
    def __mod__(self, other):
        ...

    @_validate_args
    @binary_operation
    def __rmod__(self, other):
        ...

    @_validate_args
    @binary_operation
    def __pow__(self, other):
        ...

    @_validate_args
    @binary_operation
    def __rpow__(self, other):
        ...

    # logical operations
    @_validate_args
    @binary_operation
    def __eq__(self, other):
        ...

    @_validate_args
    @binary_operation
    def __ne__(self, other):
        ...

    @_validate_args
    @binary_operation
    def __gt__(self, other):
        ...

    @_validate_args
    @binary_operation
    def __ge__(self, other):
        ...

    @_validate_args
    @binary_operation
    def __lt__(self, other):
        ...

    @_validate_args
    @binary_operation
    def __le__(self, other):
        ...

    @_validate_args
    @binary_operation
    def __and__(self, other):
        ...

    @_validate_args
    @binary_operation
    def __or__(self, other):
        ...

    @_validate_args
    @binary_operation
    def __xor__(self, other):
        ...

    # other operations
    @_validate_args
    @operation
    def __invert__(self): ...

    @_validate_args
    def __getitem__(self, obj):
        if not isinstance(obj, _PrismComponent):
            raise PrismTypeError("mask should be a PrismComponent")

        if const.FunctionComponents[const.FunctionComponents["componentid"]==obj.componentid]["categoryname"].values[0] != "Logical":
            raise PrismTypeError("mask should be a boolean components")

        if isinstance(obj, numbers.Real) or isinstance(obj, str):
            obj = const.SPECIALVALUEMAP.get(obj, obj)
            other_node = _PrismValue(data=obj)
        elif isinstance(obj, _PrismComponent):
            other_node = obj
        elif (self._component_name == "SecurityMaster") & isinstance(obj, str):
            obj = const.SPECIALVALUEMAP.get(obj, obj)
            other_node = _PrismValue(data=obj)
        else:
            raise PrismTypeError(f"unsupported operand type(s) for __getitem__: {type(self)}, {type(obj)}")

        return _functioncomponent_builder("__getitem__", {"obj": other_node}, self, other_node)

    @_validate_args
    @operation
    def resample(
        self,
        frequency: str,
        lookback: Union[int, str] = None,
        beyond: bool = True,
        drop_holiday: bool = False
    ):
        """
        Resample time-series data. Up-samples or down-samples the input PrismComponent to the desired frequency and using the specified frequency and lookback.

        Parameters
        ----------
        frequency : str
            | Desired sampling frequency to resample.
            | Frequency Format
            | Description: The 'frequency format' combines all the elements of the 'frequency' parameter, providing a comprehensive way to specify the resampling frequency.
            | Format: XBF-S
            |
            | Elements of the frequency Parameter
            | - X: Resampling Interval (Optional, If not given, it is defaults to be 1, meaning resampling occurs every data point)
            | Description: The 'X' element represents the number at which resampling should be operated. It determines how often data should be resampled.
            |
            | - B: Business Frequency (Optional, If not given, it is assumed to be a non-business frequency)
            | Description: The 'B' element indicates whether the resampling frequency should align with business days. If 'B' is included, it signifies a business frequency; otherwise, it's not considered.
            |
            | - F: Frequency Type
            | Description: The 'F' element specifies the frequency type, which defines the unit of time for resampling. It can take on one of the following values: [D, W, M, Q, SA, A].
            |
            | - S: Specific Part of Frequency (Optional)
            | Description: The 'S' element is an optional part of the 'frequency' parameter, and its presence depends on the chosen frequency type ('F'). It allows you to specify a particular aspect of the resampling frequency.
            |
            | Specific Part for Each Frequency Type
            - A (Annual) Frequency - MM/dd (Months and Day)
                Example: A-12/15 (Resample every year on December 15th)
            - M (Monthly), Q (Quarterly), SA (Semi-Annual) Frequencies - dd (Day of the Month)
                Example: 3M-25 (Resample every 3 months on the 25th day of the month)
            - W (Weekly) Frequency - Day of the Week (Case Insensitive)
                Example: 2W-Fri (Resample every 2 weeks on Fridays)
            - D (Daily) Frequency - N/A (If specific part is given it will raise an error)

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

        lookback : str
            Length of period to consider when resampling the data. This parameter defines how far back in time the resampling process should look to fill in the data for the desired frequency.

            .. admonition:: Note
                    :class: note

                    | When resampling from Quarterly data to Monthly data, it is recommended to set the lookback to at least  92 days ('92D' or '3M') or a larger value. This ensures that the resampling process considers a sufficient historical period to fill in missing values accurately.
                    | If set to only '1D', the lookback will consider data from just one day before each resampling point. This may result in missing values in the output time-series if sufficient historical data is not available.

        beyond : bool, default True
            Option to select whether to resample beyond the last data samples dates

        drop_holiday : bool, default False
            Option to select whether to drop holidays for each security during a resample

        Returns
        -------
            prismstudio._PrismComponent
                Resampled timeseries of the PrismComponent.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close_daily = close.resample('D')
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            >>> # upsampling
            >>> close_daily = close.resample('D')
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  value  Ticker
            0          2586086  2010-01-04  47.57     AFL
            1          2586086  2010-01-05  48.95     AFL
            2          2586086  2010-01-06  49.38     AFL
            3          2586086  2010-01-07  49.91     AFL
            4          2586086  2010-01-08  49.41     AFL
            ...            ...         ...    ...     ...
            1095431  344286611  2011-10-27  44.31     ITT
            1095432  344286611  2011-10-28  44.99     ITT
            1095433  344286611  2011-10-29  44.99     ITT
            1095434  344286611  2011-10-30  44.99     ITT
            1095435  344286611  2011-10-31  45.60     ITT

            >>> # downsampling to monthly frequency
            >>> close_monthly = close.resample('M')
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                listingid        date  value  Ticker
            0        2586086  2010-01-31  48.43     AFL
            1        2586086  2010-02-28  49.45     AFL
            2        2586086  2010-03-31  54.29     AFL
            3        2586086  2010-04-30  50.96     AFL
            4        2586086  2010-05-31  44.30     AFL
            ...          ...         ...    ...     ...
            36045  344286611  2011-06-30  58.93     ITT
            36046  344286611  2011-07-31  53.34     ITT
            36047  344286611  2011-08-31  47.34     ITT
            36048  344286611  2011-09-30  42.00     ITT
            36049  344286611  2011-10-31  45.60     ITT
        """

    @_validate_args
    @operation
    def round(self, decimals: int = 0):
        """
        Round each elements' value in a DataComponent to the given number of decimals.

        Parameters
        ----------
            decimals : int, default 0
                Number of decimal places to round to. If decimals is negative, it specifies the number of positions to the left of the decimal point.

        Returns
        -------
            prismstudio._PrismComponent
                Rounded values of the Datacomponent.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            >>> close_result = close.round() # 0 decimal point
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  value  Ticker
            0         2586086  2010-01-04   48.0     AFL
            1         2586086  2010-01-05   49.0     AFL
            2         2586086  2010-01-06   49.0     AFL
            3         2586086  2010-01-07   50.0     AFL
            4         2586086  2010-01-08   49.0     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25   44.0     ITT
            755972  344286611  2011-10-26   44.0     ITT
            755973  344286611  2011-10-27   44.0     ITT
            755974  344286611  2011-10-28   45.0     ITT
            755975  344286611  2011-10-31   46.0     ITT

            >>> close_result = close.round(1) # 1 decimal point
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  value  Ticker
            0         2586086  2010-01-04   47.6     AFL
            1         2586086  2010-01-05   49.0     AFL
            2         2586086  2010-01-06   49.4     AFL
            3         2586086  2010-01-07   49.9     AFL
            4         2586086  2010-01-08   49.4     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25   44.0     ITT
            755972  344286611  2011-10-26   43.5     ITT
            755973  344286611  2011-10-27   44.3     ITT
            755974  344286611  2011-10-28   45.0     ITT
            755975  344286611  2011-10-31   45.6     ITT
        """
        ...

    @_validate_args
    @operation
    def floor(self):
        """
        The floor value of each element. The floor of x i.e., the largest integer not greater than x.

        Returns
        -------
            prismstudio._PrismComponent
                The floor of each element, with ``float`` dtype. This is a scalar if element is a scalar.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            >>> close_result = close.floor()
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  value  Ticker
            0         2586086  2010-01-04   47.0     AFL
            1         2586086  2010-01-05   48.0     AFL
            2         2586086  2010-01-06   49.0     AFL
            3         2586086  2010-01-07   49.0     AFL
            4         2586086  2010-01-08   49.0     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25   44.0     ITT
            755972  344286611  2011-10-26   43.0     ITT
            755973  344286611  2011-10-27   44.0     ITT
            755974  344286611  2011-10-28   44.0     ITT
            755975  344286611  2011-10-31   45.0     ITT
        """
        ...

    @_validate_args
    @operation
    def ceil(self):
        """
        The ceiling value of each element. The ceiling of x i.e., the smallest integer greater than or equal to x.

        Returns
        -------
            prismstudio._PrismComponent
                The ceiling of each element, with ``float`` dtype. This is a scalar if element is a scalar.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            >>> close_result = close.ceil()
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  value  Ticker
            0         2586086  2010-01-04   48.0     AFL
            1         2586086  2010-01-05   49.0     AFL
            2         2586086  2010-01-06   50.0     AFL
            3         2586086  2010-01-07   50.0     AFL
            4         2586086  2010-01-08   50.0     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25   45.0     ITT
            755972  344286611  2011-10-26   44.0     ITT
            755973  344286611  2011-10-27   45.0     ITT
            755974  344286611  2011-10-28   45.0     ITT
            755975  344286611  2011-10-31   46.0     ITT

        """
        ...

    @_validate_args
    @operation
    def tanh(self):
        """
        Hyperbolic tangent value of each element.
        This function only applies to elements that are all numeric.

        Returns
        -------
            prismstudio._PrismComponent
                | The corresponding hyperbolic tangent values.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            >>> close_result = close.tanh()
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  value  Ticker
            0         2586086  2010-01-04    1.0     AFL
            1         2586086  2010-01-05    1.0     AFL
            2         2586086  2010-01-06    1.0     AFL
            3         2586086  2010-01-07    1.0     AFL
            4         2586086  2010-01-08    1.0     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25    1.0     ITT
            755972  344286611  2011-10-26    1.0     ITT
            755973  344286611  2011-10-27    1.0     ITT
            755974  344286611  2011-10-28    1.0     ITT
            755975  344286611  2011-10-31    1.0     ITT
        """
        ...

    @_validate_args
    @operation
    def cosh(self):
        """
        Hyperbolic cosine value of each element.
        This function only applies to elements that are all numeric.

        Returns
        -------
            prismstudio._PrismComponent
                | The corresponding hyperbolic cosine values.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            >>> close_result = close.cosh()
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date         value  Ticker
            0         2586086  2010-01-04  2.282225e+20     AFL
            1         2586086  2010-01-05  9.071621e+20     AFL
            2         2586086  2010-01-06  1.394542e+21     AFL
            3         2586086  2010-01-07  2.369232e+21     AFL
            4         2586086  2010-01-08  1.437012e+21     AFL
            ...           ...         ...           ...     ...
            755971  344286611  2011-10-25  6.555610e+18     ITT
            755972  344286611  2011-10-26  4.056502e+18     ITT
            755973  344286611  2011-10-27  8.761097e+18     ITT
            755974  344286611  2011-10-28  1.729333e+19     ITT
            755975  344286611  2011-10-31  3.182720e+19     ITT
        """
        ...

    @_validate_args
    @operation
    def sinh(self):
        """
        Hyperbolic sine value of each element.
        This function only applies to elements that are all numeric.

        Returns
        -------
            prismstudio._PrismComponent
                | The corresponding hyperbolic sine values.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            >>> close_result = close.sinh()
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date         value  Ticker
            0         2586086  2010-01-04  2.282225e+20     AFL
            1         2586086  2010-01-05  9.071621e+20     AFL
            2         2586086  2010-01-06  1.394542e+21     AFL
            3         2586086  2010-01-07  2.369232e+21     AFL
            4         2586086  2010-01-08  1.437012e+21     AFL
            ...           ...         ...           ...     ...
            755971  344286611  2011-10-25  6.555610e+18     ITT
            755972  344286611  2011-10-26  4.056502e+18     ITT
            755973  344286611  2011-10-27  8.761097e+18     ITT
            755974  344286611  2011-10-28  1.729333e+19     ITT
            755975  344286611  2011-10-31  3.182720e+19     ITT
        """
        ...

    @_validate_args
    @operation
    def arcsinh(self):
        r"""
        Hyperbolic inverse sine value of each element.
        This function only applies to elements that are all numeric.

        Returns
        -------
            prismstudio._PrismComponent
                | The hyperbolic inverse sine of each element in :math:`x`, in radians and in the closed interval \([-pi/2, pi/2])\. This is a scalar if :math:`x` is a scalar.
        """
        ...

    @_validate_args
    @operation
    def arccosh(self):
        r"""
        Return a DataComponet with hyperbolic inverse cosine value of each element.
        This function only applies to elements that are all numeric.

        Returns
        -------
            prismstudio._PrismComponent
                The hyperbolic inverse cosine of each element in PrismComponent, in radians and in the closed interval :math:`[-\pi/2, \pi/2]`.

        """
        ...

    @_validate_args
    @operation
    def arctanh(self):
        r"""
        Hyperbolic inverse tangent value of each element.
        This function only applies to elements that are all numeric.

        Returns
        -------
            prismstudio._PrismComponent
                The hyperbolic inverse tangent of each element in PrismComponent, in radians and in the closed interval :math:`[-\pi/2, \pi/2]`.
        """
        ...

    @_validate_args
    @operation
    def arctan(self):
        r"""
        Inverse tangent value of each element.
        This function only applies to elements that are all numeric.

        Returns
        -------
            prismstudio._PrismComponent
                The inverse tangent of each element in :math:`x`, in radians and in the closed interval :math:`[-\pi/2, \pi/2]`.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid       date  Close Ticker
            0         2586086 2010-01-04  47.57    AFL
            1         2586086 2010-01-05  48.95    AFL
            2         2586086 2010-01-06  49.38    AFL
            3         2586086 2010-01-07  49.91    AFL
            4         2586086 2010-01-08  49.41    AFL
            ...           ...        ...    ...    ...
            755971  344286611 2011-10-25  44.02    ITT
            755972  344286611 2011-10-26  43.54    ITT
            755973  344286611 2011-10-27  44.31    ITT
            755974  344286611 2011-10-28  44.99    ITT
            755975  344286611 2011-10-31  45.60    ITT

            >>> close_result = close.arctan()
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date     value   Ticker
            0         2586086  2010-01-04  1.549778     AFL
            1         2586086  2010-01-05  1.550370     AFL
            2         2586086  2010-01-06  1.550548     AFL
            3         2586086  2010-01-07  1.550763     AFL
            4         2586086  2010-01-08  1.550560     AFL
            ...           ...         ...       ...     ...
            755975  344286611  2011-10-25  1.548083  ITT.WI
            755976  344286611  2011-10-26  1.547833  ITT.WI
            755977  344286611  2011-10-27  1.548232  ITT.WI
            755978  344286611  2011-10-28  1.548573  ITT.WI
            755979  344286611  2011-10-31  1.548870  ITT.WI
        """
        ...

    @_validate_args
    @operation
    def arccos(self):
        r"""
        Return a DataComponet with inverse cosine value of each element.
        This function only applies to elements that are all numeric.

        Returns
        -------
            prismstudio._PrismComponent
                The inverse cosine of each element in PrismComponent, in radians and in the closed interval :math:`[-\pi/2, \pi/2]`.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            >>> close_result = close.arccos() # Input to arccos should be between 1 and 1. Values outside such range will yield NaNs
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  value  Ticker
            0         2586086  2010-01-04    NaN     AFL
            1         2586086  2010-01-05    NaN     AFL
            2         2586086  2010-01-06    NaN     AFL
            3         2586086  2010-01-07    NaN     AFL
            4         2586086  2010-01-08    NaN     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25    NaN     ITT
            755972  344286611  2011-10-26    NaN     ITT
            755973  344286611  2011-10-27    NaN     ITT
            755974  344286611  2011-10-28    NaN     ITT
            755975  344286611  2011-10-31    NaN     ITT

            >>> close_result = close.cross_sectional_percentile().arccos() # cross_sectional_percentile will yield values between 0 and 1, which makes suitable inputs to arccos
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date     value  Ticker
            0         2586086  2010-01-04  0.817564     AFL
            1         2586086  2010-01-05  0.778454     AFL
            2         2586086  2010-01-06  0.786962     AFL
            3         2586086  2010-01-07  0.778454     AFL
            4         2586086  2010-01-08  0.803766     AFL
            ...           ...         ...       ...     ...
            755971  344286611  2011-10-25  0.954521     ITT
            755972  344286611  2011-10-26  0.971575     ITT
            755973  344286611  2011-10-27  0.986035     ITT
            755974  344286611  2011-10-28  0.978823     ITT
            755975  344286611  2011-10-31  0.949610     ITT
        """
        ...

    @_validate_args
    @operation
    def arcsin(self):
        r"""
        Inverse sine value of each element.
        This function only applies to elements that are all numeric.

        Returns
        -------
            prismstudio._PrismComponent
                | The inverse sine of each element in :math:`x`, in radians and in the closed interval :math:`[-\pi/2,\pi/2]`. This is a scalar if :math:`x` is a scalar.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid       date  Close Ticker
            0         2586086 2010-01-04  47.57    AFL
            1         2586086 2010-01-05  48.95    AFL
            2         2586086 2010-01-06  49.38    AFL
            3         2586086 2010-01-07  49.91    AFL
            4         2586086 2010-01-08  49.41    AFL
            ...           ...        ...    ...    ...
            755971  344286611 2011-10-25  44.02    ITT
            755972  344286611 2011-10-26  43.54    ITT
            755973  344286611 2011-10-27  44.31    ITT
            755974  344286611 2011-10-28  44.99    ITT
            755975  344286611 2011-10-31  45.60    ITT

            >>> close_result = close.arcsin() # Input to arcsin should be between 1 and 1. Values outside such range will yield NaNs.
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid       date  value Ticker
            0         2586086 2010-01-04    NaN    AFL
            1         2586086 2010-01-05    NaN    AFL
            2         2586086 2010-01-06    NaN    AFL
            3         2586086 2010-01-07    NaN    AFL
            4         2586086 2010-01-08    NaN    AFL
            ...           ...        ...    ...    ...
            755971  344286611 2011-10-25    NaN    ITT
            755972  344286611 2011-10-26    NaN    ITT
            755973  344286611 2011-10-27    NaN    ITT
            755974  344286611 2011-10-28    NaN    ITT
            755975  344286611 2011-10-31    NaN    ITT

            >>> close_result = close.cross_sectional_percentile().arcsin() # cross_sectional_percentile will yield values between 0 and 1, which makes suitable inputs to arcsin.
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date     value  Ticker
            0         2586086  2010-01-04  0.753232     AFL
            1         2586086  2010-01-05  0.792342     AFL
            2         2586086  2010-01-06  0.783834     AFL
            3         2586086  2010-01-07  0.792342     AFL
            4         2586086  2010-01-08  0.767030     AFL
            ...           ...         ...       ...     ...
            755971  344286611  2011-10-25  0.616276     ITT
            755972  344286611  2011-10-26  0.599222     ITT
            755973  344286611  2011-10-27  0.584761     ITT
            755974  344286611  2011-10-28  0.591974     ITT
            755975  344286611  2011-10-31  0.621186     ITT
        """
        ...

    @_validate_args
    @operation
    def tan(self):
        """
        Tangent value of each element.
        This function only applies to elements that are all numeric.

        Returns
        -------
            prismstudio._PrismComponent
                | The corresponding tangent values.


        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            >>> close_result = close.tan()
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date       value  Ticker
            0         2586086  2010-01-04    0.478267     AFL
            1         2586086  2010-01-05   -3.831271     AFL
            2         2586086  2010-01-06   -1.223259     AFL
            3         2586086  2010-01-07   -0.371254     AFL
            4         2586086  2010-01-08   -1.150999     AFL
            ...           ...         ...         ...     ...
            755971  344286611  2011-10-25    0.037721     ITT
            755972  344286611  2011-10-26   -0.473590     ITT
            755973  344286611  2011-10-27    0.339960     ITT
            755974  344286611  2011-10-28    1.584115     ITT
            755975  344286611  2011-10-31  -21.303359     ITT
        """
        ...

    @_validate_args
    @operation
    def cos(self):
        """
        Cosine value of each element.
        This function only applies to elements that are all numeric.

        Returns
        -------
            prismstudio._PrismComponent
                | The corresponding cosine values.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            >>> close_result = close.cos()
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date      value  Ticker
            0         2586086  2010-01-04  -0.902132     AFL
            1         2586086  2010-01-05   0.252549     AFL
            2         2586086  2010-01-06   0.632916     AFL
            3         2586086  2010-01-07   0.937479     AFL
            4         2586086  2010-01-08   0.655854     AFL
            ...           ...         ...        ...     ...
            755971  344286611  2011-10-25   0.999289     ITT
            755972  344286611  2011-10-26   0.903771     ITT
            755973  344286611  2011-10-27   0.946784     ITT
            755974  344286611  2011-10-28   0.533805     ITT
            755975  344286611  2011-10-31  -0.046889     ITT
        """
        ...

    @_validate_args
    @operation
    def sin(self):
        """
        Sine value of each element.
        This function only applies to elements that are all numeric.

        Returns
        -------
            prismstudio._PrismComponent
                | The corresponding sine values.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            >>> close_result = close.sin()
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date      value  Ticker
            0         2586086  2010-01-04  -0.431460     AFL
            1         2586086  2010-01-05  -0.967584     AFL
            2         2586086  2010-01-06  -0.774220     AFL
            3         2586086  2010-01-07  -0.348043     AFL
            4         2586086  2010-01-08  -0.754887     AFL
            ...           ...         ...        ...     ...
            755971  344286611  2011-10-25   0.037694     ITT
            755972  344286611  2011-10-26  -0.428017     ITT
            755973  344286611  2011-10-27   0.321869     ITT
            755974  344286611  2011-10-28   0.845608     ITT
            755975  344286611  2011-10-31   0.998900     ITT
        """
        ...

    @_validate_args
    @operation
    def sqrt(self):
        """
        Square root value of each element.
        This function only applies to elements that are all numeric.

        Returns
        -------
            prismstudio._PrismComponent
                | If any element in is complex, a complex array is returned (and the square-roots of negative reals are calculated).
                | If all of the elements are real, negative elements returning ``nan``.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            >>> close_result = close.sqrt()
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date     value  Ticker
            0         2586086  2010-01-04  6.897101     AFL
            1         2586086  2010-01-05  6.996428     AFL
            2         2586086  2010-01-06  7.027090     AFL
            3         2586086  2010-01-07  7.064701     AFL
            4         2586086  2010-01-08  7.029225     AFL
            ...           ...         ...       ...     ...
            755971  344286611  2011-10-25  6.634757     ITT
            755972  344286611  2011-10-26  6.598485     ITT
            755973  344286611  2011-10-27  6.656576     ITT
            755974  344286611  2011-10-28  6.707459     ITT
            755975  344286611  2011-10-31  6.752777     ITT
        """
        ...

    @_validate_args
    @operation
    def log_n(self, n: numbers.Real = 10):
        """
        Logarithm base n value of each element.

        Parameters
        ----------
            n : int, default 10
                Base of the logarithm

        Returns
        -------
            prismstudio._PrismComponent
                The base-n logarithm of PrismComponent, element-wise.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            >>> log_close = close.log_n()
            >>> log_close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date     value  Ticker
            0         2586086  2010-01-04  1.677333     AFL
            1         2586086  2010-01-05  1.689753     AFL
            2         2586086  2010-01-06  1.693551     AFL
            3         2586086  2010-01-07  1.698188     AFL
            4         2586086  2010-01-08  1.693815     AFL
            ...           ...         ...        ...     ...
            755971  344286611  2011-10-25  1.643650     ITT
            755972  344286611  2011-10-26  1.638888     ITT
            755973  344286611  2011-10-27  1.646502     ITT
            755974  344286611  2011-10-28  1.653116     ITT
            755975  344286611  2011-10-31  1.658965     ITT

        """
        ...

    @_validate_args
    @operation
    def ln(self):
        """
        The natural logarithm value of each element. The natural logarithm is logarithm in base :math:`e`.

        Returns
        -------
            prismstudio._PrismComponent
                | The natural logarithm of PrismComponent, element-wise.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            >>> close_result = close.ln()
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date     value  Ticker
            0         2586086  2010-01-04  3.862202     AFL
            1         2586086  2010-01-05  3.890799     AFL
            2         2586086  2010-01-06  3.899545     AFL
            3         2586086  2010-01-07  3.910221     AFL
            4         2586086  2010-01-08  3.900153     AFL
            ...           ...         ...       ...     ...
            755971  344286611  2011-10-25  3.784644     ITT
            755972  344286611  2011-10-26  3.773680     ITT
            755973  344286611  2011-10-27  3.791210     ITT
            755974  344286611  2011-10-28  3.806440     ITT
            755975  344286611  2011-10-31  3.819908     ITT
        """
        ...

    @_validate_args
    @operation
    def exp(self):
        """
        Exponential value of each element.

        Returns
        -------
            prismstudio._PrismComponent
                | Element-wise exponential of datacomponent.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            >>> close_result = close.exp()
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date         value  Ticker
            0         2586086  2010-01-04  4.564451e+20     AFL
            1         2586086  2010-01-05  1.814324e+21     AFL
            2         2586086  2010-01-06  2.789083e+21     AFL
            3         2586086  2010-01-07  4.738464e+21     AFL
            4         2586086  2010-01-08  2.874024e+21     AFL
            ...           ...         ...           ...     ...
            755971  344286611  2011-10-25  1.311122e+19     ITT
            755972  344286611  2011-10-26  8.113005e+18     ITT
            755973  344286611  2011-10-27  1.752219e+19     ITT
            755974  344286611  2011-10-28  3.458667e+19     ITT
            755975  344286611  2011-10-31  6.365439e+19     ITT
        """
        ...

    @_validate_args
    @operation
    def __abs__(self):
        """
        Absolute value of each element.
        This function only applies to elements that are all numeric.

        Returns
        -------
            prismstudio._PrismComponent
                | Absolute values of the Datacomponent.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close_result = close.sin()
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date      value  Ticker
            0         2586086  2010-01-04  -0.431460     AFL
            1         2586086  2010-01-05  -0.967584     AFL
            2         2586086  2010-01-06  -0.774220     AFL
            3         2586086  2010-01-07  -0.348043     AFL
            4         2586086  2010-01-08  -0.754887     AFL
            ...           ...         ...        ...     ...
            755971  344286611  2011-10-25   0.037694     ITT
            755972  344286611  2011-10-26  -0.428017     ITT
            755973  344286611  2011-10-27   0.321869     ITT
            755974  344286611  2011-10-28   0.845608     ITT
            755975  344286611  2011-10-31   0.998900     ITT

            >>> abs_result = abs(close_result)
            >>> abs_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date     value  Ticker
            0         2586086  2010-01-04  0.431460     AFL
            1         2586086  2010-01-05  0.967584     AFL
            2         2586086  2010-01-06  0.774220     AFL
            3         2586086  2010-01-07  0.348043     AFL
            4         2586086  2010-01-08  0.754887     AFL
            ...           ...         ...       ...     ...
            755971  344286611  2011-10-25  0.037694     ITT
            755972  344286611  2011-10-26  0.428017     ITT
            755973  344286611  2011-10-27  0.321869     ITT
            755974  344286611  2011-10-28  0.845608     ITT
            755975  344286611  2011-10-31  0.998900     ITT
        """
        ...

    @_validate_args
    @operation
    def abs(self):
        """
        Absolute value of each element.
        This function only applies to elements that are all numeric.

        Returns
        -------
            prismstudio._PrismComponent
                | Absolute values of the Datacomponent.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close_result = close.sin()
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date      value  Ticker
            0         2586086  2010-01-04  -0.431460     AFL
            1         2586086  2010-01-05  -0.967584     AFL
            2         2586086  2010-01-06  -0.774220     AFL
            3         2586086  2010-01-07  -0.348043     AFL
            4         2586086  2010-01-08  -0.754887     AFL
            ...           ...         ...        ...     ...
            755971  344286611  2011-10-25   0.037694     ITT
            755972  344286611  2011-10-26  -0.428017     ITT
            755973  344286611  2011-10-27   0.321869     ITT
            755974  344286611  2011-10-28   0.845608     ITT
            755975  344286611  2011-10-31   0.998900     ITT

            >>> abs_result = close_result.abs()
            >>> abs_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date     value  Ticker
            0         2586086  2010-01-04  0.431460     AFL
            1         2586086  2010-01-05  0.967584     AFL
            2         2586086  2010-01-06  0.774220     AFL
            3         2586086  2010-01-07  0.348043     AFL
            4         2586086  2010-01-08  0.754887     AFL
            ...           ...         ...       ...     ...
            755971  344286611  2011-10-25  0.037694     ITT
            755972  344286611  2011-10-26  0.428017     ITT
            755973  344286611  2011-10-27  0.321869     ITT
            755974  344286611  2011-10-28  0.845608     ITT
            755975  344286611  2011-10-31  0.998900     ITT
        """
        ...

    @_validate_args
    @operation
    def sign(self):
        """
        Returns an element-wise indication of the sign of a number.
        The sign function returns -1 if x < 0, 0 if x==0, 1 if x > 0

        Returns
        -------
            prismstudio._PrismComponent
                | The sign of PrismComponent, element-wise.

        Examples
        --------
            >>> close = ps.market.close()
            >>> ret = close.samples_pct_change(n=1)
            >>> ret .get_data("KR_primary", "2023-01-01")
                     listingid        date      value
            0         20108704  2023-01-03  -0.032172
            1         20108704  2023-01-04   0.000000
            2         20108704  2023-01-05   0.008310
            3         20108704  2023-01-06   0.002747
            ...            ...         ...        ...
            371020  1842980933  2023-09-26  -0.009569
            371021  1842980933  2023-09-27   0.000000
            371022  1842980933  2023-10-04   0.000000
            371023  1842980933  2023-10-05   0.002415
            371024  1842980933  2023-10-06   0.002410

            >>> ret_sign = ret .sign()
            >>> ret_sign .get_data("KR_primary", "2023-01-01")
                     listingid        date  value
            0         20108704  2023-01-03   -1.0
            1         20108704  2023-01-04    0.0
            2         20108704  2023-01-05    1.0
            3         20108704  2023-01-06    1.0
            ...            ...         ...    ...
            371020  1842980933  2023-09-26   -1.0
            371021  1842980933  2023-09-27    0.0
            371022  1842980933  2023-10-04    0.0
            371023  1842980933  2023-10-05    1.0
            371024  1842980933  2023-10-06    1.0
        """
        ...

    @_validate_args
    @operation
    def radians(self):
        """
        Convert from degrees to radians.

        Returns
        -------
            prismstudio._PrismComponent
                | The radian of PrismComponent, element-wise.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data("KR_primary", "2023-01-01")
                      listingid         date    Close
            0          20108704   2023-01-02  18650.0
            1          20108704   2023-01-03  18050.0
            2          20108704   2023-01-04  18050.0
            3          20108704   2023-01-05  18200.0
            4          20108704   2023-01-06  18250.0
            ...             ...          ...      ...
            369058   1842980933   2023-09-25   2090.0
            369059   1842980933   2023-09-26   2070.0
            369060   1842980933   2023-09-27   2070.0
            369061   1842980933   2023-10-04   2070.0
            369062   1842980933   2023-10-05   2075.0

            >>> close_radians = close.radians()
            >>> close_radians.get_data("KR_primary", "2023-01-01")
                     listingid        date       value
            0         20108704  2023-01-02  325.503905
            1         20108704  2023-01-03  315.031930
            2         20108704  2023-01-04  315.031930
            3         20108704  2023-01-05  317.649924
            4         20108704  2023-01-06  318.522588
            ...            ...         ...         ...
            371020  1842980933  2023-09-26   36.128316
            371021  1842980933  2023-09-27   36.128316
            371022  1842980933  2023-10-04   36.128316
            371023  1842980933  2023-10-05   36.215582
            371024  1842980933  2023-10-06   36.302848
        """
        ...

    @_validate_args
    @operation
    def degrees(self):
        """
        Convert from radians to degrees.

        Returns
        -------
            prismstudio._PrismComponent
                | The natural logarithm of PrismComponent, element-wise.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data("KR_primary", "2023-01-01")
                      listingid         date     Close
            0          20108704   2023-01-02   18650.0
            1          20108704   2023-01-03   18050.0
            2          20108704   2023-01-04   18050.0
            3          20108704   2023-01-05   18200.0
            4          20108704   2023-01-06   18250.0
            ...             ...          ...       ...
            369058   1842980933   2023-09-25    2090.0
            369059   1842980933   2023-09-26    2070.0
            369060   1842980933   2023-09-27    2070.0
            369061   1842980933   2023-10-04    2070.0
            369062   1842980933   2023-10-05    2075.0

            >>> close_degree = close.degrees()
            >>> close_degree.get_data("KR_primary", "2023-01-01")
                     listingid        date         value
            0         20108704  2023-01-02  1.068566e+06
            1         20108704  2023-01-03  1.034189e+06
            2         20108704  2023-01-04  1.034189e+06
            3         20108704  2023-01-05  1.042783e+06
            4         20108704  2023-01-06  1.045648e+06
            ...            ...         ...           ...
            371020  1842980933  2023-09-26  1.186023e+05
            371021  1842980933  2023-09-27  1.186023e+05
            371022  1842980933  2023-10-04  1.186023e+05
            371023  1842980933  2023-10-05  1.188887e+05
            371024  1842980933  2023-10-06  1.191752e+05
        """
        ...

    @_validate_args
    @operation
    def clip(self, lowerbound: numbers.Real = None, upperbound: numbers.Real = None):
        """
        Clip (limit) the values in an array.
        Given an interval, values outside the interval are clipped to the interval edges.
        For example, if an interval of [0, 1] is specified, values smaller than 0 become 0, and values larger than 1 become 1.

        Parameters
        ----------
            lower_bound : number.Real, default None
                Any values below this threshold will be adjusted to this minimum value. If the threshold is not provided (e.g., None), no clipping will be applied.

            upper_bound : number.Real, default None
                Any values exceeding this threshold will be adjusted to this maximum value. If the threshold is not specified (e.g., None), no clipping will be performed.

        Returns
        -------
            prismstudio._PrismComponent
            | The clipped value of PrismComponent, element-wise.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data("KR_primary", "2023-01-01")

                      listingid        date      Close
                 0     20108704   2023-01-02   18650.0
                 1     20108704   2023-01-03   18050.0
                 2     20108704   2023-01-04   18050.0
                 3     20108704   2023-01-05   18200.0
                 4     20108704   2023-01-06   18250.0
               ...          ...          ...       ...
            369058   1842980933   2023-09-25    2090.0
            369059   1842980933   2023-09-26    2070.0
            369060   1842980933   2023-09-27    2070.0
            369061   1842980933   2023-10-04    2070.0
            369062   1842980933   2023-10-05    2075.0



            >>> clipped = close.clip(1, 18000)
            >>> clipped.get_data("KR_primary", "2023-01-01")

                     listingid        date    value
                 0    20108704  2023-01-02  18000.0
                 1    20108704  2023-01-03  18000.0
                 2    20108704  2023-01-04  18000.0
                 3    20108704  2023-01-05  18000.0
                 4    20108704  2023-01-06  18000.0
               ...         ...         ...      ...
            369058  1842980933  2023-09-25   2090.0
            369059  1842980933  2023-09-26   2070.0
            369060  1842980933  2023-09-27   2070.0
            369061  1842980933  2023-10-04   2070.0
            369062  1842980933  2023-10-05   2075.0
        """
        ...

    @_validate_args
    @operation
    def isin(self, values: list):
        """
        Whether each element in the Data Component is contained in values.

        Parameters
        ----------
            values : list

        Returns
        -------
            prismstudio._PrismComponent
                DataComponent of booleans showing whether each element is contained in values.
        """
        ...

    @_validate_args
    def fillna(self, value: Union[str, float, int, _AbstractPrismComponent] = None, method: const.FillnaMethodType = None, n: int = None):
        """
        Fill NA/NaN values using the specified method.

        Parameters
        ----------
            value : PrismComponent, str, int, float, default None
                Value to use to fill NaN values (e.g. 0), alternately for a PrismComponent input, it will fill values based on matching columns (i.e id, date etc)

            method : str {'backfill', 'bfill', 'pad', 'ffill', None}, default None
                | Method to use for filling NaN in

                - pad / ffill: Propagate last valid observation forward to next valid
                - backfilfillnal / bfill: Use next valid observation to fill gap

            n : int, default None
                | If method is specified, this is the maximum number of consecutive NaN values to forward/backward fill.
                | If method is not specified, this is the maximum number of entries along the entire axis where NaNs will be filled.
                | Must be greater than 0 if not None.

                .. admonition:: Warning
                    :class: warning

                    If the number of consecutive NaNs are greater than n , it will only be partially filled.

        Returns
        -------
            prismstudio._PrismComponent

        Examples
        --------
            >>> rd = ps.financial.income_statement(dataitemid=100602, periodtype='Q')
            >>> rd_df = rd.get_data(universe=1, startdate='2019-01-31', enddate='2022-08-31')
            >>> rd_df
                    listingid        date  currency      period  R&D Expense
            0         20106319  2019-02-20       THB  2018-12-31          NaN
            1         20106319  2019-04-24       THB  2019-03-31          NaN
            2         20106319  2019-08-08       THB  2019-06-30          NaN
            3         20106319  2019-11-06       THB  2019-09-30          NaN
            4         20106319  2020-02-26       THB  2019-12-31          NaN
            ...            ...         ...       ...         ...          ...
            103101  1780525435  2022-08-12       INR  2022-06-30          NaN
            103103  1780926579  2022-08-23       AUD  2022-06-30          NaN
            103106  1781170875  2022-08-12       INR  2022-06-30          NaN
            103111  1781747464  2022-08-08       INR  2022-06-30          NaN
            103120  1784786390  2022-08-19       MYR  2022-06-30          NaN

            >>> rd_no_na = rd.fillna(0)
            >>> rd_no_na_df = rd_no_na .get_data(universe=1, startdate='2019-01-31', enddate='2022-08-31')
            >>> rd_no_na_df
                    listingid        date  currency      period  R&D Expense
            0         20106319  2019-02-20       THB  2018-12-31          0.0
            1         20106319  2019-04-24       THB  2019-03-31          0.0
            2         20106319  2019-08-08       THB  2019-06-30          0.0
            3         20106319  2019-11-06       THB  2019-09-30          0.0
            4         20106319  2020-02-26       THB  2019-12-31          0.0
            ...            ...         ...       ...         ...          ...
            103101  1780525435  2022-08-12       INR  2022-06-30          0.0
            103103  1780926579  2022-08-23       AUD  2022-06-30          0.0
            103106  1781170875  2022-08-12       INR  2022-06-30          0.0
            103111  1781747464  2022-08-08       INR  2022-06-30          0.0
            103120  1784786390  2022-08-19       MYR  2022-06-30          0.0
        """
        other_node = None
        if value is not None:
            if isinstance(value, numbers.Real) or isinstance(value, str):
                value = const.SPECIALVALUEMAP.get(value, value)
                other_node = _PrismValue(data=value)
            elif isinstance(value, _PrismComponent):
                other_node = value
            else:
                raise PrismTypeError(f"unsupported operand type(s) for fillna: {type(self)}, {type(value)}")
        component_args = {'method': method, 'n': n}
        args = [self]
        if other_node:
            args.append(other_node)
        return _functioncomponent_builder('fillna', component_args, *args)

    # n-period operations
    @_validate_args
    @sample_operation
    @operation
    def sample_pct_change(self, n: int, positive_denominator: bool = False):
        """
        Percentage change between the current and a prior ``n``th element. Computes the percentage change from the immediately previous row by default if no ``n`` is given. This is useful in comparing the percentage of change in a time series of elements.

        Parameters
        ----------
            n : int
                Number of samples to shift for calculating percent change, accepts negative values.

            positive_denominator : bool, default False
                Whether to only include result of positive denominator. The result from negative or zero denominator will be assigned ``np.nan`` .

        Returns
        -------
            prismstudio._PrismComponent
                Percent change of the PrismComponent.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            >>> close_result = close.sample_pct_change(n=1)
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date     value  Ticker
            0         2586086  2010-01-04  0.028541     AFL
            1         2586086  2010-01-05  0.029010     AFL
            2         2586086  2010-01-06  0.008784     AFL
            3         2586086  2010-01-07  0.010733     AFL
            4         2586086  2010-01-08 -0.010018     AFL
            ...           ...         ...       ...     ...
            755903  344286611  2011-10-25 -0.013226     ITT
            755904  344286611  2011-10-26 -0.010904     ITT
            755905  344286611  2011-10-27  0.017685     ITT
            755906  344286611  2011-10-28  0.015346     ITT
            755907  344286611  2011-10-31  0.013559     ITT
        """
        ...

    @_validate_args
    @sample_operation
    @operation
    def sample_shift(self, n: int):
        """
        Shift all PrismComponent element by n periods.

        Parameters
        ----------
            n : int
                Number of samples to shift. Can be positive or negative.

        Returns
        -------
            prismstudio._PrismComponent
                Shifted values of the PrismComponent.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            >>> close_result = close.sample_shift(n=2)
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  value  Ticker
            0         2586086  2010-01-04  46.88     AFL
            1         2586086  2010-01-05  46.25     AFL
            2         2586086  2010-01-06  47.57     AFL
            3         2586086  2010-01-07  48.95     AFL
            4         2586086  2010-01-08  49.38     AFL
            ...           ...         ...    ...     ...
            755859  344286611  2011-10-25  44.25     ITT
            755860  344286611  2011-10-26  44.61     ITT
            755861  344286611  2011-10-27  44.02     ITT
            755862  344286611  2011-10-28  43.54     ITT
            755863  344286611  2011-10-31  44.31     ITT
        """
        ...

    @_validate_args
    @sample_operation
    @operation
    def sample_diff(self, n: int):
        """
        Difference between the current and a prior ``n``th element. Computes the difference from the immediately previous row by default if no ``n`` is given.


        Parameters
        ----------
            n : int
                Number of samples to shift for calculating difference, accepts negative values.

        Returns
        -------
            prismstudio._PrismComponent
                First differences of the PrismComponent.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            >>> log_close = close.sample_diff(5)
            >>> log_close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date   value  Ticker
            0         2586086  2010-01-04   0.78      AFL
            1         2586086  2010-01-05   2.15      AFL
            2         2586086  2010-01-06   2.43      AFL
            3         2586086  2010-01-07   3.03      AFL
            4         2586086  2010-01-08   3.16      AFL
            ...           ...         ...    ...      ...
            755971  344286611  2011-10-25  -0.94      ITT
            755972  344286611  2011-10-26  -0.61      ITT
            755973  344286611  2011-10-27   0.61      ITT
            755974  344286611  2011-10-28   0.74      ITT
            755975  344286611  2011-10-31   0.99      ITT
        """
        ...

    @_validate_args
    @sample_operation
    @operation
    def sample_max(self, n: int, min_sample: int = 1, weights: list = None):
        """
        Maximum of the values over given samples n.

        Parameters
        ----------
            n : int
                | Number of time samples for calculating maximum values, accepts negative values.

            min_sample : int, default 1
                Minimum number of observations in window required to have a value; otherwise, result is ``np.nan`` .

            weights : list, default None
                An optional slice with the same length as the window that will be multiplied element-wise with the values in the window.

        Returns
        -------
            prismstudio._PrismComponent
                n period maximum timeseries of the PrismComponent.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            >>> n_max= close.sample_max(n=2)
            >>> n_max.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  value  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.91     AFL
            ...           ...         ...    ...     ...
            755947  344286611  2011-10-25  44.61     ITT
            755948  344286611  2011-10-26  44.02     ITT
            755949  344286611  2011-10-27  44.31     ITT
            755950  344286611  2011-10-28  44.99     ITT
            755951  344286611  2011-10-31  45.60     ITT
        """
        if (weights is not None) and (len(weights) != n):
            raise PrismValueError("Number of weights should equal to n")

    @_validate_args
    @sample_operation
    @operation
    def sample_min(self, n: int, min_sample: int = 1, weights: list = None):
        """
        Minimum of the values over given samples n.

        Parameters
        ----------
            n : int
                | Number of time samples for calculating minimum values, accepts negative values.

            min_sample : int, default 1
                Minimum number of observations in window required to have a value; otherwise, result is ``np.nan`` .

            weights : list, default None
                An optional slice with the same length as the window that will be multiplied element-wise with the values in the window.

        Returns
        -------
            prismstudio._PrismComponent
                n samples minimum timeseries of the PrismComponent.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            >>> close_result = close.sample_min(n=2)
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  value  Ticker
            0         2586086  2010-01-04  46.25     AFL
            1         2586086  2010-01-05  47.57     AFL
            2         2586086  2010-01-06  48.95     AFL
            3         2586086  2010-01-07  49.38     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755947  344286611  2011-10-25  44.02     ITT
            755948  344286611  2011-10-26  43.54     ITT
            755949  344286611  2011-10-27  43.54     ITT
            755950  344286611  2011-10-28  44.31     ITT
            755951  344286611  2011-10-31  44.99     ITT
        """
        if (weights is not None) and (len(weights) != n):
            raise PrismValueError("Number of weights should equal to n")

    @_validate_args
    @sample_operation
    @operation
    def sample_mean(self, n: int, min_sample: int = 1, weights: list = None):
        r"""
        Mean of the values over given samples n.

        Parameters
        ----------
            n : int
                | Number of time samples for calculating mean values, accepts negative values.

            min_sample : int, default 1
                Minimum number of observations in window required to have a value; otherwise, result is ``np.nan`` .

            weights : list, default None
                An optional slice with the same length as the window that will be multiplied element-wise with the values in the window.

        Returns
        -------
            prismstudio._PrismComponent
                n samples mean timeseries of the PrismComponent.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            >>> close_result = close.sample_mean(n=5)
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date   value  Ticker
            0         2586086  2010-01-04  46.890     AFL
            1         2586086  2010-01-05  47.320     AFL
            2         2586086  2010-01-06  47.806     AFL
            3         2586086  2010-01-07  48.412     AFL
            4         2586086  2010-01-08  49.044     AFL
            ...           ...         ...     ...     ...
            755887  344286611  2011-10-25  44.146     ITT
            755888  344286611  2011-10-26  44.024     ITT
            755889  344286611  2011-10-27  44.146     ITT
            755890  344286611  2011-10-28  44.294     ITT
            755891  344286611  2011-10-31  44.492     ITT
        """
        if (weights is not None) and (len(weights) != n):
            raise PrismValueError("Number of weights should equal to n")


    @_validate_args
    @sample_operation
    @operation
    def sample_ewma(self, n: int, min_sample: int = 1):
        r"""
        Exponential moving average over given samples n.

        .. math:: EWMA_t = ar_t - (1-a)EWMA_(t-1)

        Parameters
        ----------
            n : int
                | Number of time samples for calculating exponential moving average, accepts negative values.

                .. math:: a = \frac{2}{n+1}

            min_sample : int, default 1
                Minimum number of observations in window required to have a value; otherwise, result is ``np.nan`` .

        Returns
        -------
            prismstudio._PrismComponent
                Exponential moving standard deviation of the PrismComponent.

        """
        ...


    @_validate_args
    @sample_operation
    @operation
    def sample_ewmstd(self, n: int, min_sample: int = 1):
        r"""
        Exponential moving standard deviation over given samples n.

        .. math:: EWMA_t = ar_t - (1-a)EWMA_(t-1)

        Parameters
        ----------
            n : int
                | Number of time samples for calculating exponential moving average, accepts negative values.

                .. math:: a = \frac{2}{n+1}

            min_sample : int, default 1
                Minimum number of observations in window required to have a value; otherwise, result is ``np.nan`` .

        Returns
        -------
            prismstudio._PrismComponent
                Exponential moving average of the PrismComponent.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            >>> close_result = close.sample_ewma(n=5)
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date      value  Ticker
            0         2586086  2010-01-04  46.976135     AFL
            1         2586086  2010-01-05  47.674993     AFL
            2         2586086  2010-01-06  48.266404     AFL
            3         2586086  2010-01-07  48.828901     AFL
            4         2586086  2010-01-08  49.026019     AFL
            ...           ...         ...        ...     ...
            755887  344286611  2011-10-25  44.262644     ITT
            755888  344286611  2011-10-26  44.021763     ITT
            755889  344286611  2011-10-27  44.117842     ITT
            755890  344286611  2011-10-28  44.408561     ITT
            755891  344286611  2011-10-31  44.805707     ITT
        """
        ...

    @_validate_args
    @sample_operation
    @operation
    def sample_ewmvar(self, n: int, min_sample: int = 1):
        r"""
        Exponential moving standard variance over given samples n.

        .. math:: EWMA_t = ar_t - (1-a)EWMA_(t-1)

        Parameters
        ----------
            n : int
                | Number of time samples for calculating exponential moving average, accepts negative values.

                | .. math:: a = \frac{2}{n+1}

            min_sample : int, default 1
                Minimum number of observations in window required to have a value; otherwise, result is ``np.nan`` .

            weights : list, default None
                An optional slice with the same length as the window that will be multiplied element-wise with the values in the window.

        Returns
        -------
            prismstudio._PrismComponent
                n period variance timeseries of the PrismComponent.

        """
        ...

    @_validate_args
    @sample_operation
    @operation
    def sample_median(self, n: int, min_sample: int = 1, weights: list = None):
        r"""
        Median of the values over given samples n.

        Parameters
        ----------
            n : int
                | Number of time samples for calculating median values, accepts negative values.

            min_sample : int, default 1
                Minimum number of observations in window required to have a value; otherwise, result is ``np.nan`` .

            weights : list, default None
                An optional slice with the same length as the window that will be multiplied element-wise with the values in the window.

        Returns
        -------
            prismstudio._PrismComponent
                n samples median timeseries of the PrismComponent.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            >>> close_result = close.sample_median(n=3)
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  value  Ticker
            0         2586086  2010-01-04  46.88     AFL
            1         2586086  2010-01-05  47.57     AFL
            2         2586086  2010-01-06  48.95     AFL
            3         2586086  2010-01-07  49.38     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755919  344286611  2011-10-25  44.25     ITT
            755920  344286611  2011-10-26  44.02     ITT
            755921  344286611  2011-10-27  44.02     ITT
            755922  344286611  2011-10-28  44.31     ITT
            755923  344286611  2011-10-31  44.99     ITT
        """
        if (weights is not None) and (len(weights) != n):
            raise PrismValueError("Number of weights should equal to n")

    @_validate_args
    @sample_operation
    @operation
    def sample_sum(self, n: int, min_sample: int = 1, weights: list = None):
        r"""
        The sum of the values over given samples n.

        Parameters
        ----------
            n : int
                | Number of time samples for calculating sum values, accepts negative values.

            min_sample : int, default 1
                Minimum number of observations in window required to have a value; otherwise, result is ``np.nan`` .

            weights : list, default None
                An optional slice with the same length as the window that will be multiplied element-wise with the values in the window.

        Returns
        -------
            prismstudio._PrismComponent
                n samples sum timeseries of the PrismComponent.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            >>> close_result = close.sample_sum(n=2)
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  value  Ticker
            0         2586086  2010-01-04  93.82     AFL
            1         2586086  2010-01-05  96.52     AFL
            2         2586086  2010-01-06  98.33     AFL
            3         2586086  2010-01-07  99.29     AFL
            4         2586086  2010-01-08  99.32     AFL
            ...           ...         ...    ...     ...
            755947  344286611  2011-10-25  88.63     ITT
            755948  344286611  2011-10-26  87.56     ITT
            755949  344286611  2011-10-27  87.85     ITT
            755950  344286611  2011-10-28  89.30     ITT
            755951  344286611  2011-10-31  90.59     ITT
        """
        if (weights is not None) and (len(weights) != n):
            raise PrismValueError("Number of weights should equal to n")

    @_validate_args
    @sample_operation
    @operation
    def sample_std(self, n: int, min_sample: int = 1, weights: list = None):
        r"""
        Standard deviation of the values over given samples n.

        Parameters
        ----------
            n : int
                | Number of time samples for calculating standard deviation values, accepts negative values.

            min_sample : int, default 1
                Minimum number of observations in window required to have a value; otherwise, result is ``np.nan`` .

            weights : list, default None
                An optional slice with the same length as the window that will be multiplied element-wise with the values in the window.

        Returns
        -------
            prismstudio._PrismComponent
                n samples standard deviation timeseries of the PrismComponent.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            >>> close_result = close.sample_std(n=5)
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date     value  Ticker
            0         2586086  2010-01-04  0.470053     AFL
            1         2586086  2010-01-05  1.024061     AFL
            2         2586086  2010-01-06  1.334215     AFL
            3         2586086  2010-01-07  1.487757     AFL
            4         2586086  2010-01-08  0.891392     AFL
            ...           ...         ...       ...     ...
            755887  344286611  2011-10-25  0.332009     ITT
            755888  344286611  2011-10-26  0.428287     ITT
            755889  344286611  2011-10-27  0.398786     ITT
            755890  344286611  2011-10-28  0.554103     ITT
            755891  344286611  2011-10-31  0.812078     ITT
        """
        if (weights is not None) and (len(weights) != n):
            raise PrismValueError("Number of weights should equal to n")

    @_validate_args
    @sample_operation
    @operation
    def sample_var(self, n: int, min_sample: int = 1, weights: list = None):
        r"""
        Variance of the values over given samples n.

        Parameters
        ----------
            n : int
                | Number of time samples for calculating variance values, accepts negative values.

            min_sample : int, default 1
                Minimum number of observations in window required to have a value; otherwise, result is ``np.nan`` .

            weights : list, default None
                An optional slice with the same length as the window that will be multiplied element-wise with the values in the window.

        Returns
        -------
            prismstudio._PrismComponent
                n samples variance timeseries of the PrismComponent.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            >>> close_result = close.sample_var(n=5)
            TODO
        """
        if (weights is not None) and (len(weights) != n):
            raise PrismValueError("Number of weights should equal to n")

    @_validate_args
    @sample_operation
    @operation
    def sample_z_score(self, n: int, min_sample: int = 1, weights: list = None):
        r"""
        Z-score of the values over given samples n.

        Parameters
        ----------
            n : int
                | Number of time samples for calculating z-score values, accepts negative values.

            min_sample : int, default 1
                Minimum number of observations in window required to have a value; otherwise, result is ``np.nan`` .

            weights : list, default None
                An optional slice with the same length as the window that will be multiplied element-wise with the values in the window.

        Returns
        -------
            prismstudio._PrismComponent
                n samples z-score timeseries of the PrismComponent.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            >>> close_result = close.sample_z_score(n=5)
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date      value  Ticker
            0         2586086  2010-01-04   1.446645     AFL
            1         2586086  2010-01-05   1.591703     AFL
            2         2586086  2010-01-06   1.179720     AFL
            3         2586086  2010-01-07   1.006885     AFL
            4         2586086  2010-01-08   0.410594     AFL
            ...           ...         ...        ...     ...
            755885  344286611  2011-10-25  -0.379508     ITT
            755886  344286611  2011-10-26  -1.130083     ITT
            755887  344286611  2011-10-27   0.411248     ITT
            755888  344286611  2011-10-28   1.256084     ITT
            755889  344286611  2011-10-31   1.364402     ITT
        """
        if (weights is not None) and (len(weights) != n):
            raise PrismValueError("Number of weights should equal to n")

    @_validate_args
    @sample_operation
    @operation
    def sample_skew(self, n: int, min_sample: int = 1, weights: list = None):
        r"""
        Skewness of the values over given samples n.

        Parameters
        ----------
            n : int
                | Number of time samples for calculating skewness values, accepts negative values.

            min_sample : int, default 1
                Minimum number of observations in window required to have a value; otherwise, result is ``np.nan`` .

            weights : list, default None
                An optional slice with the same length as the window that will be multiplied element-wise with the values in the window.

        Returns
        -------
            prismstudio._PrismComponent
                n sample skewness timeseries of the PrismComponent.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            >>> close_result = close.sample_skew(n=5)
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date     value  Ticker
            0         2586086  2010-01-04  0.207711     AFL
            1         2586086  2010-01-05  1.158318     AFL
            2         2586086  2010-01-06  0.144256     AFL
            3         2586086  2010-01-07 -0.794403     AFL
            4         2586086  2010-01-08 -1.451241     AFL
            ...           ...         ...       ...     ...
            755885  344286611  2011-10-25  0.117328     ITT
            755886  344286611  2011-10-26  0.346765     ITT
            755887  344286611  2011-10-27 -0.782576     ITT
            755888  344286611  2011-10-28 -0.197206     ITT
            755889  344286611  2011-10-31  0.396619     ITT
        """
        if (weights is not None) and (len(weights) != n):
            raise PrismValueError("Number of weights should equal to n")

    # periods operations
    @_validate_args
    @operation
    def period_count(self, period: str):
        """
        Number of samples within given given.

        Parameters
        ----------
            period : str
                | Desired period for counting how many data points are available.
                | Please note that the parameter value indicates the time frame covered and not the count of individual data samples.
                | For example, if you input '365D' into the parameter, the function will be computed using all available data spanning a 365-day period.

        Returns
        -------
            prismstudio._PrismComponent
                period count timeseries of the PrismComponent.
        """
        ...

    @_validate_args
    @operation
    def period_z_score(self, period: str, min_sample: int = 1):
        """
        Z-scores of the data within given period.

        Parameters
        ----------
            period : str
                | Desired period of data used to calculate each Z-score.
                | Please note that the parameter value indicates the time frame covered and not the count of individual data samples.
                | For example, if you input '365D' into the parameter, the function will be computed using all available data spanning a 365-day period.

            min_sample : int, default 1
                Minimum number of observations in period required to have a value; otherwise, result is ``np.nan`` .

        Returns
        -------
            prismstudio._PrismComponent
                period z-score timeseries of the PrismComponent.
        """
        ...

    @_validate_args
    @operation
    def period_max(self, period: str, min_sample: int = 1):
        """
        Maximum of the data within given period.

        Parameters
        ----------
            period : str
                | Desired period of data used to determine the maximum data point.
                | Please note that the parameter value indicates the time frame covered and not the count of individual data samples.
                | For example, if you input '365D' into the parameter, the function will be computed using all available data spanning a 365-day period.

            min_sample : int, default 1
                Minimum number of observations in period required to have a value; otherwise, result is ``np.nan`` .

        Returns
        -------
            prismstudio._PrismComponent
                period max timeseries of the PrismComponent.
        """
        ...

    @_validate_args
    @operation
    def period_min(self, period: str, min_sample: int = 1):
        """
        Minimum of the data within given period.

        Parameters
        ----------
            period : str
                | Desired period of data used to determine the minimum data point.
                | Please note that the parameter value indicates the time frame covered and not the count of individual data samples.
                | For example, if you input '365D' into the parameter, the function will be computed using all available data spanning a 365-day period.

            min_sample : int, default 1
                Minimum number of observations in period required to have a value; otherwise, result is ``np.nan`` .

        Returns
        -------
            prismstudio._PrismComponent
                period min timeseries of the PrismComponent.
        """
        ...

    @_validate_args
    @operation
    def period_mean(self, period: str, min_sample: int = 1):
        """
        Mean of the data within given period.

        Parameters
        ----------
            period : str
                | Desired period of data used to calculate each mean.
                | Please note that the parameter value indicates the time frame covered and not the count of individual data samples.
                | For example, if you input '365D' into the parameter, the function will be computed using all available data spanning a 365-day period.

            min_sample : int, default 1
                Minimum number of observations in period required to have a value; otherwise, result is ``np.nan`` .

        Returns
        -------
            prismstudio._PrismComponent
                period mean timeseries of the PrismComponent.
        """
        ...

    @_validate_args
    @operation
    def period_std(self, period: str, min_sample: int = 1):
        """
        Standard deviation of the data within given period.

        Parameters
        ----------
            period : str
                | Desired period of data used to calculate each standard deviation.
                | Please note that the parameter value indicates the time frame covered and not the count of individual data samples.
                | For example, if you input '365D' into the parameter, the function will be computed using all available data spanning a 365-day period.

            min_sample : int, default 1
                Minimum number of observations in period required to have a value; otherwise, result is ``np.nan`` .

        Returns
        -------
            prismstudio._PrismComponent
                period standard deviation timeseries of the PrismComponent.
        """
        ...

    @_validate_args
    @operation
    def period_var(self, period: str, min_sample: int = 1):
        """
        Variance of the data within given period.

        Parameters
        ----------
            period : str
                | Desired period of data used to calculate each variance.
                | Please note that the parameter value indicates the time frame covered and not the count of individual data samples.
                | For example, if you input '365D' into the parameter, the function will be computed using all available data spanning a 365-day period.

            min_sample : int, default 1
                Minimum number of observations in period required to have a value; otherwise, result is ``np.nan`` .

        Returns
        -------
            prismstudio._PrismComponent
                period variance timeseries of the PrismComponent.
        """
        ...

    @_validate_args
    @operation
    def period_median(self, period: str, min_sample: int = 1):
        """
        Median of the data within given period.

        Parameters
        ----------
            period : str
                | Desired period of data used to calculate each median.
                | Please note that the parameter value indicates the time frame covered and not the count of individual data samples.
                | For example, if you input '365D' into the parameter, the function will be computed using all available data spanning a 365-day period.

            min_sample : int, default 1
                Minimum number of observations in period required to have a value; otherwise, result is ``np.nan`` .

        Returns
        -------
            prismstudio._PrismComponent
                period median timeseries of the PrismComponent.
        """
        ...

    @_validate_args
    @operation
    def period_sum(self, period: str, min_sample: int = 1):
        """
        Sum of the data within given period.

        Parameters
        ----------
            period : str
                | Desired period of data used to calculate each sum.
                | Please note that the parameter value indicates the time frame covered and not the count of individual data samples.
                | For example, if you input '365D' into the parameter, the function will be computed using all available data spanning a 365-day period.

            min_sample : int, default 1
                Minimum number of observations in period required to have a value; otherwise, result is ``np.nan`` .

        Returns
        -------
            prismstudio._PrismComponent
                period sum timeseries of the PrismComponent.
        """
        ...

    # cross-sectional operations
    @_validate_args
    @cross_sectional_operation
    def cross_sectional_rank(self, rank_method: const.RankType = "standard", ascending: bool = True):
        """
        Numerical data ranks (1 through n) across each date for each element.

        Parameters
        ----------
            rank_method : str {'standard', 'modified', 'dense', 'ordinal', 'fractional'}, default 'standard'
                | Method for how equal values are assigned a rank.

                - standard: 1 2 2 4
                - modified: 1 3 3 4
                - dense: 1 2 2 3
                - ordinal: 1 2 3 4
                - fractional: 1 2.5 2.5 4

            ascending : bool, default True
                Whether or not the elements should be ranked in ascending order.

        Returns
        -------
            prismstudio._PrismComponent
                Cross sectional ranking of the PrismComponent.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            >>> close_result = close.samples_pct_change(21).cross_sectional_rank() # trading month momentum cross sectional ranking
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  value  Ticker
            0         2586086  2010-01-04  187.0     AFL
            1         2586086  2010-01-05  337.0     AFL
            2         2586086  2010-01-06  355.0     AFL
            3         2586086  2010-01-07  368.0     AFL
            4         2586086  2010-01-08  314.0     AFL
            ...           ...         ...    ...     ...
            755337  344286611  2011-10-25  150.0     ITT
            755338  344286611  2011-10-26   78.0     ITT
            755339  344286611  2011-10-27   63.0     ITT
            755340  344286611  2011-10-28   76.0     ITT
            755341  344286611  2011-10-31  166.0     ITT
        """
        ...

    @_validate_args
    @cross_sectional_operation
    def cross_sectional_percentile(self, rank_method: const.RankType = "standard", ascending: bool = True):
        """
        Numerical data percentiles (between 0 and 1) across each date for each element.

        Parameters
        ----------
            rank_method : str {'standard', 'modified', 'dense', 'ordinal', 'fractional'}, default 'standard'
                | Method for how equal values are assigned a rank.

                - standard: 1 2 2 4
                - modified: 1 3 3 4
                - dense: 1 2 2 3
                - ordinal: 1 2 3 4
                - fractional: 1 2.5 2.5 4

            ascending : bool, default True
                Whether or not the elements should be ranked in ascending order.

        Returns
        -------
            prismstudio._PrismComponent
                Group percentile timeseries of the PrismComponent.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            >>> cross_percentile = close.cross_sectional_percentile()
            >>> cross_percentile.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  value  Ticker
            0         2586086  2010-01-04  0.684    AFL
            1         2586086  2010-01-05  0.712    AFL
            2         2586086  2010-01-06  0.706    AFL
            3         2586086  2010-01-07  0.712    AFL
            4         2586086  2010-01-08  0.694    AFL
            ...           ...         ...    ...    ...
            755971  344286611  2011-10-25  0.578    ITT
            755972  344286611  2011-10-26  0.564    ITT
            755973  344286611  2011-10-27  0.552    ITT
            755974  344286611  2011-10-28  0.558    ITT
            755975  344286611  2011-10-31  0.582    ITT
        """
        ...

    @_validate_args
    @cross_sectional_operation
    def cross_sectional_quantile(
        self,
        bins: int,
        rank_method: const.RankType = "standard",
        ascending: bool = True,
        right: bool = True,
    ):
        """
        Numerical quantiles across each date for each element.

        Parameters
        ----------
            bins : int
                Number of quantiles. 10 for deciles, 4 for quartiles, etc.

            rank_method : str {'standard', 'modified', 'dense', 'ordinal', 'fractional'}, default 'standard'
                | Method for how equal values are assigned a rank.

                - standard: 1 2 2 4
                - modified: 1 3 3 4
                - dense: 1 2 2 3
                - ordinal: 1 2 3 4
                - fractional: 1 2.5 2.5 4

            ascending : bool, default True
                Whether or not the elements should be ranked in ascending order.

            right : bool, default True
                | If True, given a border value in between bins, whether to put the sample in the which bins.
                | For example, if the value borders for bin 1 is between 0 ~ 5 and bin 2 is between 5 ~ 10, if right is True, and a sample has a value 5, then it will be assigned bin 1. if False, then bin 2.

        Returns
        -------
            prismstudio._PrismComponent
                Group percentile timeseries of the PrismComponent.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            >>> close_result = close.samples_pct_change(21).cross_sectional_quantile(5) #trading month momentum cross sectional quantile
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  value  Ticker
            0         2586086  2010-01-04    2.0     AFL
            1         2586086  2010-01-05    4.0     AFL
            2         2586086  2010-01-06    4.0     AFL
            3         2586086  2010-01-07    4.0     AFL
            4         2586086  2010-01-08    4.0     AFL
            ...           ...         ...    ...     ...
            755337  344286611  2011-10-25    2.0     ITT
            755338  344286611  2011-10-26    1.0     ITT
            755339  344286611  2011-10-27    1.0     ITT
            755340  344286611  2011-10-28    1.0     ITT
            755341  344286611  2011-10-31    2.0     ITT
        """
        ...

    @_validate_args
    @cross_sectional_operation
    def cross_sectional_z_score(self):
        """
        Z-score of the values over across each date for each element.

        Parameters
        ----------
            group : PrismComponent
                Used to determine the groups.

        Returns
        -------
            prismstudio._PrismComponent
                Group z-score timeseries of the PrismComponent.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            # look for GICS Sector Security Master attribute to create a group
            >>> ps.securitymaster.list_attribute()
            ['Trading Item ID',
            'VALOR',
            'GVKEY',
            'MarkIt Red Code',
            'Country',
            'GICS Sector',
            'WKN',
            'CINS',
            "Moody's Issuer Number",
            'GICS Group',
            'SEDOL',
            'Company Name',
            'CMA Entity ID',
            'CIQ Primary',
            'NAICS',
            'Factset Security ID',
            'Composite FIGI',
            'Share Class FIGI',
            'FIGI',
            'Compustat Primary',
            'Factset Company ID',
            'Ticker',
            'Factset Entity ID',
            'GVKEYIID',
            'Company ID',
            'Factset Listing ID',
            'LEI',
            'IBES Ticker',
            'CUSIP',
            'GICS Sub-Industry',
            'Barra ID',
            'ISIN',
            'MIC',
            'SIC',
            'Security ID',
            'Trade Currency',
            'GICS Industry',
            'Fitch Issuer ID',
            'RatingsXpress Entity ID',
            'SNL Institution ID']

            >>> gics_sector = ps.securitymaster.attribute('GICS Sector') # data component: GICS Sector
            >>> close_result = close.samples_pct_change(21).group_z_score(gics_sector) # trading month momentum group ranking on gics sector
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])\
                    listingid        date      value  Ticker
            0         2586086  2010-01-04  -0.015607     AFL
            1         2586086  2010-01-05   0.421663     AFL
            2         2586086  2010-01-06   0.754689     AFL
            3         2586086  2010-01-07   0.282194     AFL
            4         2586086  2010-01-08   0.051700     AFL
            ...           ...         ...        ...     ...
            755337  344286611  2011-10-25  -0.891504     ITT
            755338  344286611  2011-10-26  -1.087371     ITT
            755339  344286611  2011-10-27  -1.296089     ITT
            755340  344286611  2011-10-28  -1.136280     ITT
            755341  344286611  2011-10-31  -0.707442     ITT
        """
        ...

    @_validate_args
    @cross_sectional_operation
    def cross_sectional_demean(self):
        """
        Demean of the values over across each date for each element.


        Returns
        -------
            prismstudio._PrismComponent
                Cross sectional demean timeseries of the PrismComponent.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            >>> close_result = close.samples_pct_change(21).cross_sectional_demean() #trading month momentum cross sectional z-score
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date      value  Ticker
            0         2586086  2010-01-04  -0.025406     AFL
            1         2586086  2010-01-05   0.017973     AFL
            2         2586086  2010-01-06   0.024147     AFL
            3         2586086  2010-01-07   0.031885     AFL
            4         2586086  2010-01-08   0.005299     AFL
            ...           ...         ...        ...     ...
            755337  344286611  2011-10-25  -0.035976     ITT
            755338  344286611  2011-10-26  -0.063636     ITT
            755339  344286611  2011-10-27  -0.105008     ITT
            755340  344286611  2011-10-28  -0.094468     ITT
            755341  344286611  2011-10-31  -0.046099     ITT
        """
        ...

    @_validate_args
    @cross_sectional_operation
    def cross_sectional_sum(self):
        """
        Sum of the values over across each date.

        Returns
        -------
            prismstudio._PrismComponent
                Cross sectional sum timeseries of the PrismComponent.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            >>> cross_sum = close.cross_sectional_sum()
            >>> cross_sum.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31')
                        date       value
            0      2010-01-04  21878.8753
            1      2010-01-05  21932.3200
            2      2010-01-06  21980.7800
            3      2010-01-07  22052.8920
            4      2010-01-08  22144.2920
            ...           ...         ...
            1505  2015-12-24  41419.2350
            1506  2015-12-28  41388.1900
            1507  2015-12-29  41858.7300
            1508  2015-12-30  41575.1400
            1509  2015-12-31  41211.8500
        """
        ...

    @_validate_args
    @cross_sectional_operation
    def cross_sectional_max(self):
        """
        Maximum of the values over across each date.

        Returns
        -------
            prismstudio._PrismComponent
                Cross sectional max timeseries of the PrismComponent.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            >>> cross_max = close.cross_sectional_max()
            >>> cross_max.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31')
                        date    value
            0      2010-01-04   626.75
            1      2010-01-05   623.99
            2      2010-01-06   608.26
            3      2010-01-07   594.10
            4      2010-01-08   602.02
            ...           ...      ...
            1505  2015-12-24  1273.07
            1506  2015-12-28  1272.96
            1507  2015-12-29  1302.40
            1508  2015-12-30  1289.16
            1509  2015-12-31  1274.95
        """
        ...

    @_validate_args
    @cross_sectional_operation
    def cross_sectional_min(self):
        """
        Minimum of the values over across each date.

        Returns
        -------
            prismstudio._PrismComponent
                Cross sectional min timeseries of the PrismComponent.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            >>> cross_min = close.cross_sectional_min()
            >>> cross_min.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31')
                        date  value
            0      2010-01-04   1.84
            1      2010-01-05   1.80
            2      2010-01-06   1.79
            3      2010-01-07   1.80
            4      2010-01-08   1.80
            ...           ...    ...
            1505  2015-12-24   4.45
            1506  2015-12-28   4.07
            1507  2015-12-29   4.58
            1508  2015-12-30   4.40
            1509  2015-12-31   4.50
        """
        ...

    @_validate_args
    @cross_sectional_operation
    def cross_sectional_mean(self):
        """
        Mean of the values over across each date.

        Returns
        -------
            prismstudio._PrismComponent
                Cross sectional mean timeseries of the PrismComponent.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            >>> cross_mean = close..cross_sectional_mean()
            >>> cross_mean.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31')
                        date     value
            0       2010-01-04  1.677333
            1       2010-01-05  1.689753
            2       2010-01-06  1.693551
            3       2010-01-07  1.698188
            4       2010-01-08  1.693815
            ...            ...       ...
            755971  2011-10-25  1.643650
            755972  2011-10-26  1.638888
            755973  2011-10-27  1.646502
            755974  2011-10-28  1.653116
            755975  2011-10-31  1.658965
        """
        ...

    @_validate_args
    @cross_sectional_operation
    def cross_sectional_std(self):
        """
        Standard deviation of the values over across each date.

        Returns
        -------
            prismstudio._PrismComponent
                Cross sectional standard deviation timeseries of the PrismComponent.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            >>> close_result = close.samples_pct_change(21).cross_sectional_std() #trading month momentum cross sectional z-score
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date      value  Ticker
            0         2586086  2010-01-04  -0.025406     AFL
            1         2586086  2010-01-05   0.017973     AFL
            2         2586086  2010-01-06   0.024147     AFL
            3         2586086  2010-01-07   0.031885     AFL
            4         2586086  2010-01-08   0.005299     AFL
            ...           ...         ...        ...     ...
            755337  344286611  2011-10-25  -0.035976     ITT
            755338  344286611  2011-10-26  -0.063636     ITT
            755339  344286611  2011-10-27  -0.105008     ITT
            755340  344286611  2011-10-28  -0.094468     ITT
            755341  344286611  2011-10-31  -0.046099     ITT
        """
        ...

    @_validate_args
    @cross_sectional_operation
    def cross_sectional_median(self):
        """
        Median of the values over across each date.

        Returns
        -------
            prismstudio._PrismComponent
                Cross sectional median timeseries of the PrismComponent.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            >>> cross_median = close.cross_sectional_median()
            >>> cross_median.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31')
                        date   value
            0       2010-01-04  35.575
            1       2010-01-05  35.390
            2       2010-01-06  35.365
            3       2010-01-07  35.230
            4       2010-01-08  35.300
            ...            ...     ...
            755971  2011-10-25  60.525
            755972  2011-10-26  60.410
            755973  2011-10-27  61.270
            755974  2011-10-28  60.905
            755975  2011-10-31  60.040
        """
        ...

    @_validate_args
    @cross_sectional_operation
    def cross_sectional_count(self):
        """
        Count of the values over across each date.

        Returns
        -------
            prismstudio._PrismComponent
                Cross sectional count timeseries of the PrismComponent.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            >>> cross_count = close.cross_sectional_count()
            >>> cross_count.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31')
                        date  value
            0      2010-01-04    500
            1      2010-01-05    500
            2      2010-01-06    500
            3      2010-01-07    500
            4      2010-01-08    500
            ...           ...    ...
            1505  2015-12-24    504
            1506  2015-12-28    504
            1507  2015-12-29    504
            1508  2015-12-30    504
            1509  2015-12-31    504
        """
        ...

    @_validate_args
    @cross_sectional_operation
    def cross_sectional_skew(self):
        """
        Skewness of the values over across each date.

        Returns
        -------
            prismstudio._PrismComponent
                Cross sectional skewness timeseries of the PrismComponent.

        Examples
        --------
        TODO
        """
        ...

    @_validate_args
    @cross_sectional_operation
    def cross_sectional_kurt(self):
        """
        Kurtosis of the values over across each date.

        Returns
        -------
            prismstudio._PrismComponent
                Cross sectional kurtosis timeseries of the PrismComponent.

        Examples
        --------
        TODO
        """
        ...

    @_validate_args
    @cross_sectional_operation
    def cross_sectional_mode(self):
        """
        Mode of the values over across each date.

        Returns
        -------
            prismstudio._PrismComponent
                Cross sectional mode timeseries of the PrismComponent.

        Examples
        --------
        TODO
        """
        ...

    @_validate_args
    @cross_sectional_operation
    def cross_sectional_prod(self):
        """
        Product of the values over across each date.

        Returns
        -------
            prismstudio._PrismComponent
                Cross sectional product timeseries of the PrismComponent.

        Examples
        --------
        TODO
        """
        ...

    # group operations
    @_validate_args
    @group_operation
    def group_mean(self, group: _AbstractPrismComponent):
        """
        Mean of values over across each date and group.

        Parameters
        ----------
            group : PrismComponent
                Used to determine the groups.

        Returns
        -------
            prismstudio._PrismComponent
                Group mean timeseries of the PrismComponent.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            # look for GICS Sector Security Master attribute to create a group
            >>> ps.securitymaster.list_attribute()
            ['Trading Item ID',
            'VALOR',
            'GVKEY',
            'MarkIt Red Code',
            'Country',
            'GICS Sector',
            'WKN',
            'CINS',
            "Moody's Issuer Number",
            'GICS Group',
            'SEDOL',
            'Company Name',
            'CMA Entity ID',
            'CIQ Primary',
            'NAICS',
            'Factset Security ID',
            'Composite FIGI',
            'Share Class FIGI',
            'FIGI',
            'Compustat Primary',
            'Factset Company ID',
            'Ticker',
            'Factset Entity ID',
            'GVKEYIID',
            'Company ID',
            'Factset Listing ID',
            'LEI',
            'IBES Ticker',
            'CUSIP',
            'GICS Sub-Industry',
            'Barra ID',
            'ISIN',
            'MIC',
            'SIC',
            'Security ID',
            'Trade Currency',
            'GICS Industry',
            'Fitch Issuer ID',
            'RatingsXpress Entity ID',
            'SNL Institution ID']

            >>> gics_sector = ps.securitymaster.attribute('GICS Sector') # Data Component: GICS Sector
            >>> close_result = close.samples_pct_change(21).group_mean(gics_sector) # trading month momentum group ranking on gics sector
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31')
                   GICS sector        date     value
            0            10.0  2010-01-04  0.082004
            1            10.0  2010-01-05  0.118139
            2            10.0  2010-01-06  0.142810
            3            10.0  2010-01-07  0.142869
            4            10.0  2010-01-08  0.181065
            ...             ...         ...       ...
            15095         55.0  2015-12-24  0.014816
            15096         55.0  2015-12-28  0.023774
            15097         55.0  2015-12-29  0.028174
            15098         55.0  2015-12-30  0.021684
            15099         55.0  2015-12-31  0.005876
        """
        ...

    @_validate_args
    @group_operation
    def group_std(self, group: _AbstractPrismComponent):
        """
        Standard deviation of values over across each date and group.

        Parameters
        ----------
            group : PrismComponent
                Used to determine the groups.

        Returns
        -------
            prismstudio._PrismComponent
                Group standard deviation timeseries of the PrismComponent.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            # look for GICS Sector Security Master attribute to create a group
            >>> ps.securitymaster.list_attribute()
            ['Trading Item ID',
            'VALOR',
            'GVKEY',
            'MarkIt Red Code',
            'Country',
            'GICS Sector',
            'WKN',
            'CINS',
            "Moody's Issuer Number",
            'GICS Group',
            'SEDOL',
            'Company Name',
            'CMA Entity ID',
            'CIQ Primary',
            'NAICS',
            'Factset Security ID',
            'Composite FIGI',
            'Share Class FIGI',
            'FIGI',
            'Compustat Primary',
            'Factset Company ID',
            'Ticker',
            'Factset Entity ID',
            'GVKEYIID',
            'Company ID',
            'Factset Listing ID',
            'LEI',
            'IBES Ticker',
            'CUSIP',
            'GICS Sub-Industry',
            'Barra ID',
            'ISIN',
            'MIC',
            'SIC',
            'Security ID',
            'Trade Currency',
            'GICS Industry',
            'Fitch Issuer ID',
            'RatingsXpress Entity ID',
            'SNL Institution ID']

            >>> gics_sector = ps.securitymaster.attribute('GICS Sector') # data component: GICS Sector
            >>> close_result = close.samples_pct_change(21).group_std(gics_sector) # trading month momentum group ranking on gics sector
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31')
                   GICS sector        date     value
            0            10.0  2010-01-04  0.070820
            1            10.0  2010-01-05  0.078481
            2            10.0  2010-01-06  0.080737
            3            10.0  2010-01-07  0.081728
            4            10.0  2010-01-08  0.091463
            ...             ...         ...       ...
            15095         55.0  2015-12-24  0.032398
            15096         55.0  2015-12-28  0.031411
            15097         55.0  2015-12-29  0.027771
            15098         55.0  2015-12-30  0.036954
            15099         55.0  2015-12-31  0.028405
        """
        ...

    @_validate_args
    @group_operation
    def group_min(self, group: _AbstractPrismComponent):
        """
        Minimum of values over across each date and group.

        Parameters
        ----------
            group : PrismComponent
                Used to determine the groups.

        Returns
        -------
            prismstudio._PrismComponent
                Group min timeseries of the PrismComponent

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            # look for GICS Sector Security Master attribute to create a group
            >>> ps.securitymaster.list_attribute()
            ['Trading Item ID',
            'VALOR',
            'GVKEY',
            'MarkIt Red Code',
            'Country',
            'GICS Sector',
            'WKN',
            'CINS',
            "Moody's Issuer Number",
            'GICS Group',
            'SEDOL',
            'Company Name',
            'CMA Entity ID',
            'CIQ Primary',
            'NAICS',
            'Factset Security ID',
            'Composite FIGI',
            'Share Class FIGI',
            'FIGI',
            'Compustat Primary',
            'Factset Company ID',
            'Ticker',
            'Factset Entity ID',
            'GVKEYIID',
            'Company ID',
            'Factset Listing ID',
            'LEI',
            'IBES Ticker',
            'CUSIP',
            'GICS Sub-Industry',
            'Barra ID',
            'ISIN',
            'MIC',
            'SIC',
            'Security ID',
            'Trade Currency',
            'GICS Industry',
            'Fitch Issuer ID',
            'RatingsXpress Entity ID',
            'SNL Institution ID']

            >>> gics_sector = ps.securitymaster.attribute('GICS Sector') # Data Component: GICS Sector
            >>> close_result = close.samples_pct_change(21).group_min(gics_sector) # trading month momentum group ranking on gics sector
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31')
                   GICS sector        date      value
            0            10.0  2010-01-04  -0.087611
            1            10.0  2010-01-05  -0.074277
            2            10.0  2010-01-06  -0.056970
            3            10.0  2010-01-07  -0.053816
            4            10.0  2010-01-08  -0.047019
            ...             ...         ...        ...
            15095         55.0  2015-12-24  -0.088748
            15096         55.0  2015-12-28  -0.066502
            15097         55.0  2015-12-29  -0.038038
            15098         55.0  2015-12-30  -0.102751
            15099         55.0  2015-12-31  -0.060464
        """
        ...

    @_validate_args
    @group_operation
    def group_max(self, group: _AbstractPrismComponent):
        """
        Maximum of values over across each date and group.

        Parameters
        ----------
            group : PrismComponent
                Used to determine the groups.

        Returns
        -------
            prismstudio._PrismComponent
                Group max timeseries of the PrismComponent

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            # look for GICS Sector Security Master attribute to create a group
            >>> ps.securitymaster.list_attribute()
            ['Trading Item ID',
            'VALOR',
            'GVKEY',
            'MarkIt Red Code',
            'Country',
            'GICS Sector',
            'WKN',
            'CINS',
            "Moody's Issuer Number",
            'GICS Group',
            'SEDOL',
            'Company Name',
            'CMA Entity ID',
            'CIQ Primary',
            'NAICS',
            'Factset Security ID',
            'Composite FIGI',
            'Share Class FIGI',
            'FIGI',
            'Compustat Primary',
            'Factset Company ID',
            'Ticker',
            'Factset Entity ID',
            'GVKEYIID',
            'Company ID',
            'Factset Listing ID',
            'LEI',
            'IBES Ticker',
            'CUSIP',
            'GICS Sub-Industry',
            'Barra ID',
            'ISIN',
            'MIC',
            'SIC',
            'Security ID',
            'Trade Currency',
            'GICS Industry',
            'Fitch Issuer ID',
            'RatingsXpress Entity ID',
            'SNL Institution ID']

            >>> gics_sector = ps.securitymaster.attribute('GICS Sector') # Data Component: GICS Sector
            >>> close_result = close.samples_pct_change(21).group_max(gics_sector) # trading month momentum group ranking on gics sector
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31')
                   GICS sector        date     value
            0            10.0  2010-01-04  0.205486
            1            10.0  2010-01-05  0.257924
            2            10.0  2010-01-06  0.326705
            3            10.0  2010-01-07  0.329350
            4            10.0  2010-01-08  0.390691
            ...             ...         ...       ...
            15095         55.0  2015-12-24  0.061547
            15096         55.0  2015-12-28  0.064403
            15097         55.0  2015-12-29  0.085882
            15098         55.0  2015-12-30  0.079646
            15099         55.0  2015-12-31  0.080636
        """
        ...

    @_validate_args
    @group_operation
    def group_sum(self, group: _AbstractPrismComponent):
        """
        Sum of values over across each date and group.

        Parameters
        ----------
            group : PrismComponent
                Used to determine the groups.

        Returns
        -------
            prismstudio._PrismComponent
                Group sum timeseries of the PrismComponent

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            # look for GICS Sector Security Master attribute to create a group
            >>> ps.securitymaster.list_attribute()
            ['Trading Item ID',
            'VALOR',
            'GVKEY',
            'MarkIt Red Code',
            'Country',
            'GICS Sector',
            'WKN',
            'CINS',
            "Moody's Issuer Number",
            'GICS Group',
            'SEDOL',
            'Company Name',
            'CMA Entity ID',
            'CIQ Primary',
            'NAICS',
            'Factset Security ID',
            'Composite FIGI',
            'Share Class FIGI',
            'FIGI',
            'Compustat Primary',
            'Factset Company ID',
            'Ticker',
            'Factset Entity ID',
            'GVKEYIID',
            'Company ID',
            'Factset Listing ID',
            'LEI',
            'IBES Ticker',
            'CUSIP',
            'GICS Sub-Industry',
            'Barra ID',
            'ISIN',
            'MIC',
            'SIC',
            'Security ID',
            'Trade Currency',
            'GICS Industry',
            'Fitch Issuer ID',
            'RatingsXpress Entity ID',
            'SNL Institution ID']

            >>> gics_sector = ps.securitymaster.attribute('GICS Sector') # Data Component: GICS Sector
            >>> close_result = close.samples_pct_change(21).group_sum(gics_sector) # trading month momentum group ranking on gics sector
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31')
                   GICS sector        date     value
            0            10.0  2010-01-04  3.198166
            1            10.0  2010-01-05  4.607422
            2            10.0  2010-01-06  5.569585
            3            10.0  2010-01-07  5.571885
            4            10.0  2010-01-08  7.061548
            ...             ...         ...       ...
            15095         55.0  2015-12-24  0.429676
            15096         55.0  2015-12-28  0.689446
            15097         55.0  2015-12-29  0.817036
            15098         55.0  2015-12-30  0.628850
            15099         55.0  2015-12-31  0.170396
        """
        ...

    @_validate_args
    @group_operation
    def group_count(self, group: _AbstractPrismComponent):
        """
        Count of values over across each date and group.

        Parameters
        ----------
            group : PrismComponent
                Used to determine the groups.

        Returns
        -------
            prismstudio._PrismComponent
                Group count timeseries of the PrismComponent

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            # look for GICS Sector Security Master attribute to create a group
            >>> ps.securitymaster.list_attribute()
            ['Trading Item ID',
            'VALOR',
            'GVKEY',
            'MarkIt Red Code',
            'Country',
            'GICS Sector',
            'WKN',
            'CINS',
            "Moody's Issuer Number",
            'GICS Group',
            'SEDOL',
            'Company Name',
            'CMA Entity ID',
            'CIQ Primary',
            'NAICS',
            'Factset Security ID',
            'Composite FIGI',
            'Share Class FIGI',
            'FIGI',
            'Compustat Primary',
            'Factset Company ID',
            'Ticker',
            'Factset Entity ID',
            'GVKEYIID',
            'Company ID',
            'Factset Listing ID',
            'LEI',
            'IBES Ticker',
            'CUSIP',
            'GICS Sub-Industry',
            'Barra ID',
            'ISIN',
            'MIC',
            'SIC',
            'Security ID',
            'Trade Currency',
            'GICS Industry',
            'Fitch Issuer ID',
            'RatingsXpress Entity ID',
            'SNL Institution ID']

            >>> gics_sector = ps.securitymaster.attribute('GICS Sector') # Data Component: GICS Sector
            >>> close_result = close.samples_pct_change(21).group_count(gics_sector) # trading month momentum group ranking on gics sector
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31')
                   GICS sector        date  value
            0            10.0  2010-01-04     39
            1            10.0  2010-01-05     39
            2            10.0  2010-01-06     39
            3            10.0  2010-01-07     39
            4            10.0  2010-01-08     39
            ...             ...         ...    ...
            15095         55.0  2015-12-24     29
            15096         55.0  2015-12-28     29
            15097         55.0  2015-12-29     29
            15098         55.0  2015-12-30     29
            15099         55.0  2015-12-31     29
        """
        ...

    @_validate_args
    @group_operation
    def group_median(self, group: _AbstractPrismComponent):
        """
        Median of the values over across each date and group.

        Parameters
        ----------
            group : PrismComponent
                Used to determine the groups.

        Returns
        -------
            prismstudio._PrismComponent
                Group median timeseries of the PrismComponent

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            # look for GICS Sector Security Master attribute to create a group
            >>> ps.securitymaster.list_attribute()
            ['Trading Item ID',
            'VALOR',
            'GVKEY',
            'MarkIt Red Code',
            'Country',
            'GICS Sector',
            'WKN',
            'CINS',
            "Moody's Issuer Number",
            'GICS Group',
            'SEDOL',
            'Company Name',
            'CMA Entity ID',
            'CIQ Primary',
            'NAICS',
            'Factset Security ID',
            'Composite FIGI',
            'Share Class FIGI',
            'FIGI',
            'Compustat Primary',
            'Factset Company ID',
            'Ticker',
            'Factset Entity ID',
            'GVKEYIID',
            'Company ID',
            'Factset Listing ID',
            'LEI',
            'IBES Ticker',
            'CUSIP',
            'GICS Sub-Industry',
            'Barra ID',
            'ISIN',
            'MIC',
            'SIC',
            'Security ID',
            'Trade Currency',
            'GICS Industry',
            'Fitch Issuer ID',
            'RatingsXpress Entity ID',
            'SNL Institution ID']

            >>> gics_sector = ps.securitymaster.attribute('GICS Sector') # data component: GICS Sector
            >>> close_result = close.samples_pct_change(21).group_median(gics_sector) # trading month momentum group ranking on gics sector
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31')
                   GICS sector        date     value
            0            10.0  2010-01-04  0.205486
            1            10.0  2010-01-05  0.257924
            2            10.0  2010-01-06  0.326705
            3            10.0  2010-01-07  0.329350
            4            10.0  2010-01-08  0.390691
            ...             ...         ...       ...
            15095         55.0  2015-12-24  0.061547
            15096         55.0  2015-12-28  0.064403
            15097         55.0  2015-12-29  0.085882
            15098         55.0  2015-12-30  0.079646
            15099         55.0  2015-12-31  0.080636
        """
        ...

    @_validate_args
    @group_operation
    def group_demean(self, group: _AbstractPrismComponent):
        """
        Demeaned of values over across each date and group for each element.

        Parameters
        ----------
            group : PrismComponent
                Used to determine the groups.

        Returns
        -------
            prismstudio._PrismComponent
                Group demean timeseries of the PrismComponent

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            # look for GICS Sector Security Master attribute to create a group
            >>> ps.securitymaster.list_attribute()
            ['Trading Item ID',
            'VALOR',
            'GVKEY',
            'MarkIt Red Code',
            'Country',
            'GICS Sector',
            'WKN',
            'CINS',
            "Moody's Issuer Number",
            'GICS Group',
            'SEDOL',
            'Company Name',
            'CMA Entity ID',
            'CIQ Primary',
            'NAICS',
            'Factset Security ID',
            'Composite FIGI',
            'Share Class FIGI',
            'FIGI',
            'Compustat Primary',
            'Factset Company ID',
            'Ticker',
            'Factset Entity ID',
            'GVKEYIID',
            'Company ID',
            'Factset Listing ID',
            'LEI',
            'IBES Ticker',
            'CUSIP',
            'GICS Sub-Industry',
            'Barra ID',
            'ISIN',
            'MIC',
            'SIC',
            'Security ID',
            'Trade Currency',
            'GICS Industry',
            'Fitch Issuer ID',
            'RatingsXpress Entity ID',
            'SNL Institution ID']

            >>> gics_sector = ps.securitymaster.attribute('GICS Sector') # data component: GICS Sector
            >>> close_result = close.samples_pct_change(21).group_demean(gics_sector) # trading month momentum group ranking on gics sector
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date      value  Ticker
            0         2586086  2010-01-04  -0.000867     AFL
            1         2586086  2010-01-05   0.023705     AFL
            2         2586086  2010-01-06   0.040230     AFL
            3         2586086  2010-01-07   0.018340     AFL
            4         2586086  2010-01-08   0.003084     AFL
            ...           ...         ...        ...     ...
            755337  344286611  2011-10-25  -0.065807     ITT
            755338  344286611  2011-10-26  -0.081308     ITT
            755339  344286611  2011-10-27  -0.121696     ITT
            755340  344286611  2011-10-28  -0.104128     ITT
            755341  344286611  2011-10-31  -0.065463     ITT
        """
        ...

    @_validate_args
    @group_operation
    def group_z_score(self, group: _AbstractPrismComponent):
        """
        Z-score of the values over across each date and group for each element.

        Parameters
        ----------
            group : PrismComponent
                Used to determine the groups.

        Returns
        -------
            prismstudio._PrismComponent
                Group z-score timeseries of the PrismComponent.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            # look for GICS Sector Security Master attribute to create a group
            >>> ps.securitymaster.list_attribute()
            ['Trading Item ID',
            'VALOR',
            'GVKEY',
            'MarkIt Red Code',
            'Country',
            'GICS Sector',
            'WKN',
            'CINS',
            "Moody's Issuer Number",
            'GICS Group',
            'SEDOL',
            'Company Name',
            'CMA Entity ID',
            'CIQ Primary',
            'NAICS',
            'Factset Security ID',
            'Composite FIGI',
            'Share Class FIGI',
            'FIGI',
            'Compustat Primary',
            'Factset Company ID',
            'Ticker',
            'Factset Entity ID',
            'GVKEYIID',
            'Company ID',
            'Factset Listing ID',
            'LEI',
            'IBES Ticker',
            'CUSIP',
            'GICS Sub-Industry',
            'Barra ID',
            'ISIN',
            'MIC',
            'SIC',
            'Security ID',
            'Trade Currency',
            'GICS Industry',
            'Fitch Issuer ID',
            'RatingsXpress Entity ID',
            'SNL Institution ID']

            >>> gics_sector = ps.securitymaster.attribute('GICS Sector') # data component: GICS Sector
            >>> close_result = close.samples_pct_change(21).group_z_score(gics_sector) # trading month momentum group ranking on gics sector
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])\
                    listingid        date      value  Ticker
            0         2586086  2010-01-04  -0.015607     AFL
            1         2586086  2010-01-05   0.421663     AFL
            2         2586086  2010-01-06   0.754689     AFL
            3         2586086  2010-01-07   0.282194     AFL
            4         2586086  2010-01-08   0.051700     AFL
            ...           ...         ...        ...     ...
            755337  344286611  2011-10-25  -0.891504     ITT
            755338  344286611  2011-10-26  -1.087371     ITT
            755339  344286611  2011-10-27  -1.296089     ITT
            755340  344286611  2011-10-28  -1.136280     ITT
            755341  344286611  2011-10-31  -0.707442     ITT
        """
        ...

    @_validate_args
    @group_operation
    def group_rank(
        self,
        group: _AbstractPrismComponent,
        rank_method: const.RankType = "standard",
        ascending: bool = True
    ):
        """
        Ranks of values (1 through n) across each date and group for each element.

        Parameters
        ----------
            group : PrismComponent
                Used to determine the groups.

            rank_method : str {'standard', 'modified', 'dense', 'ordinal', 'fractional'}, default 'standard'
                | Method for how equal values are assigned a rank.

                - standard: 1 2 2 4
                - modified: 1 3 3 4
                - dense: 1 2 2 3
                - ordinal: 1 2 3 4
                - fractional: 1 2.5 2.5 4

            ascending : bool, default True
                Whether or not the elements should be ranked in ascending order.

        Returns
        -------
            prismstudio._PrismComponent
                Group ranking of the PrismComponent.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            # look for GICS Sector Security Master attribute to create a group
            >>> ps.securitymaster.list_attribute()
            ['Trading Item ID',
            'VALOR',
            'GVKEY',
            'MarkIt Red Code',
            'Country',
            'GICS Sector',
            'WKN',
            'CINS',
            "Moody's Issuer Number",
            'GICS Group',
            'SEDOL',
            'Company Name',
            'CMA Entity ID',
            'CIQ Primary',
            'NAICS',
            'Factset Security ID',
            'Composite FIGI',
            'Share Class FIGI',
            'FIGI',
            'Compustat Primary',
            'Factset Company ID',
            'Ticker',
            'Factset Entity ID',
            'GVKEYIID',
            'Company ID',
            'Factset Listing ID',
            'LEI',
            'IBES Ticker',
            'CUSIP',
            'GICS Sub-Industry',
            'Barra ID',
            'ISIN',
            'MIC',
            'SIC',
            'Security ID',
            'Trade Currency',
            'GICS Industry',
            'Fitch Issuer ID',
            'RatingsXpress Entity ID',
            'SNL Institution ID']

            >>> gics_sector = ps.securitymaster.attribute('GICS Sector') # data component: GICS Sector
            >>> close_result = close.samples_pct_change(21).group_rank(gics_sector) # trading month momentum group ranking on gics sector
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  value  Ticker
            0         2586086  2010-01-04   35.0     AFL
            1         2586086  2010-01-05   52.0     AFL
            2         2586086  2010-01-06   61.0     AFL
            3         2586086  2010-01-07   51.0     AFL
            4         2586086  2010-01-08   40.0     AFL
            ...           ...         ...    ...     ...
            755337  344286611  2011-10-25   10.0     ITT
            755338  344286611  2011-10-26    6.0     ITT
            755339  344286611  2011-10-27    6.0     ITT
            755340  344286611  2011-10-28    8.0     ITT
            755341  344286611  2011-10-31   15.0     ITT
        """
        ...

    @_validate_args
    @group_operation
    def group_percentile(
        self,
        group: _AbstractPrismComponent,
        rank_method: const.RankType = "standard",
        ascending: bool = True
    ):
        """
        Percentile of values (between 0 and 1) across each date and group for each element.

        Parameters
        ----------
            group : PrismComponent
                Used to determine the groups.

            rank_method : str {'standard', 'modified', 'dense', 'ordinal', 'fractional'}, default 'standard'
                | Method for how equal values are assigned a rank.

                - standard: 1 2 2 4
                - modified: 1 3 3 4
                - dense: 1 2 2 3
                - ordinal: 1 2 3 4
                - fractional: 1 2.5 2.5 4

            ascending : bool, default True
                Whether or not the elements should be ranked in ascending order.

        Returns
        -------
            prismstudio._PrismComponent
                Group percentile timeseries of the PrismComponent.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            # look for GICS Sector Security Master attribute to create a group
            >>> ps.securitymaster.list_attribute()
            ['Trading Item ID',
            'VALOR',
            'GVKEY',
            'MarkIt Red Code',
            'Country',
            'GICS Sector',
            'WKN',
            'CINS',
            "Moody's Issuer Number",
            'GICS Group',
            'SEDOL',
            'Company Name',
            'CMA Entity ID',
            'CIQ Primary',
            'NAICS',
            'Factset Security ID',
            'Composite FIGI',
            'Share Class FIGI',
            'FIGI',
            'Compustat Primary',
            'Factset Company ID',
            'Ticker',
            'Factset Entity ID',
            'GVKEYIID',
            'Company ID',
            'Factset Listing ID',
            'LEI',
            'IBES Ticker',
            'CUSIP',
            'GICS Sub-Industry',
            'Barra ID',
            'ISIN',
            'MIC',
            'SIC',
            'Security ID',
            'Trade Currency',
            'GICS Industry',
            'Fitch Issuer ID',
            'RatingsXpress Entity ID',
            'SNL Institution ID']

            >>> gics_sector = ps.securitymaster.attribute('GICS Sector') # data component: GICS Sector
            >>> close_result = close.samples_pct_change(21).group_percentile(gics_sector) # trading month momentum group ranking on gics sector
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  value  Ticker
            0         2586086  2010-01-04    3.0     AFL
            1         2586086  2010-01-05    4.0     AFL
            2         2586086  2010-01-06    4.0     AFL
            3         2586086  2010-01-07    4.0     AFL
            4         2586086  2010-01-08    3.0     AFL
            ...           ...         ...    ...     ...
            755337  344286611  2011-10-25    5.0     ITT
            755338  344286611  2011-10-26    5.0     ITT
            755339  344286611  2011-10-27    5.0     ITT
            755340  344286611  2011-10-28    5.0     ITT
            755341  344286611  2011-10-31    2.0     ITT
        """
        ...

    @_validate_args
    @group_operation
    def group_quantile(
        self,
        group: _AbstractPrismComponent,
        bins: int,
        rank_method: const.RankType = "standard",
        ascending: bool = True,
        right: bool = True,
    ):
        """
        Quantile of values across each date and group for each element.

        Parameters
        ----------
            group : PrismComponent
                Used to determine the groups.

            bins : int
                Number of quantiles. 10 for deciles, 4 for quartiles, etc.

            rank_method : str {'standard', 'modified', 'dense', 'ordinal', 'fractional'}, default 'standard'
                | Method for how equal values are assigned a rank.

                - standard: 1 2 2 4
                - modified: 1 3 3 4
                - dense: 1 2 2 3
                - ordinal: 1 2 3 4
                - fractional: 1 2.5 2.5 4

            ascending : bool, default True
                Whether or not the elements should be ranked in ascending order.

            right: bool, default True
                | If True, given a border value in between bins, whether to put the sample in the which bins.
                | For example, if the value borders for bin 1 is between 0 ~ 5 and bin 2 is between 5 ~ 10, if right is True, and a sample has a value 5, then it will be assigned bin 1. if False, then bin 2.

        Returns
        -------
            prismstudio._PrismComponent
                Group percentile timeseries of the PrismComponent.

        Examples
        --------
            >>> close = ps.market.close()
            >>> close.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date  Close  Ticker
            0         2586086  2010-01-04  47.57     AFL
            1         2586086  2010-01-05  48.95     AFL
            2         2586086  2010-01-06  49.38     AFL
            3         2586086  2010-01-07  49.91     AFL
            4         2586086  2010-01-08  49.41     AFL
            ...           ...         ...    ...     ...
            755971  344286611  2011-10-25  44.02     ITT
            755972  344286611  2011-10-26  43.54     ITT
            755973  344286611  2011-10-27  44.31     ITT
            755974  344286611  2011-10-28  44.99     ITT
            755975  344286611  2011-10-31  45.60     ITT

            # look for GICS Sector Security Master attribute to create a group
            >>> ps.securitymaster.list_attribute()
            ['Trading Item ID',
            'VALOR',
            'GVKEY',
            'MarkIt Red Code',
            'Country',
            'GICS Sector',
            'WKN',
            'CINS',
            "Moody's Issuer Number",
            'GICS Group',
            'SEDOL',
            'Company Name',
            'CMA Entity ID',
            'CIQ Primary',
            'NAICS',
            'Factset Security ID',
            'Composite FIGI',
            'Share Class FIGI',
            'FIGI',
            'Compustat Primary',
            'Factset Company ID',
            'Ticker',
            'Factset Entity ID',
            'GVKEYIID',
            'Company ID',
            'Factset Listing ID',
            'LEI',
            'IBES Ticker',
            'CUSIP',
            'GICS Sub-Industry',
            'Barra ID',
            'ISIN',
            'MIC',
            'SIC',
            'Security ID',
            'Trade Currency',
            'GICS Industry',
            'Fitch Issuer ID',
            'RatingsXpress Entity ID',
            'SNL Institution ID']

            >>> gics_sector = ps.securitymaster.attribute('GICS Sector') # data component: GICS Sector
            >>> close_result = close.samples_pct_change(21).group_quantile(gics_sector, 5) # trading month momentum group ranking on gics sector
            >>> close_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                    listingid        date     value  Ticker
            0         2586086  2010-01-04  0.448718     AFL
            1         2586086  2010-01-05  0.666667     AFL
            2         2586086  2010-01-06  0.782051     AFL
            3         2586086  2010-01-07  0.653846     AFL
            4         2586086  2010-01-08  0.512821     AFL
            ...           ...         ...       ...     ...
            755337  344286611  2011-10-25  0.166667     ITT
            755338  344286611  2011-10-26  0.100000     ITT
            755339  344286611  2011-10-27  0.100000     ITT
            755340  344286611  2011-10-28  0.133333     ITT
            755341  344286611  2011-10-31  0.250000     ITT
        """
        ...

    @_validate_args
    @group_operation
    def group_mode(self, group: _AbstractPrismComponent):
        """
        Mode of the values over across each date and group.

        Parameters
        ----------
            group : PrismComponent
                Used to determine the groups.

        Returns
        -------
            prismstudio._PrismComponent
                Group mode timeseries of the PrismComponent.

        Examples
        --------
        TODO
        """
        ...

    @_validate_args
    @group_operation
    def group_skew(self, group: _AbstractPrismComponent):
        """
        Skewness values over across each date and group.

        Parameters
        ----------
            group : PrismComponent
                Used to determine the groups.

        Returns
        -------
            prismstudio._PrismComponent
                Group skewness timeseries of the PrismComponent.

        Examples
        --------
        TODO
        """
        ...

    @_validate_args
    @group_operation
    def group_kurt(self, group: _AbstractPrismComponent):
        """
        Kurtosis values over across each date and group.

        Parameters
        ----------
            group : PrismComponent
                Used to determine the groups.

        Returns
        -------
            prismstudio._PrismComponent
                Group kurtosis timeseries of the PrismComponent.

        Examples
        --------
        TODO
        """
        ...

    @_validate_args
    @group_operation
    def group_prod(self, group: _AbstractPrismComponent):
        """
        Product values over across each date and group.

        Parameters
        ----------
            group : PrismComponent
                Used to determine the groups.

        Returns
        -------
            prismstudio._PrismComponent
                Group product timeseries of the PrismComponent.

        Examples
        --------
        TODO
        """
        ...

    # map operation
    @_validate_args
    def map(self, args: dict):
        """
        Map values of Component according to an input mapping or function.
        Used for substituting each value in a Component with another value, that may be derived from a function, a ``dict`` .

        Parameters
        ----------
            args : dict

        Returns
        -------
            prismstudio._PrismComponent
                Resampled timeseries of the PrismComponent.

        Examples
        --------
            Winsorization Example

            >>> # Create Earnings to Price Z score
            >>> ni = ps.financial.income_statement(dataitemid=100639, periodtype='LTM')
            >>> mcap = ps.market.market_cap()
            >>> ep = ni.resample('D') / mcap
            >>> ep_z = ep.cross_sectional_z_score()
            >>> ep_z.get_data(1, startdate='2010-01-01')
                    listingid       date     marketcap
            0         38593288  2010-01-01  -340.182838
            1         20221860  2010-01-01   -40.071622
            2         20168002  2010-01-01    -3.852210
            3         31780211  2010-01-01    -0.998875
            4         31778710  2010-01-01    -0.967982
            ...            ...         ...          ...
            8047487   20219090  2022-11-01     0.657311
            8047488  243257057  2022-11-01     1.000056
            8047489   20215516  2022-11-01     1.609253
            8047490   20459086  2022-11-01    57.791387

            >>> # Apply Winsorization
            >>> ep_z_wind = (ep_z < -3).map({True: -3, False: ep_z})
            >>> ep_z_wind.get_data(1, startdate='2010-01-01')
                    listingid       date   marketcap
            0         38593288  2010-01-01  -3.000000
            1         20221860  2010-01-01  -3.000000
            2         20168002  2010-01-01  -3.000000
            3         38593288  2010-01-02  -3.000000
            4         20221860  2010-01-02  -3.000000
            ...            ...         ...        ...
            8047487   20219090  2022-11-01   0.657311
            8047488  243257057  2022-11-01   1.000056
            8047489   20215516  2022-11-01   1.609253
            8047490   20459086  2022-11-01  57.791387
        """
        component_args = {}
        children = [self]
        for k, v in args.items():
            if isinstance(v, _PrismComponent):
                child = v
            else:
                child = _PrismValue(data=const.SPECIALVALUEMAP.get(v, v))
            component_args[k] = child
            children.append(child)
        return _functioncomponent_builder("map", component_args, *children)


class _PrismDataComponent(_AbstractPrismComponent):
    """
    Abstract class for base nodes.
    Enforces _component_name as default class attribute.
    Args:
        kwargs: dict of component_args
    """
    component_type = const.PrismComponentType.DATA_COMPONENT

    def __init__(self, **kwargs):
        component_args = dict(kwargs)
        super().__init__(component_args=dict(kwargs))
        val_res = requests.post(url=URL_DATAQUERIES + "/validate", json=self._query, headers=_authentication())
        if val_res.status_code >= 400:
            if val_res.status_code == 401:
                raise PrismAuthError(f"Please Login First")
            else:
                try:
                    err_msg = val_res.json()["message"]
                except:
                    err_msg = f"{val_res.content}: Data Component {self._component_category}/{self._component_name}"
                    if "dataitemid" in component_args:
                        err_msg = f"{err_msg} with dataitemid {component_args['dataitemid']}"
                    if component_args.get("package") is not None:
                        err_msg = f"{err_msg} from {component_args['package']} package"
                raise PrismResponseError(err_msg)
        query = val_res.json()["rescontent"]["data"]
        metadata = val_res.json()["rescontent"]["metadata"]
        if metadata.get("info") is not None:
            warnings.warn(metadata.get("info"))
        super().__init__(**query)


class _PrismTaskComponent(_AbstractPrismComponent, ABC):
    component_type = const.PrismComponentType.TASK_COMPONENT

    def __init__(self, **kwargs):
        super().__init__(component_args=dict(kwargs))

    def run(self, *args, **kwargs):
        raise NotImplementedError()

    @_validate_args
    def save(self, name: str) -> None:
        return _taskquery.save_taskquery(self, name)

    @_validate_args
    def extract(self, return_code=False):
        return _taskquery.extract_taskquery(self, return_code)

    @classmethod
    def _list_job(cls):
        return _get(f"{URL_JOBS}/type/{cls.componentid}")


class _PrismValue(_AbstractPrismComponent):
    component_type = const.PrismComponentType.DATA_COMPONENT
    _categoryid = 40000
    _componentid = 40000
    _component_name = "Constant"
    _component_category = "Constant"

    def __init__(self, **kwargs):
        super().__init__(component_args=dict(kwargs))


class _PrismModelComponent(_PrismComponent):
    component_type = const.PrismComponentType.MODEL_COMPONENT

    def __init__(self, **kwargs):
        component_args = dict(kwargs)
        children = [] if "children" not in component_args else component_args.pop("children")
        query = {"component_args": component_args, "children": children,}
        super().__init__(**query)
        val_res = requests.post(url=URL_DATAQUERIES + "/validate", json=self._query, headers=_authentication())
        if val_res.status_code >= 400:
            if val_res.status_code == 401:
                raise PrismAuthError(f"Please Login First")
            else:
                try:
                    err_msg = val_res.json()["message"]
                except:
                    err_msg = val_res.content
                raise PrismResponseError(err_msg)
        query = val_res.json()["rescontent"]["data"]
        metadata = val_res.json()["rescontent"]["metadata"]
        if metadata.get("info") is not None:
            warnings.warn(metadata.get("info"))
        super().__init__(**query)
