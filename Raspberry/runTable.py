from run import Run
import os
import csv
from datetime import datetime

path = "SavedRuns"
file_name = "runtable.csv"
        
class RunTable:
    def __init__(self):
        self.runs = []
        self.firstIndex = 0
        self.lastIndex = -1
        
    def loadRuns(self):
        if os.path.isfile(os.path.join(path,file_name)):
            with open(os.path.join(path,file_name), mode='r') as file:  # Open the file in read mode
                reader = csv.reader(file)
                data = list(reader)  
            for line in data:
                run = Run()
                run.start = convertToDatetime(line.pop(0))
                run.stop = convertToDatetime(line.pop(0))
                run.automaticStart = line.pop(0)
                run.runIndex = line.pop(0)
                run.imageCount = line.pop(0)
                run.calculatedIndex = line.pop(0)
                for item in line:
                    run.imageTimes.append(convertToDatetime(item))
                self.appendRun(run)
    
    def saveRuns(self):
        indexDeviation = 0
        if len(self.runs) > 300:
            indexDeviation = len(self.runs) - 300 
            for i in range(0,indexDeviation):
                os.rmdir(os.path.join(path,str(i)))#maybe i-1
        if self.runs:    
            if not os.path.isfile(os.path.join(path,file_name)):
                pass
            with open(os.path.join(path,file_name), mode='w', newline='') as file:
                writer = csv.writer(file)
                for i in range(0+indexDeviation ,len(self.runs) + indexDeviation):
                    run = self.runs[i]
                    data = [run.start, run.stop, run.automaticStart, run.runIndex, run.imageCount, run.calculatedIndex]
                    for t in run.imageTimes:
                        data.append(t)
                    if run.isComplete():
                        writer.writerow(data) 
                    if indexDeviation != 0:
                        os.rename(os.path.join(path,str(i)),os.path.join(path,str(i-indexDeviation)))
    
    def appendRun(self,run:Run):
        self.lastIndex  +=1
        if run.getRunIndex() != self.lastIndex:
            run.setRunIndex(self.lastIndex)
        self.runs.append(run)
    
    def getRun(self,runIndex):
        if runIndex >= self.firstIndex and runIndex <= self.lastIndex:
            return self.runs[runIndex - self.firstIndex]
        
    def getRunCount(self):
        if not self.runs:#empty
            return 0
        return len(self.runs) 
    
    def getLastRun(self):
        return self.runs[-1]
    
def convertToDatetime(timestamp):
    return datetime.strptime(timestamp, '%H:%M:%S.%f').time()
    