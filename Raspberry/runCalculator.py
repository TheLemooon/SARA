import numpy as np
from run import Run
from imageArray import ImageArray
from datetime import datetime
import time
from PyQt5.QtCore import QObject, pyqtSignal, QThread, pyqtSlot

class RunCalculator(QObject):
    signalNewRun = pyqtSignal(Run,ImageArray) #device id, time since interrupt, is auto interrupt
    
    def __init__(self):
        super().__init__()
        self.runs = [] #start, stop, 
        self.deviceList = np.array([1,2])#front = startdevice end = goalDevice
    
    @pyqtSlot(int,float,bool)
    def addInterrupt(self,id,time,isAtuomatic):
        if (self.deviceList[0] == id) and self.runs[len(self.runs)-1].isComplete(): # start new run
            run = Run()
            run.setStart(time,isAtuomatic)
            self.runs.append(run, ImageArray())#ImageArray is Placeholder
        elif (self.deviceList[len(self.deviceList)] == id) and not self.runs[len(self.runs)-1][0].isComplete():#finish run
            #get pictures
            self.runs[len(self.runs)-1][0].setStop(time)
            self.signalNewRun.emit(self.runs[len(self.runs)-1][0],self.runs[len(self.runs)-1][1])
        elif (self.deviceList[0] == id) and not isAtuomatic and not self.runs[len(self.runs)-1][0].isComplete():#override start with manual
            self.runs[len(self.runs)-1][0].setStart(time,isAtuomatic)
        elif self.deviceList[len(self.deviceList)] != id and self.deviceList[0] != id:#zwischenzeit
            return
        else:
            return
    
    @pyqtSlot(int,int)  
    def adjustStopTime(self, runNr, imageNumber):
        if runNr < len(self.runs):
            img, time, sucessfull = self.runs[runNr][1].getImageAndTime(imageNumber)
            if sucessfull:
                self.runs[runNr][0].setStop(time)
         
    @pyqtSlot()        
    def run(self):
        while True:
            pass