__author__ = 'yangwu'

import MySQLdb
import os
import csv
from datetime import timedelta

globvar = 0

# read Input from a csv file
def categorize(filepath, db):
    Seperate=""
    dict = {}
    # read data from csv file, and calculate the number according to the domain name
    with open(filepath, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            data = row[0]
            date = row[1]
            #update the data onto "Data"
            update_data(data, db)

            if Seperate != date:# update the dictionary every second
                yield dict
                Seperate = date # update the date separator
                dict.clear()    # clean the dictionary ready for nxt set of data
                dict['time'] = Seperate.lstrip()

            # extract the domain name from data
            import re
            namelist = re.split('@',data)
            try:
                domain = namelist[1].lower() # make all the domain strings to lower case
            except IndexError:
                print "ERROR: Out of Index"

            if domain not in dict.keys():
                dict[domain] = 1
            else:
                dict[domain] +=1

    yield dict

# update the data to "Data"
def update_data(data, db):
    cursor = db.cursor()

    query = "INSERT INTO Data (INFO) VALUES ('%s');"%data
    cursor.execute(query)
    db.commit()

    cursor.close()

# updata the dictionary data up to "Analytics"
def update_table(dict, db):
    #convert the string to time
    import datetime
    time = datetime.datetime.strptime(dict['time'], "%d-%m-%Y %H:%M:%S")

    for key in dict:
        if key != 'time': # update each item in dictionary except for 'time'
            #print key, "Correspond to", dict[key]
            update_domain(key, dict[key], time, db)


def update_domain(domain, number, time, db):
    cursor = db.cursor()

    if check_exist(domain, '', cursor): #If there is previous row exist:
        query = "SELECT * FROM Analytics WHERE DOMAINs = '%s' ORDER BY DATEs DESC LIMIT 1;"%domain
        cursor.execute(query)
        tempList = cursor.fetchone()
        #print tempList, date
        number += tempList[1]

    query = "INSERT INTO Analytics (DOMAINs,COUNTs,PERCENT,DATEs) VALUES ('%s',%s, %s, '%s');"%(domain,number, 0,time)
    cursor.execute(query)
    db.commit()

    # calculate the percentage of growth
    timeBoundary = time - timedelta(seconds=60)

    condition = "AND DATEs < '%s' ORDER BY DATEs DESC LIMIT 1"%timeBoundary
    if check_exist(domain, condition,cursor): # check the total number 1 min ago
        percent = float(100*(number-globvar))/number
    else: # The domain only occurs during this period of 60 sec -> 100% growth
        percent = 100

    query = "UPDATE Analytics SET PERCENT='%s' WHERE DOMAINs ='%s' AND DATEs = '%s';"%(percent, domain, time)
    cursor.execute(query)
    db.commit()

    cursor.close()

def check_exist(domain, condition, cursor):
    query = "SELECT * FROM Analytics WHERE DOMAINs = '%s' %s;"%(domain,condition)
    cursor.execute(query)
    tempList = cursor.fetchall()

    if len(tempList)!=0:
        global globvar
        globvar = tempList[0][1]

    #print tempList
    return len(tempList)!=0


def rank(time, db):
    cursor = db.cursor()

    ranking = {}
    i = 0;

    #convert the string to time
    import datetime
    Present = datetime.datetime.strptime(time, "%d-%m-%Y %H:%M:%S")
    # calculate the percentage of growth
    timeBoundary = Present - timedelta(seconds=61) #include the 61th second ago
    #print dateBoundary
    query = "SELECT * FROM Analytics Where DATEs > '%s' ORDER BY DATEs DESC"%timeBoundary # Based on descending time, make the most present row in front
    cursor.execute(query)
    tempList = cursor.fetchall()

    for row in tempList:
        if row[0] not in ranking.keys():
            ranking[row[0]] = row[2]

    result = ""
    #print "The ranking of the growth rate over last 60 sec:"
    # Sort by the value in descending order
    for key, value in sorted(ranking.iteritems(), key=lambda (k,v): (v,k),reverse=True):
        result += "Domain: "+ key +" Growth rate: "+str(value)+"\n"
        i+=1
        if i >= 50: #only keep the top 50
            break

    cursor.close()
    return result


def run_analytic(filepath):
    result = "No update for any data!!!"
    try: # Build the connection with the database
        db = MySQLdb.connect('localhost', 'root', 'user1234', 'DataAnalytics')
    except:
        print "Unable to connect to the database"

    for index in categorize(filepath, db): # deliminate the data by different date
        #print index
        if 'time' in index.keys(): # Check if the dictionary is null
            update_table(index, db)
    
    if 'time' in index.keys(): # Check if the dictionary is null
        result = rank(index['time'],db) # Display the ranking

    #print result
    db.close() #Close the connection
    return result

#================Main Function========================#
#filedir1 = "input/email2.csv"
#filepath1 = os.path.join(os.getcwd(), filedir1)
#run_analytic(filedir1, filepath1)
#================Main Function========================#
