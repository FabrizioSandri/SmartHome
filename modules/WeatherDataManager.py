import pandas as pd
import json
import os
from datetime import datetime

class WeatherDataManager:
   
    def __init__(self, data_path, historical_prefix, date):

        self.date = date
        self.historical_prefix = historical_prefix

        # convert string to datetimeformat
        dateObj = datetime.strptime(date, "%Y-%m-%d")
        year = dateObj.strftime("%Y")
        month = dateObj.strftime("%m")
        day = dateObj.strftime("%d")

        csv_location = f"{data_path}/{self.historical_prefix}-{year}-{month}-{day}.csv"

        # error_bad_lines=False  removes lines with more columns than specified
        self.dataset = pd.read_csv(csv_location, na_values=['None'])
        self.dataset = self.dataset.fillna(0.0)
        self.dataset = self.dataset.round(3)

    '''
    ritorna i labels giornalieri nel formato (ore:minuti:secondi)
    con una certa precisione precision (es. ogni 20 secondi)
    '''
    def getDailyLabels(self, precision):
        
        X = self.dataset.loc[:,"dateTime"]
        X = X.iloc[::precision] # select 1 every GAP rows
        XLabels = X.map(lambda x: datetime.fromtimestamp(x).strftime("%H:%M:%S"))

        return XLabels.tolist()

    '''
    ritorna i dati giornalieri 
    per una certa caratteristica "property"
    con una certa precisione precision (es. ogni 20 secondi)
    '''
    def getDailyData(self, property, precision):

        Y = self.dataset.loc[:, property]
        Y = Y.iloc[::precision]

        return Y.tolist()

    '''
    ritorna il minimo e il massimo di una certa colonna nel dataset
    '''
    def getMinMax(self, property):
        Y = self.dataset[property]

        return (Y.min(), Y.max())


    '''
    ritorna i dati da inserire nel grafico nel formato

    {
        properties : ["prop1"...."propN"],
        labels : ["00:00:00"...."23:59:59"],
        data : {
            windSpeed: [1...X]
            ...
        }
    }
    '''
    def getChartData(self, properties, precision):
        
        chartData = {}

        # get the labels
        labels = self.getDailyLabels(precision)

        # get the data for each property
        data = {}
        statistic = {}
        for prop in properties:
            data[prop] = self.getDailyData(prop, precision)
            statistic[prop] = self.getMinMax(prop)
        
            
        chartData["properties"] = properties
        chartData["labels"] = labels
        chartData["data"] = data
        chartData["statistic"] = statistic
        
        return json.dumps(chartData)

    '''
    ritorna statistiche varie sulle proprietà
    '''
    def getStatistic(self, properties):
        
        statistic = {}

        for prop in properties:
            minmax = self.getMinMax(prop)
            statistic["min_" + prop] = minmax[0] # min
            statistic["max_" + prop] = minmax[1] # max
        
        return statistic

    '''
    ritorna la location del nuovo file csv da restituire all'utente dove
    - fileLocation : e' il path dove si trova il file da ottenere
    - precision : e' un intero in secondi che specifica ogni quanto prendere i dati. 
    '''
    @staticmethod
    def getFitleredHisoricalFile(fileLocation, precision):

        # / 2 in quanto ogni riga è presa ogni 2 secondi
        gap = int(int(precision)/2)
        gap = 1 if gap < 1 else gap

        # error_bad_lines=False  removes lines with more columns than specified
        dataset = pd.read_csv(fileLocation, na_values=['None'], error_bad_lines=False)
        dataset = dataset.fillna(0.0)
        dataset = dataset.round(3)

        dataset = dataset.iloc[::gap]

        dataset.to_csv("/tmp/dataset.csv", index=False)

        return ("/tmp/dataset.csv")


    @staticmethod
    def getMonthFitleredHisoricalFile(hisotricalDataLocation, historical_prefix, year, month, precision):
        
        outFileName = f"/tmp/{historical_prefix}-{year}-{month}.csv"

        print(outFileName)

        # / 2 in quanto ogni riga è presa ogni 2 secondi
        gap = int(int(precision)/2)
        gap = 1 if gap < 1 else gap

        monthDatasets = []
        
        for day in range(1, 32):
            dayFixed = str(day)
            if day < 10:
                dayFixed = '0' + dayFixed

            filename = f"{historical_prefix}-{year}-{month}-{dayFixed}.csv"
            fileLocation = os.path.join(hisotricalDataLocation, filename)

            # se il file esiste
            if os.path.isfile(fileLocation):
                temp_dataset = pd.read_csv(fileLocation, na_values=['None'], error_bad_lines=False)
                temp_dataset = temp_dataset.fillna(0.0)
                temp_dataset = temp_dataset.round(3)

                temp_dataset = temp_dataset.iloc[::gap]

                temp_dataset['dateTime'] = pd.to_datetime(temp_dataset['dateTime'], unit='s')
                temp_dataset['dateTime'] = temp_dataset['dateTime'].dt.tz_localize('UTC').dt.tz_convert('Europe/Rome')
                temp_dataset['dateTime'] = temp_dataset['dateTime'].dt.strftime('%d-%m-%Y %H:%M:%S')
                
                monthDatasets.append(temp_dataset)

    
        if len(monthDatasets) > 0:
            fullDataset = pd.concat(monthDatasets, axis=0, ignore_index=True)
            fullDataset.to_csv(outFileName, index=False)

            return (outFileName)
        else:
            return 0

            

    @staticmethod
    def getForecast(hisotricalDataLocation, historical_prefix):
        
        forecastFile = open("./static/forecast.json", "r")
        forecast = json.load(forecastFile)
        forecastFile.close()


        nowDate = datetime.now() 
        yearMonthDay = nowDate.strftime("%Y-%m-%d")

        filename = f"{historical_prefix}-{yearMonthDay}.csv"
        fileLocation = os.path.join(hisotricalDataLocation, filename)

        today_data = open(fileLocation, 'r')
        lines = today_data.readlines()
        today_data.close()

        # get first & last line
        firstLine = lines[0].strip().split(',')
        lastLine = lines[len(lines) - 1].strip().split(',')
        lastLine = [None if i == "None" else i for i in lastLine]

        data = {firstLine[i]: lastLine[i] for i in range(len(firstLine))}

        data["sunrise"] = datetime.fromtimestamp(int(data["sunrise"])).strftime('%H:%M')
        data["sunset"] = datetime.fromtimestamp(int(data["sunset"])).strftime('%H:%M')
        data["forecastIcon"] = forecast["forecastIcon"][data["forecastIcon"]],
        data["forecastRule"] = forecast["forecastRule"][data["forecastRule"]],

        return json.dumps(data)