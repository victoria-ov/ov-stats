import streamlit as st
import pandas as pd
import datetime
# from streamlit_extras.dataframe_explorer import dataframe_explorer

# import numpy as np
# import plotly.express as px
# from plotly.subplots import make_subplots
# import plotly.graph_objects as go
# import matplotlib.pyplot as plt

daily_commits = pd.read_csv('daily_commits.csv', sep=',')
today_commits = pd.read_csv('today_commits.csv', sep=',')

open_prs = pd.read_csv('open_prs.csv', sep=',')
closed_prs = pd.read_csv('closed_prs.csv', sep=',')


st.title("Open Vantage GitHub Metrics")

tab1, tab2, tab3 = st.tabs(["Commits", "Open Pull Requests", "Closed Pull Requests"])

with tab1:
   daily_commits['author.login'] = daily_commits['author.login'].replace('', pd.NA).fillna(daily_commits['author.name'])
   today_commits['author.login'] = today_commits['author.login'].replace('', pd.NA).fillna(today_commits['author.name'])

   # Create a chart -- Average number of commits for last 7 days
   day7_count = daily_commits.groupby(['author.login'])['sha'].count().reset_index(name="count")
   day7_count['count'] = round(day7_count['count'] / 7, 2)
   today_commits_count = today_commits.groupby(['author.login'])['sha'].count().reset_index(name="count")

   # Streamlet starts here
   st.header("Commits")
   st.markdown("Commits for the last 24 hours")
   today_data = pd.DataFrame()
   today_data['Engineer'] = today_commits_count['author.login']
   today_data['Count'] = today_commits_count['count']
   st.bar_chart(today_data, x='Engineer', y='Count')
   # st.dataframe(chart_data, use_container_width=True)

   st.markdown("Average number of commits per day for last 7 days")
   weekly_data = pd.DataFrame()
   weekly_data['Engineer'] = day7_count['author.login']
   weekly_data['Count'] = day7_count['count']
   st.bar_chart(weekly_data, x='Engineer', y='Count')
   # st.dataframe(chart_data, use_container_width=True)

with tab2:
   st.header("Open Pull Requests")
   open_prs_table = pd.DataFrame().assign(Repository=open_prs['head.repo.name'], Engineer=open_prs['user.login'],
                                          Reviewer=open_prs['requested_reviewers'], Created=open_prs['created_at'],
                                          Updated=open_prs['updated_at'], DaysOpen=open_prs['days-open'])

   st.dataframe(open_prs_table, width=None)

   # filtered_df = dataframe_explorer(open_prs_table)
   # st.dataframe(filtered_df, use_container_width=True)

   open_prs['days-open'] = pd.to_timedelta(open_prs['days-open'])

   open_prs['Time since created'] = open_prs['days-open'].dt.round(freq="D")
   open_prs_per_repo = open_prs.groupby(['head.repo.name'])['days-open'].mean().reset_index(name="count")

   open_prs_per_repo['count'] = open_prs_per_repo['count'].dt.days

   # # Streamlet starts here
   st.markdown("Average open time of current open PRs per repository")
   open_prs_per_repo_data = pd.DataFrame()
   open_prs_per_repo_data['Repository'] = open_prs_per_repo['head.repo.name']
   open_prs_per_repo_data['Number of days'] = open_prs_per_repo['count']
   st.bar_chart(open_prs_per_repo_data, x='Repository', y='Number of days')
   # st.dataframe(open_prs_per_repo_data, use_container_width=True)

   # Create a chart -- Open PRs per label assigned
   st.markdown("Open PRs per label assigned")
   open_prs_per_label = open_prs.groupby(['labels'])['labels'].count().reset_index(name="count")
   open_prs_per_label_data = pd.DataFrame()
   open_prs_per_label_data['Label'] = open_prs_per_label['labels']
   open_prs_per_label_data['Count'] = open_prs_per_label['count']
   st.bar_chart(open_prs_per_label_data, x='Label', y='Count')

with tab3:
   st.header("Closed Pull Requests")
   st.markdown("Owl be here soon...")

   st.image("https://static.streamlit.io/examples/owl.jpg", width=200)
