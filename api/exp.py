from flask import Flask, request, jsonify
import requests
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="*", supports_credentials=True, allow_headers=[
    "Origin", "X-Requested-With", "Content-Type", "X-Access-Token",
    "Authorization", "Access-Control-Allow-Origin"])

# Helper function to get the user's IP address
def get_client_ip():
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    return client_ip

@app.route('/api/hello', methods=['GET'])
def hello():
    visitor_name = request.args.get('visitor_name', 'Visitor')
    client_ip = get_client_ip()

    if not client_ip or client_ip == '::1' or client_ip == '127.0.0.1':
        client_ip = '8.8.8.8'  # Example IP address (Google Public DNS)

    try:
        # Use an IP Geolocation API to get the city
        geo_response = requests.get(f'https://ipapi.co/{client_ip}/json/')
        geo_response.raise_for_status()  # Raise an exception for HTTP errors

        city = geo_response.json().get('city')

        # Use a Weather API to get the temperature
        weather_response = requests.get('http://api.openweathermap.org/data/2.5/weather', params={
            'q': city,
            'appid': os.getenv('OPENWEATHER_API_KEY'),
            'units': 'metric'  # Change to 'imperial' for Fahrenheit
        })
        weather_response.raise_for_status()  # Raise an exception for HTTP errors

        temperature = weather_response.json()['main']['temp']

        return jsonify({
            "client_ip": client_ip,
            "location": city,
            "greeting": f"Hello, {visitor_name}! The temperature is {temperature} degrees Celsius in {city}"
        })
    
    except requests.RequestException as e:
        print(e)
        return jsonify({'error': 'Failed to fetch weather data'}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
