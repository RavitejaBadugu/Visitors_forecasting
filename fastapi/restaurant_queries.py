from fastapi import APIRouter
from psycopg2 import sql
from connector import Make_Connection,close_connection
from base_models import Send_Visitors_Out

router=APIRouter()

def fetch_resturant_ids(cursor):
    q="select distinct(air_store_id) from main"
    cursor.execute(q)
    data=cursor.fetchall()
    data=[d['air_store_id'] for d in data]
    return data

def Fetch_n_days_gap(store_id,cursor):
    q=sql.SQL(
        '''
        select n_days_gap_mean
        from reservations
        where air_store_id={store_id}
        '''
        ).format(store_id=sql.Literal(store_id))
    cursor.execute(q)
    data=cursor.fetchall()
    data=[d['n_days_gap_mean'] for d in data] 
    return data


def Fetch_Area_info(store_id,cursor):
    q=sql.SQL('''
    select distinct(air_area_name)
    from geo
    where air_store_id={store_id}
    ''').format(store_id=sql.Literal(store_id))
    cursor.execute(q)
    data=cursor.fetchall()
    data=[d['air_area_name'] for d in data]
    return data

def Fetch_Cuisine_Info(store_id,cursor):
    q=sql.SQL('''
    select distinct(air_genre_name)
    from cuisine
    where air_store_id={store_id}
    ''').format(store_id=sql.Literal(store_id))
    cursor.execute(q)
    data=cursor.fetchall()
    data=[d['air_genre_name'] for d in data]
    return data

def Fetch_Visitors(store_id,cursor):
    q=sql.SQL('''
    select visitors,visit_date::date
    from main
    where air_store_id={store_id}
    ''').format(store_id=sql.Literal(store_id))
    cursor.execute(q)
    data=cursor.fetchall()
    data={"visitors":[d['visitors'] for d in data],
         "dates": [d['visit_date'] for d in data]}
    return data

@router.get("/Restaurants/Fetch_N_Res")
async def Send_N_Res():
    conn,cursor=Make_Connection()
    data=fetch_resturant_ids(cursor)
    close_connection(conn,cursor)
    return data

@router.get("/Restaurants/Fetch_Area_Info/{store_id}")
async def Send_Area_Info(store_id: str):
    conn,cursor=Make_Connection()
    areas=','.join(Fetch_Area_info(store_id,cursor))
    close_connection(conn,cursor)
    return areas

@router.get("/Restaurants/Fetch_Cuisine_Info/{store_id}")
async def Send_Fetch_Info(store_id: str):
    conn,cursor=Make_Connection()
    cuisines=','.join(Fetch_Cuisine_Info(store_id,cursor))
    close_connection(conn,cursor)
    return cuisines


@router.get("/Restaurants/Fetch_N_Days_Gap/{store_id}")
async def Send_N_Days_Gap(store_id: str):
    conn,cursor=Make_Connection()
    data=Fetch_n_days_gap(store_id,cursor)
    close_connection(conn,cursor)
    return data


@router.get("/Restaurants/Fetch_Visitors/{store_id}",response_model=Send_Visitors_Out)
async def Send_Visitors(store_id: str):
    conn,cursor=Make_Connection()
    data=Fetch_Visitors(store_id,cursor)
    close_connection(conn,cursor)
    return data