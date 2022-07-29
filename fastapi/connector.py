import psycopg2
from psycopg2.extras import RealDictCursor
import time
import os

def Make_Connection():
    no_connect=True
    while no_connect:
        try:
            conn=psycopg2.connect(
            host=os.environ['host'],
            password=os.environ['password'],
            user=os.environ['user'],
            port=5432,
            database=os.environ['dbname'],
            cursor_factory = RealDictCursor
            )   
            cursor = conn.cursor()
            no_connect=False
        except:
            print("connection is not made. Wait for some time")
            time.sleep(10)
    return conn,cursor

def close_connection(conn,cursor):
    conn.close()
    cursor.close()