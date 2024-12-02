import sys
from PyQt5.QtCore import QCoreApplication, QObject, QThread, pyqtSignal, pyqtSlot,  QTimer
from runCalculator import RunCalculator
import signal
from imageArray import ImageArray
from subprocess import call

from datetime import datetime, timedelta

import termios
import tty
import sys

#calculator = None
#camera = None
#server = None
#serial = None

def __main__():
    """Start the server and wait until it's done."""
    signal.signal(signal.SIGINT, handle_ctrl_c)
    global calculator, camera, server, serial,calculator_thread, master
    master = True
    
    app = QCoreApplication(sys.argv)
    timer = QTimer()
    timer.timeout.connect(check_key_input) 
    #timer.timeout.connect(lambda: None)  # Keeps the event loop running and checks for interrupts
    timer.start(100)
    
    calculator = RunCalculator()
    calculator_thread = QThread()
    calculator.moveToThread(calculator_thread)
    calculator_thread.started.connect(calculator.run)
    calculator_thread.blockSignals(False)
    calculator.blockSignals(False)
    calculator_thread.start()
    
    #calculator.addInterrupt(1,datetime.now().time(),True)
    #calculator.addInterrupt(2,datetime.now().time(),True)
    #sys.exit(app.exec_())
    sys.exit(QCoreApplication.exec_())
    
def handle_ctrl_c(signal_received, frame):
    """Custom handler for Ctrl+C."""
    print("\nCtrl+C detected! Cleaning up...")
    perform_cleanup()
    QCoreApplication.quit()  # Stop the event loop cleanly

def perform_cleanup():
    """Functions to execute during shutdown."""
    calculator.stop()
    calculator_thread.quit()
    calculator_thread.wait()
    print("stoping")
    print("Cleanup complete!")
    #call("sudo shutdown -h now", shell=True)
    
def addInterut():
    print("adding")
    global master, calculator
    if master:
        master = False
        calculator.addInterrupt(1,datetime.now().time(),True)
    else:
        master = True   
        calculator.addInterrupt(0,datetime.now().time(),True)
        
def check_key_input():
    """Check if the 'A' key is pressed."""
    #try:
    tty.setcbreak(sys.stdin.fileno())
    if sys.stdin.read(1) == 'a':  # Non-blocking key press check for 'A'
        addInterut()

    #except Exception as e:
    #    print(f"Error e: {e}")
    
if __name__ == "__main__":
    __main__()