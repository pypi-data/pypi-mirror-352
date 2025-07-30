import os
import sys
import click
from colorama import Fore, Style, init

from weatherwhisper import __version__
from weatherwhisper.api import (
    get_current_weather, get_weather_forecast, get_historical_weather,
    get_air_pollution, get_weather_alerts, WeatherAPIError
)
from weatherwhisper.formatter import format_weather
from weatherwhisper.config import (
    ensure_config_exists, get_config, update_config, get_api_key, set_api_key,
    get_default_units, set_default_units, get_default_format, set_default_format,
    add_favorite_location, get_favorite_locations, remove_favorite_location
)

# Initialize colorama
init(autoreset=True)

# Common options for weather commands
def common_options(f):
    """Common options for weather commands."""
    f = click.option('--units', '-u', type=click.Choice(['metric', 'imperial']), 
                    help='Units of measurement (metric or imperial)')(f)
    f = click.option('--format', '-f', type=click.Choice(['brief', 'detailed', 'json']), 
                    help='Output format (brief, detailed, or json)')(f)
    f = click.option('--no-color', is_flag=True, help='Disable colored output')(f)
    f = click.option('--no-ascii', is_flag=True, help='Disable ASCII art in output')(f)
    return f

@click.group()
@click.version_option(version=__version__)
def cli():
    """WeatherWhisper - A command-line tool for fetching and displaying weather information."""
    # Ensure config exists
    ensure_config_exists()
    
    # Check if API key is set
    config = get_config()
    if not config['api']['key']:
        click.echo(f"{Fore.YELLOW}Warning: No API key set. Use 'weatherwhisper config --api-key YOUR_KEY' to set it.{Style.RESET_ALL}")
        click.echo(f"You can get a free API key from https://openweathermap.org/api")

