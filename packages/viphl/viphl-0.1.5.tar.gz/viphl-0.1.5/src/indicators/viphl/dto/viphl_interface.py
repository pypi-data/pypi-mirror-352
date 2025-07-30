"""
VipHL Python Interface - Provides the same API as the original viphl.py
but uses compiled Cython code for performance and source code protection.
"""

# Direct Python imports
from .settings import Settings
from .bypoint import ByPoint
from .recovery_window import (RecoveryWindow, RecoveryWindowResult, RecoveryWindowFailure,
                             RecoveryWindowSuccess, RecoveryWindowResultV2, 
                             FlatternRecoveryWindowResultV2, from_recovery_window_result_v2)
from .hl import HL, calculate_weighted_hl_value

# Import the Cython implementations of the HL class to get swap_hl
try:
    from .hl import swap_hl
    print("Using compiled Cython version for some helper functions.")
except ImportError:
    # If the Cython version isn't available, define a simple swap function
    def swap_hl(hl1, hl2):
        return hl2, hl1
    print("Using Python implementations.")

# Import the VipHL class
try:
    # Try importing the compiled version first
    from ..viphl import VipHL
except ImportError:
    # If that fails, try importing from viphl_indicator_1_95.py
    try:
        from ..viphl_indicator_1_95 import VipHL
        print("Using Python implementation of VipHL")
    except ImportError:
        raise ImportError("Could not import VipHL from any source")

# Export all the classes and functions with the same interface
__all__ = [
    'Settings',
    'ByPoint', 
    'RecoveryWindow',
    'RecoveryWindowResult',
    'RecoveryWindowFailure',
    'RecoveryWindowSuccess', 
    'RecoveryWindowResultV2',
    'FlatternRecoveryWindowResultV2',
    'from_recovery_window_result_v2',
    'HL',
    'calculate_weighted_hl_value',
    'swap_hl',
    'VipHL'
] 