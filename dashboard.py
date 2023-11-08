import requests
import json
import pandas as pd
import altair as alt
import streamlit as st
import plotly.express as px

from googleapiclient.discovery import build


api_key = 'AIzaSyB3mCA6t9TnPI-VK0N2K59bLH128hYfV5w'


spreadsheet_id = '1T8QXV9h01kUwzaTKTLoXWQzj6FeucM0zppR9wL_uzW4'
range_name = 'Sheet1'

# Build the Google Sheets API service
service = build('sheets', 'v4', developerKey=api_key)

# Use the API key to access data
result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
values = result.get('values', [])

if not values:
    print('No data found.')
else:
    for row in values:
        print(row)

range_name = 'Sheet1'

# Build the URL for the Google Sheets API
url = f'https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{range_name}?key={api_key}'

response = requests.get(url)
data = response.json()
values = data.get('values', [])
df=pd.DataFrame(values[1:],columns=values[0])
df['complaint_id'] = df['complaint_id'].astype(int)


st.set_page_config(
    page_title="Consumer Complaints Dashboard",
    page_icon="📊",
    layout="wide",
)


st.title("Consumer Complaints Dashboard")

container0 = st.container()

con = container0.columns([1,1])
container1 = st.container()

con_col1, con_col2, con_col3, con_col4, con_col5 = container1.columns(5)

with con_col5:
    selected_state = st.selectbox("Select State", ["All States"] + df['state'].unique().tolist())

    if selected_state == "All States":
        filtered_df = df
        subhead = f"Displaying Data for {selected_state}"
    else:
        filtered_df = df[df['state'] == selected_state]
        subhead = f"Display Data for {selected_state}"

with con[0]:
    st.subheader(subhead)

with con_col1:
    st.metric("Total Number of Complaints", filtered_df['complaint_id'].sum())
  

with con_col2:

    complaints_with_closed = filtered_df[filtered_df['company_response'].str.contains("Closed")]
    total_closed_complaints = complaints_with_closed['complaint_id'].sum()
    st.metric("Total Number of Complaints with Closed Status", total_closed_complaints)
 
with con_col3:
    timely_ratio=filtered_df[filtered_df['timely'] =='Yes']['complaint_id'].sum()/filtered_df['complaint_id'].sum()
    st.metric("% of Timely Responded Complaints",f"{timely_ratio:.2%}")

with con_col4:
    st.metric("Total Number of Complaints with In Progress Status",filtered_df[filtered_df['company_response'] =='In progress']['complaint_id'].sum())

container2=st.container()
chart1, chart2 = container2.columns(2)
chart_data = filtered_df.groupby('product')['complaint_id'].sum().reset_index()
chart = alt.Chart(chart_data).mark_bar().encode(
    x='complaint_id:Q',
    y=alt.Y('product:N', sort='-x'),
    color='product:N',
).properties(
    title="Complaints by Product",
    width=300
)

chart1.altair_chart(chart, use_container_width=True)

chart_data=filtered_df.groupby('month_year')['complaint_id'].sum().reset_index().sort_values(by='month_year')
line_chart = alt.Chart(chart_data).mark_line().encode(
    x=alt.X('month_year:O'),
    y=alt.Y('complaint_id:Q'),
    tooltip=['month_year:O', 'complaint_id:Q'],
).properties(
    title='Complaints By Month_year',
    width=400
)
chart2.altair_chart(line_chart, use_container_width=True)


container3=st.container()
chart3, chart4 = container3.columns(2)
chart_data = filtered_df.groupby('submitted_via')['complaint_id'].sum().reset_index()
pie_chart = alt.Chart(chart_data).mark_arc().encode(
    color='submitted_via:N',
    angle=alt.X('complaint_id:Q', title='Complaints'),
    tooltip=['submitted_via:N', 'complaint_id:Q'],
).properties(
    title='Complaints by Submission Method',
    width=400
)

chart3.altair_chart(pie_chart, use_container_width=True)


treemap_data = filtered_df.groupby(['issue','sub_issue'])['complaint_id'].sum().reset_index()
treemap = px.treemap(treemap_data, path=['issue', 'sub_issue'], values='complaint_id', title='Complaints by Issue and Sub-Issue')
treemap.update_layout(
    title='Complaints by Issue and Sub-Issue'
    )
treemap.update_traces(hovertemplate='Number of complaints: %{value}')
treemap.update_traces(textinfo="label+value")
chart4.plotly_chart(treemap,use_container_width=True, )

st.markdown("By Afifah Luqman")
