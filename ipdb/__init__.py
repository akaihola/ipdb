import sys
from IPython.Debugger import Pdb
from IPython.Shell import IPShell
from IPython import ipapi

shell = IPShell(argv=[''])

def set_trace():
    try:
        import nose.core
        from traceback import extract_stack
        nose_core_path = nose.core.__file__.rstrip('c')
        if nose_core_path in (entry[0] for entry in extract_stack()):
            from IPython.Shell import Term
            Term.cout = sys.stdout = sys.__stdout__
    except ImportError:
        pass
    ip = ipapi.get()
    def_colors = ip.options.colors
    Pdb(def_colors).set_trace(sys._getframe().f_back)
