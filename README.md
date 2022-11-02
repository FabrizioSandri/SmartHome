## SmartHome
SmartHome is a Flask-based framework for controlling home automation remotely.
The framework communicates with the following devices: 
* solar system based on Tesla Powerwall 2 technology + a Solaredge inverter + a Buderus water heater 
* weather station to log and analyze previous weather data 
* home surveillance system


### Home solar power system
This module allows the user to monitor solar panel production and view the electricity flow from the panels to the house, Tesla batteries, and the network in real time.
This module also allows the user to remotely activate a booster system to raise the temperature of the water supply.

### Weather station
By displaying real-time data and historical charts, smart homes allow you to monitor both current and previous weather conditions. 

### Surveillance system
This module communicates with the house surveillance system through an RTSP stream, allowing you to view the streaming in real time. 
