import os
import json
import shutil 
import datetime
from pathlib import Path
import pandas as pd
from collections import defaultdict
from common.func_client import FuncClient
from common.user_setting_operation import  UserTrackingHandler
from common.mail import MailHandler

class ReportHandler(object):

    all_track_contents = defaultdict(list)
    func_api_respones = defaultdict(list)
    
    def __init__(self):
        self.mail = MailHandler()
        self.uth = UserTrackingHandler()
        self.fc = FuncClient()
        
        
        self.email_folder_path = Path.cwd() / "common" / "email_reports"
        self.tracker_folder_path = Path.cwd() / "common" / "tracker_results"        
        self.user_info = dict(self.uth.get_all_user_info())       
        
    def _create_local_email_file(self):
        today = datetime.date.today().strftime('%Y-%m-%d')
        for ele in self.func_api_respones:
            for signal in self.func_api_respones[ele]:
                if signal[0] == today:  
                    user = ele.split("_")[0] 
                    stock1 = ele.split("_")[1] 
                    stock2 = ele.split("_")[2] 
                    start_date = ele.split("_")[3] 
                    window_size = ele.split("_")[4] 
                    std = ele.split("_")[5] 

                    data = pd.DataFrame({
                        "user": user,
                        "stock1": stock1,
                        "stock2": stock2,
                        "start_date": start_date,
                        "window_size": window_size,
                        "std": std,
                        "status" : signal[3]
                    }, index=[0])
                    file_path = os.path.join(self.email_folder_path, 'data.xlsx')
                    with pd.ExcelWriter(file_path, engine='xlsxwriter') as w:
                        data.to_excel(w, sheet_name='Short', index=False)
                    print("Excel completed")
                    
                    # 發送信件
                    email = self.user_info[user]
                    res = self.mail.send(email, f"{self.email_folder_path}/data.xlsx")
                    if res=={}:
                        print("Send email successful!")
                        self._remove_local_email_file(f"{self.email_folder_path}/data.xlsx")
                    else:
                        print("Send email failed!")
                    
    def _remove_local_email_file(self, filename: str):
        print(f"successful remove {filename}!")
        os.remove(filename)

    def _init_local_tracker_contents(self):
        
        # 查看本地端已經存在的追蹤使用者 & 刪除不存在的使用者資料夾
        self.already_exist_users = [item for item in os.listdir(self.tracker_folder_path) if os.path.isdir(os.path.join(self.tracker_folder_path , item))]
        for already_exist_user in self.already_exist_users:
            if already_exist_user not in self.user_info:
                shutil.rmtree(f"{self.tracker_folder_path}/{already_exist_user}")
        
        # 查看本地端已經存在的追蹤內容 & 刪除使用者取消追蹤的參數    
        self.already_exist_params = defaultdict(list)
        for folder_name in os.listdir(self.tracker_folder_path):
            user_folder_path = os.path.join(self.tracker_folder_path, folder_name)
            if os.path.isdir(user_folder_path):
                for file_name in os.listdir(user_folder_path):
                    file_path = os.path.join(user_folder_path, file_name)
                    if os.path.isfile(file_path):
                        self.already_exist_params[folder_name].append(file_name)
                    
        for user in self.all_track_contents:
            tracker_params = [f"{content[5]}_{content[6]}_{content[2]}_{content[7]}_{content[8]}.json" for content in self.all_track_contents[user]]
            for already_exist_param in self.already_exist_params[user]:
                if already_exist_param not in tracker_params:
                    os.remove(f"{self.tracker_folder_path}/{user}/{already_exist_param}")
        
    def _get_signals(self, content):
               
        data = self.fc.pairtrading_backtesting(
                    params = {
                        "stock1" : content[5],
                        "stock2" : content[6],
                        "start_date":content[2].strftime('%Y-%m-%d'), 
                        "end_date" : datetime.date.today().strftime('%Y-%m-%d'),
                        "window_size":content[7],
                        "n_times":content[8]
                        },
                    method = content[4]
                    )
        
        # 將 JSON 資料保存到文件
        user = content[0]
        file_name = f"{content[5]}_{content[6]}_{content[2]}_{content[7]}_{content[8]}.json"
        with open(f'{self.tracker_folder_path}/{user}/{file_name}', 'w') as json_file:
            json.dump(data, json_file, indent=4)      

            
        signals = data["trading_signals"]["upper"] + data["trading_signals"]["lower"]
        for signal in signals:
            self.func_api_respones[f"{user}_{content[5]}_{content[6]}_{content[2]}_{content[7]}_{content[8]}"].append(signal)

    def main(self):
        
        # 創立使用者資料夾 & 將追蹤內容依照使用者分群
        for ele in self.uth.get_all_track_params_combination():
            user = ele[0]
            if not os.path.exists(f"{self.tracker_folder_path}/{user}"):
                os.makedirs(f"{self.tracker_folder_path}/{user}")
            self.all_track_contents[user].append(ele)
        
        # 初始化本地資料夾
        self._init_local_tracker_contents()
        
        # 計算追蹤參數組合 & 製作email內容
        for user in self.all_track_contents:
            email = self.user_info[user]
            individual_track_contents = self.all_track_contents[user]
            for content in  individual_track_contents:
                self._get_signals(content)
                
        # 檢查是否要發送信件
        self._create_local_email_file()

 
if __name__ == "__main__":
    report = ReportHandler()
    report.main()