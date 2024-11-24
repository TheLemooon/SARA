import sys
from PyQt5.QtCore import QCoreApplication, QObject, QThread, pyqtSignal, pyqtSlot, Qt
from SerialInterface import SerialReader
from runCalculator import RunCalculator
from camera import CameraHandler
from server import WebSever
import signal
from imageArray import ImageArray

from datetime import datetime, timedelta

calculator = None
camera = None
server = None
serial = None

def __main__():
    """Start the server and wait until it's done."""
    signal.signal(signal.SIGINT, handle_ctrl_c)
    
    app = QCoreApplication(sys.argv)
    calculator = RunCalculator()
    camera = CameraHandler()
    server = WebSever()
    #serial = SerialReader()
    calculator_thread = QThread()
    camthread = QThread()
    calculator.moveToThread(calculator_thread)
    calculator_thread.started.connect(calculator.run)
    calculator_thread.blockSignals(False)
    calculator.blockSignals(False)
    camera.moveToThread(camthread)
    
    calculator.signalNewRun.connect(server.update)
    #serial.signalNewMessage.connect(calculator.addInterrupt)
    server.signalUpdateRunTime.connect(calculator.adjustStopTime)
    calculator.signalRequestingImages.connect(camera.stopRecordingAndProcessImages)
    camera.signalImagesProcessed.connect(calculator.receiveRequestedImages, Qt.DirectConnection)
    print(camera.receivers(camera.signalImagesProcessed))

    
    calculator_thread.start()
    server.start()
    camthread.start()
    #serial.start()
    
    
    print("adding run")
    calculator.addInterrupt(1,datetime.now().time(),True)
    calculator.addInterrupt(2,datetime.now().time(),True)
    print(calculator_thread.isRunning())
    sys.exit(app.exec_())
    
def handle_ctrl_c(signal_received, frame):
    """Custom handler for Ctrl+C."""
    print("\nCtrl+C detected! Cleaning up...")
    perform_cleanup()
    QCoreApplication.quit()  # Stop the event loop cleanly

def perform_cleanup():
    """Functions to execute during shutdown."""
    print("stoping")
    """calculator_thread.quit()
    calculator_thread.wait()
    camera_thread.quit()
    camera_thread.wait()
    server_thread.quit()
    server_thread.wait()
    serial_thread.quit()
    serial_thread.wait()"""
    
    print("Cleanup complete!")
    
if __name__ == "__main__":
    __main__()