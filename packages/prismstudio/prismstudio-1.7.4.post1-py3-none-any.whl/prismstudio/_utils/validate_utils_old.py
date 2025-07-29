import inspect
import logging
import re
import sys
from functools import wraps
from typing import Any, Callable

import pandas as pd

from prismstudio._utils.exceptions import PrismAuthError, PrismTypeError, PrismValueError
from .._common import const


logger = logging.getLogger()


def handle_jupyter_exception(func):
    @wraps(func)
    def showtraceback(*args, **kwargs):
        # extract exception type, value and traceback
        etype, evalue, tb = sys.exc_info()
        customType = "Prism" in etype.__name__
        if customType:
            logger.info(evalue)
            return
        else:
            # otherwise run the original hook
            value = func(*args, **kwargs)
            return value
    return showtraceback


def handle_sys_exception(exc_type, exc_value, exc_traceback):
    customType = "Prism" in exc_type.__name__
    if customType:
        logger.info(exc_value)
        return
    else:
        # otherwise run the original hook
        return sys.__excepthook__(exc_type, exc_value, exc_traceback)


def _validate_args(function):
    @wraps(function)
    def type_checker(*args, **kwargs):
        func_params_dict = inspect.signature(function).parameters

        # construct param-arg pairs: order matters - do not use set operations
        pos_params = tuple(p for p in func_params_dict.keys() if p not in kwargs.keys())
        if "self" in pos_params:
            pos_params = tuple(p for p in pos_params if p != "self")
            pos_args = dict(zip(pos_params, args[1:]))
        else:
            pos_args = dict(zip(pos_params, args))
        all_args = kwargs.copy()
        all_args.update(pos_args)

        args = list(args)

        if function.__name__ == "fillna":
            if not((all_args.get("value", None) is not None) ^ (all_args.get("method", None) is not None)):
                raise PrismValueError("Must specify one fill 'value' or 'method'.")

        for param, v in func_params_dict.items():

            # if None, not provided (nor required)
            arg = all_args.get(param, v.default)
            if (arg is not None) and (arg is not inspect._empty):
                # check types
                param_type = v.annotation  # if empty, no hints
                if param_type is not inspect._empty:
                    if hasattr(param_type, "__args__"):
                        unionArgs = param_type.__args__
                        if unionArgs is not None and not isinstance(arg, tuple(unionArgs)):
                            raise PrismTypeError(f"Type of {param} is {type(arg)} and not in the Union of {unionArgs}")
                    else:
                        if not issubclass(type(arg), param_type):
                            raise PrismTypeError(f"Type of {param} is {type(arg)} and not {param_type}")

                # validation rules
                arg_enum = None
                if param == "frequency":
                    if function.__name__ == "get_universe":
                        try:
                            arg_enum = const.UniverseFrequencyType(arg)
                        except Exception as e:
                            raise PrismValueError(f"{e}", valid_list=const.UniverseFrequencyType)
                    else:
                        try:
                            arg_enum = const.FrequencyType(arg)
                        except Exception as e:
                            raise PrismValueError(f"{e}", valid_list=const.FrequencyType)
                elif param == "datetype":
                    try:
                        arg_enum = const.DateType(arg)
                    except Exception as e:
                        raise PrismValueError(f"{e}", valid_list=const.DateType)
                elif param == "periodtype":
                    try:
                        arg_enum = const.PeriodType(arg)
                    except Exception as e:
                        raise PrismValueError(f"{e}", valid_list=const.PeriodType)
                elif param == "adjustment": # can be string or bool
                    if arg not in [a.value for a in const.AdjustmentType]:
                        raise PrismValueError(f"Invalid adjustment argument is given. ", valid_list=const.AdjustmentType)
                elif param == "shownid":
                    for idx, id in enumerate(arg):
                        arg[idx] = get_sm_attributevalue(id)
                elif param == "rank_method":
                    try:
                        arg_enum = const.RankType(arg)
                    except Exception as e:
                        raise PrismValueError(f"{e}", valid_list=const.RankType)
                elif param == "method":
                    try:
                        arg_enum = const.FillnaMethodType(arg)
                    except Exception as e:
                        raise PrismValueError(f"{e}", valid_list=const.FillnaMethodType)
                # elif param == "beyond":
                #     try:
                #         assert isinstance(arg, bool)
                #         arg_enum = arg
                #     except Exception as e:
                #         raise PrismValueError(f"{e}", valid_list=BeyondType)
                elif param in ["startdate", "enddate"]:
                    try:
                        date = pd.to_datetime(arg)
                    except Exception as e:
                        raise PrismValueError(f'Unknown string format. Cannot parse "{arg}" to a date')

                    assert (date >= const.BEGINNING_DATE) & (date <= const.ACTIVE_DATE), "Not a valid date."

                elif "universename" in param:
                    regex = re.compile("[@_!#$%^&*()<>?/\|}{~:]`\"'")
                    if isinstance(arg, list):
                        for a in arg:
                            if regex.search(a) is not None:
                                raise PrismValueError("universename not to include special characters")
                    else:
                        if regex.search(arg) is not None:
                            raise PrismValueError("universename not to include special characters")

                elif "min_periods" in param:
                    if arg < 1:
                        raise PrismValueError("min_periods cannot be less than 1")

                elif (function.__name__ == "log") & (param == "base"):
                    if arg <= 0:
                        raise Exception("base condition error")
                elif param == 'preliminary':
                    try:
                        arg_enum = const.FinancialPreliminaryType(arg)
                    except Exception as e:
                        raise PrismValueError(f"{e}", valid_list=const.FinancialPreliminaryType)
                elif param == "setting":
                    from .._common.const import PreferenceType
                    if (arg not in PreferenceType) and (arg != ""):
                        raise PrismValueError(f"Invalid preference keyword is given. ", valid_list=PreferenceType)
                elif param == "settings":
                    from .._common.const import PreferenceType
                    for k in arg.keys():
                        if k not in PreferenceType:
                            raise PrismValueError(f"Invalid preference key is given. ", valid_list=PreferenceType)

                if arg_enum is not None:
                    if param in pos_args.keys():
                        for i, k in enumerate(func_params_dict.keys()):
                            if param == k:
                                break
                        args[i] = arg_enum
                    else:
                        kwargs[param] = arg_enum

        return function(*args, **kwargs)

    return type_checker



