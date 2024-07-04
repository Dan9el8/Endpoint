""""
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
"""

#!/usr/bin/python3
"""Start the flask application"""


from flask import Flask, request, jsonify
from dotenv import load_dotenv
from os import getenv
import requests


load_dotenv()

app = Flask(__name__)


OPENWEATHERMAP_API_KEY = getenv('OPENWEATHERMAP_API_KEY')

@app.route('/', methods=['GET'], strict_slashes=False)
def welcome():
    """
    Default route to welcome users to the Flask application.

    Returns:
    - JSON response with a welcome message.
    """
    return jsonify({"message": "Welcome to the Flask application! Use the /api/hello endpoint to get a personalized greeting and weather information."})

@app.route('/api/hello', methods=['GET'], strict_slashes=False)
def index():
    """
    Endpoint to greet the visitor and provide weather
    information based on their IP address.

    This endpoint takes a query parameter 'visitor_name' and
    uses the requester's IP address to determine their location.
    It then fetches the current temperature for that location
    and returns a greeting message along with the temperature.

    Query Parameters:
    - visitor_name (str): The name of the visitor to greet.

    Returns:
    - JSON response with the following structure:
        {
            "client_ip": "127.0.0.1",  # The IP address of the requester
            "location": "New York",  # The city of the requester
            "greeting": "Hello, Mark!, the temperature is 11 degrees
            Celsius in New York"  # A greeting message with the temperature
        }
    """
    visitor_name = request.args.get('visitor_name', 'Mark')
    client_ip = request.remote_addr
    
    ipinfo_url = f'http://ip-api.com/json/{client_ip}'


    location_response = requests.get(ipinfo_url)
    if location_response.status_code == 200:
        location_data = location_response.json()
        location = location_data.get('city')
    else:
        print(f"Error fetching data. Status code: {location_response.status_code}")

    weather_url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}'.format(
        location, OPENWEATHERMAP_API_KEY)
    weather_response = requests.get(weather_url)
    weather_data = weather_response.json()
    temperature = weather_data.get('main', {}).get(
        'temp', '32')

    response = {
        "client_ip": client_ip,
        "location": location,
        "greeting": f"Hello, {visitor_name}!, the temperature is {temperature} degrees Celsius in {location}"
    }

    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)