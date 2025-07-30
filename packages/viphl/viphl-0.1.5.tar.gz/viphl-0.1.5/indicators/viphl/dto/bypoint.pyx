# cython: language_level=3
# distutils: language = c++

cdef class ByPoint:
    cdef public int n
    cdef public int m
    cdef public double price
    cdef public double close_at_pivot
    cdef public int bar_index_at_pivot
    cdef public int bar_time_at_pivot
    cdef public bint is_high
    cdef public bint is_trending
    cdef public bint used
    cdef public double close_avg_percent

    def __init__(self, int n, int m, double price, double close_at_pivot,
                 int bar_index_at_pivot, int bar_time_at_pivot, bint is_high,
                 bint is_trending, bint used, double close_avg_percent=0.0):
        self.n = n
        self.m = m
        self.price = price
        self.close_at_pivot = close_at_pivot
        self.bar_index_at_pivot = bar_index_at_pivot
        self.bar_time_at_pivot = bar_time_at_pivot
        self.is_high = is_high
        self.is_trending = is_trending
        self.used = used
        self.close_avg_percent = close_avg_percent

    def copy(self):
        return ByPoint(
            self.n, self.m, self.price, self.close_at_pivot,
            self.bar_index_at_pivot, self.bar_time_at_pivot,
            self.is_high, self.is_trending, self.used, self.close_avg_percent
        ) 