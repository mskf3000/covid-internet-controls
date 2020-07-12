IFS=$'\n' read -d '' -r -a websites < trigger_terms_website.txt ; echo ${websites[*]}

for i in "${websites[@]}"
do
echo $i
ranNum=$[RANDOM%10+1]
sudo python3.6 query_workers.py -t $i -v
sleep $ranNum
done


