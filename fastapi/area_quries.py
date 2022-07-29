from fastapi import APIRouter
from psycopg2 import sql
from connector import Make_Connection,close_connection
from base_models import Send_Avg_Visitors_Out,Send_Limits,Common_Cuisines_Out_Area,Top_Res_Out


router=APIRouter()

def Fetch_areas(cursor):
    q='''
        select distinct(air_area_name)
        from geo
    '''
    cursor.execute(q)
    data=cursor.fetchall()
    data=[d['air_area_name'] for d in data]
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

def Fetch_Res_In_Area_Month(area_name,month,cursor):
    q=sql.SQL('''
    select count(distinct(air_store_id)) as counter
    from
    (
        select a.air_store_id,b.air_area_name,extract(month from a.visit_date ) as visit_month
        from main a
        inner join geo b
        on a.air_store_id=b.air_store_id
    ) c
    where air_area_name= {area_name} and visit_month= {month}
    '''
    ).format(area_name=sql.Literal(area_name),month=sql.Literal(month))
    cursor.execute(q)
    data=cursor.fetchall()
    return data[0]['counter']


def Fetch_AVG_Visitors_Area(area,cursor):
    q=sql.SQL(
        '''with t_cte as 
            (
                select a.visitors,a.visit_date
                from main a
                inner join (select air_store_id from geo where air_area_name={area}) b
                on a.air_store_id=b.air_store_id
            )
            select visit_date,avg(visitors) as avg_visitors
            from t_cte
            group by visit_date
    '''
    ).format(area=sql.Literal(area))

    cursor.execute(q)
    data=cursor.fetchall()
    data={"visit_date": [d['visit_date'] for d in data],
          "avg_visitors": [d['avg_visitors'] for d in data]}
    return data

def Fetch_Area_Most_Cuisines(area,start,end,cursor):
    q=sql.SQL('''
    with f_cte as
    (
        select a.air_genre_name
        from cuisine a
        inner join (select air_store_id from geo where air_area_name={area}) b
        on a.air_store_id=b.air_store_id
    ),ranking_cte as
    (
        select air_genre_name,row_number() over(order by count(*) desc) as ranking
        from f_cte
        group by air_genre_name
    )
    select a.air_genre_name 
    from f_cte a
    inner join (select air_genre_name,ranking
                             from ranking_cte
                             where ranking between {start} and {end}) b
    on a.air_genre_name=b.air_genre_name
    order by b.ranking asc
    ''').format(area=sql.Literal(area),start=sql.Literal(start),end=sql.Literal(end))
    cursor.execute(q)
    data=cursor.fetchall()
    data={"genres": [d['air_genre_name'] for d in data]}
    return data

def Fetch_Top_Res(area,month,start,end,cursor):
    q=sql.SQL('''
    with t_cte as
    (
    select a.air_store_id,a.visitors
    from (select air_store_id,
                visitors
          from main
          where extract(month from visit_date) ={month}
          ) a
    inner join (select air_store_id from geo
                where air_area_name={area}
                ) b
    on a.air_store_id = b.air_store_id
    ),ranking_cte as
    (
        select air_store_id,row_number() over(order by avg(visitors) desc) as ranking
        from t_cte
        group by air_store_id
    )
    select a.air_store_id,a.visitors
    from t_cte a
    inner join ranking_cte b
    on a.air_store_id=b.air_store_id
    where b.ranking between {start} and {end}
    order by b.ranking asc  

    ''').format(area=sql.Literal(area),month=sql.Literal(month),
                start=sql.Literal(start),end=sql.Literal(end))
    cursor.execute(q)
    data=cursor.fetchall()
    data={"stores": [d['air_store_id'] for d in data],
          "visitors": [d['visitors'] for d in data]}
    return data


@router.get("/Areas/Fetch_Areas")
async def Send_Areas():
    conn,cursor=Make_Connection()
    areas=Fetch_areas(cursor)
    close_connection(conn,cursor)
    return areas


@router.get("/Areas/Fetch_Avg_Vistors_Area",response_model=Send_Avg_Visitors_Out)
async def Send_Visit_Area(area: str):
    conn,cursor=Make_Connection()
    data=Fetch_AVG_Visitors_Area(area,cursor)
    close_connection(conn,cursor)
    return data


@router.get("/Areas/Fetch_N_Cuisine",response_model=Send_Limits)
async def Send_N_Cuisine(area: str):
    conn,cursor=Make_Connection()
    cus=Fetch_Cuisine_In_Area(area,cursor)
    close_connection(conn,cursor)
    start_max_value=cus-5 if cus-5>0 else cus
    end_min_value=5 if cus>5 else cus
    return {"start_max_value":start_max_value,
             "end_min_value":end_min_value,
             'end_max_value':cus}

@router.get("/Areas/Fetch_Area_Most_Cuisines",response_model=Common_Cuisines_Out_Area)
async def Send_Area_Most_Cuisines(area: str,start: int,end: int):
    conn,cursor=Make_Connection()            
    data=Fetch_Area_Most_Cuisines(area,start,end,cursor)
    close_connection(conn,cursor)
    return data


@router.get("/Areas/Fetch_Restaurants_In_Area_Month",response_model=Send_Limits)
async def Send_Res_In_Area_Month(area: str,month: int):
    print(month)
    conn,cursor=Make_Connection()
    res=Fetch_Res_In_Area_Month(area,month,cursor)
    close_connection(conn,cursor)
    start_max_value=res-5 if res-5>0 else res
    end_min_value=5 if res>5 else res
    return {"start_max_value":start_max_value,
             "end_min_value":end_min_value,
             'end_max_value':res}
    
@router.get("/Areas/Fetch_Top_Restaurants",response_model=Top_Res_Out)
async def Send_Top_Restaurants(area: str,month: int,start: int,end: int):
    conn,cursor=Make_Connection()
    data=Fetch_Top_Res(area,month,start,end,cursor)
    close_connection(conn,cursor)
    return data