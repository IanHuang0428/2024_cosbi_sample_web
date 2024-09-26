import datetime
import time
import pandas as pd

def convert_timestamp_to_highchart(time_str):
    return int(time.mktime(datetime.datetime.strptime(time_str, "%Y-%m-%d").timetuple()))*1000

def convert_quote_series(ohlcv: dict):
    timestamp_series = list(map(convert_timestamp_to_highchart, ohlcv['date']))
    close = list(zip(timestamp_series, ohlcv['close']))
    ohlc = list(zip(timestamp_series, ohlcv['open'], ohlcv['high'], ohlcv['low'], ohlcv['close']))
    volume = list(zip(list(timestamp_series), ohlcv['volume']))
    series = {'ohlc':ohlc, 'volume':volume, 'close':close}
    return series

def yahoo_convert_quote_series(ohlcv):
    timestamp_series = list(map(convert_timestamp_to_highchart, [date.strftime('%Y-%m-%d') for date in ohlcv.index]))
    close = list(zip(timestamp_series, list(ohlcv['Close'])))
    ohlc = list(zip(timestamp_series, list(ohlcv['Open']), list(ohlcv['High']), list(ohlcv['Low']), list(ohlcv['Close'])))
    volume = list(zip(list(timestamp_series), list(ohlcv['Volume'])))
    series = {'ohlc':ohlc, 'volume':volume, 'close':close}
    return series

def calculate_price_ratio(ohlcv1, ohlcv2):
    timestamp_series = list(map(convert_timestamp_to_highchart, [date.strftime('%Y-%m-%d') for date in ohlcv1.index]))
    price_ratio = list(zip(timestamp_series, [x / y for x, y in zip(list(ohlcv1['Close']), list(ohlcv2['Close']))]))
    return price_ratio
