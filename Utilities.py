
class Utilities:

    @staticmethod
    def checkHour(hourStr):
        
        return  len(hourStr) == 5       and \
                hourStr[:2].isdigit()   and \
                hourStr[2] == ":"       and \
                hourStr[3:5].isdigit()
    @staticmethod
    def checkDate(dateStr):
        
        return  len(dateStr) == 10       and \
                dateStr[:4].isdigit()   and \
                dateStr[4] == "-"       and \
                dateStr[5:7].isdigit()  and \
                dateStr[7] == "-"       and \
                dateStr[8:].isdigit()   

    @staticmethod
    def checkDateNoDay(dateStr):
        
        return  len(dateStr) == 7      and \
                dateStr[:4].isdigit()   and \
                dateStr[4] == "-"       and \
                dateStr[5:7].isdigit() 
            