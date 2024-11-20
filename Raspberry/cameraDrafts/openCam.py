#from picamera import PiCamera
#from picamera.array import PiRGBArray
#import time
import cv2 as cv
 
#camera = PiCamera()
#time.sleep(0.1)
#camera.capture("test.jpg")
cap = cv.VideoCapture()
if not cap.isOpened():
    print("Cannot open camera")
    exit()
i=0
ret=False
while (ret==False and i< 500):
	print("+1\n")
	ret, frame = cap.read()
	i=i+1
cv.imwrite("img.png",frame)
cap.release()
 
