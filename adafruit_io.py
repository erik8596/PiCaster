# adafruit_io.py

from Adafruit_IO import Client
from config import ADAFRUIT_IO_KEY, ADAFRUIT_IO_USERNAME

# Initialize the Adafruit IO client
io = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

# Function to send data to Adafruit IO
def send_data_to_adafruit_io(feed_name, value):
    try:
        feed = io.feeds(feed_name)
        io.send_data(feed.key, value)
        print(f"Sent {value} to {feed_name} feed")
    except Exception as e:
        print(f"Error sending data to Adafruit IO: {e}")
