# cython: language_level=3
# distutils: language = c++

import math
from libc.math cimport isnan, fabs
from backtrader import DataSeries
from indicators.common.base_indicator import BaseIndicator

cdef double _calculate_weighted_hl_value(double last_hl_value, double last_by_point_value, 
                                double second_last_by_point_value, double by_point_values_except_last_two, 
                                int last_by_point_weight, int second_last_by_point_weight, 
                                int by_point_weight, int backward=True):
    cdef double total_weight = last_by_point_weight + second_last_by_point_weight + by_point_weight
    cdef double numerator = (last_by_point_value * last_by_point_weight + 
                           second_last_by_point_value * second_last_by_point_weight + 
                           by_point_values_except_last_two * by_point_weight)
    return numerator / total_weight

# Python accessible version
def calculate_weighted_hl_value(last_hl_value, last_by_point_value, 
                               second_last_by_point_value, by_point_values_except_last_two, 
                               last_by_point_weight, second_last_by_point_weight, 
                               by_point_weight, backward=True):
    return _calculate_weighted_hl_value(last_hl_value, last_by_point_value, 
                                     second_last_by_point_value, by_point_values_except_last_two, 
                                     last_by_point_weight, second_last_by_point_weight, 
                                     by_point_weight, backward)

cdef swap(hl1, hl2):
    tmp = hl1
    hl1 = hl2
    hl2 = tmp
    return hl1, hl2

# Python accessible version
def swap_hl(hl1, hl2):
    return swap(hl1, hl2)

