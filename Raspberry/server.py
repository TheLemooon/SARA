from flask import Flask, render_template, request, redirect, url_for, send_file, Response, send_from_directory
import csv
import os
from run import Run
from imageArray import ImageArray
from PyQt5.QtCore import QObject, pyqtSignal, QThread, pyqtSlot
import cv2 as cv
import FindMyIP as ip
import sys
import os
import requests
import werkzeug

path = "./SavedRuns/"
imgFormat = ".png"

# Sample data
data = [
]

imageName = "0/0.png"
myIp = "10.42.0.1"#ip.internal()

class WebSever(QThread):
    signalUpdateRunTime = pyqtSignal(int,int)
    signalResetRun = pyqtSignal()
    signalChangeMode = pyqtSignal()
    signalPowerOff = pyqtSignal()
    signalDeleteData = pyqtSignal()
    signalDeleteRun = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.runs = data
        self.currentRunIdx = 0
        self.currentImageIdx = 0
        self.image_path = imageName
        self.threadRunning = True
        self.led_states = {"led1": "green", "led2": "green"}
        self.currentTime = f"{float(0.0):.2f}"
        self.idxToDelete = -1
        self.mode = "Automatic"
        self.accuImage = "static/accu00.png"
        print("serverIsInit")
        
    def setup_routes(self):
        """Define the routes for the web application."""

        @self.app.route("/", methods=["GET", "POST"])
        def home():
            """Handle displaying the table and processing form submissions."""
            reversed_data = list(reversed(self.runs))
            return render_template("WebServer.html", data=reversed_data,image_path=self.image_path,
                                   led_states=self.led_states ,currentTIme = self.currentTime,
                                   mode = self.mode, accuStateImage=self.accuImage)
        
        @self.app.route("/powerOff", methods=["POST"])
        def shutdown_route():
            self.signalPowerOff.emit()
            return redirect(url_for("home"))
        
        @self.app.route("/mode", methods=["POST"])
        def mode_route():
            self.signalChangeMode.emit()
            if self.mode == "Automatic":
                self.mode = "Manual"
            else:
                self.mode = "Automatic"
            return redirect(url_for("home"))
        
        @self.app.route("/set_led/<led>/<color>", methods=["POST"])
        def set_led(led, color):
            """Update the LED state from Python logic."""
            if led in self.led_states:
                self.led_states[led] = color
                return f"{led} updated to {color}", 200
            return "Invalid LED", 400
        
        @self.app.route("/update_time/<int:new_time>")
        def update_time(t):
            #global time_value
            self.currentTime = t
            return f"Time updated to {t}"
        
        @self.app.route("/reset", methods=["POST"])
        def reset_route():
            self.signalResetRun.emit()
            self.changeRunIndicator(1)
            self.currentTime = 0.0
            return redirect(url_for("home"))
        
        @self.app.route("/next", methods=["POST"])
        def getNextImage_route():
            """get Next Picture"""
            self.nextImage()
            return redirect(url_for("home"))

        @self.app.route("/previous", methods=["POST"])
        def getPreviousImage_route():
            """Get Previous Picture"""
            self.previousImage()
            return redirect(url_for("home"))
        
        @self.app.route("/setNewTimestamp", methods=["POST"])
        def setNewTimeStamp_route():
            """Get Previous Picture"""
            self.setTimeStamp()
            return redirect(url_for("home"))

        @self.app.route("/delete", methods=["POST"])
        def delete_route():
            self.deleteData()
            return redirect(url_for("home"))
        
        @self.app.route("/deleteRun", methods=["POST"])
        def deleteRun_route():
            self.idxToDelete = self.currentRunIdx
            self.signalDeleteRun(self.idxToDelete)
            return redirect(url_for("home"))
        
        @self.app.route("/download", methods=["POST"])
        def download_data_route():
            """Trigger data download."""
            return self.download_data()
        
        @self.app.route("/shutdown", methods=["POST"])
        def shutdown():
            """Trigger server shutdown."""
            self.doShutdown()
            return "Server shutting down..."
        
        @self.app.route('/SavedRuns/<path:filename>')
        def serve_run_image(filename):
            return send_from_directory('SavedRuns', filename)
        
        @self.app.route('/generalUpdate', methods=["POST"])
        def generalUdate():
            return redirect(url_for("home"))

    def add_entry(self, entry_id, date,time):
        """Add a new entry to the data."""
        if entry_id > len(self.runs) -1:
            self.runs.append({"ID": entry_id, "Date": date, "Time": time})
        else:
            self.runs[entry_id] = {"ID": entry_id, "Date": date, "Time": time}

    def previousImage(self):
        self.currentImageIdx -=1
        if self.currentImageIdx < 0:
            self.currentImageIdx = 0
        self.set_image()
        
    def nextImage(self):
        self.currentImageIdx +=1
        if self.currentImageIdx >= 35:
            self.currentImageIdx = 34
        self.set_image()
        
    def setTimeStamp(self):
        #self.currentImageIdx +=1
        self.signalUpdateRunTime.emit(self.currentRunIdx, self.currentImageIdx)
        
    def deleteData(self):
        self.runs = []
        self.signalDeleteData.emit()

    def download_data(self):
        """Generate a CSV file and send it for download."""
        file_path = "runs.csv"
        with open(file_path, mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["ID", "Date", "Time"])
            writer.writeheader()
            writer.writerows(data)
        return send_file(file_path, as_attachment=True)
    
    def set_image(self):
        """Set a new image path."""
        pth = f"{self.currentRunIdx}/{self.currentImageIdx}{imgFormat}"
        print(f"Setting image path to: {pth}")
        self.image_path = f"/SavedRuns/{pth}"

    def run(self):
        """Start the Flask web server."""
        self.app = Flask(__name__)
        self.setup_routes()
        print(os.getcwd())
        while self.threadRunning: # Process pending events
            self.app.run(host=myIp, port=5000, debug=False,threaded=False)#, use_reloader=False)#
        print("serverloop terminated")
        self.led_states["led1"] ="green"
        self.led_states["led2"] ="green"
        
    def stop(self):
        print("shuting down server")
        self.threadRunning = False
        self.doShutdown()
        print("terminating")
        if not self.isRunning():
            self.quit()
        #os._exit(0)
    
    @pyqtSlot(Run)
    def updateTable(self,run: Run):
        print("recieved")
        if run.isComplete():
            self.add_entry(run.runIndex,run.getDate(),f"{run.getRunTime():.2f}")
            print("update set Image")
            self.currentRunIdx = run.runIndex
            self.currentImageIdx = run.getCalculatedIndex()
            self.set_image()
            self.currentTime = f"{run.getRunTime():.2f}"
            #self.updateServer()
            
    @pyqtSlot(Run)
    def updateRun(self,run: Run):
        self.updateTable(run)
       
    @pyqtSlot(int) 
    def changeRunIndicator(self, state):
        """1. green green =waiting 2. red green=started waiting for finish 3. red red = run finished waiting for images"""
        if state == 1:
            self.led_states["led1"] = "green"
            self.led_states["led2"] = "green"
        elif state ==2:
            self.led_states["led1"] = "red"
            self.led_states["led2"] = "green"
        elif state ==3:
            self.led_states["led1"] = "red"
            self.led_states["led2"] = "red"
        else:
            #change in to enum so this wont even be triggerd
            pass
        #self.socketio.emit("update_leds", self.led_states)
        #self.updateServer()
        
    @pyqtSlot(float)
    def updateAccu(self,accuPercent):
        val = int(accuPercent/10)
        self.accuImage =f'static/accu{val}0.png'
        print("accuupdate triggerd")
        #self.socketio.emit("update_accu_image", {"accuStateImage": self.accuImage})
        #self.updateServer()
        
    def updateServer(self):
        #change to socket script, semms like bulshit
        try:
            requests.post(f'http://{myIp}:5000/generalUpdate')
        except requests.exceptions.RequestException as e:
            print(f"Error calling update endpoint: {e}")
            
    def doShutdown(self):
        print(request.environ)
        shutdown_func = request.environ.get('werkzeug.server.shutdown')
        if shutdown_func is None:
            print("notwerkzeufg")
        else:
            shutdown_func()

if __name__ == "__main__":
    # Instantiate and run the web application
    web_app = WebSever()
    web_app.run()
