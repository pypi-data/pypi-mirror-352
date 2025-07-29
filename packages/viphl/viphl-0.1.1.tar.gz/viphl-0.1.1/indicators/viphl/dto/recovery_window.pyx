# cython: language_level=3
# distutils: language = c++

cdef class RecoveryWindow:
    cdef public double break_hl_at_price
    cdef public int break_hl_at_bar_index
    cdef public int recover_at_bar_index
    cdef public int break_hl_extend_bar_cross
    cdef public int bar_count_close_above_hl
    cdef public int vip_by_point_count
    cdef public bint recovered

    def __init__(self, double break_hl_at_price, int break_hl_at_bar_index,
                 recover_at_bar_index=None, int break_hl_extend_bar_cross=0,
                 int bar_count_close_above_hl=0, int vip_by_point_count=0):
        self.break_hl_at_price = break_hl_at_price
        self.break_hl_at_bar_index = break_hl_at_bar_index
        self.recover_at_bar_index = -1 if recover_at_bar_index is None else recover_at_bar_index
        self.break_hl_extend_bar_cross = break_hl_extend_bar_cross
        self.bar_count_close_above_hl = bar_count_close_above_hl
        self.vip_by_point_count = vip_by_point_count
        self.recovered = False

    def copy(self):
        result = RecoveryWindow(
            self.break_hl_at_price, self.break_hl_at_bar_index,
            self.recover_at_bar_index, self.break_hl_extend_bar_cross,
            self.bar_count_close_above_hl, self.vip_by_point_count
        )
        result.recovered = self.recovered
        return result

cdef class RecoveryWindowResult:
    cdef public bint has_signal
    cdef public bint close_above_low_and_hl
    cdef public bint violate_extend_bar_cross
    cdef public bint violate_recover_window
    cdef public bint violate_signal_window
    cdef public bint violate_search_range_close_above_bar_count
    cdef public RecoveryWindow recovery_window

    def __init__(self, bint has_signal=False, bint close_above_low_and_hl=False, 
                 bint violate_extend_bar_cross=False, bint violate_recover_window=False,
                 bint violate_signal_window=False, bint violate_search_range_close_above_bar_count=False,
                 RecoveryWindow recovery_window=None):
        self.has_signal = has_signal
        self.close_above_low_and_hl = close_above_low_and_hl
        self.violate_extend_bar_cross = violate_extend_bar_cross
        self.violate_recover_window = violate_recover_window
        self.violate_signal_window = violate_signal_window
        self.violate_search_range_close_above_bar_count = violate_search_range_close_above_bar_count
        self.recovery_window = recovery_window

cdef class RecoveryWindowFailure:
    cdef public bint close_above_low_and_hl
    cdef public bint violate_extend_bar_cross
    cdef public bint violate_recover_window
    cdef public bint violate_signal_window
    cdef public bint violate_search_range_close_above_bar_count
    cdef public RecoveryWindow recovery_window

    def __init__(self, bint close_above_low_and_hl=False, 
                 bint violate_extend_bar_cross=False, bint violate_recover_window=False,
                 bint violate_signal_window=False, bint violate_search_range_close_above_bar_count=False,
                 RecoveryWindow recovery_window=None):
        self.close_above_low_and_hl = close_above_low_and_hl
        self.violate_extend_bar_cross = violate_extend_bar_cross
        self.violate_recover_window = violate_recover_window
        self.violate_signal_window = violate_signal_window
        self.violate_search_range_close_above_bar_count = violate_search_range_close_above_bar_count
        self.recovery_window = recovery_window

cdef class RecoveryWindowSuccess:
    cdef public bint has_signal
    cdef public bint is_vvip_signal
    cdef public RecoveryWindow recovery_window

    def __init__(self, bint has_signal=False, bint is_vvip_signal=False, RecoveryWindow recovery_window=None):
        self.has_signal = has_signal
        self.is_vvip_signal = is_vvip_signal
        self.recovery_window = recovery_window

cdef class RecoveryWindowResultV2:
    cdef public RecoveryWindowSuccess success
    cdef public RecoveryWindowFailure failure

    def __init__(self, RecoveryWindowSuccess success=None, RecoveryWindowFailure failure=None):
        self.success = success
        self.failure = failure

