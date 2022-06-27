import queue
import serial
from threading import Thread
import time

# Reads serialcom from the Gyroscope on the port "serialPort"
class SerialReadGyro():
    def __init__(self, serialPort):

        self.q = queue.LifoQueue()

        self.serialPort = serialPort

    def start(self):

        t = Thread(target=self.run, name="GyroThread", args=())
        t.daemon = True
        t.start()

    # runns when called thread.start. reads data from arduino and setts the input to the arranged va$
    def run(self):
        try:
            while (True):

                # print("starting to read")
                data = str(self.serialPort.readline())


                ##removing b' flag at the beginning of the string
                cleanedString = data.split("b'")
                #print(cleanedString)

                # splitting the string where there is ;
                splitData = cleanedString[1].split(";")
                cleanLastPart = splitData[2].split("\\")

                # list type=string [0]=gyro heading(yaw) [1] = roll [2]= pitch
                splitData[2] = cleanLastPart[0]

                if splitData.__len__() == 3:
                    self.q.put(self.convertStringToFloat(splitData))

        except serial.SerialException as e:
            print("SerialPortException i SerialRead")

    def convertStringToFloat(self, l):
        # create a list with the size of 3 (0...2)&converts the string to float values
        list = [None] * 3
        list[0] = float(l[0])
        list[1] = float(l[1])
        list[2] = float(l[2])
        return list

    def getSerialData(self):

        # Return the latest serialData
        if not self.q.empty():
            newdata = self.q.get()

            # while not self.q.empty():
             # trashBin = self.q.get()

            return newdata
        else:
            # print("empty Queue in seiralRead")
            noData = [None] * 3
            return noData

    def queReady(self):
        if not self.q.empty():
            return True
        else:
            return False