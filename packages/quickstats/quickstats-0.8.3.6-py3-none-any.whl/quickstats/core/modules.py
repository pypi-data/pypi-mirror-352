"""Module management utilities for dependency checking and version verification.

This module provides utilities for:
- Cached module importing
- Module existence checking
- Version requirements verification
- ROOT-specific module handling
"""

import sys
import shutil
import subprocess
import importlib
import importlib.util
from typing import Dict, Any, Callable, Optional, Union, Tuple, TypeVar, List
from dataclasses import dataclass

from .versions import Version, ROOTVersion
from .root_specs import get_installed_version

__all__: List[str] = [
    'cached_import',
    'get_root_version',
    'module_exists',
    'get_module_version',
    'require_module',
    'require_module_version'
]

ModuleName = str
VersionSpec = Union[str, Tuple[int, ...], Version]
T = TypeVar('T')

@dataclass
class ModuleSpec:
    """Specification for module requirements."""
    name: str
    min_version: Optional[VersionSpec] = None
    checker: Optional[Callable[[str], bool]] = None

class ModuleError(Exception):
    """Base exception for module-related errors."""
    pass

class ModuleNotFoundError(ModuleError):
    """Raised when a required module is not found."""
    pass

class ModuleVersionError(ModuleError):
    """Raised when a module's version doesn't meet requirements."""
    pass

class ModuleRegistry:
    """Registry for managing imported modules."""
    
    def __init__(self):
        self._modules: Dict[ModuleName, Any] = {}
    
    def get(self, name: ModuleName) -> Optional[Any]:
        """Get a module from the registry."""
        return self._modules.get(name)
    
    def set(self, name: ModuleName, module: Any) -> None:
        """Add a module to the registry."""
        self._modules[name] = module
    
    def __contains__(self, name: ModuleName) -> bool:
        return name in self._modules

# Global module registry
REGISTRY = ModuleRegistry()

def cached_import(module_name: ModuleName) -> Any:
    """Import and cache a module.
    
    Parameters
    ----------
    module_name : str
        Name of the module to import
        
    Returns
    -------
    Any
        The imported module
        
    Raises
    ------
    ModuleNotFoundError
        If the module doesn't exist
    ModuleError
        For other import-related errors
    """
    if module_name not in REGISTRY:
        try:
            module = importlib.import_module(module_name)
            REGISTRY.set(module_name, module)
        except ImportError as e:
            raise ModuleNotFoundError(
                f"Failed to import module '{module_name}': {str(e)}"
            ) from e
        except Exception as e:
            raise ModuleError(
                f"Unexpected error importing '{module_name}': {str(e)}"
            ) from e
    
    module = REGISTRY.get(module_name)
    
    # Special handling for ROOT
    if module_name == "ROOT":
        module.gROOT.SetBatch(True)
    
    return module

def get_root_version() -> ROOTVersion:
    """Get the installed ROOT version.
    
    Returns
    -------
    ROOTVersion
        The installed ROOT version or (0, 0, 0) if not installed
    """
    try:
        return get_installed_version()
    except Exception:
        return ROOTVersion((0, 0, 0))

def is_root_installed() -> bool:
    """Check if ROOT is installed.
    
    Returns
    -------
    bool
        True if ROOT is installed with a valid version
    """
    return get_root_version() > ROOTVersion((0, 0, 0))

def is_kerberos_installed() -> bool:
    """Check if Kerberos client tools are installed.

    Returns
    -------
    bool
        True if Kerberos client tools are installed and functioning,
        False otherwise

    Examples
    --------
    >>> if is_kerberos_installed():
    ...     print("Kerberos is available")
    ... else:
    ...     print("Kerberos is not installed")
    """
    if not shutil.which('klist'):
        return False
        
    try:
        subprocess.run(
            ['klist', '--version'], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            timeout=5
        )
        return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False
    except subprocess.CalledProcessError:
        # Some implementations return non-zero exit code but are still valid
        return True
    except Exception:
        return False

def module_exists(name: ModuleName) -> bool:
    """Check if a module exists and can be imported.
    
    Parameters
    ----------
    name : str
        Name of the module to check
        
    Returns
    -------
    bool
        True if the module exists and is importable
    """
    if name == 'python':
        return True
    if name == 'ROOT':
        return is_root_installed()
    if name == 'kerberos':
        return is_kerberos_installed()
    return importlib.util.find_spec(name) is not None

def get_module_version(name: ModuleName) -> Version:
    """Get the version of an installed module.
    
    Parameters
    ----------
    name : str
        Name of the module
        
    Returns
    -------
    Version
        Version of the module
        
    Raises
    ------
    ModuleNotFoundError
        If the module is not installed
    ModuleVersionError
        If the module version cannot be determined
    """
    if name == 'python':
        return Version(sys.version.split()[0])
    elif name == 'ROOT':
        return get_root_version()
    
    if not module_exists(name):
        raise ModuleNotFoundError(f'Module not installed: {name}')
    
    module = cached_import(name)
    
    if not hasattr(module, '__version__'):
        raise ModuleVersionError(
            f'Cannot determine version for module: {name}'
        )
    
    return Version(module.__version__)

def require_module(
    name: ModuleName,
    checker: Optional[Callable[[str], bool]] = None
) -> bool:
    """Verify that a required module is available.
    
    Parameters
    ----------
    name : str
        Name of the module
    checker : Optional[Callable[[str], bool]]
        Custom function to check module availability
        
    Returns
    -------
    bool
        True if the module is available
        
    Raises
    ------
    ModuleNotFoundError
        If the module is not available
    """
    if name == 'python':
        return True

    check_fn = checker if checker is not None else module_exists
    
    if not check_fn(name):
        raise ModuleNotFoundError(
            f"Required module '{name}' not found. Please install it."
        )
    
    return True

def require_module_version(
    name: ModuleName,
    version: VersionSpec,
    checker: Optional[Callable[[str], bool]] = None
) -> bool:
    """Verify that a module meets version requirements.
    
    Parameters
    ----------
    name : str
        Name of the module
    version : Union[str, Tuple[int, ...], Version]
        Minimum required version
    checker : Optional[Callable[[str], bool]]
        Custom function to check module availability
        
    Returns
    -------
    bool
        True if the module meets version requirements
        
    Raises
    ------
    ModuleNotFoundError
        If the module is not available
    ModuleVersionError
        If the module version is insufficient
    """
    require_module(name, checker)
    
    module_version = get_module_version(name)
    min_version = Version(version) if not isinstance(version, Version) else version
    
    if module_version < min_version:
        raise ModuleVersionError(
            f'Module "{name}" requires minimum version {min_version} '
            f'but found {module_version}'
        )
    
    return True