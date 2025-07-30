import sys
import traceback
from typing import Optional
from contextlib import contextmanager

from quickstats import cached_import, module_exists

@contextmanager
def redirect_log(log_path: Optional[str] = None):
    """Context manager to redirect stdout to a log file and handle ROOT output redirection."""
    ROOT = cached_import("ROOT") if module_exists('ROOT') else None
    log_file = None
    _stdout = sys.stdout
    try:
        if log_path:
            log_file = open(log_path, 'w')
            sys.stdout = log_file
            if ROOT:
                ROOT.gSystem.RedirectOutput(log_path)
        yield sys.stdout
    except Exception:
        # Capture and print full traceback to the redirected stdout (or default stdout)
        traceback.print_exc(file=sys.stdout)
    finally:
        if log_file:
            log_file.close()
            if ROOT:
                ROOT.gROOT.ProcessLine('gSystem->RedirectOutput(0);')
        sys.stdout = _stdout # Restore original stdout