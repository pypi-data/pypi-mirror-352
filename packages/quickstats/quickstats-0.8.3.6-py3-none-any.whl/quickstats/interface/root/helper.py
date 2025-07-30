from contextlib import contextmanager

from quickstats import cached_import

def set_multithread(multithread:bool):
    ROOT = cached_import("ROOT")
    if (not ROOT.IsImplicitMTEnabled()) and (multithread):
        ROOT.EnableImplicitMT()
    elif (ROOT.IsImplicitMTEnabled()) and (not multithread):
        ROOT.DisableImplicitMT()

class RMultithreadEnv(object):
    def __init__(self, enable_multithread:bool):
        ROOT = cached_import("ROOT")
        self.original_multithread_state = ROOT.IsImplicitMTEnabled()
        self.new_multithread_state = enable_multithread
      
    def __enter__(self):
        ROOT = cached_import("ROOT")
        if (not self.original_multithread_state) and self.new_multithread_state:
            ROOT.EnableImplicitMT()
        elif (self.original_multithread_state) and (not self.new_multithread_state):
            ROOT.DisableImplicitMT()
        return self
  
    def __exit__(self, *args):
        ROOT = cached_import("ROOT")
        if (not self.original_multithread_state) and self.new_multithread_state:
            ROOT.DisableImplicitMT()
        elif (self.original_multithread_state) and (not self.new_multithread_state):
            ROOT.EnableImplicitMT()

def redirect_print_stream(streamer):
    ROOT = cached_import("ROOT")
    old_streamer = ROOT.RooPrintable.defaultPrintStream(streamer)
    return old_streamer

def get_default_stream():
    ROOT = cached_import("ROOT")
    return ROOT.RooPrintable.defaultPrintStream()

def get_default_print_content(obj: "ROOT.RooPrintable", indent: str = '') -> str:
    cppyy = cached_import('cppyy')
    s = cppyy.gbl.std.stringstream()
    default_content = obj.defaultPrintContents('')
    default_style = obj.defaultPrintStyle('')
    style_option = cppyy.gbl.RooPrintable.StyleOption(default_style)
    obj.printStream(s, default_content, style_option, indent)
    return s.str()

@contextmanager
def switch_error_ignore_level(level: int = 6000):
    ROOT = cached_import("ROOT")
    temp = ROOT.gErrorIgnoreLevel
    try:
        ROOT.gErrorIgnoreLevel = level
        yield
    finally:
        ROOT.gErrorIgnoreLevel = temp