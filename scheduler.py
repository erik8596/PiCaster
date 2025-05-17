# scheduler.py
import schedule
import time
from datetime import datetime, timedelta
from adafruit_io import send_data_to_adafruit_io, io
from sensor import get_weather_data, check_sensor_status
from data_quality import check_data_quality

# latitude and longitude for Harrisburg, PA
latitude = 40.2663
longitude = -76.8903

# Global variables to store the latest data and rainfall history
data = None
rainfall_history = []

def get_rainfall_last_hour():
    # If we don't have enough data points, return 0.0
    if len(rainfall_history) < 2:
        return 0.0
    
    # After pruning, the first reading in the list is the earliest within the last hour
    # and the last reading is the most recent.
    earliest_timestamp, earliest_rain = rainfall_history[0]
    latest_timestamp, latest_rain = rainfall_history[-1]
    
    # The difference in cumulative rainfall between oldest and newest readings gives
    # how much rain fell over that hour.
    return max(0.0, latest_rain - earliest_rain)

def instant_reading():
    print("Performing instant reading...")

    # Check sensor status
    check_sensor_status()

    # Fetch sensor data
    reading = get_weather_data()
    if reading:
        # Perform data quality check and capture the out_of_tolerance_count
        out_of_tolerance_count = check_data_quality(reading, latitude, longitude)

        # Update sensorhealth based on data quality
        if out_of_tolerance_count is not None and out_of_tolerance_count > 2:
            send_data_to_adafruit_io("sensorhealth", "red")
        else:
            send_data_to_adafruit_io("sensorhealth", "green")

        # Update the global data and rainfall history with this instant reading
        global data, rainfall_history
        data = reading
        current_time = datetime.now()
        rainfall_history.append((current_time, data["rainfall"]))

        # Prune readings older than 1 hour
        one_hour_ago = current_time - timedelta(hours=1)
        rainfall_history = [(t, r) for t, r in rainfall_history if t >= one_hour_ago]

        # Compute the rainfall over the last hour
        hourly_rainfall = get_rainfall_last_hour()

        # Send data to Adafruit IO
        send_data_to_adafruit_io("temperature", data["temperature"])
        send_data_to_adafruit_io("humidity", data["humidity"])
        send_data_to_adafruit_io("pressure", data["pressure"])
        send_data_to_adafruit_io("windspeed", data["windspeed"])

        # Format the wind direction for Adafruit IO icon box updates
        wind_direction = data["winddirection"]  # wind direction in degrees (0-360)
        wind_direction_formatted = f"w:wind__towards-{int(wind_direction)}-deg"
        send_data_to_adafruit_io("winddirection", wind_direction_formatted)

        # Send the hourly rainfall instead of just the instantaneous value
        send_data_to_adafruit_io("rainfall", hourly_rainfall)

        print("Instant reading data has been sent to Adafruit IO.")
    else:
        print("No sensor data to send for instant reading.")

def poll_instant_reading_button():
    try:
        # Fetch the 'instantreading' feed
        feed = io.feeds("instantreading")
        button_value = io.receive(feed.key).value

        if button_value == "1":  # Button is pressed
            print("Instant Reading Button Pressed!")
            instant_reading()
            # Reset the button value in Adafruit IO
            io.send_data(feed.key, "0")
        
    except Exception as e:
        print(f"Error monitoring instant reading button: {e}")

def get_data():
    global data, rainfall_history
    # Get weather data and store in global variable
    reading = get_weather_data()
    if reading:
        data = reading
        print(f"Fetched data: {data}")

        # Record rainfall reading
        current_time = datetime.now()
        rainfall_history.append((current_time, data["rainfall"]))

        # Remove readings older than 1 hour
        one_hour_ago = current_time - timedelta(hours=1)
        rainfall_history = [(t, r) for t, r in rainfall_history if t >= one_hour_ago]
    else:
        print("No data fetched.")

def send_data():
    global data
    # Check if data exists
    if data:
        # Compute hourly rainfall before sending
        hourly_rainfall = get_rainfall_last_hour()

        # Check data quality
        out_of_tolerance_count = check_data_quality(data, latitude, longitude)

        # Update sensorhealth based on out-of-tolerance count
        if out_of_tolerance_count is not None and out_of_tolerance_count > 2:
            send_data_to_adafruit_io("sensorhealth", "red")
        else:
            send_data_to_adafruit_io("sensorhealth", "green")

        # Send each piece of sensor data to Adafruit IO
        send_data_to_adafruit_io("temperature", data["temperature"])
        send_data_to_adafruit_io("humidity", data["humidity"])
        send_data_to_adafruit_io("pressure", data["pressure"])
        send_data_to_adafruit_io("windspeed", data["windspeed"])

        # Format the wind direction for Adafruit IO icon box updates
        wind_direction = data["winddirection"]
        wind_direction_formatted = f"w:wind__towards-{int(wind_direction)}-deg"
        send_data_to_adafruit_io("winddirection", wind_direction_formatted)

        # Send the hourly rainfall
        send_data_to_adafruit_io("rainfall", hourly_rainfall)

        print("Sensor data (including hourly rainfall) has been sent to Adafruit IO.")
    else:
        print("No sensor data to send.")

def quality_check_task():
    global data
    if data:
        out_of_tolerance_count = check_data_quality(data, latitude, longitude)
        if out_of_tolerance_count is not None and out_of_tolerance_count > 2:
            send_data_to_adafruit_io("sensorhealth", "red")
        else:
            send_data_to_adafruit_io("sensorhealth", "green")
    else:
        # If no data is available, we can't assess quality. 
        send_data_to_adafruit_io("sensorhealth", "red")
        print("No data available for quality check. Setting sensorhealth to red.")

def schedule_tasks():
    # Schedule task to check the instant read button feed every 3 seconds
    schedule.every(3).seconds.do(poll_instant_reading_button)
    
    # Schedule task for checking sensor status every 5 minutes
    schedule.every(5).minutes.do(check_sensor_status)

    # Schedule task for fetching sensor data every 5 minutes
    schedule.every(5).minutes.do(get_data)

    # Schedule task for checking data quality every 5 minutes (using the function instead of lambda)
    schedule.every(5).minutes.do(quality_check_task)
    
    # Schedule task for sending data to Adafruit IO every 5 minutes
    schedule.every(5).minutes.do(send_data)

    print("Scheduler started.")
    while True:
        # Run pending tasks
        schedule.run_pending()
        time.sleep(1)

