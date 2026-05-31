import requests
import time
from datetime import datetime
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# СЮДА ВСТАВЬ СВОИ ДАННЫЕ
INFLUX_URL    = "https://us-east-1-1.aws.cloud2.influxdata.com"
INFLUX_TOKEN  = "rmGMPDav2i_SQYdC_u65eulSgoho-e7OtRZ9Fwo_PaMJqap8wk1aqpHhBbLIe9bgsqdkR5R8r1pI7CrGbZe6Cg=="
INFLUX_ORG    = "xuwaoii@gmail.com"
INFLUX_BUCKET = "weather_nyc"

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
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Записано: {data}")
    client.close()

while True:
    try:
        weather = fetch_weather()
        write_to_influx(weather)
    except Exception as e:
        print(f"Ошибка: {e}")
    time.sleep(1800)

