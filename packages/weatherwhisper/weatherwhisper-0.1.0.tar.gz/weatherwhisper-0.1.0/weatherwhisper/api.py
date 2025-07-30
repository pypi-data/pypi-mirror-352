import os
import json
import time
import requests
from datetime import datetime, timedelta

from weatherwhisper.config import get_config, get_api_key

# Cache directory for storing API responses
CACHE_DIR = os.path.expanduser("~/.weatherwhisper/cache")
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

class WeatherAPIError(Exception):
    """Exception raised for errors in the OpenWeatherMap API."""
    pass

def _get_cache_file(endpoint, params):
    """Generate a cache file name based on the endpoint and parameters."""
    # Create a string representation of the parameters
    param_str = "_".join(f"{k}_{v}" for k, v in sorted(params.items()) if k != 'appid')
    
    # Create a filename based on the endpoint and parameters
    filename = f"{endpoint}_{param_str}.json"
    
    # Replace any characters that are not valid in filenames
    for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|', ' ']:
        filename = filename.replace(char, '_')
    
    return os.path.join(CACHE_DIR, filename)

def _is_cache_valid(cache_file, cache_time=3600):
    """Check if the cache file exists and is still valid."""
    if not os.path.exists(cache_file):
        return False
    
    # Get the modification time of the cache file
    mod_time = os.path.getmtime(cache_file)
    current_time = time.time()
    
    # Check if the cache is still valid
    return (current_time - mod_time) < cache_time

def _get_from_cache(cache_file):
    """Get data from the cache file."""
    with open(cache_file, 'r') as f:
        return json.load(f)

def _save_to_cache(cache_file, data):
    """Save data to the cache file."""
    with open(cache_file, 'w') as f:
        json.dump(data, f)

def _make_api_request(endpoint, params, cache_time=3600):
    """Make a request to the OpenWeatherMap API with caching."""
    config = get_config()
    base_url = config['api']['base_url']
    api_key = get_api_key()
    
    if not api_key:
        raise WeatherAPIError("No API key found. Please set your OpenWeatherMap API key with 'weatherwhisper config --api-key YOUR_KEY'")
    
    # Add API key to parameters
    params['appid'] = api_key
    
    # Check cache first
    cache_file = _get_cache_file(endpoint, params)
    if _is_cache_valid(cache_file, cache_time):
        return _get_from_cache(cache_file)
    
    # Make the API request
    url = f"{base_url}/{endpoint}"
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Parse the JSON response
        data = response.json()
        
        # Validate the response
        if 'cod' in data and data['cod'] != 200 and str(data['cod']) != '200':
            raise WeatherAPIError(f"API Error: {data.get('message', 'Unknown error')}")
        
        # Save to cache
        _save_to_cache(cache_file, data)
        
        return data
    except requests.exceptions.RequestException as e:
        raise WeatherAPIError(f"Request failed: {str(e)}")
    except json.JSONDecodeError:
        raise WeatherAPIError("Failed to parse API response")

def get_current_weather(location, units='metric'):
    """
    Get current weather for a location.
    
    Args:
        location (str): City name or coordinates
        units (str): Units of measurement ('metric' or 'imperial')
    
    Returns:
        dict: Current weather data
    """
    # Check if location is coordinates (lat,lon) or city name
    if ',' in location and all(part.replace('.', '', 1).replace('-', '', 1).isdigit() 
                              for part in location.split(',')):
        lat, lon = location.split(',')
        params = {
            'lat': lat.strip(),
            'lon': lon.strip(),
            'units': units
        }
    else:
        params = {
            'q': location,
            'units': units
        }
    
    return _make_api_request('weather', params)

def get_weather_forecast(location, units='metric', days=5):
    """
    Get weather forecast for a location.
    
    Args:
        location (str): City name or coordinates
        units (str): Units of measurement ('metric' or 'imperial')
        days (int): Number of days for forecast (max 5)
    
    Returns:
        dict: Forecast weather data
    """
    # Check if location is coordinates (lat,lon) or city name
    if ',' in location and all(part.replace('.', '', 1).replace('-', '', 1).isdigit() 
                              for part in location.split(',')):
        lat, lon = location.split(',')
        params = {
            'lat': lat.strip(),
            'lon': lon.strip(),
            'units': units
        }
    else:
        params = {
            'q': location,
            'units': units
        }
    
    # The free tier of OpenWeatherMap only supports 5-day forecast
    days = min(days, 5)
    
    # Get forecast data
    data = _make_api_request('forecast', params)
    
    # Filter data for the requested number of days
    if 'list' in data:
        current_date = datetime.now().date()
        filtered_list = []
        days_included = set()
        
        for item in data['list']:
            forecast_date = datetime.fromtimestamp(item['dt']).date()
            days_diff = (forecast_date - current_date).days
            
            if days_diff < days and days_diff not in days_included:
                filtered_list.append(item)
                days_included.add(days_diff)
        
        data['list'] = filtered_list
    
    return data

