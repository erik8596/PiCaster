# PiCaster Setup

## Overview
This project monitors weather conditions using the Pimoroni Weather HAT on a Raspberry Pi, processes the data, and sends it to Adafruit IO for real-time visualization of weather metrics.

---

## Prerequisites

Ensure the following are installed on the system:
1. **Python** (version 3.7 or higher)
2. **Pimoroni Weather HAT library**
3. **Adafruit IO Account**: Sign up at [Adafruit IO](https://io.adafruit.com).
4. **OpenWeatherMap API Key**: Get one at [OpenWeatherMap](https://openweathermap.org/api).

---

## Installation Steps

1. **Clone/Copy the Project Directory**  
   Place all the project files into a folder.

2. **Install Required Python Packages**  
   Navigate to the project directory and run:

   ```
   pip install -r requirements.txt
   ```

3. **Hardware Setup**  
   - Connect the **Weather HAT** to the Raspberry Pi GPIO header.
   - Ensure the Raspberry Pi has internet access.

4. **Configure API Keys**  
   Edit the `config.py` file with your credentials:
   ```python
   ADAFRUIT_IO_KEY = 'Your_Adafruit_IO_Key'
   ADAFRUIT_IO_USERNAME = 'Your_Adafruit_IO_Username'
   OPENWEATHER_API_KEY = 'Your_OpenWeather_API_Key'
   ```

---

## How to Run the Project

1. **Start the Main Application**  
   Run the following command:

   ```
   python app.py
   ```

2. **Background Operation**  
   The program will:
   - Continuously collect weather data from the Weather HAT.
   - Compare it to OpenWeatherMap data for quality verification.
   - Send the results to Adafruit IO.

---

## Key Files

| File               | Description                                          |
|--------------------|------------------------------------------------------|
| `app.py`          | Main entry point; starts the scheduler.              |
| `scheduler.py`    | Manages periodic tasks like data collection.         |
| `sensor.py`       | Reads weather data from the Weather HAT.             |
| `data_quality.py` | Compares Weather HAT data with OpenWeatherMap API.   |
| `adafruit_io.py`  | Sends data to Adafruit IO.                           |
| `config.py`       | Stores API keys and configuration settings.          |
| `requirements.txt`| List of required Python packages.                    |

---

## Testing

- Test Adafruit IO connectivity by checking if sensor readings update on your Adafruit IO dashboard.
- Run `scheduler.py` to verify periodic task execution.

---

## Troubleshooting

1. **Issue: Weather HAT not responding**  
   - Ensure the HAT is properly connected to GPIO pins.
   - Verify `weatherhat` library is installed.

2. **Issue: API Key Errors**  
   - Double-check API keys in `config.py`.

3. **Issue: Adafruit IO updates not appearing**  
   - Verify internet connectivity on the Raspberry Pi.
   - Check Adafruit IO dashboard credentials.

---
