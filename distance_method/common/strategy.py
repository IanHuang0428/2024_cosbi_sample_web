import os
import sys
import json
import math
import argparse
import itertools
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from collections import defaultdict

class Distance_method():
    
    def __init__(self, stock1:str, stock2:str, start_date:str, end_date:str, window_size:int, n_times:int, figure_path:str=None) -> None:
        
        # init params
        self.stock1 = stock1
        self.stock2 = stock2
        self.start_date = start_date
        self.end_date = end_date
        self.window_size = window_size
        self.n_times = n_times
        self.figure_path = figure_path
        self.folder_path = None
        
        # profit&loss params
        self.profit_loss_val = 0
        self.oper_value = 10000
        self.daily_profits = []
        self.total_values = []
        self.entry_point = []
        self.exit_point = []
        
        # strategy params
        self.trading_signals = defaultdict(list)
        self.closing_prices = {}
        self.spread = None  
        self.rolling_mean = None
        self.rolling_std = None  
        self.upper_line = None
        self.lower_line = None
        self.upper_status = 0
        self.lower_status = 0
          
    def _strategy(self):        
        
        # 價格進行標準化
        normalized_price1 = pd.Series(np.log(self.closing_prices[self.stock1]))
        normalized_price2 = pd.Series(np.log(self.closing_prices[self.stock2]))  
        
        # 將兩組標準化後的數組相減並計算移動標準差與移動平均值
        self.spread = normalized_price1 - normalized_price2   
        self.rolling_mean = self.spread.rolling(window=self.window_size).mean()
        self.rolling_std = self.spread.rolling(window=self.window_size).std() 
        self.upper_line = self.rolling_mean + self.n_times * self.rolling_std
        self.lower_line = self.rolling_mean - self.n_times * self.rolling_std

        for ind, val in enumerate(self.spread):
            
            if np.isnan(float(val)):
                continue
            
            date = self.spread.index[ind]
            target_spread = self.spread[ind]  
            
            if target_spread >= self.upper_line[ind] and (self.upper_status == 0):
                self.trading_signals[f'upper'].append([date, target_spread, 'SELL', "Open"])
                self.upper_status = 1

            if target_spread <= self.rolling_mean[ind] and (self.upper_status == 1):
                self.trading_signals[f'upper'].append([date, target_spread, 'BUY', "Close"])
                self.upper_status = 0


            if target_spread <= self.lower_line[ind] and (self.lower_status == 0):
                self.trading_signals[f'lower'].append([date, target_spread, 'BUY', "Open"])
                self.lower_status = 1

            if target_spread >= self.rolling_mean[ind] and (self.lower_status == 1):
                self.trading_signals[f'lower'].append([date, target_spread, 'SELL', "Close"])
                self.lower_status = 0
        
    def _load_data(self):
        # create result data folder 
        if self.figure_path != None:
            current_time = datetime.now().strftime("%Y%m%d")
            self.folder_path = f"{self.figure_path}/{current_time}_{self.stock1}_{self.stock2}_{self.start_date}_{self.end_date}"
            if not os.path.exists(self.folder_path):
                os.makedirs(self.folder_path)
        data1 = yf.download(self.stock1, start=self.start_date, end=self.end_date)
        data2 = yf.download(self.stock2, start=self.start_date, end=self.end_date)
        self.closing_prices[self.stock1] = data1['Adj Close']
        self.closing_prices[self.stock2] = data2['Adj Close']
    
    def _plot_original_price(self):
        fig, ax1 = plt.subplots(figsize=(16,5))
        # 繪製第一支股票的價格
        ax1.plot(self.closing_prices[self.stock1], label=self.stock1)
        ax1.set_xlabel('date')
        ax1.set_ylabel(self.stock1)
        ax1.tick_params('y')

        # 繪製第二支股票的價格
        ax2 = ax1.twinx()
        ax2.plot(self.closing_prices[self.stock2], label=self.stock2, color='orange')
        ax2.set_ylabel(self.stock2)
        ax2.tick_params('y')

        init_val = 0
        for n in range((math.ceil(len(self.closing_prices[self.stock1])/self.window_size)-1)):
            vline_date = self.closing_prices[self.stock1].index[init_val + self.window_size]
            plt.axvline(x=vline_date, color='r', linestyle='--', linewidth=1)
            init_val+=self.window_size
        fig.legend(bbox_to_anchor=(0.1, 0.9))
        plt.savefig(f'{self.folder_path}/original_price.png')
    
    def _plot_all_results(self):
        
        plt.figure(figsize=(18,10))
        
        # Plot normalization_price & signals
        plt.subplot(3, 1, 1)
        backtest_result = pd.DataFrame(index=[], columns=['BUY', 'SELL'])
        plt.plot(self.closing_prices[self.stock1],  label=self.stock1, zorder=1)
        plt.plot(self.closing_prices[self.stock2], label=self.stock2, zorder=1)
        for key, values in self.trading_signals.items():
            for ele in values:
                date = ele[0].strftime('%Y-%m-%d')
                data_type  = ele[2]
                
                if data_type == "SELL":
                    x = pd.Timestamp(date)
                    stock1_price = pd.DataFrame(self.closing_prices[self.stock1]).loc[date, 'Adj Close']
                    stock2_price = pd.DataFrame(self.closing_prices[self.stock2]).loc[date, 'Adj Close']
                    plt.scatter(x, stock1_price, marker='v', color='red', zorder=2)
                    plt.scatter(x, stock2_price, marker='^', color='green', zorder=2)
                    backtest_result.loc[f'{key}_{date}'] = {'BUY': stock2_price, 'SELL': stock1_price}
                    if ele[3] == "Open":
                        plt.axvline(x=x, color='slategray', linestyle='--', linewidth=1, zorder=2)
                    else:
                        plt.axvline(x=pd.Timestamp(ele[0].strftime('%Y-%m-%d')), color='hotpink', linestyle='--', linewidth=1, zorder=2)
                    
                elif data_type == "BUY":
                    x = pd.Timestamp(date)
                    stock1_price = pd.DataFrame(self.closing_prices[self.stock1]).loc[date, 'Adj Close']
                    stock2_price = pd.DataFrame(self.closing_prices[self.stock2]).loc[date, 'Adj Close']
                    plt.scatter(x, stock1_price, marker='^', color='green', zorder=2)
                    plt.scatter(x, stock2_price, marker='v', color='red', zorder=2)
                    backtest_result.loc[f'{key}_{date}'] = {'BUY': stock1_price, 'SELL': stock2_price}
                    if ele[3] == "Open":
                        plt.axvline(x=x, color='slategray', linestyle='--', linewidth=1, zorder=2)
                    else:
                        plt.axvline(x=pd.Timestamp(ele[0].strftime('%Y-%m-%d')), color='hotpink', linestyle='--', linewidth=1, zorder=2)
        plt.title(f'Price')
        plt.xticks([])
        plt.xlim(self.closing_prices[self.stock1].index[0], self.closing_prices[self.stock1].index[-1])
        plt.legend()
            
        # Profit and Loss Chart 
        plt.subplot(3, 1, 2)
        dates, profits = zip(*self.daily_profits)
        plt.plot(dates, profits, linestyle='-', color="navy", linewidth=0.8, label="Daily Value", zorder=2)
        dates, profits = zip(*self.total_values)
        plt.plot(dates, profits, linestyle='-', color="sienna", linewidth=0.8, label="Cash", zorder=1)
        dates, value = zip(*self.entry_point)
        plt.scatter(dates, value, color="orange", label="entry point", marker='o', zorder=3)
        dates, value = zip(*self.exit_point)
        plt.scatter(dates, value, color="darkcyan", label="exit point", marker='o', zorder=3)
        plt.gca().yaxis.set_major_formatter(mticker.PercentFormatter())
        plt.title('Daily Profit&Loss Over Time')
        plt.xticks([])
        plt.xlim(self.closing_prices[self.stock1].index[0], self.closing_prices[self.stock1].index[-1])
        plt.legend()
        
        # Plot spread & signals
        plt.subplot(3, 1, 3)
        std_lower_points = []
        std_upper_points = []
        for ele in self.trading_signals:
            if ele == "lower":
                std_lower_points += self.trading_signals[ele]
            if ele == "upper":
                std_upper_points += self.trading_signals[ele]                  
        
        for ele in std_upper_points:
            if ele[2] == "BUY":
                plt.scatter(ele[0], ele[1], marker='^', color='green', zorder=2)
            elif ele[2] == "SELL":
                plt.scatter(ele[0], ele[1], marker='v', color='red', zorder=2)
                    
        for ele in std_lower_points:
            if ele[2] == "BUY":
                plt.scatter(ele[0], ele[1], marker='^', color='green', zorder=2)

            elif ele[2] == "SELL":
                plt.scatter(ele[0], ele[1], marker='v', color='red', zorder=2)        
                
        for key, values in self.trading_signals.items():
            for ele in values:
                if ele[2] == "SELL":
                    if ele[3] == "Open":
                        plt.axvline(x=pd.Timestamp(ele[0].strftime('%Y-%m-%d')), color='slategray', linestyle='--', linewidth=1, zorder=2)
                    else:
                        plt.axvline(x=pd.Timestamp(ele[0].strftime('%Y-%m-%d')), color='hotpink', linestyle='--', linewidth=1, zorder=2)
                    
                elif ele[2] == "BUY":
                    if ele[3] == "Open":
                        plt.axvline(x=pd.Timestamp(ele[0].strftime('%Y-%m-%d')), color='slategray', linestyle='--', linewidth=1, zorder=2)
                    else:
                        plt.axvline(x=pd.Timestamp(ele[0].strftime('%Y-%m-%d')), color='hotpink', linestyle='--', linewidth=1, zorder=2)
                        
                        
        plt.plot(self.spread, linewidth=1, color='Maroon', label=f'spread = log({self.stock1}) - log({self.stock2})') 
        plt.plot(self.upper_line, color='red', linewidth=0.8, linestyle='--', zorder=1, label=f'upper_line = middle_line + {self.n_times}*std')
        plt.plot(self.lower_line, color='red', linewidth=0.8, linestyle='--', zorder=1, label=f'lower_line = middle_line - {self.n_times}*std')
        plt.plot(self.rolling_mean, linewidth=0.8, label=f'middle_line') 
        plt.title(f'Trading signals')
        plt.xlim(self.closing_prices[self.stock1].index[0], self.closing_prices[self.stock1].index[-1])
        plt.legend()
        plt.savefig(f'{self.folder_path}/results.png')
        plt.close()
    
    def _calculate_profit_loss(self): 
        
        tmp_result = []
        unique_trades = set()
        for trade in [item for sublist in self.trading_signals.values() for item in sublist]:
            trade_tuple = tuple(trade[1:])
            if trade_tuple not in unique_trades:
                tmp_result.append(trade)
                unique_trades.add(trade_tuple)
        all_signals = sorted(tmp_result, key=lambda x: x[0])

        # 初始變量設定
        all_qty1 = 0
        all_qty2 = 0
        qty1 = 0
        qty2 = 0
        stock1_type = None
        stock2_type = None
        for ind, val in enumerate(self.closing_prices[self.stock1]):
            date = self.closing_prices[self.stock1].index[ind]
            price1 = self.closing_prices[self.stock1][ind]
            price2 = self.closing_prices[self.stock2][ind]
            daily_profit = 0

            # 檢查是否有開倉信號
            matching_entry = list(filter(lambda x: x[0] == date and x[3] == 'Open', all_signals))
            
            if matching_entry:
                qty1 = (self.oper_value / 2) / price1
                qty2 = (self.oper_value / 2) / price2

                if stock1_type == "BUY" and stock2_type == "SELL":
                    daily_profit = (all_qty1 * price1) - (all_qty2 * price2)
                elif stock1_type == "SELL" and stock2_type == "BUY":
                    daily_profit = -(all_qty1 * price1) + (all_qty2 * price2)
                
                if matching_entry[0][2] == "BUY":
                    entry_profit = -(qty1 * price1) + (qty2 * price2)
                    stock1_type = "BUY"
                    stock2_type = "SELL"
                elif matching_entry[0][2] == "SELL":
                    entry_profit = (qty1 * price1) - (qty2 * price2)
                    stock1_type = "SELL"
                    stock2_type = "BUY"
                self.profit_loss_val += entry_profit

                all_qty1 += qty1
                all_qty2 += qty2
                
                # 計算當前總收益百分比
                entry_percentage = ((self.profit_loss_val+daily_profit) / self.oper_value) * 100
                self.entry_point.append((date, entry_percentage))
                    
            # 檢查是否有平倉信號
            matching_exits = list(filter(lambda x: x[0] == date and x[3] == 'Close', all_signals))
            if matching_exits:
                if matching_exits[0][2] == "BUY":
                    daily_profit = -(all_qty1 * price1) + (all_qty2 * price2)
                elif matching_exits[0][2] == "SELL":
                    daily_profit = (all_qty1 * price1) - (all_qty2 * price2)
            
                self.profit_loss_val += daily_profit
                
                # 計算當前總收益百分比
                exit_percentage = (self.profit_loss_val / self.oper_value) * 100
                self.exit_point.append((date, exit_percentage))
                
                # initialize
                all_qty1 = 0
                all_qty2 = 0
                stock1_type = None
                stock2_type = None
            
            # 根據持有的倉位記錄每日的獲利
            if not matching_exits and not matching_entry:
                if stock1_type == "BUY" and stock2_type == "SELL":
                    daily_profit = (all_qty1 * price1) - (all_qty2 * price2)
                elif stock1_type == "SELL" and stock2_type == "BUY":
                    daily_profit = -(all_qty1 * price1) + (all_qty2 * price2)
                
                # 計算當前總收益百分比
                daily_percentage = ((self.profit_loss_val + daily_profit) / self.oper_value) * 100
                self.daily_profits.append((date, daily_percentage))

            # 記錄總值百分比
            total_percentage = (self.profit_loss_val / self.oper_value) * 100
            self.total_values.append((date, total_percentage))
            
        # Convert the list to a JSON serializable format
        if self.folder_path:
            json_data = {"daily_value":[]}
            for ts, val in self.daily_profits:
                json_data["daily_value"].append({"date":ts.strftime('%Y-%m-%d'), "value":val})
            with open(f'{self.folder_path}/daily_value.json', "w") as f:
                json.dump(json_data, f, indent=4)
            
    def run(self):
        
        self._load_data()
        
        if self.figure_path != None:
            self._plot_original_price()
        
        if len(self.closing_prices[self.stock1]) < int(self.window_size):
            return
 
        self._strategy()
        self._calculate_profit_loss()
        
        if self.figure_path != None:
            self._plot_all_results()
            
