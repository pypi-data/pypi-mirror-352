"""ROOT environment specification and configuration utilities.

This module provides functions to interact with ROOT installation,
retrieve configuration settings, and check ROOT features.
"""

import os
import subprocess
from functools import lru_cache
from typing import Dict, List, Optional, Union
from pathlib import Path

from .versions import ROOTVersion

class ROOTConfigError(Exception):
    """Raised when ROOT configuration commands fail."""
    pass

def run_command(args: List[str], error_msg: Optional[str] = None) -> str:
    """Execute a subprocess command and return its output.

    Parameters
    ----------
    args : List[str]
        Command and its arguments as a list of strings
    error_msg : Optional[str]
        Custom error message to use if the command fails

    Returns
    -------
    str
        Command output as a UTF-8 string with whitespace stripped

    Raises
    ------
    ROOTConfigError
        If the command fails to execute or returns non-zero status
    """
    if error_msg is None:
        error_msg = f"Failed to execute command: {' '.join(args)}"

    try:
        result = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise ROOTConfigError(
            f"{error_msg}. Process returned {e.returncode}. "
            f"stderr: {e.stderr.strip()}"
        ) from e
    except OSError as e:
        raise ROOTConfigError(
            f"{error_msg}. Please check if ROOT is installed properly. "
            f"Error: {str(e)}"
        ) from e

@lru_cache(maxsize=1)
def get_rootsys() -> Optional[Path]:
    """Get the ROOT system directory from environment.

    Returns
    -------
    Optional[Path]
        Path to ROOT installation directory or None if ROOTSYS is not set
    """
    rootsys = os.getenv('ROOTSYS')
    return Path(rootsys) if rootsys else None

@lru_cache(maxsize=1)
def get_config_cmd() -> Path:
    """Get the path to root-config command.

    Returns
    -------
    Path
        Path to root-config executable

    Notes
    -----
    If ROOTSYS is set, looks for root-config in $ROOTSYS/bin,
    otherwise assumes root-config is in PATH.
    """
    rootsys = get_rootsys()
    if rootsys is None:
        return Path('root-config')
    return rootsys / 'bin' / 'root-config'

def get_installed_version() -> ROOTVersion:
    """Get the version of ROOT installed on the system.

    Returns
    -------
    ROOTVersion
        Version of the installed ROOT

    Raises
    ------
    ROOTConfigError
        If root-config command fails or returns invalid version
    """
    config_cmd = get_config_cmd()
    version = run_command(
        [str(config_cmd), '--version'],
        "Failed to determine ROOT version"
    )
    return ROOTVersion(version)

def get_runtime_version() -> ROOTVersion:
    """Get the version of ROOT being used at runtime.

    Returns
    -------
    ROOTVersion
        Version of ROOT currently loaded in Python

    Raises
    ------
    ImportError
        If ROOT Python bindings are not installed
    """
    try:
        import ROOT
        return ROOTVersion(ROOT.gROOT.GetVersionInt())
    except ImportError as e:
        raise ImportError(
            "Failed to import ROOT. Please check if PyROOT is installed properly."
        ) from e

def get_flags() -> Dict[str, List[str]]:
    """Get compilation and linking flags for ROOT.

    Returns
    -------
    Dict[str, List[str]]
        Dictionary containing 'cflags' and 'ldflags' as lists of flags

    Raises
    ------
    ROOTConfigError
        If root-config command fails
    """
    config_cmd = get_config_cmd()
    cmd_str = str(config_cmd)

    try:
        cflags = run_command(
            [cmd_str, '--cflags'],
            "Failed to get ROOT compilation flags"
        )
        ldflags = run_command(
            [cmd_str, '--libs'],
            "Failed to get ROOT linking flags"
        )
    except ROOTConfigError as e:
        raise ROOTConfigError(
            f"Failed to get ROOT build flags: {str(e)}"
        ) from e

    return {
        'cflags': cflags.split(),
        'ldflags': ldflags.split()
    }

def has_feature(feature: str) -> bool:
    """Check if ROOT was built with a specific feature.

    Parameters
    ----------
    feature : str
        Name of the feature to check

    Returns
    -------
    bool
        True if ROOT has the feature, False otherwise

    Raises
    ------
    ROOTConfigError
        If root-config command fails
    """
    config_cmd = get_config_cmd()
    try:
        result = run_command(
            [str(config_cmd), f'--has-{feature}'],
            f"Failed to check ROOT feature: {feature}"
        )
        return result.lower() == 'yes'
    except ROOTConfigError as e:
        return False