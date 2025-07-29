import numbers

from prismstudio._utils.exceptions import PrismTypeError

from .._common.const import SPECIALVALUEMAP
from .._prismcomponent.prismcomponent import _PrismComponent, _PrismValue, _functioncomponent_builder
from .._utils import _validate_args


__all__ = ["min", "max", "mean", "std", "sum", "var"]


def _fn_builder(component_name, component_args, *cmpts):
    cmpts_ = []
    for c in cmpts:
        if isinstance(c, _PrismComponent):
            cmpts_.append(c)
        elif isinstance(c, numbers.Real):
            other = SPECIALVALUEMAP.get(other, other)
            cmpts_.append(_PrismValue(data=c))
        else:
            raise PrismTypeError(f"Incompatible type for {component_name}: {type(c)}")

    return _functioncomponent_builder(component_name, component_args, *cmpts_)


@_validate_args
def min(cmpts: list):
    """
    Element-wise minimum of PrismComponents. Compare multiple PrismComponents element-wise and returns a new PrismComponent containing the element-wise minima. If one of the elements being compared is a ``NaN``, then that element is returned. If both elements are ``NaN`` s then the first is returned.

    Parameters
    ----------
        components : list of PrismComponents

    Returns
    -------
        prismstudio._PrismComponent
            The minimum of inputed PrismComponents, element-wise.

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

        >>> open_= ps.market.open()
        >>> open_.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                listingid        date   Open  Ticker
        0         2586086  2010-01-04  46.50     AFL
        1         2586086  2010-01-05  47.49     AFL
        2         2586086  2010-01-06  49.83     AFL
        3         2586086  2010-01-07  49.41     AFL
        4         2586086  2010-01-08  49.66     AFL
        ...           ...         ...    ...     ...
        755955  344286611  2011-10-25  44.35     ITT
        755956  344286611  2011-10-26  44.55     ITT
        755957  344286611  2011-10-27  44.95     ITT
        755958  344286611  2011-10-28  44.52     ITT
        755959  344286611  2011-10-31  44.65     ITT

        >>> result = ps.min([close, open_])
        >>> result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                listingid        date  value  Ticker
        0         2586086  2010-01-04  46.50     AFL
        1         2586086  2010-01-05  47.49     AFL
        2         2586086  2010-01-06  49.38     AFL
        3         2586086  2010-01-07  49.41     AFL
        4         2586086  2010-01-08  49.41     AFL
        ...           ...         ...    ...     ...
        755955  344286611  2011-10-25  44.02     ITT
        755956  344286611  2011-10-26  43.54     ITT
        755957  344286611  2011-10-27  44.31     ITT
        755958  344286611  2011-10-28  44.52     ITT
        755959  344286611  2011-10-31  44.65     ITT

        >>> high= ps.market.high()
        >>> result = ps.min([close, open_, high])
        >>> result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                listingid        date  value  Ticker
        0         2586086  2010-01-04  46.50     AFL
        1         2586086  2010-01-05  47.49     AFL
        2         2586086  2010-01-06  49.38     AFL
        3         2586086  2010-01-07  49.41     AFL
        4         2586086  2010-01-08  49.41     AFL
        ...           ...         ...    ...     ...
        755954  344286611  2011-10-25  44.02     ITT
        755955  344286611  2011-10-26  43.54     ITT
        755956  344286611  2011-10-27  44.31     ITT
        755957  344286611  2011-10-28  44.52     ITT
        755958  344286611  2011-10-31  44.65     ITT


    """
    return _fn_builder("min", {}, *cmpts)


@_validate_args
def max(cmpts: list):
    """
    Element-wise maximum of PrismComponents.
    Compare multiple PrismComponents element-wise and returns a new PrismComponent containing the element-wise maxima.
    If one of the elements being compared is a ``NaN``, then that element is returned. If both elements are ``NaN`` s then the first is returned.

    Parameters
    ----------
        components : list of PrismComponents

    Returns
    -------
        prismstudio._PrismComponent
            The maximum of inputed PrismComponents, element-wise.

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

        >>> open_= ps.market.open()
        >>> open_.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                listingid        date   Open  Ticker
        0         2586086  2010-01-04  46.50     AFL
        1         2586086  2010-01-05  47.49     AFL
        2         2586086  2010-01-06  49.83     AFL
        3         2586086  2010-01-07  49.41     AFL
        4         2586086  2010-01-08  49.66     AFL
        ...           ...         ...    ...     ...
        755955  344286611  2011-10-25  44.35     ITT
        755956  344286611   2011-10-26  44.55    ITT
        755957  344286611  2011-10-27  44.95     ITT
        755958  344286611  2011-10-28  44.52     ITT
        755959  344286611  2011-10-31  44.65     ITT

        >>> max_result = ps.max([close, open_])
        >>> max_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                listingid        date  value  Ticker
        0         2586086  2010-01-04  47.57     AFL
        1         2586086  2010-01-05  48.95     AFL
        2         2586086  2010-01-06  49.83     AFL
        3         2586086  2010-01-07  49.91     AFL
        4         2586086  2010-01-08  49.66     AFL
        ...           ...         ...    ...     ...
        755955  344286611  2011-10-25  44.35     ITT
        755956  344286611  2011-10-26  44.55     ITT
        755957  344286611  2011-10-27  44.95     ITT
        755958  344286611  2011-10-28  44.99     ITT
        755959  344286611  2011-10-31  45.60     ITT

        >>> high= ps.market.high()
        >>> max_result = ps.max([close, open_, high])
        >>> max_result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                listingid        date  value  Ticker
        0         2586086  2010-01-04  47.70     AFL
        1         2586086  2010-01-05  49.08     AFL
        2         2586086  2010-01-06  49.83     AFL
        3         2586086  2010-01-07  50.00     AFL
        4         2586086  2010-01-08  49.66     AFL
        ...           ...         ...    ...     ...
        755954  344286611  2011-10-25  44.87     ITT
        755955  344286611  2011-10-26  44.72     ITT
        755956  344286611  2011-10-27  44.98     ITT
        755957  344286611  2011-10-28  45.08     ITT
        755958  344286611  2011-10-31  47.49     ITT

    """
    return _fn_builder("max", {}, *cmpts)


