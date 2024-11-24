from imageArray import ImageArray
from datetime import datetime
from PyQt5.QtCore import pyqtSignal, QThread, pyqtSlot, QObject
import cv2 as cv

class CameraHandler(QThread):
    signalImagesProcessed = pyqtSignal(ImageArray)
    
    def __init__(self):
        super().__init__()
        self.images = ImageArray()
        self.threadRunning= True
        
    def run(self):
        while self.threadRunning:
            if True:#cameraIsOpen
                self.getNextImage()
                if self.images.getLength() > 30:
                    self.images.removeFirstImage()
                    
    def stop(self):
        self.threadRunning = False
            
    @pyqtSlot()
    def stopRecordingAndProcessImages(self):
        for i in range(0,30) : 
            self.getNextImage()
        self.doImageProcessing()
        print(self.images.getCalculatedTime())
        self.signalImagesProcessed.emit(self.images)
        print("emitted images2")
        
    def getNextImage(self):
        img = cv.imread("img.jpg")
        self.images.addImage(img,datetime.now().time())
    
    def doImageProcessing(self):
        self.images.calculateTime()