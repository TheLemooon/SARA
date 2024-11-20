import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import time

# Initialize the camera
camera = PiCamera()
raw_capture = PiRGBArray(camera)

# Allow the camera to warm up
time.sleep(0.1)

# Capture an image
camera.capture(raw_capture, format="bgr")
image = raw_capture.array

# Save the image using OpenCV
cv2.imwrite("captured_image.jpg", image)

# Optional: Display the image (for testing purposes)
cv2.imshow("Captured Image", image)
cv2.waitKey(0)
cv2.destroyAllWindows()

