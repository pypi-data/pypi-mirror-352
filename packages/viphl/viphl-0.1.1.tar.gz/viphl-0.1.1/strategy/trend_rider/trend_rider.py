import math
import backtrader as bt
import pandas as pd

from datetime import datetime
from typing import Tuple, List

from dto.threshold import Threshold, ThresholdType
from tvDatafeed import TvDatafeed, Interval
from backtrader import num2date, date2num
from dto.trade_v2 import TradeV2
from indicators.helper.bar_pattern import close_at_bar_bottom_by_percent, close_at_bar_top_by_percent
from indicators.helper.close_average import CloseAveragePercent
from indicators.helper.percentile_nearest_rank import PercentileNearestRank
from indicators.hl.hl_v4_indicator import HLv4Indicator
from indicators.dl.dl_v1_9_indicator import DLv1_9Indicator


# Create a subclass of Strategy to define the indicators and logic

FIT_SCORE_MAX = 500
TICKER_NAME = "ETH"
TIMEFRAME = '6H'

class TrendRider(bt.Strategy):
    # list of parameters which are configurable for the strategy
    params = (
        ('pfast', 10),  # period for the fast moving average
        ('pslow', 40),   # period for the slow moving average
        ('printlog', False),

        ('toggle_rsi', True),
        ('toggle_ma', True),
        ('toggle_dl_by_score', True),
        ('toggle_short_dl', True),
        ('use_date_range', False),
        ('export', False),

        # ---------trade inputs-------
        ('order_size_in_usd', 2000000),  # Equivalent to orderSizeInUSD
        ('cycle_month', 3.0),  # Equivalent to cycleMonth
        ('stop_loss_pt', 1.0),  # Equivalent to stopLossPt
        ('first_gain_ca_multiplier', 2.0),  # Equivalent to firstGainCAMultiplier
        ('max_gain_pt', 50.0),  # Equivalent to maxGainPt
        ('max_exit_ca_multiplier', 4.0),  # Equivalent to maxExitCAMultiplier
        ('stop_gain_pt', 30.0),  # Equivalent to stopGainPt
        ('toggle_pnl', True),

        # ---------entry point inputs-------
        ('entry_point_hl_threshold', 0.0),  # Minimum CA% for a bar to be considered stable on HL
        ('pullback_threshold', 0.5),  # Minimum CA% for a low pullback to approach HL
        ('close_threshold', 30),
        ('toggle_close_low', False),

        # ----------hl input------------
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

        # nbym inputs
        ('left_bars', 2),
        ('right_bars', 2),

        # DL inputs
        ('lookback', 600),
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

        # --------close average pt inputs------
        ('close_avg_percent_lookback', 500),  # Lookback period for close average calculation
        ('toggle_pp_threshold_overwrite', False),  # Overwrite threshold percentage for by-points
        ('pp_threshold_overwrite', 0.25),  # Threshold percentage for by-points
        ('default_ca_threshold_multiplier_his', 2.0),  # Default historical CA% multiplier
        ('default_ca_threshold_multiplier_pre', 1.0),  # Default present CA% multiplier

        # low t-rsi adjustment
        ('toggle_low_trsi_adjustment', False),
        ('toggle_low_trsi_with_bar_count', False),
        ('low_trsi_to_hrsi_offset', 10),
        ('hrsi_cutoff_percent_on_low_trsi', 50),
        ('low_trsi_bar_count', 5),

        # Reduce chasing inputs
        ('toggle_reduce_chase', False),
        ('window_one_rsi_chase_offset', 30),
        ('window_one_stop_loss_chase_offset', 4),
        ('window_one_close_chase_offset', 30),
        ('window_two_rsi_chase_offset', 30),
        ('window_two_stop_loss_chase_offset', 4),
        ('window_two_close_chase_offset', 30),

        # New High RSI filter
        ('toggle_new_high_loose', False),
        ('prev_high_lookback', 120),
        ('bar_count_to_prev_high', 6),
        ('new_high_ma_offset_pt', 10),
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
        ('vip_dl_ma_offset_pt', 25),
        ('vip_dl_rsi_offset', 5),

        # Key bar filters
        ('toggle_key_bar_loose', False),
        ('toggle_key_bar_no_reduce_chase', False),
        ('key_bar_t_bar_close_offset', 1),
        ('key_bar_dl_close_offset', 1),
        ('key_bar_close_top_percent', 25),
        ('key_bar_ma_offset_pt', 25),
        ('key_bar_rsi_offset', 5),

        # VIP HL inputs
        ('toggle_vip_hl_loose', False),
        ('vip_hl_rank', 2),
        ('vip_hl_score', 20.0),
        ('vip_hl_ma_offset_pt', 25),
        ('vip_hl_rsi_offset', 0),

        # Weak MA Filter
        ('toggle_weak_ma_filter', False),
        ('toggle_filter_positive_ma', True),
        ('weak_ma_length', 10),
        ('weak_ma_pt', 80),

        # MA trends inputs
        ('ma_lookback_period', 500),
        ('ma_length', 40),
        ('long_trend_threshold_up', 0),
        ('long_trend_threshold_low', 35),

        # RSI inputs
        ('rsi_length', 14),
        ('rsi_lookback', 1),
        ('rsi_long_threshold', 65),
    )

    def log(self, txt, dt=None, doprint=True):
        ''' Logging function fot this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        '''init is called once at the last row'''

        self.hlv4 = HLv4Indicator(
            lookback=self.p.lookback,
            max_num_sr=self.p.max_num_sr,
            month_period1=self.p.month_period1,
            month_period2=self.p.month_period2,
            month_period3=self.p.month_period3,
            month_period4=self.p.month_period4,
            first_weight_multiplier=self.p.first_weight_multiplier,
            second_weight_multiplier=self.p.second_weight_multiplier,
            pt_weight1=self.p.pt_weight1,
            pt_weight2=self.p.pt_weight2,
            pt_weight3=self.p.pt_weight3,
            pt_weight4=self.p.pt_weight4,
            close_avg_percent_lookback=self.p.close_avg_percent_lookback,
            toggle_pp_threshold_overwrite=self.p.toggle_pp_threshold_overwrite,
            pp_threshold_overwrite=self.p.pp_threshold_overwrite,
            default_ca_threshold_multiplier_his=self.p.default_ca_threshold_multiplier_his,
            default_ca_threshold_multiplier_pre=self.p.default_ca_threshold_multiplier_pre,
            entry_point_hl_threshold=self.p.entry_point_hl_threshold,
            pullback_threshold=self.p.pullback_threshold,
            vip_hl_rank=self.p.vip_hl_rank,
            vip_hl_score=self.p.vip_hl_score
        )
        self.dl = DLv1_9Indicator(
            hlv4=self.hlv4,
            toggle_rsi=self.p.toggle_rsi,
            toggle_dl_by_score=self.p.toggle_dl_by_score,
            toggle_short_dl=self.p.toggle_short_dl,
            use_date_range=self.p.use_date_range,
            left_bars=self.p.left_bars,
            right_bars=self.p.right_bars,
            lookback=self.p.lookback,
            min_bar_count=self.p.min_bar_count,
            dl_break_threshold=self.p.dl_break_threshold,
            non_two_by_dl_break_threshold=self.p.non_two_by_dl_break_threshold,
            short_dl_break_threshold=self.p.short_dl_break_threshold,
            extended_cross_threshold=self.p.extended_cross_threshold,
            extended_cross_uncross_threshold=self.p.extended_cross_uncross_threshold,
            distance_to_a_prime_percent=self.p.distance_to_a_prime_percent,
            long_trend_threshold=self.p.long_trend_threshold,
            min_bar_count_on_trend=self.p.min_bar_count_on_trend,
            dl_angle_up_limit=self.p.dl_angle_up_limit,
            ignore_open_price_bar_count=self.p.ignore_open_price_bar_count,
            strong_bar_multiplier=self.p.strong_bar_multiplier,
            close_top_percent=self.p.close_top_percent,
            signal_window_bar_count=self.p.signal_window_bar_count,
            deslope_score_threshold=self.p.deslope_score_threshold,
            deslope_ca_multiplier=self.p.deslope_ca_multiplier,
            close_avg_percent_lookback=self.p.close_avg_percent_lookback,
            toggle_low_trsi_adjustment=self.p.toggle_low_trsi_adjustment,
            toggle_low_trsi_with_bar_count=self.p.toggle_low_trsi_with_bar_count,
            low_trsi_to_hrsi_offset=self.p.low_trsi_to_hrsi_offset,
            hrsi_cutoff_percent_on_low_trsi=self.p.hrsi_cutoff_percent_on_low_trsi,
            low_trsi_bar_count=self.p.low_trsi_bar_count,
            toggle_reduce_chase=self.p.toggle_reduce_chase,
            window_one_rsi_chase_offset=self.p.window_one_rsi_chase_offset,
            window_one_stop_loss_chase_offset=self.p.window_one_stop_loss_chase_offset,
            window_one_close_chase_offset=self.p.window_one_close_chase_offset,
            window_two_rsi_chase_offset=self.p.window_two_rsi_chase_offset,
            window_two_stop_loss_chase_offset=self.p.window_two_stop_loss_chase_offset,
            window_two_close_chase_offset=self.p.window_two_close_chase_offset,
            toggle_new_high_loose=self.p.toggle_new_high_loose,
            prev_high_lookback=self.p.prev_high_lookback,
            bar_count_to_prev_high=self.p.bar_count_to_prev_high,
            new_high_rsi_long_threshold=self.p.new_high_rsi_long_threshold,
            new_high_window_one_rsi_offset=self.p.new_high_window_one_rsi_offset,
            new_high_window_two_rsi_offset=self.p.new_high_window_two_rsi_offset,
            toggle_top_ma_loose=self.p.toggle_top_ma_loose,
            toggle_positive_ma_delta=self.p.toggle_positive_ma_delta,
            toggle_top_ma_no_reduce_chase=self.p.toggle_top_ma_no_reduce_chase,
            ma10_top_pt=self.p.ma10_top_pt,
            ma40_top_pt=self.p.ma40_top_pt,
            top_ma_rsi_long_threshold=self.p.top_ma_rsi_long_threshold,
            top_ma_window_one_rsi_offset=self.p.top_ma_window_one_rsi_offset,
            top_ma_window_two_rsi_offset=self.p.top_ma_window_two_rsi_offset,
            toggle_vip_dl_loose=self.p.toggle_vip_dl_loose,
            toggle_vip_dl_no_reduce_chase=self.p.toggle_vip_dl_no_reduce_chase,
            vip_dl_bar_count=self.p.vip_dl_bar_count,
            vip_dl_score_limit=self.p.vip_dl_score_limit,
            vip_dl_multiplier=self.p.vip_dl_multiplier,
            vip_dl_rsi_offset=self.p.vip_dl_rsi_offset,
            toggle_key_bar_loose=self.p.toggle_key_bar_loose,
            toggle_key_bar_no_reduce_chase=self.p.toggle_key_bar_no_reduce_chase,
            key_bar_t_bar_close_offset=self.p.key_bar_t_bar_close_offset,
            key_bar_dl_close_offset=self.p.key_bar_dl_close_offset,
            key_bar_close_top_percent=self.p.key_bar_close_top_percent,
            key_bar_rsi_offset=self.p.key_bar_rsi_offset,
            toggle_vip_hl_loose=self.p.toggle_vip_hl_loose,
            vip_hl_rsi_offset=self.p.vip_hl_rsi_offset,
            ma_lookback_period=self.p.ma_lookback_period,
            ma_length=self.p.ma_length,
            rsi_length=self.p.rsi_length,
            rsi_lookback=self.p.rsi_lookback,
            rsi_long_threshold=self.p.rsi_long_threshold
        )
        self.lines_info = []
        self.dl_lines_info = []

        self.close_average_percent = CloseAveragePercent(close_avg_percent_lookback=self.p.close_avg_percent_lookback)
        self.offset_to_local_high = bt.ind.FindLastIndexHighest(self.data.high, period=(self.p.bar_count_to_prev_high + 1))
        self.offset_to_local_high.plotinfo.plot = False

        # ------RSI------
        self.rsi = bt.ind.RSI(self.datas[0], period=self.p.rsi_length)

        # --------MA distribution calc------
        self.ma = bt.indicators.SMA(self.data.close, period=self.p.ma_length)
        self.ma100 = bt.indicators.SMA(self.data.close, period=100)
        self.quick_ma = bt.indicators.SMA(self.data.close, period=10)
        self.weak_ma = bt.indicators.SMA(self.data.close, period=self.p.weak_ma_length)

        self.ma_delta = bt.indicators.ROC(self.ma, period=1)
        self.quick_ma_delta = bt.indicators.ROC(self.quick_ma, period=1)
        self.weak_ma_delta = bt.indicators.ROC(self.weak_ma, period=1)
        self.ma_delta.plotinfo.plot = False
        self.quick_ma_delta.plotinfo.plot = False
        self.weak_ma_delta.plotinfo.plot = False

        # need to deprecate this ##########
        self.top_delt_bound = PercentileNearestRank(self.ma_delta.roc, period=self.p.ma_lookback_period,
                                                    percentile=100 - self.p.long_trend_threshold)
        # need to deprecate this ##########

        self.up_delta_bound = PercentileNearestRank(self.ma_delta.roc, period=self.p.ma_lookback_period,
                                                    percentile=100 - self.p.long_trend_threshold_up)
        self.base_low_delta_bound = PercentileNearestRank(self.ma_delta.roc, period=self.p.ma_lookback_period,
                                                     percentile=100 - self.p.long_trend_threshold_low)

        # extreme uptrend
        self.quick_ma_super_low_delta_bound = PercentileNearestRank(self.quick_ma_delta.roc,
                                                                    period=self.p.ma_lookback_period,
                                                                    percentile=100 - self.p.ma10_top_pt)
        self.slow_ma_super_low_delta_bound = PercentileNearestRank(self.ma_delta.roc, period=self.p.ma_lookback_period,
                                                                   percentile=100 - self.p.ma40_top_pt)

        # weak ma filter
        self.weak_ma_low_delta_bound = PercentileNearestRank(self.weak_ma_delta.roc, period=self.p.ma_lookback_period,
                                                          percentile=100 - self.p.weak_ma_pt)

        # VIP HL loose filter
        combined_vip_hl_ma_threshold = self.p.long_trend_threshold_low + self.p.vip_hl_ma_offset_pt
        self.vip_hl_ma_threshold_low: int = (
            100 if combined_vip_hl_ma_threshold > 100
            else 0 if combined_vip_hl_ma_threshold < 0
            else combined_vip_hl_ma_threshold
        )
        self.vip_hl_low_delta_bound = PercentileNearestRank(self.ma_delta.roc, period=self.p.ma_lookback_period,
                                                            percentile=100 - self.vip_hl_ma_threshold_low)

        # New high loose filter
        combined_new_high_ma_threshold_low = self.p.long_trend_threshold_low + self.p.new_high_ma_offset_pt
        self.new_high_ma_threshold_low: int = (
            100 if combined_new_high_ma_threshold_low > 100
            else 0 if combined_new_high_ma_threshold_low < 0
            else combined_new_high_ma_threshold_low
        )
        self.new_high_low_delta_bound = PercentileNearestRank(self.ma_delta.roc, period=self.p.ma_lookback_period,
                                                              percentile=100 - self.new_high_ma_threshold_low)

        # vip dl loose filter
        combined_vip_dl_ma_threshold_low = self.p.long_trend_threshold_low + self.p.vip_dl_ma_offset_pt
        self.vip_dl_ma_threshold_low: int = (
            100 if combined_vip_dl_ma_threshold_low > 100
            else 0 if combined_vip_dl_ma_threshold_low < 0
            else combined_vip_dl_ma_threshold_low
        )
        self.vip_dl_low_delta_bound = PercentileNearestRank(self.ma_delta.roc, period=self.p.ma_lookback_period,
                                                              percentile=100 - self.vip_dl_ma_threshold_low)

        # key bar loose filter
        combined_key_bar_ma_threshold_low = self.p.long_trend_threshold_low + self.p.key_bar_ma_offset_pt
        self.key_bar_ma_threshold_low: int = (
            100 if combined_key_bar_ma_threshold_low > 100
            else 0 if combined_key_bar_ma_threshold_low < 0
            else combined_key_bar_ma_threshold_low
        )
        self.key_bar_low_delta_bound = PercentileNearestRank(self.ma_delta.roc, period=self.p.ma_lookback_period,
                                                            percentile=100 - self.key_bar_ma_threshold_low)

        # trade management
        self.max_equity: float = 0.0
        self.current_equity: float = 0.0
        self.max_drawdown: float = 0.0
        self.cur_drawdown: float = 0.0
        self.total_pnl: float = 0.0

        # For tracking trades
        self.trade_list = []

        # For exporting data
        self.csv_export_list = []

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    f'BUY EXECUTED at {self.bar_index()}, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log(f'SELL EXECUTED at {self.bar_index()}, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        '''next is called only after all data loading is completed for indicators
           for example, next is only call on the 40th bar if indicators contain
           ma 40

           quoted form doc: 'next will be 1st called when all indicators have already reached
           the minimum needed period to produce a value'

           this is where we specify the buy condition, for trend rider,
           it would be
           1. isHlSatisfied and
           2. has dl signals
        '''
        # if self.hlv4.l.is_hl_satisfied[0] == 1:
        #     print(f'hl supported at bar index {len(self)} with sr value {self.hlv4.l.cur_sr_value[0]}, final bar is {self.buflen()}, '
        #         f'low[-1] is {self.data.low[-1]} and low[-2] is {self.data.low[-2]} and close[0] is {self.data.close[0]}')

        '''
            fetching HL condition
        '''
        is_hl_satisfied: bool = self.hlv4.l.is_hl_satisfied[0] == 1
        is_vip_hl_score: bool = self.hlv4.l.is_vip_hl_score[0] == 1
        is_vip_hl_rank: bool = self.hlv4.l.is_vip_hl_rank[0] == 1
        cur_sr_value: float = self.hlv4.l.cur_sr_value[0]
        cur_hl_score: float = self.hlv4.l.cur_hl_score[0]

        # -------vip HL loose filter----------
        is_vip_hl: bool = is_vip_hl_rank or is_vip_hl_score
        should_loose_vip_hl = is_vip_hl and self.p.toggle_vip_hl_loose
        vip_hl_rsi_long_threshold: int = self.p.rsi_long_threshold + self.p.vip_hl_rsi_offset
        vip_hl_rsi_long_threshold_v2: Threshold = Threshold(
            base=self.p.rsi_long_threshold, offset=self.p.vip_hl_rsi_offset, type=ThresholdType.offset
        )
        vip_hl_rsi_normalised = vip_hl_rsi_long_threshold_v2.value()

        '''
            new high loose filter
        '''
        offset_to_max_prev_high = abs(self.highest_bars(self.data.high, self.p.prev_high_lookback + abs(int(self.offset_to_local_high[0])) + 1))
        is_local_high_global: bool = self.offset_to_local_high[0] == offset_to_max_prev_high
        should_loose_new_high: bool = (is_local_high_global and self.p.toggle_new_high_loose)

        '''
            vip DL loose filter
        '''
        vip_dl_rsi_long_threshold: int = self.p.rsi_long_threshold + self.p.vip_dl_rsi_offset

        '''
            key bar loose filter
        '''
        key_bar_rsi_long_threshold: int = self.p.rsi_long_threshold + self.p.key_bar_rsi_offset

        '''
            min bar count logic(need to deprecate)
        '''
        is_trending_positive: bool = self.p.long_trend_threshold == 100 or self.ma_delta[0] > self.top_delta_bound[0]
        is_long_trend: bool = is_trending_positive

        min_bar_count: int = self.p.min_bar_count_on_trend if is_long_trend else self.p.min_bar_count

        '''
            extreme uptrend
        '''
        is_quick_ma_up: bool = self.quick_ma_delta[0] > 0 if self.p.toggle_positive_ma_delta else True
        is_slow_ma_up: bool = self.ma_delta[0] > 0 if self.p.toggle_positive_ma_delta else True

        in_super_long_trend: bool = ((self.quick_ma_delta[0] >= self.quick_ma_super_low_delta_bound[0]) and
                                     is_quick_ma_up and (self.ma_delta[0] > self.slow_ma_super_low_delta_bound[0]) and
                                     self.p.toggle_top_ma_loose and is_slow_ma_up)

        '''
            rsi validation
        '''
        final_rsi_long_threshold: int = max(
            self.p.rsi_long_threshold,
            vip_hl_rsi_long_threshold if should_loose_vip_hl else 0,
            self.p.new_high_rsi_long_threshold if should_loose_new_high else 0,
            self.p.top_ma_rsi_long_threshold if in_super_long_trend else 0
        )

        buy_signal: bool = self.dl.l.buy_signal[0] == 1
        two_by_zero_signal: bool = self.dl.l.two_by_zero_signal[0] == 1
        dl_break_signal: bool = self.dl.l.dl_break_signal[0] == 1
        hrsi_at_signal: float = self.dl.l.rsi_at_signal[0]
        bar_count_at_signal: int = self.dl.l.bar_count_at_signal[0]
        deslope_score_at_signal: float = self.dl.l.deslope_score_at_signal[0]
        dl_value_at_signal: float = self.dl.l.dl_value_at_signal[0]

        vip_dl_signal: bool = self.dl.l.is_vip_dl_signal[0] == 1
        should_loose_vip_dl: bool = self.p.toggle_vip_dl_loose and vip_dl_signal

        key_bar_signal: bool = self.dl.l.is_key_bar_signal[0] == 1
        should_loose_key_bar: bool = self.p.toggle_key_bar_loose and key_bar_signal

        low_t_rsi_signal: bool = self.dl.l.is_low_t_rsi_signal[0] == 1
        should_loose_low_t_rsi: bool = self.p.toggle_low_trsi_adjustment and low_t_rsi_signal

        final_rsi_long_threshold = self.dl.l.latest_rsi_long_threshold[0]

        # Determine if the signal is triggered by any override
        signal_triggered_by_override = (
            self.dl.l.is_buy_signal_triggered_by_rsi_override[0] == 1 or
            self.dl.l.is_two_by_zero_triggered_by_rsi_override[0] == 1 or
            self.dl.l.is_dl_break_triggered_by_rsi_override[0] == 1
        )

        # Determine each override condition
        is_rsi_overridden_by_vip_hl = (
            should_loose_vip_hl and
            vip_hl_rsi_long_threshold <= final_rsi_long_threshold and
            (signal_triggered_by_override or
            (self.dl.l.rsi_at_signal != -1.0 and self.dl.l.rsi_at_signal[0] <= vip_hl_rsi_long_threshold))
        )

        is_rsi_overridden_by_new_high = (
            should_loose_new_high and
            self.p.new_high_rsi_long_threshold <= final_rsi_long_threshold and
            (signal_triggered_by_override or
            (self.dl.l.rsi_at_signal != -1.0 and self.dl.l.rsi_at_signal[0] <= self.p.new_high_rsi_long_threshold))
        )

        is_rsi_overridden_by_vip_dl = (
            should_loose_vip_dl and
            vip_dl_rsi_long_threshold <= final_rsi_long_threshold and
            (signal_triggered_by_override or
             (self.dl.l.rsi_at_signal != -1.0 and self.dl.l.rsi_at_signal[0] <= self.vip_dl_rsi_long_threshold))
        )

        is_rsi_overridden_by_key_bar = (
            should_loose_key_bar and
            key_bar_rsi_long_threshold <= final_rsi_long_threshold and
            (signal_triggered_by_override or
             (self.dl.l.rsi_at_signal != -1.0 and self.dl.l.rsi_at_signal[0] <= key_bar_rsi_long_threshold))
        )

        conditions: List[bool] = [
            should_loose_new_high,
            should_loose_vip_hl,
            should_loose_vip_dl,
            should_loose_key_bar
        ]

        ma_threshold_lows: List[int] = [
            self.new_high_ma_threshold_low,
            self.vip_hl_ma_threshold_low,
            self.vip_dl_ma_threshold_low,
            self.key_bar_ma_threshold_low
        ]

        condition_low_delta_bounds: List[float] = [
            self.new_high_low_delta_bound[0],
            self.vip_hl_low_delta_bound[0],
            self.vip_dl_low_delta_bound[0],
            self.key_bar_low_delta_bound[0]
        ]

        final_low_delta_bound = self.zip_for_first_condition_low_delta_bound(
            conditions, ma_threshold_lows, condition_low_delta_bounds, self.p.long_trend_threshold_low, self.ma_delta[0]
        )

        in_trending_positive_range: bool = (self.ma_delta[0] >= final_low_delta_bound) and (True if self.p.long_trend_threshold_up == 0 else self.ma_delta[0] <= self.up_delta_bound[0])
        in_long_trend_range: bool = True if in_super_long_trend else in_trending_positive_range
        should_kill_all_signal: bool = (self.p.toggle_weak_ma_filter and self.weak_ma_delta[0] <= self.weak_ma_low_delta_bound[0]
                                        and (True if self.p.toggle_filter_positive_ma else self.weak_ma_delta[0] < 0))

        current_bar_signal: bool = (buy_signal and is_hl_satisfied) or two_by_zero_signal
        extend_bar_signal: bool = dl_break_signal and is_hl_satisfied
        tbar_filter: bool = not (close_at_bar_bottom_by_percent(self.p.close_threshold * 0.01, self.data.close[0], self.data.low[0], self.data.high[0]) and self.p.toggle_close_low)
        long_signal: bool = (not (not in_long_trend_range and self.p.toggle_ma) and
                             (current_bar_signal or extend_bar_signal) and tbar_filter and not should_kill_all_signal)

        if long_signal:
            extend_bar_signal_offset = 0
            if extend_bar_signal:
                for i in range(1, self.p.signal_window_bar_count):
                    if self.dl.l.maybe_buy_signal[-i] or self.dl.l.maybe_two_by_zero_signal[-i]:
                        extend_bar_signal_offset = i

            self.record_trade(extend_bar_signal_offset)
            self.buy()

        [_cur_drawdown, _max_equity, _total_pnl] = self.manage_trade()

        # Collect data for export
        row = {
            'datetime': self.data.datetime.datetime(0),
            'open': self.data.open[0],
            'high': self.data.high[0],
            'low': self.data.low[0],
            'close': self.data.close[0],
            'volume': self.data.volume[0],
            'openinterest': 0,

            # rsi
            'rsi': self.rsi[0],

            # signal
            'has_signal': 1 if long_signal else -1,

            # ma related
            'ma40': self.ma[0],
            'ma10': self.quick_ma[0],
            'ma100': self.ma100[0],
            'ma40_delta': self.ma_delta[0],
            'ma10_delta': self.quick_ma_delta[0],
            'close_average_percent': self.close_average_percent[0],
            'close_average_cycle_day': self.p.close_avg_percent_lookback,

            # dl related
            'dl_has_window_one_signal': 1 if current_bar_signal else -1,
            'dl_has_window_two_signal': 1 if extend_bar_signal else -1,
            'dl_hrsi': hrsi_at_signal if long_signal else None,
            'dl_bar_count': bar_count_at_signal if long_signal else None,
            'dl_deslope_score': deslope_score_at_signal if long_signal else None,
            'dl_value_at_signal': dl_value_at_signal if long_signal else None,

            # hl related
            'hl_satisfied': 1 if is_hl_satisfied else -1,
            'hl_value_at_signal': cur_sr_value if long_signal else None,
            'hl_score_at_signal': cur_hl_score if long_signal else None,
        }
        self.csv_export_list.append(row)

    def record_trade(self, extend_bar_signal_offset):
        entry_size = math.floor(self.p.order_size_in_usd / self.data.close[0])

        self.trade_list.append(
            TradeV2(
                entry_price=self.data.close[0],
                entry_time=self.data.datetime[0],
                entry_bar_index=self.bar_index() - extend_bar_signal_offset,
                entry_bar_offset=0,
                open_entry_size=entry_size,
                total_entry_size=entry_size,
                is_long=True,
                is_open=True,
                max_exit_price=self.data.high[0]
            )
        )

    def manage_trade(self):
        self.cur_drawdown = 0.0

        # Calculate current drawdown
        for trade in self.trade_list:
            if trade.entry_time != self.data.datetime[0]:
                self.cur_drawdown += trade.open_entry_size * (trade.entry_price - self.data.low[0])
        self.cur_drawdown = self.max_equity - self.current_equity + self.cur_drawdown
        self.max_drawdown = max(self.max_drawdown, self.cur_drawdown)

        # Process each trade
        for index, trade in enumerate(self.trade_list):
            cur_entry_time = trade.entry_time
            cur_entry_price = trade.entry_price
            if self.data.high[0] > trade.max_exit_price and self.data.datetime[0] > cur_entry_time:
                trade.max_exit_price = self.data.high[0]

            trade.entry_bar_offset = self.bar_index() - trade.entry_bar_index
            stop_loss_long = min(self.data.low[-trade.entry_bar_offset], self.data.low[-(trade.entry_bar_offset + 1)])
            cur_max_return = (self.data.high[0] - cur_entry_price) / cur_entry_price * 100

            if trade.is_open:
                # Stop loss
                if trade.open_entry_size > 0 and self.data.close[0] < stop_loss_long and trade.is_long and trade.entry_time < self.data.datetime[0]:
                    trade.is_open = False
                    if self.p.toggle_pnl:
                        cur_return = (self.data.close[0] - cur_entry_price) / cur_entry_price * 100
                        if trade.take_profit:
                            trade.second_time = self.data.datetime[0]
                            if (trade.max_exit_price - cur_entry_price) / cur_entry_price * 100 > self.p.max_exit_ca_multiplier * self.close_average_percent:
                                cur_return = (trade.max_exit_price - cur_entry_price) * self.p.stop_gain_pt / cur_entry_price
                                self.exit_second_time(cur_entry_price, cur_return, trade)
                            else:
                                self.exit_second_time(cur_entry_price, cur_return, trade)
                        else:
                            self.exit_first_time(cur_entry_price, cur_return, trade)
                    trade.open_entry_size = 0

                # Reach 3M
                elif trade.entry_bar_offset == self.p.cycle_month * 20:
                    trade.is_open = False
                    cur_return = (trade.max_exit_price - cur_entry_price) / cur_entry_price * self.p.max_gain_pt
                    if self.p.toggle_pnl:
                        if trade.take_profit:
                            trade.second_time = self.data.datetime[0]
                            self.exit_second_time(cur_entry_price, cur_return, trade)
                        else:
                            self.exit_first_time(cur_entry_price, cur_return, trade)
                    trade.open_entry_size = 0

                # Take profit
                elif cur_max_return > max(self.p.first_gain_ca_multiplier * self.close_average_percent, self.p.stop_loss_pt) and not trade.take_profit and self.data.datetime[0] > trade.entry_time:
                    if self.p.toggle_pnl:
                        cur_return = max(self.p.first_gain_ca_multiplier * self.close_average_percent, self.p.stop_loss_pt)
                        trade.first_time = self.data.datetime[0]
                        trade.first_return = cur_return
                        self.current_equity += (1 + cur_return / 100) * cur_entry_price * int(trade.total_entry_size * 0.33)
                        self.max_equity = max(self.max_equity, self.current_equity)
                        self.total_pnl += cur_return / 3
                        trade.pnl += cur_return / 3
                    trade.take_profit = True
                    trade.open_entry_size -= int(trade.total_entry_size * 0.33)

                elif self.bar_index() == self.last_bar_index():
                    cur_return = (trade.max_exit_price - cur_entry_price) / cur_entry_price * self.p.max_gain_pt
                    if self.p.toggle_pnl:
                        if trade.take_profit:
                            self.exit_second_time(cur_entry_price, cur_return, trade)
                        else:
                            self.exit_first_time(cur_entry_price, cur_return, trade)
                    trade.open_entry_size = 0

        return self.cur_drawdown, self.max_equity, self.total_pnl

    def exit_first_time(self, cur_entry_price, cur_return, trade):
        trade.first_time = self.data.datetime[0]
        trade.first_return = cur_return
        self.current_equity += (1 + cur_return / 100) * cur_entry_price * trade.open_entry_size
        self.max_equity = max(self.max_equity, self.current_equity)
        self.total_pnl += cur_return
        trade.pnl += cur_return

    def exit_second_time(self, cur_entry_price, cur_return, trade):
        trade.second_return = cur_return
        self.current_equity += (1 + cur_return / 100) * cur_entry_price * trade.open_entry_size
        self.max_equity = max(self.max_equity, self.current_equity)
        self.total_pnl += cur_return * 2 / 3
        trade.pnl += cur_return * 2 / 3

    def stop(self):
        self.lines_info = self.hlv4.lines_info
        self.dl_lines_info = self.dl.dl_lines_info

        if not self.p.use_date_range:
            win_count = 0
            win_pnl = 0.0
            loss_pnl = 0.0
            for index, trade in enumerate(self.trade_list):
                if trade.pnl > 0:
                    win_count += 1
                    win_pnl += trade.pnl
                else:
                    loss_pnl += trade.pnl

                first_return = trade.first_return
                rounded_return = round(first_return, 2)
                formatted_return = f"{rounded_return:.2f}" if rounded_return == int(rounded_return) else str(rounded_return)

                second_return = str(round(trade.second_return, 2)) if trade.take_profit else ""

                print(f'{index}, {num2date(trade.entry_time).date()}, {"live" if trade.is_open else "closed"}, {round(trade.pnl, 2)},'
                      f' {num2date(trade.first_time).date()}, {formatted_return}, {second_return}')
                print('---------------------------')

            self.log(f"Total Pnl%: {round(self.total_pnl, 2)}%, Avg Pnl% per entry: {round(self.total_pnl / len(self.trade_list), 2)}%,"
                     f"Trade Count: {len(self.trade_list)}, Winning entry%: {round(win_count / len(self.trade_list) * 100, 2)}%,"
                     f"Avg Winner%: {round(win_pnl / win_count, 2)}%, Avg Loser%: {round(loss_pnl / len(self.trade_list), 2)}, "
                     f"Fit Score: {round(FIT_SCORE_MAX if loss_pnl == 0.0 else min((-win_pnl / loss_pnl), FIT_SCORE_MAX), 2)}")

        if self.p.export:
            self.export_csv()

    def highest_bars(self, source, length):
        if len(source) < length:
            return None  # Not enough data to calculate

        recent_highs = list(source.get(size=length))
        highest_val = max(recent_highs)
        highest_idx = recent_highs[::-1].index(highest_val)
        return -highest_idx

    def export_csv(self):
        # Convert list to DataFrame
        df = pd.DataFrame(self.csv_export_list)

        # Export DataFrame to CSV
        df.to_csv(f'{TICKER_NAME}USDT_{TIMEFRAME}.csv', index=False)

    def zip_for_first_condition_low_delta_bound(
        self,
        conditions: List[bool],
        ma_threshold_lows: List[int],
        condition_low_delta_bounds: List[float],
        base_threshold_low: int,
        cur_ma_delta: float,
    ) -> Tuple[float, int]:
        # Calculate the base low delta bound using a percentile-like approach

        final_low_delta_bound = self.base_low_delta_bound[0]
        is_fallback_set = False

        for index, condition in enumerate(conditions):
            cur_ma_threshold_low = ma_threshold_lows[index]
            condition_low_delta_bound = condition_low_delta_bounds[index]

            if condition:
                if not is_fallback_set:
                    # Set the fallback low delta bound based on the first true condition
                    final_low_delta_bound = condition_low_delta_bound
                    is_fallback_set = True

                if cur_ma_delta >= condition_low_delta_bound:
                    final_low_delta_bound = condition_low_delta_bound
                    break

        return final_low_delta_bound

if __name__ == '__main__':
    # via console.log(user.auth_token)
    token = ""

    # tv = TvDatafeed(username, password)
    tv = TvDatafeed(token=token)
    # ticker, ma10, ma40, hrsi, rd_on, rc_win1, rc_win2, nh, nh_hrsi, nh_n, lookback, ca_period
    input = ["BNB", 100, 100, 100, False, 10, 8, False, 99, 8, 1000, 500]
    timeframe = Interval.in_12_hour
    TICKER_NAME = input[0]
    TIMEFRAME = timeframe.value
    dataframe = tv.get_hist(symbol=f'{input[0]}USDT',exchange='BINANCE',interval=timeframe,n_bars=1000)
    dataframe['openinterest'] = 0
    cerebro = bt.Cerebro()  # create a "Cerebro" engine instance

    # Create a data feed
    pandasData = bt.feeds.PandasData(dataname=dataframe)
    cerebro.adddata(pandasData)  # Add the data feed
    cerebro.broker.set_coc(True)

    # for optimize
    # cerebro.optstrategy(
    #     SmaCross,
    #     pfast=range(10, 20),
    #     pslow=range(40, 60)
    # )

    cerebro.addstrategy(
        TrendRider,
        pfast=10,
        pslow=40,
        toggle_weak_ma_filter=True,
        weak_ma_pt=input[1],
        long_trend_threshold_low=input[2],
        rsi_long_threshold=input[3],
        toggle_reduce_chase=input[4],
        window_one_stop_loss_chase_offset=input[5],
        window_two_stop_loss_chase_offset=input[6],
        toggle_new_high_loose=input[7],
        new_high_rsi_long_threshold=input[8],
        bar_count_to_prev_high=input[9],
        lookback=input[10],
        close_avg_percent_lookback=input[11],
        use_date_range=False,
        export=False
    )  # Add the trading strategy
    cerebro.run()  # run it all
    # cerebro.plot(style='candlestick', barup='green', bardown='red')
