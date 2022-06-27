import gps
import threading
import time
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder


def gpsReader():

    #Global variables that the modbus function reads from
    global GpsTime
    global Speed
    global Latitude
    global Heading
    global Longitude
    global NumberOfsatelites #need to implement


    Speed = 0
    Latitude = 0
    NumberOfsatelites = 0
    Longitude = 0
    Heading = 0
    # Listen on port 2947 (gpsd) of localhost
    session = gps.gps("localhost", "2947")
    session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
    # outQueue.put(0)
    while True:
        try:

            NumberOfsatelites=session.satellites_used
            report = session.next()
            print("Number of satelites :" + str(NumberOfsatelites))


            # Wait for a 'TPV' report and display the current time
            # To see all report data, uncomment the line below
            # print(report)
            if report['class'] == 'TPV':
                if hasattr(report, 'time'):
                    print("time :" + report.time)
                    GpsTime = report.time

                if hasattr(report, 'track'):
                    print("Heading :" + str(report.track))
                    Heading = report.track
                if hasattr(report, 'lon'):
                    print("Langitude :" + str(report.lon))
                    Longitude = report.lon

                if hasattr(report, 'lat'):
                    print("Latitude :" + str(report.lat))
                    Latitude = report.lat
                if hasattr(report, 'speed'):
                    Speed = (report.speed * gps.MPS_TO_KPH)

        except KeyError:
            pass
        except KeyboardInterrupt:
            quit()
        except StopIteration:
            session = None
            print("GPSD has terminated")

#The modbusclient reads the value from the GPS and the Gyro, and sends the data to the Wago PLC.
def modbusClient(iAdress):
    client = ModbusTcpClient(iAdress)
    builder = BinaryPayloadBuilder(byteorder=Endian.Big,
                                   wordorder=Endian.Little)
    gpsTime0 = "asa"
    timeOutCheckTime = 2
    gpsTimeOutTime = time.time()
    GpsEnabled = True
    connCheckTimer = time.time()
    connCheckVar=True

    while True:
        # todo
        # enabled coil 32912
        # speed 32004 32 bit
        # numbers of satelites int 32  32008
        #connection check bool 32864

        #checking if there is connection to the GPS by looking for change in the clock, Checks status$        if gpsTimeOutTime + timeOutCheckTime < time.time():
            if GpsTime == gpsTime0 or GpsTime == None:
                GpsEnabled = False
            else:
                GpsEnabled = True
                gpsTime0 = GpsTime
                gpsTimeOutTime = time.time()
            print("GPS ENABLED: "+str(GpsEnabled))

            # Switching a bit for so the plc can notice connection loss. switching 1 time a sec.
            if connCheckTimer + 1 < time.time():
                if connCheckVar:
                    connCheckVar = False
                else:
                    connCheckVar = True
    
                client.write_coils(32864, [connCheckVar] * 8, unit=1)
                connCheckTimer = time.time()
    
            time.sleep(0.5)
    
            # Gps enable flag on coil 32912
            client.write_coils(32912, [GpsEnabled] * 8, unit=1)
    
            # write modbus Number of satelites on register 32008 on wago plc
            builder.add_16bit_int(NumberOfsatelites)
            satelitesEnc = builder.to_registers()
            client.write_registers(32008, satelitesEnc, unit=1)
            builder.reset()
    
            # write modbus Speed on register 32004 on wago plc
            builder.add_32bit_float(Speed)
            speedEnc = builder.to_registers()
            client.write_registers(32004, speedEnc, unit=1)
            builder.reset()
    
            # write modbus Latitude on register 32012 on wago plc
            builder.add_64bit_float(Latitude)
            latEnc = builder.to_registers()
            client.write_registers(32012, latEnc, unit=1)
            builder.reset()
    
            # write modbus Heading on register 32006 on wago plc
            builder.add_64bit_float(Heading)
            headEnc = builder.to_registers()
            # write modbus Langitude on register 32000 on wago plc
            builder.add_64bit_float(Longitude)
            langEnc = builder.to_registers()
            client.write_registers(32000, langEnc, unit=1)
            builder.reset()


def startModbusDataThreads(modIp):

    #Thread of a Gps reader
    gpsReaderT = threading.Thread(target=gpsReader, name="gpsThread", args=())
    #Thread of modbus communication, reads Global variable from the gpsReader and Gyro
    modbusT = threading.Thread(target=modbusClient, name="modbusThread", args=(modIp,))


    #starts the threads, when the thread joins the threads are done.
    gpsReaderT.start()
    modbusT.start()
    gpsReaderT.join()
    gpsReaderT.join()