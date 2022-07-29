import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sn
import requests
import os

host=os.environ['host'].strip()
port=os.environ['port']
@st.cache
def Total_Areas():
    areas=requests.get(f"http://{host}:{port}/Areas/Fetch_Areas").json()
    areas=["select the area"]+areas
    return areas

st.header("In this page we will get to know insights about the data based on area")


area=st.selectbox("select the area",options=Total_Areas())

c1=st.checkbox("check to see average visitors vs date given area")
if c1:
    if area!='select the area':
        data=requests.get(f"http://{host}:{port}/Areas/Fetch_Avg_Vistors_Area/",params={"area":area}).json()
        fig,ax=plt.subplots(figsize=(20,10))
        sn.lineplot(x=data['visit_date'],y=data['avg_visitors'])
        plt.xticks(list(range(0,len(data['visit_date']),10)))
        plt.xlabel("vist date")
        plt.ylabel("avg_vistors")
        plt.xticks(rotation=90)
        st.pyplot(fig)
    else:
        st.warning("please select the area")
else:
    st.empty()
c2=st.checkbox("check to see most served types of cuisines served in this area")
if c2:
    if area!='select the area':
        cus=requests.get(f"http://{host}:{port}/Areas/Fetch_N_Cuisine/",params={"area":area}).json()
        start_max_value=cus['start_max_value']
        end_min_value=cus['end_min_value']
        end_max_value=cus['end_max_value']
        start=st.number_input(label="enter start rank",min_value=1,max_value=start_max_value,value=1,step=1)
        end=st.number_input(label="enter end rank",min_value=end_min_value,max_value=end_max_value,value=end_min_value,step=1)
        if start>end:
            st.error("start should be less than or equal to end")
        else:
            data=requests.get(f"http://{host}:{port}/Areas/Fetch_Area_Most_Cuisines",params={"area":area,"start":int(start),"end":int(end)}).json()
            fig,ax=plt.subplots(figsize=(20,10))
            sn.countplot(x=data['genres'])
            plt.xticks(rotation=90)
            st.pyplot(fig)
    else:
        st.warning("please select the area")
else:
    st.empty()

c3=st.checkbox("check to see top restaurants in the area")
if c3:
    if area!='select the area':
        month=st.number_input(label="enter the month",min_value=1,max_value=12,value=1,step=1)
        cus=requests.get(f"http://{host}:{port}/Areas/Fetch_Restaurants_In_Area_Month",params={"area":area,"month":month}).json()
        start_max_value=cus['start_max_value']
        end_min_value=cus['end_min_value']
        end_max_value=cus['end_max_value']
        start=st.number_input(label="enter the start",min_value=1,max_value=start_max_value,value=1,step=1)
        end=st.number_input(label="enter the end",min_value=end_min_value,max_value=end_max_value,value=end_min_value,step=1)
        if start>end:
            st.error("start should be less than or equal to end")
        else:
            data=requests.get(f"http://{host}:{port}/Areas/Fetch_Top_Restaurants",params={"area":area,"month":month,"start":int(start),"end":int(end)}).json()
            fig,ax=plt.subplots(figsize=(20,10))
            sn.barplot(x=data['stores'],y=data['visitors'])
            plt.xticks(rotation=90)
            plt.xlabel("store ids")
            plt.ylabel("visitors")
            st.pyplot(fig)
    else:
        st.warning("please select the area")
else:
    st.empty()