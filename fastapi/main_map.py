from fastapi import FastAPI
from connector import *
from base_models import MapModel
import  restaurant_queries
import area_quries
import holiday_quries
import forecaster


app=FastAPI()

app.include_router(restaurant_queries.router)
app.include_router(area_quries.router)
app.include_router(holiday_quries.router)
app.include_router(forecaster.router)

def Get_Map(cursor):
    q='''
    select latitude::float,longitude::float
    from geo
    '''
    cursor.execute(q)
    data=cursor.fetchall()
    return data

@app.get("/Fetch_Map",response_model=MapModel)
async def Send_Map():
    conn,cursor=Make_Connection()
    data=Get_Map(cursor)
    close_connection(conn,cursor)
    latitudes=[d['latitude'] for d in data]
    longitudes=[d['longitude'] for d in data]
    return {"cooridinates":{"latitude":latitudes,
                           "longitude":longitudes}}