@_validate_args
def mean(cmpts: list):
    """
    Element-wise mean of PrismComponents. Returns a new PrismComponent containing the element-wise mean. If one of the elements being compared is a ``NaN``, then that element is removed from the calculation. If all elements are ``NaN`` s then the ``NaN`` is returned.

    Parameters
    ----------
        components : list of PrismComponents

    Returns
    -------
        prismstudio._PrismComponent
            The mean of inputed PrismComponents, element-wise.

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

        >>> open_= ps.market.open()
        >>> open_.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                listingid        date   Open  Ticker
        0         2586086  2010-01-04  46.50     AFL
        1         2586086  2010-01-05  47.49     AFL
        2         2586086  2010-01-06  49.83     AFL
        3         2586086  2010-01-07  49.41     AFL
        4         2586086  2010-01-08  49.66     AFL
        ...           ...         ...    ...     ...
        755955  344286611  2011-10-25  44.35     ITT
        755956  344286611  2011-10-26  44.55     ITT
        755957  344286611  2011-10-27  44.95     ITT
        755958  344286611  2011-10-28  44.52     ITT
        755959  344286611  2011-10-31  44.65     ITT

        >>> result = ps.mean([close, open_])
        >>> result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                listingid        date   value  Ticker
        0         2586086  2010-01-04  47.035     AFL
        1         2586086  2010-01-05  48.220     AFL
        2         2586086  2010-01-06  49.605     AFL
        3         2586086  2010-01-07  49.660     AFL
        4         2586086  2010-01-08  49.535     AFL
        ...           ...         ...     ...     ...
        755955  344286611  2011-10-25  44.185     ITT
        755956  344286611  2011-10-26  44.045     ITT
        755957  344286611  2011-10-27  44.630     ITT
        755958  344286611  2011-10-28  44.755     ITT
        755959  344286611  2011-10-31  45.125     ITT

    """
    return _fn_builder("mean", {}, *cmpts)


@_validate_args
def std(cmpts: list):
    """
    Element-wise standard deviation of PrismComponents. Returns a new PrismComponent containing the element-wise standard deviation. If one of the elements being compared is a ``NaN``, then that element is removed from the calculation. If all elements are ``NaN`` s then the ``NaN`` is returned.

    Parameters
    ----------
        components : list of PrismComponents

    Returns
    -------
        prismstudio._PrismComponent
            The standard deviation of inputed PrismComponents, element-wise.

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

        >>> open_= ps.market.open()
        >>> open_.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                listingid        date   Open  Ticker
        0         2586086  2010-01-04  46.50     AFL
        1         2586086  2010-01-05  47.49     AFL
        2         2586086  2010-01-06  49.83     AFL
        3         2586086  2010-01-07  49.41     AFL
        4         2586086  2010-01-08  49.66     AFL
        ...           ...         ...    ...     ...
        755955  344286611  2011-10-25  44.35     ITT
        755956  344286611  2011-10-26  44.55     ITT
        755957  344286611  2011-10-27  44.95     ITT
        755958  344286611  2011-10-28  44.52     ITT
        755959  344286611  2011-10-31  44.65     ITT

        >>> result = ps.std([close, open_])
        >>> result.get_data(universe='S&P 500', startdate='2010-01-01', enddate='2015-12-31', shownid=['ticker'])
                listingid        date  value  Ticker
        0         2586086  2010-01-04  0.535     AFL
        1         2586086  2010-01-05  0.730     AFL
        2         2586086  2010-01-06  0.225     AFL
        3         2586086  2010-01-07  0.250     AFL
        4         2586086  2010-01-08  0.125     AFL
        ...           ...         ...    ...     ...
        755955  344286611  2011-10-25  0.165     ITT
        755956  344286611  2011-10-26  0.505     ITT
        755957  344286611  2011-10-27  0.320     ITT
        755958  344286611  2011-10-28  0.235     ITT
        755959  344286611  2011-10-31  0.475     ITT
    """
    return _fn_builder("std", {}, *cmpts)


@_validate_args
def sum(cmpts: list):
    """
    Element-wise sum of PrismComponents. Returns a new PrismComponent containing the element-wise sum. If one of the elements being compared is a ``NaN``, then that element is removed from the calculation. If all elements are ``NaN`` s then the ``NaN`` is returned.

    Parameters
    ----------
        components : list of PrismComponents

    Returns
    -------
        prismstudio._PrismComponent
            The sum of inputed PrismComponents, element-wise.
    """
    return _fn_builder("sum", {}, *cmpts)


@_validate_args
def var(cmpts: list):
    """
    Element-wise variance of PrismComponents. Returns a new PrismComponent containing the element-wise variance. If one of the elements being compared is a ``NaN``, then that element is removed from the calculation. If all elements are ``NaN`` s then the ``NaN`` is returned.

    Parameters
    ----------
        components : list of PrismComponents

    Returns
    -------
        prismstudio._PrismComponent
            The variance of inputed PrismComponents, element-wise.
    """
    return _fn_builder("var", {}, *cmpts)
