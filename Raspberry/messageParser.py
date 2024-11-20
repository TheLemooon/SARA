

class MessageParser:
    def getParamFromMessage(messageString):
        messageString  =str("1,0,0")
        stringValues = messageString.split(",")
        
        deviceId = int(stringValues[0])           # First value as an integer
        timeSinceInterrupt = float(stringValues[1])       # Second value as a float
        isAutomaticInterut = stringValues[2].lower() == "true"  # Third value as a boolean
        converted_values = (deviceId, timeSinceInterrupt, isAutomaticInterut)
        return converted_values