import os
import json
import shutil 
import datetime
import requests
import psycopg2
import pandas as pd
from pathlib import Path
from collections import defaultdict
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

class MailHandler:
    _host_email_address: str
    _host_passwd: str
    _subject: str
    
    def __init__(self):       
        gmail_acct = Path.cwd() / "report.json"
        with open (gmail_acct, 'r')as f:
            acct_info = json.load(f)
        self._host_email_address = acct_info['username']
        self._host_passwd = acct_info['password']
        self._smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        self._smtp.ehlo() # 驗證SMTP伺服器
        self._smtp.login(self._host_email_address,self._host_passwd)   # 登入寄件者gmail
        self._local_time = datetime.date.today()
        
    def _create_mail(self, subject:str, to_address: str):
        mail = MIMEMultipart()
        mail['From'] = self._host_email_address
        mail['To'] = to_address
        mail['Subject'] = subject
        return mail     

    def _add_file(self, mail: MIMEMultipart, file: str):
        with open(file, 'rb') as fp:
            attach_file = MIMEBase('application', "octet-stream")
            attach_file.set_payload(fp.read())
        encoders.encode_base64(attach_file)
        attach_file.add_header('Content-Disposition', 'attachment', filename=f"{self._local_time}_signals_report.xlsx")
        mail.attach(attach_file)
        
    def send(self, to_address, file_path):
        mail = self._create_mail(f"Monitor Report {self._local_time}", to_address)
        contents = "This is signals report."
        mail.attach(MIMEText(contents))
        self._add_file(mail, file_path)
        status = self._smtp.sendmail(self._host_email_address, to_address, mail.as_string())

        return status

class FuncClient(object):
    _instance = None
    ROOT = 'http://140.116.214.156:1986/usFunc/'
    DISTANCEMETHOD_URL= ROOT + "distance_method/" 

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        pass

    def _send_request(self, url: str, request_body: str):
            request_header = {
                "Content-Type"  : "application/json"
            }
            response = requests.post(url, data=json.dumps(request_body), headers=request_header)
            
            return response  
        
    def pairtrading_backtesting(self,
                params: dict,
                method:str
                ):
        
            request_body = {
                "params" : params,
                "method":method
            }                       

            response = self._send_request(self.DISTANCEMETHOD_URL, request_body)
                
            if response.status_code == 200:
                return response.json()['detail']
            
            elif response.status_code == 404:
                print("It has no trading pair found!")
                print(response.json()['msg'])
            else:
                print("Something wrong at get spreads, status code:", response.status_code)
                print(response.json()['msg'])
                
            return None   
        
class UserTrackingHandler(object):

    def __init__(self):
        
        file_path = Path.cwd() / "report.json"
        with open (file_path, 'r')as f:
            self.db_info = json.load(f)
        self.db_conn = psycopg2.connect(
                                    host = self.db_info['USER_DB_HOST'],
                                    database = self.db_info['USER_DB_NAME'],
                                    user = self.db_info['USER_DB_USER'],
                                    password = self.db_info['USER_DB_PASSWORD'],
                                    port = self.db_info['USER_DB_PORT'])
    
        
        self.db_cursor = self.db_conn.cursor()

    def _get_user_id(self, username):
        sql = f"""SELECT id FROM auth_user
            WHERE username = %s"""
        sql_val = (username, )
        self.db_cursor.execute(sql, sql_val)
        user_id = self.db_cursor.fetchall()[0][0]
        
        return user_id
           
    # get tracker's user name & email
    def get_all_user_info(self):
        sql = f"""
            SELECT DISTINCT (auth_user.username), auth_user.email FROM user_tracker
            INNER JOIN auth_user ON user_tracker.user_id = auth_user.id;
        """
        self.db_cursor.execute(sql)
        res = self.db_cursor.fetchall()
        return res

    # get all track spreads
    def get_all_track_params_combination(self):
        sql = f"""
            SELECT username, user_tracker.created_at::date,  start_date::date, end_date::date, method,
            stock1, stock2, window_size, n_times
            FROM user_tracker
            INNER JOIN auth_user ON auth_user.id = user_tracker.user_id
            """
        self.db_cursor.execute(sql)
        res = self.db_cursor.fetchall()
        return res

class ReportHandler(object):

    all_track_contents = defaultdict(list)
    func_api_respones = defaultdict(list)
    
    def __init__(self):
        self.mail = MailHandler()
        self.uth = UserTrackingHandler()
        self.fc = FuncClient()
     
        self.email_folder_path = Path.cwd()  / "email_reports"
        self.tracker_folder_path = Path.cwd()  / "tracker_results" 
        os.makedirs(self.email_folder_path, exist_ok=True)
        os.makedirs(self.tracker_folder_path, exist_ok=True)
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