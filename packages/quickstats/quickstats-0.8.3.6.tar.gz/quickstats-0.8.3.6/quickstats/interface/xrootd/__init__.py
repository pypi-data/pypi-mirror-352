from quickstats.core.modules import require_module
require_module("XRootD")

from .core import *
from .filesystem import *
from .xrd_helper import XRDHelper