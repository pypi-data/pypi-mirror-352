import backtrader as bt


class VipHlDataFeed(bt.feeds.GenericCSVData):
    lines = (
        'normal_high_by_point',
        'normal_low_by_point',
        'trending_high_by_point',
        'trending_low_by_point',
        'close_average_percent',
        'is_ma_trending',
        'maybe_buy_signal',
        'maybe_two_by_zero_signal',
        'maybe_dl_break_signal',
        'bar_count_at_signal',
        'slow_ma_distr_percent',
        'fast_ma_distr_percent',
        'trsi',
        'low_trsi',
        'is_dtpl'
    )

    params = (
        ('datetime', 0),
        ('open', 1),
        ('high', 2),
        ('low', 3),
        ('close', 4),
        ('volume', 5),
        ('openinterest', 6),
        ('normal_high_by_point', 7),
        ('normal_low_by_point', 8),
        ('trending_high_by_point', 9),
        ('trending_low_by_point', 10),
        ('close_average_percent', 11),
        ('is_ma_trending', 12),
        ('maybe_buy_signal', 13),
        ('maybe_two_by_zero_signal', 14),
        ('maybe_dl_break_signal', 15),
        ('bar_count_at_signal', 16),
        ('slow_ma_distr_percent', 17),
        ('fast_ma_distr_percent', 18),
        ('trsi', 19),
        ('low_trsi', 20),
        ('is_dtpl', 21)
    )
