import streamlit as st
import requests
import matplotlib.pyplot as plt 
import seaborn as sn
import os

host=os.environ['host'].strip()
port=os.environ['port']
st.header("Please select the store_id for which we will forecast 39 days.")
@st.cache
def get_stores():
    stores=requests.get(f"http://{host}:{port}/forecast").json()
    return stores['air_store_id']
    
stores=get_stores()
store_id=st.selectbox("select the store_id",["select the store_id"]+stores)

if store_id!="select the store_id":
    data=requests.get(f"http://{host}:{port}/forecast/{store_id}").json()
    fig,ax=plt.subplots(figsize=(30,15))
    sn.lineplot(data['visit_date'],data['visitors'],hue=data['indicator'])
    plt.xlabel("dates")
    plt.ylabel("visitors")
    plt.xticks(rotation=90)
    plt.xticks(data['visit_date'][0::10])
    st.pyplot(fig)
else:
    st.warning("Please select the store_id from box")
    

