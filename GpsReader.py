import gps
from threading import Thread
import queue

class gpsReader():

    def __init__(self):


        # Gps data variables
        self.GpsTime= "asa"
        self.Speed=0
        self.Latitude=0
        self.Heading=0
        self.Longitude=0
        self.NumberOfsatelites=0
        #queue for sharing data betweem thrread
        self.q = queue.LifoQueue()
        #need to implement

        # Listen on port 2947 (gpsd) of localhost
        self.session = gps.gps("localhost", "2947")
        self.session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

    def start(self):

        t = Thread(target=self.run, name="gpsReaderThread", args=())
        t.daemon = True
        t.start()



    # outQueue.put(0)
    def run(self):
        try:
            while True:


                self.NumberOfsatelites=self.session.satellites_used
                report = self.session.next()
                #print("Number of satelites :" + str(self.NumberOfsatelites))


                # Wait for a 'TPV' report and display the current time
                # To see all report data, uncomment the line below
                # print(report)
                if report['class'] == 'TPV':
                    if hasattr(report, 'time'):
                        #print("time :" + report.time)
                        self.GpsTime = report.time

                    if hasattr(report, 'track'):
                        #print("Heading :" + str(report.track))
                        self.Heading = report.track
                    if hasattr(report, 'lon'):
                        #print("Langitude :" + str(report.lon))
                        self.Longitude = report.lon

                    if hasattr(report, 'lat'):
                        #print("Latitude :" + str(report.lat))
                        self.Latitude = report.lat
                    if hasattr(report, 'speed'):
                        self.Speed = (report.speed * gps.MPS_TO_KPH)
                    
                    gpsDataArray=[self.GpsTime,self.Heading,self.Longitude,
                                  self.Latitude,self.Speed,self.NumberOfsatelites]
                    self.q.put(gpsDataArray)

        except KeyError:
            pass
        except KeyboardInterrupt:
            quit()
        except StopIteration:
            session = None
            print("GPSD has terminated")

    def getGpsData(self):

        # Return the latest gpsdata:arrray[time,heading,long,lat,speed]
        if not self.q.empty():
            newdata = self.q.get()

            while not self.q.empty():
                trashBin = self.q.get()

            return newdata
        else:
            # print("empty Queue in seiralRead")
            noData = [None] * 6
            return noData

    def queReady(self):
        if not self.q.empty():
            return True
        else:
            return False