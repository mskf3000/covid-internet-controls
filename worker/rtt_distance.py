# Imports

import socket
import requests
import pingparsing
from math import *

def ip_rtt(ip:str):
# def rtt_distance(ip:str):   

   # Geolocating Source (host) IP address
   ipstack_access_key = "a77b2bc18426f38a043b75821a301d77"
   source_data_raw = requests.get(f"http://api.ipstack.com/check?access_key={ipstack_access_key}&format=1")
   source_data_dict = source_data_raw.json()
   #print("Host Latitude: ", source_data_dict["latitude"], "Host Longitude: ", source_data_dict["longitude"])
    
   # Geolocating Destination IP Address
   url = f"http://api.ipstack.com/{ip}?access_key={ipstack_access_key}&format=1"
   dest_location_dict = requests.get(url).json()
   
   # Source and Destination locations and coordinates
   first_city_name = source_data_dict["city"]
   second_city_name = dest_location_dict["city"]
   first_city_coordinates = f'{source_data_dict["latitude"]}, {source_data_dict["longitude"]}'
   second_city_coordinates = f'{dest_location_dict["latitude"]}, {dest_location_dict["longitude"]}'

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

   # Getting RTT from Source and Updating the results array
   host_name = socket.gethostname()
   host_ip = socket.gethostbyname(host_name)

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

   if "Request timed out" in result.stdout or result.returncode == 1:
       error_msg = f"Request to {ip} timed out"
       results_dict["error"] = error_msg
       print(error_msg)
       results_array.append(results_dict)
       
   ping_results = ping_parser.parse(result).as_dict()
     
   # Distance Calculation from RTT
     
   ping_results["rtt_avg"] = float(ping_results["rtt_avg"])
   RTT_time = float(ping_results["rtt_avg"])
   rtt_dist = ((4 / 9) * RTT_time * 186.282)
   rtt_dist_nmi = rtt_dist / 1.151
   dist = f'{distance_nmi} nmi'

   results_dict["rtt"] = RTT_time
   results_dict["distance"] = rtt_dist_nmi
   results_array.append(results_dict)

   return results_array

#rtt_distance()





