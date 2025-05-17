# sensor.py
import random
import weatherhat
from datetime import datetime
from adafruit_io import send_data_to_adafruit_io

# Initialize the Weather HAT
sensor = weatherhat.WeatherHAT()

def check_sensor_status():
    try:
        # Attempt to update sensor readings
        sensor.update()  # Updates sensor readings
        # If successful, sensor is online
        send_data_to_adafruit_io("sensorhealth", "green")  # Update Adafruit IO to green
    except Exception as e:
        # If update fails, sensor is offline
        print(f"Sensor update error: {e}")
        send_data_to_adafruit_io("sensorhealth", "red")  # Update Adafruit IO to red

def get_weather_data():
    # Update sensor readings with current environmental conditions
    sensor.update()
    
    # Read data from the Weather HAT sensor
    temperature = sensor.temperature       # °C
    humidity = sensor.relative_humidity    # %
    pressure = sensor.pressure             # hPa
    windspeed = sensor.wind_speed          # m/s
    winddirection = sensor.wind_direction  # degrees
    rainfall = sensor.rain                 # cumulative rain in mm since last reset/start
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Apply a manual offset to correct the temperature (subtract 20°F in Celsius)
    corrected_temperature = temperature - (20 / 1.8)
    
    # Apply manual offset to correct the pressure
    corrected_pressure = pressure + 10
    
    return {
        "temperature": corrected_temperature,
        "humidity": humidity,
        "pressure": corrected_pressure,
        "windspeed": windspeed,
        "winddirection": winddirection,
        "rainfall": rainfall,
        "timestamp": timestamp
    }
