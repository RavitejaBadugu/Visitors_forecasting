import requests
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sn
import os

host=os.environ['host'].strip()
port=os.environ['port']

st.header("In this page we get insights about the restaurants")
@st.cache
def Total_Restaurants():
    restaurant_ids=requests.get(f"http://{host}:{port}/Restaurants/Fetch_N_Res").json()
    data=["select"]+restaurant_ids
    return data
store_id=st.selectbox("Select the id of restaurant you want to know",Total_Restaurants())


with st.container():
    left,right=st.columns(2)
    with left:
        if store_id!="select":
            areas=requests.get(f"http://{host}:{port}/Restaurants/Fetch_Area_Info/{store_id}").json()
            st.markdown(f"This restaurant present at **{areas}**")
            
    with right:
        if store_id!="select":
            cuisines=requests.get(f"http://{host}:{port}/Restaurants/Fetch_Cuisine_Info/{store_id}").json()
            st.markdown(f"This restaurant serves: **{cuisines}**")


c1=st.checkbox("expand to see how is the distribution of gaps between reservation date and visit date is")
if c1:
    if store_id!="select":
        data=requests.get(f"http://{host}:{port}/Restaurants/Fetch_N_Days_Gap/{store_id}").json()
        if len(data)==0:
            st.info("reservations data for this restaurant is not present")
        else:
            fig,ax=plt.subplots()
            sn.histplot(data,bins=50)
            plt.xlabel("diff in reservations date to visiting date")
            plt.ylabel("freq")
            st.pyplot(fig)
    else:
        st.warning("Please select the restaurant")
else:
    st.empty()

c2=st.checkbox("expand to see how visitors are changing over the time for this restaurant")

if c2:
    if store_id!="select":
        data=requests.get(f"http://{host}:{port}/Restaurants/Fetch_Visitors/{store_id}").json()
        fig,ax=plt.subplots(figsize=(30,10))
        sn.lineplot(x=data['dates'],y=data['visitors'])
        plt.xlabel("dates")
        plt.ylabel("visitors")
        plt.xticks(list(range(0, len(data['dates']) + 1, 10)))
        plt.xticks(rotation=90)
        st.pyplot(fig)
    else:
        st.warning("Please select the restaurant")
else:
    st.empty()