def get_historical_weather(location, date, units='metric'):
    """
    Get historical weather for a location.
    
    Args:
        location (str): City name or coordinates
        date (str): Date in format YYYY-MM-DD
        units (str): Units of measurement ('metric' or 'imperial')
    
    Returns:
        dict: Historical weather data
    
    Note:
        This requires a paid OpenWeatherMap subscription.
    """
    # Convert date string to timestamp
    try:
        dt = datetime.strptime(date, '%Y-%m-%d')
        timestamp = int(dt.timestamp())
    except ValueError:
        raise WeatherAPIError("Invalid date format. Please use YYYY-MM-DD")
    
    # Check if location is coordinates (lat,lon) or city name
    if ',' in location and all(part.replace('.', '', 1).replace('-', '', 1).isdigit() 
                              for part in location.split(',')):
        lat, lon = location.split(',')
        params = {
            'lat': lat.strip(),
            'lon': lon.strip(),
            'dt': timestamp,
            'units': units
        }
    else:
        # Historical data requires coordinates, so first get coordinates from city name
        city_data = get_current_weather(location, units)
        if 'coord' not in city_data:
            raise WeatherAPIError(f"Could not find coordinates for {location}")
        
        params = {
            'lat': city_data['coord']['lat'],
            'lon': city_data['coord']['lon'],
            'dt': timestamp,
            'units': units
        }
    
    try:
        return _make_api_request('onecall/timemachine', params)
    except WeatherAPIError as e:
        if "API Error" in str(e):
            raise WeatherAPIError(
                "Historical data requires a paid OpenWeatherMap subscription. "
                "Please upgrade your API key or use current weather and forecast features."
            )
        raise

def get_air_pollution(location):
    """
    Get air pollution data for a location.
    
    Args:
        location (str): City name or coordinates
    
    Returns:
        dict: Air pollution data
    """
    # Air pollution data requires coordinates
    if ',' in location and all(part.replace('.', '', 1).replace('-', '', 1).isdigit() 
                              for part in location.split(',')):
        lat, lon = location.split(',')
        params = {
            'lat': lat.strip(),
            'lon': lon.strip()
        }
    else:
        # Get coordinates from city name
        city_data = get_current_weather(location)
        if 'coord' not in city_data:
            raise WeatherAPIError(f"Could not find coordinates for {location}")
        
        params = {
            'lat': city_data['coord']['lat'],
            'lon': city_data['coord']['lon']
        }
    
    return _make_api_request('air_pollution', params)

def get_weather_alerts(location, units='metric'):
    """
    Get weather alerts for a location.
    
    Args:
        location (str): City name or coordinates
        units (str): Units of measurement ('metric' or 'imperial')
    
    Returns:
        dict: Weather alerts data
    
    Note:
        This requires the OneCall API which may require a paid subscription.
    """
    # OneCall API requires coordinates
    if ',' in location and all(part.replace('.', '', 1).replace('-', '', 1).isdigit() 
                              for part in location.split(',')):
        lat, lon = location.split(',')
        params = {
            'lat': lat.strip(),
            'lon': lon.strip(),
            'units': units,
            'exclude': 'minutely,hourly'  # Exclude unnecessary data
        }
    else:
        # Get coordinates from city name
        city_data = get_current_weather(location)
        if 'coord' not in city_data:
            raise WeatherAPIError(f"Could not find coordinates for {location}")
        
        params = {
            'lat': city_data['coord']['lat'],
            'lon': city_data['coord']['lon'],
            'units': units,
            'exclude': 'minutely,hourly'  # Exclude unnecessary data
        }
    
    try:
        return _make_api_request('onecall', params)
    except WeatherAPIError as e:
        if "API Error" in str(e):
            raise WeatherAPIError(
                "OneCall API may require a paid OpenWeatherMap subscription. "
                "Please check your API key permissions."
            )
        raise
