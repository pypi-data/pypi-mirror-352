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
from indicators.viphl.dto.viphl import VipHL
from tvDatafeed import TvDatafeed, Interval
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
        ('krsi_coefficient', 2.5),
        ('krsi_offset', 0.5),
        ('krsi_vvip_only', True),

        # Reduce stop loss
        ('reduce_stop_loss_threshold', 3),
        ('dtpl_reduce_stop_loss_threshold', 3),
        ('vviphl_reduce_stop_loss_threshold', 5),

        # T-RSI
        ('trsi_length', 14),
        ('trsi_threshold', 57),
        ('trsi_to_low_trsi_offset', 3),
        ('dtpl_trsi_threshold', 0),
        ('dtpl_trsi_to_low_trsi_offset', 3),
        ('vviphl_trsi_threshold', 0),
        ('vviphl_trsi_to_low_trsi_offset', 5),

        # DTPL
        ('dtpl_condition_lookback_period', 15),
        ('dtpl_high_lookback_period', 250),
        ('dtpl_fast_ma_length', 10),
        ('dtpl_medium_ma_length', 40),
        ('dtpl_slow_ma_length', 100),
        ('dtpl_no_hl', False),

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
        ('cycle_month', 3.0),  # Equivalent to cycleMonth
        ('stop_loss_pt', 1.0),  # Equivalent to stopLossPt
        ('first_gain_ca_multiplier', 2.0),  # Equivalent to firstGainCAMultiplier
        ('max_gain_pt', 50.0),  # Equivalent to maxGainPt
        ('max_exit_ca_multiplier', 4.0),  # Equivalent to maxExitCAMultiplier
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
        self.ma10 = bt.indicators.SMA(self.data.close, period=10)
        self.ma40 = bt.indicators.SMA(self.data.close, period=40)
        self.ma100 = bt.indicators.SMA(self.data.close, period=100)
        self.trending_ma_delta = self.ma10 - self.ma100
        self.trending_ma_delta_distr = PercentileNearestRank(self.trending_ma_delta, period=self.p.trending_ma_delta_distr_lookback, percentile=self.p.trending_ma_delta_distr_threshold)

        self.is_ma_greater = bt.And(bt.Cmp(self.ma10, self.ma40) == 1, bt.Cmp(self.ma40, self.ma100) == 1)
        self.is_ma_trending = bt.And(self.is_ma_greater, bt.Cmp(self.trending_ma_delta, self.trending_ma_delta_distr) == 1)

        ## trsi & ma
        self.trsi = bt.ind.RSI(self.datas[0], period=self.p.trsi_length)
        self.low_trsi = bt.indicators.Lowest(self.trsi, period=3)
        self.slow_ma = bt.indicators.SMA(self.data.close, period=self.p.slow_ma_length)
        self.fast_ma = bt.indicators.SMA(self.data.close, period=5)
        self.slow_ma_delta = bt.indicators.ROC(self.slow_ma, period=1)
        self.fst_ma_delta = bt.indicators.ROC(self.fast_ma, period=1)
        self.slow_ma_distr_percent = 100 - bt.indicators.PercentRank(self.slow_ma_delta.roc, period=self.p.ma_lookback_period) * 100
        self.fast_ma_distr_percent = 100 - bt.indicators.PercentRank(self.fst_ma_delta.roc, period=self.p.ma_lookback_period) * 100

        self.trsi.plotinfo.plot = False
        self.low_trsi.plotinfo.plot = False
        self.slow_ma_delta.plotinfo.plot = False
        self.fst_ma_delta.plotinfo.plot = False

        self.dtpl = DTPL(self.data)

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
        return

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
    tv = TvDatafeed(token=token)
    # tv = TvDatafeed()
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

if __name__ == '__main__':
    # ticker, ma10, ma40, hrsi, rd_on, rc_win1, rc_win2, nh, nh_hrsi, nh_n, lookback, ca_period
    input = ["BNB", 100, 100, 100, False, 10, 8, False, 99, 8, 1000, 500]
    timeframe = Interval.in_daily
    TICKER_NAME = input[0]
    TIMEFRAME = timeframe.value
    # dataframe = load_data_from_tv('{input[0]}USDT', 'BINANCE', timeframe, 1000)
    dataframe = load_data_from_tv('NVDA', 'NASDAQ', timeframe, 1000)
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

    # for optimize
    # cerebro.optstrategy(
    #     SmaCross,
    #     pfast=range(10, 20),
    #     pslow=range(40, 60)
    # )

    cerebro.addstrategy(
        VipHLStrategy
    )  # Add the trading strategy
    cerebro.run()  # run it all
    cerebro.plot(style='candlestick', barup='green', bardown='red')
