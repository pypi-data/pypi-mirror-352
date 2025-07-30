# viphl package initialization
# This file ensures proper imports and package structure

# Version information
__version__ = "0.1.8"

# Import the main classes for easier access
# Allow direct imports like: from viphl import VipHL
try:
    from viphl.dto.viphl import VipHL
except ImportError:
    pass  # Module might not be available during build/install

# Allow use of other modules through the namespace
# from viphl.dto import settings, hl, etc.
