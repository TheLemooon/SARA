import sys
import serial as ser
from datetime import datetime, timedelta
import time
from messageParser import MessageParser
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget


class SerialReader(QThread):
    """Class to handle serial reading in a separate thread and emit data through a signal."""
    signalNewMessage = pyqtSignal(int,float,bool) #device id, time since interrupt, is auto interrupt
    data_received = pyqtSignal(str)  # Define a signal that emits a string

    def __init__(self, port='/dev/serial0', baudrate=115200):
        super().__init__()
        self.parser = MessageParser()
        # Initialize the serial port
        self.ser = ser.Serial(port=port, baudrate=baudrate, timeout=1)
        self.running = True  # Control flag for the thread

    def write_to_serial(self, data):
        if self.ser.is_open:
            print(f"Writing to serial: {data}")
            self.ser.write(data.encode())  # Encode string to bytes before sending
        else:
            print("Serial port not open.")

    def run(self):
        while self.running:
            if self.ser.is_open and self.ser.in_waiting > 0:
                # Read data from serial and emit it
                currentTime = datetime.now().time()
                data = self.ser.readline().decode().strip()
                dev, secondsSinceInterrupt, isAutomatic = self.parser.getParamFromMessage(data)
                timeStamp = currentTime -timedelta(seconds= secondsSinceInterrupt)
                self.signalNewMessage.emit(dev,timeStamp,isAutomatic)
                print(f"Received from serial: {data}")
            time.sleep(0.1)  # Adjust sleep time as necessary

    def stop(self):
        self.running = False
        if self.ser.is_open:
            self.ser.close()
            print("Serial port closed.")
