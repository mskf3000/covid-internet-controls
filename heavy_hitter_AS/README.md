# Essential files and folders required to run heavy hitter AS program
1. countries/
2. 20200501_as_rel.txt
3. asrelationship.py
4. countries_list.txt
5. heavy_hitter_list_of_all_AS_in_country_list.py
6. heavy_hitter_list_of_all_AS_in_country_list.sh
7. asrelationship_internet_coverage_code.py

# Run the process
1. $./heavy_hitter_list_of_all_AS_in_country_list.sh
2. $ python asrelationship_internet_coverage_code.py > internet_covered.txt

Note: All the pattern (for AS number parsing) to include and exclude need to be added in shell script.

# Output files:
1. File having top in file name contain top 20 ASes like north_korea_top_AS_list.txt
2. File having full in file name conatin all ASes like north_korea_full_AS_list.txt
3. File having heavy hitter and country in file name contain final heavy hitter ASes list like united_state_14_heavy_hitter.txt
4. as_relationship_graph.txt contain parent-child cone graph from caida ASes relationship dataset + heavy hitter ASes + top ASes + other information related to parent child relationship testing.
5. internet_covered.txt contain % of ASes covered as child of heavy hitter ASes.
