import sys
import serial
import time
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget


class SerialReader(QObject):
    """Class to handle serial reading in a separate thread and emit data through a signal."""
    data_received = pyqtSignal(str)  # Define a signal that emits a string

    def __init__(self, port='/dev/serial0', baudrate=115200):
        super().__init__()
        # Initialize the serial port
        self.ser = serial.Serial(port=port, baudrate=baudrate, timeout=1)
        self.running = True  # Control flag for the thread

    def write_to_serial(self, data):
        if self.ser.is_open:
            print(f"Writing to serial: {data}")
            self.ser.write(data.encode())  # Encode string to bytes before sending
        else:
            print("Serial port not open.")

    def read_from_serial(self):
        while self.running:
            if self.ser.is_open and self.ser.in_waiting > 0:
                # Read data from serial and emit it
                data = self.ser.readline().decode().strip()
                print(f"Received from serial: {data}")
                self.data_received.emit(data)  # Emit the received data as a signal
            time.sleep(0.1)  # Adjust sleep time as necessary

    def stop(self):
        self.running = False
        if self.ser.is_open:
            self.ser.close()
            print("Serial port closed.")


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Serial Data Reader")
        
        # QLabel to display serial data
        self.label = QLabel("Waiting for data...", self)
        
        # Layout and central widget
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Start serial reader in a separate thread
        self.serial_thread = QThread()
        self.serial_reader = SerialReader()
        self.serial_reader.moveToThread(self.serial_thread)

        # Connect signals
        self.serial_thread.started.connect(self.serial_reader.read_from_serial)
        self.serial_reader.data_received.connect(self.update_label)

        # Start the thread
        self.serial_thread.start()

    def update_label(self, data):
        """Update the QLabel with received serial data."""
        self.label.setText(f"Received: {data}")

    def closeEvent(self, event):
        """Handle closing the application and cleaning up the serial connection."""
        self.serial_reader.stop()
        self.serial_thread.quit()
        self.serial_thread.wait()
        event.accept()


# Run the application
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
