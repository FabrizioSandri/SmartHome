from flask import Flask
from flask import render_template
from flask import send_file
from flask import request
from flask import jsonify
from flask import session

from modules.WeatherDataManager import WeatherDataManager
from modules.BatteriesDataManager import BatteriesDataManager
from modules.BuderusDataManager import BuderusDataManager
from Utilities import Utilities

import time
import json
import os


'''
Env variables
'''
envFile = open("./ENV.json", "r")
envData = json.load(envFile)
envFile.close()

app = Flask(__name__)
app.secret_key = envData['session_secret_key']
app.config['SESSION_TYPE'] = 'filesystem'


# set permanent session
@app.before_request
def make_session_permanent():
    session.permanent = True

@app.route('/', methods = ['GET', 'POST'])
def index():
    if session.get("authenticated") :

        if request.method == 'GET' or request.method == 'POST' :
            return render_template("index.html", vars=envData["vars"])

        else:
            return "Method not supported"

    else: # need to authenticate
        return render_template("login.html", vars=envData["vars"])

#################### LOGIN ####################
@app.route('/login', methods = ['POST'])
def login():

    if request.method == 'POST' :
        password = request.form.get("pass", None, None)
        if (password and password == envData["interface_password"]):
            session["authenticated"] = True
            return render_template("index.html", vars=envData["vars"])
        else:
            return render_template("login.html", vars=envData["vars"])
    else:
        return "Method not supported"


#################### WEATHER ####################
@app.route('/weather', methods = ['GET', 'POST'])
def weather():

    if session.get("authenticated") :

        if request.method == 'POST' :
            date = request.form.get("date", None, None)
            precision = request.form.get("precision", None, None)

        elif request.method == 'GET':
            date = request.args.get("date", None, None)
            precision = request.args.get("precision", None, None)

        else:
            return "Method not supported"

        # args check
        if not date:
            return render_template("weather_date.html", vars=envData["vars"], weather=envData["weather"]) 

        gap = envData["weather"]["default_chart_gap"]
        if precision:
            gap = int(int(precision)/2) # data is retrieved every 2 seconds
            gap = 1 if gap < 1 else gap

        try:
            weatherDataManager = WeatherDataManager(envData["weather"]["historical_data_location"], envData["weather"]["historical_data_prefix"], date)

            properties = ["windSpeed", "outTemp", "inTemp", "barometer", "outHumidity", "inHumidity", "dayRain"]
            chartData = weatherDataManager.getChartData(properties, gap)
            statistics = weatherDataManager.getStatistic(properties)

            return render_template("weather.html", chartData=chartData, date=date, statistics=statistics, vars=envData["vars"])

        except Exception as e: ## selected a date without data
            print(e)
            return render_template("weather_date.html", vars=envData["vars"], weather=envData["weather"])         

    else: # need to authenticate
        return render_template("login.html", vars=envData["vars"])

@app.route('/weather/historical', methods = ['GET'])
def download_historical_file():
    if session.get("authenticated") :
        if request.method == 'GET':

            date = request.args.get("datehistorical", None, None)
            precision = request.args.get("precisionhistorical", None, None)

            filename = f"{envData['weather']['historical_data_prefix']}-{date}.csv"

            if filename != ""  and precision.isnumeric():
                
                fileLocation = os.path.join(envData["weather"]["historical_data_location"], filename)
                precision = int(precision)
                
                if os.path.isfile(fileLocation):
                    newFileLocation = WeatherDataManager.getFitleredHisoricalFile(fileLocation, envData["weather"]["historical_data_prefix"], precision)

                    return send_file(newFileLocation)
                else:
                    return "File non trovato"

            else:
                return "Specifica un file e una precisione corretti"
        else:
            return "Method not supported"

    else: # need to authenticate
        return render_template("login.html", vars=envData["vars"])

@app.route('/weather/historicalMonth', methods = ['GET'])
def download_monthly_historical_file():
    if session.get("authenticated") :
        if request.method == 'GET':

            month = request.args.get("mese", None, None)
            year = request.args.get("anno", None, None)
            precision = request.args.get("precisionMonth", None, None)

            if int(month) < 10:
                month = '0' + month

            if precision.isnumeric():
                fileLocationFirstOfMonth = os.path.join(envData["weather"]["historical_data_location"], f"{envData['weather']['historical_data_prefix']}-{year}-{month}-01.csv")

                # se il file del 1 del mese esiste allora ok
                if os.path.isfile(fileLocationFirstOfMonth):

                    monthDatasetLocation = WeatherDataManager.getMonthFitleredHisoricalFile(envData["weather"]["historical_data_location"], year, month, precision)
                    if monthDatasetLocation != 0:
                        return send_file(monthDatasetLocation)
                    else:
                        return "Errore nell'estrazione dei dati"
                
                else:
                    return "Nessun dato trovato per il mese specificato"

            else:
                return "Specifica una precisione in secondi corretta"
        else:
            return "Method not supported"

    else: # need to authenticate
        return render_template("login.html", vars=envData["vars"])

