# cython: language_level=3
# distutils: language = c++

cdef class Settings:
    cdef public int high_by_point_n
    cdef public int high_by_point_m
    cdef public int low_by_point_n
    cdef public int low_by_point_m
    cdef public int high_by_point_n_on_trend
    cdef public int high_by_point_m_on_trend
    cdef public int low_by_point_n_on_trend
    cdef public int low_by_point_m_on_trend
    cdef public int bar_count_to_by_point
    cdef public int bar_cross_threshold
    cdef public int hl_length_threshold
    cdef public double hl_overlap_ca_percent_multiplier
    cdef public bint only_body_cross
    cdef public int last_by_point_weight
    cdef public int second_last_by_point_weight
    cdef public int by_point_weight
    cdef public int hl_extend_bar_cross_threshold
    cdef public bint draw_from_recent
    cdef public bint allow_reuse_by_point
    cdef public bint debug
    cdef public int debug_start_time
    cdef public int debug_end_time
    cdef public double debug_start_price
    cdef public double debug_end_price

    def __init__(self, 
                 int high_by_point_n=10,
                 int high_by_point_m=10,
                 int low_by_point_n=8,
                 int low_by_point_m=8,
                 int high_by_point_n_on_trend=5,
                 int high_by_point_m_on_trend=5,
                 int low_by_point_n_on_trend=4,
                 int low_by_point_m_on_trend=4,
                 int bar_count_to_by_point=700,
                 int bar_cross_threshold=5,
                 int hl_length_threshold=300,
                 double hl_overlap_ca_percent_multiplier=1.5,
                 bint only_body_cross=True,
                 int last_by_point_weight=3,
                 int second_last_by_point_weight=2,
                 int by_point_weight=1,
                 int hl_extend_bar_cross_threshold=0,
                 bint draw_from_recent=True,
                 bint allow_reuse_by_point=False,
                 bint debug=False,
                 int debug_start_time=0,
                 int debug_end_time=0,
                 double debug_start_price=0.0,
                 double debug_end_price=0.0):
        self.high_by_point_n = high_by_point_n
        self.high_by_point_m = high_by_point_m
        self.low_by_point_n = low_by_point_n
        self.low_by_point_m = low_by_point_m
        self.high_by_point_n_on_trend = high_by_point_n_on_trend
        self.high_by_point_m_on_trend = high_by_point_m_on_trend
        self.low_by_point_n_on_trend = low_by_point_n_on_trend
        self.low_by_point_m_on_trend = low_by_point_m_on_trend
        self.bar_count_to_by_point = bar_count_to_by_point
        self.bar_cross_threshold = bar_cross_threshold
        self.hl_length_threshold = hl_length_threshold
        self.hl_overlap_ca_percent_multiplier = hl_overlap_ca_percent_multiplier
        self.only_body_cross = only_body_cross
        self.last_by_point_weight = last_by_point_weight
        self.second_last_by_point_weight = second_last_by_point_weight
        self.by_point_weight = by_point_weight
        self.hl_extend_bar_cross_threshold = hl_extend_bar_cross_threshold
        self.draw_from_recent = draw_from_recent
        self.allow_reuse_by_point = allow_reuse_by_point
        self.debug = debug
        self.debug_start_time = debug_start_time
        self.debug_end_time = debug_end_time
        self.debug_start_price = debug_start_price
        self.debug_end_price = debug_end_price 