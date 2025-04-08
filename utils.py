# libraries
import http.client
import json
from typing import Union, Dict
import logging
import urllib.parse
import os
import math
from dotenv import load_dotenv # only for debugging

logger = logging.getLogger(__name__)

def calculate_population_from_api(city: str, api_key: str): 
    """Calculate population using API Ninjas"""
    encoded_city = urllib.parse.quote(city)

    conn = http.client.HTTPSConnection("api.api-ninjas.com")

    headers = { 'x-api-key': api_key }

    conn.request("GET", "/v1/city?name=" + encoded_city, headers=headers)

    res = conn.getresponse()
    
    data = json.loads(res.read().decode("utf-8"))

    population = data[0]["population"]

    return population

def calculate_distance(origin: str, destination: str, api_key: str) -> Union[float, str]:
    """Calculate road distance in km using Google Distance Matrix API"""
    if not api_key:
        logger.error("API key is missing")
        return "Error: Google API key is not configured"

    try:
        # URL encode the parameters
        encoded_origin = urllib.parse.quote(origin)
        encoded_destination = urllib.parse.quote(destination)

        conn = http.client.HTTPSConnection("maps.googleapis.com")

        path = f"/maps/api/distancematrix/json?destinations={encoded_destination}&origins={encoded_origin}&mode=driving&units=imperial&key={api_key}"

        conn.request("GET", path)
        response = conn.getresponse()
        data = json.loads(response.read().decode("utf-8"))

        if data.get("status") != "OK":
            error_message = data.get("error_message", data.get("status", "Unknown error"))
            logger.error(f"API Error: {error_message}")
            if "REQUEST_DENIED" in str(error_message):
                return "Error: API key is invalid or not properly configured. Please ensure the Distance Matrix API is enabled and billing is set up."
            return f"API Error: {error_message}"

        if data["rows"][0]["elements"][0]["status"] != "OK":
            logger.error("Could not calculate distance between these locations")
            return "Could not calculate distance between these locations"

        # Distance in meters (convert to kilometers)
        distance_text = data["rows"][0]["elements"][0]["distance"]["text"]
        # Extract numeric value and convert to kilometers if in miles
        # Remove commas from the number and convert to float
        distance_value = float(distance_text.split()[0].replace(',', ''))
        if "mi" in distance_text:
            distance_value = distance_value * 1.60934  # Convert miles to kilometers

        return round(distance_value)

    except Exception as e:
        logger.error(f"Error calculating distance: {str(e)}")
        return f"Error calculating distance: {str(e)}"
    finally:
        if 'conn' in locals():
            conn.close()

def calculate_ridership(populationA: float, populationB: float, distance: float, mode_share: float = 1.0) -> float:
    """
    Calculates ridership between two cities given their population and distance (km)

    Equation derived from: https://pedestrianobservations.com/2021/04/25/sanity-checking-my-hsr-ridership-model/

    equation modified to be calibrated with US rail data
    """
    distance_modifier = 2
    base_factor = 11.67
    population_scaling = 0.8
    return round(mode_share * base_factor * (populationA)**population_scaling * (populationB)**population_scaling / min(distance,500)**distance_modifier)

def calculate_travel_time(distance: float, accel: float = 3000, max_speed: float = 250) -> float:
    """Calculate travel time in minutes based on Shinkansen acceleration. Units in km/h and km."""
    # if train will not hit max speed
    if distance < ( (max_speed**2) / (accel) ):
        time = math.sqrt(distance / (accel)) * 2
        return round(time)
    # derived from standard kinematics equations
    time = max_speed / accel + distance / max_speed
    time = time * 60  # Convert to minutes
    return round(time)

def estimate_cost(road_distance: float, cost_per_km: float = 1443750) -> float:
    """
    Calculate estimated cost based on road distance in km
    
    https://compassinternational.net/railroad-engineering-construction-cost-benchmarks/    
    """
    estimated_cost = cost_per_km*road_distance
    return round(estimated_cost, 2)

def calculate_yearly_cost(distance: float, cost_per_km: float = 630_000) -> float:
    """Calculate yearly cost based on distance and cost per km, default is 630,000$/km"""
    return distance * cost_per_km

def calculate_revenue(ridership: float, ticket_price: float = 80.0) -> float:
    """Calculate revenue based on ridership and ticket price, default price is 80 ($)"""
    return ridership * ticket_price

def calculate_yearly_profit(yearly_cost_value: float, yearly_revenue_value: float) -> float:
    """Calculate yearly profit based on yearly cost and revenue"""
    return yearly_revenue_value - yearly_cost_value

def calculate_years_to_profit(estimated_cost: float, yearly_profit_value: float) -> float:
    """Calculate the number of years to profit based on estimated cost and yearly profit"""
    return round(estimated_cost / yearly_profit_value, 1)

def calculate_railway_metrics(city1: str, city2: str) -> Dict[str, float]:
    populationA = calculate_population_from_api(city1, os.getenv("NINJAS_API_KEY"))
    populationB = calculate_population_from_api(city2, os.getenv("NINJAS_API_KEY"))
    distance = calculate_distance(city1, city2, os.getenv("GOOGLE_MAPS_API_KEY"))
    ridership = calculate_ridership(populationA, populationB, distance)
    travel_time = calculate_travel_time(distance)
    estimated_cost = estimate_cost(distance)
    yearly_cost = calculate_yearly_cost(distance)
    revenue = calculate_revenue(ridership)
    yearly_profit = calculate_yearly_profit(yearly_cost, revenue)
    years_to_profit = calculate_years_to_profit(estimated_cost, yearly_profit)

    return {
        "populationA": populationA,
        "populationB": populationB,
        "road_distance": distance,
        "ridership": ridership,
        "travel_time": travel_time,
        "estimated_cost": estimated_cost,
        "yearly_cost": yearly_cost,
        "revenue": revenue,
        "profit": yearly_profit,
        "years_to_even": years_to_profit,
    }


load_dotenv()
if(False):
    population1 = calculate_population_from_api("Cincinnati", os.getenv("NINJAS_API_KEY"))
    population2 = calculate_population_from_api("Columbus", os.getenv("NINJAS_API_KEY"))
else:
    population1 = 2000000
    population2 = 2000000
if(False): 
    distance = calculate_distance("Cincinnati", "Columbus", os.getenv("GOOGLE_MAPS_API_KEY"))
else:
    distance = 200
railway_metrics = estimate_cost(distance)
ridership = calculate_ridership(population1, population2, distance)
revenue_value = calculate_revenue(ridership)
travel_time_value = calculate_travel_time(distance)
yearly_cost_value = calculate_yearly_cost(distance)
yearly_profit_value = calculate_yearly_profit(yearly_cost_value, revenue_value)
years_to_profit_value = calculate_years_to_profit(railway_metrics, yearly_profit_value)

print(f"Population of Cincinnati: {population1}")
print(f"Population of Columbus: {population2}")
print(f"Distance between Cincinnati and Columbus: {distance} km")
print(f"Railway Metrics: {railway_metrics}")
print(f"Estimated Ridership: {ridership}")
print(f"Revenue: ${revenue_value}")
print(f"Travel Time: {travel_time_value} minutes")
print(f"Yearly Cost: ${yearly_cost_value}")
print(f"Yearly Profit: ${yearly_profit_value}")
print(f"Years to Profit: {years_to_profit_value}")