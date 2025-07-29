import math

import backtrader as bt

from typing import List

from indicators.helper.close_average import CloseAveragePercent
from dto.horizontal_line import HorizontalLine, HLScoreParam
from indicators.helper.pivot_high import PivotHigh
from indicators.helper.pivot_low import PivotLow


def swap(x, y, horizontal_line_array):
    horizontal_line_array[x], horizontal_line_array[y] = horizontal_line_array[y], horizontal_line_array[x]


class HLv4:
    lines = ('is_hl_satisfied', 'cur_sr_value')
    params = (
        # ----------hl input------------
        ('lookback', 500),
        ('max_num_sr', 50),
        ('month_period1', 3),
        ('month_period2', 6),
        ('month_period3', 12),
        ('month_period4', 24),

        # --------hl pt weight----------
        ('first_weight_multiplier', 1.25),  # The closest by-point weight multiplier
        ('second_weight_multiplier', 1.25),  # The second closest by-point weight multiplier
        ('pt_weight1', 4.0),  # Weights for by-points, in order from nearest to furthest
        ('pt_weight2', 2.0),
        ('pt_weight3', 1.0),
        ('pt_weight4', 0.0),

        # ----------hl score input-------------
        ('toggle_hl_score', True),  # Toggle line importance scoring
        # For 'hlScoreCol', since Backtrader doesn't natively support color for indicators' visual representation,
        # you might handle it in custom plotting logic or documentation.
        ('hl_score_col', '#d4aa00'),  # Placeholder for color, might need custom handling for plotting
        ('hl_score_size', 'normal'),  # Placeholder for size, can be managed with custom plotting logic

        # --------close average pt inputs------
        ('close_avg_percent_lookback', 500),  # Lookback period for close average calculation
        ('toggle_pp_threshold_overwrite', False),  # Overwrite threshold percentage for by-points
        ('pp_threshold_overwrite', 0.25),  # Threshold percentage for by-points
        ('default_ca_threshold_multiplier_his', 2.0),  # Default historical CA% multiplier
        ('default_ca_threshold_multiplier_pre', 1.0),  # Default present CA% multiplier

        # ---------entry point inputs-------
        ('entry_point_hl_threshold', 0.0),  # Minimum CA% for a bar to be considered stable on HL
        ('pullback_threshold', 0.5),  # Minimum CA% for a low pullback to approach HL
    )

    bar_index: int = 0
    last_bar_index: int = 0
    close: float = 0
    open: float = 0
    high: float = 0
    low: float = 0
    within_lookback_period: bool = False

    level_ph_loc: List[int] = []
    level_ph_imp: List[float] = []
    level_pl_loc: List[int] = []
    level_pl_imp: List[float] = []
    pivot_vals: List[float] = []
    pivot_locs: List[float] = []
    pivot_is_high: List[bool] = []
    horizontal_lines: List[HorizontalLine] = []
    lines_info = []
    rightBars = 2
    leftBars = 2

    ph: float = 0
    pl: float = 0
    levelh1: float = 0
    levelh2: float = 0
    levelh3: float = 0
    levelh4: float = 0
    levell1: float = 0
    levell2: float = 0
    levell3: float = 0
    levell4: float = 0
    close_average_percent: float = 0

    def __init__(self):
        self.cur_sr_value = None
        self.is_hl_satisfied = None
        self.first_weight_multiplier = None
        self.pt_weight1 = None
        self.pt_weight2 = None
        self.pt_weight3 = None
        self.pt_weight4 = None
        self.pp_threshold_overwrite = None
        self.month_period1 = None
        self.month_period2 = None
        self.month_period3 = None
        self.month_period4 = None
        self.toggle_pp_threshold_overwrite = None
        self.default_ca_threshold_multiplier_pre = None
        self.default_ca_threshold_multiplier_his = None
        self.entry_point_hl_threshold = None
        self.pullback_threshold = None
        self.lookback = None

    def refresh_required_data(self, bar_index, last_bar_index, close, open_val, high, low, within_lookback_period,):
        self.bar_index = bar_index
        self.last_bar_index = last_bar_index
        self.close = close
        self.open = open_val
        self.high = high
        self.low = low
        self.within_lookback_period = within_lookback_period

    def next(self, bar_index, last_bar_index, close, open_val, high, low, within_lookback_period):
        self.refresh_required_data(bar_index, last_bar_index, close, open_val, high, low, within_lookback_period)
        self.get_hl()

    def get_hl(self):
        # Check if the current bar index is within the specified range
        self.horizontal_lines = []
        close_average_percent = self.close_average_percent
        self.calculate_all_hl(close_average_percent, self.pivot_vals, self.pivot_locs, self.horizontal_lines,
                              self.pivot_is_high)

        if not math.isnan(self.ph) or not math.isnan(self.pl):
            if self.bar_index >= (self.bar_index - self.lookback - self.month_period4 * 20):
                # If both pp on the same line, update both
                if not math.isnan(self.ph):
                    self.pivot_vals.append(self.ph)
                    self.pivot_is_high.append(True)
                    self.pivot_locs.append(self.bar_index - self.rightBars)
                if not math.isnan(self.pl):
                    self.pivot_vals.append(self.pl)
                    self.pivot_is_high.append(False)
                    self.pivot_locs.append(self.bar_index - self.rightBars)

        do_remove = False
        if len(self.pivot_vals) > 0:
            if (self.bar_index - self.pivot_locs[0]) > self.month_period4 * 20:
                do_remove = True

        while do_remove:
            self.pivot_vals.pop(0)  # Removes the first element from 'pivotvals'
            self.pivot_locs.pop(0)  # Removes the first element from 'pivotlocs'
            self.pivot_is_high.pop(0)  # Removes the first element from 'pivotIsHigh'

            if len(self.pivot_vals) > 0:
                if (self.bar_index - self.pivot_locs[0]) > self.month_period4 * 20:
                    continue
            do_remove = False

        if self.bar_index >= (self.bar_index - self.lookback - self.month_period4 * 20):

            # High points significance calculation
            high_levels = [(self.levelh4, 2), (self.levelh3, 5), (self.levelh2, 10), (self.levelh1, 20)]
            for level, offset in high_levels:
                if not math.isnan(level):  # Equivalent to not na(level)
                    index = self.bar_index - offset  # Adjusted as per Pine Script's self.bar_index[x]
                    if index in self.level_ph_loc:
                        i = self.level_ph_loc.index(index)
                        self.level_ph_imp[i] = high_levels.index((level, offset)) + 1
                    else:
                        self.level_ph_loc.append(index)
                        self.level_ph_imp.append(high_levels.index((level, offset)) + 1)

            # Low points significance calculation
            low_levels = [(self.levell4, 2), (self.levell3, 5), (self.levell2, 10), (self.levell1, 20)]
            for level, offset in low_levels:
                if not math.isnan(level):  # Equivalent to not na(level)
                    index = self.bar_index - offset  # Adjusted as per Pine Script's self.bar_index[x]
                    if index in self.level_pl_loc:
                        i = self.level_pl_loc.index(index)
                        self.level_pl_imp[i] = low_levels.index((level, offset)) + 1
                    else:
                        self.level_pl_loc.append(index)
                        self.level_pl_imp.append(low_levels.index((level, offset)) + 1)

        if not math.isnan(self.ph) or not math.isnan(self.pl):
            if self.within_lookback_period:
                # Clear the list to reinitialize HL
                self.horizontal_lines.clear()

                # Recalculate all HL
                self.calculate_all_hl(close_average_percent, self.pivot_vals, self.pivot_locs, self.horizontal_lines,
                                      self.pivot_is_high)

                # Sort based on strength (end bar index of HL), using a simple sort algorithm (e.g., bubble sort for demonstration)
                hl_size = len(self.horizontal_lines)
                for x in range(hl_size - 1):
                    for y in range(x + 1, hl_size):
                        line_x = self.horizontal_lines[x]
                        line_y = self.horizontal_lines[y]
                        if line_y.hl_sr_end_bar_index > line_x.hl_sr_end_bar_index:
                            swap(x, y, self.horizontal_lines)

        is_hl_supported = False
        cur_sr_value = 0.0
        hl_size = len(self.horizontal_lines)
        hl_end_index = hl_size - 1 if hl_size > 0 else None

        if hl_end_index is not None and self.within_lookback_period:
            for y in range(hl_end_index + 1):
                each_hl = self.horizontal_lines[y]
                cur_sr_value = each_hl.hl_sr_value
                if math.isnan(cur_sr_value):
                    continue

                # Assuming `low`, `close`, and other relevant data are accessible as lists or through a data structure
                # for the current and previous bar (index -1).
                low_below_hl = (self.low < cur_sr_value * (
                        1 + 0.01 * close_average_percent * self.pullback_threshold) or self.low
                                < cur_sr_value * (1 + 0.01 * close_average_percent * self.pullback_threshold))
                close_above_hl = self.close > cur_sr_value * (
                        1 + close_average_percent * 0.01 * self.entry_point_hl_threshold)
                if low_below_hl and close_above_hl:
                    is_hl_supported = True
                    break

        if self.last_bar_index == self.bar_index:
            hl_size = len(self.horizontal_lines)
            for x in range(hl_size - 1):  # Adjusted range to ensure Pythonic zero-based indexing
                for y in range(x + 1, hl_size):
                    line_x = self.horizontal_lines[x]
                    line_y = self.horizontal_lines[y]
                    level_x = line_x.hl_sr_accum_value / line_x.hl_sr_by_point_weighted_count if line_x.hl_sr_by_point_weighted_count > 0 else 0
                    level_y = line_y.hl_sr_accum_value / line_y.hl_sr_by_point_weighted_count if line_y.hl_sr_by_point_weighted_count > 0 else 0
                    if level_y > level_x:
                        swap(x, y, self.horizontal_lines)

            for hl in self.horizontal_lines:
                self.lines_info.append((hl.hl_sr_value, hl.hl_sr_start_bar_index, hl.hl_sr_end_bar_index + 3))

        self.is_hl_satisfied = 1 if is_hl_supported else -1
        self.cur_sr_value = cur_sr_value

    def calculate_all_hl(self,
                         close_avg_percent: float,
                         cur_pivot_vals: List[float],
                         cur_pivot_locs: List[float],
                         cur_horizontal_line: List[HorizontalLine],
                         cur_pivot_is_high: List[bool]
                         ):
        pp_size = len(cur_pivot_vals)
        # Resetting scores to prevent duplicate calculations
        for cur_line in cur_horizontal_line:
            cur_line.hl_sr_score_info.point_score = 0.0
            cur_line.hl_sr_accum_value = 0.0
            cur_line.hl_sr_by_point_weighted_count = 0
            cur_line.hl_sr_by_point_count1 = 0
            cur_line.hl_sr_by_point_count2 = 0
        # Iterating through pivot points to update or create SR levels
        for x in range(pp_size):
            # Assuming update_or_create_sr is a function defined elsewhere in your Python code.
            self.update_or_create_sr(pp_size - 1 - x, close_avg_percent, cur_pivot_vals, cur_pivot_locs,
                                     cur_horizontal_line, cur_pivot_is_high)

    def update_or_create_sr(self,
                            index,
                            close_avg_percent,
                            cur_pivot_vals,
                            cur_pivot_locs,
                            horizontal_line_array,
                            cur_pivot_is_high
                            ):
        threshold = close_avg_percent * self.default_ca_threshold_multiplier_his

        # Initially, assume current pivot point as the start of a new HL
        sr_value = cur_pivot_vals[index]
        sr_start_bar_index = cur_pivot_locs[index]
        sr_end_bar_index = cur_pivot_locs[index]
        sr_is_high = cur_pivot_is_high[index]

        new_hl = True

        if self.bar_index - sr_start_bar_index <= self.month_period3 * 20:
            threshold = close_avg_percent * self.default_ca_threshold_multiplier_pre
        if self.toggle_pp_threshold_overwrite:
            threshold = self.pp_threshold_overwrite

        # Next, look all HL and check if found any close one, and update HL starting point
        for cur_line in horizontal_line_array:
            if cur_line.overlap(threshold, sr_value):
                new_hl = False
                if sr_is_high:
                    cur_line.hl_sr_score_info.has_high = True
                    self.renew_hl_score(cur_line, int(sr_end_bar_index), sr_value, self.level_ph_imp, self.level_ph_loc)
                else:
                    cur_line.hl_sr_score_info.has_low = True
                    self.renew_hl_score(cur_line, int(sr_end_bar_index), sr_value, self.level_pl_imp, self.level_pl_loc)

        if new_hl:
            new_line = HorizontalLine(float('nan'), sr_start_bar_index, sr_end_bar_index, 0.0, 0, 0, 0.0,
                                      HLScoreParam(), 0.0)
            if sr_is_high:
                new_line.hl_sr_score_info.has_high = True
                self.renew_hl_score(new_line, int(sr_end_bar_index), sr_value, self.level_ph_imp, self.level_ph_loc)
            else:
                new_line.hl_sr_score_info.has_low = True
                self.renew_hl_score(new_line, int(sr_end_bar_index), sr_value, self.level_pl_imp, self.level_pl_loc)

            if new_line.hl_sr_by_point_weighted_count > 0:
                horizontal_line_array.append(new_line)

    def renew_hl_score(self, cur_line, point_bar_index, point_value, level_score, level_loc):
        cur_sr_score = 0.0
        point_score = 0.0
        point_ind = -1

        # -----renew line score------
        # step 1
        try:
            point_ind = level_loc.index(point_bar_index)
            point_score = level_score[point_ind] if point_ind >= 0 else 0.0
        except ValueError:
            point_score = 0.0

        if self.bar_index - point_bar_index <= self.month_period1 * 20:
            pass  # point_score remains unchanged
        elif self.bar_index - point_bar_index <= self.month_period2 * 20:
            point_score *= 0.75
        elif self.bar_index - point_bar_index <= self.month_period3 * 20:
            point_score *= 0.5
        elif self.bar_index - point_bar_index <= self.month_period4 * 20 and point_score >= 2:
            point_score *= 0.3
        else:
            point_score = 0

        cur_line.hl_sr_score_info.point_score += point_score

        if point_score > 0 and cur_line.hl_sr_start_bar_index > point_bar_index:
            cur_line.hl_sr_start_bar_index = point_bar_index
        cur_sr_timeframe = cur_line.hl_sr_end_bar_index - cur_line.hl_sr_start_bar_index

        # step 2
        if 20 < cur_sr_timeframe <= 60:
            cur_sr_score = 2
        elif 60 < cur_sr_timeframe <= 120:
            cur_sr_score = 4
        elif cur_sr_timeframe > 120:
            cur_sr_score = 6

        # step 3
        cur_sr_score += cur_line.hl_sr_score_info.point_score
        if cur_line.hl_sr_score_info.has_high and cur_line.hl_sr_score_info.has_low:
            cur_sr_score *= 1.3

        cur_line.hl_sr_score = cur_sr_score

        # for display only
        if self.bar_index - point_bar_index <= self.month_period3 * 20:
            cur_line.hl_sr_by_point_count1 += 1
        elif point_score != 0:
            cur_line.hl_sr_by_point_count2 += 1

        # -----renew line price-----
        weighted_value = point_value * self.pt_weight4
        weighted_count = self.pt_weight4
        if self.bar_index - point_bar_index <= self.month_period1 * 20:
            multiplier = self.first_weight_multiplier if cur_line.hl_sr_by_point_count1 == 1 else self.first_weight_multiplier if cur_line.hl_sr_by_point_count1 == 2 else 1
            weighted_value = point_value * self.pt_weight1 * multiplier
            weighted_count = self.pt_weight1 * multiplier
        elif self.bar_index - point_bar_index <= self.month_period2 * 20:
            weighted_value = point_value * self.pt_weight2
            weighted_count = self.pt_weight2
        elif self.bar_index - point_bar_index <= self.month_period3 * 20:
            weighted_value = point_value * self.pt_weight3
            weighted_count = self.pt_weight3

        cur_line.hl_sr_accum_value += weighted_value
        cur_line.hl_sr_by_point_weighted_count += weighted_count
        cur_line.hl_sr_value = cur_line.hl_sr_accum_value / cur_line.hl_sr_by_point_weighted_count if cur_line.hl_sr_by_point_weighted_count > 0 else float(
            'nan')
