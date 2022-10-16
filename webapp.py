import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


title = "Closing The Chronically Homeless Housing Gap in Massachusetts"
st.title(title)

demographic_data = pd.read_excel("current_situation.xls")
gender_list = list(demographic_data.columns)[3:9]
hispanic_list = list(demographic_data.columns)[9:15]
white_list = list(demographic_data.columns)[15:]



st.header("Forecasting Model")
turnover_rate = st.slider(label="Turn over rate", min_value=0.0, max_value=1.0, value=0.2)
added_units = st.slider(label="Added Units per Year", min_value=300, max_value=3000, value=2573)
unit_effectiveness = st.slider(label="1 unit of housing reduces homelessness by", min_value=0.2, max_value=1.0, value=0.43)
cost_per_unit = st.text_input(label="Cost per Unit ($)", value=50000)

total_budget = float(cost_per_unit)*added_units


first_future_year = 2022

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

st.header('How many additional housing opportunities are needed to reach "Functional Zero" by 2030?')
# Main Outputs
col1, col2, col3 = st.columns(3)
col1.metric(label="Total Annual Budget",value=str(total_budget/1000000)+" $M")
col2.metric(label="New Added Units per year", value=str(added_units)+ " Units")
col3.metric(label="Unit Surplus/Deficit by 2026", value=str(int(chart1_data["delta"].values[-1]))+" Units")


# Supply and Demand
colors = px.colors.qualitative.Plotly
fig = go.Figure()
fig.add_traces(
    go.Scatter(x=chart1_data['year'], y = chart1_data['demand'], mode = 'lines', line=dict(color=colors[0]), name="People falling into CH")
)
fig.add_traces(
    go.Scatter(x=chart1_data['year'], y = chart1_data['number_of_beds_available'], mode = 'lines', line=dict(color=colors[1]), name="Housing Available for CH")
)
fig.add_traces(
    go.Bar(x=chart1_data['year'], y=chart1_data['delta'], name="Housing shortage/surplus")
)
fig.update_layout(
    title = {
        'text': "Housing for Chronic Homelessness (CH)",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'}
)
st.plotly_chart(fig, use_container_width=True)

# Shortage graph
remaining_homeless = (-1.0)*chart1_data['delta']

remaining_homeless[remaining_homeless < 0] = 0
fig2 = go.Figure()
fig2.add_traces(
    go.Scatter(x=chart1_data['year'], y = remaining_homeless, mode = 'lines', line=dict(color=colors[0]), name="Shortage")
)

fig2.update_layout(
    title = {
        'text': "Number of Chronically Homeless Individuals Without Permanent Housing",
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

st.header("Current Situation")
#Gender
gender_filter = st.multiselect("Select a demographic or multiple", gender_list)

figA = go.Figure()
color_id = 0
for demo in gender_filter:
    figA.add_traces(
        go.Bar(x=demographic_data["County"], y=demographic_data[demo], name=demo)
    )
    color_id+=1

figA.update_layout(
    title = {
        'text': "Demographics by Gender",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'}
)
st.plotly_chart(figA, use_container_width=True)

#hispanic
hispanic_filter = st.multiselect("Select a demographic or multiple", hispanic_list)

figB = go.Figure()
color_id = 0
for demo in hispanic_filter:
    figB.add_traces(
        go.Bar(x=demographic_data["County"], y=demographic_data[demo], name=demo)
    )
    color_id+=1

figB.update_layout(
    title = {
        'text': "Demographics Hispanic, Latino, Neither",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'}
)
st.plotly_chart(figB, use_container_width=True)

#white
white_filter = st.multiselect("Select a demographic or multiple", white_list)

figC = go.Figure()
color_id = 0
for demo in white_filter:
    figC.add_traces(
        go.Bar(x=demographic_data["County"], y=demographic_data[demo], name=demo)
    )
    color_id+=1

figC.update_layout(
    title = {
        'text': "Demographics White, African American, Neither",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'}
)
st.plotly_chart(figC, use_container_width=True)