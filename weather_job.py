import os
import requests
import time as time_module
from datetime import datetime
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

INFLUX_URL = os.environ.get('INFLUX_URL')
INFLUX_TOKEN = os.environ.get('INFLUX_TOKEN')
INFLUX_ORG = os.environ.get('INFLUX_ORG')
INFLUX_BUCKET = os.environ.get('INFLUX_BUCKET')

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')
    def log_message(self, format, *args):
        pass

def run_server():
    HTTPServer(('0.0.0.0', 8080), Handler).serve_forever()

threading.Thread(target=run_server, daemon=True).start()
print('HTTP server started', flush=True)

def fetch_weather():
    r = requests.get('https://api.open-meteo.com/v1/forecast', params={'latitude': 40.7128, 'longitude': -74.0060, 'current': 'temperature_2m,wind_speed_10m,precipitation,relative_humidity_2m', 'timezone': 'America/New_York'})
    r.raise_for_status()
    return r.json()['current']

def write_to_influx(data):
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)
    point = Point('nyc_weather').field('temperature_c', float(data['temperature_2m'])).field('wind_speed_kmh', float(data['wind_speed_10m'])).field('precipitation', float(data['precipitation'])).field('humidity_pct', float(data['relative_humidity_2m']))
    write_api.write(bucket=INFLUX_BUCKET, record=point)
    print(f'Zapisano: {data}', flush=True)
    client.close()

while True:
    try:
        write_to_influx(fetch_weather())
        print('Sleeping 30 min...', flush=True)
    except Exception as e:
        print(f'Oshibka: {e}', flush=True)
    time_module.sleep(1800)
