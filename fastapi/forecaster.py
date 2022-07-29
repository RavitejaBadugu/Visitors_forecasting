from psycopg2 import sql
from connector import Make_Connection,close_connection
from fastapi import APIRouter

router=APIRouter()



@router.get("/forecast")
async def get_stores():
    conn,cursor=Make_Connection()
    query=sql.SQL('''
        select distinct air_store_id
        from predictions
          ''')
    
    cursor.execute(query)
    data=cursor.fetchall()
    data={"air_store_id":list(d['air_store_id'] for d in data)}
    close_connection(conn,cursor)
    return data

@router.get("/forecast/{store_id}")
async def forecast(store_id: str):
    conn,cursor=Make_Connection()
    query=sql.SQL('''
        with t1_cte as (
            select visit_date::date,visitors,1 as indicator
            from predictions
            where air_store_id={store_id}
        ),t2_cte as (
            select visit_date::date,visitors::decimal,0 as indicator
            from main
            where air_store_id={store_id}
        )
        select *
        from t2_cte
        union
        select *
        from t1_cte
        order by visit_date asc
          ''').format(store_id=sql.Placeholder())
    cursor.execute(query,(store_id,store_id))
    data=cursor.fetchall()
    data={"visit_date":list(d['visit_date'] for d in data),
         "visitors":list(d['visitors'] for d in data),
         "indicator":list(d['indicator'] for d in data)}
    close_connection(conn,cursor)
    return data