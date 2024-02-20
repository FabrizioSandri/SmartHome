from flask import Flask
from flask import render_template
from flask import send_file
from flask import request
from flask import jsonify
from flask import session
from flask import Response
from flask import send_from_directory

from modules.WeatherDataManager import WeatherDataManager
from modules.BatteriesDataManager import BatteriesDataManager
from modules.BuderusDataManager import BuderusDataManager
from modules.VoipDataManager import VoipDataManager
from modules.Camera import Camera
from Utilities import Utilities
from functools import wraps

import json
import os
from datetime import datetime

# Env variables
envFile = open("./ENV.json", "r", encoding='utf-8')
envData = json.load(envFile)
envFile.close()

app = Flask(__name__)
app.secret_key = envData['session_secret_key']
app.config['SESSION_TYPE'] = 'filesystem'

voipDataManager = VoipDataManager(envData["router"]["ip"], envData["router"]["username"], envData["router"]["password"])

# Configure permanent session
@app.before_request
def make_session_permanent():
    session.permanent = True

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')

def requires_auth():
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if session.get("authenticated") or request.args.get("salt", None, None) == envData['buderus']['download_secret']:
                return f(*args, **kwargs)
            else: # need to authenticate
                return render_template("login.html", vars=envData["vars"])
        return decorated
    return wrapper

@app.route('/', methods = ['GET'])
@requires_auth()
def index():
    return render_template("index.html", vars=envData["vars"])

################################################################################
#### AUTHENTICATION 
################################################################################
@app.route('/login', methods = ['POST', 'GET'])
def login():

    password = request.form.get("pass", None, None)
    if (password and password == envData["interface_password"]):
        session["authenticated"] = True
        return render_template("index.html", vars=envData["vars"])
    else:
        return render_template("login.html", vars=envData["vars"])


################################################################################
#### WEATHER 
################################################################################
@app.route('/weather', methods = ['GET', 'POST'])
@requires_auth()
def weather():
    if request.method == 'POST' :
        date = request.form.get("date", None, None)
        precision = request.form.get("precision", None, None)
    elif request.method == 'GET':
        date = request.args.get("date", None, None)
        precision = request.args.get("precision", None, None)
    else:
        return "Method not supported"

    # Missing date 
    if not date:
        return render_template("weather_date.html", vars=envData["vars"], weather=envData["weather"], error="Nessuna data speficata")         

    gap = envData["weather"]["default_chart_gap"]
    if precision:
        gap = int(int(precision)/2) # one data point is retrieved once every 2 seconds
        gap = 1 if gap < 1 else gap
    try:
        weatherDataManager = WeatherDataManager(envData["weather"]["historical_data_location"], envData["weather"]["historical_data_prefix"], date)

        properties = ["windSpeed", "outTemp", "inTemp", "barometer", "outHumidity", "inHumidity", "dayRain"]
        chartData = weatherDataManager.getChartData(properties, gap)
        statistics = weatherDataManager.getStatistic(properties)

        return render_template("weather.html", chartData=chartData, date=date, statistics=statistics, vars=envData["vars"])
    except Exception as e: # No data found for the selected date
        return render_template("weather_date.html", vars=envData["vars"], weather=envData["weather"], error="Nessun dato trovato per il giorno selezionato.")         

@app.route('/weather/historical', methods = ['GET'])
@requires_auth()
def download_historical_file():

    date = request.args.get("datehistorical", None, None)
    precision = request.args.get("precisionhistorical", envData["weather"]["default_chart_gap"], int)
    
    filename = f"{envData['weather']['historical_data_prefix']}-{date}.csv"

    if filename != ""  and precision:
        
        fileLocation = os.path.join(envData["weather"]["historical_data_location"], filename)
        precision = int(precision)
        
        if os.path.isfile(fileLocation):
            newFileLocation = WeatherDataManager.getFitleredHisoricalFile(fileLocation, precision)

            return send_file(newFileLocation)
        else:
            return "File non trovato"

    else:
        return "Specifica un file e una precisione corretti"

