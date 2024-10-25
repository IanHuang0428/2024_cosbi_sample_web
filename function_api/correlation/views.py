from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from django.db import connection
from rest_framework.response import Response
import json
from pathlib import Path

from lib.strategy import Distance_method

class ViewSetValidate(object):
    
    def check_params(self, payload: dict, required_params: list, valid_params: list) -> bool:

        # request body is empty
        if not payload:
            self.response = Response(data={"msg":"params is empty"})
            self.response.status_code = 402
            return False
        
        # request body contain invalid parameters
        invalid = set(payload.keys()) - set(valid_params)
        missing = set(required_params) - set(payload.keys())
        msg = ""
        
        # all parameters is valid
        if not invalid and not missing:
            for key in set(valid_params) - set(payload.keys()):
                payload[key] = None
            return True
        
        msg = msg + f"invalid parameters {invalid}" if invalid else msg
        msg = msg + f"required parameters {missing} is missing" if missing else msg
        self.response = Response(data={"msg":msg})        
        self.response.status_code = 402
        return False
    
    def validate_params(self, params) -> bool:
        return True
    
    def validate_method(self, method) -> bool:
        if method not in ['distance']:
            msg = "method must in ['distance']"
            self.response = Response(data={"msg":msg})
            self.response.status_code = 402
            return False
        return True

class PairTradingBacktestingViewSet(viewsets.ModelViewSet, ViewSetValidate):
    queryset = None
    parser_classes = (JSONParser,)
    response = None
    required_params = ["params", "method"]
    valid_params = ["params", "method"]
       
    def _validate(self, payload:dict) -> bool:
        
        return (self.check_params(payload, self.required_params, self.valid_params)) and (
                self.validate_params(payload['params'])) and (
                self.validate_method(payload['method']))
                
    def create(self, request):

        method = request.data.get("method")
        params = request.data.get("params")

        # check input 
        if not self._validate(request.data):
            return self.response
        
        results = {}
        if method =="distance":
            object = Distance_method(
                stock1 = str(params["stock1"]), 
                stock2 = str(params["stock2"]), 
                start_date = str(params["start_date"]), 
                end_date = str(params["end_date"]), 
                window_size = int(params["window_size"]), 
                n_times = int(params["n_times"]),
                )
        
            object.run()        
            results["trading_signals"] = dict(object.trading_signals)
            results["exe_trading_signals"] = object.exe_trading_signals
            results["daily_profits"] = object.daily_profits
            results["total_values"] = object.total_values
            results["entry_point"] = object.entry_point
            results["exit_point"] = object.exit_point
            results["spread"] = object.spread.reset_index().to_json(orient='records')
            results["middle_line"] = object.rolling_mean.reset_index().to_json(orient='records')
            results["upper_line"] = object.upper_line.reset_index().to_json(orient='records')
            results["lower_line"] = object.lower_line.reset_index().to_json(orient='records')
    
            
        results = json.dumps(results, indent=4, ensure_ascii=False)
        results = json.loads(results)
        
        # not found in database
        if len(results) == 0:
            self.response = Response(data={"msg":"not found"})
            self.response.status_code = 404
            return self.response
        
        self.response = Response(data={"msg":"Succeed", 'detail':results})  
        self.response.status_code = 200
        return self.response
