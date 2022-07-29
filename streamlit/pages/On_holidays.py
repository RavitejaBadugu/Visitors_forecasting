import requests
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sn
import pandas as pd
import plotly_express as px
import requests
import os
host=os.environ['host'].strip()
port=os.environ['port']
st.header("In this page we will get to know insights about the data based on holidays")

@st.cache
def Total_Areas():
    areas=requests.get(f"http://{host}:{port}/Areas/Fetch_Areas").json()
    areas=["select the area"]+areas
    return areas
    
area=st.selectbox("select the area",options=Total_Areas())

c1=st.checkbox("see which areas are more busy")

if c1:
    holiday_flg=st.radio("select 1 to see on holidays",options=[0,1],index=0)
    data=requests.get(f"http://{host}:{port}/holidays/Fetch_Busy_Areas"
                        ,params={"holiday_flg":holiday_flg}).json()
    df=pd.DataFrame(data)
    fig = px.scatter_mapbox(df, lat='latitude', lon='longitude', color='visitors', zoom=4,
                        mapbox_style="carto-positron")
    st.plotly_chart(fig)
else:
    st.empty()

c2=st.checkbox("which type of food are mostly eaten on holidays vs non-holidays")
if c2:
    if area!='select the area':
        cus=requests.get(f"http://{host}:{port}/holidays/Fetch_Cuisines_In_Area"
                        ,params={"area":area}).json()
        start_max_value=cus['start_max_value']
        end_min_value=cus['end_min_value']
        end_max_value=cus['end_max_value']
        start=st.number_input(label="enter start rank",min_value=1,max_value=start_max_value,value=1,step=1)
        end=st.number_input(label="enter end rank",min_value=end_min_value,max_value=end_max_value,value=end_min_value,step=1)
        if start>end:
            st.error("start should be less than or equal to end")
        else:
            data=requests.get(f"http://{host}:{port}/holidays/Fetch_Available_Cuisines"
                        ,params={"area":area,"start":int(start),"end":int(end)}).json()
            fig,ax=plt.subplots(figsize=(20,10))
            sn.countplot(x=data['genres'],hue=data['holiday_flg'])
            plt.xticks(rotation=90)
            plt.xlabel("types of servings")
            plt.ylabel("count")
            st.pyplot(fig)
    else:
        st.warning("please select the area")
else:
    st.empty()

c3=st.checkbox("expand to check how visitors changing for restaurant by holidays and non-holidays")
if c3:
    if area!='select the area':
        res=requests.get(f"http://{host}:{port}/holidays/Fetch_Restaurants_In_Area"
                        ,params={"area":area}).json()
        start_max_value=res['start_max_value']
        end_min_value=res['end_min_value']
        end_max_value=res['end_max_value']
        start=st.number_input(label="enter the start",min_value=1,max_value=start_max_value,value=1,step=1)
        end=st.number_input(label="enter the end",min_value=end_min_value,max_value=end_max_value,value=end_min_value,step=1)
        if start>end:
            st.error("start should be less than or equal to end")
        else:
            data=requests.get(f"http://{host}:{port}/holidays/Fetch_Top_Restaurants"
                        ,params={"area":area,"start":int(start),"end":int(end)}).json()
            fig,ax=plt.subplots(figsize=(20,10))
            sn.barplot(x=data['stores'],y=data['visitors'],hue=data['holiday_flg'])
            plt.xticks(rotation=90)
            plt.xlabel("restaurants")
            plt.ylabel("visitors")
            st.pyplot(fig)
    else:
        st.warning("please select the area")
else:
    st.empty()