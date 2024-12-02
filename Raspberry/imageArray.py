from datetime import datetime
import cv2 as cv

class ImageArray:
    def __init__(self):
        self.images = []
        self.timestamps = []
        self.calculatedTime = 0
        self.calculatedIndex = 0
        
    def addImage(self, image, timeStamp):
        self.images.append(image)
        self.timestamps.append(timeStamp)
        
    def removeFirstImage(self):
        self.images.pop(0)
        self.timestamps.pop(0)
        
    def calculateTime(self):
        self.calculatedTime = datetime.now().time()#Do image processing
        self.calculatedIndex = 10
        
    def getImageAndTime(self,index):
        if index < len(self.images):
            return self.images[index], self.timestamps[index]
        return cv.imread("img.jpg"), datetime.now().time()
    
    def getCalculatedTimeNearestIndex(self):
        return self.calculatedTime, self.calculatedIndex
    
    def getLength(self):
        return len(self.images)