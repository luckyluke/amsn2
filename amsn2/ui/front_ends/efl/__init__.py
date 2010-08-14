
from amsn2.core import aMSNUserInterfaceManager
import sys
import traceback

# Here we load the actual front end.
# We need to import the front end module and return it
# so the guimanager can access its classes
def load():
    try:
        import amsn2.ui.front_ends.efl.efl
    except ImportError:
        etype, value, trace = sys.exc_info()
        traceback.print_exception(etype, value, trace.tb_next)
        return None
    return amsn2.ui.front_ends.efl.efl


# Initialize the front end by checking for any
# dependency then register it to the guimanager
try:
    import imp
    imp.find_module("evas")
    imp.find_module("edje")
    imp.find_module("ecore")
    imp.find_module("elementary")

    aMSNUserInterfaceManager.register_frontend("efl", sys.modules[__name__])

except ImportError:
    pass

