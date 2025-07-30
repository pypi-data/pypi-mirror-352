import json
import datetime
from colorama import Fore, Back, Style, init

# Initialize colorama
init(autoreset=True)

# ASCII art for different weather conditions
WEATHER_ASCII = {
    # Clear sky
    "01d": """
    \\   /
     .-.
  ― (   ) ―
     `-'
    /   \\
    """,
    "01n": """
      .-.
    ― ( ) ―
       ⁎ 
     ⁎ ⁎ ⁎
    """,
    # Few clouds
    "02d": """
   \\  /
 _ /''.-.
   \\_(   ).
   /(___(__)
    """,
    "02n": """
      .-.
     (   ).
    (___(__)
     ⁎ ⁎ ⁎
    """,
    # Scattered clouds
    "03d": """
     .-.
    (   ).
   (___(__)
    """,
    "03n": """
     .-.
    (   ).
   (___(__)
    """,
    # Broken clouds
    "04d": """
    .-.   .-.
   (   ).(   )
  (___(__)___)
    """,
    "04n": """
    .-.   .-.
   (   ).(   )
  (___(__)___)
    """,
    # Shower rain
    "09d": """
     .-.
    (   ).
   (___(__)
    ' ' ' '
   ' ' ' '
    """,
    "09n": """
     .-.
    (   ).
   (___(__)
    ' ' ' '
   ' ' ' '
    """,
    # Rain
    "10d": """
   \\  /
 _ /''.-.
   \\_(   ).
   /(___(__)
    ' ' ' '
   ' ' ' '
    """,
    "10n": """
     .-.
    (   ).
   (___(__)
    ' ' ' '
   ' ' ' '
    """,
    # Thunderstorm
    "11d": """
     .-.
    (   ).
   (___(__)
    ⚡' '⚡
   ' ' ' '
    """,
    "11n": """
     .-.
    (   ).
   (___(__)
    ⚡' '⚡
   ' ' ' '
    """,
    # Snow
    "13d": """
     .-.
    (   ).
   (___(__)
    * * * *
   * * * *
    """,
    "13n": """
     .-.
    (   ).
   (___(__)
    * * * *
   * * * *
    """,
    # Mist/fog
    "50d": """
    _ - _ - _
     _ - _ - 
    _ - _ - _
    """,
    "50n": """
    _ - _ - _
     _ - _ - 
    _ - _ - _
    """
}

# Default ASCII art for unknown weather conditions
DEFAULT_ASCII = """
    ?????
    ?????
    ?????
    """

def get_temp_color(temp, units="metric"):
    """Return color based on temperature."""
    if units == "metric":
        if temp < 0:
            return Fore.BLUE
        elif temp < 10:
            return Fore.CYAN
        elif temp < 20:
            return Fore.GREEN
        elif temp < 30:
            return Fore.YELLOW
        else:
            return Fore.RED
    else:  # imperial
        if temp < 32:
            return Fore.BLUE
        elif temp < 50:
            return Fore.CYAN
        elif temp < 68:
            return Fore.GREEN
        elif temp < 86:
            return Fore.YELLOW
        else:
            return Fore.RED

def get_condition_color(condition):
    """Return color based on weather condition."""
    condition = condition.lower()
    if "clear" in condition:
        return Fore.YELLOW
    elif "sun" in condition:
        return Fore.YELLOW
    elif "cloud" in condition:
        return Fore.WHITE
    elif "rain" in condition or "drizzle" in condition:
        return Fore.CYAN
    elif "snow" in condition:
        return Fore.WHITE + Style.BRIGHT
    elif "storm" in condition or "thunder" in condition:
        return Fore.MAGENTA
    elif "fog" in condition or "mist" in condition or "haze" in condition:
        return Fore.WHITE + Style.DIM
    else:
        return Fore.WHITE

def get_ascii_art(icon_code):
    """Get ASCII art for weather condition icon code."""
    return WEATHER_ASCII.get(icon_code, DEFAULT_ASCII)

def format_wind_direction(degrees):
    """Convert wind direction in degrees to cardinal direction."""
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", 
                  "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    index = round(degrees / 22.5) % 16
    return directions[index]

