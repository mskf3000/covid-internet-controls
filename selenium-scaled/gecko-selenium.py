from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import Firefox
foptions = Options()
foptions.add_argument("--headless")
from datetime import date
import os
import sys
import errno
import time
driver = Firefox(options=foptions)


#create date folder
today = date.today()
d1 = today.strftime("%m-%d-%Y")
try:
    os.mkdir(d1)
except OSError as exc:#catch non-alreadyexists exception
    if exc.errno != errno.EEXIST:
        raise
    pass

#passed in args become the VPSfolder name
#Expecting to pass in city/country/ip
#ex python3 gecko-selenium.py HongKong129.21.21.21
VPSfolder = ""
for i, arg in enumerate(sys.argv):
    if(i > 0):
        VPSfolder = VPSfolder+arg 

print("Creating folder:"+VPSfolder)


#create VPS folder
try:
    os.mkdir(d1+"/"+VPSfolder)
except OSError as exc:#catch non-alreadyexists exception
    if exc.errno != errno.EEXIST:
        raise

#create some variables to track targets and errors
targetNum = 0
errorNum = 0
#if you need to resume to continue the process, set the value below to the value below the highest created directory in the past execution
resumeNum = 0

file = open("joined_urls.txt","r")
for i in file.readlines():
    targetNum = targetNum + 1
    if(targetNum < resumeNum):
        continue
    i = i[:-1]
    #create date/target  folder
    try:
        print(d1+"/"+VPSfolder+"/"+str(targetNum))
        os.mkdir(d1+"/"+VPSfolder+"/"+str(targetNum))
    except OSError as exc:#catch non-alreadyexists exception
        if exc.errno != errno.EEXIST:
            raise
        pass
    
    #create target.txt file containing the target string
    with open(d1+"/"+VPSfolder+"/"+str(targetNum)+"/"+'target.txt','w') as f:
        f.write(i+"\n")
   
   #create target.html file containing the resulting html from selenium
    print("getting:http://"+i+ " [start target #"+str(resumeNum)+",current target #"+str(targetNum)+",Errors:"+str(errorNum)+"]")
    driver = Firefox(options=foptions)
    try:
        #driver.manage().timeouts().implicitylWait(30, TimeUnit.SECONDS);
        driver.get("http://"+i)
        time.sleep(3)
        with open(d1+"/"+VPSfolder+"/"+str(targetNum)+"/"+'target.html','w') as f:
            f.write(driver.page_source)
    except Exception as a:
        print("Error getting page:"+i+":"+str(a))
        errorNum = errorNum + 1
        pass
    driver.close()
    
    #create target.html file containing the resulting html from selenium
    
    try:
        print("getting:https://"+i+" [target #"+str(targetNum)+",Errors:"+str(errorNum)+"]")
        driver = Firefox(options=foptions)
        driver.get("https://"+i)
        time.sleep(3)
        with open(d1+"/"+VPSfolder+"/"+str(targetNum)+"/"+'target_https.html','w') as f:
            f.write(driver.page_source)
    except Exception as a:
        print("Error getting page:"+i+":"+str(a))
        errorNum = errorNum + 1
        pass
    driver.close()

#driver = webdriver.Firefox('/home/matt/Downloads/geckodriver')#I give up
#driver = webdriver.Firefox()

print("Completed "+str(targetNum*2)+" requests, with "+str(errorNum)+" errors.")


