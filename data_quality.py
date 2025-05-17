# data_quality.py
import requests
from config import OPENWEATHER_API_KEY

# Function to fetch local weather data from OpenWeatherMap API
def fetch_local_weather_data(lat, lon):
    api_key = OPENWEATHER_API_KEY
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"

    try:
        response = requests.get(url)
        data = response.json()
        #When cod is 200 the API request was successful and valid weather data is available in the response.
        if data["cod"] == 200: 
            # Extract the necessary weather data (temperature, humidity, pressure)
            local_weather_data = {
                "temperature": data["main"]["temp"],        # Temperature in °C
                "humidity": data["main"]["humidity"],       # Humidity in %
                "pressure": data["main"]["pressure"],       # Pressure in hPa
                "windspeed": data["wind"]["speed"],         # Wind speed in m/s
                "winddirection": data["wind"]["deg"],       # Wind direction in degrees
                "rainfall": data.get("rain", {}).get("1h", 0)  # Rainfall in mm (if available)
            }
            return local_weather_data
        else:
            print("Failed to get weather data.")
            return None
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return None

# Function to compare fetched weather data against local weather data
def check_data_quality(fetched_data, lat, lon):
    # Fetch local weather data from OpenWeatherMap API
    local_weather_data = fetch_local_weather_data(lat, lon)
    
    if local_weather_data is None:
        print("Error: Could not fetch local weather data.")
        # Return 0 since we can't compare
        return 0
    
    # Define individual tolerances for each metric, excluding winddirection
    tolerances = {
        "temperature": 3.0,    # Tolerance in °C
        "humidity": 10.0,      # Tolerance in percentage points
        "pressure": 5.0,       # Tolerance in hPa
        "windspeed": 2.0,      # Tolerance in m/s
        "rainfall": 2.0        # Tolerance in mm
    }
    
    quality_report = {}
    out_of_tolerance_count = 0
    
    for key in fetched_data:
        if key in local_weather_data and key in tolerances:
            fetched_value = fetched_data[key]
            local_value = local_weather_data[key]
            
            # Calculate the difference and check if it's within acceptable range for this metric
            difference = abs(fetched_value - local_value)
            within_tolerance = difference <= tolerances[key]
            
            quality_report[key] = {
                "fetched_value": fetched_value,
                "local_value": local_value,
                "difference": difference,
                "tolerance": tolerances[key],
                "within_tolerance": within_tolerance
            }
            
            if not within_tolerance:
                out_of_tolerance_count += 1

    # Print the quality report
    if quality_report:
        print("Data Quality Report:")
        for key, value in quality_report.items():
            status = "OK" if value["within_tolerance"] else "Out of Tolerance"
            print(f"{key.capitalize()}: "
                  f"Fetched {value['fetched_value']} | "
                  f"Local {value['local_value']} | "
                  f"Difference {value['difference']} | "
                  f"Tolerance {value['tolerance']} | "
                  f"Status: {status}")
    else:
        print("No data to compare.")

    return out_of_tolerance_count
