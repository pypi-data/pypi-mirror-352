import math
import sys
import os
import pandas as pd
from itertools import product
from typing import Tuple, Dict, Any, List
import time
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
import array

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import backtrader as bt

from generic_csv_feed import VipHlDataFeed
from backtrader import num2date
from indicators.helper.dtpl import DTPL
from indicators.helper.pivot_high import PivotHigh
from indicators.helper.pivot_low import PivotLow
from indicators.viphl.dto.recovery_window import from_recovery_window_result_v2
from indicators.viphl.dto.settings import Settings
from indicators.viphl.dto.viphl import VipHL
from tvDatafeed import TvDatafeed, Interval
from dto.trade_v2 import TradeV2
from indicators.helper.close_average import CloseAveragePercent
from indicators.helper.percentile_nearest_rank import PercentileNearestRank
from indicators.helper.percent_rank import PercentRank
from indicators.dl.dl_v1_9_indicator import DLv1_9Indicator
from strategy.viphl.viphl_preload_strategy import VipHLPreloadStrategy

FIT_SCORE_MAX = 500
TICKER_NAME = "ETH"
TIMEFRAME = '6H'
# Global declarations at module level
global _log_file
_log_file = None

def log_print(*args, **kwargs):
    """Print to both console and log file if it exists."""
    print(*args, **kwargs)  # Print to console
    if _log_file is not None:
        print(*args, **kwargs, file=_log_file)
        _log_file.flush()

