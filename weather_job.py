import os
import requests
import time
from datetime import datetime
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

INFLUX_URL    = os.environ["INFLUX_URL"]
INFLUX_TOKEN  = os.environ["INFLUX_TOKEN"]
INFLUX_ORG    = os.environ["INFLUX_ORG"]
INFLUX_BUCKET = os.environ["INFLUX_BUCKET"]

def fetch_weather():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "current": "temperature_2m,wind_speed_10m,precipitation,relative_humidity_2m",
        "timezone": "America/New_York"
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    return r.json()["current"]

def write_to_influx(data):
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)
    point = Point("nyc_weather") \
        .field("temperature_c",  float(data["temperature_2m"])) \
        .field("wind_speed_kmh", float(data["wind_speed_10m"])) \
        .field("precipitation",  float(data["precipitation"])) \
        .field("humidity_pct",   float(data["relative_humidity_2m"]))
    write_api.write(bucket=INFLUX_BUCKET, record=point)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Zapisano: {data}")
    client.close()

while True:
    try:
        weather = fetch_weather()
        write_to_influx(weather)
    except Exception as e:
        print(f"Oshibka: {e}")
    time.sleep(1800)
