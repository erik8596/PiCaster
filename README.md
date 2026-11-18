# PiCaster — Raspberry Pi Weather Station

**Python · Raspberry Pi · Pimoroni Weather HAT · Adafruit IO · OpenWeatherMap**

PiCaster is a Raspberry Pi weather-monitoring project that reads environmental data from a **Pimoroni Weather HAT**, compares selected measurements against **OpenWeatherMap** observations, and sends readings to **Adafruit IO** for online visualization.

The code brings together sensor integration, API requests, scheduled jobs, basic data-quality checks, and cloud dashboard feeds.

> **Project scope:** PiCaster is a personal hardware/software project. The published repository contains the Python application, but no dashboard screenshots, automatic deployment scripts, or automated test suite. Running it requires compatible physical hardware and configured third-party accounts.

## Features

- **Sensor acquisition:** Temperature, relative humidity, atmospheric pressure, wind speed, wind direction, and rainfall from the Weather HAT.
- **Scheduled uploads:** Weather readings and health status are collected or published on five-minute schedules.
- **On-demand readings:** Polls an Adafruit IO `instantreading` feed every three seconds; a value of `1` triggers an immediate sensor reading and upload, then resets the feed to `0`.
- **Cross-reference checks:** Compares sensor values with OpenWeatherMap measurements using per-metric tolerances.
- **Dashboard feeds:** Publishes sensor data, formatted wind direction, and a simple red/green sensor-health status to Adafruit IO.
- **Rainfall history:** Keeps recent rainfall readings in memory and computes a difference-based hourly value (see the limitation below).

## Hardware and Services

