from enum import EnumMeta, Enum

class PrismError(Exception):
    """Exception raised for errors in module prism"""

    def __init__(self, *args, **kwargs):
        if args:
            self.message = args[0]
        else:
            self.message = None

        super().__init__(self.message)

    def __str__(self):
        exception_type = "\033[91mPrismError\033[0m"
        return f"{exception_type}: {self.message}"


class PrismResponseError(Exception):
    """Exception raised for response errors from Prism BackEnd"""

    def __init__(self, *args, **kwargs):
        if args:
            self.message = args[0]
        else:
            self.message = None

        super().__init__(self.message)

    def __str__(self):
        exception_type = "\033[91mPrismResponseError\033[0m"
        return f"{exception_type}: {self.message}"


class PrismTypeError(Exception):
    """Exception raised for type errors from type checker in validate_utils.py"""

    def __init__(self, *args, **kwargs):
        if args:
            self.message = args[0]
        else:
            self.message = None

        super().__init__(self.message)

    def __str__(self):

        exception_type = "\033[91mPrismTypeError\033[0m"

        return f"{exception_type}: {self.message}"


class PrismValueError(Exception):
    """Exception raised for wrong Enum"""

    def __init__(self, *args, **kwargs):

        if args:
            self.message = args[0]
        else:
            self.message = None

        if kwargs:
            self.valid_list = kwargs.get("valid_list")
            self.invalids = kwargs.get("invalids")
        else:
            self.valid_list = []
            self.invalids = []

        super().__init__(self.message)

    def __str__(self):

        exception_type = "\033[91mPrismValueError\033[0m"
        if self.valid_list is not None and len(self.valid_list) > 0:
            extra_info_type = "\033[92mValid Arguments\033[0m"
            if isinstance(self.valid_list, (Enum, EnumMeta)):
                extra_info_message = [item.value for item in self.valid_list]
            elif isinstance(self.valid_list, list):
                extra_info_message = self.valid_list

            if self.invalids is not None:
                extra_info_message = list(set(extra_info_message) - set(self.invalids))

            return f"{exception_type}: {self.message}\n{extra_info_type} : {extra_info_message}"
        return f"{exception_type}: {self.message}"


class PrismAuthError(Exception):
    """ """

    def __init__(self, *args, **kwargs):
        if args:
            self.message = args[0]
        else:
            self.message = None

        super().__init__(self.message)

    def __str__(self):

        exception_type = "\033[91mPrismAuthError\033[0m"

        return f"{exception_type}: {self.message}"


class PrismNotFoundError(Exception):
    """Exception raised for"""

    def __init__(self, *args, **kwargs):
        if args:
            self.message = args[0]
        else:
            self.message = None
        super().__init__(self.message)

    def __str__(self):

        exception_type = "\033[91mPrismNotFoundError\033[0m"

        return f"{exception_type}: {self.message}"


class PrismTaskError(Exception):
    """Exception raised for"""

    def __init__(self, *args, **kwargs):
        if args:
            self.message = args[0]
        else:
            self.message = None
        super().__init__(self.message)

    def __str__(self):

        exception_type = "\033[91mPrismTaskError\033[0m"

        return f"{exception_type}: {self.message}"
