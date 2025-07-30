import os
import pathlib

from .logger import _LOGGER_
from .modules import get_root_version

__all__ = ["module_path", "macro_path",
           "resource_path", "stylesheet_path",
           "MAX_WORKERS", "stdout", "corelib_loaded",
           "root_version"]

# silence cppyy warning
os.environ['CLING_STANDARD_PCH'] = "none"
os.environ['CPPYY_API_PATH'] = "none"

module_path = pathlib.Path(__file__).parent.parent.absolute()
macro_path = os.path.join(module_path, 'macros')
resource_path = os.path.join(module_path, 'resources')
stylesheet_path = os.path.join(resource_path, 'mpl_stylesheets')

MAX_WORKERS = 8

corelib_loaded = False

stdout = _LOGGER_

root_version = get_root_version()