import json
import psycopg2
import os
from pathlib import Path


class ConnectUserDB(object):
    
    def __init__(self):
        
        env = os.environ.get('PROJECT_ENV', 'dev')
        # Connect to PostgreSQL server (Docker)
        if env == "prod":
            self.db_conn = psycopg2.connect(
                                        host=os.environ['USER_DB_HOST'],
                                        database=os.environ['USER_DB_NAME'],
                                        user=os.environ['USER_DB_USER'],
                                        password=os.environ['USER_DB_PASSWORD'],
                                        port=os.environ['USER_DB_PORT'])
            print("Connect successful!")

        # Connect to PostgreSQL server (Local)
        elif env == "dev":
            file_path = Path.cwd() / "config" / "correlation_db.json"
            with open (file_path, 'r')as f:
                self.db_info = json.load(f)
            self.db_conn = psycopg2.connect(
                                        host = self.db_info['USER_DB_HOST'],
                                        database = self.db_info['USER_DB_NAME'],
                                        user = self.db_info['USER_DB_USER'],
                                        password = self.db_info['USER_DB_PASSWORD'],
                                        port = self.db_info['USER_DB_PORT'])
        else:
            raise EnvironmentError("Unknown environment! Please set the 'ENV' variable to 'production' or 'development'.")
    
        
        self.db_cursor = self.db_conn.cursor()

    def _get_user_id(self, username):
        sql = f"""SELECT id FROM auth_user
            WHERE username = %s"""
        sql_val = (username, )
        self.db_cursor.execute(sql, sql_val)
        user_id = self.db_cursor.fetchall()[0][0]
        
        return user_id

class UserTrackingHandler(ConnectUserDB):

    def __init__(self):
        super().__init__()
        
    # add track
    def add(self, **kwargs):
        user_id = self._get_user_id(kwargs['username'])
        
        # 確定要插入的欄位和相應的值
        fields = ['user_id']
        values = [user_id]
        placeholders = ['%s']
        
        # 動態添加其餘的欄位和值
        optional_fields = [
            'method', 'stock1', 'stock2', 'start_date', 'end_date', 'window_size', 'n_times'
        ]
        
        for field in optional_fields:
            if field in kwargs and kwargs[field] is not None:
                fields.append(field)
                values.append(kwargs[field])
                placeholders.append('%s')
        
        # 動態生成 INSERT 語句
        sql = f"""
            INSERT INTO user_tracker ({', '.join(fields)}) 
            VALUES({', '.join(placeholders)}) 
            ON CONFLICT DO NOTHING;
        """
        
        # 執行 SQL 語句
        self.db_cursor.execute(sql, values)
        self.db_conn.commit()

    # remove track
    def remove(self, **kwargs):
        user_id = self._get_user_id(kwargs['username'])
        
        # 起始 WHERE 條件，最少要有 user_id 作為條件
        conditions = ['user_id = %s']
        values = [user_id]
        
        # 可選的條件
        optional_conditions = [
            'method', 'stock1', 'stock2', 'start_date', 'end_date', 'window_size', 'n_times'
        ]
        
        # 動態添加條件
        for field in optional_conditions:
            if field in kwargs and kwargs[field] is not None:
                conditions.append(f"{field} = %s")
                values.append(kwargs[field])
        
        # 動態生成 DELETE 語句
        sql = f"""
            DELETE FROM user_tracker 
            WHERE {' AND '.join(conditions)}
        """
        
        # 執行 SQL 語句
        self.db_cursor.execute(sql, values)
        self.db_conn.commit()
        return

    # get user email from name
    def get_user_email(self, user):

        sql = f"""
            SELECT email FROM auth_user 
            where username = %s
        """
        sql_val = (user, )
        self.db_cursor.execute(sql, sql_val)
        res = self.db_cursor.fetchall()[0][0]
        return res
    
    # get tracker's user name & email
    def get_all_user_info(self):
        sql = f"""
            SELECT DISTINCT (auth_user.username), auth_user.email FROM user_tracker
            INNER JOIN auth_user ON user_tracker.user_id = auth_user.id;
        """
        self.db_cursor.execute(sql)
        res = self.db_cursor.fetchall()
        return res

    # select track spreads
    def get_all_track_params_combination_from_user(self, user):
        sql = f"""
            SELECT user_tracker.created_at::date,  start_date::date, end_date::date, method,
            stock1, stock2, window_size, n_times
            FROM user_tracker
            INNER JOIN auth_user ON auth_user.id = user_tracker.user_id
            WHERE auth_user.username = %s"""
        sql_val = (user, )
        self.db_cursor.execute(sql, sql_val)
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


if __name__ == "__main__":
    uth = UserTrackingHandler()

    # uth.add(
    #     username='distance',
    #     method = 'distance',
    #     start_date='2020-01-01',       
    #     end_date = '2021-01-01',  
    #     stock1='AAPL',                  
    #     stock2='MSFT',                  
    #     window_size=200,                
    #     n_times=2,              
    # )
    
    
    # uth.remove(
    #     username='ian',
    #     method = 'distance',
    #     track_date = '',
    #     start_date='2020-01-01',       
    #     end_date = '2021-01-01',  
    #     stock1='AAPL',                  
    #     stock2='MSFT',                  
    #     window_size=200,                
    #     n_times=2,              
    # )
    
    
    # email = uth.get_user_email("distance")
    # print(email)


    # user_info = uth.get_all_user_info()   
    # print(user_info)
        
    # track_info = uth.get_all_track_params_combination_from_user('distance')
    # print(track_info)


    # all_info = uth.get_all_track_params_combination()
    # print(all_info)