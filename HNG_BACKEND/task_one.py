from flask import Flask, request, jsonify
import requests
import json
import pandas
from urllib.request import urlopen


app = Flask(__name__)
url = 'http://ipinfo.io/json'
# response = urlopen(url)
# data = json.load(response)


@app.route('/api/hello/<visitor_name>', methods=['GET'])
def hello(visitor_name):

    # Use a third-party service to get location information based on IP
    response = urlopen(url)
    data = json.load(response)
    client_ip = data['ip']
    city = data['city']
    lat = data.get('lat', 0)
    lon = data.get('lon', 0)
    temperature = get_temperature(lat, lon)

    return jsonify({
        'client_ip': client_ip,
        'location': city,
        'greeting': f'Hello, {visitor_name}!, the temperature is {temperature} degrees Celsius in {city}'
    })


def get_temperature(lat, lon):
    base_url = 'https://api.open-meteo.com/v1/forecast'
    params = {
        'latitude': lat,
        'longitude': lon,
        'current_weather': True
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    
    if 'current_weather' in data:
        temperature = data['current_weather']['temperature']
        return temperature
    else:
        return 11

if __name__ == '__main__':
    app.run(debug=True)
