import sys
import socket
import csv
import os
import errno
import re

url_list = []

with open('ru.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    line_count = 0
    for row in csv_reader:
         with open(row["URL"], mode='r') as csv_file:
             h_filename = "houtput/Ukraine/russia" + row["URL"] + ".csv"
             t_filename = "toutput/Ukraine/russia" + row["URL"] + ".csv"

             with open(h_filename, mode='r') as h_csv_file:
                 h_csv_reader = csv.DictReader(h_csv_file)
                 for h_row in h_csv_reader:
                     if(re.search('HTTP',h_row["Message"])):
                         h_TTL = h_row["TTL"]
                         break

             with open(t_filename, mode='r') as t_csv_file:
                 t_csv_reader = csv.DictReader(t_csv_file)
                 for t_row in t_csv_reader:
                     t_TTL = t_row["TTL"]

             if(h_TTL < t_TTL-3):
                 url_list.append([row["URL"]])


    with open("results.csv", mode='w') as results:
        results_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        results_writer.writerow(['URL'])
        for item in url_list:
            results_writer.writerow(item)






