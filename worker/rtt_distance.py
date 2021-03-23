# Imports

#import geopy
#from geopy.geocoders import Nominatim
#import json
import socket
import requests
import pingparsing
from math import *

# Latitude and longitude of input country and city:
# def lat_long():
# # Getting country and city from user
#  country = input("Country: ")
#  city = input("City: ")
#
# geolocator = Nominatim(user_agent='myapp')
#  location = geolocator.geocode(city + ',' + country)
#  print(location.address)
#
#  # Getting and printing the latitude and longitude of the location
#  print("Latitude: ", location.latitude)
#  print("Longitude: ", location.longitude)

# Getting host name and IP address
# def host_IP():
#
#  ipstack_access_key = "a77b2bc18426f38a043b75821a301d77"
#  location_data_raw = requests.get(f"http://api.ipstack.com/check?access_key={ipstack_access_key}&format=1")
#  location_data_dict = location_data_raw.json()
# print("Host Latitude: ", location_data_dict["latitude"])
#  print("Host Longitude: ", location_data_dict["longitude"])

def ip_rtt(ip:str):
   
   # Geolocating Source (host) IP address
   ipstack_access_key = "a77b2bc18426f38a043b75821a301d77"
   source_data_raw = requests.get(f"http://api.ipstack.com/check?access_key={ipstack_access_key}&format=1")
   source_data_dict = source_data_raw.json()
   #print("Host Latitude: ", source_data_dict["latitude"], "Host Longitude: ", source_data_dict["longitude"])
    
   # Geolocating Destination IP Address
   url = f"http://api.ipstack.com/{ip}?access_key={ipstack_access_key}&format=1"
   dest_location_dict = requests.get(url).json()
   #print("Destination latitude: ", dest_location_dict["latitude"], ", Destination Longitude: ", dest_location_dict["longitude"])

   first_city_name = source_data_dict["city"]
   second_city_name = dest_data_dict["city"]
   first_city_coordinates = f'{source_data_dict["latitude"]}, {source_data_dict["longitude"]}'
   second_city_coordinates = f'{dest_data_dict["latitude"]}, {dest_data_dict["longitude"]}'

   # Distance between two latitudes and longitudes:

   lat1 = float(source_data_dict["latitude"])
   long1 = float(source_data_dict["longitude"])
   lat2 = float(dest_location_dict["latitude"])
   long2 = float(dest_location_dict["longitude"])

   lat1 = radians(lat1)
   long1 = radians(long1)
   lat2 = radians(lat2)
   long2 = radians(long2)

  # Haversine Distance Formula
   d_lat = (lat2 - lat1)
   d_long = (long2 - long1)

   a = sin(d_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(d_long / 2) ** 2
   c = 2 * asin(sqrt(a))

  # Radius of earth in kilometers (use 3956 for miles).
   r = 6371

  # Distance in Km and nautical miles
   distance_km = c * r
   distance_nmi = distance_km / 1.852

  # Calculated distance in km and n mi
#  print("Distance:", distance_km, "km")
#  print("Distance:", distance_nmi, "n mi")

   host_name = socket.gethostname()
   host_ip = socket.gethostbyname(host_name)

    # Reading IP addresses to get RTT
    #with open(r"target_ips.txt") as ip_list_file:
    #    ip_lists = [ip.replace("\n", "") for ip in ip_list_file.readlines()]
    #print(ip_lists)
    #with open(r"target_ips.txt") as ip_list_file:
    #    ip_lists = [ip.replace("\n", "") for ip in ip_list_file.readlines()]
    #print(ip_lists)

    # with open("ips_with_rtt.csv", "w") as ip_with_rtt_file:
        #ip_with_rtt_file.write("host_ip,ip,rtt_avg\n")

   results_array = []

   
   ping_parser = pingparsing.PingParsing()
   transmitter = pingparsing.PingTransmitter()
   transmitter.destination = ip
   transmitter.count = 5
   result = transmitter.ping()
   host = str(host_ip)
   dest = str(ip)
   print("Source IP Address: ", host)
   print("Destination IP Address: ", dest)
   print("Pinging ", ip)
   results_dict = dict({'first_city_name': first_city_name, 'first_city_coordinates': first_city_coordinates, 'second_city_name': second_city_name, 'second_city_coordinates': second_city_coordinates,'rtt': '','distance': ''})
   # results_dict = dict({'source': host, 'destination': dest, 'rtt': '', 'distance': '','rtt_distance': ''})
   # print(result)

   if "Request timed out" in result.stdout or result.returncode == 1:
       error_msg = f"Request to {ip} timed out"
       results_dict["error"] = error_msg
       print(error_msg)
       results_array.append(results_dict)
       # continue
   ping_results = ping_parser.parse(result).as_dict()
       # ip_with_rtt_file.write("Host IP: " + str(host_ip) + "\n")
       # ip_with_rtt_file.write("Destination IP: " + ip + "\n")
       # ip_with_rtt_file.write("RTT: " + str(ping_results["rtt_avg"] + "\n"))
       # ip_with_rtt_file.write(f"{ip},{ping_results['rtt_avg']}\n")
       # print(ip, ":")
#      print("RTT_min: ", ping_results['rtt_min'], "RTT_avg: ", ping_results['rtt_avg'], "RTT_max: ",
#      ping_results['rtt_max'])

       # Distance Calculation
       # for ip in ip_lists:
   ping_results["rtt_avg"] = float(ping_results["rtt_avg"])
   RTT_time = float(ping_results["rtt_avg"])
   rtt_dist = ((4 / 9) * RTT_time * 186.282)
   rtt_dist_nmi = rtt_dist / 1.151
   dist = f'{distance_nmi} nmi'

       # print("IP: ", ip, ",", "Distance(mi): " + dist)
       # ip_with_rtt_file.write("Distance: " + str(distance))
       #results_dict = dict({'Source': host, 'Destination': ip,
        #                    'RTT': str(ping_results["rtt_avg"]), 'Distance(mi)': dist})
   results_dict["rtt"] = RTT_time
   #results_dict["distance"] = dist
   results_dict["distance"] = rtt_dist_nmi
   results_array.append(results_dict)

   #json_result = json.dumps(results_array, indent=2)
   #print(json_result)
   return results_array

# lat_long()
# host_IP()
# coordinate_distance()
#ip_rtt(ip)
# lat_long()
# host_IP()
# coordinate_distance()
#ip_rtt()





