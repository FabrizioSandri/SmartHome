import urllib
import json
import requests
import socket
import time
from datetime import datetime
from Utilities import Utilities

class BatteriesDataManager:
    
    def __init__(self, session, solaredgeEnv, teslaEnv, elios4youEnv):
        
        # Solaredge data
        self.api_key = solaredgeEnv["api_key"]
        self.site_id = solaredgeEnv["site_id"]
        self.solaredgeUrl = f"https://monitoringapi.solaredge.com/site/{self.site_id}"
        
        # Tesla data
        self.gateway_ip = teslaEnv["gateway_ip"]
        self.gateway_email = teslaEnv["gateway_email"]
        self.gateway_password = teslaEnv["gateway_password"]

        # Elios4you data
        self.device_ip = elios4youEnv["device_ip"]
        self.device_port = elios4youEnv["device_port"]


        ## session for the specific user
        self.session = session

        # if the user already have an AuthCookie for Tesla get it from the session, otherwise set it to a 
        # temporary wrong cookie -> in the next request will be updated
        teslaAuthCookie = session.get("teslaAuthCookie")
        self.teslaAuthCookies = {
            "AuthCookie": 'teslauthcookie' if teslaAuthCookie is None else teslaAuthCookie
        }
        
        #TODO disable
        requests.packages.urllib3.disable_warnings() 
        

    
    ############# TESLA data requests #############

    '''
    ottiene il json presente sulla pagina specificata da requestUrl tramite le API
    del gateway di Tesla
    '''
    def teslaRequest(self, requestUrl):
        firstLoop = True
        jsonResponse = {"code": 200}

        while(firstLoop or ("code" in jsonResponse and jsonResponse["code"] == 401)):
            
            if firstLoop is False: # generate a new AuthCookie on the second loop (error code 401)
                try:
                    self.getAuthCookie() 
                except Exception as e:
                    print("ERRORE getAuthCookie")

            firstLoop = False

            response = requests.get(requestUrl, cookies=self.teslaAuthCookies, verify=False)
            jsonResponse = json.loads(response.text)
            
        return jsonResponse

    '''
    gets Tesla gateway auth-token
    '''
    def getAuthCookie(self):
        requestUrl = "https://" + self.gateway_ip + "/api/login/Basic"
        params = {
            "username":"customer",
            "password": self.gateway_password,
            "email": self.gateway_email
        }

        response = requests.post(requestUrl, params, verify=False)
        jsonResponse = json.loads(response.text)

        self.teslaAuthCookies["AuthCookie"] = jsonResponse["token"]
        self.session["teslaAuthCookie"] = jsonResponse["token"] # assign the new cookie to the user session


    '''
    gets Tesla battery percentage
    '''
    def getBatteryPercentage(self):
        requestUrl = "https://" + self.gateway_ip + "/api/system_status/soe"

        jsonResponse = self.teslaRequest(requestUrl)
        
        apiPercentage = jsonResponse["percentage"]
        # fix app percetange different from gateway percentage : app = (api - 5)/0.95
        appPercentage = (apiPercentage - 5)/0.95

        return round(appPercentage, 1)

    
    '''
    gets Tesla aggregates data
        site -> rete
        battery
        load -> casa
        solar
    '''
    def getAggregatesData(self):
        requestUrl = "https://" + self.gateway_ip + "/api/meters/aggregates"

        jsonResponse = self.teslaRequest(requestUrl)

        for agg in ("site", "load", "battery", "solar"):
            jsonResponse[agg]["instant_power"] = float(jsonResponse[agg]["instant_power"])/1000.0 # convert W/h to Kw/h 
            jsonResponse[agg]["instant_power"] = round(jsonResponse[agg]["instant_power"], 1 )

        return jsonResponse


    '''
    gets Tesla system version
    '''
    def getVersion(self):
        requestUrl = "https://" + self.gateway_ip + "/api/status"

        jsonResponse = self.teslaRequest(requestUrl)

        return jsonResponse["version"]
        

    ############# SOLAREDGE data requests #############

    '''
    Returns current site power in Watts/Hour
    '''
    def getCurrentPower(self):
        requestUrl = self.solaredgeUrl + f"/overview?api_key={self.api_key}" 
        response = urllib.request.urlopen(requestUrl)

        jsonResponse = json.loads(response.read())
        return jsonResponse["overview"]["currentPower"]["power"]


    '''
    Returns site details
    '''
    def getDetails(self):
        requestUrl = self.solaredgeUrl + f"/overview?api_key={self.api_key}" 
        response = urllib.request.urlopen(requestUrl)
        jsonResponse = json.loads(response.read())

        result = {}

        result["currentPower"] = jsonResponse["overview"]["currentPower"]["power"]/1000 # W -> kW
        result["lastDayEnergy"] = jsonResponse["overview"]["lastDayData"]["energy"]/1000
        result["lastMonthEnergy"] = jsonResponse["overview"]["lastMonthData"]["energy"]/1000
        result["lastYearEnergy"] = jsonResponse["overview"]["lastYearData"]["energy"]/1000

        return result

    '''
    Returns produced energy in Kw/h for the specified date
    '''
    def getEnergyProduced(self, date):
        requestUrl = self.solaredgeUrl + f"/energy?timeUnit=DAY&endDate={date}&startDate={date}&api_key={self.api_key}"
        response = urllib.request.urlopen(requestUrl)
        jsonResponse = json.loads(response.read())
    
        result = str(int(jsonResponse["energy"]["values"][0]["value"] or 0)/1000) # W -> kW

        return result

    '''
    Returns energy power for a specific day
    '''
    def getDailySolarPower(self, date):
        requestUrl = self.solaredgeUrl + f"/power?startTime={date}%2000:00:00&endTime={date}%2023:59:00&api_key={self.api_key}"
        response = urllib.request.urlopen(requestUrl)
        jsonResponse = json.loads(response.read())

        result = {
            "time" : [],
            "value" : []
        }

        for elem in jsonResponse["power"]["values"]:
            result["time"].append(elem["date"].split(" ")[1])
            if elem["value"] == None:
                result["value"].append(0)   
            else:
                result["value"].append(round(elem["value"] / 1000 , 2) ) # W/h -> kW/h

        return result



    ############# ELIOS4YOU requests #############
    
    '''
    Elios4You device command runner 

    Params:
        - command: command to execute
        - prefix: command prefix
        - outputMaxLen: the maximum output result length (2^x)
    
    Returns:
        - string : the commnad output
        - 2 : device communication error

    '''
    def executeCommand(self, command, prefix, outputMaxLen):
        try:
            ## SOCKET send command
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TCP socket
            sock.connect((self.device_ip, self.device_port))

            res = sock.send(command)

            if (res):
                commandResponse = sock.recv(outputMaxLen)
                ### DEBUG: print("RES: " + commandResponse.decode("utf-8"))
                if commandResponse.decode("utf-8")[:len(prefix)] == prefix:
                    sock.close()
                    return(commandResponse.decode("utf-8"))
        except: 
            return 2

        return 0

    ''' 
    Boost della resistenza fino alle ore specificate da "endTime".

    Ritorna:
        - 1 : boost attivato
        - 0 : errore orario errato
        - 2 : errore di connessione con il dispositivo E4U
    '''
    def boost(self, endTime):
       
        if (Utilities.checkHour(endTime)): # hour format check
            fullEndTime = datetime.now().strftime("%Y-%m-%d ") + endTime # include the day in order to get the correct UNIX timestamp

            nowTimestamp = datetime.timestamp(datetime.now())
            endTimestamp = datetime.timestamp(datetime.strptime(fullEndTime, "%Y-%m-%d %H:%M"))
            timeDiff = round(endTimestamp - nowTimestamp)
            
            if timeDiff > 0: # check if future hour
                command = bytes(f"@BOO 10000 {timeDiff}\n", "utf-8")

                result = self.executeCommand(command, "Activate", 512)
                if result == 2:
                    return 2

                return 1

        return 0

    ''' 
    Switch della resistenza a stato OFF oppure AUTO

    Parametri:
        status: 
            - off
            - auto

    Ritorna:
        - 1 : stato aggiornato
        - 2 : errore di connessione con il dispositivo E4U
    '''
    def changePowerReducerStatus(self, status):
        
        command = ""
        if status=="off":
            command = bytes(f"@BOO 0 65535\n", "utf-8") # off
        else:
            command = bytes(f"@BOO 0 1\n", "utf-8")     # auto

        result = self.executeCommand(command, "Activate", 512)
        if result == 2:
            return 2
        
        return 1

    '''
    ottiene gli schedule giornalieri per la resistenza per tutta la settimana

    Ritorna:
        - array of strings: schedule
        - 2 : errore di connessione con il dispositivo E4U
    '''
    def getPowerReducerSchedules(self):

        schedules = []

        for i in range(7): ## giorni della settimana
            schedules.append(self.getPowerReducerDailySchedule(i))

        return schedules


    '''
    ottiene lo schedule giornaliero per la resistenza nel giorno day-esimo

    Parametri:
        - day   0 Lunedi
                1 Martedi
                2 Mercoledi
    Ritorna:
        - string schedule : schedule ottenuto con successo
        - 0 : errore giorno sbagliato
        - 2 : errore di connessione con il dispositivo E4U
    '''
    def getPowerReducerDailySchedule(self, day):

        if day >= 0 and day <= 6 :
            command = bytes(f"@PRS 0 {day}\n", "utf-8")

            result = self.executeCommand(command, "@PRS", 512)
            if result == 2 or result == 0:
                return 2

            return(result[7:-15]) # [7:-15] removes unused data ("ready, @PRS ...")

        return 0
        

    '''
    ritorna i dati live del dispositivo in formato dizionario

    Ritorna:
        - 2 : errore di connessione col device
        - dictionary : successo
    '''
    def getOnlineData(self):
        command = bytes(f"@dat\n", "utf-8")

        result = self.executeCommand(command, "@DAT", 1024)
        if type(result) == int: # ritorna il codice di errore
            return result
            
        return(self.parseOnlineData(result))


    '''
    effettua il parsing dei dati "online" ritornati dal comando @dat
    '''
    def parseOnlineData(self, onlineDataResponse):

        splittedLines = onlineDataResponse.split("\n;")

        reducerPower = splittedLines[27].split(";")[1]
        boostActive = splittedLines[28].split(";")[1]
        boostRemaining = 0
        status = "OFF"

        if boostActive == "0" :
            status = "AUTO"
        else:
            if reducerPower == "0":
                status = "OFF"
            else:
                status = "BOOST"
                boostRemaining = splittedLines[31].split(";")[1] # tempo di boost rimanente
                boostRemaining = time.strftime('%H:%M:%S', time.gmtime(int(boostRemaining)))


        result = {
            "reducerPower": reducerPower,
            "boostActive": boostActive,
            "boostRemaining": boostRemaining,
            "status": status
        }

        return result