def format_time(timestamp, timezone=0):
    """Format Unix timestamp to readable time."""
    dt = datetime.datetime.fromtimestamp(timestamp + timezone)
    return dt.strftime("%H:%M:%S")

def format_date(timestamp, timezone=0):
    """Format Unix timestamp to readable date."""
    dt = datetime.datetime.fromtimestamp(timestamp + timezone)
    return dt.strftime("%Y-%m-%d")

def format_datetime(timestamp, timezone=0):
    """Format Unix timestamp to readable date and time."""
    dt = datetime.datetime.fromtimestamp(timestamp + timezone)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def format_brief(weather_data, units="metric", use_color=True, use_ascii=True):
    """
    Format weather data in brief format.
    
    Args:
        weather_data (dict): Weather data from OpenWeatherMap API
        units (str): Units of measurement ('metric' or 'imperial')
        use_color (bool): Whether to use colored output
        use_ascii (bool): Whether to include ASCII art
    
    Returns:
        str: Formatted weather data
    """
    if not weather_data:
        return "No weather data available."
    
    # Extract data
    location = weather_data.get("name", "Unknown")
    country = weather_data.get("sys", {}).get("country", "")
    
    if "main" not in weather_data:
        return f"No weather data available for {location}, {country}."
    
    main_data = weather_data["main"]
    temp = main_data.get("temp", "N/A")
    feels_like = main_data.get("feels_like", "N/A")
    
    weather_cond = weather_data.get("weather", [{}])[0]
    condition = weather_cond.get("main", "Unknown")
    description = weather_cond.get("description", "").capitalize()
    icon = weather_cond.get("icon", "")
    
    # Format temperature with appropriate unit
    temp_unit = "°C" if units == "metric" else "°F"
    
    # Apply colors if enabled
    if use_color:
        temp_str = f"{get_temp_color(temp)}{temp}{temp_unit}{Style.RESET_ALL}"
        feels_like_str = f"{get_temp_color(feels_like)}{feels_like}{temp_unit}{Style.RESET_ALL}"
        condition_str = f"{get_condition_color(condition)}{description}{Style.RESET_ALL}"
    else:
        temp_str = f"{temp}{temp_unit}"
        feels_like_str = f"{feels_like}{temp_unit}"
        condition_str = description
    
    # Build output
    output = []
    output.append(f"{Fore.CYAN if use_color else ''}Weather for {location}, {country}{Style.RESET_ALL if use_color else ''}")
    output.append(f"Temperature: {temp_str} (Feels like: {feels_like_str})")
    output.append(f"Condition: {condition_str}")
    
    # Add ASCII art if enabled
    if use_ascii and icon:
        ascii_art = get_ascii_art(icon)
        if use_color:
            ascii_art = f"{get_condition_color(condition)}{ascii_art}{Style.RESET_ALL}"
        output.append(ascii_art)
    
    return "\n".join(output)