# forecast istantaneo della stazione meteo
@app.route('/weather/getForecast', methods = ['GET', 'POST'])
def getWeatherForecast():
    if session.get("authenticated") :

        if request.method == 'GET':
            
            return WeatherDataManager.getForecast(envData["weather"]["historical_data_location"], envData["weather"]["historical_data_prefix"])

        else:
            return "Method not supported"

    else: # need to authenticate
        return render_template("login.html", vars=envData["vars"])

#################### BATTERIE ####################

@app.route('/batteries', methods = ['GET', 'POST'])
def batteries():
    if session.get("authenticated") :

        if request.method == 'GET':
            batteriesDataManager = BatteriesDataManager(session, envData["solaredge"], envData["tesla"], envData["elios4you"])
            
            teslaData = {
                "batteryPercentage" : batteriesDataManager.getBatteryPercentage(),
                "aggregates" : batteriesDataManager.getAggregatesData(),
                "version" : batteriesDataManager.getVersion()
            }
            siteDetails = batteriesDataManager.getDetails()

            
            return render_template("batteries.html", siteDetails=siteDetails, teslaData=teslaData, vars=envData["vars"])

        else:
            return "Method not supported"

    else: # need to authenticate
        return render_template("login.html", vars=envData["vars"])

################## SOLAREDGE ##################

@app.route('/getEnergyProduced', methods = ['GET', 'POST'])
def getEnergyProduced():
    if session.get("authenticated") :

        if request.method == 'GET':

            date = request.args.get("date", None, None)
                        
            # TODO CHECK DATE
            if Utilities.checkDate(date) == False:
                return "Data errata"

            batteriesDataManager = BatteriesDataManager(session, envData["solaredge"], envData["tesla"], envData["elios4you"])
            energyProduced = batteriesDataManager.getEnergyProduced(date)
            
            return energyProduced

        else:
            return "Method not supported"

    else: # need to authenticate
        return render_template("login.html", vars=envData["vars"])


## get every quarte of an hour the power value in kW/h
@app.route('/getDailySolarPower', methods = ['GET', 'POST'])
def getDailySolarPower():
    if session.get("authenticated") :

        if request.method == 'GET':

            date = request.args.get("date", None, None)
                        
            # TODO CHECK DATE
            if Utilities.checkDate(date) == False:
                return "Data errata"

            batteriesDataManager = BatteriesDataManager(session, envData["solaredge"], envData["tesla"], envData["elios4you"])
            powerProduction = batteriesDataManager.getDailySolarPower(date)
            
            return powerProduction

        else:
            return "Method not supported"

    else: # need to authenticate
        return render_template("login.html", vars=envData["vars"])

#################### TESLA ####################

@app.route('/batteryPercentage', methods = ['GET', 'POST'])
def batteryPercentage():
    if session.get("authenticated") :

        if request.method == 'GET':
            batteriesDataManager = BatteriesDataManager(session, envData["solaredge"], envData["tesla"], envData["elios4you"])
            return(str(batteriesDataManager.getBatteryPercentage()))
        else:
            return "Method not supported"

    else: # need to authenticate
        return render_template("login.html", vars=envData["vars"])


@app.route('/batteriesUsageChart', methods = ['GET', 'POST'])
def batteriesUsageChart():
    if session.get("authenticated") :

        if request.method == 'GET' or request.method == 'POST':
            batteriesDataManager = BatteriesDataManager(session, envData["solaredge"], envData["tesla"], envData["elios4you"])

            teslaData = {
                "batteryPercentage" : batteriesDataManager.getBatteryPercentage(),
                "aggregates" : batteriesDataManager.getAggregatesData(),
                "version" : batteriesDataManager.getVersion()
            }

            return render_template("batteriesUsageChart.html", teslaData=teslaData, vars=envData["vars"])
        else:
            return "Method not supported"

    else: # need to authenticate
        return render_template("login.html", vars=envData["vars"])

