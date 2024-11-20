import cv2
import datetime

# Define the video filename
filename = "recording_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".avi"
resolution = (640, 480)  # Adjust as needed
framerate = 20           # Frames per second

# Open the camera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
cap.set(cv2.CAP_PROP_FPS, framerate)

# Define the codec and create a VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(filename, fourcc, framerate, resolution)

print("Recording started, press 'q' to stop")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # Write the frame to the video file
    out.write(frame)

    # Display the frame (optional)
    cv2.imshow('Recording...', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Recording stopped")
        break

# Release resources
cap.release()
out.release()
cv2.destroyAllWindows()