@cli.command()
@click.argument('location', required=False)
@common_options
def current(location, units, format, no_color, no_ascii):
    """
    Get current weather for a location.
    
    If no location is provided, it will use your favorite location if set.
    """
    # Use defaults from config if not specified
    config = get_config()
    if not units:
        units = config['display']['units']
    if not format:
        format = config['display']['format']
    
    # Use color and ASCII art based on config and options
    use_color = config['display'].getboolean('color') and not no_color
    use_ascii = config['display'].getboolean('ascii_art') and not no_ascii
    
    # If no location provided, use first favorite location
    if not location:
        favorites = get_favorite_locations()
        if favorites:
            location = favorites[0]
            click.echo(f"Using favorite location: {location}")
        else:
            click.echo(f"{Fore.RED}Error: No location provided and no favorite locations set.{Style.RESET_ALL}")
            click.echo("Use 'weatherwhisper current LOCATION' or add a favorite location with 'weatherwhisper favorites --add LOCATION'")
            sys.exit(1)
    
    try:
        # Get weather data
        weather_data = get_current_weather(location, units)
        
        # Format and display weather data
        formatted_output = format_weather(weather_data, format, units, use_color, use_ascii)
        click.echo(formatted_output)
    except WeatherAPIError as e:
        click.echo(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

@cli.command()
@click.argument('location', required=False)
@click.option('--days', '-d', type=int, default=5, help='Number of days for forecast (max 5)')
@common_options
def forecast(location, days, units, format, no_color, no_ascii):
    """
    Get weather forecast for a location.
    
    If no location is provided, it will use your favorite location if set.
    """
    # Use defaults from config if not specified
    config = get_config()
    if not units:
        units = config['display']['units']
    if not format:
        format = "forecast"  # Always use forecast format for forecast command
    
    # Use color and ASCII art based on config and options
    use_color = config['display'].getboolean('color') and not no_color
    use_ascii = config['display'].getboolean('ascii_art') and not no_ascii
    
    # If no location provided, use first favorite location
    if not location:
        favorites = get_favorite_locations()
        if favorites:
            location = favorites[0]
            click.echo(f"Using favorite location: {location}")
        else:
            click.echo(f"{Fore.RED}Error: No location provided and no favorite locations set.{Style.RESET_ALL}")
            click.echo("Use 'weatherwhisper forecast LOCATION' or add a favorite location with 'weatherwhisper favorites --add LOCATION'")
            sys.exit(1)
    
    try:
        # Get forecast data
        forecast_data = get_weather_forecast(location, units, days)
        
        # Format and display forecast data
        formatted_output = format_weather(forecast_data, format, units, use_color, use_ascii)
        click.echo(formatted_output)
    except WeatherAPIError as e:
        click.echo(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

@cli.command()
@click.argument('location', required=False)
@common_options
def pollution(location, units, format, no_color, no_ascii):
    """
    Get air pollution data for a location.
    
    If no location is provided, it will use your favorite location if set.
    """
    # If no location provided, use first favorite location
    if not location:
        favorites = get_favorite_locations()
        if favorites:
            location = favorites[0]
            click.echo(f"Using favorite location: {location}")
        else:
            click.echo(f"{Fore.RED}Error: No location provided and no favorite locations set.{Style.RESET_ALL}")
            click.echo("Use 'weatherwhisper pollution LOCATION' or add a favorite location with 'weatherwhisper favorites --add LOCATION'")
            sys.exit(1)
    
    try:
        # Get pollution data
        pollution_data = get_air_pollution(location)
        
        # Format and display pollution data
        if format == "json":
            formatted_output = format_weather(pollution_data, "json", units, False, False)
        else:
            # Simple display for pollution data
            components = pollution_data.get("list", [{}])[0].get("components", {})
            aqi = pollution_data.get("list", [{}])[0].get("main", {}).get("aqi", 0)
            
            aqi_labels = ["Good", "Fair", "Moderate", "Poor", "Very Poor"]
            aqi_colors = [Fore.GREEN, Fore.CYAN, Fore.YELLOW, Fore.RED, Fore.MAGENTA]
            
            click.echo(f"Air Pollution for {location}:")
            click.echo(f"Air Quality Index: {aqi_colors[aqi-1] if not no_color and aqi > 0 else ''}{aqi} - {aqi_labels[aqi-1] if aqi > 0 else 'Unknown'}{Style.RESET_ALL if not no_color else ''}")
            click.echo("\nPollutants (μg/m³):")
            for name, value in components.items():
                click.echo(f"  {name}: {value}")
        
    except WeatherAPIError as e:
        click.echo(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

@cli.command()
@click.argument('location', required=False)
@click.option('--date', '-d', help='Date for historical data (YYYY-MM-DD)')
@common_options
def historical(location, date, units, format, no_color, no_ascii):
    """
    Get historical weather data for a location.
    
    Note: This requires a paid OpenWeatherMap subscription.
    """
    # Use defaults from config if not specified
    config = get_config()
    if not units:
        units = config['display']['units']
    
    # If no location provided, use first favorite location
    if not location:
        favorites = get_favorite_locations()
        if favorites:
            location = favorites[0]
            click.echo(f"Using favorite location: {location}")
        else:
            click.echo(f"{Fore.RED}Error: No location provided and no favorite locations set.{Style.RESET_ALL}")
            click.echo("Use 'weatherwhisper historical LOCATION --date DATE' or add a favorite location")
            sys.exit(1)
    
    # Check if date is provided
    if not date:
        click.echo(f"{Fore.RED}Error: No date provided.{Style.RESET_ALL}")
        click.echo("Use 'weatherwhisper historical LOCATION --date YYYY-MM-DD'")
        sys.exit(1)
    
    try:
        # Get historical data
        historical_data = get_historical_weather(location, date, units)
        
        # Format and display historical data
        formatted_output = format_weather(historical_data, format or "detailed", units, 
                                         not no_color, not no_ascii)
        click.echo(formatted_output)
    except WeatherAPIError as e:
        click.echo(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

@cli.command()
@click.argument('location', required=False)
@common_options
def alerts(location, units, format, no_color, no_ascii):
    """
    Get weather alerts for a location.
    
    Note: This may require a paid OpenWeatherMap subscription.
    """
    # Use defaults from config if not specified
    config = get_config()
    if not units:
        units = config['display']['units']
    
    # If no location provided, use first favorite location
    if not location:
        favorites = get_favorite_locations()
        if favorites:
            location = favorites[0]
            click.echo(f"Using favorite location: {location}")
        else:
            click.echo(f"{Fore.RED}Error: No location provided and no favorite locations set.{Style.RESET_ALL}")
            click.echo("Use 'weatherwhisper alerts LOCATION' or add a favorite location")
            sys.exit(1)
    
    try:
        # Get alerts data
        alerts_data = get_weather_alerts(location, units)
        
        # Format and display alerts
        if format == "json":
            formatted_output = format_weather(alerts_data, "json", units, False, False)
            click.echo(formatted_output)
        else:
            # Extract and display alerts
            alerts = alerts_data.get("alerts", [])
            if not alerts:
                click.echo(f"No weather alerts for {location}")
            else:
                click.echo(f"{Fore.YELLOW if not no_color else ''}Weather Alerts for {location}:{Style.RESET_ALL if not no_color else ''}")
                for i, alert in enumerate(alerts, 1):
                    click.echo(f"\n{Fore.RED if not no_color else ''}Alert {i}:{Style.RESET_ALL if not no_color else ''}")
                    click.echo(f"Event: {alert.get('event', 'Unknown')}")
                    click.echo(f"Source: {alert.get('sender_name', 'Unknown')}")
                    click.echo(f"Description: {alert.get('description', 'No description available')}")
                    
                    # Format start and end times
                    start = alert.get('start', 0)
                    end = alert.get('end', 0)
                    if start and end:
                        from datetime import datetime
                        start_time = datetime.fromtimestamp(start).strftime('%Y-%m-%d %H:%M:%S')
                        end_time = datetime.fromtimestamp(end).strftime('%Y-%m-%d %H:%M:%S')
                        click.echo(f"Valid: {start_time} to {end_time}")
    
    except WeatherAPIError as e:
        click.echo(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

@cli.group()
def config():
    """Manage WeatherWhisper configuration."""
    pass

@config.command('show')
def config_show():
    """Show current configuration."""
    config = get_config()
    
    click.echo(f"{Fore.CYAN}WeatherWhisper Configuration:{Style.RESET_ALL}")
    for section in config.sections():
        click.echo(f"\n[{section}]")
        for key, value in config[section].items():
            # Don't show the API key directly
            if section == 'api' and key == 'key':
                if value:
                    masked_key = value[:4] + '*' * (len(value) - 8) + value[-4:] if len(value) > 8 else '****'
                    click.echo(f"  {key} = {masked_key}")
                else:
                    click.echo(f"  {key} = {Fore.YELLOW}Not set{Style.RESET_ALL}")
            else:
                click.echo(f"  {key} = {value}")

@config.command('set')
@click.option('--api-key', help='Set the OpenWeatherMap API key')
@click.option('--units', type=click.Choice(['metric', 'imperial']), help='Set default units')
@click.option('--format', type=click.Choice(['brief', 'detailed', 'json']), help='Set default output format')
@click.option('--color/--no-color', default=None, help='Enable/disable colored output')
@click.option('--ascii/--no-ascii', default=None, help='Enable/disable ASCII art')
def config_set(api_key, units, format, color, ascii):
    """Set configuration options."""
    if api_key:
        set_api_key(api_key)
        click.echo(f"API key updated")
    
    if units:
        set_default_units(units)
        click.echo(f"Default units set to {units}")
    
    if format:
        set_default_format(format)
        click.echo(f"Default format set to {format}")
    
    if color is not None:
        update_config('display', 'color', 'true' if color else 'false')
        click.echo(f"Colored output {'enabled' if color else 'disabled'}")
    
    if ascii is not None:
        update_config('display', 'ascii_art', 'true' if ascii else 'false')
        click.echo(f"ASCII art {'enabled' if ascii else 'disabled'}")
    
    if not any([api_key, units, format, color is not None, ascii is not None]):
        click.echo("No configuration options provided. Use --help to see available options.")

@cli.group()
def favorites():
    """Manage favorite locations."""
    pass

@favorites.command('list')
def favorites_list():
    """List favorite locations."""
    favorites = get_favorite_locations()
    
    if not favorites:
        click.echo("No favorite locations set")
    else:
        click.echo(f"{Fore.CYAN}Favorite Locations:{Style.RESET_ALL}")
        for i, location in enumerate(favorites, 1):
            click.echo(f"{i}. {location}")

@favorites.command('add')
@click.argument('location')
def favorites_add(location):
    """Add a location to favorites."""
    # Validate location by trying to get weather for it
    try:
        get_current_weather(location)
        add_favorite_location(location)
    except WeatherAPIError as e:
        click.echo(f"{Fore.RED}Error: Could not add location. {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

@favorites.command('remove')
@click.argument('location')
def favorites_remove(location):
    """Remove a location from favorites."""
    remove_favorite_location(location)

def main():
    """Entry point for the CLI."""
    try:
        cli()
    except Exception as e:
        click.echo(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == '__main__':
    main()
