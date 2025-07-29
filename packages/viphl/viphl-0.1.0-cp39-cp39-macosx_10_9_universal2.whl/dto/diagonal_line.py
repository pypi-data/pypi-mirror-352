import copy
import logging
import math
from dataclasses import dataclass
from typing import Optional, Tuple

from backtrader import DataSeries
from dto.line import Line
from indicators.helper.bar_pattern import close_at_bar_top_by_percent


@dataclass
class DiagonalLine:
    close: DataSeries
    open: DataSeries
    high: DataSeries
    low: DataSeries
    bar_index: int

    a_bar_index: int = -1
    a_prime_bar_index: int = -1
    a_double_prime_bar_index: int = -1
    b_bar_index: int = -1
    b_prime_bar_index: int = -1
    a_high: float = -1.0
    a_body_high: float = -1.0
    a_prime_high: float = -1.0
    a_prime_rescale_high: float = -1.0
    a_double_prime_high: float = -1.0
    a_double_prime_rescale_high: float = -1.0
    b_high: float = -1.0
    b_prime_high: float = -1.0
    b_prime_rescale_high: float = -1.0
    gradient: float = float('NaN')
    y_intercept: float = float('NaN')
    rescaled_gradient: float = float('NaN')
    rescaled_y_intercept: float = float('NaN')
    rescaled_a_bar_index: int = -1
    rescaled_a: float = -1.0
    rescaled_b_bar_index: int = -1
    rescaled_b: float = -1.0
    rescaled_end_index: int = -1
    is_completed: bool = False
    is_changed: bool = False
    is_b_confirmed: bool = False
    is_two_by_zero: bool = True
    last_bar_has_signal: bool = False
    over_bought: bool = False
    a_bar_over_bought: bool = False
    is_processed: bool = False
    # Lines, labels, and counts to be defined based on backtrader's structure
    fixed_dl: Optional[Line] = None
    extended_dl: Optional[Line] = None
    rescaled_dl: Optional[Line] = None
    rescaled_extended: Optional[Line] = None
    rescaled_to_a: Optional[Line] = None
    extended_cross_count: int = 0
    body_cross_count: int = 0
    break_dl_window_bar_count: int = 0
    last_signal_bar_index: int = -1
    harmony_score: float = -1.0
    deslope_score: float = -1.0
    slope: float = 0.0
    angle: float = -1.0
    rsi: float = 0.0
    is_rsi_recent_highest: bool = False
    overlap_start_bar_index: int = -1
    overlap_end_bar_index: int = -1
    bar_count_end_index: int = 0
    bar_count: int = 0
    short_dl_break_bar_index: int = 0
    cur_by_point_low: float = float('NaN')

    x1: float = float('NaN')
    y1: float = float('NaN')
    x2: float = float('NaN')
    y2: float = float('NaN')

    use_rounding_value: bool = True

    def update_cur_by_point_low(self, value):
        if math.isnan(self.cur_by_point_low) or value < self.cur_by_point_low:
            self.cur_by_point_low = value

    def set_dl_overbought(self, final_rsi_long_threshold):
        rsi_overbought_v2 = False

        if self.rsi >= final_rsi_long_threshold and self.is_rsi_recent_highest:
            rsi_overbought_v2 = True

        self.over_bought = rsi_overbought_v2

    def need_to_set_b_v2(self):
        need_b = False
        if self.a_bar_index != -1 and self.a_high != -1 and not self.is_b_confirmed and not self.is_completed:
            need_b = True
        return need_b

    def is_dl_break(self, dl_break_threshold: float, close_avg_percent: float, bar_index_offset: int = 0):
        is_broken = False
        if not math.isnan(self.rescaled_gradient) and not math.isnan(self.rescaled_y_intercept):
            dl_value = self.get_rescaled_y_with_bar_index(self.bar_index - bar_index_offset)
            if dl_value == 0.0:
                return False
            if self.is_close(self.close[-bar_index_offset], dl_value):
                return False
            if (self.close[-bar_index_offset] / dl_value - 1) > (close_avg_percent * dl_break_threshold * 0.01):
                is_broken = True

        return is_broken

    def pass_validation(self, min_bar_count: int, deslope_score_threshold: float, dl_angle_up_limit: int,
                        check_bar_count: bool = True):
        b_not_confirmed_and_invalid_bar_count = not self.check_dl_bar_count_v3(
            min_bar_count) and not self.is_b_confirmed and check_bar_count
        # if b_not_confirmed_and_invalid_bar_count:
        #     logging.error(f"fail dl bar count check, need: [{min_bar_count}], current: [{self.bar_count}]")
        # if not (self.deslope_score <= deslope_score_threshold):
        #     logging.error(
        #         f"fail dl with deslope score, need: [{deslope_score_threshold}], current: [{self.deslope_score}]")
        # if not (self.angle <= dl_angle_up_limit):
        #     logging.error(f"fail dl with angle, need: [{dl_angle_up_limit}], current: [{self.angle}]")
        # if not (self.angle > 0):
        #     logging.error(f"negative angle detected, need: [0], current: [{self.angle}]")

        return ((not b_not_confirmed_and_invalid_bar_count) and (self.deslope_score <= deslope_score_threshold) and
                (self.angle <= dl_angle_up_limit) and (self.angle > 0))

    def cross_rescaled_dl(self, offset=0):
        is_crossed = False
        # Assuming self.data is available with the open and close arrays appropriately indexed
        # Fetching the current bar index offset values for open and close prices
        open_price = self.open[-offset]
        close_price = self.close[-offset]

        # Fetching the Y value of the diagonal line at the adjusted bar index
        dl_value = self.get_rescaled_y_with_bar_index(self.bar_index - offset)

        # Checking if the diagonal line value is between the open and close or below both
        between_body = min(open_price, close_price) <= dl_value <= max(open_price, close_price)
        below_body = min(open_price, close_price) > dl_value

        # Updating the isCrossed flag if any of the conditions are met
        if between_body or below_body:
            is_crossed = True

        return is_crossed

    def check_dl_crosses(self, check_end_index, extended_cross_threshold, dl_break_threshold,
                         extended_cross_uncross_threshold, close_avg_percent):
        rescale_check_length = check_end_index - self.rescaled_b_bar_index
        self.extended_cross_count = 0
        self.body_cross_count = 0

        untouch_count = 0

        # Checking rescale extended crosses
        for x in range(1, rescale_check_length + 1 if rescale_check_length > 0 else 0):
            cur_bar_index = self.rescaled_b_bar_index + x
            cur_bar_index_offset = check_end_index - cur_bar_index

            if self.is_dl_break(dl_break_threshold, close_avg_percent, cur_bar_index_offset):
                self.extended_cross_count += 1
                untouch_count = 0

            if self.cross_rescaled_dl(cur_bar_index_offset):
                untouch_count = 0
            else:
                untouch_count += 1

            complete_or_confirmed_and_hit_extend_threshold = ((self.is_completed or self.is_b_confirmed)
                                                              and self.extended_cross_count == extended_cross_threshold)
            hit_untouched_threshold = untouch_count == extended_cross_uncross_threshold
            b_not_confirmed_but_hit_extend_threshold = (not self.is_b_confirmed and
                                                        self.extended_cross_count >= extended_cross_threshold)

            if (complete_or_confirmed_and_hit_extend_threshold or hit_untouched_threshold or
                b_not_confirmed_but_hit_extend_threshold):
                self.rescaled_end_index = cur_bar_index
                if hit_untouched_threshold:
                    self.is_b_confirmed = True
                    self.is_completed = True
                elif b_not_confirmed_but_hit_extend_threshold:
                    break

        # Checking rescale DL crosses
        rescale_check_length = self.rescaled_b_bar_index - self.rescaled_a_bar_index - 1
        for x in range(1, rescale_check_length + 1 if rescale_check_length > 0 else 0):
            cur_bar_index = self.rescaled_a_bar_index + x
            cur_bar_index_offset = check_end_index - cur_bar_index
            if self.cross_rescaled_dl(cur_bar_index_offset):
                self.body_cross_count += 1

    def get_rescaled_y_with_bar_index(self, cur_bar_index: int):
        y = self.close[0]  # Assuming the current close price
        if self.rescaled_gradient == -1 and self.rescaled_y_intercept == -1:
            return y
        else:
            y = cur_bar_index * self.rescaled_gradient + self.rescaled_y_intercept

        return y

    def calculate_dl_bar_count_v3(self):
        a_bar_index = self.a_bar_index
        self.overlap_start_bar_index = a_bar_index
        dl_horizontal_distance = (
                                     self.rescaled_end_index if self.rescaled_end_index != -1 else self.bar_index) - self.a_bar_index
        self.bar_count = 0

        # if self.bar_index == 1695 and self.a_bar_index == 1693:
        #     print("")

        for x in range(max(dl_horizontal_distance, 1) + 1):
            cur_bar_index = a_bar_index + x
            cur_bar_index_offset = self.bar_index - cur_bar_index
            body_high = max(self.open[-cur_bar_index_offset], self.close[-cur_bar_index_offset])
            dl_value = self.get_rescaled_y_with_bar_index(cur_bar_index)

            if not self.is_close(body_high, dl_value) and body_high > dl_value:
            # if body_high > dl_value:
                continue

            self.bar_count += 1
            self.overlap_end_bar_index = cur_bar_index

        return self.bar_count

    def check_dl_bar_count_v3(self, min_bar_count: int):
        self.calculate_dl_bar_count_v3()

        return self.bar_count >= min_bar_count

    def resolute_flags(self, is_vip_dl_signal: bool, toggle_vip_dl_no_reduce_chase: bool, is_key_bar_signal: bool, toggle_key_bar_no_reduce_chase: bool,
                       in_super_long_trend: bool, toggle_top_ma_no_reduce_chase: bool, toggle_reduce_chase: bool, should_check_against_hrsi: bool,
                       rsi: float, dl_rsi: float, window_rsi_chase_offset: int) -> Tuple[bool, bool, bool, bool]:
        disable_reduce_chase_on_features = (is_vip_dl_signal and toggle_vip_dl_no_reduce_chase) or \
                                           (is_key_bar_signal and toggle_key_bar_no_reduce_chase) or \
                                           (in_super_long_trend and toggle_top_ma_no_reduce_chase)
        should_check_against_a_bar_rsi = toggle_reduce_chase and not disable_reduce_chase_on_features
        should_check_rsi_override = should_check_against_a_bar_rsi or should_check_against_hrsi
        no_signal_if_reduce_chase = toggle_reduce_chase and rsi > (dl_rsi + window_rsi_chase_offset)

        return disable_reduce_chase_on_features, should_check_against_a_bar_rsi, should_check_rsi_override, no_signal_if_reduce_chase

    def resolve_condition(self, should_check_against_a_bar_rsi: bool, dl_rsi: float, window_rsi_chase_offset: float,
                          should_check_against_hrsi: bool, latest_rsi_long_threshold: float, strong_trend_window_rsi_offset: int,
                          window_stop_loss_chase_offset: float, close_avg_percent: float, should_check_rsi_override: bool,
                          rsi: float, dl_a_bar_index: int, toggle_rsi: bool, window_close_chase_offset: float,
                          dl_overbought: bool, is_window_2: bool = False) -> Tuple[bool, bool, bool, bool]:
        max_against_a_bar_rsi_window_one = dl_rsi + window_rsi_chase_offset if should_check_against_a_bar_rsi else 0
        max_against_hrsi_window_one = latest_rsi_long_threshold + strong_trend_window_rsi_offset if should_check_against_hrsi else 0
        max_rsi_window_one = max(max_against_a_bar_rsi_window_one, max_against_hrsi_window_one)

        # Assuming self.low and self.close are accessible as lists or similar structure
        stop_loss = min(self.low[0], self.low[-1]) if not is_window_2 else min(self.low[-1], self.low[-2])# Accessing the last two lows
        stop_loss_percent = (self.close[0] - stop_loss) / self.close[0] * 100

        stop_loss_above_chase_limit = stop_loss_percent > window_stop_loss_chase_offset * close_avg_percent
        window_above_hrsi = should_check_rsi_override and rsi > max_rsi_window_one
        bar_offset = self.bar_index - dl_a_bar_index
        t_bar_close_above_chase_limit = self.close[0] > (self.high[-bar_offset] + self.close[-bar_offset]) / 2 * (1 + window_close_chase_offset * close_avg_percent * 0.01)
        should_check_rsi_and_hrsi_over_bought = toggle_rsi and dl_overbought

        return stop_loss_above_chase_limit, window_above_hrsi, t_bar_close_above_chase_limit, should_check_rsi_and_hrsi_over_bought

    def resolve_signal(self, toggle_vip_dl_loose, toggle_key_bar_loose, vip_dl_bar_count, vip_dl_score_limit,
                       vip_dl_multiplier, latest_rsi_long_threshold, rsi_long_threshold, vip_dl_rsi_offset,
                       in_super_long_trend,
                       key_bar_t_bar_close_offset, key_bar_dl_close_offset, key_bar_close_top_percent,
                       key_bar_rsi_offset, close_avg_percent, toggle_vip_dl_no_reduce_chase,
                       toggle_key_bar_no_reduce_chase, toggle_top_ma_no_reduce_chase,
                       toggle_reduce_chase, should_check_against_hrsi, strong_trend_window_rsi_offset,
                       window_stop_loss_chase_offset, window_close_chase_offset, toggle_rsi, rsi,
                       window_rsi_chase_offset, toggle_low_t_rsi_adjustment,
                       toggle_low_t_rsi_with_bar_count, low_t_rsi_to_h_rsi_offset, h_rsi_cutoff_percent_on_low_t_rsi,
                       low_t_rsi_bar_count):

        is_vip_dl_signal = False
        is_key_bar_signal = False
        _latest_rsi_long_threshold = latest_rsi_long_threshold

        # VIP DL Logic
        if toggle_vip_dl_loose:
            _is_vip_dl_signal, _rsi_long_threshold_post_vip_dl = self.validate_vip_dl(vip_dl_bar_count,
                                                                                      vip_dl_score_limit,
                                                                                      vip_dl_multiplier,
                                                                                      _latest_rsi_long_threshold,
                                                                                      rsi_long_threshold,
                                                                                      vip_dl_rsi_offset
                                                                                      )
            is_vip_dl_signal = is_vip_dl_signal or _is_vip_dl_signal
            _latest_rsi_long_threshold = max(_latest_rsi_long_threshold,
                                             _rsi_long_threshold_post_vip_dl) if is_vip_dl_signal else _latest_rsi_long_threshold

        # Key Bar Logic
        if toggle_key_bar_loose:
            _is_key_bar_signal, _rsi_long_threshold_post_key_bar = self.validate_key_bar(key_bar_t_bar_close_offset,
                                                                                         key_bar_dl_close_offset,
                                                                                         key_bar_close_top_percent,
                                                                                         key_bar_rsi_offset,
                                                                                         _latest_rsi_long_threshold,
                                                                                         rsi_long_threshold,
                                                                                         in_super_long_trend,
                                                                                         close_avg_percent)
            is_key_bar_signal = is_key_bar_signal or _is_key_bar_signal
            _latest_rsi_long_threshold = max(_latest_rsi_long_threshold,
                                             _rsi_long_threshold_post_key_bar) if is_key_bar_signal else _latest_rsi_long_threshold

        # Resolve Flags and Conditions
        disable_reduce_chase_on_features, should_check_against_a_bar_rsi, should_check_rsi_override, no_signal_if_reduce_chase = self.resolute_flags(
            is_vip_dl_signal, toggle_vip_dl_no_reduce_chase, is_key_bar_signal, toggle_key_bar_no_reduce_chase,
            in_super_long_trend, toggle_top_ma_no_reduce_chase, toggle_reduce_chase, should_check_against_hrsi,
            rsi, self.rsi, window_rsi_chase_offset)

        stop_loss_above_chase_limit, window_above_hrsi, t_bar_close_above_chase_limit, should_check_rsi_and_hrsi_over_bought = self.resolve_condition(
            should_check_against_a_bar_rsi, self.rsi, window_rsi_chase_offset, should_check_against_hrsi,
            _latest_rsi_long_threshold, strong_trend_window_rsi_offset, window_stop_loss_chase_offset,
            close_avg_percent,
            should_check_rsi_override, rsi, self.a_bar_index, toggle_rsi, window_close_chase_offset,
            self.over_bought)

        # Generate Signal
        (_buy_signal, _is_low_t_rsi_signal, _is_buy_signal_disabled_by_rsi, _is_buy_signal_disabled_by_stop_loss,
         _is_buy_signal_disabled_by_high_close, _is_buy_signal_triggered_by_rsi_override, _need_update,
         _signal_source_a_bar_index, _rsi_at_signal, _bar_count_at_signal, _deslope_score_at_signal, _dl_value_at_signal) = self.generate_signal(
            should_check_rsi_override, toggle_rsi, window_above_hrsi, should_check_rsi_and_hrsi_over_bought,
            toggle_reduce_chase, disable_reduce_chase_on_features, stop_loss_above_chase_limit,
            t_bar_close_above_chase_limit, rsi,
            toggle_low_t_rsi_adjustment, toggle_low_t_rsi_with_bar_count, low_t_rsi_to_h_rsi_offset,
            h_rsi_cutoff_percent_on_low_t_rsi, low_t_rsi_bar_count, _latest_rsi_long_threshold,
            no_signal_if_reduce_chase)

        return (_buy_signal, _is_low_t_rsi_signal, is_vip_dl_signal, is_key_bar_signal, _latest_rsi_long_threshold,
                _is_buy_signal_disabled_by_rsi, _is_buy_signal_disabled_by_stop_loss, _is_buy_signal_disabled_by_high_close,
                _is_buy_signal_triggered_by_rsi_override, _need_update, _signal_source_a_bar_index, _rsi_at_signal,
                _bar_count_at_signal, _deslope_score_at_signal, _dl_value_at_signal)

    def generate_signal(self, should_check_rsi_override: bool, toggle_rsi: bool, window_above_hrsi: bool,
                        should_check_rsi_and_hrsi_over_bought: bool, toggle_reduce_chase: bool, disable_reduce_chase_on_features: bool,
                        stop_loss_above_chase_limit: bool, t_bar_close_above_chase_limit: bool, rsi: float, toggle_low_t_rsi_adjustment: bool,
                        toggle_low_t_rsi_with_bar_count: bool, low_t_rsi_to_h_rsi_offset: int, h_rsi_cutoff_percent_on_low_t_rsi: int,
                        low_t_rsi_bar_count: int, latest_rsi_long_threshold: float, no_signal_if_reduce_chase: bool) -> (
        Tuple)[bool, bool, bool, bool, bool, bool, bool, int, float, int, float, float]:
        buy_signal = not (toggle_rsi and (window_above_hrsi or self.over_bought)) if should_check_rsi_override else not should_check_rsi_and_hrsi_over_bought

        if toggle_reduce_chase and not disable_reduce_chase_on_features:
            buy_signal = buy_signal and not (stop_loss_above_chase_limit or t_bar_close_above_chase_limit or should_check_rsi_and_hrsi_over_bought)

        is_buy_signal_disabled_by_rsi = toggle_rsi and (self.over_bought or (window_above_hrsi and should_check_rsi_override))

        # Low t-RSI adjustment
        final_buy_signal, final_is_disabled_by_rsi, is_low_t_rsi_signal = self.validate_low_t_rsi(buy_signal, is_buy_signal_disabled_by_rsi, rsi,
                                                                                                toggle_low_t_rsi_adjustment, toggle_low_t_rsi_with_bar_count,
                                                                                                low_t_rsi_to_h_rsi_offset, h_rsi_cutoff_percent_on_low_t_rsi,
                                                                                                low_t_rsi_bar_count, latest_rsi_long_threshold,
                                                                                                stop_loss_above_chase_limit, t_bar_close_above_chase_limit,
                                                                                                toggle_reduce_chase)

        buy_signal = final_buy_signal
        is_buy_signal_disabled_by_rsi = final_is_disabled_by_rsi
        is_buy_signal_disabled_by_stop_loss = stop_loss_above_chase_limit and toggle_reduce_chase
        is_buy_signal_disabled_by_high_close = t_bar_close_above_chase_limit and toggle_reduce_chase
        is_buy_signal_triggered_by_rsi_override = (self.a_bar_over_bought or no_signal_if_reduce_chase) and buy_signal

        self.last_signal_bar_index = self.bar_index # Assuming self.data contains historical data
        self.break_dl_window_bar_count += 1

        need_update = False
        signal_source_a_bar_index = 0
        rsi_at_signal = -1.0
        bar_count_at_signal = 0
        deslope_score_at_signal = -1.0
        dl_value_at_signal = -1.0

        if buy_signal:
            signal_source_a_bar_index = self.a_bar_index
            rsi_at_signal = self.rsi
            bar_count_at_signal = self.bar_count
            deslope_score_at_signal = self.deslope_score
            dl_value_at_signal = self.get_rescaled_y_with_bar_index(self.bar_index)

        return (buy_signal, is_low_t_rsi_signal, is_buy_signal_disabled_by_rsi, is_buy_signal_disabled_by_stop_loss,
                is_buy_signal_disabled_by_high_close, is_buy_signal_triggered_by_rsi_override, need_update,
                signal_source_a_bar_index, rsi_at_signal, bar_count_at_signal, deslope_score_at_signal, dl_value_at_signal)

    def set_dl_over_bought(self, final_rsi_long_threshold):
        rsi_overbought_v2 = False

        if self.rsi >= final_rsi_long_threshold and self.is_rsi_recent_highest:
            rsi_overbought_v2 = True

        self.over_bought = rsi_overbought_v2

    def validate_vip_dl(self, vip_dl_bar_count, vip_dl_score_limit, vip_dl_multiplier, latest_rsi_long_threshold,
                        rsi_long_threshold, vip_dl_rsi_offset):
        is_vip_dl_signal = False
        cur_rsi_long_threshold = latest_rsi_long_threshold

        if self.is_vip_dl(vip_dl_bar_count, vip_dl_score_limit, vip_dl_multiplier):
            cur_rsi_long_threshold = max(latest_rsi_long_threshold, rsi_long_threshold + vip_dl_rsi_offset)
            self.set_dl_over_bought(cur_rsi_long_threshold)
            is_vip_dl_signal = True

        return is_vip_dl_signal, cur_rsi_long_threshold

    def is_vip_dl(self, vip_dl_bar_count, vip_dl_score_limit, vip_dl_multiplier):
        score_limit = vip_dl_score_limit + (self.bar_count - 4) * vip_dl_multiplier

        return self.bar_count >= vip_dl_bar_count and self.deslope_score <= score_limit

    def validate_key_bar(self, key_bar_t_bar_close_offset: float, key_bar_dl_close_offset: float, key_bar_close_top_percent: int, key_bar_rsi_offset: int, latest_rsi_long_threshold: float, rsi_long_threshold: float, in_super_long_trend: bool, close_avg_percent: float) -> Tuple[bool, float]:
        is_key_bar_signal = False
        cur_rsi_long_threshold = latest_rsi_long_threshold

        if self.is_key_bar(key_bar_t_bar_close_offset, key_bar_dl_close_offset, key_bar_close_top_percent, close_avg_percent):
            cur_rsi_long_threshold = max(latest_rsi_long_threshold, rsi_long_threshold + key_bar_rsi_offset)
            self.set_dl_over_bought(cur_rsi_long_threshold)
            is_key_bar_signal = True

        return is_key_bar_signal, cur_rsi_long_threshold

    def is_key_bar(self, key_bar_t_bar_close_offset: float, key_bar_dl_close_offset: float, key_bar_close_top_percent: int, close_avg_percent: float) -> bool:
        # Assuming 'DiagnalLine' is a class defined elsewhere with the required methods
        t_bar_close_greater_than_offset = ((self.close[0] / self.close[-1]) - 1) > (close_avg_percent * key_bar_t_bar_close_offset * 0.01)
        t_bar_close_to_dl_greater_than_offset = ((self.close[0] / self.get_rescaled_y_with_bar_index(self.bar_index)) - 1) > (close_avg_percent * key_bar_dl_close_offset * 0.01)
        close_at_bar_top = close_at_bar_top_by_percent(key_bar_close_top_percent * 0.01, self.close[0], self.low[0], self.high[0])  # Assuming `bar_pattern` is defined to handle this

        return t_bar_close_greater_than_offset and t_bar_close_to_dl_greater_than_offset and close_at_bar_top

    def validate_low_t_rsi(self, buy_signal: bool, is_buy_signal_disabled_by_rsi: bool, rsi: float,
                           toggle_low_t_rsi_adjustment: bool, toggle_low_t_rsi_with_bar_count: bool,
                           low_t_rsi_to_h_rsi_offset: int, h_rsi_cutoff_percent_on_low_t_rsi: int,
                           low_t_rsi_bar_count: int, latest_rsi_long_threshold: float,
                           stop_loss_above_chase_limit: bool, t_bar_close_above_chase_limit: bool,
                           toggle_reduce_chase: bool) -> Tuple[bool, bool, bool]:
        final_buy_signal = buy_signal
        final_is_disabled_by_rsi = is_buy_signal_disabled_by_rsi
        is_low_t_rsi_signal = False

        if is_buy_signal_disabled_by_rsi and toggle_low_t_rsi_adjustment:
            if not (toggle_low_t_rsi_with_bar_count and not (self.bar_count >= low_t_rsi_bar_count)):
                # Check if the RSI difference exceeds the defined offset threshold
                if self.rsi - rsi > low_t_rsi_to_h_rsi_offset:
                    # Calculate adjusted RSI threshold
                    adjusted_rsi_long_threshold = self.rsi - (h_rsi_cutoff_percent_on_low_t_rsi * 0.01 * (self.rsi - rsi))
                    # Re-evaluate buy signal based on adjusted threshold
                    if adjusted_rsi_long_threshold < latest_rsi_long_threshold:
                        final_is_disabled_by_rsi = False
                        final_buy_signal = not ((stop_loss_above_chase_limit or t_bar_close_above_chase_limit) and toggle_reduce_chase)
                        is_low_t_rsi_signal = not buy_signal and final_buy_signal

        return final_buy_signal, final_is_disabled_by_rsi, is_low_t_rsi_signal

    def reset_except_bar_a(self, is_two_by_two: bool = False):
        # Resetting attributes except those related to Bar A
        self.a_prime_bar_index = -1
        self.b_bar_index = -1
        self.b_prime_bar_index = -1

        self.a_prime_high = -1.0
        self.a_prime_rescale_high = -1.0
        self.b_high = -1.0
        self.b_prime_high = -1.0
        self.b_prime_rescale_high = -1.0

        self.gradient = -1.0
        self.y_intercept = -1.0

        self.rescaled_gradient = -1.0
        self.rescaled_y_intercept = -1.0
        self.rescaled_a_bar_index = -1
        self.rescaled_a = -1.0
        self.rescaled_b_bar_index = -1
        self.rescaled_b = -1.0
        self.rescaled_end_index = -1

        # Assume that graphical elements such as lines and labels are handled elsewhere in the class
        if self.fixed_dl is not None:
            self.fixed_dl.reset()
        if self.extended_dl is not None:
            self.extended_dl.reset()

        self.extended_cross_count = 0
        self.body_cross_count = 0
        self.break_dl_window_bar_count = 0

        self.harmony_score = -1.0
        self.deslope_score = -1.0

        self.slope = 0.0
        self.angle = -1.0

        self.overlap_start_bar_index = -1
        self.overlap_end_bar_index = -1

        self.last_signal_bar_index = -1

        self.is_processed = False
        self.is_completed = False
        if not is_two_by_two:
            self.is_b_confirmed = False

    def compute_gradient_and_y_intercept(self):
        if (self.b_bar_index - self.a_bar_index) != 0:  # Prevent division by zero
            self.gradient = (self.b_high - self.a_high) / (self.b_bar_index - self.a_bar_index)
            self.y_intercept = self.a_high - self.gradient * self.a_bar_index
        else:
            self.gradient = float('NaN')  # Handling the undefined case
            self.y_intercept = float('NaN')

    def set_b_bar_and_b_high(self, b_bar_index: int, b_high: float):
        self.b_bar_index = b_bar_index
        self.b_high = b_high
        self.compute_gradient_and_y_intercept()

    def find_flattest_dl_from_a_prime(self, distance_to_a_prime, deslope_ca_multiplier, close_avg_percent, ignore_open_price_bar_count,
                                      dl_break_threshold, min_bar_count, deslope_score_threshold, dl_angle_up_limit, toggle_dl_by_score):
        no_break_deslope_score = float('inf')
        dl_break_deslope_score = float('inf')

        no_break_rescaled_a_bar_index = 0
        no_break_rescaled_a = 0
        no_break_rescaled_b_bar_index = 0
        no_break_rescaled_b = 0

        dl_break_rescaled_a_bar_index = 0
        dl_break_rescaled_a = 0
        dl_break_rescaled_b_bar_index = 0
        dl_break_rescaled_b = 0

        final_rescaled_a_bar_index = 0
        final_rescaled_a = 0
        final_rescaled_b_bar_index = 0
        final_rescaled_b = 0

        dl_horizontal_distance = self.b_bar_index - self.a_bar_index
        cur_a_prime_angle = 0.0

        is_body_high_open = False
        first_ignore_bar_index = 0
        dl_break = False

        for x in range(distance_to_a_prime + 1):
            cur_a_prime_bar_index = self.a_bar_index + x
            cur_a_prime_bar_index_offset = self.bar_index - cur_a_prime_bar_index  # bar_index needs definition or context
            cur_a_prime_angle = 0.0

            for y in range(1, dl_horizontal_distance - x + 1):
                cur_bar_index = cur_a_prime_bar_index + y
                cur_bar_index_offset = self.bar_index - cur_bar_index  # bar_index needs definition or context
                body_high = max(self.open[-cur_bar_index_offset], self.close[-cur_bar_index_offset])  # open and close need definition or context
                current_angle = self.get_angle_with_bars(cur_a_prime_bar_index, cur_bar_index, self.high[-cur_a_prime_bar_index_offset], body_high, deslope_ca_multiplier, close_avg_percent)

                if current_angle >= cur_a_prime_angle:
                    cur_a_prime_angle = current_angle
                    is_body_high_open = self.open[-cur_bar_index_offset] == body_high
                    self.rescaled_a_bar_index = cur_a_prime_bar_index
                    self.rescaled_a = self.high[-cur_a_prime_bar_index_offset]
                    self.rescaled_b_bar_index = cur_bar_index
                    self.rescaled_b = body_high

            self.process_drawing(deslope_ca_multiplier, close_avg_percent)

            if self.is_dl_break(dl_break_threshold, close_avg_percent) and self.pass_validation(min_bar_count, deslope_score_threshold, dl_angle_up_limit):
                if self.deslope_score < dl_break_deslope_score:
                    dl_break_deslope_score = self.deslope_score
                    dl_break_rescaled_a = self.rescaled_a
                    dl_break_rescaled_a_bar_index = self.rescaled_a_bar_index
                    dl_break_rescaled_b = self.rescaled_b
                    dl_break_rescaled_b_bar_index = self.rescaled_b_bar_index
                    dl_break = True
            else:
                if self.deslope_score < no_break_deslope_score:
                    no_break_deslope_score = self.deslope_score
                    no_break_rescaled_a = self.rescaled_a
                    no_break_rescaled_a_bar_index = self.rescaled_a_bar_index
                    no_break_rescaled_b = self.rescaled_b
                    no_break_rescaled_b_bar_index = self.rescaled_b_bar_index

        final_rescaled_a = dl_break_rescaled_a if dl_break_rescaled_a != 0 else no_break_rescaled_a
        final_rescaled_a_bar_index = dl_break_rescaled_a_bar_index if dl_break_rescaled_a_bar_index != 0 else no_break_rescaled_a_bar_index
        final_rescaled_b = dl_break_rescaled_b if dl_break_rescaled_b != 0 else no_break_rescaled_b
        final_rescaled_b_bar_index = dl_break_rescaled_b_bar_index if dl_break_rescaled_b_bar_index != 0 else no_break_rescaled_b_bar_index

        ignore_first_open = dl_horizontal_distance >= ignore_open_price_bar_count and is_body_high_open
        if ignore_first_open:
            first_ignore_bar_index = final_rescaled_b_bar_index

        if first_ignore_bar_index != 0:
            dl_break = False
            for x in range(distance_to_a_prime + 1):
                cur_a_prime_bar_index = self.a_bar_index + x
                cur_a_prime_bar_index_offset = self.bar_index - cur_a_prime_bar_index  # Needs definition or context
                cur_a_prime_angle = 0.0
                no_break_deslope_score = float('inf')
                dl_break_deslope_score = float('inf')

                dl_break_rescaled_a = 0
                dl_break_rescaled_a_bar_index = 0
                dl_break_rescaled_b = 0
                dl_break_rescaled_b_bar_index = 0

                no_break_rescaled_a = 0
                no_break_rescaled_a_bar_index = 0
                no_break_rescaled_b = 0
                no_break_rescaled_b_bar_index = 0

                for y in range(1, dl_horizontal_distance - distance_to_a_prime + 1):
                    cur_bar_index = cur_a_prime_bar_index + y
                    cur_bar_index_offset = self.bar_index - cur_bar_index  # Needs definition or context
                    body_high = max(self.open[-cur_bar_index_offset], self.close[-cur_bar_index_offset])  # Needs definition or context
                    current_angle = self.get_angle_with_bars(cur_a_prime_bar_index, cur_bar_index, self.high[-cur_a_prime_bar_index_offset], body_high, deslope_ca_multiplier, close_avg_percent)

                    if current_angle >= cur_a_prime_angle and cur_bar_index != first_ignore_bar_index:
                        cur_a_prime_angle = current_angle
                        is_body_high_open = self.open[-cur_bar_index_offset] == body_high
                        self.rescaled_a_bar_index = cur_a_prime_bar_index
                        self.rescaled_a = self.high[-cur_a_prime_bar_index_offset]
                        self.rescaled_b_bar_index = cur_bar_index
                        self.rescaled_b = body_high

                self.process_drawing(deslope_ca_multiplier, close_avg_percent)
                if self.pass_cross_validation(self.bar_index) and self.is_dl_break(dl_break_threshold, close_avg_percent) and self.pass_validation(min_bar_count, deslope_score_threshold, dl_angle_up_limit, dl_break_threshold):
                    if self.deslope_score < dl_break_deslope_score:
                        dl_break_deslope_score = self.deslope_score
                        dl_break_rescaled_a = self.rescaled_a
                        dl_break_rescaled_a_bar_index = self.rescaled_a_bar_index
                        dl_break_rescaled_b = self.rescaled_b
                        dl_break_rescaled_b_bar_index = self.rescaled_b_bar_index
                        dl_break = True
                else:
                    if self.deslope_score < no_break_deslope_score:
                        no_break_deslope_score = self.deslope_score
                        no_break_rescaled_a = self.rescaled_a
                        no_break_rescaled_a_bar_index = self.rescaled_a_bar_index
                        no_break_rescaled_b = self.rescaled_b
                        no_break_rescaled_b_bar_index = self.rescaled_b_bar_index

        final_rescaled_a = dl_break_rescaled_a if dl_break_rescaled_a != 0 else no_break_rescaled_a
        final_rescaled_a_bar_index = dl_break_rescaled_a_bar_index if dl_break_rescaled_a_bar_index != 0 else no_break_rescaled_a_bar_index
        final_rescaled_b = dl_break_rescaled_b if dl_break_rescaled_b != 0 else no_break_rescaled_b
        final_rescaled_b_bar_index = dl_break_rescaled_b_bar_index if dl_break_rescaled_b_bar_index != 0 else no_break_rescaled_b_bar_index

        self.rescaled_a_bar_index = final_rescaled_a_bar_index if final_rescaled_a_bar_index != 0 else self.rescaled_a_bar_index
        self.rescaled_a = final_rescaled_a if final_rescaled_a != 0 else self.rescaled_a
        self.rescaled_b_bar_index = final_rescaled_b_bar_index if final_rescaled_b_bar_index != 0 else self.rescaled_b_bar_index
        self.rescaled_b = final_rescaled_b if final_rescaled_b != 0 else self.rescaled_b
        self.process_drawing(deslope_ca_multiplier, close_avg_percent)

        return self.deslope_score, final_rescaled_a_bar_index, final_rescaled_a, final_rescaled_b_bar_index, final_rescaled_b, dl_break


    def find_flattest_dl_from_a(self,distance_to_a_prime, deslope_ca_multiplier, close_avg_percent, ignore_open_price_bar_count,
                                dl_break_threshold, min_bar_count, deslope_score_threshold, dl_angle_up_limit, toggle_dl_by_score):
        rescaled_a_bar_index = self.a_bar_index
        rescaled_a = self.a_high
        rescaled_b_bar_index = 0
        rescaled_b = 0

        dl_horizontal_distance = self.b_bar_index - self.a_bar_index
        cur_a_prime_angle = 0.0

        is_body_high_open = False
        first_ignore_bar_index = 0
        dl_break = False

        for x in range(1, dl_horizontal_distance + 1):
            cur_bar_index = self.a_bar_index + x
            cur_bar_index_offset = self.bar_index - cur_bar_index  # bar_index must be defined elsewhere
            body_high = max(self.open[-cur_bar_index_offset], self.close[-cur_bar_index_offset])  # open and close lists need to be defined

            current_angle = self.get_angle_with_bars(start_index=self.a_bar_index, end_index=cur_bar_index, start_y=self.a_high, end_y=body_high,
                                                     deslope_ca_multiplier=deslope_ca_multiplier, close_avg_percent=close_avg_percent)
            if current_angle >= cur_a_prime_angle:
                cur_a_prime_angle = current_angle
                rescaled_b = body_high
                rescaled_b_bar_index = cur_bar_index
                is_body_high_open = self.open[-cur_bar_index_offset] == body_high

        ignore_first_open = dl_horizontal_distance >= ignore_open_price_bar_count and is_body_high_open
        if ignore_first_open:
            first_ignore_bar_index = rescaled_b_bar_index

        if first_ignore_bar_index != 0:
            cur_a_prime_angle = 0.0
            for x in range(distance_to_a_prime + 1, dl_horizontal_distance + 1):
                cur_bar_index = self.a_bar_index + x
                cur_bar_index_offset = self.bar_index - cur_bar_index

                body_high = max(self.open[-cur_bar_index_offset], self.close[-cur_bar_index_offset])
                current_angle = self.get_angle_with_bars(start_index=self.a_bar_index, end_index=cur_bar_index, start_y=self.a_high, end_y=body_high,
                                                         deslope_ca_multiplier=deslope_ca_multiplier, close_avg_percent=close_avg_percent)

                if current_angle >= cur_a_prime_angle and cur_bar_index != first_ignore_bar_index:
                    rescaled_b = body_high
                    rescaled_b_bar_index = cur_bar_index
                    cur_a_prime_angle = current_angle

        self.rescaled_a_bar_index = self.a_bar_index
        self.rescaled_a = self.a_high
        self.rescaled_b_bar_index = rescaled_b_bar_index
        self.rescaled_b = rescaled_b
        self.process_drawing(deslope_ca_multiplier, close_avg_percent)

        if self.pass_cross_validation(self.bar_index) and self.is_dl_break(dl_break_threshold, close_avg_percent) and self.pass_validation(min_bar_count, deslope_score_threshold, dl_angle_up_limit, dl_break_threshold):
            dl_break = True

        return self.deslope_score, self.a_bar_index, self.a_high, rescaled_b_bar_index, rescaled_b, dl_break

    def rescale_dl_v2(self, b_bar_index_for_distance, distance_percent, deslope_ca_multiplier, close_avg_percent, ignore_open_price_bar_count,
                      dl_break_threshold, min_bar_count, deslope_score_threshold, dl_angle_up_limit, toggle_dl_by_score):
        distance_to_a = math.ceil((b_bar_index_for_distance - self.a_bar_index) * distance_percent)
        from_a_prime = copy.deepcopy(self)
        from_a = copy.deepcopy(self)

        results_a_prime = from_a_prime.find_flattest_dl_from_a_prime(distance_to_a, deslope_ca_multiplier, close_avg_percent,
                                                                     ignore_open_price_bar_count, dl_break_threshold, min_bar_count,
                                                                     deslope_score_threshold, dl_angle_up_limit, toggle_dl_by_score)
        results_a = from_a.find_flattest_dl_from_a(distance_to_a, deslope_ca_multiplier, close_avg_percent,
                                                   ignore_open_price_bar_count, dl_break_threshold, min_bar_count,
                                                   deslope_score_threshold, dl_angle_up_limit, toggle_dl_by_score)

        if results_a_prime[5] and not results_a[5]:
            self.update_rescaled_values(*results_a_prime)
        elif results_a[5] and not results_a_prime[5]:
            self.update_rescaled_values(*results_a)
        else:
            if results_a_prime[0] <= results_a[0]:
                self.update_rescaled_values(*results_a_prime)
            else:
                self.update_rescaled_values(*results_a)

    def update_rescaled_values(self, _, rescaled_a_bar_index, rescaled_a, rescaled_b_bar_index, rescaled_b, __):
        self.rescaled_a = rescaled_a
        self.rescaled_a_bar_index = rescaled_a_bar_index
        self.rescaled_b = rescaled_b
        self.rescaled_b_bar_index = rescaled_b_bar_index

    def rescale_dl(self, b_bar_index_for_distance, distance_percent, toggle_rescale_debug, deslope_ca_multiplier,
                   close_avg_percent, ignore_open_price_bar_count):
        # TODO park for now
        pass

    def process_and_maybe_two_by_zero_signal(self, deslope_ca_multiplier: float, close_avg_percent: float,
                                             dl_angle_up_limit: int, dl_break_threshold: float, extended_cross_threshold: int, toggle_rsi: bool,
                                             min_bar_count: int, extended_cross_uncross_threshold: int, deslope_score_threshold: float, rsi: float,
                                             window_one_rsi_chase_offset: int, window_one_stop_loss_chase_offset: float, window_one_close_chase_offset: float, toggle_reduce_chase: bool,
                                             strong_trend_window_one_rsi_offset: int, final_rsi_long_threshold: float, vip_dl_bar_count: int, vip_dl_score_limit: float,
                                             vip_dl_multiplier: float, rsi_long_threshold: float, vip_dl_rsi_offset: int, in_super_long_trend: bool, key_bar_t_bar_close_offset: float,
                                             key_bar_dl_close_offset: float, key_bar_close_top_percent: int, key_bar_rsi_offset: int, toggle_vip_dl_loose: bool, toggle_key_bar_loose: bool,
                                             toggle_low_t_rsi_adjustment: bool, toggle_low_t_rsi_with_bar_count: bool, low_t_rsi_to_h_rsi_offset: int,
                                             h_rsi_cutoff_percent_on_low_t_rsi: int, low_t_rsi_bar_count: int, toggle_vip_dl_no_reduce_chase: bool, toggle_key_bar_no_reduce_chase: bool,
                                             should_check_against_hrsi: bool, toggle_top_ma_no_reduce_chase: bool) -> Tuple[bool, bool, bool, bool, bool, bool, bool, bool, bool, float]:
        self.rescaled_end_index = self.bar_index
        self.process_drawing(deslope_ca_multiplier, close_avg_percent)
        self.check_dl_crosses(check_end_index=self.bar_index, extended_cross_threshold=extended_cross_threshold, dl_break_threshold=dl_break_threshold, extended_cross_uncross_threshold=extended_cross_uncross_threshold, close_avg_percent=close_avg_percent)

        two_by_zero_signal = False
        is_disabled_by_rsi = False
        is_disabled_by_stop_loss = False
        is_disabled_by_high_close = False
        is_triggered_by_rsi_override = False
        need_update = True
        is_vip_dl_signal = False
        is_key_bar_signal = False
        is_low_t_rsi_signal = False
        latest_rsi_long_threshold = final_rsi_long_threshold

        if self.is_dl_break(dl_break_threshold, close_avg_percent) and self.pass_validation(min_bar_count, deslope_score_threshold, dl_angle_up_limit, check_bar_count=False):
            self.set_export_coordinates()
            results = self.resolve_signal(toggle_vip_dl_loose, toggle_key_bar_loose, vip_dl_bar_count, vip_dl_score_limit, vip_dl_multiplier, latest_rsi_long_threshold, rsi_long_threshold, vip_dl_rsi_offset, in_super_long_trend,
                                        key_bar_t_bar_close_offset, key_bar_dl_close_offset, key_bar_close_top_percent, key_bar_rsi_offset, close_avg_percent, toggle_vip_dl_no_reduce_chase, toggle_key_bar_no_reduce_chase, toggle_top_ma_no_reduce_chase,
                                        toggle_reduce_chase, should_check_against_hrsi, strong_trend_window_one_rsi_offset, window_one_stop_loss_chase_offset, window_one_close_chase_offset, toggle_rsi, rsi,
                                        window_one_rsi_chase_offset, toggle_low_t_rsi_adjustment, toggle_low_t_rsi_with_bar_count, low_t_rsi_to_h_rsi_offset, h_rsi_cutoff_percent_on_low_t_rsi, low_t_rsi_bar_count)

            (two_by_zero_signal, is_low_t_rsi_signal, is_vip_dl_signal, is_key_bar_signal, latest_rsi_long_threshold,
             is_disabled_by_rsi, is_disabled_by_stop_loss, is_disabled_by_high_close, is_triggered_by_rsi_override,
             need_update, signal_source_a_bar_index, rsi_at_signal, bar_count_at_signal, deslope_score_at_signal,
             dl_value_at_signal) = results

            self.is_b_confirmed = True
            self.is_completed = True
            self.last_signal_bar_index = self.bar_index

        return (two_by_zero_signal, is_disabled_by_rsi, is_disabled_by_stop_loss, is_disabled_by_high_close, is_triggered_by_rsi_override, need_update,
                is_vip_dl_signal, is_key_bar_signal, is_low_t_rsi_signal, latest_rsi_long_threshold)

    def process_drawing(self, deslope_ca_multiplier: float, close_avg_percent: float):
        # Extract rescaled points and indices
        rescaled_a_bar_index = self.rescaled_a_bar_index
        rescaled_a = self.rescaled_a
        rescaled_b_bar_index = self.rescaled_b_bar_index
        rescaled_b = self.rescaled_b

        # Update rescaled gradient and y-intercept
        if rescaled_a_bar_index == rescaled_b_bar_index:
            return

        self.rescaled_gradient = (rescaled_b - rescaled_a) / (rescaled_b_bar_index - rescaled_a_bar_index)
        self.rescaled_y_intercept = rescaled_a - self.rescaled_gradient * rescaled_a_bar_index

        # Additional calculations for diagonal line properties
        horizontal_distance = (rescaled_b_bar_index - rescaled_a_bar_index) * (deslope_ca_multiplier * close_avg_percent)
        percent_move = ((rescaled_a - rescaled_b) / rescaled_a) * 100
        if percent_move == 0:
            cur_dl_tan = math.tan(90)
            cur_dl_angle = 90
        else:
            cur_dl_tan = horizontal_distance / percent_move
            cur_dl_angle = math.atan(cur_dl_tan)

        # Calculate scores
        deslope_score, harmony_score = self.calculate_deslope_score(close_avg_percent, cur_dl_angle)
        self.calculate_dl_bar_count_v3()

        # Additional condition checks and logging
        if self.bar_count == 2:
            # logging.info("two bar DL detected, setting score to 10000")
            deslope_score = 10000

        if round(cur_dl_angle * (180 / math.pi), 1) < 0:
            # logging.info("negative angle detected, setting score to 10000")
            deslope_score = 10000

        # Update diagonal line properties
        self.slope = round(1 / cur_dl_tan, 2)
        self.deslope_score = round(deslope_score, 2)
        self.harmony_score = round(harmony_score, 2)
        self.angle = round(cur_dl_angle * (180 / math.pi), 1)
        self.is_processed = True

    def calculate_deslope_score(self, close_avg_percent: float, angle: float) -> Tuple[float, float]:
        rescaled_a_bar_index = self.rescaled_a_bar_index
        self.overlap_start_bar_index = rescaled_a_bar_index
        dl_horizontal_distance = self.b_bar_index - rescaled_a_bar_index

        total_deslope_diff = 0.0
        total_diff = 0.0
        bar_count = 0

        for x in range(1, dl_horizontal_distance + 1):
            cur_bar_index = rescaled_a_bar_index + x
            cur_bar_index_offset = self.bar_index - cur_bar_index
            body_high = max(self.open[-cur_bar_index_offset], self.close[-cur_bar_index_offset])
            dl_value = self.get_rescaled_y_with_bar_index(cur_bar_index)

            # Check if the last bar and it breaks DL, then don't count
            if x == dl_horizontal_distance and not self.is_close(body_high, dl_value) and body_high > dl_value:
                continue

            y_value = self.get_rescaled_y_with_bar_index(cur_bar_index)
            high_value = self.high[-cur_bar_index_offset]
            deslope_diff = abs((y_value - high_value) * math.sin(angle))
            diff = abs(y_value - high_value)

            total_deslope_diff += deslope_diff
            total_diff += diff
            bar_count += 1
            self.overlap_end_bar_index = cur_bar_index

        # Calculation of scores
        ca = close_avg_percent * 0.01 * self.close[-(self.bar_index - rescaled_a_bar_index)]
        deslope_score = (total_deslope_diff / bar_count) / ca if bar_count > 0 else 0
        harmony_score = (total_diff / bar_count) / ca if bar_count > 0 else 0

        return deslope_score, harmony_score

    def is_close(self, a, b, rel_tol=0.0000000001):
        less = min(a, b)
        more = max(a, b)

        return (more / less - 1) < rel_tol if self.use_rounding_value and less != 0 else False

    def get_angle_with_bars(self, start_index: int, end_index: int, start_y: float, end_y: float, deslope_ca_multiplier: float, close_avg_percent: float) -> float:

        if start_y == end_y:
            return 90

        horizontal_distance = (end_index - start_index) * (deslope_ca_multiplier * close_avg_percent)
        percent_move = ((start_y - end_y) / start_y) * 100 if start_y != 0 else 0  # Guard against division by zero

        cur_dl_tan = horizontal_distance / percent_move if percent_move != 0 else 0  # Guard against division by zero
        cur_dl_angle = math.atan(cur_dl_tan)  # Calculate the arctangent of the tangent
        cur_dl_angle_degree = round(cur_dl_angle * (180 / math.pi), 1)  # Convert radians to degrees and round

        # Adjust the result if angle is between -90 and 0 degrees
        result = cur_dl_angle_degree if not (-90 < cur_dl_angle_degree < 0) else 180 + cur_dl_angle_degree

        return result

    def pass_cross_validation(self, check_end_index: int) -> bool:
        rescale_check_length = check_end_index - self.rescaled_a_bar_index
        pass_validation = True  # Start assuming the line passes validation

        for x in range(1, rescale_check_length + 1):
            cur_bar_index = self.rescaled_a_bar_index + x
            cur_bar_index_offset = check_end_index - cur_bar_index

            if self.cross_rescaled_dl(cur_bar_index_offset):
                pass_validation = False
                break  # Exit the loop early if a cross is detected

        return pass_validation

    def is_dl_break_non_two_by(self, non_two_by_dl_break_threshold: float, close_avg_percent: float, is_quick_ma_up: bool, is_slow_ma_up: bool, bar_index_offset: int = 0, break_only: bool = True) -> bool:
        is_broken = False

        if not math.isnan(self.rescaled_gradient) and not math.isnan(self.rescaled_y_intercept):
            dl_value = self.get_rescaled_y_with_bar_index(self.bar_index - bar_index_offset)
            if ((self.close[-bar_index_offset] / dl_value) - 1) > (close_avg_percent * non_two_by_dl_break_threshold * 0.01) or (not break_only and is_quick_ma_up and is_slow_ma_up):
                is_broken = True

        return is_broken

    def ready_to_draw(self):
        ready = False
        if (self.rescaled_a_bar_index != -1 and self.rescaled_a != -1 and
            self.rescaled_b_bar_index != -1 and self.rescaled_b != -1 and
            not self.is_completed):
            ready = True
        return ready

    def ready_for_export(self):
        ready = False
        if (self.rescaled_a_bar_index != -1 and self.rescaled_a != -1 and
            self.rescaled_b_bar_index != -1 and self.rescaled_b != -1 and self.is_completed):
            # self.rescaled_b_bar_index != -1 and self.rescaled_b != -1): # and self.is_completed):
            ready = True
        return ready

    def ready_for_export_v2(self):
        ready = False
        if not math.isnan(self.x1) and not math.isnan(self.y1) and not math.isnan(self.x2) and not math.isnan(self.y2):
            ready = True
        return ready

    def copy_all_from(self, source_dl: 'DiagnalLine'):
        self.a_bar_index = source_dl.a_bar_index
        self.a_prime_bar_index = source_dl.a_prime_bar_index
        self.a_double_prime_bar_index = source_dl.a_double_prime_bar_index

        self.b_bar_index = source_dl.b_bar_index
        self.b_prime_bar_index = source_dl.b_prime_bar_index

        self.a_high = source_dl.a_high
        self.a_body_high = source_dl.a_body_high
        self.a_prime_high = source_dl.a_prime_high
        self.a_prime_rescale_high = source_dl.a_prime_rescale_high
        self.a_double_prime_high = source_dl.a_double_prime_high
        self.a_double_prime_rescale_high = source_dl.a_double_prime_rescale_high

        self.b_high = source_dl.b_high
        self.b_prime_high = source_dl.b_prime_high
        self.b_prime_rescale_high = source_dl.b_prime_rescale_high

        self.gradient = source_dl.gradient
        self.y_intercept = source_dl.y_intercept

        self.rescaled_gradient = source_dl.rescaled_gradient
        self.rescaled_y_intercept = source_dl.rescaled_y_intercept
        self.rescaled_a_bar_index = source_dl.rescaled_a_bar_index
        self.rescaled_a = source_dl.rescaled_a
        self.rescaled_b_bar_index = source_dl.rescaled_b_bar_index
        self.rescaled_b = source_dl.rescaled_b
        self.rescaled_end_index = source_dl.rescaled_end_index

        self.is_completed = source_dl.is_completed
        self.is_changed = source_dl.is_changed
        self.is_b_confirmed = source_dl.is_b_confirmed
        self.is_two_by_zero = source_dl.is_two_by_zero
        self.last_bar_has_signal = source_dl.last_bar_has_signal
        self.over_bought = source_dl.over_bought
        self.is_processed = source_dl.is_processed

        # original DL without rescaling
        self.fixed_dl = source_dl.fixed_dl
        self.extended_dl = source_dl.extended_dl

        # rescaled DL
        self.rescaled_dl = source_dl.rescaled_dl
        self.rescaled_extended = source_dl.rescaled_extended
        self.rescaled_to_a = source_dl.rescaled_to_a

        self.extended_cross_count = source_dl.extended_cross_count
        self.body_cross_count = source_dl.body_cross_count
        self.break_dl_window_bar_count = source_dl.break_dl_window_bar_count
        self.last_signal_bar_index = source_dl.last_signal_bar_index

        self.harmony_score = source_dl.harmony_score
        self.deslope_score = source_dl.deslope_score

        self.slope = source_dl.slope
        self.angle = source_dl.angle
        self.rsi = source_dl.rsi

        self.overlap_start_bar_index = source_dl.overlap_start_bar_index
        self.overlap_end_bar_index = source_dl.overlap_end_bar_index
        self.bar_count_end_index = source_dl.bar_count_end_index
        self.bar_count = source_dl.bar_count

        self.short_dl_break_bar_index = source_dl.short_dl_break_bar_index
        self.cur_by_point_low = source_dl.cur_by_point_low

    def is_short_dl_break(self, toggle_short_dl: bool, short_dl_break_threshold: float, close_avg_percent: float) -> bool:

        should_check_short_dl = toggle_short_dl and self.bar_count == 3
        short_dl_break = self.is_processed and self.is_dl_break(0, close_avg_percent)
        long_fourth_bar = ((self.close[0] / self.low[-1]) - 1) > (short_dl_break_threshold * close_avg_percent * 0.01)

        return should_check_short_dl and short_dl_break and long_fourth_bar

    def need_to_reset(self, right_bars):
        should_reset = False
        if self.high[0] >= self.a_high != -1:
            should_reset = True
        return should_reset

    def set_export_coordinates(self):
        self.x1 = self.a_bar_index
        self.y1 = self.get_rescaled_y_with_bar_index(self.a_bar_index)
        self.x2 = self.rescaled_end_index
        self.y2 = self.get_rescaled_y_with_bar_index(self.rescaled_end_index)


@dataclass
class DiagonalLineWrapper:
    current: DiagonalLine = None
    rollback: DiagonalLine = None


@dataclass
class SignalWrapper:
    two_by_zero_signal: bool = False
    buy_signal: bool = False
    dl_break_signal: bool = False

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

    is_vip_dl_signal: bool = False
    is_key_bar_signal: bool = False
    is_low_t_rsi_signal: bool = False

    latest_rsi_long_threshold: float = -1.0
    rsi_at_signal: float = -1.0
    bar_count_at_signal: int = 0
    deslope_score_at_signal: float = -1.0
    dl_value_at_signal: float = -1.0
