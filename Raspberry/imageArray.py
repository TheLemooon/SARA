from datetime import datetime
import cv2 as cv

class ImageArray:
    def __init__(self):
        self.images = []
        self.timestamps = []
        self.calculatedTime = 0
        
    def addImage(self, image, timeStamp):
        self.images.append(image)
        self.timestamps.append(timeStamp)
        
    def removeFirstImage(self):
        self.images.pop(0)
        self.timestamps.pop(0)
        
    def calculateTime(self):
        self.calculatedTime#Do image processing
        
    def getImageAndTime(self,index):
        if index < len(self.images):
            return self.images[index], self.timestamps[index], True
        return cv.Mat(), datetime.now().time(), False
    
    def getCalculatedTime(self):
        return self.calculatedTime