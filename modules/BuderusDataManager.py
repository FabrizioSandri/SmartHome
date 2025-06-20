import requests
import json
import base64
import hashlib
import binascii
import pandas as pd
import os
import math

from pyaes import PADDING_NONE, AESModeOfOperationECB, Decrypter
from datetime import datetime
import time

class BuderusDataManager:
    
    # costanti per AES (non cambaire)
    MAGIC = bytearray.fromhex("867845e97c4e29dce522b9a7d3a3e07b152bffadddbed7f5ffd842e9895ad1e4")
    BS = 16

    def __init__(self, historical_data_location, gateway_ip, gateway_secret, gateway_password):

        gp_hash = hashlib.md5(bytearray(gateway_secret, "utf8") + self.MAGIC)
        pp_hash = hashlib.md5(self.MAGIC + bytearray(gateway_password, "utf8"))
        _saved_key = gp_hash.hexdigest() + pp_hash.hexdigest()

        self.key = binascii.unhexlify(_saved_key)
        self.historical_data_location = historical_data_location
        self.gateway_ip = gateway_ip

    '''
    padding per la codifica / decodifica AES
    '''
    def pad(self, s):
        """Pad of encryption."""
        return s + ((self.BS - len(s) % self.BS) * chr(0))


    '''
    decodifica una stringa "enc" ottenuta dal gateway in formato base64
    '''
    def decrypt(self, enc):
        if enc and len(enc) > 2:
            enc = base64.b64decode(enc)
            cipher = Decrypter(
                AESModeOfOperationECB(self.key),
                padding=PADDING_NONE)
            decrypted = cipher.feed(enc) + cipher.feed()

            return decrypted.decode("utf8").rstrip(chr(0))
        return "{}"

    '''
    ottiene il json presente sulla pagina specificata da requestUrl tramite le API
    del gateway di Buderus
    '''
    def buderusRequest(self, requestUrl):
        headers = {
            'User-Agent': 'TeleHeater',
            'Connection': 'Close'
        }
        
        requestUrl = "http://" + self.gateway_ip + requestUrl

        # decodifica della risposta
        try:
            encryptedResponse = requests.get(requestUrl, headers=headers, verify=False)
            decryptedResponse = self.decrypt(encryptedResponse.text)
        except requests.exceptions.RequestException as e:  
            decryptedResponse = '{}'

        jsonResponse = json.loads(decryptedResponse)
        
        return jsonResponse


    '''
    ritorna la temperatura di tutti gli heating circuits
    '''
    def getHeatingCircuitsTemperature(self, date):
        heatingCircuitsNum = 4

        hours = []
        heatingCircuits = []

        # labels ore
        for hour in range(0, 24):
            hours.append(hour)

        # valori per ogni Heating Circuit
        for hc in range(1, heatingCircuitsNum+1):
            measure = []

            requestUrl = f"/recordings/heatingCircuits/hc{hc}/roomtemperature?interval={date}" 
            recordings = self.buderusRequest(requestUrl)["recording"]
            if (recordings == -1):  # Error handling
                return -1

            for hour in range(0, 24):
                value = recordings[hour]["y"]
                c = recordings[hour]["c"]
                if c == 0 or value < 0: # se valori negativi non ha senso
                    measure.append(0)
                else:
                    measure.append(math.floor( (float(value) / float(c)) * 100 ) / 100)

            heatingCircuits.append(measure)


        # valori per le temeprature
        boilerTemperatures = []

        requestUrl = f"/recordings/dhwCircuits/dhw1/actualTemp?interval={date}" 
        recordings = self.buderusRequest(requestUrl)["recording"]
        if (recordings == -1):  # Error handling
            return -1

        for hour in range(0, 24):
            value = recordings[hour]["y"]
            c = recordings[hour]["c"]
            if c == 0 or value < 0: # se valori negativi non ha senso
                boilerTemperatures.append(0)
            else:
                boilerTemperatures.append(float(value) / float(c))

        # result
        temperatures = {
            "hours" : hours,
            "heatingCircuits" : heatingCircuits,
            "boilerTemperatures" : boilerTemperatures
        }

        return json.dumps(temperatures)
    


    '''
    ritorna l'energia consumata dalla pompa di calore
    '''
    def getDaillyConsumedEnergy(self, date):
        date_time = datetime.strptime(date, '%Y-%m-%d').strftime("%Y%m%d")
        fileLocation = os.path.join(self.historical_data_location, "consumed" , f"{date_time}_buderus.csv")

        data = {
            "hours": list(range(0,24)),
            "measure": [None] * 24
        }
        
        if os.path.isfile(fileLocation):
            dataframe = pd.read_csv(fileLocation)

            hours = dataframe.iloc[:,0].values
            measure = dataframe.iloc[:,1].values
            
            data = {
                "hours" : hours.tolist(),
                "measure" : measure.tolist()
            }

        return data

    '''
    ritorna l'energia consuamta dalla pompa a calore / caldaia
    '''
    def saveDaillyConsumedEnergy(self, date):
        requestUrl = "/recordings/heatSources/total/energyMonitoring/consumedEnergy?interval=" + date

        recordings = self.buderusRequest(requestUrl)["recording"]
        if (recordings == -1):  # Error handling
            return -1
        
        hours = []
        measure = []
        for hour in range(0, 24):
            hours.append(hour)

            value = recordings[hour]["y"]
            c = recordings[hour]["c"]
            if c == 0:
                measure.append(0)
            else:
                measure.append(round(float(value) / float(c) , 0))
                
        date_time = datetime.strptime(date, "%Y-%m-%d").strftime("%Y%m%d")

        # dump to file
        fileLocation = os.path.join(self.historical_data_location, "consumed" , f"{date_time}_buderus.csv")
        dataframe = pd.DataFrame({"hours" : hours, "measure" : measure})
        dataframe.to_csv(fileLocation, index=False)

        return "Success"



    '''
    ritorna l'energia Mensile consuamta dalla pompa a calore / caldaia
    '''
    def getMonthlyConsumedEnergy(self, date):
        requestUrl = "/recordings/heatSources/total/energyMonitoring/consumedEnergy?interval=" + date

        recordings = self.buderusRequest(requestUrl)["recording"]
        if (recordings == -1):  # Error handling
            return -1
        
        days = []
        measure = []
        for day in range(0, len(recordings)): # Nota: day parte da 0
            days.append(day + 1) # +1 perchè day parte da 0

            # valori
            value = recordings[day]["y"]
            c = recordings[day]["c"]
            if c == 0:
                measure.append(0)
            else:
                measure.append(round(float(value) / float(60) , 2) )
                

        consumedEnergy = {
            "days" : days,
            "measure" : measure
        }

        return json.dumps(consumedEnergy)

    def getMonthlyConsumedEnergyFile(self, date):
        parsedDate = datetime.strptime(date, "%Y-%m")

        month = parsedDate.strftime("%m")
        year = parsedDate.strftime("%Y")
        fileLocation = os.path.join(self.historical_data_location, f"{year}{month}_buderus.csv")

        return (fileLocation)


    '''
    salva i dati mensili della pompa di calore
    '''
    def saveMonthlyConsumedEnergy(self, date):
        parsedDate = datetime.strptime(date, "%Y-%m")

        month = parsedDate.strftime("%m")
        year = parsedDate.strftime("%Y")
        fileLocation = os.path.join(self.historical_data_location, f"{year}{month}_buderus.csv")

        monthlyConsumedEnergy = json.loads(self.getMonthlyConsumedEnergy(date))
        dataframe = pd.DataFrame(monthlyConsumedEnergy)
        dataframe = dataframe.rename(columns={'days': 'giorno', 'measure': 'Energia consumata (Kw/h)'})
        dataframe.to_csv(fileLocation, index=False)
        
        return(monthlyConsumedEnergy)


    '''
    ritorna l'energia consumata mensilmente, presa da file e non direttamente dal sistema buderus
    '''
    def getMonthlyConsumedEnergyFromFile(self, date):
        parsedDate = datetime.strptime(date, "%Y-%m")

        month = parsedDate.strftime("%m")
        year = parsedDate.strftime("%Y")
        fileLocation = os.path.join(self.historical_data_location, f"{year}{month}_buderus.csv")

        if os.path.isfile(fileLocation):

            dataframe = pd.read_csv(fileLocation)

            days = dataframe.iloc[:,0].values
            measure = dataframe.iloc[:,1].values
            
            consumedEnergy = {
                "days" : days.tolist(),
                "measure" : measure.tolist()
            }

            return json.dumps(consumedEnergy)

        return 0
    
    def getTotalMonthlyConsumedEnergy(self):
        """
        Scan all files named 'YYYYMM_buderus.csv' in self.historical_data_location,
        compute the sum of the second column (kW consumed) for each month,
        and return a JSON string mapping 'YYYY-MM' -> total_kW.
        """
        averages = {}

        for fname in os.listdir(self.historical_data_location):
            if not fname.endswith("_buderus.csv"):
                continue

            basename = fname[:-len("_buderus.csv")]
            if len(basename) != 6 or not basename.isdigit():
                continue

            year = basename[:4]
            month = basename[4:6]
            key = f"{year}-{month}"

            path = os.path.join(self.historical_data_location, fname)
            try:
                df = pd.read_csv(path)
                print(df)
                avg = df.iloc[:, 1].sum()
            except Exception as e:
                print(e)
                continue

            averages[key] = round(float(avg), 2)
        print(averages)
        return averages

    '''
    ottiene dati generali sull'impianto
    '''
    def getGeneralData(self):
        heatingCircuitsNum = 4

        requestUrl = f"/dhwCircuits/dhw1/currentSetpoint" 
        response = self.buderusRequest(requestUrl)
        if response == -1:
            return -1
        setpointAttuale = response["value"]

        requestUrl = f"/dhwCircuits/dhw1/actualTemp" 
        response = self.buderusRequest(requestUrl)
        if response == -1:
            return -1
        temperaturaAttuale = response["value"]

        requestUrl = f"/system/sensors/temperatures/outdoor_t1" 
        response = self.buderusRequest(requestUrl)
        if response == -1:
            return -1
        temperaturaEsterna = response["value"]

        requestUrl = f"/heatSources/actualModulation" 
        response = self.buderusRequest(requestUrl)
        if response == -1:
            return -1
        modulazionePompa = response["value"]

        requestUrl = f"/system/appliance/actualSupplyTemperature" 
        response = self.buderusRequest(requestUrl)
        if response == -1:
            return -1
        temperaturaMandata = response["value"]

        if setpointAttuale == -1 or temperaturaAttuale == -1 or temperaturaEsterna == -1 or modulazionePompa == -1 or temperaturaMandata == -1:  # Error handling
            return -1
        
        temperatureHc = {
            "setPointAmbiente" : [],
            "temperaturaAmbiente" : [],
            "temperaturaMandata" : []
        }
        
        for hc in range(1, heatingCircuitsNum+1):
            requestUrl = f"/heatingCircuits/hc{hc}/currentRoomSetpoint" 
            response = self.buderusRequest(requestUrl)
            if response == -1:
                return -1
            temperatureHc["setPointAmbiente"].append(response["value"])

            requestUrl = f"/heatingCircuits/hc{hc}/roomtemperature" 
            response = self.buderusRequest(requestUrl)
            if response == -1:
                return -1
            temperatureHc["temperaturaAmbiente"].append(response["value"])

            requestUrl = f"/heatingCircuits/hc{hc}/actualSupplyTemperature" 
            response = self.buderusRequest(requestUrl)
            if response == -1:
                return -1
            temperatureHc["temperaturaMandata"].append(response["value"])


        # dati finali
        data = {
            "setpointAttuale" : setpointAttuale,
            "temperaturaAttuale": temperaturaAttuale,
            "temperaturaEsterna": temperaturaEsterna,
            "modulazionePompa": modulazionePompa,
            "temperaturaMandata": temperaturaMandata,
            "temperatureHc": temperatureHc
        }

        return json.dumps(data)


    '''
    Save some daily information about the pump, like the external temperature
    and the modulation
    '''
    def saveGeneralInformation(self):
        requestUrl = f"/system/sensors/temperatures/outdoor_t1" 
        response = self.buderusRequest(requestUrl)
        if response == -1:
            return -1
        externalTemperature = response["value"]

        requestUrl = f"/heatSources/actualModulation" 
        response = self.buderusRequest(requestUrl)
        if response == -1:
            return -1
        modulation = response["value"]
        
        now = datetime.now() 
        date_time = now.strftime("%Y%m%d")
        unixtime = str(int(time.mktime(now.timetuple())))
        fileLocation = os.path.join(self.historical_data_location, "info" , f"{date_time}_buderus.csv")

        if not os.path.isfile(fileLocation):
            with open(fileLocation, "a") as datafile:
                datafile.write("dateTime,externalTemperature,modulation\n")
                datafile.write("{},{},{}\n".format(unixtime, externalTemperature, modulation))
        else:
            with open(fileLocation, "a") as datafile:
                datafile.write("{},{},{}\n".format(unixtime, externalTemperature, modulation))

        return "Success"

    '''
    Get the daily information about the pump
    '''
    def getGeneralInformation(self, date):

        date_time = datetime.strptime(date, '%Y-%m-%d').strftime("%Y%m%d")
        fileLocation = os.path.join(self.historical_data_location, "info" , f"{date_time}_buderus.csv")

        data = {}
        if os.path.isfile(fileLocation):
            dataframe = pd.read_csv(fileLocation)

            dateTime = dataframe.iloc[:,0].values
            externalTemperature = dataframe.iloc[:,1].values
            modulation = dataframe.iloc[:,2].values
            
            data = {
                "dateTime" : dateTime.tolist(),
                "externalTemperature" : externalTemperature.tolist(),
                "modulation": modulation.tolist()
            }

        return data