#################### ELIOS4YOU ####################

@app.route('/boost', methods = ['GET', 'POST'])
def boost():
    
    if session.get("authenticated") :

        if request.method == 'POST':

            endTime = request.form.get("endtime", None, None)      

            batteriesDataManager = BatteriesDataManager(session, envData["solaredge"], envData["tesla"], envData["elios4you"])
            res = batteriesDataManager.boost(endTime)
            if (res == 1):
                return "Boost avviato"
            elif(res == 0):
                return "Fornisci un orario corretto"
            else:
                return "Errore di connessione con il dispositivo E4U"

        else:
            return "Method not supported"
    else: # need to authenticate
        return render_template("login.html", vars=envData["vars"])

@app.route('/e4u_data', methods = ['GET', 'POST'])
def e4u_data():
    
    if session.get("authenticated") :
        if request.method == 'GET' or request.method == 'POST':

            batteriesDataManager = BatteriesDataManager(session, envData["solaredge"], envData["tesla"], envData["elios4you"])
            e4uOnlineData = batteriesDataManager.getOnlineData()

            if (e4uOnlineData == 0):
                return jsonify({"error": "Errore di connessione con il dispositivo E4U"})
            elif (e4uOnlineData == 2):
                return jsonify({"error": "Segnale debole"})
            else:
                return jsonify(e4uOnlineData)

        else:
            return "Method not supported"

    else: # need to authenticate
        return render_template("login.html", vars=envData["vars"])

@app.route('/changePowerReducerStatus', methods = ['GET', 'POST'])
def changePowerReducerStatus():
    
    if session.get("authenticated") :
        if request.method == 'POST':

            status = request.args.get("status", None, None)    

            batteriesDataManager = BatteriesDataManager(session, envData["solaredge"], envData["tesla"], envData["elios4you"])
            res = batteriesDataManager.changePowerReducerStatus(status)
            if (res == 1):
                return "Stato aggiornato"
            else:
                return "Errore di connessione con il dispositivo E4U"

        else:
            return "Method not supported"
    
    else: # need to authenticate
        return render_template("login.html", vars=envData["vars"])


@app.route('/getPowerReducerSchedule', methods = ['GET', 'POST'])
def getPowerReducerSchedule():
    if session.get("authenticated") :

        if request.method == 'GET':

            batteriesDataManager = BatteriesDataManager(session, envData["solaredge"], envData["tesla"], envData["elios4you"])
            powerReducerSchedules = batteriesDataManager.getPowerReducerSchedules()
            
            if powerReducerSchedules[0] == 2:
                return ("Segnale dispositivo E4U assente")
                
            return jsonify(powerReducerSchedules)

        else:
            return "Method not supported"

    else: # need to authenticate
        return render_template("login.html", vars=envData["vars"])


#################### BUDERUS / BOSCH ####################

@app.route('/buderus', methods = ['GET', 'POST'])
def buderus():
    if session.get("authenticated") :

        if request.method == 'GET':

            return render_template("buderus.html", vars=envData["vars"])

        else:
            return "Method not supported"

    else: # need to authenticate
        return render_template("login.html", vars=envData["vars"])

@app.route('/buderus/energyConsumed', methods = ['GET', 'POST'])
def buderusEnergyConsumed():
    if session.get("authenticated") :

        if request.method == 'GET':
            
            date = request.args.get("date", None, None)
                        
            if Utilities.checkDate(date) == False: # controllo validita data
                return "Data errata"

            buderusDataManager = BuderusDataManager(envData["buderus"]["historical_data_location"], envData["buderus"]["gateway_ip"], envData["buderus"]["gateway_secret"], envData["buderus"]["gateway_password"])

            return str(buderusDataManager.getConsumedEnergy(date))

        else:
            return "Method not supported"

    else: # need to authenticate
        return render_template("login.html", vars=envData["vars"])


@app.route('/buderus/energyConsumedMonthly', methods = ['GET', 'POST'])
def buderusEnergyConsumedMonthly():
    if session.get("authenticated") :

        if request.method == 'GET':
            
            date = request.args.get("date", None, None)
                        
            if Utilities.checkDateNoDay(date) == False: # controllo validita data
                return "Data errata"

            buderusDataManager = BuderusDataManager(envData["buderus"]["historical_data_location"], envData["buderus"]["gateway_ip"], envData["buderus"]["gateway_secret"], envData["buderus"]["gateway_password"])

            return str(buderusDataManager.getMonthlyConsumedEnergy(date))

        else:
            return "Method not supported"

    else: # need to authenticate
        return render_template("login.html", vars=envData["vars"])


