from quickstats.core.modules import require_module_version
require_module_version("python", (3, 8, 0))
require_module_version("pydantic", (2, 0, 0))

from .default_model import DefaultModel