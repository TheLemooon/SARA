import cv2
import numpy as np
import picamera
import picamera.array
import datetime
import threading
import sys

# Define the video filename
filename = "recording_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".h264"

# Define the recording resolution and framerate
resolution = (640, 480)  # Adjust as needed
framerate = 24           # Frames per second

# Define a flag to control recording
is_recording = True

def record_video():
    global is_recording
    with picamera.PiCamera() as camera:
        camera.resolution = resolution
        camera.framerate = framerate
        camera.start_recording(filename)
        print(f"Recording started, saving to {filename}")
        try:
            # Keep recording until stopped
            while is_recording:
                camera.wait_recording(1)  # Wait in 1-second increments
        finally:
            camera.stop_recording()
            print("Recording stopped and saved")

def wait_for_input():
    global is_recording
    input("Press Enter to stop recording...\n")
    is_recording = False

# Create a thread to run the video recording
recording_thread = threading.Thread(target=record_video)
recording_thread.start()

# Wait for keyboard input in the main thread
wait_for_input()

# Wait for the recording thread to finish
recording_thread.join()

print(f"Video saved as {filename}")

