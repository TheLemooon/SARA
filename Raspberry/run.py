from imageArray import ImageArray
from datetime import time

class Run:
    def __init__(self):
        self.start = 0
        self.stop = 0
        self.times = []
        self.automaticStart = True
        self.images = ImageArray()
        
    def setStart(self, startTime, automatic):
        self.start = startTime
        self.automaticStart = automatic
        
    def addTime(self, time):
        self.times.append(time)
        
    def setStop(self,stopTime):
        self.stop = stopTime
        
    def isAutomaticStart(self):
        return self.automaticStart
    
    def isComplete(self):
        if self.start != 0 and self.stop != 0:
            return True
        return False
    
    def getRunTime(self):
        return timeToSec(self.stop) - timeToSec(self.start)
    
    def getStartTime(self):
        return self.start
    
    def getStopTime(self):
        return self.stop
    
def timeToSec(time):
    return time.hour *3600 + time.minute * 60 + time.second