def validate_fillna_function(args_dict, function):
    if function.__name__ == "fillna":
        v, m = args_dict.get("value"), args_dict.get("method")
        if not (v is not None) ^ (m is not None):
            raise PrismValueError("Must specify one fill 'value' or 'method'.")


def check_argument_type(arg, param_type, param_name):
    if param_type is inspect.Parameter.empty:
        return

    if isinstance(param_type, type):
        if not isinstance(arg, param_type):
            raise PrismTypeError(
                f"Type of {param_name} is {type(arg)} and not {param_type}")
    elif not any(isinstance(arg, t) for t in param_type.__args__):
        raise PrismTypeError(
            f"Type of {param_name} is {type(arg)} and not in the Union of {param_type.__args__}")


def apply_validation_rules(arg, param_name: str, function_name: str):
    # if param_name equals function name
    if param_name in validation_functions:
        validation_function = validation_functions[param_name]
        return validation_function(arg, function_name)

    # if param_name matches custom pattern
    for _, (pattern_checker, validation_function) in custom_validation_functions.items():
        if pattern_checker(param_name):
            return validation_function(arg)

    # when there is no validation rule to check
    return arg


def frequency_param_validator(arg, function_name):
    if function_name == "get_universe":
        try:
            return const.UniverseFrequencyType(arg)
        except Exception as e:
            raise PrismValueError(
                f"{e}", valid_list=const.UniverseFrequencyType) from e
    else:
        try:
            return const.FrequencyType(arg)
        except Exception as e:
            raise PrismValueError(f"{e}", valid_list=const.FrequencyType) from e


def datetype_param_validator(arg, _):
    try:
        return const.DateType(arg)
    except Exception as e:
        raise PrismValueError(f"{e}", valid_list=const.DateType) from e