def format_detailed(weather_data, units="metric", use_color=True, use_ascii=True):
    """
    Format weather data in detailed format.
    
    Args:
        weather_data (dict): Weather data from OpenWeatherMap API
        units (str): Units of measurement ('metric' or 'imperial')
        use_color (bool): Whether to use colored output
        use_ascii (bool): Whether to include ASCII art
    
    Returns:
        str: Formatted weather data
    """
    if not weather_data:
        return "No weather data available."
    
    # Extract data
    location = weather_data.get("name", "Unknown")
    country = weather_data.get("sys", {}).get("country", "")
    
    if "main" not in weather_data:
        return f"No weather data available for {location}, {country}."
    
    main_data = weather_data["main"]
    temp = main_data.get("temp", "N/A")
    feels_like = main_data.get("feels_like", "N/A")
    temp_min = main_data.get("temp_min", "N/A")
    temp_max = main_data.get("temp_max", "N/A")
    pressure = main_data.get("pressure", "N/A")
    humidity = main_data.get("humidity", "N/A")
    
    weather_cond = weather_data.get("weather", [{}])[0]
    condition = weather_cond.get("main", "Unknown")
    description = weather_cond.get("description", "").capitalize()
    icon = weather_cond.get("icon", "")
    
    wind_data = weather_data.get("wind", {})
    wind_speed = wind_data.get("speed", "N/A")
    wind_deg = wind_data.get("deg", "N/A")
    wind_dir = format_wind_direction(wind_deg) if isinstance(wind_deg, (int, float)) else "N/A"
    
    clouds = weather_data.get("clouds", {}).get("all", "N/A")
    visibility = weather_data.get("visibility", "N/A")
    
    sys_data = weather_data.get("sys", {})
    sunrise = sys_data.get("sunrise", "N/A")
    sunset = sys_data.get("sunset", "N/A")
    
    timezone = weather_data.get("timezone", 0)
    
    # Format units
    temp_unit = "°C" if units == "metric" else "°F"
    speed_unit = "m/s" if units == "metric" else "mph"
    
    # Apply colors if enabled
    if use_color:
        temp_str = f"{get_temp_color(temp)}{temp}{temp_unit}{Style.RESET_ALL}"
        feels_like_str = f"{get_temp_color(feels_like)}{feels_like}{temp_unit}{Style.RESET_ALL}"
        temp_min_str = f"{get_temp_color(temp_min)}{temp_min}{temp_unit}{Style.RESET_ALL}"
        temp_max_str = f"{get_temp_color(temp_max)}{temp_max}{temp_unit}{Style.RESET_ALL}"
        condition_str = f"{get_condition_color(condition)}{description}{Style.RESET_ALL}"
    else:
        temp_str = f"{temp}{temp_unit}"
        feels_like_str = f"{feels_like}{temp_unit}"
        temp_min_str = f"{temp_min}{temp_unit}"
        temp_max_str = f"{temp_max}{temp_unit}"
        condition_str = description
    
    # Format sunrise and sunset
    if isinstance(sunrise, (int, float)):
        sunrise_str = format_time(sunrise, timezone)
    else:
        sunrise_str = "N/A"
        
    if isinstance(sunset, (int, float)):
        sunset_str = format_time(sunset, timezone)
    else:
        sunset_str = "N/A"
    
    # Format visibility
    if isinstance(visibility, (int, float)):
        visibility_km = visibility / 1000
        visibility_str = f"{visibility_km:.1f} km"
    else:
        visibility_str = "N/A"
    
    # Build output
    output = []
    output.append(f"{Fore.CYAN if use_color else ''}Weather for {location}, {country}{Style.RESET_ALL if use_color else ''}")
    output.append(f"{Fore.YELLOW if use_color else ''}Date: {format_date(weather_data.get('dt', time.time()), timezone)}{Style.RESET_ALL if use_color else ''}")
    output.append("")
    
    # Add ASCII art if enabled
    if use_ascii and icon:
        ascii_art = get_ascii_art(icon)
        if use_color:
            ascii_art = f"{get_condition_color(condition)}{ascii_art}{Style.RESET_ALL}"
        output.append(ascii_art)
    
    output.append(f"Condition: {condition_str}")
    output.append("")
    output.append(f"Temperature: {temp_str}")
    output.append(f"Feels like: {feels_like_str}")
    output.append(f"Min/Max: {temp_min_str} / {temp_max_str}")
    output.append("")
    output.append(f"Humidity: {humidity}%")
    output.append(f"Pressure: {pressure} hPa")
    output.append(f"Visibility: {visibility_str}")
    output.append(f"Cloudiness: {clouds}%")
    output.append("")
    output.append(f"Wind: {wind_speed} {speed_unit} {wind_dir}")
    output.append("")
    output.append(f"Sunrise: {sunrise_str}")
    output.append(f"Sunset: {sunset_str}")
    
    return "\n".join(output)

