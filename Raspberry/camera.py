from imageArray import ImageArray
from datetime import datetime
from PyQt5.QtCore import pyqtSignal, QThread, pyqtSlot, QObject
import cv2 as cv
import time

pipeline = ("libcamerasrc ! video/x-raw, width=640, height=480, framerate=30/1 ! "
    "videoconvert ! appsink"
    )

imageCountBevorInterupt = 5
imageCountAfterInterupt = 30

class CameraHandler(QThread):
    signalImagesProcessed = pyqtSignal(ImageArray)
    
    def __init__(self):
        super().__init__()
        self.images = ImageArray()
        self.threadRunning= True
        self.returnImages = False
        
        self.capture = cv.VideoCapture(pipeline, cv.CAP_GSTREAMER)
        self.capture.set(cv.CAP_PROP_FRAME_WIDTH, 640)
        self.capture.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
        if self.capture.isOpened():#cameraIsOpen
            print("cap Open")
        else:
            print("capclose")
    
    @pyqtSlot()    
    def run(self):
        while self.threadRunning:
            if self.capture.isOpened():#cameraIsOpen
                self.getNextImage()
                if self.images.getLength() > imageCountBevorInterupt and not self.returnImages:
                    self.images.removeFirstImage()
                elif self.returnImages and self.images.getLength() >= (imageCountBevorInterupt +imageCountAfterInterupt):
                    self.sendImages()
            #time.sleep(0.001)
                    
    def stop(self):
        print("stoping camera")
        self.capture.release()
        self.threadRunning = False
        self.quit()
        self.wait()
            
    @pyqtSlot()
    def stopRecordingAndProcessImages(self):
        print("recieved")
        self.returnImages = True       
        
    def sendImages(self):
        self.returnImages = False 
        self.doImageProcessing()   
        print(self.images.getCalculatedTimeNearestIndex())
        imagesToSend = self.images
        self.images = ImageArray()
        print("emitted images2")
        self.signalImagesProcessed.emit(imagesToSend)
        
    def getNextImage(self):
        ret, frame = self.capture.read()
        if ret:
            self.images.addImage(frame,datetime.now().time()) 
    
    def doImageProcessing(self):
        self.images.calculateTime()