class PrecomputedIndicators:
    def __init__(self, dataframe, ticker):
        # Initialize cerebro for indicator calculation only
        cerebro = bt.Cerebro()
        data = bt.feeds.PandasData(dataname=dataframe)
        cerebro.adddata(data)
        cerebro.broker.set_coc(True)
        
        # Add strategy just to compute indicators
        cerebro.addstrategy(
            VipHLPreloadStrategy, 
            mintick=dataframe['mintick'].iloc[0],
            ticker=ticker
        )
        cerebro.run()

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
        ('trsi_threshold', 0),
        ('trsi_to_low_trsi_offset', 0),
        ('dtpl_trsi_threshold', 0),
        ('dtpl_trsi_to_low_trsi_offset', 0),
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
        ('ma_lookback_period', 500),
        ('fast_ma_length', 5),        # fast
        ('fast_ma_distr_threshold', 80),
        ('fast_ma_dtpl_distr_threshold', 100),
        ('fast_ma_vvip_distr_threshold', 100),
        ('slow_ma_length', 40),       # slow
        ('slow_ma_distr_threshold', 100),
        ('slow_ma_dtpl_distr_threshold', 100),
        ('slow_ma_vvip_distr_threshold', 100),

        # CA设置
        ('close_avg_percent_lookback', 500),
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
        self.normal_high_by_point = self.data.normal_high_by_point
        self.normal_low_by_point = self.data.normal_low_by_point
        self.trending_high_by_point = self.data.trending_high_by_point
        self.trending_low_by_point = self.data.trending_low_by_point
        self.close_average_percent = self.data.close_average_percent
        self.is_ma_trending = self.data.is_ma_trending
        ## trsi & ma
        self.trsi = self.data.trsi
        self.low_trsi = self.data.low_trsi
        self.slow_ma_distr_percent = self.data.slow_ma_distr_percent
        self.fast_ma_distr_percent = self.data.fast_ma_distr_percent

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

        # For tracking trades
        self.trade_list = []
        self.trade_detail_list = []  # this is for outputting trade list to excel using dictionary

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

        has_dl_signal: bool = (self.data.maybe_buy_signal[0] or self.data.maybe_two_by_zero_signal[0] or
                            self.data.maybe_dl_break_signal[0])
        is_dtpl: bool = self.data.is_dtpl[0]

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
            (self.data.bar_count_at_signal[0] > 3 or
                (self.data.bar_count_at_signal[0] == 3 and self.data.close[-1] < self.data.close[-2]))
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
        self.finalize_and_display_backtest_result()

    def finalize_and_display_backtest_result(self):
        win_count = 0
        loss_count = 0
        win_pnl = 0.0
        loss_pnl = 0.0

        trade_detail_list = []
        for index, trade in enumerate(self.trade_list):
            if trade.pnl > 0:
                win_count += 1
                win_pnl += trade.pnl
            else:
                loss_count += 1
                loss_pnl += trade.pnl

            first_return = trade.first_return
            rounded_return = round(first_return, 2)
            formatted_return = f"{rounded_return:.2f}" if rounded_return == int(rounded_return) else str(rounded_return)

            second_return = str(round(trade.second_return, 2)) if trade.take_profit else ""
            second_trade_time = num2date(trade.second_time).date() if trade.second_time != 0 else self.data.close[0]

            cur_trade_detail = {
                "No.": index + 1,
                "Entry Date": f'{num2date(trade.entry_time).date()} {num2date(trade.entry_time).time()}',
                "Status:": "live" if trade.is_open else "closed",
                "Weighted Return:": round(trade.pnl, 2),
                "1st Trade Time": num2date(trade.first_time).date(),
                "1st Return%": formatted_return,
                "2nd Trade Time": second_trade_time if trade.take_profit else "",
                "2nd Return%": second_return
            }
            trade_detail_list.append(cur_trade_detail)

            # print(
            #     f'{index}, {num2date(trade.entry_time).date()}, {"live" if trade.is_open else "closed"}, {round(trade.pnl, 2)},'
            #     f' {num2date(trade.first_time).date()}, {formatted_return}, {second_return}')
            # print('---------------------------')


        total_pnl = round(self.total_pnl, 2)
        avg_pnl_per_entry = round(self.total_pnl / len(self.trade_list), 2) if len(self.trade_list) > 0 else 0
        trade_count = len(trade_detail_list)
        winning_entry_rate = round(win_count / trade_count * 100, 2) if trade_count > 0 else 0
        avg_winning_pnl = round(win_pnl / win_count, 2) if win_count > 0 else 0
        avg_losing_pnl = round(loss_pnl / loss_count, 2) if loss_count > 0 else 0
        rounded_winning_pnl = round(win_pnl, 2)
        rounded_losing_pnl = round(loss_pnl, 2)
        fit_score = round(FIT_SCORE_MAX if loss_pnl == 0.0 else min((-win_pnl / loss_pnl), FIT_SCORE_MAX), 2)
        win_rate_ratio = (win_count / trade_count) / (1 - (win_count / trade_count)) if trade_count > 0 and (1 - (win_count / trade_count) )> 0 else 0
        pnl_ratio = (win_pnl / win_count) / math.fabs(loss_pnl / loss_count) if trade_count > 0 and win_count > 0 and loss_count > 0 else 0
        fit_score_v2 = round(FIT_SCORE_MAX if loss_pnl == 0.0 else min(win_rate_ratio * pnl_ratio, FIT_SCORE_MAX), 2)

        self.result = {
            "Total Pnl%": total_pnl,
            "Avg Pnl% per entry": avg_pnl_per_entry,
            "Trade Count": trade_count,
            "Winning entry%": winning_entry_rate,
            "Avg Winner%": avg_winning_pnl,
            "Avg Loser%": avg_losing_pnl,
            "Fit Score": fit_score
        }
        self.trade_detail_list = trade_detail_list
    
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
        df.to_csv(f'NVDA.csv', index=False)

def load_data_from_tv(ticker, exchange, timeframe, n_bars):
    token = ""
    # tv = TvDatafeed(username, password)
    # tv = TvDatafeed(token=token)
    tv = TvDatafeed()
    dataframe = tv.get_hist(symbol=ticker,exchange=exchange,interval=timeframe,n_bars=n_bars)
    dataframe['openinterest'] = 0
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