@app.route('/weather/historicalMonth', methods = ['GET'])
@requires_auth()
def download_monthly_historical_file():

    month = request.args.get("mese", None, None)
    year = request.args.get("anno", None, None)
    if int(month) < 10:
        month = '0' + month

    fileLocationFirstOfMonth = os.path.join(envData["weather"]["historical_data_location"], f"{envData['weather']['historical_data_prefix']}-{year}-{month}-01.csv")

    # if the file for the first of the month does not exist then there is no
    # data for that specific month
    if os.path.isfile(fileLocationFirstOfMonth):

        monthDatasetLocation = WeatherDataManager.getMonthHisoricalFile(envData["weather"]["historical_data_location"], envData["weather"]["historical_data_prefix"], year, month)
        if monthDatasetLocation != 0:
            return send_file(monthDatasetLocation)
        else:
            return "Errore nell'estrazione dei dati"
    
    else:
        return "Nessun dato trovato per il mese specificato"

# get forecast icon, sunrise and sunset
@app.route('/weather/getForecast', methods = ['GET'])
@requires_auth()
def getWeatherForecast():
    
    nowDate = datetime.now() 
    yearMonthDay = nowDate.strftime("%Y-%m-%d")

    historical_prefix = envData["weather"]["historical_data_prefix"]
    hisotricalDataLocation = envData["weather"]["historical_data_location"]
    filename = f"{historical_prefix}-{yearMonthDay}.csv"
    fileLocation = os.path.join(hisotricalDataLocation, filename)
    
    return WeatherDataManager.getForecast(fileLocation)

# get monthly rain
@app.route('/weather/getMonthRain', methods = ['GET'])
@requires_auth()
def getMonthRain():
            
    month = request.args.get("mese", None, None)
    year = request.args.get("anno", None, None)
    if int(month) < 10:
        month = '0' + month

    fileLocationLastOfMonth = Utilities.getLastFileOfMonth(os.path.join(envData["weather"]["historical_data_location"], f"{envData['weather']['historical_data_prefix']}"), month, year)
    if fileLocationLastOfMonth is not None:
        historical_prefix = envData["weather"]["historical_data_prefix"]
        hisotricalDataLocation = envData["weather"]["historical_data_location"]
        fileLocation = os.path.join(hisotricalDataLocation, fileLocationLastOfMonth)

        forecast = WeatherDataManager.getForecast(fileLocation)
        jsonParsed = json.loads(forecast)
        return jsonParsed["monthRain"]
        
    else:
        return "0.0"

################################################################################
#### BATTERIES 
################################################################################
@app.route('/batteries', methods = ['GET'])
@requires_auth()
def batteries():

    batteriesDataManager = BatteriesDataManager(session, envData["solaredge"], envData["tesla"], envData["elios4you"])
    
    teslaData = {
        "batteryPercentage" : batteriesDataManager.getBatteryPercentage(),
        "aggregates" : batteriesDataManager.getAggregatesData(),
        "version" : batteriesDataManager.getVersion()
    }
    siteDetails = batteriesDataManager.getDetails()

    return render_template("batteries.html", siteDetails=siteDetails, teslaData=teslaData, vars=envData["vars"])

################################################################################
#### SOLAREDGE 
################################################################################
@app.route('/getEnergyProduced', methods = ['GET'])
@requires_auth()
def getEnergyProduced():
    date = request.args.get("date", None, None)
    if Utilities.checkDate(date) == False:
        return "Data errata"

    batteriesDataManager = BatteriesDataManager(session, envData["solaredge"], envData["tesla"], envData["elios4you"])
    energyProduced = batteriesDataManager.getEnergyProduced(date)
    
    return energyProduced


## get every quarte of an hour the power value in kW/h
@app.route('/getDailySolarPower', methods = ['GET'])
@requires_auth()
def getDailySolarPower():

    date = request.args.get("date", None, None)
    if Utilities.checkDate(date) == False:
        return "Data errata"

    batteriesDataManager = BatteriesDataManager(session, envData["solaredge"], envData["tesla"], envData["elios4you"])
    powerProduction = batteriesDataManager.getDailySolarPower(date)
    
    return powerProduction

#################### TESLA ####################

@app.route('/batteryPercentage', methods = ['GET'])
@requires_auth()
def batteryPercentage():
    batteriesDataManager = BatteriesDataManager(session, envData["solaredge"], envData["tesla"], envData["elios4you"])
    return(str(batteriesDataManager.getBatteryPercentage()))

