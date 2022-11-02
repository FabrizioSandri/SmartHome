# SmartHome
SmartHome is a Flask-based framework for controlling home automation remotely.
The framework communicates with the following devices: 
* solar system based on Tesla Powerwall 2 technology + a Solaredge inverter + a Buderus water heater 
* weather station to log and analyze previous weather data 
* home surveillance system


#### Home solar power system
This module allows the user to monitor solar panel production and view the electricity flow from the panels to the house, Tesla batteries, and the network in real time.
This module also allows the user to remotely activate a booster system to raise the temperature of the water supply.

#### Weather station
By displaying real-time data and historical charts, smart homes allow you to monitor both current and previous weather conditions. 

#### Surveillance system
This module communicates with the house surveillance system through an RTSP stream, allowing you to view the streaming in real time. 

## Usage
Before launching the system, a `ENV.json` configuration file must be created in the SmartHome folder. This file is organized as follows: 
```json
{
    "interface_password": "...",
    "session_secret_key": "...",
    "vars":{
        "house_name": "...",
        "weather_location" : "Location - State"
    },
    "weather" : {
        "historical_data_location" : "/srv/history_weather",
        "historical_data_prefix" : "prefix",
        "default_chart_gap" : 500,
        "forecast_iframe_address" : "...",
        "forecast_link_address" : "..."
    },
    "buderus":{
        "download_secret" : "...",
        "gateway_ip" : "http://192.168.1.x",
        "gateway_secret" : "...",
        "gateway_password" : "...",
        "historical_data_location" : "/srv/history_buderus"
    },
    "solaredge": {
        "api_key" : "...",
        "site_id" : "..."
    },
    "tesla" : {
        "gateway_ip" : "https://192.168.1.x",
        "gateway_email" : "...",
        "gateway_password" : "..."
    },
    "elios4you" : {
        "device_ip" : "192.168.1.x",
        "device_port" : 5001
    },
    "surveillance" : {
        "camera1" : {
            "ip" : "192.168.1.x",
            "rtsp_port" : "554",
            "username" : "...",
            "password" : "...",
            "stream" : "main"
        },
        "camera2" : {
            "ip" : "192.168.1.x",
            "rtsp_port" : "554",
            "username" : "...",
            "password" : "...",
            "stream" : "main"
        },
        "camera3" : {
            "ip" : "192.168.1.x",
            "rtsp_port" : "554",
            "username" : "...",
            "password" : "...",
            "stream" : "main"
        }
    }
}
```
