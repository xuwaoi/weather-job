import os
import requests
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

INFLUX_URL = os.environ.get('INFLUX_URL')
INFLUX_TOKEN = os.environ.get('INFLUX_TOKEN')
INFLUX_ORG = os.environ.get('INFLUX_ORG')
INFLUX_BUCKET = os.environ.get('INFLUX_BUCKET')

r = requests.get('https://api.open-meteo.com/v1/forecast', params={'latitude': 40.7128, 'longitude': -74.0060, 'current': 'temperature_2m,wind_speed_10m,precipitation,relative_humidity_2m', 'timezone': 'America/New_York'})
data = r.json()['current']

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)
point = Point('nyc_weather').field('temperature_c', float(data['temperature_2m'])).field('wind_speed_kmh', float(data['wind_speed_10m'])).field('precipitation', float(data['precipitation'])).field('humidity_pct', float(data['relative_humidity_2m']))
write_api.write(bucket=INFLUX_BUCKET, record=point)
print(f'Zapisano: {data}', flush=True)
client.close()
