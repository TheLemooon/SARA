

class MessageParser:
    def getParamFromMessage(self,messageString):
        #messageString  =str("1,0.000,0")
        stringValues = messageString.split(",")
        
        deviceId = int(stringValues[0])           # First value as an integer
        timeSinceInterrupt = float(stringValues[1])       # Second value as a float
        isAutomaticInterut = not stringValues[2].lower() == "true"  # Third value as a boolean
        converted_values = (deviceId, timeSinceInterrupt, isAutomaticInterut)
        return converted_values