def initialize_cerebro(dataframe: pd.DataFrame, ticker: str, precomputed_indicators: bool = False) -> Tuple[bt.Cerebro, pd.DataFrame]:
    """
    Initialize Cerebro instance and load data once
    
    Returns:
        Tuple containing:
        - cerebro: Initialized Cerebro instance with data loaded
        - dataframe: The loaded data for reference
    """
    # Load data once
    
    # Initialize Cerebro
    cerebro = bt.Cerebro()
    
    # Add data feed
    if not precomputed_indicators:
        data = bt.feeds.PandasData(dataname=dataframe)
    else:
        data = VipHlDataFeed(
            dataname=f'{ticker.replace("/", "_")}.csv',
            datetime=0,
            open=1,
            high=2,
            low=3,
            close=4,
            volume=5,
            openinterest=6,
            dtformat='%Y-%m-%d %H:%M:%S',
            timeframe=bt.TimeFrame.Minutes
        )
    cerebro.adddata(data)
    
    # Set broker parameters
    cerebro.broker.set_coc(True)
    
    return cerebro, dataframe['mintick'].iloc[0]

def run_backtrader(
    cerebro: bt.Cerebro,
    mintick: float,
    strategy_params: Dict[str, Any],
    precomputed_indicators: bool
) -> Tuple[float, float, float]:
    """
    Run backtrader with specified parameters
    
    Args:
        ticker: Trading symbol (e.g., 'GBTC', 'BTC')
        exchange: Exchange name (e.g., 'BINANCE', 'AMEX') 
        timeframe: Trading timeframe (from tvDatafeed.Interval)
        n_bars: Number of bars to fetch
        ... (strategy parameters with default values)
        
    Returns:
        Tuple containing:
        - total_pnl: Total profit/loss percentage
        - max_drawdown: Maximum drawdown percentage 
        - fit_score: Strategy fit score
    """

    log_print(f"Running backtrader with parameters: {strategy_params}")

    # Add strategy with explicit parameters
    cerebro.addstrategy(
        VipHLStrategy,
        precomputed_indicators=precomputed_indicators,
        mintick=mintick,
        **strategy_params
    )
    
    # Run backtest
    results = cerebro.run()
    strat = results[0]
    
    return strat.result, strat.trade_detail_list

# Define parameter groups for sequential optimization
PARAMETER_GROUPS = [
    {
        # Group 1: DTPL
        # Format: (min, max, step size)
        'dtpl_trsi_threshold': (65, 88, 5),
        'dtpl_trsi_to_low_trsi_offset': (1, 5, 1),
        'fast_ma_dtpl_distr_threshold': (50, 85, 5),
    },
    {
        # Group 2: VVIPHL
        'vviphl_trsi_threshold': (40, 50, 1),
        'vviphl_trsi_to_low_trsi_offset': (1, 5, 1),
    },
    {
        # Group 3: RSI and MA Distribution thresholds
        'trsi_threshold': (50, 65, 5),
        'trsi_to_low_trsi_offset': (0, 5, 1),
        'fast_ma_distr_threshold': (40, 80, 5),
        'slow_ma_distr_threshold': (60, 100, 5),
    },
    {
        # Group 4: Close above low thresholds (synchronized)
        'close_above_low_threshold': (1.25, 1.5, 0.25),
        'close_above_recover_low_threshold': (1.25, 1.5, 0.25),
    },
]

def generate_param_combinations(param_ranges: Dict[str, Tuple[float, float, float]]) -> List[Dict[str, Any]]:
    """Generate all possible parameter combinations within the specified ranges."""
    param_values = {}
    for param, (min_val, max_val, step) in param_ranges.items():
        if step is None:  # Handle boolean parameters
            param_values[param] = [min_val]
        else:
            values = []
            current = min_val
            while current <= max_val:
                values.append(current)
                if current + step > max_val and current != max_val:
                    values.append(max_val)
                    break
                current += step
            param_values[param] = values
    
    # Generate all combinations
    keys = param_values.keys()
    combinations = product(*[param_values[key] for key in keys])
    
    # Filter combinations to keep only those where thresholds are equal
    filtered_combinations = []
    for combo in combinations:
        combo_dict = dict(zip(keys, combo))
        # Check if both threshold parameters exist in the combination
        if ('close_above_low_threshold' in combo_dict and 
            'close_above_recover_low_threshold' in combo_dict):
            # Only keep combinations where thresholds are equal
            if combo_dict['close_above_low_threshold'] == combo_dict['close_above_recover_low_threshold']:
                filtered_combinations.append(combo_dict)
        else:
            # Keep combinations that don't involve the thresholds
            filtered_combinations.append(combo_dict)
    
    return filtered_combinations

