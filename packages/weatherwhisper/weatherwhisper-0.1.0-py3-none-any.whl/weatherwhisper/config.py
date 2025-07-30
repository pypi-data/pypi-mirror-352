import os
import configparser
from pathlib import Path

# Default configuration directory and file
CONFIG_DIR = os.path.expanduser("~/.weatherwhisper")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.ini")

# Default configuration settings
DEFAULT_CONFIG = {
    "api": {
        "key": "",
        "base_url": "https://api.openweathermap.org/data/2.5",
    },
    "display": {
        "units": "metric",
        "format": "brief",
        "color": "true",
        "ascii_art": "true",
    },
    "locations": {
        "favorites": "",
        "cache_time": "3600",  # Cache locations for 1 hour
    },
    "forecast": {
        "days": "5",
    },
}


def ensure_config_exists():
    """Create the configuration directory and file if they don't exist."""
    # Create config directory if it doesn't exist
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    
    # Create config file with default values if it doesn't exist
    if not os.path.exists(CONFIG_FILE):
        config = create_default_config()
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)
        print(f"Created new configuration file at {CONFIG_FILE}")
        
        # Prompt for API key if it's not set
        if not config['api']['key']:
            api_key = input("Please enter your OpenWeatherMap API key: ").strip()
            if api_key:
                config['api']['key'] = api_key
                with open(CONFIG_FILE, 'w') as configfile:
                    config.write(configfile)
                print("API key saved to configuration file")
            else:
                print("No API key provided. You'll need to set it later with 'weatherwhisper config --api-key YOUR_KEY'")
    
    return CONFIG_FILE


def create_default_config():
    """Create a ConfigParser object with default configuration."""
    config = configparser.ConfigParser()
    for section, options in DEFAULT_CONFIG.items():
        config[section] = {}
        for option, value in options.items():
            config[section][option] = value
    return config


def get_config():
    """Read and return the configuration."""
    ensure_config_exists()
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    return config


def update_config(section, option, value):
    """Update a specific configuration option."""
    config = get_config()
    
    # Create section if it doesn't exist
    if section not in config:
        config[section] = {}
    
    # Update the option
    config[section][option] = value
    
    # Write the updated configuration
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)
    
    return config


def get_api_key():
    """Get the API key from the configuration."""
    config = get_config()
    return config['api']['key']


def set_api_key(api_key):
    """Set the API key in the configuration."""
    return update_config('api', 'key', api_key)


def get_default_units():
    """Get the default units from the configuration."""
    config = get_config()
    return config['display']['units']


def set_default_units(units):
    """Set the default units in the configuration."""
    if units not in ['metric', 'imperial']:
        raise ValueError("Units must be either 'metric' or 'imperial'")
    return update_config('display', 'units', units)


def get_default_format():
    """Get the default output format from the configuration."""
    config = get_config()
    return config['display']['format']


def set_default_format(format_type):
    """Set the default output format in the configuration."""
    if format_type not in ['brief', 'detailed', 'json']:
        raise ValueError("Format must be one of: 'brief', 'detailed', 'json'")
    return update_config('display', 'format', format_type)


def add_favorite_location(location):
    """Add a location to favorites."""
    config = get_config()
    favorites = config['locations']['favorites']
    favorites_list = [loc.strip() for loc in favorites.split(',')] if favorites else []
    
    if location not in favorites_list:
        favorites_list.append(location)
        new_favorites = ','.join(favorites_list)
        update_config('locations', 'favorites', new_favorites)
        print(f"Added {location} to favorite locations")
    else:
        print(f"{location} is already in your favorite locations")


def get_favorite_locations():
    """Get the list of favorite locations."""
    config = get_config()
    favorites = config['locations']['favorites']
    return [loc.strip() for loc in favorites.split(',')] if favorites else []


def remove_favorite_location(location):
    """Remove a location from favorites."""
    config = get_config()
    favorites = config['locations']['favorites']
    favorites_list = [loc.strip() for loc in favorites.split(',')] if favorites else []
    
    if location in favorites_list:
        favorites_list.remove(location)
        new_favorites = ','.join(favorites_list)
        update_config('locations', 'favorites', new_favorites)
        print(f"Removed {location} from favorite locations")
    else:
        print(f"{location} is not in your favorite locations")
