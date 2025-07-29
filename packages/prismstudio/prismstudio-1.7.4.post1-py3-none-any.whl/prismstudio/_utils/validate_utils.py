from enum import Enum
import inspect
import logging
import re
import sys
from functools import wraps
from typing import Any, Callable, Union

import pandas as pd

from prismstudio._utils.exceptions import PrismTypeError, PrismValueError, PrismAuthError
from .._common import const


logger = logging.getLogger()


def handle_jupyter_exception(func):
    @wraps(func)
    def showtraceback(*args, **kwargs):
        # extract exception type, value and traceback
        etype, evalue, tb = sys.exc_info()
        customType = "Prism" in etype.__name__
        if customType:
            logger.critical(evalue)
            return
        else:
            # otherwise run the original hook
            value = func(*args, **kwargs)
            return value
    return showtraceback


def handle_sys_exception(exc_type, exc_value, exc_traceback):
    customType = "Prism" in exc_type.__name__
    if customType:
        logger.critical(exc_value)
        return
    else:
        # otherwise run the original hook
        return sys.__excepthook__(exc_type, exc_value, exc_traceback)


def _validate_args(function):
    signature = inspect.signature(function)

    @wraps(function)
    def type_checker(*args, **kwargs):
        try:
            bound_args = signature.bind(*args, **kwargs)
            bound_args.apply_defaults()
            bound_args_dict = dict(bound_args.arguments)

            for param_name, param_info in signature.parameters.items():
                if param_name == "self": continue

                arg = bound_args_dict[param_name]
                if arg is None: continue

                param_type = param_info.annotation

                check_argument_type(arg, param_type, param_name)
                arg = apply_validation_rules(arg, param_name, function.__name__, bound_args_dict.get("self", None).__class__.__name__)

                bound_args_dict[param_name] = arg
            function_specific_validation(bound_args_dict, function.__name__, bound_args_dict.get("self", None).__class__.__name__)

            return function(**bound_args_dict)
        except TypeError as e:
            raise PrismTypeError(f"{e}")
    return type_checker


def function_specific_validation(args_dict, function_name, class_name=None):
    if function_name == "fillna":
        v, m = args_dict.get("value"), args_dict.get("method")
        if not (v is not None) ^ (m is not None):
            raise PrismValueError("Must specify one fill 'value' or 'method'")
    elif function_name == "clip":
        l, u = args_dict.get("lowerbound"), args_dict.get("upperbound")
        if (l is None) and (u is None):
            raise PrismValueError("Must specify at leat one of 'lowerbound' or 'upperbound'")
    elif function_name == "log_n" and args_dict["n"] <= 0:
        raise Exception("Base must be positive")
    elif class_name == "beta":
        if (function_name == "__init__"):
            if args_dict["min_sample"] < 2: raise PrismValueError("min_sample cannot be less than 2")
            interval = int(re.findall(r"\d+", args_dict["data_interval"])[0])
            if interval < args_dict["min_sample"]:
                raise PrismValueError("min_sample should be smaller than the number of samples used in calcualtion inferred from data_interval")
    # elif class_name in ["screen", "factor_backtest"]:
    #     if function_name in ["__init__", "run"]:
    #         frequency_validator(args_dict["frequency"], class_name)


def check_argument_type(arg, param_type, param_name):
    if param_type is inspect.Parameter.empty:
        return

    if isinstance(param_type, type):
        if issubclass(param_type, Enum):
            try:
                arg = param_type(arg)
            except Exception as e:
                raise PrismValueError(f"{e}", valid_list=param_type) from e
        elif isinstance(arg, str) and len(arg) >= 200:
            raise PrismValueError(f"Parameter '{param_name}' length exceeds the 200-character limit.")
        elif not isinstance(arg, param_type):
            raise PrismTypeError(
                f"Type of {param_name} is {type(arg)} and not {param_type}")
    elif not any(isinstance(arg, t) for t in param_type.__args__):
        raise PrismTypeError(
            f"Type of {param_name} is {type(arg)} and not in the Union of {param_type.__args__}")


def apply_validation_rules(arg, param_name: str, function_name: str, class_name: str = None):
    # if param_name equals function name
    if param_name in validation_functions:
        validation_function = validation_functions[param_name]
        return validation_function(arg, function_name, class_name)

    # if param_name matches custom pattern
    for _, (pattern_checker, validation_function) in custom_validation_functions.items():
        if pattern_checker(param_name):
            return validation_function(arg)

    # when there is no validation rule to check
    return arg


def startdate_param_validator(arg, *args, **kwargs):
    try:
        date = pd.to_datetime(arg)
    except Exception as e:
        raise PrismValueError(
            f'Unknown string format. Cannot parse "{arg}" to a date') from e

    assert (date >= const.BEGINNING_DATE) & (
        date <= const.ACTIVE_DATE), "Not a valid date."
    return arg


