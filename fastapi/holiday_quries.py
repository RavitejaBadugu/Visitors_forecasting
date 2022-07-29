from psycopg2 import sql
from connector import Make_Connection,close_connection
from fastapi import APIRouter
from base_models import Send_Limits,Common_Cuisines_Holidays,Top_Res_Holidays


router=APIRouter()


def Make_View(conn,cursor):
    q=sql.SQL(
        '''
        create or replace view  base_table as
        select a.air_store_id,a.visit_date,a.visitors,b.holiday_flg
        from main a
        inner join dates_info b
        on a.visit_date=b.calendar_date
        '''
    )
    cursor.execute(q)
    conn.commit()

def Fetch_areas(cursor):
    q='''
        select distinct(air_area_name) as areas
        from geo
    '''
    cursor.execute(q)
    data=cursor.fetchall()
    data=[d['areas'] for d in data]
    return data

def Fetch_Res_In_Area(area_name,cursor):
    q=sql.SQL('''
    select count(distinct(air_store_id)) as counter
    from
    (
        select a.air_store_id,b.air_area_name
        from main a
        inner join geo b
        on a.air_store_id=b.air_store_id
    ) c
    where air_area_name= {area_name}
    '''
    ).format(area_name=sql.Literal(area_name))
    cursor.execute(q)
    data=cursor.fetchall()
    return data[0]['counter']

def Fetch_Cuisine_In_Area(area_name,cursor):
    q=sql.SQL('''
    select count(distinct(air_genre_name)) as counter
    from
    (
        select b.air_genre_name,a.air_area_name
        from geo a
        inner join cuisine b
        on a.air_store_id=b.air_store_id
    ) c
    where air_area_name= {area_name}
    '''
    ).format(area_name=sql.Literal(area_name))
    cursor.execute(q)
    data=cursor.fetchall()
    return data[0]['counter']

def Fetch_Busy_Area_Holi(holiday_flg,cursor):
    q=sql.SQL('''
    with f_cte as
    (
    select a.visitors,a.holiday_flg,b.air_area_name,b.latitude,b.longitude
    from base_table a
    inner join geo b
    on a.air_store_id=b.air_store_id
    )
    select air_area_name,latitude,longitude,visitors from f_cte
    where holiday_flg={holiday_flg}
    ''').format(holiday_flg=sql.Literal(holiday_flg))
    cursor.execute(q)
    data=cursor.fetchall()
    data={"areas": [d['air_area_name'] for d in data],
          "latitude":[d['latitude'] for d in data],
          "longitude":[d['longitude'] for d in data],
          "visitors":[d['visitors'] for d in data]
          }
    return data

def Fetch_Ava_Cuisine_Holi(area,start,end,cursor):
    q=sql.SQL('''
    with f_cte as
    (
    select a.holiday_flg,a.air_store_id
    from base_table a
    inner join (select air_store_id from geo where air_area_name={area}) b
    on a.air_store_id=b.air_store_id
    ),ranking_cte as
    (
        select b.air_genre_name,row_number() over(order by count(*) desc) as ranking
        from f_cte a
        left join cuisine b
        on a.air_store_id=b.air_store_id
        group by b.air_genre_name
    ),final_cte as
    (
    select b.air_genre_name,a.holiday_flg
    from f_cte a
    inner join cuisine b
    on a.air_store_id=b.air_store_id
    )
    select a.air_genre_name,a.holiday_flg
    from final_cte a
    inner join ranking_cte b
    on a.air_genre_name = b.air_genre_name
    where b.ranking between {start} and {end}
    order by b.ranking asc
    ''').format(area=sql.Literal(area),
                start=sql.Literal(start),end=sql.Literal(end))
    cursor.execute(q)
    data=cursor.fetchall()
    data={"genres": [d['air_genre_name'] for d in data],
         "holiday_flg":[d['holiday_flg'] for d in data]}
    return data

def Fetch_Top_Res_Holi(area,start,end,cursor):
    q=sql.SQL('''
    with f_cte as
    (
    select a.visitors,a.holiday_flg,a.air_store_id
    from base_table a
    inner join (select air_store_id from geo where air_area_name={area}) b
    on a.air_store_id=b.air_store_id
    )
    select a.air_store_id,a.visitors,a.holiday_flg
    from f_cte a
    inner join (
        select air_store_id,row_number() over(order by avg(visitors) desc) as ranking
        from f_cte
        group by air_store_id
    ) b
    on a.air_store_id=b.air_store_id
    where b.ranking between {start} and {end}
    order by b.ranking asc
    ''').format(area=sql.Literal(area),
                start=sql.Literal(start),end=sql.Literal(end))
    cursor.execute(q)
    data=cursor.fetchall()
    data={"stores": [d['air_store_id'] for d in data],
          "visitors": [d['visitors'] for d in data],
          "holiday_flg":[d['holiday_flg'] for d in data]}
    return data


@router.get("/holidays/Fetch_Areas")
async def Send_Areas():
    conn,cursor=Make_Connection()
    areas=Fetch_areas(cursor)
    close_connection(conn,cursor)
    return areas


@router.get("/holidays/Fetch_Busy_Areas")
async def Send_Busy_Areas(holiday_flg: int):
    conn,cursor=Make_Connection()
    Make_View(conn,cursor)
    data=Fetch_Busy_Area_Holi(holiday_flg,cursor)
    close_connection(conn,cursor)
    return data


@router.get("/holidays/Fetch_Cuisines_In_Area",response_model=Send_Limits)
async def Send_N_Cuisines_In_Area(area: str):
    conn,cursor=Make_Connection()
    cus=Fetch_Cuisine_In_Area(area,cursor)
    close_connection(conn,cursor)
    start_max_value=cus-5 if cus-5>0 else cus
    end_min_value=5 if cus>5 else cus
    return {"start_max_value":start_max_value,
             "end_min_value":end_min_value,
             'end_max_value':cus}

@router.get("/holidays/Fetch_Available_Cuisines",response_model=Common_Cuisines_Holidays)
async def Send_Available_Cuisines(area: str,start: int,end: int):
    conn,cursor=Make_Connection()
    Make_View(conn,cursor)
    data=Fetch_Ava_Cuisine_Holi(area,start,end,cursor)
    close_connection(conn,cursor)
    return data


@router.get("/holidays/Fetch_Restaurants_In_Area",response_model=Send_Limits)
async def Send_Restaurants_In_Area(area: str):
    conn,cursor=Make_Connection()
    res=Fetch_Res_In_Area(area,cursor)
    close_connection(conn,cursor)
    start_max_value=res-5 if res-5>0 else res
    end_min_value=5 if res>5 else res
    return {"start_max_value":start_max_value,
             "end_min_value":end_min_value,
             'end_max_value':res}

@router.get("/holidays/Fetch_Top_Restaurants",response_model=Top_Res_Holidays)
async def Send_Top_Restaurants(area: str,start: int,end: int):
    conn,cursor=Make_Connection()
    Make_View(conn,cursor)
    data=Fetch_Top_Res_Holi(area,start,end,cursor)
    close_connection(conn,cursor)
    return data