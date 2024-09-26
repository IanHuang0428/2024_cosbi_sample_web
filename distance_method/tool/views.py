from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from collections import defaultdict
from itertools import permutations
import json
import numpy as np
import pandas as pd
import yfinance as yf
import datetime
from django.contrib import messages
from common import highchart_format 
from common.strategy import Distance_method

def web(request):
    # if not request.user.is_authenticated:
    #     messages.success(request, 'Sorry ! Please Log In.')
    #     return redirect("http://140.116.214.156:9002/account/login")
    return (render(request,"base.html"))

def ScreenerDistance(request):
    stock1 = request.POST.get("stock1")
    stock2 = request.POST.get("stock2")
    start_date = request.POST.get("start_date")
    end_date = request.POST.get("end_date")
    window_sizes = request.POST.get("window_sizes")
    std = int(request.POST.get("std"))
    
    # yahoo database
    data1_response = yf.download(stock1, start=start_date, end=end_date)
    if data1_response is not None:
        data1_his = highchart_format.yahoo_convert_quote_series(data1_response)
    data2_response = yf.download(stock2, start=start_date, end=end_date)
    if data2_response is not None:
        data2_his = highchart_format.yahoo_convert_quote_series(data2_response)   
    
    # stock price data
    plot_corr = pd.DataFrame({
        'date': data1_response.index,
        stock1: data1_response['Close'],
        stock2: data2_response['Close']
    })

    object = Distance_method(
        stock1 = str(stock1), 
        stock2 = str(stock2), 
        start_date = str(start_date), 
        end_date = str(end_date), 
        window_size = int(window_sizes), 
        n_times = int(std),
        )
    object.run()
    
    # Handle signals data
    res = object.trading_signals
    sorted_list = sorted((res['upper'] + res['lower']), key=lambda x: x[0])
    plot_signals = defaultdict(list)   
    for row in sorted_list:
        date1 = highchart_format.convert_timestamp_to_highchart(row[0].strftime("%Y-%m-%d"))
        stock1_price1 = plot_corr.loc[row[0], stock1]
        stock2_price1 = plot_corr.loc[row[0], stock2]       
        
        if row[2]=="BUY":
            plot_signals["stock1_buy_point"].append([date1, stock1_price1]) 
            plot_signals["stock2_sell_point"].append([date1, stock2_price1])
        elif row[2]=="SELL":
            plot_signals["stock1_sell_point"].append([date1, stock1_price1]) 
            plot_signals["stock2_buy_point"].append([date1, stock2_price1]) 
        if row[3]=="Open":
            plot_signals["Entry_Exit"].append({ "date": date1, "color": 'pink', "label": 'entry'})
        elif row[3]=="Close":
            plot_signals["Entry_Exit"].append({ "date": date1, "color": 'gray', "label": 'exit'})

    table_signals = []
    for row in sorted_list:
        stock1_price1 = round(plot_corr.loc[row[0].strftime("%Y-%m-%d"), stock1], 2)
        stock2_price1 = round(plot_corr.loc[row[0].strftime("%Y-%m-%d"), stock2], 2)     
        if row[2]=="BUY":
            table_signals.append({"date":row[0].strftime("%Y-%m-%d"), "stock1_action": "BUY", "stock1_price":stock1_price1, "stock2_action":"SELL", "stock2_price":stock2_price1, "type":row[3]})
        elif row[2]=="SELL":
            table_signals.append({"date":row[0].strftime("%Y-%m-%d"), "stock1_action":"SELL", "stock1_price":stock1_price1, "stock2_action":"BUY", "stock2_price":stock2_price1, "type":row[3]})
    
    # Handle Bollinger Bands data
    spread = object.spread.dropna()
    spread = spread.reset_index()
    spread = spread.values.tolist()
    spread = [[int(date.timestamp() * 1000), val] for date, val in spread]
    middle_line = object.rolling_mean.dropna()
    middle_line = middle_line.reset_index()
    middle_line = middle_line.values.tolist()
    middle_line = [[int(date.timestamp() * 1000), val] for date, val in middle_line]
    upper_line = object.upper_line.dropna()
    upper_line = upper_line.reset_index()
    upper_line = upper_line.values.tolist()
    upper_line = [[int(date.timestamp() * 1000), val] for date, val in upper_line]
    lower_line = object.lower_line.dropna()
    lower_line = lower_line.reset_index()
    lower_line = lower_line.values.tolist()
    lower_line = [[int(date.timestamp() * 1000), val] for date, val in lower_line]
    bands_signals_sell = [[int(ele[0].timestamp() * 1000), ele[1]] for ele in sorted_list if ele[2]=='SELL']
    bands_signals_buy = [[int(ele[0].timestamp() * 1000) , ele[1]] for ele in sorted_list if ele[2]=='BUY']
    
    # Handle Profit_loss data
    pl_daily_profits = [[int(date.timestamp() * 1000), val] for date, val in object.daily_profits]
    pl_total_values = [[int(date.timestamp() * 1000), val] for date, val in object.total_values]
    pl_entry_point = [[int(date.timestamp() * 1000), val] for date, val in object.entry_point]
    pl_exit_point = [[int(date.timestamp() * 1000), val] for date, val in object.exit_point]

    response = {
        'stock1': stock1, 
        'stock2': stock2, 
        'data1_his': data1_his, 
        'data2_his': data2_his,
        'plot_signals': plot_signals,
        'table_signals': table_signals,
        'spread' : spread,
        'middle_line' : middle_line,
        'upper_line' : upper_line,
        'lower_line' : lower_line,
        'bands_signals_sell' : bands_signals_sell,
        'bands_signals_buy' : bands_signals_buy,
        'pl_daily_profits' : pl_daily_profits,
        'pl_total_values' : pl_total_values,
        'pl_entry_point' : pl_entry_point,
        'pl_exit_point' : pl_exit_point
    }
    
    return JsonResponse(response)




# from common.data_client import APIClient 
# from common.func_client import  FuncClient
# from common.database_manager import Database_Manager 
# fc = FuncClient()
# ac = APIClient()
# Communicate with function api
# params = {
#     'start_date' : start_date,
#     'end_date' : end_date,
#     'period' : int(window_sizes),
#     'n_times' : std1,
#     "portfolio_value": 50000,
#     "cash" : 200000,
#     "commperc" : 0.001,
# }
# res = fc.pairtrading_backtesting(pair=[stock1,stock2], method="distance", data_source="yahoo", params=params)
# res_2 = fc.pairtrading_backtesting(pair=[stock2,stock1], method="distance", data_source="yahoo", params=params)