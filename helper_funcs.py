from matplotlib import pyplot as plt
import matplotlib.patches as mpatches
from datetime import timedelta
from math import floor
import requests



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


def plot_result(data,mondays,projectnames=True):
    handles,labels=[],[]

    fig2,legend=plt.subplots()
    fig,graph=plt.subplots()
    graph.set_ylabel('Weekly hours')

    lower_line=[0]*len(data[0]['weekly_hours'])
    x=list(range(0,len(lower_line)))
    plt.xticks(x,mondays,rotation='vertical')
    for item in data:
        if projectnames:
            labels.append(item['client_name'] + " : " + item['project_name'])
        else:
            labels.append(item['client_name'])
        handles.append(mpatches.Patch(color=item['color']))
        upper_line=vector_sum(item['weekly_hours'],lower_line)
        graph.fill_between(x,upper_line,lower_line,color=item['color'],edgecolor='#555555')
        #graph.plot(x,upper_line,color=item['color'],antialiased=True,linewidth=5)
        lower_line=upper_line

    #plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
    legend.legend(handles,labels,loc=(0.05,0.05),fancybox=True)

    #plt.subplots_adjust(right=0.5)
    #plt.savefig('result.png')
    plt.tight_layout()
    plt.show()


i=0

def all_project_hours(data,client_name):
    global i
    #pdb.set_trace()
    hours=[0]*len(data[0]['weekly_hours'])

    for item in data:
        if item['client_name']==client_name:
            hours=vector_sum(hours,item['weekly_hours'])

    color=colordict[i]
    i+=1 if i<=14 else 0

    return {'hours':hours,'color':color}


def get_download_dates(startdate,enddate):
    # IF start date is not the beginning of the week (not Monday),
    # We will start from the Monday of the week selected."
    if startdate.weekday()!=0:
        startdate=startdate-timedelta(days=startdate.weekday())


    # calculating number of weeks from the number of days.
    # If the range is 13 days, this is considered as 1 week because the last week is not finished yet
    # and we can't make a report if we don't have all the data.
    weeks_number=int(floor(float((enddate-startdate).days)/7))

    # to get all the data for the selected range, we need to divide it into 7-day chunks
    mondays=[]
    for monday in range(0,weeks_number):
        mondays.append(startdate.strftime('%Y-%m-%d'))
        startdate+=timedelta(days=7)

    return mondays