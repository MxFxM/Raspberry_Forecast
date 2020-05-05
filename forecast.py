import configparser
import requests
import sys
from influxdb import InfluxDBClient
 
def get_api_key():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['openweathermap']['api']

def get_limits():
    limits = configparser.ConfigParser()
    limits.read('limits.ini')
    return limits['ForecastLimits']
 
def get_forecast(api_key, location):
    url = "https://api.openweathermap.org/data/2.5/forecast?q={}&units=metric&appid={}".format(location, api_key)
    r = requests.get(url)
    return r.json()

def approve(date):
    temperature = float(date['main']['temp'])
    pressure = float(date['main']['pressure'])
    humidity = float(date['main']['humidity'])
    windspeed = float(date['wind']['speed'])
    clouds = float(date['clouds']['all'])

    limits = get_limits()

    approved = True

    if temperature < float(limits['TemperatureMinimum']):
        approved = False
    if temperature > float(limits['TemperatureMaximum']):
        approved = False

    if pressure < float(limits['PressureMinimum']):
        approved = False
    if pressure > float(limits['PressureMaximum']):
        approved = False

    if humidity < float(limits['HumidityMinimum']):
        approved = False
    if humidity > float(limits['HumidityMaximum']):
        approved = False

    if windspeed < float(limits['WindspeedMinimum']):
        approved = False
    if windspeed > float(limits['WindspeedMaximum']):
        approved = False

    if clouds < float(limits['CloudsMinimum']):
        approved = False
    if clouds > float(limits['CloudsMaximum']):
        approved = False

    return approved

def get_body(date):
    json_body = [{"measurement": "Oberderdingen",
                  "fields": {
                      "Temperature": float(date['main']['temp']),
                      "Pressure": int(date['main']['pressure']),
                      "Humidity": int(date['main']['humidity']),
                      "Windspeed": float(date['wind']['speed']),
                      "Clouds": int(date['clouds']['all']),
                      "Approved": approve(date)
                      },
                  "time": date['dt_txt']
                }]
    return json_body
 
def main():
    location = ""
    if len(sys.argv) != 2:
        #exit("Usage: {} LOCATION".format(sys.argv[0]))
        location = "Oberderdingen" # use this if no location given
    else:
        location = sys.argv[1]
 
    api_key = get_api_key()
    forecast = get_forecast(api_key, location)

    client = InfluxDBClient('localhost', 8086, 'root', 'root', 'FORECAST')
 
    for date in forecast['list']:
        client.write_points(get_body(date))


if __name__ == '__main__':
    main()