def get_optimal_workers():
    cores = multiprocessing.cpu_count()
    return max(1, cores - 1)  # Ensure at least 1 worker

def process_single_combination(params: Dict[str, Any], dataframe: pd.DataFrame, ticker: str, precomputed_indicators: bool) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Process a single parameter combination"""
    cerebro, mintick = initialize_cerebro(dataframe=dataframe, ticker=ticker, precomputed_indicators=precomputed_indicators)
    result, _ = run_backtrader(cerebro, mintick, params, precomputed_indicators)  # Ignore trade_detail_list for speed
    return params, result

def run_backtrader_single(param_combinations: List[Dict[str, Any]], dataframe: pd.DataFrame, ticker: str, precomputed_indicators: bool, min_trades: int = 10) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Run backtrader with multiple processes"""
    total_combinations = len(param_combinations)
    
    # Store all results
    all_results = []
    valid_results = []
    
    print(f"\nProcessing {total_combinations} combinations...")
    
    # Use a single ProcessPoolExecutor with optimal workers
    with ProcessPoolExecutor(max_workers=get_optimal_workers()) as executor:
        # Submit all combinations at once
        futures = [
            executor.submit(process_single_combination, params, dataframe, ticker, precomputed_indicators)
            for params in param_combinations
        ]
        
        # Process results with progress bar
        for future in tqdm(as_completed(futures), total=len(futures)):
            try:
                params, result = future.result()
                all_results.append((params, result))
                log_print(f"fit score for {params}: {result['Fit Score']}")
                if result['Trade Count'] >= min_trades:
                    valid_results.append((params, result))
            except Exception as e:
                print(f"Error in parameter combination: {str(e)}")
                raise e
    
    # Find the best result 
    if valid_results:
        best_params, best_result = max(valid_results, key=lambda x: x[1]['Fit Score'])
    elif all_results:
        best_params, best_result = max(all_results, key=lambda x: x[1]['Fit Score'])
        print(f"\nWarning: No results met minimum trade count of {min_trades}")
    else:
        return None, None
    
    # Print only the best result
    print(f"\nBest result: Score={best_result['Fit Score']:.2f}, "
          f"Trades={best_result['Trade Count']}, "
          f"Parameters={best_params}")
    
    return best_params, best_result

def sequential_optimize_strategy(ticker='SOLUSDT', exchange='BINANCE', timeframe=Interval.in_daily, n_bars=1500):
    """Run optimization sequentially for each parameter group"""
    group_best_params = {}
    group_best_results = {}
    precomputed_indicators = True
    
    # Load data once
    log_print("Loading data...")
    dataframe = load_data_from_tv(ticker=ticker, exchange=exchange, timeframe=timeframe, n_bars=n_bars)

    # Pre-compute indicators once
    if precomputed_indicators:
        log_print("Pre-computing indicators...")
        PrecomputedIndicators(dataframe, ticker=ticker)
    
    # Calculate and print total combinations
    total_combinations = 0
    for param_group in PARAMETER_GROUPS:
        combinations = generate_param_combinations(param_group)
        total_combinations += len(combinations)
    log_print(f"\nTotal number of combinations across all groups: {total_combinations}")
    
    # Process each group independently
    for group_idx, param_group in enumerate(PARAMETER_GROUPS, 1):
        log_print(f"\nGroup {group_idx}: {list(param_group.keys())}")
        
        if group_idx != 4:
            # For groups 1-3, simply generate and optimize the combinations.
            current_combinations = generate_param_combinations(param_group)
            best_params, best_result = run_backtrader_single(current_combinations, dataframe, ticker, precomputed_indicators)
            
            if best_params:
                group_best_params[group_idx] = best_params
                group_best_results[group_idx] = best_result
        else:
            # For group 4, combine each combination with the best params from groups 1-3.
            combined_params = {}
            for i in range(1, 4):
                if i in group_best_params:
                    combined_params.update(group_best_params[i])
            
            group4_combinations = generate_param_combinations(param_group)
            new_combinations = []
            for combo in group4_combinations:
                new_combo = combined_params.copy()
                new_combo.update(combo)
                new_combinations.append(new_combo)
            
            best_params, best_result = run_backtrader_single(new_combinations, dataframe, ticker, precomputed_indicators)
            if best_params:
                group_best_params[group_idx] = best_params
                group_best_results[group_idx] = best_result
    
    return group_best_params, group_best_results, {'ticker': ticker, 'exchange': exchange, 'timeframe': timeframe}