def format_forecast(forecast_data, units="metric", use_color=True, use_ascii=True):
    """
    Format forecast data.
    
    Args:
        forecast_data (dict): Forecast data from OpenWeatherMap API
        units (str): Units of measurement ('metric' or 'imperial')
        use_color (bool): Whether to use colored output
        use_ascii (bool): Whether to include ASCII art
    
    Returns:
        str: Formatted forecast data
    """
    if not forecast_data or "list" not in forecast_data:
        return "No forecast data available."
    
    city = forecast_data.get("city", {})
    location = city.get("name", "Unknown")
    country = city.get("country", "")
    timezone = city.get("timezone", 0)
    
    temp_unit = "°C" if units == "metric" else "°F"
    speed_unit = "m/s" if units == "metric" else "mph"
    
    # Build output
    output = []
    output.append(f"{Fore.CYAN if use_color else ''}5-day Forecast for {location}, {country}{Style.RESET_ALL if use_color else ''}")
    output.append("")
    
    # Group forecast by day
    forecast_by_day = {}
    for item in forecast_data["list"]:
        dt = datetime.datetime.fromtimestamp(item["dt"] + timezone)
        day = dt.strftime("%Y-%m-%d")
        
        if day not in forecast_by_day:
            forecast_by_day[day] = []
        
        forecast_by_day[day].append(item)
    
    # Process each day
    for day, items in forecast_by_day.items():
        # Get day of week
        dt = datetime.datetime.strptime(day, "%Y-%m-%d")
        day_of_week = dt.strftime("%A")
        
        output.append(f"{Fore.YELLOW if use_color else ''}{day_of_week} ({day}){Style.RESET_ALL if use_color else ''}")
        
        # Get daily summary
        temps = [item["main"]["temp"] for item in items]
        min_temp = min(temps)
        max_temp = max(temps)
        
        # Get most common weather condition
        conditions = {}
        for item in items:
            cond = item["weather"][0]["main"]
            if cond not in conditions:
                conditions[cond] = 0
            conditions[cond] += 1
        
        most_common_condition = max(conditions.items(), key=lambda x: x[1])[0]
        
        # Get icon for most common condition
        icon = next((item["weather"][0]["icon"] for item in items 
                    if item["weather"][0]["main"] == most_common_condition), "")
        
        # Apply colors
        if use_color:
            min_temp_str = f"{get_temp_color(min_temp)}{min_temp}{temp_unit}{Style.RESET_ALL}"
            max_temp_str = f"{get_temp_color(max_temp)}{max_temp}{temp_unit}{Style.RESET_ALL}"
            condition_str = f"{get_condition_color(most_common_condition)}{most_common_condition}{Style.RESET_ALL}"
        else:
            min_temp_str = f"{min_temp}{temp_unit}"
            max_temp_str = f"{max_temp}{temp_unit}"
            condition_str = most_common_condition
        
        # Add ASCII art if enabled
        if use_ascii and icon:
            ascii_art = get_ascii_art(icon)
            if use_color:
                ascii_art = f"{get_condition_color(most_common_condition)}{ascii_art}{Style.RESET_ALL}"
            output.append(ascii_art)
        
        output.append(f"Condition: {condition_str}")
        output.append(f"Temperature: {min_temp_str} to {max_temp_str}")
        
        # Add hourly details
        output.append("Hourly:")
        for item in items:
            dt = datetime.datetime.fromtimestamp(item["dt"] + timezone)
            hour = dt.strftime("%H:%M")
            temp = item["main"]["temp"]
            cond = item["weather"][0]["description"].capitalize()
            
            if use_color:
                temp_str = f"{get_temp_color(temp)}{temp}{temp_unit}{Style.RESET_ALL}"
                cond_str = f"{get_condition_color(cond)}{cond}{Style.RESET_ALL}"
            else:
                temp_str = f"{temp}{temp_unit}"
                cond_str = cond
            
            output.append(f"  {hour}: {temp_str}, {cond_str}")
        
        output.append("")
    
    return "\n".join(output)

def format_json(data):
    """
    Format data as JSON.
    
    Args:
        data (dict): Weather data
    
    Returns:
        str: JSON-formatted data
    """
    return json.dumps(data, indent=2)

def format_weather(data, format_type="brief", units="metric", use_color=True, use_ascii=True):
    """
    Format weather data according to the specified format.
    
    Args:
        data (dict): Weather data
        format_type (str): Format type ('brief', 'detailed', 'json')
        units (str): Units of measurement ('metric' or 'imperial')
        use_color (bool): Whether to use colored output
        use_ascii (bool): Whether to include ASCII art
    
    Returns:
        str: Formatted weather data
    """
    if format_type == "json":
        return format_json(data)
    elif format_type == "detailed":
        return format_detailed(data, units, use_color, use_ascii)
    elif format_type == "forecast" and "list" in data:
        return format_forecast(data, units, use_color, use_ascii)
    else:  # brief is the default
        return format_brief(data, units, use_color, use_ascii)
