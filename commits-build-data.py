import os
import pandas as pd
# import numpy as np
import datetime

# Setup GitHub API (GhApi)
token = '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'
from ghapi.all import GhApi
api = GhApi(owner='openvantage', token=token)

# Specify columns of interest
cols = ['sha', 'commit.author.name', 'commit.author.email', 'commit.author.date', 'commit.committer.name',
        'commit.committer.email', 'commit.committer.date', 'commit.message', 'commit.tree.sha',
        'commit.url', 'commit.comment_count', 'commit.verification.verified', 'commit.verification.reason',
        'author.login', 'committer.login']

# Specify DF structure
cols_specified = ['sha', 'author.name', 'author.email', 'author.date', 'committer.name', 'committer.email',
                  'committer.date', 'message', 'tree.sha', 'url', 'comment_count', 'verification.verified',
                  'verification.reason', 'author.login', 'committer.login']

# Specify columns for the users in the organtization
org_cols = ['name', 'updated_at', 'pushed_at']

# Get list of all Repositories in Organization
org_repos = api.repos.list_for_org(org="openvantage")
org_repos = pd.json_normalize(org_repos)
org_repos.drop(columns=[col for col in org_repos if col not in org_cols], inplace=True)
org_repos['updated_at'] = pd.to_datetime(org_repos['updated_at']).dt.tz_localize(None)
org_repos['pushed_at'] = pd.to_datetime(org_repos['pushed_at']).dt.tz_localize(None)

# Filter df to show entries within the last 30 days
today = pd.to_datetime('today')
df_filtered = org_repos.loc[org_repos['pushed_at'] > (today - pd.Timedelta(30, unit='d'))]

# Convert the DF into a list of repo as a list
repo_list = df_filtered["name"].tolist()


# Build a DF with the commits over the last 7days
# Create an empty DF to be populated in the for loop
daily_commits = pd.DataFrame(columns=cols_specified)

# Get the date for 7 days ago
h = datetime.timedelta(days=7)
date = pd.to_datetime('today') - h
date = date.strftime('%Y-%m-%d')

# Loop through all active repos and get the commits per branch
for i in range(len(repo_list)):
    repo_branches = api.repos.list_branches(repo=repo_list[i])
    repo_branches = pd.json_normalize(repo_branches)
    branches_list = repo_branches["name"].tolist()
    for j in branches_list:
        # print(repo_list[i] + '_' + j)
        temp_data = api.repos.list_commits(repo=repo_list[i], sha=j, since=date)
        if len(temp_data) == 0:
            pass
        else:
            temp = pd.json_normalize(temp_data)
            temp.drop(columns=[col for col in temp if col not in cols], inplace=True)
            temp.columns = temp.columns.map(lambda x: x.removeprefix("commit."))
            daily_commits = pd.concat([daily_commits, temp])
            # print(temp)

daily_commits['author.date'] = pd.to_datetime(daily_commits['author.date']).dt.tz_localize(None)
today_commits = daily_commits.loc[daily_commits['author.date'] > (today - pd.Timedelta(1, unit='d'))]

daily_commits.to_csv('daily_commits.csv')
today_commits.to_csv('today_commits.csv')