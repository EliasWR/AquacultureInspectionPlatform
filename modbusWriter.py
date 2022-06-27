import serial
import time
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
from threading import Thread
from GpsReader import gpsReader
from SerialReadGyro import SerialReadGyro
from cameraServoController import CameraServoController

#The modbusclient reads the value from the GPS and the Gyro, and sends the data to the Wago PLC.
class modbusClient():

    def __init__(self,iAdress):
        self.client = ModbusTcpClient(iAdress)
        self.builder = BinaryPayloadBuilder(byteorder=Endian.Big,
                                       wordorder=Endian.Little)
        self.gpsreader = gpsReader()
        self.gyroreader = SerialReadGyro(serialPort=serial.Serial('/dev/ttyACM1', 19200, timeout=5))

        self.gpsTime0 = "asa"
        self.timeOutCheckTime = 2
        self.gpsTimeOutTime = time.time()
        self.GpsEnabled = True
        self.connCheckTimer = time.time()
        self.connCheckVar=True

        ##GPSDATA#####
        self.GpsTime = "asa"
        self.GpsHeading = 0
        self.GpsLong = 0
        self.GpsLat = 0
        self.GpsSpeed = 0
        self.GpsNumberOfSat = 0

        ##GYRODATA##
        self.GyroHeading = 0
        self.GyroPitch = 0
        self.GyroRoll = 0

        ##cameraServoController###
        self.CameraRovPos=False
        self.camCoilNr=0

    def start(self):
        self.gpsreader.start()
        self.gyroreader.start()
        t = Thread(target=self.run, name="ModbusThread", args=())
        t.daemon = True
        t.start()

    # runns when called thread.start. reads data from gps and gyro
    def run(self):

        while True:
            # todo
            # enabled coil 32912
            # speed 32004 32 bit
            # numbers of satelites int 32  32008
            #connection check bool 32864

            #checking if there is connection to the GPS by looking for change in the clock, Checks st$            if self.gpsTimeOutTime + self.timeOutCheckTime < time.time():
                if self.GpsTime == self.gpsTime0 or self.GpsTime == None:
                    if self.GpsTime == self.gpsTime0 or self.GpsTime == None:
                    self.GpsEnabled = False
                else:
                    self.GpsEnabled = True
                    self.gpsTime0 = self.GpsTime
                    self.gpsTimeOutTime = time.time()
                    # Gps enable flag on coil 32912
                self.client.write_coil(32768, [self.GpsEnabled] * 8, unit=1)
                print("GPS ENABLED: "+str(self.GpsEnabled))

            # Switching a bit for so the plc can notice connection loss. switching 1 time a sec.
            if self.connCheckTimer + 1 < time.time():
                if self.connCheckVar:
                    self.connCheckVar = False
                else:
                    self.connCheckVar = True

                self.client.write_coils(33168, [self.connCheckVar] * 8, unit=1)
                self.connCheckTimer = time.time()
                ##Read the cameraServoControlBit###
                #self.newCameraPos=self.client.read_input_registers()
                #if not self.newCameraPos == self.currentCamPos:
                   # self.changeCameraPos(self.newCameraPos)
                   # self.currentCameraPos=self.newCameraPos




            # if the gpsReader thread is ready with new values then send to Modbus
            if self.gpsreader.queReady():

                self.updateLocalGPsData(self.gpsreader.getGpsData())

                # write modbus Number of satelites on register 32008 on wago plc
                self.client.write_registers(32001, self.build16BitMessage(self.GpsNumberOfSat), unit=$
                # write modbus Speed on register 32004 on wago plc

                self.client.write_registers(32002, self.build32BitMessage(self.GpsSpeed), unit=1)

                # write modbus Latitude on register 32012 on wago plc

                self.client.write_registers(32004, self.build64BitMessage(self.GpsLat), unit=1)

                # write modbus Heading on register 320012 on wago plc

                self.client.write_registers(32012, self.build64BitMessage(self.GpsHeading), unit=1)

                # write modbus Longitude on register 32008 on wago plc

                self.client.write_registers(32008, self.build64BitMessage(self.GpsLong), unit=1)

                #Change CameraPos
                self.client.read_coils(self.camCoilNr, 1, unit=1)

            #if Gyro thread is ready with new data then send gyro data to plc
            if self.gyroreader.queReady():

                self.updateLocalGyroData(self.gyroreader.getSerialData())

                # write modbus GyroHeading on register 32004 on wago plc

                self.client.write_registers(32025, self.build32BitMessage(self.GyroHeading), unit=1)

                # write modbus GyroPitch on register 32004 on wago plc

                self.client.write_registers(32016, self.build32BitMessage(self.GyroPitch), unit=1)
                
                # write modbus GyroRoll on register 32004 on wago plc

                self.client.write_registers(32020, self.build32BitMessage(self.GyroRoll), unit=1)

    def changeCameraPos(self,rovCamPos):
        if not(rovCamPos == self.CameraRovPos):
            if rovCamPos == True:
                self.cameracontroller.changeToRovPos()

            else:
                self.cameracontroller.changeToForwardPos()




    def updateLocalGPsData(self,gpsData):
        self.GpsTime = gpsData[0]
        self.GpsHeading = gpsData[1]
        self.GpsLong = gpsData[2]
        self.GpsLat = gpsData[3]
        self.GpsSpeed = gpsData[4]
        self.GpsNumberOfSat = gpsData[5]

    def updateLocalGyroData(self,gyroData):
        self.GyroHeading = gyroData[0]
        print("gyroHeading: "+ str(self.GyroHeading))
        self.GyroPitch = gyroData[2]
        print("gyroPitch: " + str(self.GyroPitch))
        self.GyroRoll = gyroData[1]
        print("gyroRoll: " + str(self.GyroRoll))
        
    def build16BitMessage(self,message):
        #encode 16 bit integer message
        self.builder.reset()
        self.builder.add_16bit_int(message)
        encoded16 = self.builder.to_registers()
        return encoded16


    def build32BitMessage(self, message):
        # encode 32 bit float message
        self.builder.reset()
        self.builder.add_32bit_float(message)
        encoded32 = self.builder.to_registers()
        return encoded32

    def build64BitMessage(self, message):
        # encode 64 bit float message
        self.builder.reset()
        self.builder.add_64bit_float(message)
        encoded64 = self.builder.to_registers()
        return encoded64
    