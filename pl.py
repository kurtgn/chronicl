



def vector_sum(v1,v2):
    length1=len(v1)
    if length1!=len(v2):
        print "Vector lengths differ. Quitting..."
        quit()
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




