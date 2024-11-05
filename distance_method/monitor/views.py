from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from common.user_setting_operation import  UserTrackingHandler
from common.func_client import FuncClient
import json
import os
from pathlib import Path
import datetime
import yfinance as yf
from common import highchart_format 
from common.postprocessing import handle_api_signals_data, handle_api_bollinger_band_data, handle_api_profit_loss_data, handle_api_exe_signals_data

uth = UserTrackingHandler()
fc = FuncClient()


def web(request):
    # render search page
    if not request.user.is_authenticated:
        messages.success(request, 'Sorry ! Please Log In.')
        return redirect(f'/account/login')
    return (render(request, "monitor.html"))

@csrf_exempt
def get_track_list(request):
    user = str(request.user)
    tracks = uth.get_all_track_params_combination_from_user(user)
    track_data  = []
    for track in tracks:    
        ele = {
            'track_date':track[0].strftime('%Y-%m-%d'),
            'start_date':track[1].strftime('%Y-%m-%d'),
            'end_date':track[2].strftime('%Y-%m-%d'),
            'method':track[3],
            'stock1':track[4],
            'stock2':track[5],
            'window_size':track[6],
            'n_times':track[7],
        }
        track_data.append(ele)
        
    if track_data is None:
        """error handling"""
    return JsonResponse({"track_data": track_data}) 

@csrf_exempt
def add_track(request):

    stock1 = request.POST.get("stock1")
    stock2 = request.POST.get("stock2")
    start_date = request.POST.get("start_date")
    end_date = request.POST.get("end_date")
    method = request.POST.get("method")
    window_sizes = request.POST.get("window_sizes")
    std = int(request.POST.get("std"))
    
    uth.add(
        username=str(request.user),
        method = method,
        start_date=start_date,       
        end_date = end_date,  
        stock1=stock1,                  
        stock2=stock2,                  
        window_size=window_sizes,                
        n_times=std,              
    )
    
    return JsonResponse({"msg": "Successful!"})

@csrf_exempt
def remove_track(request):
    method = request.POST.get('method')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    stock1 = request.POST.get('stock1')
    stock2 = request.POST.get('stock2')
    window_size = request.POST.get('window_size')
    user = str(request.user)
    std = request.POST.get('n_times')
    uth.remove(
        username=user,
        method = method,
        start_date=start_date,       
        end_date = end_date,  
        stock1=stock1,                  
        stock2=stock2,                  
        window_size=window_size,                
        n_times=std,              
    )
        
    return JsonResponse({'msg': 'Successful'})

@csrf_exempt
def run_tracker(request):
    start_date = request.POST.get('start_date')
    end_date = datetime.date.today().strftime('%Y-%m-%d')
    stock1 = request.POST.get('stock1')
    stock2 = request.POST.get('stock2')
    method = request.POST.get('method')
    window_size = request.POST.get('window_size')
    std = request.POST.get('n_times')
    user = str(request.user)
    
      
    env = os.environ.get('PROJECT_ENV', 'dev')
    if env == "prod":
        tracker_folder_path = "/distance_method/tracker_results"
    elif env == "dev":
        tracker_folder_path = Path.cwd().parent / "tracker_results"
    else:
        raise EnvironmentError("Unknown environment! Please set the 'ENV' variable to 'production' or 'development'.")
    
    file_path = f"{tracker_folder_path}/{user}/{stock1}_{stock2}_{start_date}_{window_size}_{std}.json"
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            data = json.load(file) 
    else:
        data = fc.pairtrading_backtesting(
            params = {
                "stock1" : stock1,
                "stock2" : stock2,
                "start_date":start_date, 
                "end_date" : end_date,
                "window_size":window_size,
                "n_times":std
                },
            method = method
            )
        # 將 JSON 資料保存到文件
        with open(f'{file_path}', 'w') as json_file:
            json.dump(data, json_file, indent=4)       
                
    # yahoo database
    data1_response = yf.download(stock1, start=start_date, end=end_date)
    if data1_response is not None:
        data1_his = highchart_format.yahoo_convert_quote_series(data1_response)
    data2_response = yf.download(stock2, start=start_date, end=end_date)
    if data2_response is not None:
        data2_his = highchart_format.yahoo_convert_quote_series(data2_response)  
    # Handle signals data
    plot_signals, table_signals = handle_api_signals_data(object = data, 
                                        stock1 = stock1, 
                                        stock2 = stock2, 
                                        data1 = data1_response, 
                                        data2 = data2_response)
    
    # Handle Bollinger Bands data
    spread, middle_line, upper_line, lower_line, bands_signals_sell, bands_signals_buy = handle_api_bollinger_band_data(object = data)
    
    # Handle Profit_loss data
    pl_daily_profits, pl_total_values, pl_entry_point, pl_exit_point = handle_api_profit_loss_data(object = data)
    
    # Handle execution signals data
    exe_table_signals = handle_api_exe_signals_data(object = data, 
                                                    stock1 = stock1, 
                                                    stock2 = stock2, 
                                                    data1 = data1_response, 
                                                    data2 = data2_response)

    response = {
        'stock1': stock1, 
        'stock2': stock2, 
        'data1_his': data1_his, 
        'data2_his': data2_his,
        'plot_signals': plot_signals,
        'exe_table_signals':exe_table_signals,
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

