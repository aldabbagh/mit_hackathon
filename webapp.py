import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


title = "Closing The Chronically Homeless Housing Gap in Massachusetts"
st.title(title)

st.header("Model Inputs")
turnover_rate = st.slider(label="Turn over rate", min_value=0.0, max_value=1.0, value=0.2)
added_units = st.slider(label="Added Units per Year", min_value=300, max_value=20000, value=1500)
unit_effectiveness = st.slider(label="Unit Effectiveness", min_value=0.2, max_value=1.0, value=0.43)
cost_per_unit = st.text_input(label="Cost per Unit ($)")

st.header("Model Outputs")
st.caption("Total budget ($)")
total_budget = float(cost_per_unit)*added_units
st.write(total_budget)

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
    chart1_data.iloc[i,5] = unit_effectiveness*chart1_data.iloc[i,2] - chart1_data.iloc[i,1]

chart1_data["delta"] = chart1_data["delta"].astype(float)



# Supply and Demand
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

# Shortage graph
fig2 = go.Figure()
fig2.add_traces(
    go.Scatter(x=chart1_data['year'], y = chart1_data['delta'], mode = 'lines', line=dict(color=colors[0]), name="Shortage")
)

fig2.update_layout(
    title = {
        'text': "Number of Chronically Homeless Individuals Without A Bed",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'}
)
st.plotly_chart(fig2, use_container_width=True)


county_share = pd.read_csv("county_demand_share.csv")
county_dict = dict(zip(county_share.County, county_share.share))
counties = list(county_share.County.values)

county_filter = st.multiselect("Select a County or Multiple Counties", counties)

#County demand
fig3 = go.Figure()
color_id = 0
for county in county_filter:
    fig3.add_traces(
        go.Scatter(x=chart1_data['year'], y = chart1_data['demand']*county_dict[county], mode = 'lines', line=dict(color=colors[color_id]), name=county)
    )
    color_id+=1

fig3.update_layout(
    title = {
        'text': "Demand By County",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'}
)
st.plotly_chart(fig3, use_container_width=True)