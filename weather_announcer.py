import os
import requests
from datetime import datetime
from asterisk.ami import AMIClient, SimpleAction
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Weather Underground API configuration
WU_API_KEY = os.getenv('WU_API_KEY')
WU_STATION_ID = os.getenv('WU_STATION_ID')  # Your local weather station ID

# AllStar Link configuration
ASTERISK_HOST = os.getenv('ASTERISK_HOST', 'localhost')
ASTERISK_PORT = int(os.getenv('ASTERISK_PORT', '5038'))
ASTERISK_USER = os.getenv('ASTERISK_USER')
ASTERISK_SECRET = os.getenv('ASTERISK_SECRET')
ALLSTAR_NODE = os.getenv('ALLSTAR_NODE')  # Your AllStar node number

def get_weather_data():
    """Get weather data from Weather Underground API."""
    if not WU_API_KEY or not WU_STATION_ID:
        print("Error: WU_API_KEY or WU_STATION_ID not set in .env file")
        return None

    # Using the correct API endpoint for Weather Underground
    url = "https://api.weather.com/v2/pws/observations/current"
    params = {
        'stationId': WU_STATION_ID,
        'format': 'json',
        'units': 'm',
        'apiKey': WU_API_KEY,
        'numericPrecision': 'decimal'
    }
    
    try:
        print(f"Requesting weather data from station: {WU_STATION_ID}")
        print(f"Using API key: {WU_API_KEY[:8]}...")  # Only show first 8 characters for security
        response = requests.get(url, params=params)
        
        # Print the full URL for debugging (without the API key)
        debug_url = url + "?" + "&".join([f"{k}={v}" for k, v in params.items() if k != 'apiKey'])
        print(f"Request URL: {debug_url}")
        
        response.raise_for_status()
        data = response.json()
        
        # Debug: Print the response structure
        print("API Response received. Checking data structure...")
        
        if 'observations' not in data or not data['observations']:
            print("Error: No observations found in API response")
            print("API Response:", data)
            return None
            
        obs = data['observations'][0]
        
        # Check if all required fields are present
        required_fields = {
            'metric': ['temp', 'pressure', 'windSpeed'],
            'humidity': None,
            'winddir': None
        }
        
        for field, subfields in required_fields.items():
            if field not in obs:
                print(f"Error: Missing field '{field}' in observation data")
                return None
            if subfields and isinstance(subfields, list):
                for subfield in subfields:
                    if subfield not in obs[field]:
                        print(f"Error: Missing subfield '{subfield}' in {field}")
                        return None
        
        # Get weather conditions from available fields
        conditions = "Unknown"
        if 'wxPhraseLong' in obs:
            conditions = obs['wxPhraseLong']
        elif 'wxPhrase' in obs:
            conditions = obs['wxPhrase']
        elif 'wxPhraseShort' in obs:
            conditions = obs['wxPhraseShort']
        
        return {
            'temperature': obs['metric']['temp'],
            'humidity': obs['humidity'],
            'pressure': obs['metric']['pressure'],
            'wind_speed': obs['metric']['windSpeed'],
            'wind_direction': obs['winddir'],
            'conditions': conditions
        }
    except requests.exceptions.RequestException as e:
        print(f"Network error getting weather data: {e}")
        if hasattr(e.response, 'text'):
            print(f"API Error Response: {e.response.text}")
        return None
    except ValueError as e:
        print(f"Error parsing API response: {e}")
        print("API Response:", response.text if 'response' in locals() else "No response received")
        return None
    except Exception as e:
        print(f"Unexpected error getting weather data: {e}")
        return None

def format_weather_message(weather_data):
    """Format weather data into a readable message."""
    if not weather_data:
        return "Unable to get weather data at this time."
    
    # Format wind direction into cardinal directions
    wind_direction = weather_data['wind_direction']
    cardinal_directions = {
        'N': (337.5, 22.5),
        'NE': (22.5, 67.5),
        'E': (67.5, 112.5),
        'SE': (112.5, 157.5),
        'S': (157.5, 202.5),
        'SW': (202.5, 247.5),
        'W': (247.5, 292.5),
        'NW': (292.5, 337.5)
    }
    
    wind_cardinal = 'N'
    for direction, (min_angle, max_angle) in cardinal_directions.items():
        if min_angle <= wind_direction < max_angle:
            wind_cardinal = direction
            break
    
    message = (
        f"Current weather conditions: {weather_data['conditions']}. "
        f"Temperature {weather_data['temperature']} degrees Celsius. "
        f"Humidity {weather_data['humidity']} percent. "
        f"Wind {weather_data['wind_speed']} kilometers per hour from {wind_cardinal}. "
        f"Pressure {weather_data['pressure']} millibars. "
        f"Reported at {datetime.now().strftime('%H:%M')} local time."
    )
    return message

