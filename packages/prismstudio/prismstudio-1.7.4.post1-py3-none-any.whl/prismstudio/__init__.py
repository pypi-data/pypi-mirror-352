import sys
import inspect
import IPython
from ._core import *
from ._core import _data, ols, _model
from ._core._req_builder import preference
from ._utils.version import __version__
from ._utils.validate_utils import handle_sys_exception, handle_jupyter_exception
from ._utils.modes import log_config
from ._prismcomponent.abstract_prismcomponent import _AbstractPrismComponent
from ._prismcomponent.prismcomponent import _PrismComponent, _PrismDataComponent


_username = ''

IPython.core.interactiveshell.InteractiveShell.showtraceback = handle_jupyter_exception(IPython.core.interactiveshell.InteractiveShell.showtraceback)
sys.excepthook = handle_sys_exception

_data_pkg_list = inspect.getmembers(_data, inspect.ismodule)
_model_list = inspect.getmembers(_model, inspect.ismodule)
_data_pkg_list = _data_pkg_list + _model_list
for pkg_name, pkg in _data_pkg_list:
    new_pkg_name = f"{__name__}.{pkg_name}"
    if new_pkg_name not in sys.modules.keys():
        pkg.__name__ = new_pkg_name  # Will have no effect; see below
        sys.modules[new_pkg_name] = pkg

# ols module
new_pkg_name = f"{__name__}.ols"
ols.__name__ = new_pkg_name
sys.modules[new_pkg_name] = ols

new_pkg_name = f"{__name__}.preference"
preference.__name__ = new_pkg_name
sys.modules[new_pkg_name] = preference

log_config()