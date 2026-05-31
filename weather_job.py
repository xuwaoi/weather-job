import os
import requests
import time
from datetime import datetime
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

print('Script started')

INFLUX_URL = os.environ.get('INFLUX_URL', 'NOT SET')
INFLUX_TOKEN = os.environ.get('INFLUX_TOKEN', 'NOT SET')
INFLUX_ORG = os.environ.get('INFLUX_ORG', 'NOT SET')
INFLUX_BUCKET = os.environ.get('INFLUX_BUCKET', 'NOT SET')

print(f'URL: {INFLUX_URL}')
print(f'ORG: {INFLUX_ORG}')
print(f'BUCKET: {INFLUX_BUCKET}')

def fetch_weather():
    r = requests.get('https://api.open-meteo.com/v1/forecast', params={'latitude': 40.7128, 'longitude': -74.0060, 'current': 'temperature_2m,wind_speed_10m,precipitation,relative_humidity_2m', 'timezone': 'America/New_York'})
    r.raise_for_status()
    return r.json()['current']

def write_to_influx(data):
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)
    point = Point('nyc_weather').field('temperature_c', float(data['temperature_2m'])).field('wind_speed_kmh', float(data['wind_speed_10m'])).field('precipitation', float(data['precipitation'])).field('humidity_pct', float(data['relative_humidity_2m']))
    write_api.write(bucket=INFLUX_BUCKET, record=point)
    print(f'Zapisano: {data}')
    client.close()

while True:
    try:
        write_to_influx(fetch_weather())
    except Exception as e:
        print(f'Oshibka: {e}')
    time.sleep(1800)