@app.route('/batteriesUsageChart', methods = ['GET', 'POST'])
@requires_auth()
def batteriesUsageChart():

    batteriesDataManager = BatteriesDataManager(session, envData["solaredge"], envData["tesla"], envData["elios4you"])

    teslaData = {
        "batteryPercentage" : batteriesDataManager.getBatteryPercentage(),
        "aggregates" : batteriesDataManager.getAggregatesData(),
        "version" : batteriesDataManager.getVersion()
    }

    return render_template("batteriesUsageChart.html", teslaData=teslaData, vars=envData["vars"])

#################### ELIOS4YOU ####################

@app.route('/boost', methods = ['POST'])
@requires_auth()
def boost():
    
    endTime = request.form.get("endtime", None, None)      

    batteriesDataManager = BatteriesDataManager(session, envData["solaredge"], envData["tesla"], envData["elios4you"])
    res = batteriesDataManager.boost(endTime)
    if (res == 1):
        return "Boost avviato"
    elif(res == 0):
        return "Fornisci un orario corretto"
    else:
        return "Errore di connessione con il dispositivo E4U"

@app.route('/e4u_data', methods = ['GET'])
@requires_auth()
def e4u_data():

    batteriesDataManager = BatteriesDataManager(session, envData["solaredge"], envData["tesla"], envData["elios4you"])
    e4uOnlineData = batteriesDataManager.getOnlineData()

    if (e4uOnlineData == 0):
        return jsonify({"error": "Errore di connessione con il dispositivo E4U"})
    elif (e4uOnlineData == 2):
        return jsonify({"error": "Segnale debole"})
    else:
        return jsonify(e4uOnlineData)

@app.route('/changePowerReducerStatus', methods = ['POST'])
@requires_auth()
def changePowerReducerStatus():
    
    status = request.args.get("status", None, None)    

    batteriesDataManager = BatteriesDataManager(session, envData["solaredge"], envData["tesla"], envData["elios4you"])
    res = batteriesDataManager.changePowerReducerStatus(status)
    if (res == 1):
        return "Stato aggiornato"
    else:
        return "Errore di connessione con il dispositivo E4U"


@app.route('/getPowerReducerSchedule', methods = ['GET'])
@requires_auth()
def getPowerReducerSchedule():

    batteriesDataManager = BatteriesDataManager(session, envData["solaredge"], envData["tesla"], envData["elios4you"])
    powerReducerSchedules = batteriesDataManager.getPowerReducerSchedules()
    
    if powerReducerSchedules[0] == 2:
        return ("Segnale dispositivo E4U assente")
        
    return jsonify(powerReducerSchedules)


################################################################################
#### BUDERUS/BOSCH HEATER
################################################################################
@app.route('/buderus', methods = ['GET'])
@requires_auth()
def buderus():
    return render_template("buderus.html")
        
@app.route('/buderus/getDaillyConsumedEnergy', methods = ['GET'])
@requires_auth()
def buderusGetDaillyConsumedEnergy():

    date = request.args.get("date", None, None)        
    if Utilities.checkDate(date) == False: # Check date validity
        return "Data errata"

    buderusDataManager = BuderusDataManager(envData["buderus"]["historical_data_location"], envData["buderus"]["gateway_ip"], envData["buderus"]["gateway_secret"], envData["buderus"]["gateway_password"])
    response = buderusDataManager.getDaillyConsumedEnergy(date)
    if response == -1:
        return response

    return jsonify(response)

@app.route('/buderus/saveDaillyConsumedEnergy', methods = ['GET'])
@requires_auth()
def saveDaillyConsumedEnergy():
    date = request.args.get("date", None, None)
                
    if Utilities.checkDate(date) == False: # Check date validity
        return "Data errata"

    buderusDataManager = BuderusDataManager(envData["buderus"]["historical_data_location"], envData["buderus"]["gateway_ip"], envData["buderus"]["gateway_secret"], envData["buderus"]["gateway_password"])
    return str(buderusDataManager.saveDaillyConsumedEnergy(date))


