from flask import Flask, render_template, request, redirect, url_for, send_file, Response
import csv
import os
from run import Run
from imageArray import ImageArray
from PyQt5.QtCore import QObject, pyqtSignal, QThread, pyqtSlot
import cv2 as cv



# Sample data
data = [
    {"ID": 1, "Name": "Alice", "Age": 30},
    {"ID": 2, "Name": "Bob", "Age": 25},
    {"ID": 3, "Name": "Charlie", "Age": 35},
]

class WebSever(QThread):
    signalUpdateRunTime = pyqtSignal(int,int)
    
    def __init__(self):
        super().__init__()
        self.runs = data
        self.currentRunIdx = 0
        self.currentImageIdx = 0
        self.threadRunning = True
        self.img = cv.imread("img.jpg")
        
    def setup_routes(self):
        """Define the routes for the web application."""

        @self.app.route("/", methods=["GET", "POST"])
        def home():
            """Handle displaying the table and processing form submissions."""
            return render_template("WebServer.html", data=self.runs)
        
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

        @self.app.route("/download", methods=["POST"])
        def download_data_route():
            """Trigger data download."""
            return self.download_data()
        
        @self.app.route("/set-image", methods=["POST"])
        def set_image_route():
            """Set a new image."""
            return self.set_image()

    def add_entry(self, entry_id, startTime, stopTime,time):
        """Add a new entry to the data."""
        self.runs.append({"ID": entry_id, "Start": startTime, "Stop": stopTime, "Time": time})

    def previousImage(self):
        self.currentImageIdx -=1
        
    def nextImage(self):
        self.currentImageIdx +=1
        
    def setTimeStamp(self):
        self.currentImageIdx +=1
        self.signalUpdateRunTime.emit(self.currentImageIdx,self.currentRunIdx)

    def download_data(self):
        """Generate a CSV file and send it for download."""
        file_path = "runs.csv"
        with open(file_path, mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["ID", "Start", "Stop", "Time"])
            writer.writeheader()
            writer.writerows(self.data)
        return send_file(file_path, as_attachment=True)
    
    def set_image(self):
        """Set a new image path."""
        img  = self.img #self.currentImageIdx
        _, buffer = cv.imencode(".png", img)
        print("tring set Image")
        return Response(buffer.tobytes(), mimetype="image/png")

    def run(self):
        """Start the Flask web server."""
        self.app = Flask(__name__)
        self.setup_routes()
        self.app.run(port=5000, debug=False, use_reloader=False)
        
    def stop(self):
        self.threadRunning = False
    
    @pyqtSlot(Run)
    def update(self,run = Run):
        if run.isComplete():
            self.add_entry(len(self.runs),run.getStartTime(),run.getStopTime(),run.getRunTime())
            print("update set Image")
            #do image stuff
            #self.img, _, _ = run.images.getImageAndTime(0)
            #self.set_image()


if __name__ == "__main__":
    # Instantiate and run the web application
    web_app = WebSever()
    web_app.run()
