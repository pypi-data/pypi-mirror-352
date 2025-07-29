import copy
import math
from typing import List, Tuple

import backtrader as bt
from dto.diagonal_line import DiagonalLineWrapper, DiagonalLine, SignalWrapper
from indicators.helper.bar_pattern import close_at_bar_top_by_percent, greater_than_close_avg_by
from indicators.helper.close_average import CloseAveragePercent
from indicators.helper.percentile_nearest_rank import PercentileNearestRank
from indicators.helper.pivot_high import PivotHigh
from indicators.helper.pivot_low import PivotLow
from indicators.hl.hl_v4_indicator import HLv4Indicator


class DLv1_9Indicator(bt.Indicator):
    lines = ('two_by_zero_signal', 'buy_signal', 'dl_break_signal', 'is_two_by_zero_disabled_by_rsi',
             'is_two_by_zero_disabled_by_hl', 'is_two_by_zero_disabled_by_stop_loss', 'is_two_by_zero_disabled_by_high_close',
             'is_two_by_zero_triggered_by_rsi_override', 'is_buy_signal_disabled_by_rsi', 'is_buy_signal_disabled_by_stop_loss',
             'is_buy_signal_disabled_by_high_close', 'is_buy_signal_triggered_by_rsi_override', 'is_dl_break_disabled_by_rsi',
             'is_dl_break_disabled_by_stop_loss', 'is_dl_break_disabled_by_high_close', 'is_dl_break_triggered_by_rsi_override',
             'is_vip_dl_signal', 'is_key_bar_signal', 'is_low_t_rsi_signal', 'latest_rsi_long_threshold', 'rsi_at_signal',
             'maybe_buy_signal', 'maybe_two_by_zero_signal', 'maybe_dl_break_signal', 'bar_count_at_signal', 'deslope_score_at_signal',
             'dl_value_at_signal')

    params = (
        # inputs
        ('toggle_rsi', False),
        ('toggle_dl_by_score', True),
        ('toggle_short_dl', True),
        ('use_date_range', False),

        # nbym inputs
        ('left_bars', 2),
        ('right_bars', 2),

        # DL inputs
        ('lookback', 500),
        ('min_bar_count', 5),
        ('dl_break_threshold', 0.2),
        ('non_two_by_dl_break_threshold', 0.3),
        ('short_dl_break_threshold', 1.5),
        ('extended_cross_threshold', 2),
        ('extended_cross_uncross_threshold', 8),
        ('distance_to_a_prime_percent', 0.3),
        ('long_trend_threshold', 100),
        ('min_bar_count_on_trend', 4),
        ('dl_angle_up_limit', 75),
        ('ignore_open_price_bar_count', 7),

        # 2by0 DL settings
        ('strong_bar_multiplier', 1.5),
        ('close_top_percent', 45),
        ('signal_window_bar_count', 2),

        # harmony score
        ('deslope_score_threshold', 0.5),
        ('deslope_ca_multiplier', 0.45),

        # close average pt inputs
        ('close_avg_percent_lookback', 500),

        # low t-rsi adjustment
        ('toggle_low_trsi_adjustment', False),
        ('toggle_low_trsi_with_bar_count', False),
        ('low_trsi_to_hrsi_offset', 10),
        ('hrsi_cutoff_percent_on_low_trsi', 50),
        ('low_trsi_bar_count', 5),

        # Reduce chasing inputs
        ('toggle_reduce_chase', False),
        ('window_one_rsi_chase_offset', 5),
        ('window_one_stop_loss_chase_offset', 4),
        ('window_one_close_chase_offset', 2),
        ('window_two_rsi_chase_offset', 5),
        ('window_two_stop_loss_chase_offset', 4),
        ('window_two_close_chase_offset', 1),

        # New High RSI filter
        ('toggle_new_high_loose', False),
        ('prev_high_lookback', 20),
        ('bar_count_to_prev_high', 8),
        ('new_high_rsi_long_threshold', 75),
        ('new_high_window_one_rsi_offset', 0),
        ('new_high_window_two_rsi_offset', 0),

        # Top MA loose filter
        ('toggle_top_ma_loose', False),
        ('toggle_positive_ma_delta', True),
        ('toggle_top_ma_no_reduce_chase', True),
        ('ma10_top_pt', 15),
        ('ma40_top_pt', 20),
        ('top_ma_rsi_long_threshold', 75),
        ('top_ma_window_one_rsi_offset', 0),
        ('top_ma_window_two_rsi_offset', 0),

        # VIP DL
        ('toggle_vip_dl_loose', False),
        ('toggle_vip_dl_no_reduce_chase', False),
        ('vip_dl_bar_count', 4),
        ('vip_dl_score_limit', 0.15),
        ('vip_dl_multiplier', 0.020),
        ('vip_dl_rsi_offset', 5),

        # Key bar filters
        ('toggle_key_bar_loose', False),
        ('toggle_key_bar_no_reduce_chase', False),
        ('key_bar_t_bar_close_offset', 1),
        ('key_bar_dl_close_offset', 1),
        ('key_bar_close_top_percent', 25),
        ('key_bar_rsi_offset', 5),

        # VIP HL inputs
        ('toggle_vip_hl_loose', False),
        ('vip_hl_rsi_offset', 0),

        # MA trends inputs
        ('ma_lookback_period', 500),
        ('ma_length', 40),

        # RSI inputs
        ('rsi_length', 14),
        ('rsi_lookback', 1),
        ('rsi_long_threshold', 65),
    )

    dl_wrapper_array: List[DiagonalLineWrapper] = []
    dl_lines_info = []

    plotlines = dict(
        latest_rsi_long_threshold=dict(_plotskip=True),   # This line will not be plotted
        rsi_at_signal=dict(_plotskip=True),   # This line will be plotted
        bar_count_at_signal=dict(_plotskip=True),
        deslope_score_at_signal=dict(_plotskip=True)
    )

    def __init__(self, hlv4, viphl):
        self.hlv4 = hlv4
        self.viphl = viphl
        self.rsi = bt.ind.RSI(self.datas[0], period=self.p.rsi_length)
        self.rsi_highest = bt.ind.Highest(self.rsi, period=self.p.rsi_lookback)
        # self.rsi_is_high = self.rsi == self.rsi_highest
        self.ph = PivotHigh()
        self.pl = PivotLow()
        self.two_by_zero = PivotLow(leftbars=2, rightbars=0)
        self.two_by_one = PivotLow(leftbars=2, rightbars=1)
        self.two_by_two = PivotLow(leftbars=2, rightbars=2)
        self.close_average_percent = CloseAveragePercent(close_avg_percent_lookback=self.p.close_avg_percent_lookback)
        self.offset_to_local_high = bt.ind.FindLastIndexHighest(self.data.high, period=(self.p.bar_count_to_prev_high + 1))
        self.offset_to_local_high.plotinfo.plot = False

        self.ma = bt.indicators.SMA(self.data.close, period=self.p.ma_length)
        self.quick_ma = bt.indicators.SMA(self.data.close, period=10)
        self.ma_delta = bt.indicators.ROC(self.ma, period=1)
        self.quick_ma_delta = bt.indicators.ROC(self.quick_ma, period=1)
        self.ma_delta.plotinfo.plot = False
        self.quick_ma_delta.plotinfo.plot = False

        self.top_delta_bound = PercentileNearestRank(self.ma_delta.roc, period=self.p.ma_lookback_period,
                                                    percentile=100 - self.p.long_trend_threshold)

        # extreme uptrend
        self.quick_ma_super_low_delta_bound = PercentileNearestRank(self.quick_ma_delta.roc,
                                                                    period=self.p.ma_lookback_period,
                                                                    percentile=100 - self.p.ma10_top_pt)
        self.slow_ma_super_low_delta_bound = PercentileNearestRank(self.ma_delta.roc, period=self.p.ma_lookback_period,
                                                                   percentile=100 - self.p.ma40_top_pt)

    def next(self):
        '''
        below is equivalent to precalculation
        '''

        # Reduce chase filter
        window_one_offset: int = self.p.window_one_rsi_chase_offset if self.p.toggle_reduce_chase else 0
        window_two_offset: int = self.p.window_two_rsi_chase_offset if self.p.toggle_reduce_chase else 0

        # VIP HL loose filter
        should_loose_vip_hl: bool = self.p.toggle_vip_hl_loose
        vip_hl_rsi_long_threshold: int = self.p.rsi_long_threshold + self.p.vip_hl_rsi_offset

        # New high loose filter
        offset_to_max_prev_high = abs(self.highest_bars(self.data.high, self.p.prev_high_lookback + abs(int(self.offset_to_local_high[0])) + 1))
        is_local_high_global: bool = self.offset_to_local_high[0] == offset_to_max_prev_high
        should_loose_new_high: bool = (is_local_high_global and self.p.toggle_new_high_loose)

        is_trending_positive: bool = self.p.long_trend_threshold == 100 or self.ma_delta[0] > self.top_delta_bound[0]
        is_long_trend: bool = is_trending_positive

        min_bar_count: int = self.p.min_bar_count_on_trend if is_long_trend else self.p.min_bar_count

        # extreme uptrend
        is_quick_ma_up: bool = self.quick_ma_delta[0] > 0 if self.p.toggle_positive_ma_delta else True
        is_slow_ma_up: bool = self.ma_delta[0] > 0 if self.p.toggle_positive_ma_delta else True

        in_super_long_trend: bool = ((self.quick_ma_delta[0] >= self.quick_ma_super_low_delta_bound[0]) and
                                     is_quick_ma_up and (self.ma_delta[0] > self.slow_ma_super_low_delta_bound[0]) and
                                     self.p.toggle_top_ma_loose and is_slow_ma_up)

        # RSI validation
        rsi_look_index_offset_array: List[int] = [1, 2, 3]  # Equivalent to Pine Script's a + 1, a, a - 1
        rsi_max: float = self.rsi[-1]  # Assume the [1] index as previous value initially
        rsi_max_index_offset: int = 1

        for offset in rsi_look_index_offset_array:
            if self.rsi[-offset] >= rsi_max:
                rsi_max = self.rsi[-offset]
                rsi_max_index_offset = offset

        final_rsi_long_threshold: int = max(
            self.p.rsi_long_threshold,
            vip_hl_rsi_long_threshold if should_loose_vip_hl else 0,
            self.p.new_high_rsi_long_threshold if should_loose_new_high else 0,
            self.p.top_ma_rsi_long_threshold if in_super_long_trend else 0
        )

        strong_trend_window_one_rsi_offset: int = max(
            0,
            self.p.new_high_window_one_rsi_offset if should_loose_new_high else 0,
            self.p.top_ma_window_one_rsi_offset if in_super_long_trend else 0
        )

        strong_trend_window_two_rsi_offset: int = max(
            0,
            self.p.new_high_window_two_rsi_offset if should_loose_new_high else 0,
            self.p.top_ma_window_two_rsi_offset if in_super_long_trend else 0
        )

        is_rsi_recent_highest: bool = self.rsi[-rsi_max_index_offset] == self.rsi_highest[-rsi_max_index_offset]
        rsi_overbought_v2: bool = rsi_max >= final_rsi_long_threshold and is_rsi_recent_highest
        rsi_overbought_a_bar_v2: bool = rsi_max >= self.p.rsi_long_threshold and is_rsi_recent_highest
        dl_overbought: bool = rsi_overbought_v2

        # pivot points and bar pattern
        potential_pl: bool = not math.isnan(self.two_by_zero.value[0])
        close_at_bar_top: bool = close_at_bar_top_by_percent(
            self.p.close_top_percent * 0.01, self.data.close[0], self.data.low[0], self.data.high[0]
        )
        bar_height_greater_than_ca: bool = greater_than_close_avg_by(
            self.close_average_percent[0], self.p.strong_bar_multiplier, self.data.high[0], self.data.low[0]
        )

        # HL
        current_bar_index_offset = self.last_bar_index() - self.bar_index()
        # is_hl_satisfied = self.hlv4.l.is_hl_satisfied[-current_bar_index_offset] == 1.0
        # is_hl_satisfied = self.viphl.l.is_hl_satisfied[-current_bar_index_offset] == 1.0
        is_hl_satisfied = True
        '''
        below is equivalent to getDL
        '''

        if not math.isnan(self.ph.value[0]) and self.within_lookback_period(use_date_range=self.p.use_date_range):
        # if not math.isnan(self.ph.value[0]) and self.with_in_lookback_period(use_date_range=self.p.use_date_range) and self.bar_index() - self.p.right_bars == 994:
            dl = DiagonalLine(close=self.data.close, open=self.data.open, high=self.data.high, low=self.data.low, bar_index=self.bar_index())
            dl.a_bar_index = self.bar_index() - self.p.right_bars
            dl.a_high = self.data.high[-self.p.right_bars]
            dl.a_body_high = max(self.data.close[-self.p.right_bars], self.data.open[-self.p.right_bars])

            if dl_overbought:
                dl.over_bought = True
            if rsi_overbought_a_bar_v2:
                dl.a_bar_over_bought = True
            dl.rsi = rsi_max
            dl.is_rsi_recent_highest = is_rsi_recent_highest

            dl_wrapper = DiagonalLineWrapper()
            dl_wrapper.current = dl
            self.dl_wrapper_array.append(dl_wrapper)

        signal_wrapper = SignalWrapper()
        if self.within_lookback_period(use_date_range=self.p.use_date_range):
            signal_wrapper = self.get_dl(should_loose_new_high, in_super_long_trend, final_rsi_long_threshold,
                        self.close_average_percent[0], close_at_bar_top, bar_height_greater_than_ca,
                        strong_trend_window_one_rsi_offset, strong_trend_window_two_rsi_offset, potential_pl,
                        min_bar_count, is_quick_ma_up, is_slow_ma_up, is_hl_satisfied)

        self.export_signals(signal_wrapper)

        if self.last_bar_index() == self.bar_index():
            for each_dl_wrapper in self.dl_wrapper_array:
                dl = each_dl_wrapper.current
                if dl.ready_for_export_v2():
                    self.dl_lines_info.append((dl.x1, dl.y1, dl.x2, dl.y2))

    def export_signals(self, signal_wrapper: SignalWrapper):
        self.l.two_by_zero_signal[0] = 1 if signal_wrapper.two_by_zero_signal else -1
        self.l.buy_signal[0] = 1 if signal_wrapper.buy_signal else -1
        self.l.dl_break_signal[0] = 1 if signal_wrapper.dl_break_signal else -1

        self.l.is_two_by_zero_disabled_by_rsi[0] = 1 if signal_wrapper.is_two_by_zero_disabled_by_rsi else -1
        self.l.is_two_by_zero_disabled_by_hl[0] = 1 if signal_wrapper.is_two_by_zero_disabled_by_hl else -1
        self.l.is_two_by_zero_disabled_by_stop_loss[0] = 1 if signal_wrapper.is_two_by_zero_disabled_by_stop_loss else -1
        self.l.is_two_by_zero_disabled_by_high_close[0] = 1 if signal_wrapper.is_two_by_zero_disabled_by_high_close else -1
        self.l.is_two_by_zero_triggered_by_rsi_override[0] = 1 if signal_wrapper.is_two_by_zero_triggered_by_rsi_override else -1

        self.l.is_buy_signal_disabled_by_rsi[0] = 1 if signal_wrapper.is_buy_signal_disabled_by_rsi else -1
        self.l.is_buy_signal_disabled_by_stop_loss[0] = 1 if signal_wrapper.is_buy_signal_disabled_by_stop_loss else -1
        self.l.is_buy_signal_disabled_by_high_close[0] = 1 if signal_wrapper.is_buy_signal_disabled_by_high_close else -1
        self.l.is_buy_signal_triggered_by_rsi_override[0] = 1 if signal_wrapper.is_buy_signal_triggered_by_rsi_override else -1

        self.l.is_dl_break_disabled_by_rsi[0] = 1 if signal_wrapper.is_dl_break_disabled_by_rsi else -1
        self.l.is_dl_break_disabled_by_stop_loss[0] = 1 if signal_wrapper.is_dl_break_disabled_by_stop_loss else -1
        self.l.is_dl_break_disabled_by_high_close[0] = 1 if signal_wrapper.is_dl_break_disabled_by_high_close else -1
        self.l.is_dl_break_triggered_by_rsi_override[0] = 1 if signal_wrapper.is_dl_break_triggered_by_rsi_override else -1

        self.l.is_vip_dl_signal[0] = 1 if signal_wrapper.is_vip_dl_signal else -1
        self.l.is_key_bar_signal[0] = 1 if signal_wrapper.is_key_bar_signal else -1
        self.l.is_low_t_rsi_signal[0] = 1 if signal_wrapper.is_low_t_rsi_signal else -1

        self.l.latest_rsi_long_threshold[0] = signal_wrapper.latest_rsi_long_threshold
        self.l.rsi_at_signal[0] = signal_wrapper.rsi_at_signal
        self.l.bar_count_at_signal[0] = signal_wrapper.bar_count_at_signal
        self.l.deslope_score_at_signal[0] = signal_wrapper.deslope_score_at_signal
        self.l.dl_value_at_signal[0] = signal_wrapper.dl_value_at_signal

        buy_signal_filtered_by_rsi: bool = not signal_wrapper.buy_signal and signal_wrapper.is_buy_signal_disabled_by_rsi
        buy_signal_filtered_by_stop_loss: bool = not signal_wrapper.buy_signal and signal_wrapper.is_buy_signal_disabled_by_stop_loss
        buy_signal_filtered_by_high_close: bool = not signal_wrapper.buy_signal and signal_wrapper.is_buy_signal_disabled_by_high_close
        self.l.maybe_buy_signal[0] = signal_wrapper.buy_signal or buy_signal_filtered_by_rsi or buy_signal_filtered_by_stop_loss or buy_signal_filtered_by_high_close

        two_by_zero_filtered_by_hl: bool = not signal_wrapper.two_by_zero_signal and signal_wrapper.is_two_by_zero_disabled_by_hl
        two_by_zero_filtered_by_rsi: bool = not signal_wrapper.two_by_zero_signal and signal_wrapper.is_two_by_zero_disabled_by_rsi
        two_by_zero_filtered_by_stop_loss: bool = not signal_wrapper.two_by_zero_signal and signal_wrapper.is_two_by_zero_disabled_by_stop_loss
        two_by_zero_filtered_by_high_close: bool = not signal_wrapper.two_by_zero_signal and signal_wrapper.is_two_by_zero_disabled_by_high_close
        self.l.maybe_two_by_zero_signal[0] = (signal_wrapper.two_by_zero_signal or two_by_zero_filtered_by_hl
                                          or two_by_zero_filtered_by_rsi or two_by_zero_filtered_by_stop_loss
                                          or two_by_zero_filtered_by_high_close)

        dl_break_signal_filtered_by_rsi: bool = not signal_wrapper.dl_break_signal and signal_wrapper.is_dl_break_disabled_by_rsi
        dl_break_signal_filtered_by_stop_loss: bool = not signal_wrapper.dl_break_signal and signal_wrapper.is_dl_break_disabled_by_stop_loss
        dl_break_signal_filtered_by_high_close: bool = not signal_wrapper.dl_break_signal and signal_wrapper.is_dl_break_disabled_by_high_close
        self.l.maybe_dl_break_signal[0] = (signal_wrapper.dl_break_signal or
                                           dl_break_signal_filtered_by_rsi or
                                           dl_break_signal_filtered_by_stop_loss or
                                           dl_break_signal_filtered_by_high_close)

    def highest_bars(self, source, length):
        if len(source) < length:
            return None  # Not enough data to calculate

        recent_highs = list(source.get(size=length))
        highest_val = max(recent_highs)
        highest_idx = recent_highs[::-1].index(highest_val)
        return -highest_idx

    def get_dl(self, should_loose_new_high: bool, in_super_long_trend: bool, final_rsi_long_threshold: float,
               close_avg_percent: float, close_at_bar_top: bool, bar_height_greater_than_ca: bool,
               strong_trend_window_one_rsi_offset: int, strong_trend_window_two_rsi_offset: int, potential_pl: bool,
               min_bar_count: int, is_quick_ma_up: bool, is_slow_ma_up: bool, is_hl_satisfied: bool):

        two_by_zero_signal: bool = False
        buy_signal: bool = False
        dl_break_signal: bool = False

        # Signal disabling conditions
        is_two_by_zero_disabled_by_rsi: bool = False
        is_two_by_zero_disabled_by_hl: bool = False
        is_two_by_zero_disabled_by_stop_loss: bool = False
        is_two_by_zero_disabled_by_high_close: bool = False
        is_two_by_zero_triggered_by_rsi_override: bool = False

        is_buy_signal_disabled_by_rsi: bool = False
        is_buy_signal_disabled_by_stop_loss: bool = False
        is_buy_signal_disabled_by_high_close: bool = False
        is_buy_signal_triggered_by_rsi_override: bool = False

        is_dl_break_disabled_by_rsi: bool = False
        is_dl_break_disabled_by_stop_loss: bool = False
        is_dl_break_disabled_by_high_close: bool = False
        is_dl_break_triggered_by_rsi_override: bool = False

        # Additional signal flags
        is_vip_dl_signal: bool = False
        is_key_bar_signal: bool = False
        is_low_t_rsi_signal: bool = False

        # Signal-related variables
        signal_source_a_bar_index: int = 0
        latest_rsi_long_threshold: float = final_rsi_long_threshold  # Assuming final_rsi_long_threshold is defined elsewhere

        # Condition for two by zero signal satisfaction
        is_two_by_zero_satisfied: bool = close_at_bar_top and bar_height_greater_than_ca  # Assuming close_at_bar_top and bar_height_greater_than_ca are defined elsewhere

        # RSI value at the time of signal generation
        rsi_at_signal: float = float('NaN')  # Use float('nan') to represent Pine Script's `na`
        bar_count_at_signal: int = 0
        deslope_score_at_signal: float = -1.0
        dl_value_at_signal: float = -1.0

        # Assuming dl_wrapper_array is a list of DlWrapper objects
        for each_dl_wrapper in self.dl_wrapper_array:
            # print(f'checking for dl starting index at {each_dl_wrapper.current.a_bar_index}, cur index {self.bar_index()}')
            # update close/open/high/low
            each_dl_wrapper.current.close = self.data.close
            each_dl_wrapper.current.open = self.data.open
            each_dl_wrapper.current.low = self.data.low
            each_dl_wrapper.current.high = self.data.high
            each_dl_wrapper.current.bar_index = self.bar_index()

            if each_dl_wrapper.rollback is not None:
                each_dl_wrapper.rollback.close = self.data.close
                each_dl_wrapper.rollback.open = self.data.open
                each_dl_wrapper.rollback.low = self.data.low
                each_dl_wrapper.rollback.high = self.data.high
                each_dl_wrapper.rollback.bar_index = self.bar_index()

            # Determine if HRIS check is needed
            should_check_against_hrsi = (should_loose_new_high or in_super_long_trend) and each_dl_wrapper.current.a_bar_over_bought

            # Update the current by point low based on conditions
            if not math.isnan(self.two_by_one.value[0]):  # Assuming two_by_one is defined elsewhere
                each_dl_wrapper.current.update_cur_by_point_low(self.data.low[-1])

            if not math.isnan(self.pl.value[0]):  # Assuming pl is defined elsewhere
                each_dl_wrapper.current.update_cur_by_point_low(self.data.low[-2])

            rsi_offset = final_rsi_long_threshold - self.p.rsi_long_threshold
            should_update_rollback = False

            # Set DL overbought status for the current and rollback DLs
            each_dl_wrapper.current.set_dl_overbought(final_rsi_long_threshold)
            if each_dl_wrapper.rollback is not None:
                each_dl_wrapper.rollback.set_dl_overbought(final_rsi_long_threshold)

            # Update the latest RSI long threshold
            latest_rsi_long_threshold = final_rsi_long_threshold

            if each_dl_wrapper.current.need_to_set_b_v2():
                need_update: bool = True
                if self.bar_index() > each_dl_wrapper.current.a_bar_index:
                    if self.p.toggle_short_dl and each_dl_wrapper.current.bar_count == 3:
                        dl_break = each_dl_wrapper.current.is_processed and each_dl_wrapper.current.is_dl_break(0, close_avg_percent)
                        long_fourth_bar = ((self.data.close[0] / self.data.low[-1]) - 1) > (self.p.short_dl_break_threshold * close_avg_percent * 0.01)

                        if (dl_break and long_fourth_bar and
                            each_dl_wrapper.current.pass_validation(
                                self.p.min_bar_count, self.p.deslope_score_threshold, self.p.dl_angle_up_limit,
                                check_bar_count=False
                            )
                        ):

                            if each_dl_wrapper.current.last_signal_bar_index == -1:
                                each_dl_wrapper.current.rescaled_end_index = self.bar_index()
                                each_dl_wrapper.current.check_dl_crosses(
                                    check_end_index=self.bar_index(),
                                    extended_cross_threshold=self.p.extended_cross_threshold,
                                    dl_break_threshold=self.p.dl_break_threshold,
                                    extended_cross_uncross_threshold=self.p.extended_cross_uncross_threshold,
                                    close_avg_percent=close_avg_percent
                                )
                                each_dl_wrapper.current.set_export_coordinates()

                                (
                                    _buy_signal,
                                    _is_low_t_rsi_signal,
                                    _is_vip_dl_signal,
                                    _is_key_bar_signal,
                                    _latest_rsi_long_threshold,
                                    _is_buy_signal_disabled_by_rsi,
                                    _is_buy_signal_disabled_by_stop_loss,
                                    _is_buy_signal_disabled_by_high_close,
                                    _is_buy_signal_triggered_by_rsi_override,
                                    _need_update,
                                    _signal_source_a_bar_index,
                                    _rsi_at_signal,
                                    _bar_count_at_signal,
                                    _deslope_score_at_signal,
                                    _dl_value_at_signal
                                ) = each_dl_wrapper.current.resolve_signal(
                                    self.p.toggle_vip_dl_loose,
                                    self.p.toggle_key_bar_loose,
                                    self.p.vip_dl_bar_count,
                                    self.p.vip_dl_score_limit,
                                    self.p.vip_dl_multiplier,
                                    latest_rsi_long_threshold,
                                    self.p.rsi_long_threshold,
                                    self.p.vip_dl_rsi_offset,
                                    in_super_long_trend,
                                    self.p.key_bar_t_bar_close_offset,
                                    self.p.key_bar_dl_close_offset,
                                    self.p.key_bar_close_top_percent,
                                    self.p.key_bar_rsi_offset,
                                    close_avg_percent,
                                    self.p.toggle_vip_dl_no_reduce_chase,
                                    self.p.toggle_key_bar_no_reduce_chase,
                                    self.p.toggle_top_ma_no_reduce_chase,
                                    self.p.toggle_reduce_chase,
                                    should_check_against_hrsi,
                                    strong_trend_window_one_rsi_offset,
                                    self.p.window_one_stop_loss_chase_offset,
                                    self.p.window_one_close_chase_offset,
                                    self.p.toggle_rsi,
                                    self.rsi[0],
                                    self.p.window_one_rsi_chase_offset,
                                    self.p.toggle_low_trsi_adjustment,
                                    self.p.toggle_low_trsi_with_bar_count,
                                    self.p.low_trsi_to_hrsi_offset,
                                    self.p.hrsi_cutoff_percent_on_low_trsi,
                                    self.p.low_trsi_bar_count,
                                )

                                buy_signal = _buy_signal
                                is_low_t_rsi_signal = _is_low_t_rsi_signal
                                is_vip_dl_signal = _is_vip_dl_signal
                                is_key_bar_signal = _is_key_bar_signal
                                is_buy_signal_disabled_by_rsi = _is_buy_signal_disabled_by_rsi
                                is_buy_signal_disabled_by_stop_loss = _is_buy_signal_disabled_by_stop_loss
                                is_buy_signal_disabled_by_high_close = _is_buy_signal_disabled_by_high_close
                                is_buy_signal_triggered_by_rsi_override = _is_buy_signal_triggered_by_rsi_override
                                need_update = _need_update
                                signal_source_a_bar_index = _signal_source_a_bar_index
                                rsi_at_signal = _rsi_at_signal
                                bar_count_at_signal = max(_bar_count_at_signal, bar_count_at_signal) if bar_count_at_signal != 0 else _bar_count_at_signal
                                deslope_score_at_signal = _deslope_score_at_signal
                                dl_value_at_signal = _dl_value_at_signal

                                each_dl_wrapper.current.short_dl_break_bar_index = self.bar_index()
                                each_dl_wrapper.rollback = copy.deepcopy(each_dl_wrapper.current)

                                continue

                    if potential_pl:
                        each_dl_wrapper.current.bar_count_end_index = self.bar_index()

                        if is_two_by_zero_satisfied and (self.bar_index() - each_dl_wrapper.current.a_bar_index + 1 >= min_bar_count):
                            each_dl_wrapper.current.reset_except_bar_a()
                            each_dl_wrapper.current.set_b_bar_and_b_high(b_bar_index=self.bar_index() - 1, b_high=max(self.data.close[-1], self.data.open[-1]))

                            if self.p.toggle_dl_by_score:
                                each_dl_wrapper.current.rescale_dl_v2(b_bar_index_for_distance=each_dl_wrapper.current.b_bar_index, distance_percent=self.p.distance_to_a_prime_percent,
                                                                      deslope_ca_multiplier=self.p.deslope_ca_multiplier,
                                                                      close_avg_percent=close_avg_percent, ignore_open_price_bar_count=self.p.ignore_open_price_bar_count,
                                                                      dl_break_threshold=self.p.dl_break_threshold, min_bar_count=min_bar_count,
                                                                      deslope_score_threshold=self.p.deslope_score_threshold, dl_angle_up_limit=self.p.dl_angle_up_limit,
                                                                      toggle_dl_by_score=self.p.toggle_dl_by_score)
                            else:
                                each_dl_wrapper.current.rescale_dl(b_bar_index_for_distance=each_dl_wrapper.current.b_bar_index, distance_percent=self.p.distance_to_a_prime_percent,
                                                                   toggle_rescale_debug=self.p.toggle_rescale_debug, deslope_ca_multiplier=self.p.deslope_ca_multiplier,
                                                                   close_avg_percent=close_avg_percent, ignore_open_price_bar_count=self.p.ignore_open_price_bar_count)

                            result = each_dl_wrapper.current.process_and_maybe_two_by_zero_signal(self.p.deslope_ca_multiplier, close_avg_percent,                                                                                                      self.p.dl_angle_up_limit, self.p.dl_break_threshold, self.p.extended_cross_threshold,
                                                                                                  self.p.toggle_rsi, min_bar_count,
                                                                                                  self.p.extended_cross_uncross_threshold, self.p.deslope_score_threshold, self.rsi[0],
                                                                                                  self.p.window_one_rsi_chase_offset, self.p.window_one_stop_loss_chase_offset, self.p.window_one_close_chase_offset,
                                                                                                  self.p.toggle_reduce_chase, strong_trend_window_one_rsi_offset, final_rsi_long_threshold,
                                                                                                  self.p.vip_dl_bar_count, self.p.vip_dl_score_limit, self.p.vip_dl_multiplier, self.p.rsi_long_threshold,
                                                                                                  self.p.vip_dl_rsi_offset, in_super_long_trend, self.p.key_bar_t_bar_close_offset, self.p.key_bar_dl_close_offset,
                                                                                                  self.p.key_bar_close_top_percent, self.p.key_bar_rsi_offset, self.p.toggle_vip_dl_loose, self.p.toggle_key_bar_loose,
                                                                                                  self.p.toggle_low_trsi_adjustment, self.p.toggle_low_trsi_with_bar_count, self.p.low_trsi_to_hrsi_offset,
                                                                                                  self.p.hrsi_cutoff_percent_on_low_trsi, self.p.low_trsi_bar_count, self.p.toggle_vip_dl_no_reduce_chase,
                                                                                                  self.p.toggle_key_bar_no_reduce_chase, should_check_against_hrsi, self.p.toggle_top_ma_no_reduce_chase)

                            two_by_zero_signal, is_disabled_by_rsi, is_disabled_by_stop_loss, is_disabled_by_high_close, is_triggered_by_rsi_override, need_update, \
                                is_vip_dl_signal, is_key_bar_signal, is_low_t_rsi_signal, latest_rsi_long_threshold = result

                            if not is_hl_satisfied and two_by_zero_signal:
                                two_by_zero_signal = False
                                is_two_by_zero_disabled_by_hl = True

                            if two_by_zero_signal:
                                signal_source_a_bar_index = each_dl_wrapper.current.a_bar_index
                                rsi_at_signal = each_dl_wrapper.current.rsi
                                bar_count_at_signal = max(each_dl_wrapper.current.bar_count, bar_count_at_signal) if bar_count_at_signal != 0 else each_dl_wrapper.current.bar_count
                                deslope_score_at_signal = each_dl_wrapper.current.deslope_score
                                dl_value_at_signal = each_dl_wrapper.current.get_rescaled_y_with_bar_index(self.bar_index())
                        else:
                            need_update = True

                    elif not math.isnan(self.two_by_one.value[0]):
                        if self.p.toggle_dl_by_score:
                            each_dl_wrapper.current.reset_except_bar_a()
                            max_high = max(self.data.close[-1], self.data.open[-1])  # Assumes the close and open are lists or similar structure
                            each_dl_wrapper.current.set_b_bar_and_b_high(self.bar_index() - 1, max_high)
                            each_dl_wrapper.current.rescale_dl_v2(each_dl_wrapper.current.b_bar_index, self.p.distance_to_a_prime_percent, self.p.deslope_ca_multiplier,
                                                       close_avg_percent, self.p.ignore_open_price_bar_count, self.p.dl_break_threshold, min_bar_count, self.p.deslope_score_threshold,
                                                       self.p.dl_angle_up_limit, self.p.toggle_dl_by_score)
                            each_dl_wrapper.current.process_drawing(self.p.deslope_ca_multiplier, close_avg_percent)

                        dl_break = each_dl_wrapper.current.is_processed and each_dl_wrapper.current.is_dl_break(0, close_avg_percent)
                        dl_break_and_cross_threshold = each_dl_wrapper.current.is_processed and each_dl_wrapper.current.is_dl_break(self.p.dl_break_threshold, close_avg_percent)

                        if dl_break_and_cross_threshold and each_dl_wrapper.current.pass_validation(min_bar_count, self.p.deslope_score_threshold, self.p.dl_angle_up_limit):
                            if each_dl_wrapper.current.last_signal_bar_index == -1:
                                results = each_dl_wrapper.current.resolve_signal(self.p.toggle_vip_dl_loose, self.p.toggle_key_bar_loose, self.p.vip_dl_bar_count, self.p.vip_dl_score_limit, self.p.vip_dl_multiplier, latest_rsi_long_threshold, self.p.rsi_long_threshold, self.p.vip_dl_rsi_offset, in_super_long_trend,
                                                                      self.p.key_bar_t_bar_close_offset, self.p.key_bar_dl_close_offset, self.p.key_bar_close_top_percent, self.p.key_bar_rsi_offset, close_avg_percent, self.p.toggle_vip_dl_no_reduce_chase, self.p.toggle_key_bar_no_reduce_chase, self.p.toggle_top_ma_no_reduce_chase,
                                                                      self.p.toggle_reduce_chase, should_check_against_hrsi, strong_trend_window_one_rsi_offset, self.p.window_one_stop_loss_chase_offset, self.p.window_one_close_chase_offset, self.p.toggle_rsi, self.rsi[0], self.p.window_one_rsi_chase_offset, self.p.toggle_low_trsi_adjustment,
                                                                      self.p.toggle_low_trsi_with_bar_count, self.p.low_trsi_to_hrsi_offset, self.p.hrsi_cutoff_percent_on_low_trsi, self.p.low_trsi_bar_count)
                                (_buy_signal, _is_low_t_rsi_signal, _is_vip_dl_signal, _is_key_bar_signal,
                                 _latest_rsi_long_threshold, _is_buy_signal_disabled_by_rsi,
                                 _is_buy_signal_disabled_by_stop_loss, _is_buy_signal_disabled_by_high_close,
                                 _is_buy_signal_triggered_by_rsi_override, _need_update, _signal_source_a_bar_index,
                                 _rsi_at_signal, _bar_count_at_signal, _deslope_score_at_signal, _dl_value_at_signal) = results

                                buy_signal = _buy_signal
                                is_low_t_rsi_signal = _is_low_t_rsi_signal
                                is_vip_dl_signal = _is_vip_dl_signal
                                is_key_bar_signal = _is_key_bar_signal
                                latest_rsi_long_threshold = _latest_rsi_long_threshold
                                is_buy_signal_disabled_by_rsi = _is_buy_signal_disabled_by_rsi
                                is_buy_signal_disabled_by_stop_loss = _is_buy_signal_disabled_by_stop_loss
                                is_buy_signal_disabled_by_high_close = _is_buy_signal_disabled_by_high_close
                                is_buy_signal_triggered_by_rsi_override = _is_buy_signal_triggered_by_rsi_override
                                signal_source_a_bar_index = _signal_source_a_bar_index
                                rsi_at_signal = _rsi_at_signal
                                bar_count_at_signal = max(_bar_count_at_signal, bar_count_at_signal) if bar_count_at_signal != 0 else _bar_count_at_signal
                                deslope_score_at_signal = _deslope_score_at_signal
                                dl_value_at_signal = _dl_value_at_signal
                                need_update = _need_update

                        elif not dl_break and not dl_break_and_cross_threshold:
                            if each_dl_wrapper.current.is_processed:  # only skip re-process if not the first time
                                need_update = False
                        elif dl_break and not dl_break_and_cross_threshold:
                            need_update = True
                    else:
                        if self.p.toggle_dl_by_score and each_dl_wrapper.current.last_signal_bar_index == -1:
                            each_dl_wrapper.current.reset_except_bar_a()
                            b_high = max(self.data.close[-1], self.data.open[-1])  # assuming close and open are list-like structures
                            each_dl_wrapper.current.set_b_bar_and_b_high(self.bar_index() - 1, b_high)
                            each_dl_wrapper.current.rescale_dl_v2(each_dl_wrapper.current.b_bar_index, self.p.distance_to_a_prime_percent,
                                                                  self.p.deslope_ca_multiplier, close_avg_percent, self.p.ignore_open_price_bar_count,
                                                                  self.p.dl_break_threshold, min_bar_count, self.p.deslope_score_threshold, self.p.dl_angle_up_limit,
                                                                  self.p.toggle_dl_by_score)
                            each_dl_wrapper.current.process_drawing(self.p.deslope_ca_multiplier, close_avg_percent)

                        # Determine the type of DL break condition
                        if math.isnan(self.pl.value[0]):
                            non_two_by_two_dl_break = each_dl_wrapper.current.is_dl_break_non_two_by(self.p.non_two_by_dl_break_threshold,
                                                                                          close_avg_percent, is_quick_ma_up, is_slow_ma_up)
                        else:
                            non_two_by_two_dl_break = False

                        is_dl_break = each_dl_wrapper.current.is_dl_break(self.p.dl_break_threshold, close_avg_percent)
                        two_by_two_dl_break = not math.isnan(self.pl.value[0]) and is_dl_break and each_dl_wrapper.current.is_processed
                        satisfy_break_condition = non_two_by_two_dl_break or two_by_two_dl_break

                        if satisfy_break_condition and each_dl_wrapper.current.pass_validation(min_bar_count, self.p.deslope_score_threshold, self.p.dl_angle_up_limit):
                            need_update = False

                        # Update conditions based on 2by2 criteria
                        if not math.isnan(self.pl.value[0]) and each_dl_wrapper.current.bar_count >= min_bar_count and each_dl_wrapper.current.is_processed and each_dl_wrapper.current.check_dl_bar_count_v3(min_bar_count):
                            each_dl_wrapper.current.is_b_confirmed = True

                    if need_update:
                        each_dl_wrapper.current.reset_except_bar_a(not math.isnan(self.pl.value[0]))
                        max_high = max(self.data.close[0], self.data.open[0])
                        each_dl_wrapper.current.set_b_bar_and_b_high(self.bar_index(), max_high)

                        if self.p.toggle_dl_by_score:
                            each_dl_wrapper.current.rescale_dl_v2(each_dl_wrapper.current.b_bar_index, self.p.distance_to_a_prime_percent, self.p.deslope_ca_multiplier,
                                                       close_avg_percent, self.p.ignore_open_price_bar_count, self.p.dl_break_threshold, min_bar_count,
                                                                  self.p.deslope_score_threshold, self.p.dl_angle_up_limit, self.p.toggle_dl_by_score)
                        else:
                            each_dl_wrapper.current.rescale_dl(each_dl_wrapper.current.b_bar_index, self.p.distance_to_a_prime_percent, self.p.toggle_rescale_debug, self.p.deslope_ca_multiplier,
                                                    close_avg_percent, self.p.ignore_open_price_bar_count)

                        each_dl_wrapper.current.process_drawing(self.p.deslope_ca_multiplier, close_avg_percent)

            if each_dl_wrapper.current.ready_to_draw():
                should_draw = True

                each_dl_wrapper.current.rescaled_end_index = self.bar_index()

                if each_dl_wrapper.current.pass_validation(min_bar_count, self.p.deslope_score_threshold, self.p.dl_angle_up_limit):
                    each_dl_wrapper.current.check_dl_crosses(check_end_index=self.bar_index(), extended_cross_threshold=self.p.extended_cross_threshold,
                                                  dl_break_threshold=self.p.dl_break_threshold, extended_cross_uncross_threshold=self.p.extended_cross_uncross_threshold,
                                                  close_avg_percent=close_avg_percent)
                elif each_dl_wrapper.rollback and each_dl_wrapper.rollback.pass_validation(min_bar_count, self.p.deslope_score_threshold, self.p.dl_angle_up_limit):
                    each_dl_wrapper.current.copy_all_from(each_dl_wrapper.rollback)
                    each_dl_wrapper.current.rescaled_end_index = self.bar_index()
                    each_dl_wrapper.current.check_dl_crosses(check_end_index=self.bar_index(), extended_cross_threshold=self.p.extended_cross_threshold,
                                                          dl_break_threshold=self.p.dl_break_threshold, extended_cross_uncross_threshold=self.p.extended_cross_uncross_threshold,
                                                          close_avg_percent=close_avg_percent)
                else:
                    should_draw = False

                if should_draw:
                    # Check various conditions to decide the break strategy
                    not_two_by = not potential_pl and math.isnan(self.two_by_one.value[0]) and math.isnan(self.pl.value[0])
                    is_dl_break = each_dl_wrapper.current.is_dl_break_non_two_by(self.p.non_two_by_dl_break_threshold, close_avg_percent, is_quick_ma_up, is_slow_ma_up, break_only=True) if not_two_by else each_dl_wrapper.current.is_dl_break(self.p.dl_break_threshold, close_avg_percent)
                    is_short_dl_break = each_dl_wrapper.current.is_short_dl_break(self.p.toggle_short_dl, self.p.short_dl_break_threshold, close_avg_percent)

                    if is_dl_break or is_short_dl_break:
                        if each_dl_wrapper.current.last_signal_bar_index == -1:
                            # Resolve signals based on various conditions
                            (_buy_signal, _is_low_t_rsi_signal, _is_vip_dl_signal, _is_key_bar_signal,
                             _latest_rsi_long_threshold, _is_buy_signal_disabled_by_rsi,
                             _is_buy_signal_disabled_by_stop_loss, _is_buy_signal_disabled_by_high_close,
                             _is_buy_signal_triggered_by_rsi_override, _need_update, _signal_source_a_bar_index,
                             _rsi_at_signal, _bar_count_at_signal, _deslope_score_at_signal, _dl_value_at_signal) = each_dl_wrapper.current.resolve_signal(
                                self.p.toggle_vip_dl_loose, self.p.toggle_key_bar_loose, self.p.vip_dl_bar_count, self.p.vip_dl_score_limit, self.p.vip_dl_multiplier, latest_rsi_long_threshold, self.p.rsi_long_threshold, self.p.vip_dl_rsi_offset, in_super_long_trend,
                                self.p.key_bar_t_bar_close_offset, self.p.key_bar_dl_close_offset, self.p.key_bar_close_top_percent, self.p.key_bar_rsi_offset, close_avg_percent, self.p.toggle_vip_dl_no_reduce_chase, self.p.toggle_key_bar_no_reduce_chase, self.p.toggle_top_ma_no_reduce_chase,
                                self.p.toggle_reduce_chase, should_check_against_hrsi, strong_trend_window_one_rsi_offset, self.p.window_one_stop_loss_chase_offset, self.p.window_one_close_chase_offset, self.p.toggle_rsi, self.rsi[0], self.p.window_one_rsi_chase_offset, self.p.toggle_low_trsi_adjustment,
                                self.p.toggle_low_trsi_with_bar_count, self.p.low_trsi_to_hrsi_offset, self.p.hrsi_cutoff_percent_on_low_trsi, self.p.low_trsi_bar_count)

                            buy_signal = _buy_signal
                            is_low_t_rsi_signal = _is_low_t_rsi_signal
                            is_vip_dl_signal = _is_vip_dl_signal
                            is_key_bar_signal = _is_key_bar_signal
                            latest_rsi_long_threshold = _latest_rsi_long_threshold
                            is_buy_signal_disabled_by_rsi = _is_buy_signal_disabled_by_rsi
                            is_buy_signal_disabled_by_stop_loss = _is_buy_signal_disabled_by_stop_loss
                            is_buy_signal_disabled_by_high_close = _is_buy_signal_disabled_by_high_close
                            is_buy_signal_triggered_by_rsi_override = _is_buy_signal_triggered_by_rsi_override
                            signal_source_a_bar_index = _signal_source_a_bar_index
                            rsi_at_signal = _rsi_at_signal
                            bar_count_at_signal = max(_bar_count_at_signal, bar_count_at_signal) if bar_count_at_signal != 0 else _bar_count_at_signal
                            deslope_score_at_signal = _deslope_score_at_signal
                            dl_value_at_signal = _dl_value_at_signal

                    each_dl_wrapper.current.set_export_coordinates()
                    should_update_rollback = True

                # Check for completion condition based on extended cross count
                if each_dl_wrapper.current.is_b_confirmed and (each_dl_wrapper.current.extended_cross_count >= self.p.extended_cross_threshold or two_by_zero_signal):
                    each_dl_wrapper.current.is_completed = True

            # Check if a standard DL break condition is met
            dl_break: bool = each_dl_wrapper.current.is_dl_break(self.p.dl_break_threshold, close_avg_percent)

            # Determine if a short DL break happened in the previous bar within a specific window
            if each_dl_wrapper.rollback is not None:
                short_dl_break_window_two: bool = (
                    each_dl_wrapper.current.short_dl_break_bar_index == self.bar_index() - 1 and
                    each_dl_wrapper.rollback.bar_count == 3 and
                    self.p.toggle_short_dl and
                    each_dl_wrapper.rollback.is_dl_break(self.p.dl_break_threshold, close_avg_percent)
                )
            else:
                short_dl_break_window_two: bool = False

            # Combine DL break conditions
            dl_break_or_last_bar_short_dl_break: bool = dl_break or short_dl_break_window_two

            # Check if a buy signal was potentially generated but canceled due to various conditions
            has_buy_signal_but_canceled: bool = not buy_signal and (
                is_buy_signal_disabled_by_rsi or
                is_buy_signal_disabled_by_stop_loss or
                is_buy_signal_disabled_by_high_close
            )

            # Check if a two by zero signal was potentially generated but canceled
            has_two_by_zero_signal_but_canceled: bool = not two_by_zero_signal and (
                is_two_by_zero_disabled_by_rsi or
                is_two_by_zero_disabled_by_stop_loss or
                is_two_by_zero_disabled_by_high_close
            )

            # Check if the signal originated from the current diagonal line
            signal_from_cur_dl: bool = signal_source_a_bar_index == each_dl_wrapper.current.a_bar_index

            # Determine if there is no valid buy signal on the current diagonal line
            no_buy_signal_on_cur_dl: bool = not (
                (buy_signal or has_buy_signal_but_canceled) and signal_from_cur_dl
            )

            # Determine if there is no valid two by zero signal on the current diagonal line
            no_two_by_zero_signal_on_cur_dl: bool = not (
                (two_by_zero_signal or has_two_by_zero_signal_but_canceled) and signal_from_cur_dl
            )

            # Check if the current bar has no valid signals
            current_bar_no_signal: bool = no_buy_signal_on_cur_dl and no_two_by_zero_signal_on_cur_dl
            close_greater_than_by_point_low_if_exist: bool = (
                math.isnan(each_dl_wrapper.current.cur_by_point_low) or
                (not math.isnan(each_dl_wrapper.current.cur_by_point_low) and self.data.close[0] > each_dl_wrapper.current.cur_by_point_low)
            )

            # check if still within break dl window bar count
            signal_within_break_window_count: bool = each_dl_wrapper.current.break_dl_window_bar_count < self.p.signal_window_bar_count

            if current_bar_no_signal and dl_break_or_last_bar_short_dl_break and signal_within_break_window_count and close_greater_than_by_point_low_if_exist:
                if self.bar_index() - each_dl_wrapper.current.last_signal_bar_index == each_dl_wrapper.current.break_dl_window_bar_count or self.bar_index() - each_dl_wrapper.current.short_dl_break_bar_index == 1:
                    # -------vip DL--------
                    if self.p.toggle_vip_dl_loose:
                        _is_vip_dl_signal, _rsi_long_threshold_post_vip_dl = (each_dl_wrapper.rollback.validate_vip_dl(self.p.vip_dl_bar_count, self.p.vip_dl_score_limit, self.p.vip_dl_multiplier, latest_rsi_long_threshold, self.p.rsi_long_threshold, self.p.vip_dl_rsi_offset)
                                                                              if short_dl_break_window_two else
                                                                              each_dl_wrapper.current.validate_vip_dl(self.p.vip_dl_bar_count, self.p.vip_dl_score_limit, self.p.vip_dl_multiplier, latest_rsi_long_threshold, self.p.rsi_long_threshold, self.p.vip_dl_rsi_offset))
                        is_vip_dl_signal |= _is_vip_dl_signal
                        latest_rsi_long_threshold = max(latest_rsi_long_threshold, _rsi_long_threshold_post_vip_dl) if is_vip_dl_signal else latest_rsi_long_threshold

                    # -------key bar------
                    if self.p.toggle_key_bar_loose:
                        _is_key_bar_signal, _rsi_long_threshold_post_key_bar = (each_dl_wrapper.rollback.validate_key_bar(self.p.key_bar_t_bar_close_offset, self.p.key_bar_dl_close_offset, self.p.key_bar_close_top_percent, self.p.key_bar_rsi_offset, latest_rsi_long_threshold, self.p.rsi_long_threshold, in_super_long_trend, close_avg_percent)
                                                                                if short_dl_break_window_two else
                                                                                each_dl_wrapper.current.validate_key_bar(self.p.key_bar_t_bar_close_offset, self.p.key_bar_dl_close_offset, self.p.key_bar_close_top_percent, self.p.key_bar_rsi_offset, latest_rsi_long_threshold, self.p.rsi_long_threshold, in_super_long_trend, close_avg_percent))
                        is_key_bar_signal |= _is_key_bar_signal
                        latest_rsi_long_threshold = max(latest_rsi_long_threshold, _rsi_long_threshold_post_key_bar) if is_key_bar_signal else latest_rsi_long_threshold

                    flags: Tuple[bool, bool, bool, bool] = each_dl_wrapper.current.resolute_flags(is_vip_dl_signal, self.p.toggle_vip_dl_no_reduce_chase, is_key_bar_signal, self.p.toggle_key_bar_no_reduce_chase, in_super_long_trend, self.p.toggle_top_ma_no_reduce_chase, self.p.toggle_reduce_chase, should_check_against_hrsi,
                                                                          self.rsi[0], each_dl_wrapper.current.rsi, self.p.window_two_rsi_chase_offset)
                    (disable_reduce_chase_on_features, should_check_against_a_bar_rsi, should_check_rsi_override, no_signal_if_reduce_chase) = flags

                    conditions: Tuple[bool, bool, bool, bool] = each_dl_wrapper.current.resolve_condition(should_check_against_a_bar_rsi, each_dl_wrapper.current.rsi, self.p.window_two_rsi_chase_offset, should_check_against_hrsi,
                                                                                  latest_rsi_long_threshold, strong_trend_window_two_rsi_offset, self.p.window_two_stop_loss_chase_offset, close_avg_percent,
                                                                                                          should_check_rsi_override, self.rsi[0], each_dl_wrapper.current.a_bar_index, self.p.toggle_rsi, self.p.window_two_close_chase_offset,
                                                                                  each_dl_wrapper.current.over_bought, is_window_2=True)

                    normalised_overbought: bool = each_dl_wrapper.rollback.over_bought if short_dl_break_window_two else each_dl_wrapper.current.over_bought

                    dl_break_signal: bool = not (self.p.toggle_rsi and (conditions[1] or normalised_overbought)) if should_check_rsi_override else not conditions[3]
                    if self.p.toggle_reduce_chase and not flags[0]:
                        dl_break_signal &= not (conditions[0] or conditions[2] or conditions[3])

                    is_dl_break_disabled_by_rsi: bool = self.p.toggle_rsi and (normalised_overbought or (conditions[1] and should_check_rsi_override))
                    # --------low t-rsi adjustment------
                    final_buy_signal, final_is_disabled_by_rsi, _is_low_t_rsi_signal = (each_dl_wrapper.rollback.validate_low_t_rsi(dl_break_signal, is_dl_break_disabled_by_rsi, self.rsi[0], self.p.toggle_low_trsi_adjustment, self.p.toggle_low_trsi_with_bar_count, self.p.low_trsi_to_hrsi_offset, self.p.hrsi_cutoff_percent_on_low_trsi,
                                                                                                                                   self.p.low_trsi_bar_count, latest_rsi_long_threshold, conditions[0], conditions[2], self.p.toggle_reduce_chase)
                                                                                        if short_dl_break_window_two else
                                                                                        each_dl_wrapper.current.validate_low_t_rsi(dl_break_signal, is_dl_break_disabled_by_rsi, self.rsi[0], self.p.toggle_low_trsi_adjustment, self.p.toggle_low_trsi_with_bar_count, self.p.low_trsi_to_hrsi_offset, self.p.hrsi_cutoff_percent_on_low_trsi,
                                                                                                                                  self.p.low_trsi_bar_count, latest_rsi_long_threshold, conditions[0], conditions[2], self.p.toggle_reduce_chase))
                    is_low_t_rsi_signal |= _is_low_t_rsi_signal
                    dl_break_signal = final_buy_signal
                    is_dl_break_disabled_by_rsi = final_is_disabled_by_rsi

                    is_dl_break_disabled_by_stop_loss: bool = conditions[0] and self.p.toggle_reduce_chase
                    is_dl_break_disabled_by_high_close: bool = conditions[2] and self.p.toggle_reduce_chase
                    is_dl_break_triggered_by_rsi_override: bool = (each_dl_wrapper.current.a_bar_over_bought or flags[3]) and dl_break_signal

                    if dl_break_signal:
                        rsi_at_signal = each_dl_wrapper.current.rsi
                        bar_count_at_signal = max(each_dl_wrapper.current.bar_count, bar_count_at_signal) if bar_count_at_signal != 0 else each_dl_wrapper.current.bar_count
                        deslope_score_at_signal = each_dl_wrapper.current.deslope_score
                        dl_value_at_signal = each_dl_wrapper.current.get_rescaled_y_with_bar_index(self.bar_index())

                    if short_dl_break_window_two:
                        each_dl_wrapper.rollback.break_dl_window_bar_count += 1
                    else:
                        each_dl_wrapper.current.break_dl_window_bar_count += 1

            # Update the rollback object if needed
            if should_update_rollback:
                each_dl_wrapper.rollback = copy.deepcopy(each_dl_wrapper.current)

            # Reset conditions based on various checks
            if (each_dl_wrapper.current.need_to_reset(-self.p.right_bars) and
                each_dl_wrapper.current.rescaled_b_bar_index != self.bar_index() and
                not (each_dl_wrapper.current.is_b_confirmed or buy_signal)):
                each_dl_wrapper.current.is_b_confirmed = True

            # If a change has been detected, reset the change flag
            if each_dl_wrapper.current.is_changed:
                each_dl_wrapper.current.is_changed = False

        return SignalWrapper(
            two_by_zero_signal=two_by_zero_signal,
            buy_signal=buy_signal,
            dl_break_signal=dl_break_signal,
            is_two_by_zero_disabled_by_rsi=is_two_by_zero_disabled_by_rsi,
            is_two_by_zero_disabled_by_hl=is_two_by_zero_disabled_by_hl,
            is_two_by_zero_disabled_by_stop_loss=is_two_by_zero_disabled_by_stop_loss,
            is_two_by_zero_disabled_by_high_close=is_two_by_zero_disabled_by_high_close,
            is_two_by_zero_triggered_by_rsi_override=is_two_by_zero_triggered_by_rsi_override,
            is_buy_signal_disabled_by_rsi=is_buy_signal_disabled_by_rsi,
            is_buy_signal_disabled_by_stop_loss=is_buy_signal_disabled_by_stop_loss,
            is_buy_signal_disabled_by_high_close=is_buy_signal_disabled_by_high_close,
            is_buy_signal_triggered_by_rsi_override=is_buy_signal_triggered_by_rsi_override,
            is_dl_break_disabled_by_rsi=is_dl_break_disabled_by_rsi,
            is_dl_break_disabled_by_stop_loss=is_dl_break_disabled_by_stop_loss,
            is_dl_break_disabled_by_high_close=is_dl_break_disabled_by_high_close,
            is_dl_break_triggered_by_rsi_override=is_dl_break_triggered_by_rsi_override,
            is_vip_dl_signal=is_vip_dl_signal,
            is_key_bar_signal=is_key_bar_signal,
            is_low_t_rsi_signal=is_low_t_rsi_signal,
            latest_rsi_long_threshold=latest_rsi_long_threshold,
            rsi_at_signal=rsi_at_signal,
            bar_count_at_signal=bar_count_at_signal,
            deslope_score_at_signal = deslope_score_at_signal,
            dl_value_at_signal=dl_value_at_signal
        )
