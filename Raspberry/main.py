import sys
from PyQt5.QtCore import QCoreApplication, QThread
from SerialInterface import SerialReader
from runCalculator import RunCalculator
from server import WebSever

def __main__():
    """Start the server and wait until it's done."""
    app = QCoreApplication(sys.argv)
    calculator = RunCalculator()
    server = WebSever()
    #serial = SerialReader()
    calculator_thread = QThread()
    calculator.moveToThread(calculator_thread)
    calculator_thread.started.connect(calculator.run)
    
    calculator.signalNewRun.connect(server.update)
    #serial.signalNewMessage.connect(calculator.addInterrupt)
    server.signalUpdateRunTime.connect(calculator.adjustStopTime)
    calculator_thread.start()
    server.start()
    #serial.start()
    
    
    sys.exit(app.exec_())
    
    # connect signals
    # start threads
    
    
if __name__ == "__main__":
    __main__()