from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import Firefox
foptions = Options()
foptions.add_argument("--headless")
from datetime import date
from datetime import datetime
import os
import sys
import errno
import time

#python get 
import urllib.request,urllib.error,urllib.parse

#wget get
import subprocess

driver = Firefox(options=foptions)
#below will put a delay between each request
#driver.manage().timeouts().implicitylWait(30, TimeUnit.SECONDS);
#driver.manage().timeouts().pageLoadTimeout(10,TimeUnit.SECONDS);
driver.set_page_load_timeout(20)
#driver.implicitly_wait(30)
#will throw timeoutexception when takes longer

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

file = open("5000subsetrandom.txt","r")
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
        f.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S')+"\n")
   
    #create target.html file containing the resulting html from selenium
    print("getting:http://"+i+ " [start target #"+str(resumeNum)+",current target #"+str(targetNum)+",Errors:"+str(errorNum)+"]")
    driver = Firefox(options=foptions)
    try:
        driver.get("http://"+i)
        time.sleep(3)
        with open(d1+"/"+VPSfolder+"/"+str(targetNum)+"/"+'selenium_target.html','w') as f:
            f.write(driver.page_source)
    except Exception as a:
        print("Error getting page:"+i+":"+str(a))
        errorNum = errorNum + 1
        pass
    
    #create target_https.html file containing the resulting html from selenium 
    try:
        print("getting:https://"+i+" [target #"+str(targetNum)+",Errors:"+str(errorNum)+"]")
        driver.get("https://"+i)
        time.sleep(3)
        with open(d1+"/"+VPSfolder+"/"+str(targetNum)+"/"+'selenium_target_https.html','w') as f:
            f.write(driver.page_source)
    except Exception as a:
        print("Error getting page:"+i+":"+str(a))
        errorNum = errorNum + 1
        pass
    
        
    #python get
    try:
        with open(d1+"/"+VPSfolder+"/"+str(targetNum)+"/"+'python_target.html','w') as f:
            url = "http://"+i
            f.write(urllib.request.urlopen(url).read().decode("utf8"))
    except Exception as a:
        print("(python)Error getting page:"+i+":"+str(a))
        pass
    
    try:
        with open(d1+"/"+VPSfolder+"/"+str(targetNum)+"/"+'python_target_https.html','w') as f:
            url = "https://"+i 
            f.write(urllib.request.urlopen(url).read().decode("utf8"))
    except Exception as a:
        print("(python)Error getting page:"+i+":"+str(a))
        pass

    #wget get
    output = subprocess.run(["wget","-O",d1+"/"+VPSfolder+"/"+str(targetNum)+"/wget_target_http.html","-e","robots=off","http://"+i],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)     
    output = subprocess.run(["wget","-O",d1+"/"+VPSfolder+"/"+str(targetNum)+"/wget_target_https.html","-e","robots=off","https://"+i],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
   
   #now compare the length of the files and see if there is a significant length difference (>100)
   #for now use something like wc *.html perhaps

driver.close()

print("Completed "+str(targetNum*2)+" requests, with "+str(errorNum)+" errors.")


