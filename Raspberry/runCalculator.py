import numpy as np
from datetime import date
import time
import subprocess
import os
from PyQt5.QtCore import QObject, pyqtSignal, QThread, pyqtSlot, Qt, QCoreApplication,  QTimer
from INA219 import INA219

from run import Run, Mode
from runTable import RunTable
from camera import CameraHandler
from server import WebSever
from SerialInterface import SerialReader
from imageArray import ImageArray

runTimeoutMs = 600000# in ms
accuUpdateIntervalMs = 60000#in ms

class RunCalculator(QObject):
    signalNewRun = pyqtSignal(Run) #device id, time since interrupt, is auto interrupt
    signalUpdateRun = pyqtSignal(Run)
    signalRequestingImages = pyqtSignal()
    signalChangeRunIndicator = pyqtSignal(int)
    signalSendSerialMsg = pyqtSignal(str)
    signalAccuUpdate = pyqtSignal(float)
    
    def __init__(self):
        super().__init__()
        self.runs = [] #start, stop, 
        self.runTable = RunTable()
        self.deviceList = np.array([2,1])#front = startdevice end = goalDevice
        self.requestedIndex = -1 #imageproccessing started
        self.threadRunning = True
        self.mode = Mode.AutomaticTrigger
        self.timer = QTimer()
        self.timer.singleShot(runTimeoutMs,self.runTimerout)
        self.accuTimer = QTimer()
        self.accuTimer.setInterval(accuUpdateIntervalMs)#1min
        self.accuTimer.timeout.connect(self.updateAkkuPercentage)
        
        self.camera = CameraHandler()
        self.server = WebSever()
        self.serial = SerialReader()
        self.connectSignals()
        self.camera.start()
        self.serial.start()
        self.server.start()
        time.sleep(1000)#guarantees that webserver is running
        
        self.ic2Connection = INA219(addr=0x41)
        self.updateAkkuPercentage()
        self.accuTimer.start(accuUpdateIntervalMs)
    
    @pyqtSlot(int,object,Mode)
    def addInterrupt(self,id,time,isAutomatic):
        print("run",time)
        #d = bytes.fromhex(0x002C04)
        #print(d)
        
        if self.runTable.getRunCount() > 0:
            if (self.deviceList[0] == id) and self.runTable.getLastRun().isComplete() and self.mode == isAutomatic: # start new run
                print("atartin new run")
                if self.runTable.runs[-1].getStartTime() != 0:# if run is not reset
                    run = Run()
                    self.runTable.appendRun(run)#ImageArray is Placeholder
                self.runTable.runs[-1].setStart(time,isAutomatic)
                self.runTable.runs[-1].setDate(date.today())
                self.signalChangeRunIndicator.emit(2)
                self.timer.singleShot(runTimeoutMs,self.runTimerout)
                self.timer.start()
                self.signalSendSerialMsg.emit("0,4\n") 
            
            elif (self.deviceList[len(self.deviceList)-1] == id) and not self.runTable.getLastRun().isComplete():#finish run
                print("finish run")#get pictures
                self.runTable.runs[-1].setStop(time)
                self.timer.stop()
                if self.requestedIndex == -1:#image request not already running
                    self.requestedIndex = self.runTable.runs[-1].getRunIndex()
                    self.signalRequestingImages.emit()
                    self.signalChangeRunIndicator.emit(3)
                    self.signalSendSerialMsg.emit("0,5\n") 
            
            elif self.deviceList[len(self.deviceList)-1] != id and self.deviceList[0] != id:#zwischenzeit
                return
            else:
                return
        else: # first run
            if (self.deviceList[0] == id):
                print("first run")
                run = Run()
                run.setStart(time,isAutomatic)
                run.setDate(date.today())
                self.runTable.appendRun(run)#ImageArray is Placeholder
                self.signalChangeRunIndicator.emit(2)
                self.timer.singleShot(runTimeoutMs,self.runTimerout)
                self.timer.start()
                self.signalSendSerialMsg.emit("0,4\n") 
    
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
            self.thread().msleep(10)
            QCoreApplication.processEvents()
        
    def stop(self):
        print("stoping runcalculator")
        self.runTable.saveRuns()
        self.camera.stop()
        self.serial.stop() 
        self.server.stop()
        self.threadRunning = False
        #subprocess.call(["sudo","shutdown"])
        print("shutdownCalled")
        os._exit(0)
        
    def connectSignals(self):
        self.signalNewRun.connect(self.server.updateTable)
        self.signalUpdateRun.connect(self.server.updateRun)
        self.serial.signalNewMessage.connect(self.addInterrupt)#, Qt.DirectConnection)
        self.server.signalUpdateRunTime.connect(self.adjustStopTime, Qt.DirectConnection)
        self.signalRequestingImages.connect(self.camera.stopRecordingAndProcessImages)
        self.camera.signalImagesProcessed.connect(self.receiveRequestedImages, Qt.DirectConnection)
        self.signalChangeRunIndicator.connect(self.server.changeRunIndicator)
        self.server.signalResetRun.connect(self.resetCurrentRun, Qt.DirectConnection)
        self.server.signalChangeMode.connect(self.changeMode, Qt.DirectConnection)
        self.server.signalPowerOff.connect(self.powerOff, Qt.DirectConnection)
        self.server.signalDeleteData.connect(self.deleteAllRuns, Qt.DirectConnection)
        self.signalSendSerialMsg.connect(self.serial.write_to_serial)#, Qt.DirectConnection)
        self.signalAccuUpdate.connect(self.server.updateAccu)
        
    def loadRuns(self):
        self.runTable.loadRuns()
        for run in self.runTable.runs:
            self.signalNewRun.emit(run)
     
    @pyqtSlot()       
    def resetCurrentRun(self):
        self.signalSendSerialMsg.emit("0,5\n") 
        self.signalChangeRunIndicator.emit(1)
        if len(self.runTable.runs) > 0 and not self.runTable.runs[-1].isComplete():
            self.runTable.runs.pop(-1)
    
    @pyqtSlot()
    def deleteAllRuns(self):
        pass
    
    @pyqtSlot()
    def changeMode(self):
        if self.mode == Mode.AutomaticTrigger:
            self.mode = Mode.ManualTrigger
        elif self.mode == Mode.ManualTrigger:
            self.mode = Mode.AutomaticTrigger
    
    @pyqtSlot()        
    def powerOff(self):
        self.stop()
    
    @pyqtSlot()
    def runTimerout(self):
        print("timeout")
        self.resetCurrentRun()
        # doesent have rest of webserver led
        
    @pyqtSlot()
    def updateAkkuPercentage(self):
        bus_voltage = self.ic2Connection.getBusVoltage_V()             # voltage on V- (load side)
        self.accuPercentage = (bus_voltage - 9)/3.6*100
        if(self.accuPercentage > 100):self.accuPercentage = 100
        if(self.accuPercentage < 0):self.accuPercentage = 0
        print(self.accuPercentage)
        self.signalAccuUpdate.emit(self.accuPercentage)
        if self.accuPercentage < 5.0 :
            time.sleep(2)
            self.stop()
        