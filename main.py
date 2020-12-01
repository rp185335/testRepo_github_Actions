# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import requests



from datetime import date

import time

import pandas as pd
from tqdm import tqdm
from flask import request



def teams_info(auth):
    res = {}
    team_members_url = 'https://flow.pluralsight.com/v3/customer/core/teams/'
    response = requests.get(team_members_url, headers=auth)
    data = response.json()

    for member in data['results']:
        res[member['id']] = (member['id'], member['name'], member['ancestors'])
    # print(res)
    return res


# In[35]:


# teams_lst=teams_info(auth)
# print(len(teams_lst))


# In[36]:


# teams_id_lst=[]
# teams_name_lst=[]
# ancestor_team_lst=[]
# for info in teams_lst.values():
#   teams_id_lst.append(info[0])
#  teams_name_lst.append(info[1])
#  ancestor_team_lst.append(info[2])


# In[37]:


def get_members(team_id_lst, auth):
    res = {}
    for team_id in team_id_lst:
        team_members_url = 'https://flow.pluralsight.com/v3/customer/core/team_membership/?team_id={}&limit=1000'
        url = team_members_url.format(team_id)
        response = requests.get(url, headers=auth)
        data = response.json()

        for member in data['results']:
            if member['apex_user_id'] in res:
                res[member['apex_user_id']].append((member['id'], member['apex_user']['name'], member['team']['name']))
            else:
                res[member['apex_user_id']] = [(member['id'], member['apex_user']['name'], member['team']['name'])]

    # print(res)

    return res


# In[38]:


# All_members=get_members(teams_id_lst,auth)
# print(type(All_members))


# In[39]:


# import pprint

# pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(All_members)
# pp.pprint(len(All_members))


# In[40]:


# count = 0
# for i in All_members.values():
#   count+=len(i)
# print(count)


# In[41]:


# d = {}
# for key, value in All_members.items():
#    teams = []
#    for _, _, team in value:
#        teams.append(team)
#    d[key] = (value[0][1], ', '.join(teams))


# In[42]:


# pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(d)
# pp.pprint(len(d))
# from tqdm import tqdm


# In[43]:


# import pandas as pd
def get_impact_haloc(impacts):
    res = {}

    # print(impacts['results'])
    for impact in impacts['results']:
        if impact['apex_user_id'] not in res:
            res[impact['apex_user_id']] = (impact['impact_sum'], impact['haloc_sum'])

        else:
            new_impact_sum = (res[impact['apex_user_id']][0] + impact['impact_sum'])
            new_haloc_sum = (res[impact['apex_user_id']][1] + impact['haloc_sum'])
            res[impact['apex_user_id']] = (new_impact_sum, new_haloc_sum)

    res = list(res.values())
    if len(res) == 0:
        return 0, 0
    haloc_sum = res[0][1]

    impact_per_week = res[0][0]
    return haloc_sum, impact_per_week


def get_churn(impacts):
    churn = {}
    for impactss in impacts['results']:
        if impactss['apex_user_id'] not in churn:
            churn[impactss['apex_user_id']] = (impactss['churn_sum'], impactss['haloc_sum'])

        else:
            new_churn_sum = (churn[impactss['apex_user_id']][0] + impactss['churn_sum'])
            new_haloc_sum = (churn[impactss['apex_user_id']][1] + impactss['haloc_sum'])
            churn[impactss['apex_user_id']] = (new_churn_sum, new_haloc_sum)
    churn_sum = 0
    for j in churn.values():
        churn_sum = j[0]
    return churn_sum


def get_coding_days(impacts):
    ls = set()
    for k in impacts['results']:
        val = str(k['author_local_date_date'])
        val = val.split('-')
        ls.add(val[2])
        # code_lst.append(k['author_local_date_date'])

    coding_days_per_week = len(ls)
    return coding_days_per_week


# Impact per 2 weeks
def get_counts(impacts):
    # commits per coding day
    id_counts = 0

    for j in impacts['results']:
        id_counts += j['id_count']
    return id_counts


