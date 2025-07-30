import streamlit as st
from geopy.geocoders import Nominatim

# Initialize the geolocator
geolocator = Nominatim(user_agent="transport_optimization_app_20")

def get_coordinates(location_name, location_cache):
    """
    Get the coordinates of a location using geopy, with caching for performance.

    Args:
        location_name (str): Name of the location.

    Returns:
        tuple: Latitude and longitude of the location.
    """
    if location_name in location_cache:
        return location_cache[location_name]
    try:
        location = geolocator.geocode(location_name, timeout=10)
        if location:
            coordinates = (location.latitude, location.longitude)
            if location.latitude is None or location.longitude is None:
                return (0, 0)
            location_cache[location_name] = coordinates
            return coordinates
        else:
            return (0, 0)
    except Exception as e:
        st.error(f"Error fetching coordinates for {location_name}: {e}")
        return (0, 0)