if __name__ == '__main__':
    start_time = time.time()

    # Run sequential optimization
    ticker_config = [
        # {
        #     'ticker': 'BNBUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_daily,
        # },
        # {
        #     'ticker': 'SUIUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_daily,
        # },
        # {
        #     'ticker': 'BNBUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_12_hour,
        # },
        # {
        #     'ticker': 'SUIUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_12_hour,
        # },
        # {
        #     'ticker': 'BNBUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_6_hour,
        # },
        # {
        #     'ticker': 'SUIUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_6_hour,
        # },
        # {
        #     'ticker': 'XRPUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_daily,
        # },
        # {
        #     'ticker': 'XRPUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_12_hour,
        # },
        # {
        #     'ticker': 'XRPUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_6_hour,
        # },
        # {
        #     'ticker': 'DOGEUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_daily,
        # },
        # {
        #     'ticker': 'DOGEUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_12_hour,
        # },
        # {
        #     'ticker': 'DOGEUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_6_hour,
        # },
        # {
        #     'ticker': 'ADAUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_daily,
        # },
        # {
        #     'ticker': 'ADAUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_6_hour,
        # },
        # {
        #     'ticker': 'ADAUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_12_hour,
        # },
        # {
        #     'ticker': 'LTCUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_daily,
        # },
        # {
        #     'ticker': 'LTCUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_6_hour,
        # },
        # {
        #     'ticker': 'LTCUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_12_hour,
        # },
        # {
        #     'ticker': 'AVAXUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_daily,
        # },
        # {
        #     'ticker': 'AVAXUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_6_hour,
        # },
        # {
        #     'ticker': 'AVAXUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_12_hour,
        # },
        # {
        #     'ticker': 'LTCUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_daily,
        # },
        # {
        #     'ticker': 'LTCUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_6_hour,
        # },
        # {
        #     'ticker': 'LTCUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_12_hour,
        # },
        # {
        #     'ticker': 'TRXUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_daily,
        # },
        # {
        #     'ticker': 'TRXUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_6_hour,
        # },
        # {
        #     'ticker': 'LINKUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_daily,
        # },
        # {
        #     'ticker': 'LINKUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_6_hour,
        # },
        # {
        #     'ticker': 'LINKUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_12_hour,
        # },
        # {
        #     'ticker': 'SHIBUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_daily,
        # },
        # {
        #     'ticker': 'SHIBUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_6_hour,
        # },
        # {
        #     'ticker': 'SHIBUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_12_hour,
        # },
        # {
        #     'ticker': 'HBARUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_daily,
        # },
        # {
        #     'ticker': 'HBARUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_6_hour,
        # },
        # {
        #     'ticker': 'HBARUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_12_hour,
        # },
        # {
        #     'ticker': 'DOTUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_daily,
        # },
        # {
        #     'ticker': 'DOTUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_6_hour,
        # },
        # {
        #     'ticker': 'DOTUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_12_hour,
        # },
        # {
        #     'ticker': 'NEARUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_daily,
        # },
        # {
        #     'ticker': 'NEARUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_6_hour,
        # },
        # {
        #     'ticker': 'NEARUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_12_hour,
        # },
        # {
        #     'ticker': 'UNIUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_daily,
        # },
        # {
        #     'ticker': 'UNIUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_6_hour,
        # },
        # {
        #     'ticker': 'UNIUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_12_hour,
        # },
        # {
        #     'ticker': 'XLMUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_daily,
        # },
        # {
        #     'ticker': 'XLMUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_6_hour,
        # },
        # {
        #     'ticker': 'XLMUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_12_hour,
        # },
        # {
        #     'ticker': 'AAVEUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_daily,
        # },
        # {
        #     'ticker': 'AAVEUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_6_hour,
        # },
        # {
        #     'ticker': 'AAVEUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_12_hour,
        # },
        # {
        #     'ticker': 'OPUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_daily,
        # },
        # {
        #     'ticker': 'OPUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_6_hour,
        # },
        # {
        #     'ticker': 'OPUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_12_hour,
        # },
        # {
        #     'ticker': 'TRXUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_12_hour,
        # },
        # {
        #     'ticker': 'ICPUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_6_hour,
        # },
        # {
        #     'ticker': 'ICPUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_12_hour,
        # },
        # {
        #     'ticker': 'ICPUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_daily,
        # },
        # {
        #     'ticker': 'FILUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_6_hour,
        # },
        # {
        #     'ticker': 'FILUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_12_hour,
        # },
        # {
        #     'ticker': 'FILUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_daily,
        # },
        # {
        #     'ticker': 'RENDERUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_6_hour,
        # },
        # {
        #     'ticker': 'RENDERUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_12_hour,
        # },
        # {
        #     'ticker': 'RENDERUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_daily,
        # },
        # {
        #     'ticker': 'BCHUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_6_hour,
        # },
        # {
        #     'ticker': 'BCHUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_12_hour,
        # },
        # {
        #     'ticker': 'BCHUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_daily,
        # },
        # {
        #     'ticker': 'IMXUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_6_hour,
        # },
        # {
        #     'ticker': 'IMXUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_12_hour,
        # },
        # {
        #     'ticker': 'IMXUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_daily,
        # },
        # {
        #     'ticker': 'APTUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_6_hour,
        # },
        # {
        #     'ticker': 'APTUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_12_hour,
        # },
        # {
        #     'ticker': 'APTUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_daily,
        # },
        # {
        #     'ticker': 'ENSUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_6_hour,
        # },
        # {
        #     'ticker': 'ENSUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_12_hour,
        # },
        # {
        #     'ticker': 'ENSUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_daily,
        # },
        # {
        #     'ticker': 'GALAUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_6_hour,
        # },
        # {
        #     'ticker': 'GALAUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_12_hour,
        # },
        # {
        #     'ticker': 'GALAUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_daily,
        # },
        # {
        #     'ticker': 'ETCUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_6_hour,
        # },
        # {
        #     'ticker': 'ETCUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_12_hour,
        # },
        # {
        #     'ticker': 'ETCUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_daily,
        # },
        # {
        #     'ticker': 'POLUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_daily,
        # },
        # {
        #     'ticker': 'RENDERUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_daily,
        # },
        # {
        #     'ticker': 'ALGOUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_daily,
        # },
        # {
        #     'ticker': 'ALGOUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_6_hour,
        # },
        # {
        #     'ticker': 'ALGOUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_12_hour,
        # },
        # {
        #     'ticker': 'OMUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_daily,
        # },
        # {
        #     'ticker': 'OMUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_6_hour,
        # },
        # {
        #     'ticker': 'OMUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_12_hour,
        # },
        # {
        #     'ticker': 'PEPEUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_daily,
        # },
        # {
        #     'ticker': 'PEPEUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_6_hour,
        # },
        # {
        #     'ticker': 'PEPEUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_12_hour,
        # },
        # {
        #     'ticker': 'TONUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_6_hour,
        # },
        # {
        #     'ticker': 'TONUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_12_hour,
        # },
        # {
        #     'ticker': 'TONUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_daily,
        # },
        # {
        #     'ticker': '1000000/BINANCE:BTCUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_6_hour,
        # },
        # {
        #     'ticker': '1000000/BINANCE:BTCUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_12_hour,
        # },
        # {
        #     'ticker': '1000000/BINANCE:BTCUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_daily,
        # },
        #         {
        #     'ticker': '100000/BINANCE:ETHUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_6_hour,
        # },
        # {
        #     'ticker': '100000/BINANCE:ETHUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_12_hour,
        # },
        # {
        #     'ticker': '100000/BINANCE:ETHUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_daily,
        # },
        # {
        #     'ticker': '1000/BINANCE:SOLUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_6_hour,
        # },
        # {
        #     'ticker': '1000/BINANCE:SOLUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_12_hour,
        # },
        # {
        #     'ticker': '1000/BINANCE:SOLUSDT',
        #     'exchange': 'BINANCE',
        #     'timeframe': Interval.in_daily,
        # },
        {
            'ticker': '1/BINANCE:ADAUSDT',
            'exchange': 'BINANCE',
            'timeframe': Interval.in_6_hour,
        },
        {
            'ticker': '1/BINANCE:ADAUSDT',
            'exchange': 'BINANCE',
            'timeframe': Interval.in_12_hour,
        },
        {
            'ticker': '1/BINANCE:ADAUSDT',
            'exchange': 'BINANCE',
            'timeframe': Interval.in_daily,
        },
        {
            'ticker': '10/BINANCE:XRPUSDT',
            'exchange': 'BINANCE',
            'timeframe': Interval.in_6_hour,
        },
        {
            'ticker': '10/BINANCE:XRPUSDT',
            'exchange': 'BINANCE',
            'timeframe': Interval.in_12_hour,
        },
        {
            'ticker': '10/BINANCE:XRPUSDT',
            'exchange': 'BINANCE',
            'timeframe': Interval.in_daily,
        },
    ]
    for config in ticker_config:
        # Create log filename based on config
        log_filename = f"{config['ticker'].replace('/', '_')}_{config['timeframe']}.log"
        
        _log_file = open(log_filename, 'w')
        
        try:
            log_print(f"Starting optimization for {config['ticker']} on {config['timeframe']}")
            
            n_bars = 1500
            group_best_params, group_best_results, test_config = sequential_optimize_strategy(
                ticker=config['ticker'], 
                exchange=config['exchange'], 
                timeframe=config['timeframe'], 
                n_bars=n_bars
            )
            
            # Calculate elapsed time
            end_time = time.time()
            elapsed_time = end_time - start_time
            hours = int(elapsed_time // 3600)
            minutes = int((elapsed_time % 3600) // 60)
            seconds = int(elapsed_time % 60)
            
            log_print("\n=== Final Optimization Results ===")
            log_print(f"Time taken: {hours:02d}:{minutes:02d}:{seconds:02d}")
            
            log_print(f"\nTest Configuration:")
            log_print(f"Ticker: {test_config['ticker']}")
            log_print(f"Exchange: {test_config['exchange']}")
            log_print(f"Timeframe: {test_config['timeframe']}")
            
            log_print("\nBest Parameters by Group:")
            ordered_params = [
                "close_above_low_threshold",
                "close_above_recover_low_threshold",
                "trsi_threshold",
                "trsi_to_low_trsi_offset",
                "dtpl_trsi_threshold",
                "dtpl_trsi_to_low_trsi_offset",
                "vviphl_trsi_threshold",
                "vviphl_trsi_to_low_trsi_offset",
                "fast_ma_distr_threshold",
                "slow_ma_distr_threshold",
                "fast_ma_dtpl_distr_threshold"
            ]
            for group_idx, params in group_best_params.items():
                log_print(f"\nGroup {group_idx} Parameters:")
                for key in ordered_params:
                    if key in params:
                        log_print(f"{key}: {params[key]}")
                
                log_print(f"\nGroup {group_idx} Results:")
                for metric, value in group_best_results[group_idx].items():
                    log_print(f"{metric}: {value}")
                log_print("---------------------------")
            
            # New Combined Section
            log_print("\n=== Combined Best Parameters ===")
            combined_best_params = {}
            for params in group_best_params.values():
                combined_best_params.update(params)
            for key in ordered_params:
                if key in combined_best_params:
                    log_print(f"{key}: {combined_best_params[key]}")
        finally:
            # Always close the log file
            if _log_file:
                _log_file.close()
                _log_file = None