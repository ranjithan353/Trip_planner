"""
Weather Tool - Provides weather information for destinations
"""
from typing import Dict, Any
import random
from datetime import datetime


def get_weather_info(destination: str, date: str = None) -> Dict[str, Any]:
    """
    Get weather information for a destination.
    
    Args:
        destination: Name of the destination city
        date: Optional date string (YYYY-MM-DD format)
    
    Returns:
        Dictionary containing weather information
    """
    # Realistic weather data based on destination and season
    destinations_weather = {
        "paris": {"temp": 18, "condition": "Partly Cloudy", "humidity": 65, "wind": "10 km/h"},
        "tokyo": {"temp": 22, "condition": "Sunny", "humidity": 70, "wind": "8 km/h"},
        "new york": {"temp": 15, "condition": "Cloudy", "humidity": 60, "wind": "12 km/h"},
        "london": {"temp": 12, "condition": "Rainy", "humidity": 80, "wind": "15 km/h"},
        "dubai": {"temp": 35, "condition": "Sunny", "humidity": 45, "wind": "5 km/h"},
        "barcelona": {"temp": 20, "condition": "Sunny", "humidity": 55, "wind": "10 km/h"},
        "rome": {"temp": 19, "condition": "Partly Cloudy", "humidity": 65, "wind": "8 km/h"},
        "sydney": {"temp": 24, "condition": "Sunny", "humidity": 68, "wind": "12 km/h"},
        "bangkok": {"temp": 32, "condition": "Partly Cloudy", "humidity": 75, "wind": "6 km/h"},
        "singapore": {"temp": 30, "condition": "Partly Cloudy", "humidity": 80, "wind": "8 km/h"},
    }
    
    # Normalize destination name
    dest_lower = destination.lower().strip()
    
    # Get weather data or use default
    if dest_lower in destinations_weather:
        weather_data = destinations_weather[dest_lower]
    else:
        # Generate realistic weather for unknown destinations
        weather_data = {
            "temp": random.randint(15, 28),
            "condition": random.choice(["Sunny", "Partly Cloudy", "Cloudy", "Rainy"]),
            "humidity": random.randint(50, 80),
            "wind": f"{random.randint(5, 15)} km/h"
        }
    
    result = {
        "destination": destination,
        "temperature": f"{weather_data['temp']}°C",
        "condition": weather_data["condition"],
        "humidity": f"{weather_data['humidity']}%",
        "wind_speed": weather_data.get("wind", "10 km/h"),
        "date": date or datetime.now().strftime("%Y-%m-%d"),
        "recommendation": _get_weather_recommendation(weather_data["condition"], weather_data["temp"])
    }
    
    return result


def _get_weather_recommendation(condition: str, temp: int) -> str:
    """Generate weather-based activity recommendations"""
    if condition == "Rainy":
        return "Indoor activities recommended. Pack an umbrella and waterproof gear."
    elif condition == "Sunny" and temp > 25:
        return "Perfect for outdoor activities! Wear light clothing and use sunscreen."
    elif temp < 10:
        return "Cold weather expected. Dress warmly and consider indoor attractions."
    elif condition == "Cloudy":
        return "Mild weather conditions. Good for both indoor and outdoor activities."
    else:
        return "Pleasant weather conditions ideal for sightseeing and outdoor exploration."
