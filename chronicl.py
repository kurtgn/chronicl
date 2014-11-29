import requests
import base64
import sys
from datetime import datetime,timedelta
from math import floor
from matplotlib import pyplot as plt


if len(sys.argv)!=3:
    print "Enter start date and end date as command line arguments."
    print "Example: python chronicl.py 2014-08-15 2014-10-21\n"
    quit()


colordict={0:'#4dc3ff',
        1:'#bc85e6',
        2:'#df7baa',
        3:'#f68d38',
        4:'#b27636',
        5:'#8ab734',
        6:'#14a88e',
        7:'#268bb5',
        8:'#6668b4',
        9:'#a4506c',
        10:'#67412c',
        11:'#3c6526',
        12:'#094558',
        13:'#bc2d07',
        14:'#999999'}



# search the JSON response for occurences of project_id, return project summary time in minutes
def project_weekly_hours(project_id,response):
    for entry in response['data']:
        if entry.get('pid')==project_id:
            return round(entry['totals'][7]/float(3600000),2)
    return 0

# get weekly summary starting from start_date
def get_weekly_data(start_date,headers,params):
    url='https://toggl.com/reports/api/v2/weekly'
    params['since']=start_date
    response=requests.get(url,headers=headers,params=params).json()
    return response

def projects_of_client(client_id,project_list):
    c_projects=[project for project in project_list if project.get('cid')==client_id]
    return c_projects



def vector_sum(v1,v2):
    length1=len(v1)
    result=[round(v1[i]+v2[i],2) for i in range(0,length1)]
    return result


def plot_result(data,mondays):
    lower_line=[0]*len(data[0]['weekly_hours'])
    x=list(range(0,len(lower_line)))
    plt.xticks(x,mondays,rotation='vertical')
    for item in data:
        upper_line=vector_sum(item['weekly_hours'],lower_line)
        plt.fill_between(x,upper_line,lower_line,color=item['color'],edgecolor='grey')
        lower_line=upper_line
    #plt.savefig('result.png',bbox_inches='tight')
    #plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
    plt.show()




try:
    startdate=datetime.strptime(sys.argv[1],'%Y-%m-%d')
except ValueError:
    print "Can't read the arguments. The date format should be YYYY-MM-DD, e.g. 2014-08-15\n"
    quit()
try:
    enddate=datetime.strptime(sys.argv[2],'%Y-%m-%d')
except ValueError:
    print "Can't read the arguments. The date format should be YYYY-MM-DD, e.g. 2014-08-15\n"
    quit()

print "range chosen: ",sys.argv[1], sys.argv[2]

if startdate.weekday()!=0:
    print "Your start date is not the beginning of the week (not Monday). We will start from the Monday of the week you selected."
    startdate=startdate-timedelta(days=startdate.weekday())
    print "\nThis Monday is: ",startdate.strftime('%Y-%m-%d')

# calculating number of weeks from the number of days.
# If the range is 13 days, this is considered as 1 week because the last week is not finished yet
# and we can't make a report if we don't have all the data.
weeks_number=int(floor(float((enddate-startdate).days)/7))

# to get all the data for the selected range, we need to divide it into 7-day chunks
mondays=[]
for monday in range(0,weeks_number):
    mondays.append(startdate.strftime('%Y-%m-%d'))
    startdate+=timedelta(days=7)


print "\nall mondays in range:", mondays


usertoken='0853c89724897fd187717c5798543975'

string=usertoken+':api_token'
headers={'Authorization':'Basic '+base64.b64encode(string)}
url='https://www.toggl.com/api/v8/me'
response=requests.get(url,headers=headers).json()

email=response['data']['email']


workspace_ids_names=[{'name':item['name'],'id':item['id']} for item in response['data']['workspaces'] if item['admin']==True]

if len(workspace_ids_names)>1:
    print "There are more than 1 workspace with user as admin:"
    for w in workspace_ids_names:
        print workspace_ids_names.index(w),":",w['name']
    print "Which workspace do you want analyzed?"
    wnum = int(raw_input("Enter 0,1,2 etc.: "))

if len(workspace_ids_names)==0:
    print "There are no workspaces where user is admin. Quitting"
    quit()

# a short way of selecting workspace: we just get the first one from the list. Need to prompt the user though
print "getting workspace clients..."
first_workspace_id=workspace_ids_names[wnum]['id']

# getting clients dict
url='https://www.toggl.com/api/v8/workspaces/'+str(first_workspace_id)+'/clients'
params={'user_agent':email,'workspace_id':first_workspace_id}
clients=requests.get(url,headers=headers,params=params).json()

print "getting workspace projects..."

# getting projects dict
url='https://www.toggl.com/api/v8/workspaces/'+str(first_workspace_id)+'/projects'
project_list=requests.get(url,headers=headers,params=params).json()


# going through the client dict, adding projects to each client
for client in clients:
    print 'client:', client['name']
    client['projects']=projects_of_client(client['id'],project_list)

# we also need to find all projects not attached to clients
noclient={'name':'No client','id':0}
noclient['projects']=projects_of_client(None,project_list)
clients.append(noclient)

# making a clean and simple list of clients and projects
client_project_list=[]
for client in clients:
    for project in client['projects']:
        #pdb.set_trace()
        client_project_list.append({'client_id':client['id'],'project_id':project['id'],
                                    'client_name':client['name'],'project_name':project['name'],
                                    'weekly_hours':[],'color':colordict[int(project['color'])]})

# and a final entry in our list is time spent without projects at all
client_project_list.append({'client_id':None,'project_id':None,
                                    'client_name':'No client','project_name':'No project',
                                    'weekly_hours':[],'color':'black'})


# iterating over our project list and adding summary hours for each week
for monday in mondays:
    week=get_weekly_data(monday,headers,params)
    print "week: ",monday
    for item in client_project_list:
        item['weekly_hours'].append(project_weekly_hours(item['project_id'],week))
        print item['client_name'],":",item['project_name'],":",item['weekly_hours']

# and plotting the whole bunch
plot_result(client_project_list,mondays)
