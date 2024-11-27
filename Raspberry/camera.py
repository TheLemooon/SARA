from imageArray import ImageArray
from datetime import datetime
from PyQt5.QtCore import pyqtSignal, QThread, pyqtSlot, QObject
import cv2 as cv

pipeline = ("libcamerasrc ! video/x-raw, width=640, height=480, framerate=30/1 ! "
    "videoconvert ! appsink"
    )

class CameraHandler(QThread):
    signalImagesProcessed = pyqtSignal(ImageArray)
    
    def __init__(self):
        super().__init__()
        self.images = ImageArray()
        self.threadRunning= True
        
        self.capture = cv.VideoCapture(pipeline, cv.CAP_GSTREAMER)
        self.capture.set(cv.CAP_PROP_FRAME_WIDTH, 640)
        self.capture.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
        if self.capture.isOpened():#cameraIsOpen
            print("cap Open")
        else:
            print("capclose")
        
    def run(self):
        while self.threadRunning:
            if self.capture.isOpened():#cameraIsOpen
                #print("get new image")
                #self.getNextImage()
                if self.images.getLength() > 30:
                    self.images.removeFirstImage()
            #time.sleep(0.001)
                    
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
        ret, frame = self.capture.read()
        if ret:
            cv.imwrite("camImage.jpg",frame)
        else:
            print("couldnt read")
        self.images.addImage(frame,datetime.now().time())
    
    def doImageProcessing(self):
        self.images.calculateTime()
