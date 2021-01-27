#!/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

IFS=$'\n' read -d '' -r -a websites < /home/hbuser/covid-internet-controls/website_list.txt ; echo ${websites[*]}

for i in "${websites[@]}"
do
echo $i
ranNum=$[RANDOM%5+1]
sudo python3.6 query_workers.py -t $i -v
sleep $ranNum
done

sleep 108

IFS=$'\n' read -d '' -r -a websites < /home/hbuser/covid-internet-controls/trigger_terms_website.txt ; echo ${websites[*]}
touch sahiltest.txt
for i in "${websites[@]}"
do
echo $i
ranNum=$[RANDOM%5+1]
sudo python3.6 query_workers.py -t $i -v
sleep $ranNum
done

