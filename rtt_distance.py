# Imports
from geopy.geocoders import Nominatim
import requests
import pingparsing
from math import *

# Latitude and longitude of input country and city:
def lat_long():
    # Getting country and city from user
    country = input("Country: ")
    city = input("City: ")

    geolocator = Nominatim(user_agent='myapp')
    location = geolocator.geocode(city + ',' + country)
    print(location.address)

    # Getting and printing the latitude and longitude of the location
    print("Latitude: ", location.latitude)
    print("Longitude: ", location.longitude)

# Getting host name and IP address
def host_IP():

    ipstack_access_key = "a77b2bc18426f38a043b75821a301d77"
    location_data_raw = requests.get(f"http://api.ipstack.com/check?access_key={ipstack_access_key}&format=1")
    location_data_dict = location_data_raw.json()
    print("Host Latitude: ", location_data_dict["latitude"])
    print("Host Longitude: ", location_data_dict["longitude"])

# Distance between two latitudes and longitudes:
def coordinate_distance():
    lat1 = float(input("Latitude of location 1: "))
    long1 = float(input("Longitude of location 1:"))
    lat2 = float(input("Latitude of location 2: "))
    long2 = float(input("Longitude of location 2:"))
   
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
    print("Distance:", distance_km, "km")
    print("Distance:", distance_nmi, "n mi")
def ip_rtt():
    with open(r"/home/osboxes/covid-internet-controls/target_ips.txt") as ip_list_file:
        ip_lists = [ip.replace("\n", "") for ip in ip_list_file.readlines()]
    print(ip_lists)

    with open("ips_with_rtt.csv", "w") as ip_with_rtt_file:
        ip_with_rtt_file.write("ip,rtt_avg\n")
        for ip in ip_lists:
            print("Pinging ", ip)
            ping_parser = pingparsing.PingParsing()
            transmitter = pingparsing.PingTransmitter()
            transmitter.destination = ip
            transmitter.count = 10
            result = transmitter.ping()
            ping_results = ping_parser.parse(result).as_dict()
            # ip_with_rtt_file.write(ip + "," + str(ping_results["rtt_avg"]))
            # ip_with_rtt_file.write(f"{ip},{ping_results['rtt_avg']}\n")
            print(ip, ":")
            print("RTT_min: ", ping_results['rtt_min'], "RTT_avg: ", ping_results['rtt_avg'], "RTT_max: ",
                  ping_results['rtt_max'])

    # Distance Calculation
    #for ip in ip_lists:
            RTT_time = ping_results['rtt_avg']
            distance = ((4 / 9) * RTT_time * 186.282)
            dist = str(distance)
            print("IP: ", ip, ",", "Distance(mi): " + dist)


lat_long()
host_IP()
coordinate_distance()
ip_rtt()





