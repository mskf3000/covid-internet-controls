#!/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

#IFS=$'\n' read -d '' -r -a websites < /home/sg5414/covid-internet-controls/website_list.txt ; #echo ${websites[*]}

#for i in "${websites[@]}"
#do
#echo $i
#ranNum=$[RANDOM%10+1]
#sudo python3.6 query_workers.py -t $i -v
#sleep $ranNum
#done

for file in *; do
	    if [ -d "$file" ]; then
	        echo "$file"
		cd $file
		for innerfile in *; do
		    if [ -d "$innerfile" ]; then
		        echo "$innerfile"
			cd $innerfile
			firefox *
			sleep 0.5
			cd ../
		    fi
		done
		cd ../
	    fi
done

