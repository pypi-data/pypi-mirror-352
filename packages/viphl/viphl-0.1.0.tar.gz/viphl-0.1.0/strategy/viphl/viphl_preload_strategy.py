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


class VipHLPreloadStrategy(bt.Strategy):
    # list of parameters which are configurable for the strategy
    params = (
        ('ticker', 'BTCUSDT'),
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
        ('reduce_stop_loss_threshold', 3),
        ('dtpl_reduce_stop_loss_threshold', 3),
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
        '''init is called once at the last row'''

        '''
        viphl
        '''
        # Compute indicators as before
        self.normal_high_by_point = PivotHigh(leftbars=self.p.high_by_point_n, rightbars=self.p.high_by_point_m)
        self.normal_low_by_point = PivotLow(leftbars=self.p.low_by_point_n, rightbars=self.p.low_by_point_m)
        self.trending_high_by_point = PivotHigh(leftbars=self.p.high_by_point_n_on_trend, rightbars=self.p.high_by_point_m_on_trend)
        self.trending_low_by_point = PivotLow(leftbars=self.p.low_by_point_n_on_trend, rightbars=self.p.low_by_point_m_on_trend)
        self.close_average_percent = CloseAveragePercent(close_avg_percent_lookback=self.p.close_avg_percent_lookback)

        self.ma10 = bt.indicators.SMA(self.data.close, period=10)
        self.ma40 = bt.indicators.SMA(self.data.close, period=40)
        self.ma100 = bt.indicators.SMA(self.data.close, period=100)
        self.trending_ma_delta = self.ma10 - self.ma100
        self.trending_ma_delta_distr = PercentileNearestRank(self.trending_ma_delta, period=self.p.trending_ma_delta_distr_lookback, percentile=self.p.trending_ma_delta_distr_threshold)

        self.is_ma_greater = bt.And(bt.Cmp(self.ma10, self.ma40) == 1, bt.Cmp(self.ma40, self.ma100) == 1)
        self.is_ma_trending = bt.And(self.is_ma_greater, bt.Cmp(self.trending_ma_delta, self.trending_ma_delta_distr) == 1)

        self.dl = DLv1_9Indicator(
            hlv4=None,
            viphl=None,
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
        ## trsi & ma
        self.trsi = bt.ind.RSI(self.datas[0], period=self.p.trsi_length)
        self.low_trsi = bt.indicators.Lowest(self.trsi, period=3)
        self.slow_ma = bt.indicators.SMA(self.data.close, period=self.p.slow_ma_length)
        self.fast_ma = bt.indicators.SMA(self.data.close, period=self.p.fast_ma_length)
        self.slow_ma_delta = bt.indicators.ROC(self.slow_ma, period=1)
        self.fst_ma_delta = bt.indicators.ROC(self.fast_ma, period=1)
        self.slow_ma_distr_percent = 100 - bt.indicators.PercentRank(self.slow_ma_delta.roc, period=self.p.ma_lookback_period) * 100
        self.fast_ma_distr_percent = 100 - bt.indicators.PercentRank(self.fst_ma_delta.roc, period=self.p.ma_lookback_period) * 100

        # For exporting data
        self.csv_export_list = []
        return

    def next(self):
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

    def stop(self):
        self.export_csv()

    def export_csv(self):
        # Convert list to DataFrame
        df = pd.DataFrame(self.csv_export_list)

        # Export DataFrame to CSV
        df.to_csv(f'{self.p.ticker.replace("/", "_")}.csv', index=False)