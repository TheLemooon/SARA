import numpy as np
from run import Run
from imageArray import ImageArray
from datetime import datetime
import time
from PyQt5.QtCore import QObject, pyqtSignal, QThread, pyqtSlot

class RunCalculator(QObject):
    signalNewRun = pyqtSignal(Run) #device id, time since interrupt, is auto interrupt
    signalRequestingImages = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.runs = [] #start, stop, 
        self.deviceList = np.array([1,0])#front = startdevice end = goalDevice
        self.requestedIndex = -1 #imageproccessing started
        self.threadRunning = True
        #openCameraStream
    
    @pyqtSlot(int,object,bool)
    def addInterrupt(self,id,time,isAtuomatic):
        print("run with delay:%.3f",time)
        if len(self.runs) > 0:
            if (self.deviceList[0] == id) and self.runs[len(self.runs)-1].isComplete(): # start new run
                run = Run()
                run.setStart(time,isAtuomatic)
                self.runs.append(run)#ImageArray is Placeholder
            
            elif (self.deviceList[len(self.deviceList)-1] == id) and not self.runs[len(self.runs)-1].isComplete():#finish run
                #get pictures
                self.runs[-1].setStop(time)
                if self.requestedIndex == -1:#image request not already running
                    self.requestedIndex = len(self.runs)-1
                    self.signalRequestingImages.emit()
            
            elif (self.deviceList[0] == id) and not isAtuomatic and not self.runs[len(self.runs)-1].isComplete():#override start with manual
                self.runs[len(self.runs)-1].setStart(time,isAtuomatic)
            
            elif self.deviceList[len(self.deviceList)-1] != id and self.deviceList[0] != id:#zwischenzeit
                return
            else:
                return
        else: # first run
            if (self.deviceList[0] == id):
                run = Run()
                run.setStart(time,isAtuomatic)
                self.runs.append(run)#ImageArray is Placeholder
    
    @pyqtSlot(int,int)  
    def adjustStopTime(self, runNr, imageNumber):
        if runNr < len(self.runs):
            img, time, sucessfull = self.runs[runNr].getImageAndTime(imageNumber)
            if sucessfull:
                self.runs[runNr].setStop(time)
                
    @pyqtSlot(ImageArray)
    def receiveRequestedImages(self,images:ImageArray):
        print("emited run1")
        if self.requestedIndex != -1:
            self.runs[self.requestedIndex].images = images
            self.signalNewRun.emit(self.runs[self.requestedIndex])
            print("emited run")
            if self.requestedIndex != len(self.runs)-1:#requesting newer images
                self.requestedIndex +=1
                self.signalRequestingImages.emit()
            else:
                self.requestedIndex = -1

    @pyqtSlot()        
    def run(self):
        while self.threadRunning:
            time.sleep(1)
            #TODO implement active event loop for qt queuedConnection may work if interuupts arent adde whilst staring up
        
    def stop(self):
        self.threadRunning = False