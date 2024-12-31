from imageArray import ImageArray
from datetime import time
import cv2 as cv
import os
from enum import Enum
#from runCalculator import Mode

path = "SavedRuns/"
imgFormat = ".png"

class Mode(Enum):
    AutomaticTrigger = 1
    ManualTrigger = 2
    
class Run:
    def __init__(self):
        self.start = 0
        self.stop = 0
        self.date = 0
        self.times = []
        self.automaticStart = Mode.AutomaticTrigger
        self.imageTimes = []
        self.runIndex = -1
        self.imageCount = 0
        self.calculatedIndex = -1
        
    def setStart(self, startTime, automatic:Mode):
        self.start = startTime
        self.automaticStart = automatic
        
    def setDate(self, date):
        self.date = date
        
    def getDate(self):
        return self.date
        
    def resetStart(self):
        self.start = 0
        
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
    
    def getImageTimestamp(self, imageIndex):
        if imageIndex < len(self.imageTimes):
            return self.imageTimes[imageIndex]
        return self.stop
    
    def setRunIndex(self,idx):
        if idx >-1:
            self.runIndex = idx
            
    def getRunIndex(self):
        return self.runIndex
        
    def setImagesAndCalculatedStopTime(self,images:ImageArray):
        t, index = images.getCalculatedTimeNearestIndex()
        self.calculatedIndex = index
        self.setStop(t)
        self.saveImages(images)
        self.imageCount = images.getLength()
        
    def saveImages(self,images:ImageArray):
        print("imagecount")
        print(images.getLength())
        for i in range(0,images.getLength()):
            image, time = images.getImageAndTime(i)
            if not os.path.isdir(path + str(self.runIndex)):
                os.makedirs(path + str(self.runIndex))
            cv.imwrite(path + str(self.runIndex) + "/"+ str(i) + imgFormat,image)
            self.imageTimes.append(time)
            
    def getRunAsCSVline(self):
        return
    
    def getCalculatedIndex(self):
        return self.calculatedIndex
    
def timeToSec(time):
    return time.hour *3600 + time.minute * 60 + time.second + time.microsecond /1000000