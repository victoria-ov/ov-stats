import streamlit as st
import pandas as pd
import altair as alt
import AgGrid
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder

st.set_page_config(page_title="Open Vantage GitHub Metrics")

daily_commits = pd.read_csv('./Data/daily_commits.csv', sep=',')
today_commits = pd.read_csv('./Data/today_commits.csv', sep=',')

open_prs = pd.read_csv('./Data/open_prs.csv', sep=',')
closed_prs = pd.read_csv('./Data/closed_prs.csv', sep=',')


st.title("Open Vantage GitHub Metrics")

tab1, tab2, tab3, tab4 = st.tabs(["Commits", "Open Pull Requests", "Closed Pull Requests", "Other"])

with tab1:
   daily_commits['author.login'] = daily_commits['author.login'].replace('', pd.NA).fillna(daily_commits['author.name'])
   today_commits['author.login'] = today_commits['author.login'].replace('', pd.NA).fillna(today_commits['author.name'])

   # Create a chart -- Average number of commits for last 7 days
   day7_count = daily_commits.groupby(['author.login'])['sha'].count().reset_index(name="count")
   day7_count['count'] = round(day7_count['count'] / 7, 2)
   today_commits_count = today_commits.groupby(['author.login'])['sha'].count().reset_index(name="count")

   today_data = pd.DataFrame()
   today_data['Engineer'] = today_commits_count['author.login']
   today_data['Count'] = today_commits_count['count']

   weekly_data = pd.DataFrame()
   weekly_data['Engineer'] = day7_count['author.login']
   weekly_data['Count'] = day7_count['count']

   st.markdown("**Overview of commits per Engineer**")
   commits_merged = pd.merge(today_data, weekly_data, how="outer", on=["Engineer", "Engineer"])
   commits_merged.rename(columns={'Count_x': 'Last 24hrs'}, inplace=True)
   commits_merged.rename(columns={'Count_y': '7 day average'}, inplace=True)

   commits_merged = commits_merged.melt('Engineer', var_name='Interval', value_name='Number')

   c = alt.Chart(commits_merged).mark_bar().encode(
      alt.Row('Engineer', header=alt.Header(titleOrient='left', labelOrient='top')),
      alt.X('Number', axis=alt.Axis(grid=True)),
      alt.Y('Interval', axis=alt.Axis(title=None, labels=True)),
      alt.Color('Interval', legend=None)
   )
   st.altair_chart(c, use_container_width=True)

with tab2:
   # st.header("Open Pull Requests")
   st.markdown("**All Open Pull Requests**")
   open_prs_table = pd.DataFrame().assign(Repository=open_prs['head.repo.name'], Engineer=open_prs['user.login'],
                                          Reviewer=open_prs['requested_reviewers'], Created=open_prs['created_at'],
                                          Updated=open_prs['updated_at'], DaysOpen=open_prs['days-open'])

   gb = GridOptionsBuilder.from_dataframe(open_prs_table)
   gb.configure_pagination()
   gb.configure_side_bar()
   gb.configure_default_column(groupable=True, value=True, enableRowGroup=True)
   gridOptions = gb.build()
   AgGrid(open_prs_table, gridOptions=gridOptions)


   open_prs['days-open'] = pd.to_timedelta(open_prs['days-open'])
   open_prs['Time since created'] = open_prs['days-open'].dt.round(freq="D")
   open_prs_per_repo = open_prs.groupby(['head.repo.name'])['days-open'].mean().reset_index(name="count")
   open_prs_per_repo['count'] = open_prs_per_repo['count'].dt.days

   # # Streamlet starts here
   st.markdown("**Average open time of current open PRs per repository**")
   open_prs_per_repo_data = pd.DataFrame()
   open_prs_per_repo_data['Repository'] = open_prs_per_repo['head.repo.name']
   open_prs_per_repo_data['Number of days'] = open_prs_per_repo['count']
   # st.bar_chart(open_prs_per_repo_data, x='Repository', y='Number of days')

   open_prs_chart = alt.Chart(open_prs_per_repo_data).mark_bar().encode(
      # alt.Row('Engineer', header=alt.Header(titleOrient='left', labelOrient='bottom')),
      alt.X('Number of days', axis=alt.Axis(grid=True)),
      alt.Y('Repository', axis=alt.Axis(title=None, labels=True)),
      # alt.Color('Number of days', legend=None)
   )
   st.altair_chart(open_prs_chart, use_container_width=True)

   # Create a chart -- Open PRs per label assigned
   st.markdown("**Open PRs per label assigned**")
   open_prs_per_label = open_prs.groupby(['labels'])['labels'].count().reset_index(name="count")
   open_prs_per_label_data = pd.DataFrame()
   open_prs_per_label_data['Label'] = open_prs_per_label['labels']
   open_prs_per_label_data['Count'] = open_prs_per_label['count']
   # st.bar_chart(open_prs_per_label_data, x='Label', y='Count')
   open_prs_label_chart = alt.Chart(open_prs_per_label_data).mark_bar().encode(
      # alt.Row('Engineer', header=alt.Header(titleOrient='left', labelOrient='bottom')),
      alt.X('Count', axis=alt.Axis(grid=True, tickMinStep=1)),
      alt.Y('Label', axis=alt.Axis(title=None, labels=True)),
      # alt.Color('Number of days', legend=None)
   )
   st.altair_chart(open_prs_label_chart)

   # Create a chart -- Open PRs per label assigned
   st.markdown("**Open PRs per assigned reviewer**")
   open_prs_per_reviewer = open_prs.groupby(['requested_reviewers'])['requested_reviewers'].count().reset_index(name="count")
   open_prs_per_reviewer_data = pd.DataFrame()
   open_prs_per_reviewer_data['Reviewer'] = open_prs_per_reviewer['requested_reviewers']
   open_prs_per_reviewer_data['Number of PRs'] = open_prs_per_reviewer['count']
   # st.bar_chart(open_prs_per_reviewer_data, x='Reviewer', y='Number of PRs')
   open_prs_reviewer_chart = alt.Chart(open_prs_per_reviewer_data).mark_bar().encode(
      # alt.Row('Engineer', header=alt.Header(titleOrient='left', labelOrient='bottom')),
      alt.X('Number of PRs', axis=alt.Axis(grid=True, tickMinStep=1)),
      alt.Y('Reviewer', axis=alt.Axis(title=None, labels=True)),
      # alt.Color('Number of days', legend=None)
   )
   st.altair_chart(open_prs_reviewer_chart)

with tab3:
   # st.header("Closed Pull Requests")
   st.markdown("**Owl be here soon...**")

   st.image("https://static.streamlit.io/examples/owl.jpg", width=200)
