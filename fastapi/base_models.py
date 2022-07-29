from pydantic import BaseModel
from typing import List,Dict
from datetime import date

class MapModel(BaseModel):
    cooridinates: Dict[str,List[float]]

class Send_Visitors_Out(BaseModel):
    visitors: List[int]
    dates: List[date]

class Send_Avg_Visitors_Out(BaseModel):
    avg_visitors: List[float]
    visit_date: List[date]

class Send_Limits(BaseModel):
    end_min_value: int
    start_max_value: int
    end_max_value: int

class Common_Cuisines_Out_Area(BaseModel):
    genres: List[str]

class Top_Res_Out(BaseModel):
    stores: List[str]
    visitors: List[int]

class Busy_Areas_Holidays(BaseModel):
    areas: List[str]
    latitude: List[float]
    longitude: List[float]
    visitors: List[int]

class Common_Cuisines_Holidays(BaseModel):
    genres: List[str]
    holiday_flg: List[int]

class Top_Res_Holidays(Top_Res_Out):
    holiday_flg: List[int]