cdef class FlatternRecoveryWindowResultV2:
    cdef public bint has_signal
    cdef public bint is_vvip_signal
    cdef public bint close_above_low_and_hl
    cdef public bint violate_extend_bar_cross
    cdef public bint violate_recover_window
    cdef public bint violate_signal_window
    cdef public bint violate_search_range_close_above_bar_count
    cdef public double break_hl_at_price
    cdef public int break_hl_at_bar_index
    cdef public int recover_at_bar_index
    cdef public int break_hl_extend_bar_cross
    cdef public int bar_count_close_above_hl
    cdef public int vip_by_point_count
    cdef public bint is_hl_satisfied
    cdef public bint is_non_vvip_signal
    cdef public bint no_signal_but_close_above
    cdef public bint violate_extended_bar_cross

    def __init__(self, bint has_signal=False, bint is_vvip_signal=False, bint close_above_low_and_hl=False,
                 bint violate_extend_bar_cross=False, bint violate_recover_window=False, bint violate_signal_window=False,
                 bint violate_search_range_close_above_bar_count=False, double break_hl_at_price=0.0,
                 int break_hl_at_bar_index=0, int recover_at_bar_index=0, int break_hl_extend_bar_cross=0,
                 int bar_count_close_above_hl=0, int vip_by_point_count=0, bint is_hl_satisfied=False,
                 bint is_non_vvip_signal=False, bint no_signal_but_close_above=False,
                 bint violate_extended_bar_cross=False):
        self.has_signal = has_signal
        self.is_vvip_signal = is_vvip_signal
        self.close_above_low_and_hl = close_above_low_and_hl
        self.violate_extend_bar_cross = violate_extend_bar_cross
        self.violate_recover_window = violate_recover_window
        self.violate_signal_window = violate_signal_window
        self.violate_search_range_close_above_bar_count = violate_search_range_close_above_bar_count
        self.break_hl_at_price = break_hl_at_price
        self.break_hl_at_bar_index = break_hl_at_bar_index
        self.recover_at_bar_index = recover_at_bar_index
        self.break_hl_extend_bar_cross = break_hl_extend_bar_cross
        self.bar_count_close_above_hl = bar_count_close_above_hl
        self.vip_by_point_count = vip_by_point_count
        self.is_hl_satisfied = is_hl_satisfied
        self.is_non_vvip_signal = is_non_vvip_signal
        self.no_signal_but_close_above = no_signal_but_close_above
        self.violate_extended_bar_cross = violate_extended_bar_cross

def from_recovery_window_result_v2(result):
    flattened = FlatternRecoveryWindowResultV2()
    
    flattened.break_hl_at_price = -1
    flattened.is_hl_satisfied = False
    flattened.is_vvip_signal = False
    flattened.is_non_vvip_signal = False
    flattened.no_signal_but_close_above = False
    flattened.violate_extended_bar_cross = False
    flattened.violate_search_range_close_above_bar_count = False
    flattened.violate_recover_window = False
    flattened.violate_signal_window = False
    
    if result.success is not None:
        flattened.has_signal = result.success.has_signal
        flattened.is_vvip_signal = result.success.is_vvip_signal
        flattened.is_hl_satisfied = result.success.has_signal
        flattened.is_non_vvip_signal = result.success.has_signal and not result.success.is_vvip_signal
        
        if result.success.recovery_window is not None:
            flattened.break_hl_at_price = result.success.recovery_window.break_hl_at_price
            flattened.break_hl_at_bar_index = result.success.recovery_window.break_hl_at_bar_index
            flattened.recover_at_bar_index = result.success.recovery_window.recover_at_bar_index
            flattened.break_hl_extend_bar_cross = result.success.recovery_window.break_hl_extend_bar_cross
            flattened.bar_count_close_above_hl = result.success.recovery_window.bar_count_close_above_hl
            flattened.vip_by_point_count = result.success.recovery_window.vip_by_point_count
    
    elif result.failure is not None:
        flattened.close_above_low_and_hl = result.failure.close_above_low_and_hl
        flattened.violate_extend_bar_cross = result.failure.violate_extend_bar_cross
        flattened.violate_recover_window = result.failure.violate_recover_window
        flattened.violate_signal_window = result.failure.violate_signal_window
        flattened.violate_search_range_close_above_bar_count = result.failure.violate_search_range_close_above_bar_count
        
        flattened.no_signal_but_close_above = result.failure.close_above_low_and_hl
        flattened.violate_extended_bar_cross = result.failure.violate_extend_bar_cross
        
        if result.failure.recovery_window is not None:
            flattened.break_hl_at_price = result.failure.recovery_window.break_hl_at_price
            flattened.break_hl_at_bar_index = result.failure.recovery_window.break_hl_at_bar_index
            flattened.recover_at_bar_index = result.failure.recovery_window.recover_at_bar_index
            flattened.break_hl_extend_bar_cross = result.failure.recovery_window.break_hl_extend_bar_cross
            flattened.bar_count_close_above_hl = result.failure.recovery_window.bar_count_close_above_hl
            flattened.vip_by_point_count = result.failure.recovery_window.vip_by_point_count
    
    return flattened 