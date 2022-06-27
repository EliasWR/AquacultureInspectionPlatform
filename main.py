from VideoStream import videoStream

from modbusTcp import startModbusDataThreads
import threading



def main():
    modbusIpadress = "158.38.140.124"
    t = threading.Thread(target=videoStream,name="thread1",args=("158.38.194.166",12342))
    t.start()
    startModbusDataThreads(modbusIpadress)











if __name__ == '__main__':main()