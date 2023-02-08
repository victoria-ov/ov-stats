import os

import pandas as pd

# Setup GitHub API (GhApi)
token = os.environ['ACCESS_TOKEN']
from ghapi.all import GhApi

api = GhApi(owner='openvantage', token=token)

# specify columns of interest
pr_cols = ['number', 'user.login', 'created_at', 'updated_at', 'closed_at', 'merged_at', 'requested_reviewers',
           'labels', 'head.label', 'head.ref', 'head.repo.name', 'head.repo.size', 'state']

# specify columns for the users in the organtization
org_cols = ['name', 'updated_at', 'pushed_at']

# Create a list of open PRs for all repos
# Get all repos in the Organization
org_repos = api.repos.list_for_org(org="openvantage")
org_repos = pd.json_normalize(org_repos)
org_repos.drop(columns=[col for col in org_repos if col not in org_cols], inplace=True)
org_repos['updated_at'] = pd.to_datetime(org_repos['updated_at']).dt.tz_localize(None)
org_repos['pushed_at'] = pd.to_datetime(org_repos['pushed_at']).dt.tz_localize(None)
repo_list = org_repos["name"].tolist()

# Iterate and build the df
all_prs = pd.DataFrame(columns=pr_cols)
# open_prs = open_prs.reset_index(drop=True)ß

for i in range(len(repo_list)):
    temp_data = api.pulls.list(repo=repo_list[i], state='all')
    temp = pd.json_normalize(temp_data)
    temp.drop(columns=[col for col in temp if col not in pr_cols], inplace=True)
    all_prs = pd.concat([all_prs, temp])

all_prs = all_prs.reset_index(drop=True)

reviewers = []
labels = []
for i in all_prs.index:
    if all_prs['requested_reviewers'][i] == []:
        reviewers.append('')
    else:
        reviewers.append(all_prs['requested_reviewers'][i][0]['login'])

    if all_prs['labels'][i] == []:
        labels.append('')
    else:
        labels.append(all_prs['labels'][i][0]['name'])

all_prs['requested_reviewers'] = reviewers
all_prs['labels'] = labels

all_prs['labels'] = all_prs['labels'].replace('', 'Not labelled', regex=True)
all_prs['requested_reviewers'] = all_prs['requested_reviewers'].replace('', 'No reviewer assigned', regex=True)

all_prs['created_at'] = pd.to_datetime(all_prs['created_at']).dt.tz_localize(None)
all_prs['updated_at'] = pd.to_datetime(all_prs['updated_at']).dt.tz_localize(None)
all_prs['closed_at'] = pd.to_datetime(all_prs['closed_at']).dt.tz_localize(None)
all_prs['merged_at'] = pd.to_datetime(all_prs['merged_at']).dt.tz_localize(None)

grouped = all_prs.groupby(['state'])
open_prs = grouped.get_group("open")
closed_prs = grouped.get_group("closed")

# specify columns of interest
open_prs_cols = ['number', 'user.login', 'created_at', 'updated_at', 'requested_reviewers',
               'labels', 'head.label', 'head.ref', 'head.repo.name', 'head.repo.size', 'state']

open_prs.drop(columns=[col for col in open_prs if col not in open_prs_cols], inplace=True)

# Calculate the duration since the PR was created
open_prs['days-open'] = pd.to_datetime('today') - open_prs['created_at']

closed_prs_v2 = closed_prs.assign(closing_time=lambda x: x.merged_at - x.created_at)
closed_prs_v2['hours'] = closed_prs_v2['closing_time'] / pd.Timedelta(hours=1)

open_prs.to_csv('./Data/open_prs.csv')
closed_prs_v2.to_csv('./Data/closed_prs.csv')