if __name__ == "__main__":
      
    def parse_args(pargs=None):

        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        
        parser.add_argument('--stock1', required=False,
                            default='AAPL',
                            help='Data')
        
        parser.add_argument('--stock2', required=False,
                            default='GLD',
                            help='Data')
        
        parser.add_argument('--start_date', required=False, default='2021-01-01',
                            help='Date[time] in YYYY-MM-DD[THH:MM:SS] format')

        parser.add_argument('--end_date', required=False, default='2024-01-01',
                            help='Date[time] in YYYY-MM-DD[THH:MM:SS] format')

        parser.add_argument('--window_size', required=False, default=200,
                            help='')

        parser.add_argument('--n_times', required=False, default=2,
                            help='')

        parser.add_argument('--figure_path', required=False, 
                            default="/home/thomas/Desktop/distance_method/distance_method/common", 
                            help='')    
        return parser.parse_args(pargs)
    
    args = parse_args()
    
    object = Distance_method(
        stock1 = str(args.stock1), 
        stock2 = str(args.stock2), 
        start_date = str(args.start_date), 
        end_date = str(args.end_date), 
        window_size = int(args.window_size), 
        n_times = int(args.n_times),
        figure_path = str(args.figure_path)
        )
    
    object.run()
    
    print(object.trading_signals)