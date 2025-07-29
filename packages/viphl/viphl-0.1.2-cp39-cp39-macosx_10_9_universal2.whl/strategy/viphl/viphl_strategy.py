import math
import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import backtrader as bt

from generic_csv_feed import VipHlDataFeed
from backtrader import num2date
from indicators.helper.dtpl import DTPL
from indicators.helper.pivot_high import PivotHigh
from indicators.helper.pivot_low import PivotLow
from indicators.viphl.dto.recovery_window import from_recovery_window_result_v2
from indicators.viphl.dto.settings import Settings
from indicators.viphl.dto.viphl_interface import VipHL
try:
    from tvDatafeed import TvDatafeed, Interval
except ImportError:
    print("Warning: tvDatafeed not installed, will use sample data instead.")
    Interval = type('Interval', (), {'in_daily': 'D', 'value': 'D'})
from dto.trade_v2 import TradeV2
from indicators.helper.close_average import CloseAveragePercent
from indicators.helper.percentile_nearest_rank import PercentileNearestRank
from indicators.helper.percent_rank import PercentRank
from indicators.dl.dl_v1_9_indicator import DLv1_9Indicator


# Create a subclass of Strategy to define the indicators and logic

FIT_SCORE_MAX = 500
TICKER_NAME = "ETH"
TIMEFRAME = '6H'

