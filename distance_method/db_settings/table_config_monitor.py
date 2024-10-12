import psycopg2
import json 
import os

with open ("/home/thomas/Desktop/distance_method/distance_method/config/correlation_db.json", 'r')as f:
    db_info = json.load(f)
    

# Connect to PostgreSQL server
db_conn = psycopg2.connect(
                            host = db_info['USER_DB_HOST'],
                            database = db_info['USER_DB_NAME'],
                            user = db_info['USER_DB_USER'],
                            password = db_info['USER_DB_PASSWORD'],
                            port = db_info['USER_DB_PORT'])
print("Connect successful!")
db_cursor = db_conn.cursor()
db_cursor.execute("""DROP TABLE IF EXISTS user_tracker;""")
db_cursor.execute("""CREATE TABLE user_tracker(
        id BIGSERIAL PRIMARY KEY,
        user_id INTEGER,
        method VARCHAR(20),
        stock1 VARCHAR(10) DEFAULT NULL,
        stock2 VARCHAR(10) DEFAULT NULL,
        start_date DATE DEFAULT NULL,
        end_date DATE DEFAULT NULL,
        window_size INTEGER DEFAULT NULL,
        n_times INTEGER DEFAULT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        FOREIGN KEY(user_id) REFERENCES auth_user(id) ON DELETE CASCADE
    );
    """)
print("CREATE TABLE 'user_tracker' successful")
db_conn.commit()
db_conn.close()
print("connect terminated")