@app.route('/buderus/energyConsumedMonthly', methods = ['GET'])
@requires_auth()
def buderusEnergyConsumedMonthly():
    
    date = request.args.get("date", None, None)    
    if Utilities.checkDateNoDay(date) == False: # Check date validity
        return "Data errata"

    buderusDataManager = BuderusDataManager(envData["buderus"]["historical_data_location"], envData["buderus"]["gateway_ip"], envData["buderus"]["gateway_secret"], envData["buderus"]["gateway_password"])
    return str(buderusDataManager.getMonthlyConsumedEnergyFromFile(date))


@app.route('/buderus/saveEnergyConsumedMonthly', methods = ['GET'])
@requires_auth()
def buderusSaveEnergyConsumedMonthly():
    date = request.args.get("date", None, None)
                
    if Utilities.checkDateNoDay(date) == False: # Check date validity
        return "Data errata"

    buderusDataManager = BuderusDataManager(envData["buderus"]["historical_data_location"], envData["buderus"]["gateway_ip"], envData["buderus"]["gateway_secret"], envData["buderus"]["gateway_password"])       
    return buderusDataManager.saveMonthlyConsumedEnergy(date)


@app.route('/buderus/temperatures', methods = ['GET'])
@requires_auth()
def buderusTemperatures():

    date = request.args.get("date", None, None)
                
    if Utilities.checkDate(date) == False: # Check date validity
        return "Data errata"

    buderusDataManager = BuderusDataManager(envData["buderus"]["historical_data_location"], envData["buderus"]["gateway_ip"], envData["buderus"]["gateway_secret"], envData["buderus"]["gateway_password"])
    return str(buderusDataManager.getHeatingCircuitsTemperature(date))

@app.route('/buderus/downloadMonthlyPowerConsume', methods = ['GET'])
@requires_auth()
def buderusDownloadMonthlyPowerConsume():

    month = request.args.get("mese", None, None)
    year = request.args.get("anno", None, None)

    if int(month) < 10:
        month = '0' + month

    date = year + "-" + month

    if Utilities.checkDateNoDay(date) == False: # Check date validity
        return "Data errata"

    buderusDataManager = BuderusDataManager(envData["buderus"]["historical_data_location"], envData["buderus"]["gateway_ip"], envData["buderus"]["gateway_secret"], envData["buderus"]["gateway_password"])
    return send_file(buderusDataManager.getMonthlyConsumedEnergyFile(date))


@app.route('/buderus/getGeneralData', methods = ['GET'])
@requires_auth()
def buderusgetGeneralData():
            
    buderusDataManager = BuderusDataManager(envData["buderus"]["historical_data_location"], envData["buderus"]["gateway_ip"], envData["buderus"]["gateway_secret"], envData["buderus"]["gateway_password"])
    return buderusDataManager.getGeneralData()


@app.route('/buderus/saveGeneralInformation', methods = ['GET'])
@requires_auth()
def buderusSaveGeneralInformation():
    buderusDataManager = BuderusDataManager(envData["buderus"]["historical_data_location"], envData["buderus"]["gateway_ip"], envData["buderus"]["gateway_secret"], envData["buderus"]["gateway_password"])
    return buderusDataManager.saveGeneralInformation()


@app.route('/buderus/getGeneralInformation', methods = ['GET'])
@requires_auth()
def buderusGetGeneralInformation():
        
    date = request.args.get("date", None, None)           
    if Utilities.checkDate(date) == False: # Check date validity
        return "Data errata"

    buderusDataManager = BuderusDataManager(envData["buderus"]["historical_data_location"], envData["buderus"]["gateway_ip"], envData["buderus"]["gateway_secret"], envData["buderus"]["gateway_password"])
    response = buderusDataManager.getGeneralInformation(date)
    if response == -1:
        return -1
        
    return jsonify(response)


'''
@app.route('/buderus/test', methods = ['GET', 'POST'])
def buderusTesting():
    if session.get("authenticated") :
        
        path = request.args.get("path", None, None)
        buderusDataManager = BuderusDataManager(envData["buderus"]["historical_data_location"], envData["buderus"]["gateway_ip"], envData["buderus"]["gateway_secret"], envData["buderus"]["gateway_password"])
        recordings = buderusDataManager.buderusRequest(path)
        
        return jsonify(recordings)

    else: # need to authenticate
        return render_template("login.html")
'''


