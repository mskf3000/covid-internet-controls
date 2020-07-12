IFS=$'\n' read -d '' -r -a countries < countries_list.txt ; echo ${countries[*]}
A="full_AS_list.txt"
B="top_AS_list.txt"
for i in "${countries[@]}"
do
echo $i
C=$i$A
D=$i$B
C="${C/countries/}" 
C="${C/.html/_}" 
C="${C/'/'/}" 
D="${D/countries/}" 
D="${D/.html/_}" 
D="${D/'/'/}"
python3 heavy_hitter_list_of_all_AS_in_country_list.py $i| grep AS[0-9]|grep -v -e '"' |grep -v -e 'Net' |grep -v -e "Cyfyngedig" > $C ; sed -i 's/Data  : AS//g' $C ; sed '1,100!d' $C > $D; IFS=$'\n' read -d '' -r -a lines < $D ; echo ${lines[*]}
done

python asrelationship.py > as_relationship_graph.txt
