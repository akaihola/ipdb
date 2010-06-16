import os
import pprint
import sys
import traceback
from IPython.Debugger import Pdb as _Pdb
from IPython.Shell import IPShell
from IPython import ipapi

shell = IPShell(argv=[''])

class Pdb(_Pdb):
    
    watched_vars = []
    
    def postcmd(self, stop, line):
        locals = self.curframe.f_locals
        if any(var in locals for var in self.watched_vars):
            print 'watched vars:'
            pprint.pprint(dict([(k,v) for k,v in locals.items() if k in self.watched_vars]))
        return stop

    def do_watch(self, var):
        self.watched_vars.append(var)
        print 'now watching "%s"' % var

    def do_unwatch(self, var):
        self.watched_vars.remove(var)
        print 'stopped watching "%s"' % var

class Restart(Exception):
    """Causes a debugger to be restarted for the debugged python program."""
    pass

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

def main():
    if not sys.argv[1:] or sys.argv[1] in ("--help", "-h"):
        print "usage: ipdb scriptfile [arg] ..."
        sys.exit(2)

    mainpyfile =  sys.argv[1]     # Get script filename
    if not os.path.exists(mainpyfile):
        print 'Error:', mainpyfile, 'does not exist'
        sys.exit(1)

    del sys.argv[0]         # Hide "pdb.py" from argument list

    # Replace pdb's dir with script's dir in front of module search path.
    sys.path[0] = os.path.dirname(mainpyfile)

    # Note on saving/restoring sys.argv: it's a good idea when sys.argv was
    # modified by the script being debugged. It's a bad idea when it was
    # changed by the user from the command line. There is a "restart" command which
    # allows explicit specification of command line arguments.

    # Don't initialize color, since Emacs can't handle it
    pdb = Pdb()
    while 1:
        try:
            pdb._runscript(mainpyfile)
            if pdb._user_requested_quit:
                break
            print "The program finished and will be restarted"
        except Restart:
            print "Restarting", mainpyfile, "with arguments:"
            print "\t" + " ".join(sys.argv[1:])
        except SystemExit:
            # In most cases SystemExit does not warrant a post-mortem session.
            print "The program exited via sys.exit(). Exit status: ",
            print sys.exc_info()[1]
        except:
            traceback.print_exc()
            print "Uncaught exception. Entering post mortem debugging"
            print "Running 'cont' or 'step' will restart the program"
            t = sys.exc_info()[2]
            pdb.interaction(None, t)
            print "Post mortem debugger finished. The "+mainpyfile+" will be restarted"
