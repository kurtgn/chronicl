import requests
import base64
import json
import pdb
import sys
from datetime import datetime,timedelta


def project_weekly_minutes(project_id,response):
    for entry in response['data']:
        if entry['pid']!=None:
            if entry['pid']==project_id:
                return int(entry['totals'][7]/60000)
    return 'Not found'

def get_week(start_date):
    wkurl='https://toggl.com/reports/api/v2/weekly'
    token='0853c89724897fd187717c5798543975'
    string=token+':api_token'
    headers={'Authorization':'Basic '+base64.b64encode(string)}
    params={'user_agent':'lilmike@ya.ru','workspace_id':'550757','since':start_date}
    response=requests.get(wkurl,headers=headers,params=params).json()
    return response





startdate=datetime.strptime(sys.argv[1],'%Y-%m-%d')
enddate=datetime.strptime(sys.argv[2],'%Y-%m-%d')

print "range chosen: ",sys.argv[1], sys.argv[2]

# if selected day is not monday, we search for previous monday
startdate=startdate-timedelta(days=startdate.weekday())

print "\nprevious monday is: ",startdate.strftime('%Y-%m-%d')

weeks_number=int((enddate-startdate).days/7)

mondays=[]
for monday in range(0,weeks_number+1):
    mondays.append(startdate.strftime('%Y-%m-%d'))
    startdate+=timedelta(days=7)


print "\nall mondays in range:", mondays





token='0853c89724897fd187717c5798543975'
string=token+':api_token'
headers={'Authorization':'Basic '+base64.b64encode(string)}
url='https://www.toggl.com/api/v8/me'
response=requests.get(url,headers=headers).json()

email=response['data']['email']
print "got email: ",email

workspace_ids_names=[{'name':item['name'],'id':item['id']} for item in response['data']['workspaces'] if item['admin']==True]

print "workspaced detected: ",workspace_ids_names

if len(workspace_ids_names)>1:
    print "There are more than 1 workspaces with user as admin.\n",workspace_ids_names,"\nQuitting"
    quit()
if len(workspace_ids_names)==0:
    print "There are no workspaces where the user is admin. Quitting"
    quit()


print "getting workspace clients..."
first_workspace_id=workspace_ids_names[0]['id']

url='https://www.toggl.com/api/v8/workspaces/'+str(first_workspace_id)+'/clients'
params={'user_agent':email,'workspace_id':first_workspace_id}
clients=requests.get(url,headers=headers,params=params).json()

print "getting workspace projects by client..."



for client in clients:
    print 'client:', client['name']
    url='https://www.toggl.com/api/v8/clients/'+str(client['id'])+'/projects'
    projects=requests.get(url,headers=headers,params=params).json()
    client['projects']=projects


client_project_list=[]
for client in clients:
    for project in client['projects']:
        client_project_list.append({'client_id':client['id'],'project_id':project['id'],
                                    'client_name':client['name'],'project_name':project['name']})



for monday in mondays:
    week=get_week(monday)
    print "week: ",monday
    for item in client_project_list:
        print item['client_name'],":",item['project_name'], project_weekly_minutes(item['project_id'],week)



#c_id='14899549'
#url='https://www.toggl.com/api/v8/workspaces/'+c_id+'/projects'




#response=requests.get(url,headers=headers).json()

#print json.dumps(clients,indent=4,sort_keys=True)




