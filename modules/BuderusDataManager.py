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
            if len(enc) % self.BS != 0:
                enc = _pad(enc)
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
        
        requestUrl = self.gateway_ip + requestUrl

        # decodifica della risposta
        encryptedResponse = requests.get(requestUrl, headers=headers, verify=False)
        decryptedResponse = self.decrypt(encryptedResponse.text)
        
        jsonResponse = json.loads(decryptedResponse)
        
        return jsonResponse

    '''
    ritorna l'energia consuamta dalla pompa a calore / caldaia
    '''
    def getConsumedEnergy(self, date):
        requestUrl = "/recordings/heatSources/total/energyMonitoring/consumedEnergy?interval=" + date

        recordings = self.buderusRequest(requestUrl)["recording"]
        
        hours = []
        measure = []
        for hour in range(0, 24):
            hours.append(hour)

            # valori
            value = recordings[hour]["y"]
            c = recordings[hour]["c"]
            if c == 0:
                measure.append(0)
            else:
                measure.append(round(float(value) / float(c) , 0))
                

        consumedEnergy = {
            "hours" : hours,
            "measure" : measure
        }

        return json.dumps(consumedEnergy)

    '''
    ritorna l'energia Mensile consuamta dalla pompa a calore / caldaia
    '''
    def getMonthlyConsumedEnergy(self, date):
        requestUrl = "/recordings/heatSources/total/energyMonitoring/consumedEnergy?interval=" + date

        recordings = self.buderusRequest(requestUrl)["recording"]
        
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
                measure.append(round(float(value) / float(60) , 0) )
                

        consumedEnergy = {
            "days" : days,
            "measure" : measure
        }

        return json.dumps(consumedEnergy)


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
    salva i dati mensili della pompa di calore
    '''
    def saveMonthlyConsumedEnergy(self, date):
        parsedDate = datetime.strptime(date, "%Y-%m")

        month = parsedDate.strftime("%m")
        year = parsedDate.strftime("%Y")
        fileLocation = os.path.join(self.self.historical_data_location, f"{year}{month}_buderus.csv")

        monthlyConsumedEnergy = json.loads(self.getMonthlyConsumedEnergy(date))
        dataframe = pd.DataFrame(monthlyConsumedEnergy)
        dataframe = dataframe.rename(columns={'days': 'giorno', 'measure': 'Energia consumata (Kw/h)'})
        dataframe.to_csv(fileLocation, index=False)

    '''
    esporta i dati mensili (specificando il mese tramite il parametro date) in formato csv.
    Il metodo ritorna la location del file csv generato
    '''
    def exportMonthlyConsumedEnergy(self, date):

        # monthlyConsumedEnergy = json.loads(self.getMonthlyConsumedEnergy(date))
        # dataframe = pd.DataFrame(monthlyConsumedEnergy)
        # dataframe = dataframe.rename(columns={'days': 'giorno', 'measure': 'Energia consumata (Kw/h)'})
        # dataframe.to_csv("/tmp/buderus.csv", index=False)

        parsedDate = datetime.strptime(date, "%Y-%m")

        month = parsedDate.strftime("%m")
        year = parsedDate.strftime("%Y")
        fileLocation = os.path.join(self.self.historical_data_location, f"{year}{month}_buderus.csv")


        return (fileLocation)

    '''
    ritorna l'energia prodotta dalla pompa di calore per il calcolo del rendimento
    '''
    def getTotalProducedEnergy(self):
        requestUrl = "/heatSources/cumulatedHeatEnergySecondBurner"

        producedEnergy = self.buderusRequest(requestUrl)["value"]

        return producedEnergy

    '''
    ottiene dati generali sull'impianto
    '''
    def getHeaderData(self):
        heatingCircuitsNum = 4

        requestUrl = f"/dhwCircuits/dhw1/currentSetpoint" 
        setpointAttuale = self.buderusRequest(requestUrl)["value"]

        requestUrl = f"/dhwCircuits/dhw1/actualTemp" 
        temperaturaAttuale = self.buderusRequest(requestUrl)["value"]

        requestUrl = f"/system/sensors/temperatures/outdoor_t1" 
        temperaturaEsterna = self.buderusRequest(requestUrl)["value"]

        requestUrl = f"/heatSources/actualModulation" 
        modulazionePompa = self.buderusRequest(requestUrl)["value"]

        requestUrl = f"/system/appliance/actualSupplyTemperature" 
        temperaturaMandata = self.buderusRequest(requestUrl)["value"]

        temperatureHc = {
            "setPointAmbiente" : [],
            "temperaturaAmbiente" : [],
            "temperaturaMandata" : []
        }
        
        for hc in range(1, heatingCircuitsNum+1):
            requestUrl = f"/heatingCircuits/hc{hc}/currentRoomSetpoint" 
            temperatureHc["setPointAmbiente"].append(self.buderusRequest(requestUrl)["value"])

            requestUrl = f"/heatingCircuits/hc{hc}/roomtemperature" 
            temperatureHc["temperaturaAmbiente"].append(self.buderusRequest(requestUrl)["value"])

            requestUrl = f"/heatingCircuits/hc{hc}/actualSupplyTemperature" 
            temperatureHc["temperaturaMandata"].append(self.buderusRequest(requestUrl)["value"])


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
