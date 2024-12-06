import numpy as np
from run import Run
from runTable import RunTable
from camera import CameraHandler
from server import WebSever
from SerialInterface import SerialReader
from imageArray import ImageArray
from datetime import datetime
import time
from PyQt5.QtCore import QObject, pyqtSignal, QThread, pyqtSlot, Qt, QCoreApplication

class RunCalculator(QObject):
    signalNewRun = pyqtSignal(Run) #device id, time since interrupt, is auto interrupt
    signalUpdateRun = pyqtSignal(Run)
    signalRequestingImages = pyqtSignal()
    signalChangeRunIndicator = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.runs = [] #start, stop, 
        self.runTable = RunTable()
        self.deviceList = np.array([1,0])#front = startdevice end = goalDevice
        self.requestedIndex = -1 #imageproccessing started
        self.threadRunning = True
        self.mode = True #True = automatic only / False = manual only
        
        self.camera = CameraHandler()
        self.server = WebSever()
        self.serial = SerialReader()
        self.connectSignals()
        self.camera.start()
        self.serial.start()
        self.server.start()
    
    @pyqtSlot(int,object,bool)
    def addInterrupt(self,id,time,isAutomatic):
        print("run",time)
        if self.runTable.getRunCount() > 0:
            if (self.deviceList[0] == id) and self.runTable.getLastRun().isComplete() and self.mode == isAutomatic: # start new run
                print("atartin new run")
                run = Run()
                run.setStart(time,isAutomatic)
                self.runTable.appendRun(run)#ImageArray is Placeholder
                self.signalChangeRunIndicator.emit(2)
            
            elif (self.deviceList[len(self.deviceList)-1] == id) and not self.runTable.getLastRun().isComplete():#finish run
                print("finish run")#get pictures
                self.runTable.runs[-1].setStop(time)
                if self.requestedIndex == -1:#image request not already running
                    self.requestedIndex = self.runTable.runs[-1].getRunIndex()
                    self.signalRequestingImages.emit()
                    self.signalChangeRunIndicator.emit(3)
            
            elif self.deviceList[len(self.deviceList)-1] != id and self.deviceList[0] != id:#zwischenzeit
                return
            else:
                return
        else: # first run
            if (self.deviceList[0] == id):
                run = Run()
                run.setStart(time,isAutomatic)
                self.runTable.appendRun(run)#ImageArray is Placeholder
                self.signalChangeRunIndicator.emit(2)
    
    @pyqtSlot(int,int)  
    def adjustStopTime(self, runNr, imageNumber):
        if runNr < self.runTable.getRunCount():
            time = self.runTable.runs[runNr].getImageTimestamp(imageNumber)
            self.runTable.runs[runNr].setStop(time)
            print("reemitting")
            self.signalUpdateRun.emit(self.runTable.getRun(runNr))
                
    @pyqtSlot(ImageArray)
    def receiveRequestedImages(self,images:ImageArray):
        if self.requestedIndex != -1:
            self.runTable.runs[self.requestedIndex].setImagesAndCalculatedStopTime(images)
            self.signalNewRun.emit(self.runTable.getRun(self.requestedIndex))
            self.signalChangeRunIndicator.emit(1)
            print("emited run")
            if self.requestedIndex != self.runTable.getRunCount()-1:#requesting newer images
                self.requestedIndex +=1
                self.signalRequestingImages.emit()
            else:
                self.requestedIndex = -1

    @pyqtSlot()        
    def run(self):
        time.sleep(2)
        print("starting")
        print(self.runTable.getRunCount())
        self.loadRuns()
        while self.threadRunning:
            time.sleep(1)
            #QCoreApplication.processEvents() 
            #TODO implement active event loop for qt queuedConnection may work if interuupts arent adde whilst staring up
        
    def stop(self):
        print("stoping runcalculator")
        self.runTable.saveRuns()
        self.camera.stop()
        self.serial.stop() 
        self.server.stop()
        self.threadRunning = False
        
    def connectSignals(self):
        self.signalNewRun.connect(self.server.updateTable)
        self.signalUpdateRun.connect(self.server.updateRun)
        self.serial.signalNewMessage.connect(self.addInterrupt, Qt.DirectConnection)
        self.server.signalUpdateRunTime.connect(self.adjustStopTime, Qt.DirectConnection)
        self.signalRequestingImages.connect(self.camera.stopRecordingAndProcessImages)
        self.camera.signalImagesProcessed.connect(self.receiveRequestedImages, Qt.DirectConnection)
        self.signalChangeRunIndicator.connect(self.server.changeRunIndicator)
        
    def loadRuns(self):
        self.runTable.loadRuns()
        for run in self.runTable.runs:
            self.signalNewRun.emit(run)
