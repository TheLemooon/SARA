

class Run:
    def __init__(self):
        self.start = 0
        self.stop = 0
        self.times = []
        self.automaticStart = True
        
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
        return self.stop - self.start
    
    def getStartTime(self):
        return self.start
    
    def getStopTime(self):
        return self.stop