################################################################################
#### SURVEILLANCE
################################################################################
def gen_frames(videoCaptureSource):  
    while True:
        frame = videoCaptureSource.getFrame()  # read the videoCaptureSource frame
        frame = frame.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n') 


@app.route('/surveillance', methods = ['GET'])
@requires_auth()
def surveillance():
    return render_template('surveillance.html', vars=envData["vars"], cameras=json.dumps(list(envData["surveillance"].keys())))


@app.route('/surveillance/video_feed', methods = ['GET'])
@requires_auth()
def video_feed():
    cameraid = request.args.get("cameraid", None, None)
    numCameras = request.args.get("numCameras", None, None) # in order to resize the image

    cameraData = envData["surveillance"][cameraid]
    
    httpStream = f"http://{cameraData['username']}:{cameraData['password']}@{cameraData['ip']}:{cameraData['http_port']}/ipcam/mjpeg{cameraData['stream']}.cgi"
    camera = Camera(httpStream, numCameras)
    
    return Response(gen_frames(camera), mimetype='multipart/x-mixed-replace; boundary=frame')


################################################################################
#### SETTINGS
################################################################################
@app.route('/settings', methods = ['GET'])
@requires_auth()
def settings():
    # filter the envData variable
    filtered_envData = {
        "vars": {
            "house_name": envData["vars"]["house_name"],
            "weather_location": envData["vars"]["weather_location"]
        },
        "weather": {
            "historical_data_location": envData["weather"]["historical_data_location"],
            "historical_data_prefix": envData["weather"]["historical_data_prefix"],
            "default_chart_gap": envData["weather"]["default_chart_gap"]
        },
        "buderus": {
            "download_secret": envData["buderus"]["download_secret"],
            "gateway_ip": envData["buderus"]["gateway_ip"],
            "historical_data_location": envData["buderus"]["historical_data_location"]                
        },
        "solaredge": {
            "api_key": envData["solaredge"]["api_key"],
            "site_id": envData["solaredge"]["site_id"]
        },
        "tesla": {
            "gateway_ip": envData["tesla"]["gateway_ip"],
            "gateway_email": envData["tesla"]["gateway_email"]
        },
        "elios4you": {
            "device_ip": envData["elios4you"]["device_ip"],
            "device_port": envData["elios4you"]["device_port"]
        },
        "surveillance": {
            "Orto": {i:envData["surveillance"]["Orto"][i] for i in envData["surveillance"]["Orto"] if i!='password'},
            "Portoni": {i:envData["surveillance"]["Portoni"][i] for i in envData["surveillance"]["Portoni"] if i!='password'},
            "Entrata": {i:envData["surveillance"]["Entrata"][i] for i in envData["surveillance"]["Entrata"] if i!='password'},
            "Giardino": {i:envData["surveillance"]["Giardino"][i] for i in envData["surveillance"]["Giardino"] if i!='password'},
            "Terrazzo": {i:envData["surveillance"]["Terrazzo"][i] for i in envData["surveillance"]["Terrazzo"] if i!='password'}
        }
    }

    return render_template('settings.html', vars=envData["vars"], envData=filtered_envData)
    

