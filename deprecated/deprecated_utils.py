import http.client
import json
from typing import Union, Dict
import logging
import urllib.parse
import pandas as pd
import pickle
import os
import math
import numpy as np
import zipfile
from dotenv import load_dotenv

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the distance between two points from lat/long into kilometers"""
    R = 6371  # Earth radius in kilometers
    
    # Convert degrees to radians
    lat1_rad, lon1_rad, lat2_rad, lon2_rad = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def longitude_distance(latitude: float) -> float:
    """Returns the distance in kilometers per degree of longitude at a given latitude"""
    return 111.32 * math.cos(math.radians(latitude))


# Unpack the cache.zip file
with zipfile.ZipFile("cache.zip", "r") as zip_ref:
    zip_ref.extract("cache.pkl")

# Load the cache.pkl into a DataFrame
"""
Data Source:

WorldPop (www.worldpop.org - School of Geography and Environmental Science, University of Southampton; 
Department of Geography and Geosciences, University of Louisville; Departement de Geographie, Universite de Namur) 
and Center for International Earth Science Information Network (CIESIN), Columbia University (2018). 
Global High Resolution Population Denominators Project - Funded by The Bill and Melinda Gates Foundation (OPP1134076). 
https://dx.doi.org/10.5258/SOTON/WP00670
"""
global_data = pd.DataFrame(pickle.load(open("cache.pkl", "rb")), columns=['longitude', 'latitude', 'population'])
# Filter out rows with zero population
global_data = global_data[global_data['population'] != 0.0]


def calculate_population(longitude: float, latitude: float, radius: float) -> float:
    """Calculate the total population within a given radius of a point"""
    data = global_data.copy()
    
    # Calculate distance bounds
    lat_distance = radius / 111
    lon_distance = longitude_distance(latitude)
    lon_min = longitude - (radius / lon_distance)
    lon_max = longitude + (radius / lon_distance)
    lat_min = latitude - lat_distance
    lat_max = latitude + lat_distance

    # Filter based on bounding box
    data = data[(data['longitude'] >= lon_min) & (data['longitude'] <= lon_max) &
                (data['latitude'] >= lat_min) & (data['latitude'] <= lat_max)]

    # Convert degrees to radians for vectorized haversine calculation
    lat1_rad = math.radians(latitude)
    lon1_rad = math.radians(longitude)
    data['lat_rad'] = np.radians(data['latitude'])
    data['lon_rad'] = np.radians(data['longitude'])

    # Vectorized haversine distance calculation
    dlat = data['lat_rad'] - lat1_rad
    dlon = data['lon_rad'] - lon1_rad
    a = np.sin(dlat / 2)**2 + np.cos(lat1_rad) * np.cos(data['lat_rad']) * np.sin(dlon / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    data['distance'] = 6371 * c

    # Filter based on radius
    data = data[data['distance'] <= radius]

    # Return population
    return data['population'].sum()

''' old testing code
distance = 80
population1 = (calculate_population(-84.512016, 39.103119, 10))  # Example usage
population2 = (calculate_population(-84.191605, 39.758949, 10))  # Example usage
ridership = (calculate_ridership(population1, population2, distance))
estimated_cost = 30000000*distance
travel_time_value = travel_time(distance)
yearly_cost_value = yearly_cost(distance)
revenue_value = revenue(ridership)
yearly_profit_value = yearly_profit(yearly_cost_value, revenue_value)

print(f"Estimated Construction Cost: ${estimated_cost}")
print(f"Estimated Ridership: {ridership}")
print(f"Travel Time: {travel_time_value} minutes")
print(f"Yearly Cost: ${yearly_cost_value}")
print(f"Yearly Profit: ${yearly_profit_value}")
print(f"Population in radius of 10 km: {population1}")
print(f"Population in radius of 10 km: {population2}")
print(f"Years to profit: {estimated_cost/(yearly_profit_value)}")

print(calculate_ridership(1000000,1000000, 200))

'''