def periodtype_param_validator(arg, _):
    try:
        return const.PeriodType(arg)
    except Exception as e:
        raise PrismValueError(f"{e}", valid_list=const.PeriodType) from e


def adjustment_param_validator(arg, _):
    if arg not in [a.value for a in const.AdjustmentType]:
        # need review. original code 'e' is not bounded
        raise PrismValueError(
            'Invalid adjustment argument is given. ', valid_list=const.AdjustmentType)

    return arg


def shownid_param_validator(arg, _):
    for idx, id in enumerate(arg):
        arg[idx] = get_sm_attributevalue(id)

    return arg


def rank_method_param_validator(arg, _):
    try:
        return const.RankType(arg)
    except Exception as e:
        raise PrismValueError(f"{e}", valid_list=const.RankType) from e


def method_param_validator(arg, _):
    try:
        return const.FillnaMethodType(arg)
    except Exception as e:
        raise PrismValueError(f"{e}", valid_list=const.FillnaMethodType) from e


def startdate_param_validator(arg, _):
    try:
        date = pd.to_datetime(arg)
    except Exception as e:
        raise PrismValueError(
            f'Unknown string format. Cannot parse "{arg}" to a date') from e

    assert (date >= const.BEGINNING_DATE) & (
        date <= const.ACTIVE_DATE), "Not a valid date."

    return arg


def enddate_param_validator(arg, _):
    return startdate_param_validator(arg, _)


def base_param_validator(arg, function_name):
    if function_name == "log" and arg <= 0:
        raise Exception("base condition error")

    return arg


def preliminary_param_validator(arg, _):
    try:
        return const.FinancialPreliminaryType(arg)
    except Exception as e:
        raise PrismValueError(
            f"{e}", valid_list=const.FinancialPreliminaryType) from e


def setting_param_validator(arg, _):
    from .._common.const import PreferenceType
    if (arg not in PreferenceType) and (arg != ""):
        raise PrismValueError(
            "Invalid preference keyword is given. ", valid_list=PreferenceType)

    return arg


def settings_param_validator(arg, _):
    from .._common.const import PreferenceType
    for k in arg.keys():
        if k not in PreferenceType:
            raise PrismValueError(
                "Invalid preference key is given. ", valid_list=PreferenceType)

    return arg


# if param_name equals dict's key name
# TODO: refactor this code using eval
validation_functions: dict[str, Callable[[Any, str], Any]] = {
    "frequency": frequency_param_validator,
    "datetype": datetype_param_validator,
    "periodtype": periodtype_param_validator,
    "adjustment": adjustment_param_validator,
    "shownid": shownid_param_validator,
    "rank_method": rank_method_param_validator,
    "method": method_param_validator,
    "startdate": startdate_param_validator,
    "enddate": enddate_param_validator,
    "base": base_param_validator,
    "preliminary": preliminary_param_validator,
    "setting": setting_param_validator,
    "settings": settings_param_validator
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


def custom_min_periods_validator(arg):
    if arg < 1:
        raise PrismValueError("min_periods cannot be less than 1")

    return arg


# uses custum pattern to check param_name
custom_validation_functions: dict[str, tuple[Callable[[str], bool], Callable[[Any], Any]]] = {
    "universename": (lambda param_name: "universename" in param_name, custom_universename_validator),
    "min_periods": (lambda param_name: "min_periods" in param_name, custom_min_periods_validator)
}


def get_sm_attributevalue(attribute: str):
    if const.SMValues is None:
        raise PrismAuthError(f"Please Login First")
    smattributes_lower = {
        a.lower().replace(' ', '').replace('_', ''): const.SMValues[a]
        for a in const.SMValues.keys()
    }
    smattributes_lower.update({
        a.lower().replace(' ', '').replace('_', ''): a
        for a in const.SMValues.values()
    })
    attribute_lower = attribute.lower().replace(' ', '').replace('_', '')
    smattributevalue = smattributes_lower.get(attribute_lower)
    if smattributevalue is None:
        raise PrismValueError(
            f"{attribute} is not a valid Security Master attribute",
            valid_list=list(const.SMValues.keys())
        )
    return smattributevalue