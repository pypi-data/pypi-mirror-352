import copy
import orjson
import logging
from abc import ABC
from dataclasses import dataclass
from uuid import UUID, uuid4
from typing import Union, ClassVar

import pandas as pd

from .._common import const
from .._core._req_builder import _dataquery
from .._utils import _validate_args, _req_call
from .._utils.exceptions import PrismAuthError, PrismTypeError


logger = logging.getLogger()


class classproperty:
    def __init__(self, f):
        self.f = f
    def __get__(self, instance, owner):
        return self.f(owner)


@dataclass
class _AbstractPrismComponent(ABC):
    _componentid: ClassVar[int] = None
    _categoryid: ClassVar[int] = None
    _component_category: ClassVar[str] = None
    _component_name: ClassVar[str] = None
    _query = None

    def __init__(
        self,
        component_args: dict = {},
        children: list = [],
        nodeid: UUID = None,
        **kwargs,
    ):
        if nodeid is None: nodeid = str(uuid4())

        self._query = {
            "component_type": self.component_type.value,
            "categoryid": self.categoryid,
            "component_category": self.component_category,
            "componentid": self.componentid,
            "component_name": self.component_name,
            "component_args": {k: v._query if isinstance(v, _AbstractPrismComponent) else v for k, v in component_args.items()},
            "children": [c._query if isinstance(c, _AbstractPrismComponent) else c for c in children],
            "nodeid": nodeid,
        }
        orjson.dumps(self._query)


    @classproperty
    def componentid(cls):
        if not cls._componentid:
            if const.CategoryComponent is None:
                raise PrismAuthError(f"Please Login First")
            attr = const.CategoryComponent[(const.CategoryComponent["component_name_repr"]==cls.__name__)]
            if cls.component_type != "functioncomponent":
                attr = attr[attr["component_category_repr"]==cls._component_category_repr]
            cls._componentid = int(attr["componentid"].values[0])
            cls._component_name = attr["componentname"].values[0]
        return cls._componentid

    @classproperty
    def categoryid(cls):
        if not cls._categoryid:
            if const.CategoryComponent is None:
                raise PrismAuthError(f"Please Login First")
            if cls.component_type == "functioncomponent":
                attr = const.CategoryComponent[(const.CategoryComponent["component_name_repr"]==cls.__name__)]
            else:
                attr = const.CategoryComponent[const.CategoryComponent["component_category_repr"]==cls._component_category_repr]
            cls._categoryid = int(attr["categoryid"].values[0])
            cls._component_category = attr["categoryname"].values[0]
        return cls._categoryid

    @classproperty
    def component_name(cls):
        if not cls._component_name:
            if const.CategoryComponent is None:
                raise PrismAuthError(f"Please Login First")
            attr = const.CategoryComponent[(const.CategoryComponent["component_name_repr"]==cls.__name__)]
            if cls.component_type != "functioncomponent":
                attr = attr[attr["component_category_repr"]==cls._component_category_repr]
            cls._componentid = int(attr["componentid"].values[0])
            cls._component_name = attr["componentname"].values[0]
        return cls._component_name

    @classproperty
    def component_category(cls):
        if not cls._component_category:
            if const.CategoryComponent is None:
                raise PrismAuthError(f"Please Login First")
            if cls.component_type == "functioncomponent":
                attr = const.CategoryComponent[(const.CategoryComponent["component_name_repr"]==cls.__name__)]
            else:
                attr = const.CategoryComponent[const.CategoryComponent["component_category_repr"]==cls._component_category_repr]
            cls._categoryid = int(attr["categoryid"].values[0])
            cls._component_category = attr["categoryname"].values[0]
        return cls._component_category

    def __setattr__(self, name, value):
        if (name in ["__componentid", "__categoryid", "_component_name", "_component_category", "_component_type"]) and (getattr(self, name) is not None):
            raise AttributeError("Can't modify {}".format(name))
        super().__setattr__(name, value)

    def __repr__(self):
        self.query(verbose=False)
        return "Query Structure"

    def _dict_to_tree(self, query: dict, verbose: bool, depth: int = 0):
        if not verbose:
            try:
                logger.info("\t" * depth, "====", query["component_name"])
                for c in query["children"]:
                    self._dict_to_tree(c, False, depth + 1)
            except:
                pass
        else:
            # try:
            if (query["component_name"] == "Constant") or (query["component_type"] == "functioncomponent") or (query["component_category"] is None):
                component = query["component_name"]
            else:
                component = query["component_category"] + "/" + query["component_name"]
            logger.info(
                "\t" * depth,
                "====",
                component,
            )
            if len(query["component_args"]) > 0:
                logger.info(
                    "\t" * (depth + 1),
                    "parameters: {",
                )
                for k, v in query["component_args"].items():
                    if "_dataquery" in str(k):
                        logger.info("\t" * (depth + 2), k.split("_dataquery")[0], ":")
                        if isinstance(v, list):
                            for d in v:
                                logger.info(self._dict_to_tree(d, True, depth + 2))
                        else:
                            logger.info(self._dict_to_tree(v, True, depth + 2))
                    else:
                        logger.info("\t" * (depth + 2), k, ":", v)
                logger.info("\t" * (depth + 2), "}")
            for idx, c in enumerate(query["children"]):
                if (self._component_name == "map") & (idx != 0):
                    break
                self._dict_to_tree(c, True, depth + 1)
            # except:
            #     pass

    def copy(self):
        """
        Return a deep copy of PrismComponent.

        Returns
        -------
            PrismComponent
                A deep copy of PrismComponent object

        Examples
        --------
            >>> o = ps.market.open()
            >>> intraday_r = c/o
            >>> intraday_r.query()
            ==== __truediv__
                parameters: {}
                ==== MarketDataComponentType.CLOSE
                    parameters: {
                        package : None
                        adjustment : True
                        currency : None
                        }
                ==== MarketDataComponentType.OPEN
                    parameters: {
                        package : None
                        adjustment : True
                        currency : None

            >>> intraday_r_copy = intraday_r.copy()
            >>> intraday_r_copy.query()
            ==== __truediv__
                parameters: {}
                ==== MarketDataComponentType.CLOSE
                    parameters: {
                        package : None
                        adjustment : True
                        currency : None
                        }
                ==== MarketDataComponentType.OPEN
                    parameters: {
                        package : None
                        adjustment : True
                        currency : None

        """
        return copy.deepcopy(self)

    def query(self, verbose: bool = True):
        """
        Print query held by the component represented in a tree format.

        Parameters
        ----------
            verbose : bool, default True
                | Option to run execution in 'verbose' mode.
                | If True, the parameter details are also printed.

        Returns
        -------
            None
                Print query held by the component represented in a tree format.

        Examples
        --------
            >>> c = ps.market.close()
            >>> o = ps.market.open()
            >>> intraday_r = c/o
            >>> print(intraday_r )
            === __truediv__
            ==== MarketDataComponentType.CLOSE
            ==== MarketDataComponentType.OPEN
            Query Structure

            >>> intraday_r.query()
            ==== __truediv__
                parameters: {}
                ==== MarketDataComponentType.CLOSE
                    parameters: {
                        package : None
                        adjustment : True
                        currency : None
                        }
                ==== MarketDataComponentType.OPEN
                    parameters: {
                        package : None
                        adjustment : True
                        currency : None
                        }
        """
        self._dict_to_tree(self._query, verbose)

    @_validate_args
    @_req_call(_dataquery)
    def get_data(
        self,
        universe: Union[str, int] = None,
        startdate: str = None,
        enddate: str = None,
        shownid: list = None,
        name: list = None,
        data_type: str = 'pandas',
        timeout: int = 600,
    ) -> pd.DataFrame:
        """
        This is an alias to :func:`prismstudio.get_data`.
        """
        ...

    @_validate_args
    def save(self, name: str):
        """
        If the component is a data component, this is an alias to :func:`prismstudio.save_dataquery`
        and if the component is a task component, this is an alias to :func:`prismstudio.save_taskquery`
        """
        return _dataquery.save_dataquery(self, name)


    # @_validate_args
    # def extract(self, return_code=False):
    #     """
    #     If the component is a data component, this is an alias to :func:`prismstudio.extract_dataquery`
    #     and if the component is a task component, this is an alias to :func:`prismstudio.extract_taskquery`
    #     """
    #     return _dataquery.extract_dataquery(self, return_code)
