import cv2
from picamera2 import Picamera2, Preview

# Initialize the camera
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration())

# Start the camera preview (optional)
picam2.start_preview(Preview.QTGL)

# Start the camera
picam2.start()

# Capture an image
image = picam2.capture_array()

# Save the image using OpenCV
cv2.imwrite('captured_image.jpg', image)

# Optional: Display the image
cv2.imshow('Captured Image', image)
cv2.waitKey(0)

# Clean up
cv2.destroyAllWindows()
picam2.stop()