@app.route('/buderus/saveEnergyConsumedMonthly', methods = ['GET', 'POST'])
def buderusSaveEnergyConsumedMonthly():
    if session.get("authenticated") or request.args.get("salt", None, None) == envData['buderus']['download_secret'] :

        if request.method == 'GET':
            
            date = request.args.get("date", None, None)
                        
            if Utilities.checkDateNoDay(date) == False: # controllo validita data
                return "Data errata"

            buderusDataManager = BuderusDataManager(envData["buderus"]["historical_data_location"], envData["buderus"]["gateway_ip"], envData["buderus"]["gateway_secret"], envData["buderus"]["gateway_password"])
            buderusDataManager.saveMonthlyConsumedEnergy(date)

            return "OK"

        else:
            return "Method not supported"

    else: # need to authenticate
        return render_template("login.html", vars=envData["vars"])



@app.route('/buderus/temperatures', methods = ['GET', 'POST'])
def buderusTemperatures():
    if session.get("authenticated") :

        if request.method == 'GET':
            
            date = request.args.get("date", None, None)
                        
            if Utilities.checkDate(date) == False: # controllo validita data
                return "Data errata"

            buderusDataManager = BuderusDataManager(envData["buderus"]["historical_data_location"], envData["buderus"]["gateway_ip"], envData["buderus"]["gateway_secret"], envData["buderus"]["gateway_password"])
            
            return str(buderusDataManager.getHeatingCircuitsTemperature(date))

        else:
            return "Method not supported"

    else: # need to authenticate
        return render_template("login.html")


@app.route('/buderus/downloadMonthlyPowerConsume', methods = ['GET', 'POST'])
def buderusDownloadMonthlyPowerConsume():
    if session.get("authenticated"):

        if request.method == 'GET':
            
            month = request.args.get("mese", None, None)
            year = request.args.get("anno", None, None)

            if int(month) < 10:
                month = '0' + month

            date = year + "-" + month

            if Utilities.checkDateNoDay(date) == False: # controllo validita data
                return "Data errata"

            buderusDataManager = BuderusDataManager(envData["buderus"]["historical_data_location"], envData["buderus"]["gateway_ip"], envData["buderus"]["gateway_secret"], envData["buderus"]["gateway_password"])
            return send_file(buderusDataManager.exportMonthlyConsumedEnergy(date))


        else:
            return "Method not supported"

    else: # need to authenticate
        return render_template("login.html", vars=envData["vars"])


@app.route('/buderus/getGeneralData', methods = ['GET', 'POST'])
def buderusgetGeneralData():
    if session.get("authenticated") :

        if request.method == 'GET':
            
            buderusDataManager = BuderusDataManager(envData["buderus"]["historical_data_location"], envData["buderus"]["gateway_ip"], envData["buderus"]["gateway_secret"], envData["buderus"]["gateway_password"])
            data = buderusDataManager.getHeaderData()

            return data


        else:
            return "Method not supported"

    else: # need to authenticate
        return render_template("login.html", vars=envData["vars"])


@app.route('/buderus/getTotalProducedEnergy', methods = ['GET', 'POST'])
def buderusGetTotalProducedEnergy():
    if session.get("authenticated") or request.args.get("salt", None, None) == envData['buderus']['download_secret'] :

        if request.method == 'GET':
            
            buderusDataManager = BuderusDataManager(envData["buderus"]["historical_data_location"], envData["buderus"]["gateway_ip"], envData["buderus"]["gateway_secret"], envData["buderus"]["gateway_password"])
            data = buderusDataManager.getTotalProducedEnergy()

            return str(data)

        else:
            return "Method not supported"

    else: # need to authenticate
        return render_template("login.html")

'''
@app.route('/buderus/test', methods = ['GET', 'POST'])
def buderusTesting():
    if session.get("authenticated") :

        if request.method == 'GET':
            
            path = request.args.get("path", None, None)
            buderusDataManager = BuderusDataManager(envData["buderus"]["historical_data_location"], envData["buderus"]["gateway_ip"], envData["buderus"]["gateway_secret"], envData["buderus"]["gateway_password"])
            recordings = buderusDataManager.buderusRequest(path)

            return jsonify(recordings)
        else:
            return "Method not supported"

    else: # need to authenticate
        return render_template("login.html")

'''