def announce_to_allstar(message):
    """Send the weather announcement to AllStar Link."""
    try:
        client = AMIClient(host=ASTERISK_HOST, port=ASTERISK_PORT)
        client.login(username=ASTERISK_USER, secret=ASTERISK_SECRET)
        
        # Create the announcement action
        action = SimpleAction(
            'Originate',
            Channel=f'Local/{ALLSTAR_NODE}@from-internal',
            Application='Playback',
            Data='silence/1&weather-announcement',
            Priority=1,
            Timeout=30000,
            CallerID='Weather Service <1000>'
        )
        
        # Send the action
        client.send_action(action)
        client.logoff()
        print("Weather announcement sent successfully")
    except Exception as e:
        print(f"Error sending announcement to AllStar: {e}")

def main():
    print("Getting weather data...")
    weather_data = get_weather_data()
    
    if weather_data:
        message = format_weather_message(weather_data)
        
        # Print raw API response
        print("\n=== Raw API Response ===")
        try:
            response = requests.get(
                "https://api.weather.com/v2/pws/observations/current",
                params={
                    'stationId': WU_STATION_ID,
                    'format': 'json',
                    'units': 'm',
                    'apiKey': WU_API_KEY,
                    'numericPrecision': 'decimal'
                }
            )
            data = response.json()
            obs = data['observations'][0]
            
            print("\nInformación de la Estación:")
            print(f"ID de Estación: {obs['stationID']}")
            print(f"Ubicación: {obs['neighborhood']}")
            print(f"País: {obs['country']}")
            print(f"Coordenadas: {obs['lat']}°N, {obs['lon']}°W")
            print(f"Elevación: {obs['metric']['elev']} metros")
            
            print("\nInformación Temporal:")
            print(f"Tiempo UTC: {obs['obsTimeUtc']}")
            print(f"Tiempo Local: {obs['obsTimeLocal']}")
            
            print("\nCondiciones Actuales:")
            print(f"Temperatura: {obs['metric']['temp']}°C")
            print(f"Índice de Calor: {obs['metric']['heatIndex']}°C")
            print(f"Punto de Rocío: {obs['metric']['dewpt']}°C")
            print(f"Sensación Térmica: {obs['metric']['windChill']}°C")
            print(f"Humedad: {obs['humidity']}%")
            
            print("\nInformación del Viento:")
            print(f"Dirección: {obs['winddir']}°")
            print(f"Velocidad: {obs['metric']['windSpeed']} km/h")
            print(f"Ráfagas: {obs['metric']['windGust']} km/h")
            
            print("\nPresión y Precipitación:")
            print(f"Presión: {obs['metric']['pressure']} mb")
            print(f"Tasa de Precipitación: {obs['metric']['precipRate']} mm/h")
            print(f"Precipitación Total: {obs['metric']['precipTotal']} mm")
            
            print("\nOtros Datos:")
            print(f"Radiación Solar: {obs['solarRadiation']}")
            print(f"Índice UV: {obs['uv']}")
            print(f"Estado QC: {obs['qcStatus']}")
            
        except Exception as e:
            print(f"Error getting raw data: {e}")
        print("=======================\n")
        
        # Print formatted weather information
        print("\n=== Weather Information ===")
        print(f"Conditions: {weather_data['conditions']}")
        print(f"Temperature: {weather_data['temperature']}°C")
        print(f"Humidity: {weather_data['humidity']}%")
        print(f"Wind Speed: {weather_data['wind_speed']} km/h")
        print(f"Wind Direction: {weather_data['wind_direction']}°")
        print(f"Pressure: {weather_data['pressure']} mb")
        print("========================\n")
        
        print("Formatted message:")
        print(message)
    else:
        print("Failed to get weather data")

if __name__ == "__main__":
    main() 