def get_user_info(employee_id, auth, date, num_days):
    date_today = str(pd.to_datetime(date))
    past_days = str(pd.to_datetime(date - pd.Timedelta(days=num_days)))

    commit_lst_members_url = 'https://flow.pluralsight.com/v3/customer/core/commits.agg/?limit=1000&apex_user_id__in={}&is_merge=false&is_pr_orphan=false&haloc__lt=1000&exclude_outliers=true&smart_dedupe=true&author_local_date__gte=' + past_days + '&author_local_date__lt=' + date_today + '&aggregate[count]=id&aggregate[sum]=haloc,churn,impact&group_by[apex_user_id,author_local_date__date]'
    url = commit_lst_members_url.format(employee_id)
    response = requests.get(url, headers=auth)
    impacts = response.json()

    # getting today's date without time.
    date_today_temp = date_today
    date_today_No_time = date_today_temp.split(' ')
    date_today_No_time_1 = date_today_No_time[0]
    # print(date_today_No_time_1)

    # getting past date without time
    past_days_temp = past_days
    past_days_No_time = past_days_temp.split(' ')
    past_days_No_time_1 = past_days_No_time[0]
    # print(past_days_No_time_1)

    haloc_sum, impact_value = get_impact_haloc(impacts)

    impact_value = float(impact_value)
    # haloc_sum= float(haloc_sum)

    churn_sum = get_churn(impacts)

    coding_days = get_coding_days(impacts)
    coding_days = float(coding_days)

    id_counts = get_counts(impacts)
    if coding_days != 0:
        commits_per_coding_day = (id_counts / coding_days)
    else:
        commits_per_coding_day = 0
    commits_per_coding_day = float(commits_per_coding_day)

    if haloc_sum == 0:
        efficiency = 0
    else:
        efficiency = 100 * (1 - ((churn_sum) / (haloc_sum)))
    efficiency = float(efficiency)

    Rating = ''
    Normalized_factor = 0

    if impact_value >= 200:
        Rating = 'Excellent'
        Normalized_factor = 5
    elif impact_value >= 150 and impact_value < 200:
        Rating = 'Good'
        Normalized_factor = 4
    elif impact_value >= 100 and impact_value < 150:
        Rating = 'Average'
        Normalized_factor = 3
    elif impact_value >= 50 and impact_value < 100:
        Rating = 'Below Average'
        Normalized_factor = 2
    elif impact_value >= 10 and impact_value < 50:
        Rating = 'Poor'
        Normalized_factor = 1
    else:
        Rating = 'Not Coding'
        Normalized_factor = 0

    return {'Impact': impact_value, 'Normalized': Normalized_factor, 'Rating': Rating,
            'Start Date': past_days_No_time_1, 'End Date': date_today_No_time_1}


# import time

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

#@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

def create_excel(All_members, auth):
    df = pd.DataFrame(columns=['Employee', 'Teams', 'Impact', 'Normalized', 'Rating', 'Start Date', 'End Date'])
    d = {}

    for key, value in All_members.items():
        teams = []
        for _, _, team in value:
            teams.append(team)
        d[key] = (value[0][1], ', '.join(teams))

    c = len(d)
    s = 0
    for key, value in tqdm(d.items()):
        # print(value)
        employee_id = key
        employee_name = value[0]
        teams_Name = value[1]
        start = time.time()
        info = get_user_info(employee_id, auth, date.today(), 7)
        s += time.time() - start

        info['Employee'] = employee_name
        info['Teams'] = teams_Name

        df = df.append(info, ignore_index=True)

    days_temp = info['Start Date']
    df = df.sort_values(by='Impact', ascending=False)
    # df['Commits Per Coding Day']=df['Commits Per Coding Day'].round(2)
    # df['Coding Days']=df['Coding Days'].round(2)
    df['Impact'] = df['Impact'].round(2)
    # df['Efficiency (in Percentages)']=df['Efficiency (in Percentages)'].round(2)
    df = df.round(2)
    # df['Commits Per Coding Day']=df['Commits Per Coding Day'].round(2)
    df = df[df['Employee'] != 'Undisclosed']
    df = df.drop_duplicates(subset=['Employee'])

    # strr=str(past_days_No_time_1)
    df.loc['mean'] = df.mean()
    # print(df)
    df.to_excel('/Users/RP185335/Weekly Reports/GitPrimeReport' + days_temp + '.xlsx', index=False)

    # return df



def main():
    # Use a breakpoint in the code line below to debug your script.
    #print(f'Hi')  # Press ⌘F8 to toggle the breakpoint.
    print('starting server')
    #keyboard.send('ctrl+c')

    auth = {
        'Authorization': 'Bearer sPsT4LxSYJzq7Rmxi6fyx1eN80XyBX9CrQMzHPYOkQZh0vptJ9otIJef011gB9fL'
    }

    # getting info of the teams
    teams_lst = teams_info(auth)
    # print(len(teams_lst))

    # list containing all the team id's
    teams_id_lst = []

    # list containing all the team names
    teams_name_lst = []

    # list containing all the parent team names
    ancestor_team_lst = []

    for info in teams_lst.values():
        teams_id_lst.append(info[0])
        teams_name_lst.append(info[1])
        ancestor_team_lst.append(info[2])

    # getting all members from get members function
    All_members = get_members(teams_id_lst, auth)

    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(All_members)
    # pp.pprint(len(All_members))

    # In[40]:

    # count = 0
    # for i in All_members.values():
    #    count+=len(i)
    # print(count)

    # In[41]:

    d = {}
    for key, value in All_members.items():
        teams = []
        for _, _, team in value:
            teams.append(team)
        d[key] = (value[0][1], ', '.join(teams))

    # In[42]:

    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(d)
    # pp.pprint(len(d))

    create_excel(All_members, auth)
    print('hi')
    shutdown()
    #exit(0)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
