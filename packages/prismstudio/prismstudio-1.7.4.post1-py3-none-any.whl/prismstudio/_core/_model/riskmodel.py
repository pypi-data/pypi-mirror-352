import copy
import uuid

from ..._common.const import FrequencyType, WeekEndType
from ..._prismcomponent.prismcomponent import _PrismModelComponent, _PrismComponent, _functioncomponent_builder
from ..._utils import _validate_args


_data_category = __name__.split(".")[-1]


class _PrismRiskModelComponent(_PrismModelComponent):
    _component_category_repr  = _data_category

    # def inv(self):
    #     return _functioncomponent_builder("inv", {}, self)

    def __getattribute__(self, name):
        if name not in [
            "get_data",
            "inv",
            "save",
            "copy",
            "query",
            "component_type",
            "categoryid",
            "component_category",
            "componentid",
            "component_name",
            "_query",
            "_dict_to_tree",
            "__class__",
        ]: raise AttributeError(f"{name} not allowed")
        return _PrismModelComponent.__getattribute__(self, name)


class qis(_PrismRiskModelComponent):
    r"""
    | Provides fast and accurate estimators of the covariance matrix based on nonlinear shrinkage for financial assets.
    | Nonlinear shrinkage derived under Frobenius loss and its two cousins, Inverse Stein's loss and Minimum Variance loss, called quadratic-inverse shrinkage (QIS).

    Parameters
    ----------

        frequency : str
            | Desired rebalancing frequency for the risk model
            | Examples:
            |     'M': Generates risk models at the end of every month.
            |     'M-23': Generates risk models on the 23rd day of each month.
            |     'W-M': Generates risk models every Monday of a week.

        data_interval : str
            | Desired period of data used to calculate a risk model.
            | Please note that the parameter value indicates the time frame covered and not the count of individual data samples.
            | For example, if you input '365D' into the parameter, the risk model will be computed using all available data spanning a 365-day period.
            .. admonition:: Note
            :class: note
            | Consider data intervals like **`12M`** (12 months) or **`365D`** (365 days), which both represent approximately a one-year span. The critical distinction lies in the processing of data within these intervals.
            | For instance, in a risk model, a **`12M`** data interval would entail resampling the data to a monthly frequency (M) before analyzing it over the course of a year. This typically results in about 12 data points, giving the risk model a monthly resolution. Conversely, a **`365D`** interval involves working with daily frequency data, leading to a daily resolution in the risk model.

        include : bool, default False
            | Determines whether to include pricing data from the rebalancing dates when calculating the risk model. By default, this parameter is set to False

        weekend : str, {'Sat-Sun', 'Fri-Sat', 'Thu-Fri', 'Fri'}, default 'Sat-Sun'
            | Specifies the weekend days used in the model. This parameter is only relevant when the frequency is set to a business frequency (e.g., 'BM').
            |     - 'Sat-Sun': Standard weekend of Saturday and Sunday
            |     - 'Fri-Sat': Weekend of Friday and Saturday
            |     - 'Thu-Fri': Weekend of Thursday and Friday
            |     - 'Fri': Single day weekend on Friday

        holiday_country : str, {None, ISO 3166 alpha-2 country code}, default None
            | Determines the country-specific holidays to be applied in the model. This parameter is only relevant when the frequency is set to a business frequency (e.g., 'BM').
            |     - None: No holidays are applied
            |     - ISO 3166 alpha-2 country code: Apply holidays based on the specified country's exchange calendar (e.g., 'US' for the United States, 'GB' for Great Britain)

    Returns
    -------
        prismstudio._PrismComponent

    References
    ----------
        Ledoit, O. and Wolf, M. (2022). Quadratic shrinkage for large covariance matrices. Bernoulli.
        Available online at https://www.econ.uzh.ch/en/people/faculty/wolf/publications.html.

    Examples
    --------
        >>> qis = ps.riskmodel.qis("M", "365D", False)
        >>> qis_result = qis.get_data("big_tech", "2020-01-01", "2024-07-08")
        >>> qis_result
        {
        [68 rows x 68 columns],
        '2020-01-31':
                   2587303   2588568   2590360  ...  32517716  46391739  44778083
        2587303   0.000574  0.000092  0.000120  ...  0.000102  0.000131  0.000099
        2588568   0.000092  0.000519  0.000030  ...  0.000039  0.000081  0.000077
        2590360   0.000120  0.000030  0.000505  ...  0.000068  0.000087  0.000073
        2613214   0.000076  0.000007  0.000061  ...  0.000062  0.000055  0.000071
        2621295   0.000127  0.000063  0.000085  ...  0.000070  0.000098  0.000081
        ...            ...       ...       ...  ...       ...       ...       ...
        32517350  0.000118  0.000063  0.000093  ...  0.000057  0.000135  0.000077
        32517592  0.000100  0.000051  0.000052  ...  0.000075  0.000124  0.000079
        32517716  0.000102  0.000039  0.000068  ...  0.000487  0.000139  0.000103
        46391739  0.000131  0.000081  0.000087  ...  0.000139  0.000638  0.000129
        44778083  0.000099  0.000077  0.000073  ...  0.000103  0.000129  0.000461

        [75 rows x 75 columns],
        '2024-06-30':
                     670616003    20237801  ...      20212709  1684108147
        670616003     0.000537    0.000041  ... -2.432627e-06    0.000108
        20237801      0.000041    0.000463  ... -8.907780e-06    0.000111
        32517316      0.000045    0.000045  ... -5.238237e-07    0.000099
        32517350      0.000101    0.000046  ...  5.972674e-05    0.000102
        32517592      0.000065    0.000047  ...  9.782844e-06    0.000131
        ...                ...         ...  ...           ...         ...
        20222173      0.000005    0.000113  ... -1.726302e-05    0.000051
        31781269      0.000003    0.000062  ...  4.193094e-05    0.000009
        407030968    -0.000021    0.000024  ...  2.748597e-06    0.000035
        20212709     -0.000002   -0.000009  ...  4.914296e-04   -0.000009
        1684108147    0.000108    0.000111  ... -8.776752e-06    0.000830
        }

        >>> qis_result['2020-01-31'].dropped
        {'No data found': [],
         'Insufficient sample count': [538619222,
         664143006,
         670616003,
         698666600,
         1683465366,
         1684108147,
         1761029585],
         'No co-occurence': []}

    """

    @_validate_args
    def __init__(
        self,
        frequency: str,
        data_interval: str,
        include: bool = False,
        weekend: WeekEndType = "Sat-Sun",
        holiday_country: str = None,
    ):
        super().__init__(
            frequency=frequency,
            data_interval=data_interval,
            include=include,
            weekend=weekend,
            holiday_country=holiday_country
        )


def map_attribute(self, attribute):
    attributes = self.attributes[attribute]
    ret = self.copy()
    ret.column = attributes
    ret.index = attributes
    return ret
