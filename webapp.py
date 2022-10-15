import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


title = "Closing The Homeless Housing Gap in Massachusetts"
st.title(title)

turnover_rate = st.slider(label="Turn over rate", min_value=0.0, max_value=1.0, value=0.2)
added_units = st.slider(label="Added Units per Year", min_value=300, max_value=20000, value=1500)
first_future_year = 2021

# Read and process data
data = pd.read_excel("supply_data.xls")

# create new columns
data["turnover"] = data["number_of_beds_available"]
data["new_units"] = added_units

# update supply and turnover
for i in range(len(data)):
    year = data.iloc[i]["year"]
    if year >= first_future_year:
        data.iloc[i,3] = data.iloc[i-1]["number_of_beds_available"]*turnover_rate
        data.iloc[i,2] = data.iloc[i,3]+data.iloc[i,4]

# data for plotting
chart1_data = data.dropna()
chart1_data["number_of_beds_available"] = chart1_data["number_of_beds_available"].astype(float)
chart1_data["turnover"] = chart1_data["turnover"].astype(float)

chart1_data["delta"] = chart1_data["number_of_beds_available"]
for i in range(len(chart1_data)):
    chart1_data.iloc[i,5] = chart1_data.iloc[i,2] - chart1_data.iloc[i,1]

chart1_data["delta"] = chart1_data["delta"].astype(float)

st.write("Here")

# Express option
colors = px.colors.qualitative.Plotly
fig = go.Figure()
fig.add_traces(
    go.Scatter(x=chart1_data['year'], y = chart1_data['demand'], mode = 'lines', line=dict(color=colors[0]), name="Demand")
)
fig.add_traces(
    go.Scatter(x=chart1_data['year'], y = chart1_data['number_of_beds_available'], mode = 'lines', line=dict(color=colors[1]), name="Supply")
)
fig.add_traces(
    go.Bar(x=chart1_data['year'], y=chart1_data['delta'], name="Surplus")
)
fig.update_layout(
    title = {
        'text': "Housing Supply and Demand",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'}
)
st.plotly_chart(fig, use_container_width=True)
