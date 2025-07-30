# Package namespace for viphl.dto
import sys
import os

# Add the current package to path to allow relative imports within Cython modules
__path__ = [os.path.dirname(os.path.abspath(__file__))]

# Important: We'll modify the import order to prevent circular imports
# First, let's make the Cython modules available by simple names in sys.modules
# This will let Cython modules find each other without triggering full imports
class LazyModule:
    def __init__(self, name):
        self.name = name
        self._real_module = None
        
    def __getattr__(self, attr):
        if self._real_module is None:
            import importlib
            self._real_module = importlib.import_module(f"viphl.dto.{self.name}")
        return getattr(self._real_module, attr)

# Register lazy module proxies instead of immediately importing
sys.modules['settings'] = LazyModule('settings')
sys.modules['hl'] = LazyModule('hl')
sys.modules['bypoint'] = LazyModule('bypoint')
sys.modules['recovery_window'] = LazyModule('recovery_window')

# Now import modules individually to expose their contents
from .settings import *
from .hl import *
from .bypoint import *
from .recovery_window import *

# Import viphl last as it may depend on the others
from .viphl import *

# Optional: Clean up sys.modules to use real modules instead of proxies
import importlib
for mod_name in ['settings', 'hl', 'bypoint', 'recovery_window']:
    try:
        sys.modules[mod_name] = importlib.import_module(f"viphl.dto.{mod_name}")
    except ImportError as e:
        print(f"Warning: Could not load real module for {mod_name}: {e}")