@app.route('/settings/save', methods = ['POST'])
@requires_auth()
def settings_save():

    old_password = request.form.get("old_password", default=None)  
    if old_password != envData["interface_password"]:
        return "Password errata, non sei autorizzato a modificre le impostazioni"

    interface_password = request.form.get("interface_password", default=envData["interface_password"])  
    house_name = request.form.get("house_name", default=envData["vars"]["house_name"])  
    weather_location = request.form.get("weather_location", default=envData["vars"]["weather_location"]) 
    weather_historical_data_location = request.form.get("weather_historical_data_location", default=envData["weather"]["historical_data_location"]) 
    historical_data_prefix = request.form.get("historical_data_prefix", default=envData["weather"]["historical_data_prefix"]) 
    default_chart_gap = request.form.get("default_chart_gap", default=envData["weather"]["default_chart_gap"], type=int) 
    download_secret = request.form.get("download_secret", default=envData["buderus"]["download_secret"]) 
    buderus_gateway_ip = request.form.get("buderus_gateway_ip", default=envData["buderus"]["gateway_ip"]) 
    gateway_secret = envData["buderus"]["gateway_secret"] if len(request.form.get("gateway_secret"))==0 else request.form.get("gateway_secret", default=envData["buderus"]["gateway_secret"]) 
    buderus_gateway_password = envData["buderus"]["gateway_password"] if len(request.form.get("buderus_gateway_password"))==0  else request.form.get("buderus_gateway_password", default=envData["buderus"]["gateway_password"]) 
    buderus_historical_data_location = request.form.get("buderus_historical_data_location", default=envData["buderus"]["historical_data_location"]) 
    api_key = request.form.get("api_key", default=envData["solaredge"]["api_key"]) 
    site_id = request.form.get("site_id", default=envData["solaredge"]["site_id"]) 
    tesla_gateway_ip = request.form.get("tesla_gateway_ip", default=envData["tesla"]["gateway_ip"]) 
    gateway_email = request.form.get("gateway_email", default=envData["tesla"]["gateway_email"]) 
    tesla_gateway_password = envData["tesla"]["gateway_password"] if len(request.form.get("gateway_password"))==0 else request.form.get("gateway_password", default=envData["tesla"]["gateway_password"]) 
    device_ip = request.form.get("device_ip", default=envData["elios4you"]["device_ip"]) 
    device_port = request.form.get("device_port", default=envData["elios4you"]["device_port"], type=int)  


    for cam in range(1,len(envData["surveillance"])+1):
        cam_name = request.form.get("cam%d_name_hidden" % cam, default=None)
        envData["surveillance"][cam_name]["ip"] = request.form.get("cam%d_ip" % cam, default=envData["surveillance"][cam_name]["ip"])
        envData["surveillance"][cam_name]["http_port"] = request.form.get("cam%d_http_port" % cam, default=envData["surveillance"][cam_name]["http_port"])
        envData["surveillance"][cam_name]["username"] = request.form.get("cam%d_username" % cam, default=envData["surveillance"][cam_name]["username"])
        envData["surveillance"][cam_name]["password"] = envData["surveillance"][cam_name]["password"] if len(request.form.get("cam%d_password" % cam)) == 0 else request.form.get("cam%d_password" % cam, default=envData["surveillance"][cam_name]["password"])
        envData["surveillance"][cam_name]["stream"] = request.form.get("cam%d_stream" % cam, default=envData["surveillance"][cam_name]["stream"])
        
    envData["interface_password"] = interface_password
    envData["vars"]["house_name"] = house_name
    envData["vars"]["weather_location"] = weather_location
    envData["weather"]["historical_data_location"] = weather_historical_data_location
    envData["weather"]["historical_data_prefix"] = historical_data_prefix
    envData["weather"]["default_chart_gap"] = default_chart_gap
    envData["buderus"]["download_secret"] = download_secret
    envData["buderus"]["gateway_ip"] = buderus_gateway_ip
    envData["buderus"]["gateway_secret"] = gateway_secret
    envData["buderus"]["gateway_password"] = buderus_gateway_password
    envData["buderus"]["historical_data_location"] = buderus_historical_data_location
    envData["solaredge"]["api_key"] = api_key
    envData["solaredge"]["site_id"] = site_id
    envData["tesla"]["gateway_ip"] = tesla_gateway_ip
    envData["tesla"]["gateway_email"] = gateway_email
    envData["tesla"]["gateway_password"] = tesla_gateway_password
    envData["elios4you"]["device_ip"] = device_ip
    envData["elios4you"]["device_port"] = device_port

    envFile = open("./ENV.json", "w")
    json.dump(envData, envFile, indent=4, ensure_ascii=False)
    envFile.close()
    
    return "Impostazioni salvate correttamente"


################################################################################
#### VOIP CALLS LOG
################################################################################
@app.route('/telephone', methods = ['GET'])
@requires_auth()
def router():
    return render_template("telephone.html", vars=envData["vars"])
        
@app.route('/telephone/callsLog', methods = ['GET'])
@requires_auth()
def telephoneCallsLog():
    calls = voipDataManager.get_calls()    
    calls = sorted(calls, key=lambda x: datetime.strptime(x[0], '%d-%m-%Y %H:%M:%S'), reverse=True)
    for call in calls:
        if call[1] == envData["router"]["telephone"]:
            call[6] = 1
        else:
            call[6] = 0
    return jsonify(calls)