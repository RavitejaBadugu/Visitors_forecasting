import os
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from get_data_from_s3 import create_new_tables
import time
from tqdm import tqdm
import pandas as pd
import numpy as np


no_connect=True
while no_connect:
    try:
        conn=psycopg2.connect(
            host=os.environ['host'].strip(),
            password=os.environ['password'].strip(),
            user=os.environ['user'].strip(),
            port=5432,
            database=os.environ['dbname'].strip(),
            cursor_factory = RealDictCursor
        )
        cursor = conn.cursor()
        no_connect=False
    except:
        print("connection is not made. Wait for some time")
        time.sleep(10)

def CREATE_TABLES():
    query='''
          CREATE TABLE IF NOT EXISTS MAIN (
            air_store_id varchar(20) not null,
            visit_date date not null,
            visitors int CHECK( visitors >= 0),
            PRIMARY KEY(air_store_id,visit_date)
          );
          '''
    cursor.execute(query)
    query='''
          CREATE TABLE IF NOT EXISTS RESERVATIONS (
            air_store_id varchar(20) not null,
            visit_date date not null,
            reserve_visitors_mean decimal,
            n_hrs_gap_mean decimal,
            n_days_gap_mean decimal,
            PRIMARY KEY(air_store_id,visit_date)
          );
          '''
      #FOREIGN KEY (air_store_id,visit_date) REFERENCES MAIN (air_store_id,visit_date)
      #we can't have the foreign key because in reservations we have other days combination with restaurant which are not in main table.

    cursor.execute(query)

    query='''
          CREATE TABLE IF NOT EXISTS CUISINE (
            ID serial PRIMARY KEY,
            air_store_id varchar(20) not null,
            air_genre_name varchar(50) not null
          );
          '''
    cursor.execute(query)
    query='''
          CREATE TABLE IF NOT EXISTS GEO (
            ID serial PRIMARY KEY,
            air_store_id varchar(20) not null,
            air_area_name varchar(100) not null,
            latitude decimal not null,
            longitude decimal not null
          );
          '''
    cursor.execute(query)
    query='''
          CREATE TABLE IF NOT EXISTS DATES_INFO (
            calendar_date date PRIMARY KEY,
            day_of_week varchar(10) not null,
            holiday_flg int not null
          );
          '''
    cursor.execute(query)
    query='''
      CREATE TABLE PREDICTIONS(
        id varchar(50) PRIMARY KEY,
        air_store_id varchar(20) not null,
        visit_date date not null,
        visitors decimal not null
      )
        '''
    cursor.execute(query)
    conn.commit()

def Insert_To_Table(sections):
  for section in sections:
    path,name=section
    for chunck in tqdm(pd.read_csv(path,chunksize=10_000)):
      columns=chunck.columns.tolist()
      tuples = [tuple(x) for x in chunck.to_numpy()]
      query=sql.SQL('''
         INSERT INTO {table} ({columns})
         VALUES
         ({values})
         ''').format(table= sql.Identifier(name),
                     columns= sql.SQL(",").join([sql.Identifier(col) for col in columns]),
                     values=sql.SQL(",").join(sql.Placeholder()*len(columns)))
      cursor.executemany(query,tuples)
    conn.commit()

def insert_predictions(dataframe):
  columns=dataframe.columns.tolist()
  query=sql.SQL('''
  INSERT INTO {table} ({columns})
  VALUES
  ({values})
      ''').format(table=sql.Identifier("predictions"),
                  columns=sql.SQL(",").join([sql.Identifier(col) for col in columns]),
                  values=sql.SQL(",").join(sql.Placeholder()*len(columns)))
  BATCH_SIZE=10_000
  total=dataframe.shape[0]
  n_iters=int(np.ceil(BATCH_SIZE/total))
  for batch in range(n_iters):
    start=batch*BATCH_SIZE
    end=(batch+1)*BATCH_SIZE
    if end>total:
      end=total
    temp=dataframe.iloc[start:end].reset_index(drop=True)
    tuples=list(tuple(x) for x in temp.to_numpy())
    cursor.executemany(query,tuples)
  conn.commit()



if __name__=='__main__':
    create_new_tables()
    CREATE_TABLES()
    Insert_To_Table([('air_visit_data.csv',"main"),('reservations.csv','reservations'),
                      ('cuisine.csv','cuisine'),('date_info.csv','dates_info')
                      ,('geo.csv','geo')])