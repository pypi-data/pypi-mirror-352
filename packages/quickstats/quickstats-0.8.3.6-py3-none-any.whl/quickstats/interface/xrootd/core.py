from contextlib import contextmanager

__all__ = ["get_cachedir", "set_cachedir", "switch_cachedir"]

class Setting:
    CACHEDIR = None

def get_cachedir():
    return Setting.CACHEDIR

def set_cachedir(dirname:str=None):
    Setting.CACHEDIR = dirname

@contextmanager
def switch_cachedir(dirname:str):
    try:
        tmp_cachedir = get_cachedir()
        set_cachedir(dirname)
        yield None
    finally:
        set_cachedir(tmp_cachedir)