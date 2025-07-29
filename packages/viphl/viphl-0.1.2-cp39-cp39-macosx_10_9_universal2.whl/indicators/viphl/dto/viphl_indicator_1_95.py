import backtrader as bt

from indicators.helper.pivot_high import PivotHigh
from indicators.helper.pivot_low import PivotLow
from indicators.helper.close_average import CloseAveragePercent
from indicators.helper.percentile_nearest_rank import PercentileNearestRank
from indicators.viphl.dto.recovery_window import from_recovery_window_result_v2
from indicators.viphl.dto.viphl import VipHL, Settings


class VipHLIndicatorV1_95(bt.Indicator):
    lines = (
        'break_hl_at_price',
        'is_hl_satisfied',
        'is_vvip_signal',
        'is_non_vvip_signal',
        'no_signal_but_close_above',
        'violate_extended_bar_cross',
        'violate_search_range_close_above_bar_count',
        'violate_recover_window',
        'violate_signal_window',
    )

    params = (
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
        ('show_hl_break', True),
        ('recover_hl_width', 4),

        # VVIPHL
        ('vviphl_min_bypoint_count', 2),

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
    )

    lines_info = []

    def __init__(self):
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
            bar_index=self.bar_index(),
            time=self.data.datetime,
            last_bar_index=self.last_bar_index(),
            settings=viphl_settings,
            hls=[],
            vip_by_points=[],
            new_vip_by_points=[],
            recovery_windows=[],
            latest_recovery_windows=[],
            normal_high_by_point=self.normal_high_by_point,
            normal_low_by_point=self.normal_low_by_point,
            trending_high_by_point=self.trending_high_by_point,
            trending_low_by_point=self.trending_low_by_point
        )

    def next(self):
        self.viphl.update_built_in_vars(bar_index=self.bar_index(), last_bar_index=self.last_bar_index())
        self.viphl.update(is_ma_trending=self.is_ma_trending, close_avg_percent=self.close_average_percent[0])

        # Update the recovery window
        self.viphl.update_recovery_window(
            trap_recover_window_threshold=self.params.trap_recover_window_threshold,
            search_range=self.params.close_above_hl_search_range,
            low_above_hl_threshold=self.params.low_above_hl_threshold,
            close_avg_percent=self.params.close_avg_percent_lookback
        )

        # Check the recovery window
        recovery_window_result = self.viphl.check_recovery_window_v3(
            close_avg_percent=self.params.close_avg_percent_lookback,
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

        self.l.break_hl_at_price[0] = flattern.break_hl_at_price
        self.l.is_hl_satisfied[0] = flattern.is_hl_satisfied
        self.l.is_vvip_signal[0] = flattern.is_vvip_signal
        self.l.is_non_vvip_signal[0] = flattern.is_non_vvip_signal
        self.l.no_signal_but_close_above[0] = flattern.no_signal_but_close_above
        self.l.violate_extended_bar_cross[0] = flattern.violate_extended_bar_cross
        self.l.violate_search_range_close_above_bar_count[0] = flattern.violate_search_range_close_above_bar_count
        self.l.violate_recover_window[0] = flattern.violate_recover_window
        self.l.violate_signal_window[0] = flattern.violate_signal_window

        if self.last_bar_index() == self.bar_index():
            for hl in self.viphl.hls:
                if hl.extend_end_bar_index > 0 and hl.post_extend_end_bar_index == 0:
                    end_index = hl.extend_end_bar_index
                elif hl.post_extend_end_bar_index > 0:
                    end_index = hl.post_extend_end_bar_index
                else:
                    end_index = hl.end_bar_index
                self.lines_info.append((hl.hl_value, hl.start_bar_index, end_index))
