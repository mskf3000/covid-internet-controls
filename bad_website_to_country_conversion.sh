#!/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
IFS=$'\n' read -d '' -r -a websites < /home/sg5414/covid-internet-controls/bad_website_list.txt ; ##echo ${websites[*]}


for i in "${websites[@]}"
do
##echo $i
E=`dig +short \$i @resolver1.opendns.com`
#paste <(printf %s "$i") <(printf %s "$E")
F=`echo $E  | head -n1 | cut -d " " -f2`
#paste <(printf %s "$i") <(printf %s "$F")
G=`geoiplookup \$F`
H=`echo \$G  | head -n1 | cut -d " " -f5-6`
##echo $H
paste <(printf %s "$i") <(printf %s "$H")
done