class VipHLStrategy(bt.Strategy):
    # list of parameters which are configurable for the strategy
    params = (
        ('precomputed_indicators', False),
        ('mintick', -1.0),
        # By Point设置
        ('draw_from_recent', True),
        ('allow_reuse_by_point', False),
        ('high_by_point_n', 10),
        ('high_by_point_m', 10),
        ('low_by_point_n', 8),
        ('low_by_point_m', 8),
        ('high_by_point_n_on_trend', 5),
        ('high_by_point_m_on_trend', 5),
        ('low_by_point_n_on_trend', 4),
        ('low_by_point_m_on_trend', 4),
        ('show_vip_by_point', True),
        ('show_closest_vip_hl', True),
        ('show_ma_trending', False),
        ('last_by_point_weight', 3),
        ('second_last_by_point_weight', 2),
        ('by_point_weight', 1),

        # HL Violation设置
        ('bar_count_to_by_point', 700),
        ('bar_cross_threshold', 5),
        ('hl_length_threshold', 300),

        # 入场点设置
        ('only_body_cross', True),
        ('close_above_hl_threshold', 0.25),
        ('close_above_low_threshold', 1.25),
        ('close_above_recover_low_threshold', 1.25),
        ('low_above_hl_threshold', 0.5),
        ('hl_extend_bar_cross_threshold', 6),
        ('close_above_hl_search_range', 5),
        ('close_above_hl_bar_count', 3),
        ('trap_recover_window_threshold', 6),
        ('signal_window', 2),
        ('recover_hl_width', 4),
        ('krsi_coefficient', 2),
        ('krsi_offset', 0.0),
        ('krsi_vvip_only', True),

        # Reduce stop loss
        ('reduce_stop_loss_threshold',5),
        ('dtpl_reduce_stop_loss_threshold', 5),
        ('vviphl_reduce_stop_loss_threshold', 5),

        # T-RSI
        ('trsi_length', 14),
        ('trsi_threshold', 50),
        ('trsi_to_low_trsi_offset', 0),
        ('dtpl_trsi_threshold', 0),
        ('dtpl_trsi_to_low_trsi_offset', 2),
        ('vviphl_trsi_threshold', 0),
        ('vviphl_trsi_to_low_trsi_offset', 0),

        # DTPL
        ('dtpl_condition_lookback_period', 15),
        ('dtpl_high_lookback_period', 90),
        ('dtpl_fast_ma_length', 10),
        ('dtpl_medium_ma_length', 40),
        ('dtpl_slow_ma_length', 100),
        ('dtpl_no_hl', True),

        # VVIPHL
        ('vviphl_min_bypoint_count', 2),

        # MA
        ('ma_lookback_period', 200),
        ('fast_ma_length', 5),        # fast
        ('fast_ma_distr_threshold', 80),
        ('fast_ma_dtpl_distr_threshold', 80),
        ('fast_ma_vvip_distr_threshold', 100),
        ('slow_ma_length', 40),       # slow
        ('slow_ma_distr_threshold', 100),
        ('slow_ma_dtpl_distr_threshold', 100),
        ('slow_ma_vvip_distr_threshold', 100),

        # CA设置
        ('close_avg_percent_lookback', 200),
        ('hl_overlap_ca_percent_multiplier', 1.5),

        # 回测设置
        ('debug', False),
        ('start_time', "22 May 2024 21:30 +0000"),
        ('end_time', "23 Jun 2024 21:30 +0000"),
        ('start_price', 60000),
        ('end_price', 61000),

        # By Point设置 (Trending MA Delta Distr Config)
        ('trending_ma_delta_distr_lookback', 500),
        ('trending_ma_delta_distr_threshold', 1),

        # others
        ('use_date_range', False),
        ('export', False),

        ######### DL ########
        ######### should be hard-coded similar to pinescript? ########
        ('printlog', False),

        ('toggle_rsi', False),
        ('toggle_ma', True),
        ('toggle_dl_by_score', True),
        ('toggle_short_dl', True),
        ('use_date_range', False),
        ('export', False),

        # ---------trade inputs-------
        ('order_size_in_usd', 2000000),  # Equivalent to orderSizeInUSD
        ('cycle_month', 6.0),  # Equivalent to cycleMonth
        ('stop_loss_pt', 1.0),  # Equivalent to stopLossPt
        ('first_gain_ca_multiplier', 2.0),  # Equivalent to firstGainCAMultiplier
        ('max_gain_pt', 50.0),  # Equivalent to maxGainPt
        ('max_exit_ca_multiplier', 3.0),  # Equivalent to maxExitCAMultiplier
        ('stop_gain_pt', 30.0),  # Equivalent to stopGainPt
        ('toggle_pnl', True),

        # nbym inputs
        ('left_bars', 2),
        ('right_bars', 2),

        # DL inputs
        ('lookback', 600),
        ('min_bar_count', 3),
        ('dl_break_threshold', 0.2),
        ('non_two_by_dl_break_threshold', 0.3),
        ('short_dl_break_threshold', 0.5),
        ('extended_cross_threshold', 2),
        ('extended_cross_uncross_threshold', 8),
        ('distance_to_a_prime_percent', 0.3),
        ('long_trend_threshold', 100),
        ('min_bar_count_on_trend', 3),
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
        ('ma_length', 40),
        ('long_trend_threshold_up', 0),
        ('long_trend_threshold_low', 35),

        # RSI inputs
        ('rsi_length', 14),
        ('rsi_lookback', 1),
        ('rsi_long_threshold', 100),
    )

    def log(self, txt, dt=None, doprint=True):
        ''' Logging function fot this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        '''init is called once at the last row'''

        '''
        viphl
        '''
        self.normal_high_by_point = PivotHigh(leftbars=self.p.high_by_point_n, rightbars=self.p.high_by_point_m)
        self.normal_low_by_point = PivotLow(leftbars=self.p.low_by_point_n, rightbars=self.p.low_by_point_m)
        self.trending_high_by_point = PivotHigh(leftbars=self.p.high_by_point_n_on_trend, rightbars=self.p.high_by_point_m_on_trend)
        self.trending_low_by_point = PivotLow(leftbars=self.p.low_by_point_n_on_trend, rightbars=self.p.low_by_point_m_on_trend)

        self.ma10 = bt.indicators.SMA(self.data.close, period=10)
        self.ma40 = bt.indicators.SMA(self.data.close, period=40)
        self.ma100 = bt.indicators.SMA(self.data.close, period=100)
        self.trending_ma_delta = self.ma10 - self.ma100
        self.trending_ma_delta_distr = PercentileNearestRank(self.trending_ma_delta, period=self.p.trending_ma_delta_distr_lookback, percentile=self.p.trending_ma_delta_distr_threshold)

        self.is_ma_greater = bt.And(bt.Cmp(self.ma10, self.ma40) == 1, bt.Cmp(self.ma40, self.ma100) == 1)
        self.is_ma_trending = bt.And(self.is_ma_greater, bt.Cmp(self.trending_ma_delta, self.trending_ma_delta_distr) == 1)

        viphl_settings = Settings(
            high_by_point_n=self.p.high_by_point_n,
            high_by_point_m=self.p.high_by_point_m,
            low_by_point_n=self.p.low_by_point_n,
            low_by_point_m=self.p.low_by_point_m,
            high_by_point_n_on_trend=self.p.high_by_point_n_on_trend,
            high_by_point_m_on_trend=self.p.high_by_point_m_on_trend,
            low_by_point_n_on_trend=self.p.low_by_point_n_on_trend,
            low_by_point_m_on_trend=self.p.low_by_point_m_on_trend,
            bar_count_to_by_point=self.p.bar_count_to_by_point,
            bar_cross_threshold=self.p.bar_cross_threshold,
            hl_length_threshold=self.p.hl_length_threshold,
            hl_overlap_ca_percent_multiplier=self.p.hl_overlap_ca_percent_multiplier,
            only_body_cross=self.p.only_body_cross,
            last_by_point_weight=self.p.last_by_point_weight,
            second_last_by_point_weight=self.p.second_last_by_point_weight,
            by_point_weight=self.p.by_point_weight,
            hl_extend_bar_cross_threshold=self.p.hl_extend_bar_cross_threshold,
        )
        self.viphl = VipHL(
            close=self.data.close,
            open=self.data.open,
            high=self.data.high,
            low=self.data.low,
            mintick=self.p.mintick,
            bar_index=self.bar_index(),
            time=self.data.datetime,
            last_bar_index=self.last_bar_index(),
            settings=viphl_settings,
            hls=[],
            vip_by_points=[],
            new_vip_by_points=[],
            recovery_windows=[],
            latest_recovery_windows={},
            normal_high_by_point=self.normal_high_by_point,
            normal_low_by_point=self.normal_low_by_point,
            trending_high_by_point=self.trending_high_by_point,
            trending_low_by_point=self.trending_low_by_point
        )

        self.dl = DLv1_9Indicator(
            hlv4=None,
            viphl=self.viphl,
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
        self.dtpl = DTPL(self.data, dtpl_high_lookback_period=self.p.dtpl_high_lookback_period)
        self.close_average_percent = CloseAveragePercent(close_avg_percent_lookback=self.p.close_avg_percent_lookback)

        ## trsi & ma
        self.trsi = bt.ind.RSI(self.datas[0], period=self.p.trsi_length)
        self.low_trsi = bt.indicators.Lowest(self.trsi, period=3)
        self.slow_ma = bt.indicators.SMA(self.data.close, period=self.p.slow_ma_length)
        self.fast_ma = bt.indicators.SMA(self.data.close, period=self.p.fast_ma_length)
        self.slow_ma_delta = bt.indicators.ROC(self.slow_ma, period=1)
        self.fst_ma_delta = bt.indicators.ROC(self.fast_ma, period=1)
        self.slow_ma_distr_percent = 100 - bt.indicators.PercentRank(self.slow_ma_delta.roc, period=self.p.ma_lookback_period) * 100
        self.fast_ma_distr_percent = 100 - bt.indicators.PercentRank(self.fst_ma_delta.roc, period=self.p.ma_lookback_period) * 100

        self.trsi.plotinfo.plot = False
        self.low_trsi.plotinfo.plot = False
        self.slow_ma_delta.plotinfo.plot = False
        self.fst_ma_delta.plotinfo.plot = False

        # For tracking trades
        self.trade_list = []

        # For exporting data
        self.csv_export_list = []

        self.lines_info = []
        self.dl_lines_info = []

        # trade management
        self.max_equity: float = 0.0
        self.current_equity: float = 0.0
        self.max_drawdown: float = 0.0
        self.cur_drawdown: float = 0.0
        self.total_pnl: float = 0.0
        return

    def next(self):
        self.viphl.update_built_in_vars(bar_index=self.bar_index(), last_bar_index=self.last_bar_index())
        self.viphl.update(is_ma_trending=self.is_ma_trending, close_avg_percent=self.close_average_percent[0])

        # Update the recovery window
        self.viphl.update_recovery_window(
            trap_recover_window_threshold=self.params.trap_recover_window_threshold,
            search_range=self.params.close_above_hl_search_range,
            low_above_hl_threshold=self.params.low_above_hl_threshold,
            close_avg_percent=self.close_average_percent[0]
        )

        # Check the recovery window
        recovery_window_result = self.viphl.check_recovery_window_v3(
            close_avg_percent=self.close_average_percent[0],
            close_above_hl_threshold=self.params.close_above_hl_threshold,
            trap_recover_window_threshold=self.params.trap_recover_window_threshold,
            signal_window=self.params.signal_window,
            close_above_low_threshold=self.params.close_above_low_threshold,
            close_above_recover_low_threshold=self.params.close_above_recover_low_threshold,
            bar_count_close_above_hl_threshold=self.params.close_above_hl_bar_count,
            vvip_hl_min_by_point_count=self.params.vviphl_min_bypoint_count
        )

        # flattern RecoveryWindowResultV2
        flattern = from_recovery_window_result_v2(recovery_window_result)

        break_hl_at_price: float = flattern.break_hl_at_price
        is_hl_satisfied: bool = flattern.is_hl_satisfied
        is_vvip_signal: bool = flattern.is_vvip_signal
        is_non_vvip_signal: bool = flattern.is_non_vvip_signal

        has_dl_signal: bool = (self.dl.lines.maybe_buy_signal[0] or self.dl.lines.maybe_two_by_zero_signal[0] or
                               self.dl.lines.maybe_dl_break_signal[0])

        is_dtpl: bool = self.dtpl.lines.is_dtpl[0]

        # Check stop loss
        quoted_trade = self.quote_trade()
        # Calculate stop loss thresholds
        stoploss_below_threshold = quoted_trade.stop_loss_percent < self.close_average_percent[0] * self.p.reduce_stop_loss_threshold
        dtpl_stoploss_below_threshold = quoted_trade.stop_loss_percent < self.close_average_percent[0] * self.p.dtpl_reduce_stop_loss_threshold
        vviphl_stoploss_below_threshold = quoted_trade.stop_loss_percent < self.close_average_percent[0] * self.p.vviphl_reduce_stop_loss_threshold


        ## TODO KRSI
        k = ((self.data.close[0] / self.data.low[0] - 1) * 100) / self.close_average_percent[0]
        krsi_threshold = k * self.p.krsi_coefficient + self.p.krsi_offset

        # Boolean checks for KRSI thresholds
        krsi_above_normal_trsi = krsi_threshold > self.p.trsi_to_low_trsi_offset
        krsi_above_vvip_trsi = krsi_threshold > self.p.vviphl_trsi_to_low_trsi_offset
        krsi_above_dtpl_trsi = krsi_threshold > self.p.dtpl_trsi_to_low_trsi_offset

        ## TODO trading signal
        maybe_dl_signal = True
        within_lookback_period = self.last_bar_index() - self.bar_index() <= self.p.lookback

        # Normal signals
        above_ma_distr_threshold = self.slow_ma_distr_percent[0] > self.p.slow_ma_distr_threshold or self.fast_ma_distr_percent[0] > self.p.fast_ma_distr_threshold
        has_long_signal = is_hl_satisfied and maybe_dl_signal and stoploss_below_threshold
        normal_rsi_failed = self.trsi[0] > self.p.trsi_threshold or (self.trsi[0] - self.low_trsi[0] < self.p.trsi_to_low_trsi_offset)
        only_rsi_offset_failed = self.trsi[0] <= self.p.trsi_threshold and (self.trsi[0] - self.low_trsi[0] < self.p.trsi_to_low_trsi_offset) and not above_ma_distr_threshold
        krsi_normal_pass = only_rsi_offset_failed and krsi_above_normal_trsi and not self.p.krsi_vvip_only
        alert_only = (normal_rsi_failed or above_ma_distr_threshold) and not krsi_normal_pass

        # VVIP signals
        above_vvip_ma_distr_threshold = self.slow_ma_distr_percent[0] > self.p.slow_ma_vvip_distr_threshold or self.fast_ma_distr_percent[0] > self.p.fast_ma_vvip_distr_threshold
        has_vvip_long_signal = is_vvip_signal and maybe_dl_signal and vviphl_stoploss_below_threshold
        vvip_rsi_failed = self.trsi[0] > self.p.vviphl_trsi_threshold or (self.trsi[0] - self.low_trsi[0] < self.p.vviphl_trsi_to_low_trsi_offset)
        only_vvip_rsi_offset_failed = self.trsi[0] <= self.p.vviphl_trsi_threshold and (self.trsi[0] - self.low_trsi[0] < self.p.vviphl_trsi_to_low_trsi_offset) and not above_vvip_ma_distr_threshold
        krsi_vvip_pass = only_vvip_rsi_offset_failed and krsi_above_vvip_trsi
        vviphl_alert_only = (vvip_rsi_failed or above_vvip_ma_distr_threshold) and not krsi_vvip_pass

        # DTPL signals
        above_dtpl_ma_distr_threshold = self.slow_ma_distr_percent[0] > self.p.slow_ma_dtpl_distr_threshold or self.fast_ma_distr_percent[0] > self.p.fast_ma_dtpl_distr_threshold
        has_dtpl_with_hl_signal = is_hl_satisfied and maybe_dl_signal and is_dtpl and dtpl_stoploss_below_threshold
        dtpl_rsi_failed = self.trsi[0] > self.p.dtpl_trsi_threshold or (self.trsi[0] - self.low_trsi[0] < self.p.dtpl_trsi_to_low_trsi_offset)
        only_dtpl_rsi_offset_failed = self.trsi[0] <= self.p.dtpl_trsi_threshold and (self.trsi[0] - self.low_trsi[0] < self.p.dtpl_trsi_to_low_trsi_offset) and not above_dtpl_ma_distr_threshold
        krsi_dtpl_pass = only_dtpl_rsi_offset_failed and krsi_above_dtpl_trsi and not self.p.krsi_vvip_only
        dtpl_alert_only = (dtpl_rsi_failed or above_dtpl_ma_distr_threshold) and not krsi_dtpl_pass

        no_hl_signal_but_dl_signal = not is_hl_satisfied and has_dl_signal

        dl_length_satisfied = (
            has_dl_signal and 
            (self.dl.l.bar_count_at_signal[0] > 3 or
             (self.dl.l.bar_count_at_signal[0] == 3 and self.data.close[-1] < self.data.close[-2]))
        )
        has_dtpl_no_hl_signal = no_hl_signal_but_dl_signal and dl_length_satisfied and is_dtpl and dtpl_stoploss_below_threshold
        has_dtpl_long_signal = (has_dtpl_no_hl_signal and self.p.dtpl_no_hl) or has_dtpl_with_hl_signal

        # Initialize signal and alert flags
        use_normal_signal = False
        use_vvip_signal = False
        use_dtpl_signal = False
        normal_alert = False
        vviphl_alert = False
        dtpl_alert = False
        no_signal_or_alert = False

        if has_long_signal:
            if not alert_only:
                use_normal_signal = True
            else:
                # If normal and alert, check vviphl
                if has_vvip_long_signal:
                    if not vviphl_alert_only:
                        use_vvip_signal = True
                    else:
                        # If vviphl and alert, check dtpl
                        if has_dtpl_long_signal:
                            if not dtpl_alert_only:
                                use_dtpl_signal = True
                            else:
                                normal_alert = True
                        else:
                            normal_alert = True
                else:
                    # If no vviphl then check dtpl directly
                    if has_dtpl_long_signal:
                        if not dtpl_alert_only:
                            use_dtpl_signal = True
                        else:
                            normal_alert = True
                    else:
                        normal_alert = True
        elif has_vvip_long_signal:
            if not vviphl_alert_only:
                use_vvip_signal = True
            else:
                # If vviphl and alert, check dtpl
                if has_dtpl_long_signal:
                    if not dtpl_alert_only:
                        use_dtpl_signal = True
                    else:
                        vviphl_alert = True
                else:
                    vviphl_alert = True
        else:
            # If no vviphl then check dtpl directly
            if has_dtpl_long_signal:
                if not dtpl_alert_only:
                    use_dtpl_signal = True
                else:
                    dtpl_alert = True
            else:
                # If none passes, use none
                no_signal_or_alert = True

        if within_lookback_period:
            if use_normal_signal or use_vvip_signal or use_dtpl_signal:
                self.record_trade(0)
                if use_normal_signal or use_vvip_signal or (use_dtpl_signal and has_dtpl_with_hl_signal):
                    self.viphl.commit_latest_recovery_window(break_hl_at_price)

        self.manage_trade()

        # Collect data for export
        row = {
            'datetime': self.data.datetime.datetime(0),
            'open': self.data.open[0],
            'high': self.data.high[0],
            'low': self.data.low[0],
            'close': self.data.close[0],
            'volume': self.data.volume[0],
            'openinterest': 0,

            'normal_high_by_point': self.normal_high_by_point.value[0],
            'normal_low_by_point': self.normal_low_by_point.value[0],
            'trending_high_by_point': self.trending_high_by_point.value[0],
            'trending_low_by_point': self.trending_low_by_point.value[0],
            'close_average_percent': self.close_average_percent[0],

            'is_ma_trending': self.is_ma_trending[0],

            'maybe_buy_signal': 1 if self.dl.lines.maybe_buy_signal[0] else -1,
            'maybe_two_by_zero_signal': 1 if self.dl.lines.maybe_two_by_zero_signal[0] else -1,
            'maybe_dl_break_signal': 1 if self.dl.lines.maybe_dl_break_signal[0] else -1,
            'bar_count_at_signal': self.dl.l.bar_count_at_signal[0],

            'slow_ma_distr_percent': self.slow_ma_distr_percent[0],
            'fast_ma_distr_percent': self.fast_ma_distr_percent[0],

            'trsi': self.trsi[0],
            'low_trsi': self.low_trsi[0],

            'is_dtpl': self.dtpl.lines.is_dtpl[0],
        }
        self.csv_export_list.append(row)

    def quote_trade(self):
        # Calculate stop loss
        stop_loss_long = min(self.data.low[0], self.data.low[-1])
        stop_loss_percent = (self.data.close[0] - stop_loss_long) / self.data.close[0] * 100

        # Calculate entry size
        entry_size = math.floor(self.p.order_size_in_usd / self.data.close[0])

        # Create a new trade
        new_trade = TradeV2(
            entry_price=self.data.close[0],
            entry_time=self.data.datetime[0],
            entry_bar_index=self.bar_index(),
            entry_bar_offset=0,
            open_entry_size=entry_size,
            total_entry_size=entry_size,
            is_long=True,
            is_open=True,
            max_exit_price=self.data.high[0],
            stop_loss_percent=stop_loss_percent
        )

        return new_trade

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
        for hl in self.viphl.hls:
            if hl.extend_end_bar_index > 0 and hl.post_extend_end_bar_index == 0:
                end_index = hl.extend_end_bar_index
            elif hl.post_extend_end_bar_index > 0:
                end_index = hl.post_extend_end_bar_index
            else:
                end_index = hl.end_bar_index
            self.lines_info.append((hl.hl_value, hl.start_bar_index, end_index))

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

            if len(self.trade_list) > 0:
                self.log(f"Total Pnl%: {round(self.total_pnl, 2)}%, Avg Pnl% per entry: {round(self.total_pnl / len(self.trade_list), 2)}%,"
                     f"Trade Count: {len(self.trade_list)}, Winning entry%: {round(win_count / len(self.trade_list) * 100, 2) if len(self.trade_list) > 0 else 0}%,"
                     f"Avg Winner%: {round(win_pnl / win_count, 2) if win_count > 0 else 0}%, Avg Loser%: {round(loss_pnl / (len(self.trade_list) - win_count), 2) if len(self.trade_list) > win_count else 0}, "
                     f"Fit Score: {round(FIT_SCORE_MAX if loss_pnl == 0.0 else min((-win_pnl / loss_pnl), FIT_SCORE_MAX), 2)}")
            else:
                self.log("No trades executed during the backtest period.")

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
        df.to_csv(f'BTC.csv', index=False)

def load_data_from_tv(ticker, exchange, timeframe, n_bars):
    try:
        token = ""
        # tv = TvDatafeed(username, password)
        # tv = TvDatafeed(token=token)
        tv = TvDatafeed(token="eyJhbGciOiJSUzUxMiIsImtpZCI6IkdaeFUiLCJ0eXAiOiJKV1QifQ.eyJ1c2VyX2lkIjo0MDYzMjQxNCwiZXhwIjoxNzQ4Nzg2ODA4LCJpYXQiOjE3NDg3NzI0MDgsInBsYW4iOiJwcm9fcHJlbWl1bSIsInByb3N0YXR1cyI6Im5vbl9wcm8iLCJleHRfaG91cnMiOjEsInBlcm0iOiIiLCJzdHVkeV9wZXJtIjoiUFVCO2NjYThmODlmODg0MTQ2MDZiMzdhYzQzZDZkYTFmZjYzLFBVQjtjYjgxZjcyNjE1NWU0MmIzODZmYzZlMjg5NmVjMzRlNCxQVUI7MmE1MGI5MzI2YWY0NDc0OTk1NjVmNWY4NWYxMWI3MGUsUFVCOzFkMjg2NWIyOWFlNjRmNWRiOWJjY2ZiMWM1OTc2NmMzLFBVQjswNGMwYzc4MjRiYTg0Yzg5ODU1ZGMxZTQyYzAwMjlhYyxQVUI7ZDhmNDUyNGU2ZjIwNDg5NWEyOGJmNzc4ODY0YjEyMWIsUFVCO2ZlZDljNDA2NTU1YjQ5YmM4MjM1N2QyNjQwMTk0NDYyLFBVQjs3NzU3NGM2MTBjZGE0ZTUwOWQwMzc3MDNkNTBkNzM5ZCx0di1wcm9zdHVkaWVzLFBVQjtjYWYwYmZkOWI4MTE0NWIwOTIzYzNkZjQ3M2YyMmNjZCxQVUI7MzFkY2I4NzEzZDRjNGRlOGEyNWYzNmVjMDkwODY3YjIsUFVCOzNjMWZmZTI4ZjY3ZjRkMGZhN2ZhZGMyZTNmNWM0ZmQ2LFBVQjs2ZGJjN2U2NGRiNmM0ZDY3YTY4YWZiOTMxNDM1MmFmNyxQVUI7ZjY4NzBmOGZkN2M3NDM4ZjgxNzNjZmE2NjM4ZDE2ZmUsUFVCOzUxMGEzMmI2NWYzMzRmYjQ4MWIwYjk1ODQzMGE0Y2Q5LFBVQjtkMWY1YTE4ZWU1Mjk0MGRjODI4NzUxYWIzOGE3NjhiYSxQVUI7YjBiZTA5ZjRiMjNlNGJiOGI2MjkyNGVkMzU2YWU1NzgsUFVCOzc5ZWE1NzgzYWUzNjRlNTFhNGFhMjIyYjg4ODA2ZTU4LFBVQjs4YTgzNTAyZTAwYjA0YTdhOTM1ZDcwNGZiYTJkZTJhZixQVUI7MzU4MTQzNzNiYzY3NDZkNGJhMWQ4NDgwNDk5NjdiYTgsUFVCOzZlMDMzNmFkNzI3NDRkOGY5NDZjOTQ2MzFjZTg4YjJmLFBVQjthYTI5ODk3MzE2NjQ0MjIzYmVjMjUyMmNlMzAyMGExNCxQVUI7NTZlMzM0NTUyZTFiNGE1ZGI0MzZhZGJiZGQyNzE0OTAsUFVCOzhhNDkwYmIxNjcyYzRjMGE5MWY0MTEyZDg5Mjc3NmRkLHR2LWNoYXJ0X3BhdHRlcm5zLFBVQjs3YzI4ZjgyN2NiMWU0ZDU4YTgxNjNkMDQyMjAyODdmMCxQVUI7NzJlZjMyNjBiNDFjNDhiZWFkNmZhMGY0NTUyZGU1ZDYsUFVCOzFjYTVlOTUxYzA1YjQyYTc5NTBhYTY5NjkzY2UwZDJiLFBVQjs1NjNiY2NmODc3ODM0MTMzOTE3MGY3YmVkMjU2ZWNkOSxQVUI7MDllY2YzMDNkYjY3NDM2Njk0OGZiNmJlMWU5MTk4OWYsUFVCOzk4OWM0MGM4MDVhZTRmOWI4MDA2OTFiMmQ3N2VkODIyLHR2LXZvbHVtZWJ5cHJpY2UsUFVCOzk5YzcxMjEyM2Q0NzQ3MTJiZTA3OTBkMzNhODI0NzAyLFBVQjs2MmUwZWJlZWJkZTY0NWFlYmVmZDhjMmRlYWU3NzQwZixQVUI7MzU1MTcwZWEzMzgwNDcwZDk2NWRkNzE1NmVkZDMzZmYsUFVCOzU3NDYwYjBiOThkNDQ3N2NiMGYxNTM4NDA0MTUxZWMxLFBVQjswMGQ0YTFkYzljNWQ0MjAzYWY3ZmNiY2U2NDQ5NjQwNixQVUI7MzFlODYyMzI5OTQxNDRhYmI0M2E4N2FiZGMzYWM4OTQsUFVCO2VmYTE0MWUwNWQxMjQwNDQ5MmNjZjE3MDFiMzYzZDA2LFBVQjs1MjZiNTE5ODdkMDE0M2JhOTMyZjdkN2I0MzE1OTRiOSxQVUI7YzhhYmEzYTA3ZjE0NDQ2N2FmZWMxNjZlNTlhNmRjY2UsUFVCOzI4YjMzYWY2ZTExODQ1NWZhZjI4M2I0YzA2ZjAzNTQxLFBVQjs1MzA1NWFhMTIwYzg0MzBiYWVlYWNiNjY0ZTE0ODI3ZSx0di1jaGFydHBhdHRlcm5zLFBVQjs3NWNhNWUzYjY1NGM0NGQxYWI2YjRmYjM5YzA5NWE4OCxQVUI7ZDM2Y2RkN2U0ZjUwNGVmODljOGQ3YzAxMzk4ODY2ODksUFVCOzFkZTM0N2IzOGJjYjQzMWI5N2EyZjlkNmM0MDU1ODhlLFBVQjs4ZjM4M2IyNDE1MzE0ZTcyOTk5OTViYzliNjdiOGVmZixQVUI7OWI5YTNlNmZkMDNmNGJhOTllZTQ1MzRmMTM3MWM1ODcsUFVCOzM3MGRhZDMzMGUzZjQzMzg5ZTA4YzQyM2I2NDQ2Y2Q0LFBVQjs4Yzg1Zjk4NTM4ZmY0MjVkYmJkYzUzZjJjZjlkZDNkOCxQVUI7MDI0YTdhNTVjNThlNGE4MGI2MzQzMTEyM2FiZWRhZDksUFVCOzI1YTg0ZmZjNmFmYjQ4ZGFhNmM5NDk5Y2E0ZDQ0OGUzLFBVQjsxMmI5ZmM4ZDMyNGQ0MmI2OTU5OTExMTE2ZmE3MTM2OSxQVUI7NjljYjMxOTQ3MDNiNDYwOTgyN2M4MjUzYTM4YmIwNDksUFVCO2RmZjYwYWRmNTFmYjQ5ZDJhMzgwYTVlYTlkOWQwZjBhLFBVQjtjNjM2YzBkZDgxZDE0YzcxYTNjN2NlZTE1MWY0Y2RjOSxQVUI7MDhlYzFiZmJkNzk5NGI2NWIzNmZkOGVhNzc5YjgyYzYsUFVCO2ZjNTI0YjA2ODBhOTRmN2Y4YzZjOTA5MmNlMjY1YzFkIiwibWF4X3N0dWRpZXMiOjI1LCJtYXhfZnVuZGFtZW50YWxzIjoxMCwibWF4X2NoYXJ0cyI6OCwibWF4X2FjdGl2ZV9hbGVydHMiOjQwMCwibWF4X3N0dWR5X29uX3N0dWR5IjoyNCwiZmllbGRzX3Blcm1pc3Npb25zIjpbInJlZmJvbmRzIl0sIm1heF9hbGVydF9jb25kaXRpb25zIjo1LCJtYXhfb3ZlcmFsbF9hbGVydHMiOjIwMDAsIm1heF9vdmVyYWxsX3dhdGNobGlzdF9hbGVydHMiOjUsIm1heF9hY3RpdmVfcHJpbWl0aXZlX2FsZXJ0cyI6NDAwLCJtYXhfYWN0aXZlX2NvbXBsZXhfYWxlcnRzIjo0MDAsIm1heF9hY3RpdmVfd2F0Y2hsaXN0X2FsZXJ0cyI6MiwibWF4X2Nvbm5lY3Rpb25zIjo1MH0.uFx-DMSwwsiprIuQJM7uAEO_p-wVqHh8ONGtyQzS8_O4Ziuqsqy0aVi8AeDrQlZuotIWKznXm23sj5eMjMAZUd-WqTrDy0a2YRRGrcWU6pkp9U2iYQ7wDAu9ZRjEC6BS_ywlvkx9pUAxO7rzuJmafRSWkH3QV34Nd3OMj79t7OA")
        dataframe = tv.get_hist(symbol=ticker,exchange=exchange,interval=timeframe,n_bars=n_bars)
        dataframe['openinterest'] = 0
        print("\n" + "="*50)
        print(f"SUCCESS: Using real TradingView data for {ticker} from {exchange}")
        print("Data sample:")
        print(dataframe.head(3))
        print("="*50 + "\n")
        return dataframe
    except (ImportError, NameError):
        # Create sample data if tvDatafeed is not available
        print("\n" + "="*50)
        print("WARNING: tvDatafeed package not available")
        print("USING SYNTHETIC SAMPLE DATA FOR BACKTESTING")
        print("="*50 + "\n")
        import pandas as pd
        import numpy as np
        import datetime
        
        # Create a date range
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=n_bars)
        date_range = pd.date_range(start=start_date, end=end_date, periods=n_bars)
        
        # Generate some sample price data
        close = np.linspace(50000, 60000, n_bars) + np.random.normal(0, 1000, n_bars).cumsum()
        high = close + np.random.uniform(100, 500, n_bars)
        low = close - np.random.uniform(100, 500, n_bars)
        open_price = close.copy()
        np.random.shuffle(open_price)
        volume = np.random.uniform(1000, 5000, n_bars)
        
        # Create the DataFrame
        dataframe = pd.DataFrame({
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume,
            'openinterest': np.zeros(n_bars),
            'mintick': np.ones(n_bars) * 0.01
        }, index=date_range)
        
        print("Sample of synthetic data:")
        print(dataframe.head(3))
        
        return dataframe

def load_data_from_csv(csv_file):
    # Read the CSV file
    dataframe = pd.read_csv(csv_file,
                                skiprows=0,
                                header=0,
                                parse_dates=True,
                                index_col=0)
    
    # # Convert the datetime column from string/int to datetime objects
    # dataframe['datetime'] = pd.to_datetime(dataframe['datetime'])
    
    return dataframe

if __name__ == '__main__':
    # ticker, ma10, ma40, hrsi, rd_on, rc_win1, rc_win2, nh, nh_hrsi, nh_n, lookback, ca_period
    input = ["BNB", 100, 100, 100, False, 10, 8, False, 99, 8, 1000, 500]
    timeframe = Interval.in_daily
    TICKER_NAME = input[0]
    TIMEFRAME = timeframe.value
    # dataframe = load_data_from_tv('{input[0]}USDT', 'BINANCE', timeframe, 1000)
    dataframe = load_data_from_tv(ticker='BTCUSDT', exchange='BINANCE', timeframe=Interval.in_daily, n_bars=1500)
    # dataframe = load_data_from_tv(ticker='NVDA', exchange='NASDAQ', timeframe=Interval.in_daily, n_bars=1500)
    # print(f"Number of data points: {len(dataframe)}")

    # Remove symbol column if it exists
    # if 'symbol' in dataframe.columns:
    #     dataframe = dataframe.drop('symbol', axis=1)

    # Save to CSV
    # csv_filename = 'NVDA_data.csv'
    # dataframe.to_csv(csv_filename)
    # print(f"Data saved to {csv_filename}")

    # dataframe = load_data_from_csv('NVDA.csv')
    cerebro = bt.Cerebro()  # create a "Cerebro" engine instance

    # Create a data feed
    pandasData = bt.feeds.PandasData(dataname=dataframe)
    # csvData = VipHlDataFeed(
    #     dataname=f'./NVDA_data.csv',
    #     datetime=0,
    #     open=1,
    #     high=2,
    #     low=3,
    #     close=4,
    #     volume=5,
    #     openinterest=6,
    #     dtformat='%Y-%m-%d %H:%M:%S',
    #     timeframe=bt.TimeFrame.Minutes
    # )
    cerebro.adddata(pandasData)  # Add the data feed
    cerebro.broker.set_coc(True)

    cerebro.addstrategy(
        VipHLStrategy,
        mintick = dataframe['mintick'].iloc[0],
        export=True,
    )  # Add the trading strategy
    cerebro.run()  # run it all
    cerebro.plot(style='candlestick', barup='green', bardown='red')
