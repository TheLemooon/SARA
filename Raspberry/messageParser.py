from runCalculator import Mode 

class MessageParser:
    def getParamFromMessage(self,messageString):
        stringValues = messageString.split(",")
        
        if len(stringValues) >=3:
            deviceId = int(stringValues[0])           # First value as an integer
            timeSinceInterrupt = float(stringValues[1])       # Second value as a float
            isAutomaticInterut = Mode.AutomaticTrigger 
            if int(stringValues[2]) ==0:  # Third value as a boolean
                isAutomaticInterut = Mode.ManualTrigger 
            converted_values = (deviceId, timeSinceInterrupt, isAutomaticInterut)
            return converted_values
        return 0,-1.0,Mode.AutomaticTrigger