cdef class HL:
    cdef public int start_bar_index
    cdef public int end_bar_index
    cdef public int start_time
    cdef public int end_time
    cdef public double hl_value
    cdef public double hl_accum_value
    cdef public list by_point_values
    cdef public double close_avg_percent
    cdef public list close
    cdef public list open
    cdef public list high
    cdef public list low
    cdef public int bar_index
    cdef public list time
    cdef public int last_bar_index
    cdef public double mintick
    cdef public bint extended
    cdef public int extend_end_bar_index
    cdef public bint historical_extend_bar_crosses_checked
    cdef public int post_extend_end_bar_index
    cdef public int bar_crosses
    cdef public int bar_crosses_post_extend
    cdef public bint violated

    def __init__(self, int start_bar_index, int end_bar_index, int start_time, int end_time,
                 double hl_value, double hl_accum_value, list by_point_values,
                 double close_avg_percent, list close, list open, list high, list low,
                 int bar_index, list time, int last_bar_index, double mintick):
        self.start_bar_index = start_bar_index
        self.end_bar_index = end_bar_index
        self.start_time = start_time
        self.end_time = end_time
        self.hl_value = hl_value
        self.hl_accum_value = hl_accum_value
        self.by_point_values = by_point_values
        self.close_avg_percent = close_avg_percent
        self.close = close
        self.open = open
        self.high = high
        self.low = low
        self.bar_index = bar_index
        self.time = time
        self.last_bar_index = last_bar_index
        self.mintick = mintick
        self.extended = False
        self.extend_end_bar_index = 0
        self.historical_extend_bar_crosses_checked = False
        self.post_extend_end_bar_index = 0
        self.bar_crosses = 0
        self.bar_crosses_post_extend = 0
        self.violated = False

    def round_to_mintick(self, double price):
        return round(price / self.mintick) * self.mintick

    def overlap(self, hl, double overlap_threshold):
        return fabs(self.hl_value - hl.hl_value) <= self.hl_value * self.close_avg_percent * 0.01 * overlap_threshold

    def is_hl_bar_crosses_violated(self, int bar_cross_threshold):
        return self.bar_crosses > bar_cross_threshold

    def is_hl_length_passed(self, int hl_length_threshold):
        return fabs(self.end_bar_index - self.start_bar_index) < hl_length_threshold

    def is_hl_bar_crosses_violated_if_merged(self, hl, int bar_cross_threshold,
                                            int last_by_point_weight, int second_last_by_point_weight,
                                            int by_point_weight, int orig_hl_bar_crosses):
        # Variable declarations at the beginning
        cdef int by_point_values_size = len(self.by_point_values)
        cdef double merged_hl_value = 0.0
        cdef double sum_values_except_last_two = 0.0
        cdef int count_values_except_last_two = 0
        cdef double avg_values_except_last_two = 0.0
        cdef int merged_bar_crosses = 0
        cdef int bar_count_to_loop = 0
        cdef int bar_y = 0
        cdef double ohlc_min_y = 0.0
        cdef double ohlc_max_y = 0.0
        cdef int i = 0
        
        if by_point_values_size == 0:
            merged_hl_value = hl.hl_value
        elif by_point_values_size == 1:
            merged_hl_value = _calculate_weighted_hl_value(
                hl.hl_value, self.by_point_values[0], 0.0, 0.0,
                last_by_point_weight, second_last_by_point_weight, by_point_weight
            )
        elif by_point_values_size == 2:
            merged_hl_value = _calculate_weighted_hl_value(
                hl.hl_value, self.by_point_values[0], self.by_point_values[1], 0.0,
                last_by_point_weight, second_last_by_point_weight, by_point_weight
            )
        else:
            # Calculate average of all except last two
            sum_values_except_last_two = 0.0
            count_values_except_last_two = by_point_values_size - 2
            
            for i in range(2, by_point_values_size):
                sum_values_except_last_two += self.by_point_values[i]
            
            avg_values_except_last_two = sum_values_except_last_two / count_values_except_last_two
            
            merged_hl_value = _calculate_weighted_hl_value(
                hl.hl_value, self.by_point_values[0], self.by_point_values[1], avg_values_except_last_two,
                last_by_point_weight, second_last_by_point_weight, by_point_weight
            )
        
        # For all historical bars, count bar crosses if merged with the new HL value
        merged_bar_crosses = 0
        bar_count_to_loop = self.bar_index - hl.end_bar_index
        
        for bar_y in range(min(bar_count_to_loop, hl.end_bar_index - hl.start_bar_index), 0, -1):
            # Handle LineBuffer objects by checking if they support indexing
            try:
                close_val = self.close[-bar_y]
                open_val = self.open[-bar_y]
                high_val = self.high[-bar_y]
                low_val = self.low[-bar_y]
                
                ohlc_min_y = min(close_val, open_val, high_val, low_val)
                ohlc_max_y = max(close_val, open_val, high_val, low_val)
                
                if ohlc_min_y < merged_hl_value < ohlc_max_y:
                    merged_bar_crosses += 1
            except (TypeError, IndexError):
                # Skip if we can't access the data properly
                continue
        
        # Add original crosses to the merged ones
        merged_bar_crosses += orig_hl_bar_crosses
        
        # Check if the merged crosses exceed the threshold
        return merged_bar_crosses > bar_cross_threshold

    def is_hl_length_passed_if_merged(self, hl, int hl_length_threshold):
        cdef int merged_hl_length = abs(max(self.end_bar_index, hl.end_bar_index) - min(self.start_bar_index, hl.start_bar_index))
        return merged_hl_length < hl_length_threshold

    def merge(self, hl, int last_by_point_weight, int second_last_by_point_weight, int by_point_weight, bint backward=True):
        # Variable declarations at the beginning
        cdef int by_point_values_size
        cdef double sum_values_except_last_two
        cdef int count_values_except_last_two
        cdef double avg_values_except_last_two
        cdef int i
        
        # Set the new bar indices and times for the merged HL
        if self.start_bar_index > hl.start_bar_index:
            self.start_bar_index = hl.start_bar_index
            self.start_time = hl.start_time
        
        if self.end_bar_index < hl.end_bar_index:
            self.end_bar_index = hl.end_bar_index
            self.end_time = hl.end_time
        
        # Add the by_point_values from the other HL
        if backward:
            # If backward is True, prepend the values
            self.by_point_values[:0] = hl.by_point_values
        else:
            # If backward is False, append the values
            self.by_point_values.extend(hl.by_point_values)
        
        # Calculate the new weighted HL value
        by_point_values_size = len(self.by_point_values)
        
        if by_point_values_size == 0:
            self.hl_value = 0.0
        elif by_point_values_size == 1:
            self.hl_value = self.by_point_values[0]
        elif by_point_values_size == 2:
            self.hl_value = (self.by_point_values[0] * last_by_point_weight + self.by_point_values[1] * second_last_by_point_weight) / (last_by_point_weight + second_last_by_point_weight)
        else:
            # Calculate average of all except last two
            sum_values_except_last_two = 0.0
            count_values_except_last_two = by_point_values_size - 2
            
            for i in range(2, by_point_values_size):
                sum_values_except_last_two += self.by_point_values[i]
            
            avg_values_except_last_two = sum_values_except_last_two / count_values_except_last_two
            
            self.hl_value = _calculate_weighted_hl_value(
                0.0, self.by_point_values[0], self.by_point_values[1], avg_values_except_last_two,
                last_by_point_weight, second_last_by_point_weight, by_point_weight
            )
        
        # Reset extension-related properties
        self.extended = False
        self.extend_end_bar_index = 0
        self.historical_extend_bar_crosses_checked = False
        self.post_extend_end_bar_index = 0
        self.bar_crosses = 0
        self.bar_crosses_post_extend = 0
        self.violated = False
        
        return self 