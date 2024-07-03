from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def homepage():
    return "<h3>Welcome!!!..add 'api/hello?visitor_name=yourname' to the URL to get your IP address, location, and environmental temperature</h3>"

@app.route('/api/hello', methods=['GET'])
def hello():
    visitor_name = request.args.get('visitor_name', 'Visitor')
    url = 'http://ipinfo.io/json'
    response = requests.get(url)
    data = response.json()
    client_ip = data['ip']
    city = data['city']
    loc = data['loc'].split(',')
    lat = float(loc[0])
    lon = float(loc[1])
    temperature = get_temperature(lat, lon)

    return jsonify({
        'client_ip': client_ip,
        'location': city,
        'greeting': f'Hello, {visitor_name}!, the temperature is {temperature} degrees Celsius in {city}'
    })

def get_temperature(lat, lon):
    api_key = 'api key'
    base_url = 'https://api.openweathermap.org/data/2.5/weather'
    params = {
        'lat': lat,
        'lon': lon,
        'appid': 'api key',
        'units': 'metric'
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    
    if 'main' in data:
        temperature = data['main']['temp']
        return temperature
    else:
        return 11

if __name__ == '__main__':
    app.run(debug=True)
