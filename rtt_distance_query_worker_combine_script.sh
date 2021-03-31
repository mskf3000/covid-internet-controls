#!/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

IFS=$'\n' read -d '' -r -a targets < /home/${USER}/covid-internet-controls/rtt_target_ips.txt ; echo ${targets[*]}

for i in "${targets[@]}"
do
echo $i
ranNum=$[RANDOM%5+1]
sudo python3.6 query_workers.py -r $i -v
sleep $ranNum
done

sleep 108