def enddate_param_validator(arg, *args, **kwargs):
    return startdate_param_validator(arg)


def setting_param_validator(arg, *args, **kwargs):
    if const.PreferenceType is None:
        raise PrismAuthError("Please Login First")
    if (arg not in const.PreferenceType) and (arg != ""):
        raise PrismValueError(
            "Invalid preference keyword is given. ", valid_list=const.PreferenceType)
    return arg


def settings_param_validator(arg, *args, **kwargs):
    if const.PreferenceType is None:
        raise PrismAuthError("Please Login First")
    for k in arg.keys():
        if k not in const.PreferenceType:
            raise PrismValueError(
                "Invalid preference key is given. ", valid_list=const.PreferenceType)
    return arg


def frequency_validator(frequency: str, function_name: str, class_name: str):
    if (function_name == "resample") or (class_name in ["screen", "factor_backtest"]): business_pattern = "b?"
    else: business_pattern = ""
    days_str = "|".join(const.DaysRepr)
    day_pattern = fr"([1-9][0-9]{{0,3}})?{business_pattern}d"
    week_pattern = fr"([1-9][0-9]{{0,2}})?{business_pattern}w(-(0[1-7]|[1-7]|{days_str}))?"
    month_pattern = fr"([1-9][0-9]{{0,1}})?{business_pattern}(m|q|sa)(-(0[1-9]|[12]\d|3[01]|[1-9]))?"
    yearly_pattern = fr"[1-9]?{business_pattern}a(-(0?[1-9]|[1][0-2])\/(0[1-9]|[12]\d|3[01]|[1-9]))?"

    frequency_pattern = fr"({day_pattern})|({week_pattern})|({month_pattern})|{yearly_pattern}"
    if re.fullmatch(frequency_pattern, frequency.lower()) is None:
        raise PrismValueError("Not a valid frequency format - Please refer to the User Guide")
    return frequency


def data_interval_validator(period: str, *args, **kwargs):
    period_pattern = r"([1-9][0-9]{0,3})?(D|W|M|Q|SA|Y)"

    if re.fullmatch(period_pattern, period) is None:
        raise PrismValueError("Not a valid sample period format - Please refer to the User Guide")
    return period


def lookback_validator(lookback: Union[str, int], *args, **kwargs):
    if isinstance(lookback, int) and (lookback < 0): raise PrismValueError('lookback should be positive')
    if isinstance(lookback, str):
        period_pattern = r"([1-9][0-9]{0,3})?(D|W)"
        if re.fullmatch(period_pattern, lookback) is None:
            raise PrismValueError("Not a valid sample lookback format - Please refer to the User Guide")
        return lookback
    return f"{lookback}D"

def period_validator(period, *args, **kwargs):
    period_pattern = r"([1-9][0-9]{0,3})?(D|W|M|Q|SA|Y)"

    if re.fullmatch(period_pattern, period) is None:
        raise PrismValueError("Not a valid sample period format - Please refer to the User Guide")
    return period

def n_quarter_validator(n_quarter, *args, **kwargs):
    if n_quarter < 0: raise PrismValueError("n_quarter must be non-negative integer")

# if param_name equals dict's key name
# TODO: refactor this code using eval
validation_functions: dict[str, Callable[[Any, str], Any]] = {
    "startdate": startdate_param_validator,
    "enddate": enddate_param_validator,
    "setting": setting_param_validator,
    "settings": settings_param_validator,
    "data_interval": data_interval_validator,
    "period": period_validator,
    "lookback": lookback_validator,
    "frequency": frequency_validator,
}


# custom validators
def custom_universename_validator(arg):
    regex = re.compile("[@_!#$%^&*()<>?/|}{~:]`\"'")
    if isinstance(arg, list):
        for a in arg:
            if regex.search(a) is not None:
                raise PrismValueError(
                    "universename not to include special characters")
    else:
        if regex.search(arg) is not None:
            raise PrismValueError(
                "universename not to include special characters")
    return arg


def custom_min_sample_validator(arg):
    if arg < 1:
        raise PrismValueError("min_sample cannot be less than 1")
    return arg


# uses custum pattern to check param_name
custom_validation_functions: dict[str, tuple[Callable[[str], bool], Callable[[Any], Any]]] = {
    "universename": (lambda param_name: "universename" in param_name, custom_universename_validator),
    "min_sample": (lambda param_name: "min_sample" in param_name, custom_min_sample_validator)
}


def get_sm_attributeid(attribute: str, id=True):
    if const.SMAttributemap is None:
        raise PrismAuthError(f"Please Login First")
    attribute_lower = attribute.lower().replace(' ', '').replace('_', '')
    smattributeid = const.SMAttributemap.get(attribute_lower)
    if smattributeid is None:
        raise PrismValueError(
            f"{attribute} is not a valid Security Master attribute",
            valid_list=list(const.SMValues["attributename"].unique())
        )
    return smattributeid