- Raspberry Pi with a 40-pin GPIO header, network access, and a supported Raspberry Pi OS installation
- Pimoroni Weather HAT, with compatible wind and rain sensors if collecting those measurements
- [Adafruit IO](https://io.adafruit.com/) account and API key
- [OpenWeatherMap](https://openweathermap.org/api) account and API key

The Weather HAT library and hardware-interface setup are documented by [Pimoroni](https://github.com/pimoroni/weatherhat-python) and in its [getting-started guide](https://learn.pimoroni.com/article/getting-started-with-weather-hat).

## How It Works

~~~text
Pimoroni Weather HAT
        |
        v
   sensor.py  --------> Weather measurements
        |                         |
        v                         v
   scheduler.py --------> data_quality.py <---- OpenWeatherMap API
        |
        v
   adafruit_io.py -----> Adafruit IO feeds/dashboard
~~~

- `sensor.py` updates the Weather HAT and assembles sensor readings, including manual temperature and pressure offsets.
- `scheduler.py` manages recurring reads, upload tasks, data-quality checks, recent rainfall history, and the on-demand reading feed.
- `data_quality.py` retrieves nearby weather observations and counts measurements that exceed predefined tolerances.
- `adafruit_io.py` connects to Adafruit IO and publishes data to the configured feeds.
- `app.py` launches the scheduler in a background thread and keeps the process alive.

### Data-quality thresholds

The code currently compares these five metrics with OpenWeatherMap readings:

| Measurement | Tolerance |
| --- | ---: |
| Temperature | 3 °C |
| Relative humidity | 10 percentage points |
| Atmospheric pressure | 5 hPa |
| Wind speed | 2 m/s |
| Rainfall | 2 mm |

The app publishes `sensorhealth = red` if **more than two** compared metrics exceed their tolerances; otherwise it publishes `green`. This is a heuristic, not a calibrated sensor-health or safety assessment.

## Installation

### 1. Set up the Weather HAT

Connect the Weather HAT and any external wind/rain sensors following the hardware manufacturer's instructions.

On the Raspberry Pi, install Pimoroni's library using its maintained setup instructions:

~~~bash
git clone https://github.com/pimoroni/weatherhat-python.git
cd weatherhat-python
./install.sh
~~~

Pimoroni's installer configures required dependencies and interfaces and typically uses a `pimoroni` Python virtual environment. Consult the linked instructions if a reboot or different virtual environment is required.

### 2. Clone PiCaster and install Python dependencies

~~~bash
git clone https://github.com/erik8596/PiCaster.git
cd PiCaster
source ~/.virtualenvs/pimoroni/bin/activate
python -m pip install -r requirements.txt
~~~

**Dependency note:** The repository's `requirements.txt` includes Adafruit IO, `requests`, and `schedule`, but does **not** include the Pimoroni `weatherhat` library. Install and activate that library as described in step 1. The virtual-environment path above reflects Pimoroni's documented default and may vary.

### 3. Configure your API credentials

~~~bash
cp config_example.py config.py
~~~

Edit the newly created `config.py`:

~~~python
ADAFRUIT_IO_KEY = "your_adafruit_io_key"
ADAFRUIT_IO_USERNAME = "your_adafruit_io_username"
OPENWEATHER_API_KEY = "your_openweathermap_api_key"
~~~

**Keep `config.py` private.** It is listed in `.gitignore` so credentials should not be committed. Never share real API keys or paste them into issues or screenshots.

### 4. Configure your monitoring location

Open `scheduler.py` and set its `latitude` and `longitude` variables to the location of your weather station. The published version has coordinates hardcoded for the original deployment.

### 5. Create Adafruit IO feeds

Create these feeds in your Adafruit IO account before starting the application:

| Feed key | Value published / expected |
| --- | --- |
| `temperature` | Temperature (°C) |
| `humidity` | Relative humidity (%) |
| `pressure` | Atmospheric pressure (hPa) |
| `windspeed` | Wind speed (m/s) |
| `winddirection` | Formatted wind-direction icon identifier |
| `rainfall` | Difference-based hourly rainfall value (mm; see limitations) |
| `sensorhealth` | `green` or `red` |
| `instantreading` | Set to `1` to request an immediate reading; app resets it to `0` |

You can then arrange the corresponding dashboard blocks in Adafruit IO. Dashboard layout files are not included in this repository.

### 6. Run

~~~bash
python app.py
~~~

The application schedules most weather tasks at **five-minute intervals** and polls for manual readings every **three seconds**. It does not perform a full upload immediately at launch. To request an on-demand update, set the `instantreading` feed to `1` after starting the program.

Stop the application with **Ctrl+C**.

## Repository Files

| File | Purpose |
| --- | --- |
| `app.py` | Starts the scheduler thread and keeps the app running |
| `scheduler.py` | Coordinates sampling, quality checks, uploads, rainfall history, and on-demand readings |
| `sensor.py` | Interfaces with the Weather HAT and applies manual calibration offsets |
| `data_quality.py` | Calls OpenWeatherMap and compares selected weather metrics |
| `adafruit_io.py` | Sends values to Adafruit IO feeds |
| `config_example.py` | Template for local API credentials |
| `requirements.txt` | Lists Python package dependencies other than `weatherhat` |
| `.gitignore` | Excludes local `config.py`, Python cache directories, and `.pyc` files |

## Verification and Troubleshooting

There is no automated test suite in the published repository. To check a hardware deployment manually:

1. Confirm that the Weather HAT library can detect and read your attached hardware.
2. Launch `python app.py` and inspect terminal output for sensor errors.
3. Verify that Adafruit IO feeds update after the scheduled interval.
4. Set `instantreading` to `1` and confirm a new reading appears and the feed resets.
5. Review the printed comparison report and confirm that OpenWeatherMap credentials and station coordinates are correct.

If data is missing, check GPIO connections, the active Python environment, API credentials, internet connectivity, and feed names.

## Known Limitations

- **Rainfall aggregation:** The current calculation differences two recent `sensor.rain` readings, treating them as cumulative. Pimoroni documents rain readings as interval-based, so the displayed hourly rainfall may be inaccurate. This should be revised before treating rainfall totals as reliable.
- **Calibration:** `sensor.py` applies hardcoded temperature and pressure offsets. These were chosen for a particular setup and may not be suitable elsewhere.
- **Location:** Weather-reference coordinates are hardcoded in `scheduler.py` rather than provided through configuration.
- **Quality-check fallback:** If OpenWeatherMap cannot return data, `check_data_quality` returns zero out-of-tolerance readings. This can cause a green health status even though the comparison could not be completed.
- **HTTP and credentials:** `data_quality.py` currently requests OpenWeatherMap over plain HTTP with the API key in the URL. Switch to HTTPS before deployment.
- **CPU usage:** `app.py` uses a tight `while True: pass` loop, which may waste CPU while keeping the process alive.
- **Testing and deployment:** Automated tests, a system service, and a reproducible dashboard export are not included.

## Future Improvements

Potential improvements include corrected rolling rainfall aggregation, environment-based configuration, HTTPS requests with timeouts, improved error handling and health indicators, automated tests with mock sensor/API responses, and a screenshot of the running Adafruit IO dashboard.

---

**PiCaster** demonstrates Python-based sensor integration, API data processing, task scheduling, and IoT dashboard publishing.
