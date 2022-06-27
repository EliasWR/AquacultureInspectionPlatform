from VideoStream import videoStream

from modbusTcp import startModbusDataThreads
from modbusWriter import modbusClient
from SerialReadGyro import SerialReadGyro
import threading
import serial


def main():
    modbusIpadress = "192.168.0.112"
    t = threading.Thread(target=videoStream,name="VidThread",args=("192.168.0.103",12345))
    t.start()
    #startModbusDataThreads(modbusIpadress)
    modclient=modbusClient(modbusIpadress)
    modclient.start()

if __name__ == '__main__':
    main()