from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from collections import defaultdict
from itertools import permutations
import json
import numpy as np
import pandas as pd
import yfinance as yf
from django.contrib import messages
from common import highchart_format 
from common.strategy import Distance_method
from common.postprocessing import handle_signals_data, handle_bollinger_band_data, handle_profit_loss_data

def web(request):
    if not request.user.is_authenticated:
        messages.success(request, 'Sorry ! Please Log In.')
        return redirect("http://140.116.214.156:1984/account/login")
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
    
    object = Distance_method(
        stock1 = str(stock1), 
        stock2 = str(stock2), 
        start_date = str(start_date), 
        end_date = str(end_date), 
        window_size = int(window_sizes), 
        n_times = int(std)
        )
    object.run()
    
    # Handle signals data
    plot_signals, table_signals = handle_signals_data(object = object, 
                                                      stock1 = stock1, 
                                                      stock2 = stock2, 
                                                      data1 = data1_response, 
                                                      data2 = data2_response)
    
    # Handle Bollinger Bands data
    spread, middle_line, upper_line, lower_line, bands_signals_sell, bands_signals_buy = handle_bollinger_band_data(object = object)
    
    # Handle Profit_loss data
    pl_daily_profits, pl_total_values, pl_entry_point, pl_exit_point = handle_profit_loss_data(object = object)

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