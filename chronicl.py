import base64
import sys
from datetime import datetime
from helper_funcs import *
import re


if len(sys.argv)!=4:
    print "\nEnter 3 command line arguments: start date, end date, and user token."
    print "Example: python chronicl.py 2014-08-15 2014-10-21 0853c89724897fd1877\n"
    quit()



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

mondays=get_download_dates(startdate,enddate)

usertoken=sys.argv[3]


string=usertoken+':api_token'
headers={'Authorization':'Basic '+base64.b64encode(string)}
url='https://www.toggl.com/api/v8/me'
response=requests.get(url,headers=headers)
if response.status_code!=200:
    print "Login failed. Check your API key"
    quit()

response=response.json()
email=response['data']['email']

workspace_ids_names=[{'name':item['name'],'id':item['id']} for item in response['data']['workspaces'] if item['admin']==True]

if len(workspace_ids_names)>1:
    print "\nThere are more than 1 workspace with user as admin:"
    for w in workspace_ids_names:
        print workspace_ids_names.index(w),":",w['name']
    print "\nWhich workspace do you want graphed?"
    try:
        wnum = int(raw_input("Enter 0,1,2 etc.: "))
        first_workspace_id=workspace_ids_names[wnum]['id']

    except ValueError:
        print 'Wrong input (non-integer).'
        quit()
    except IndexError:
        print 'Wrong input: you dont have workspace with this number.'
        quit()


if len(workspace_ids_names)==0:
    print "There are no workspaces where user is admin. Quitting"
    quit()


print "getting workspace clients..."


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
    client['projects']=projects_of_client(client['id'],project_list)

# we also need to find all projects not attached to clients
noclient={'name':'No client','id':0}
noclient['projects']=projects_of_client(None,project_list)
clients.append(noclient)

# making a clean and simple list of clients and projects
client_project_list=[]
for client in clients:
    for project in client['projects']:

        client_project_list.append({'client_id':client['id'],'project_id':project['id'],
                                    'client_name':client['name'],'project_name':project['name'],
                                    'weekly_hours':[],'color':colordict[int(project['color'])]})

# and a final entry in our list is time spent without projects at all
client_project_list.append({'client_id':None,'project_id':None,
                                    'client_name':'No client','project_name':'No project',
                                    'weekly_hours':[],'color':'black'})


# iterating over our project list and downloading summary hours for each week
for monday in mondays:
    week=get_weekly_data(monday,headers,params)
    print "Downloading weekly data: ",monday
    for item in client_project_list:
        item['weekly_hours'].append(project_weekly_hours(item['project_id'],week))
        #print item['client_name'],":",item['project_name'],":",item['weekly_hours']


print '\nYour projects: '
for item in client_project_list:
    print str(client_project_list.index(item))+" : "+item['client_name']+" : "+item['project_name']


clients_or_projects=raw_input('\nGroup by clients or by projects? (p or c) ')

if clients_or_projects=='p':

    print 'Select projects you want in your graph.'
    positions=raw_input('Enter integers separated by spaces, or "a" for all: ')

    if positions!="a":
        positions=re.sub(' +',' ',positions).split(' ')
        try:
            positions=[int(p) for p in positions]
        except ValueError:
            print 'Wrong input. Enter integers separated by spaces.'
            quit()
        client_project_list=[item for item in client_project_list if client_project_list.index(item) in positions]




    # and plotting the whole bunch
    plot_result(client_project_list,mondays)

elif clients_or_projects=='c':



    client_list=[]
    clientnames=[item['client_name'] for item in client_project_list]
    clientnames=list(set(clientnames))


    print '\nYour clients:\n'
    for item in clientnames:
        print str(clientnames.index(item))+" : "+item


    print '\nSelect clients you want in your graph.'
    positions=raw_input('Enter integers separated by spaces, or "a" for all: ')
    if positions!='a':
        positions=re.sub(' +',' ',positions).split(' ')
        try:
            positions=[int(p) for p in positions]
        except ValueError:
            print 'Wrong input. Enter integers separated by spaces.'
            quit()
        clientnames=[name for name in clientnames if clientnames.index(name) in positions]

    for name in clientnames:
        client_list.append({'client_id':None,'project_id':None,
                                    'client_name':name,'project_name':None,
                                    'weekly_hours':all_project_hours(client_project_list,name)['hours'],
                                    'color':all_project_hours(client_project_list,name)['color']})



    plot_result(client_list,mondays,projectnames=False)

else:
    print "Wrong input. Enter p or c"