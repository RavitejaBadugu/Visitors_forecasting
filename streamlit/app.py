import streamlit as st
import pandas as pd
import requests
import os

host=os.environ['host'].strip()
port=os.environ['port']


st.title("welcome")

data=requests.get(f"http://{host}:{port}/Fetch_Map")
coordinates=data.json()['cooridinates']
st.map(pd.DataFrame({"latitude":coordinates['latitude'],
                     "longitude":coordinates['longitude']}))
st.subheader("Dots in the plot represents the places where the restaurants in data are present")
st.write('''
   Through this demostration we can know where the restaurants are present and what they serve. Analysis based on area
   is done. Also we will be forecasting for 39 days for the restaurants. For which I used LSTM Model.
   Below I have shown you the performance of this model when submitted.
   left score is private score and right side is public score.
   The metric used by competition is RMSLE.
   ''')

st.image("Screenshot 2022-07-17 144459.png")