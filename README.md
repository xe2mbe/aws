# Weather AllStar Announcer

This script retrieves weather data from Weather Underground and announces it on AllStar Link.

## Prerequisites

- Python 3.7 or higher
- Weather Underground API key
- AllStar Link node
- Asterisk AMI access

## Setup

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```

3. Edit the `.env` file and fill in your configuration:
   - `WU_API_KEY`: Your Weather Underground API key
   - `WU_STATION_ID`: Your local weather station ID
   - `ASTERISK_HOST`: Your Asterisk server hostname (default: localhost)
   - `ASTERISK_PORT`: Your Asterisk AMI port (default: 5038)
   - `ASTERISK_USER`: Your Asterisk AMI username
   - `ASTERISK_SECRET`: Your Asterisk AMI secret
   - `ALLSTAR_NODE`: Your AllStar node number

## Usage

Run the script:
```bash
python weather_announcer.py
```

## Features

- Retrieves current weather conditions from Weather Underground
- Formats weather data into a readable message
- Announces the weather on AllStar Link using Asterisk AMI
- Includes temperature, humidity, wind speed, wind direction, and pressure information

## Error Handling

The script includes error handling for:
- Weather API connection issues
- AllStar Link connection problems
- Invalid configuration

## License

This project is open source and available under the MIT License. 