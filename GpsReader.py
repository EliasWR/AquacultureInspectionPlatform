import gps
import queue

def gpsReader():
    global test
    test = "latitude"
    # Listen on port 2947 (gpsd) of localhost
    session = gps.gps("localhost", "2947")
    session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
    #outQueue.put(0)
    while True:
        try:
            report = session.next()
            # Wait for a 'TPV' report and display the current time
            # To see all report data, uncomment the line below
            # print(report)
            if report['class'] == 'TPV':
                if hasattr(report, 'time'):
                    print("time :"+report.time)


                if hasattr(report, 'alt'):
                    print("Altitude :"+str(report.alt))
                if hasattr(report, 'lan'):
                    print("Langitude :"+str(report.lan))
                if hasattr(report, 'lat'):
                    print("Latitude :"+str(report.lat))
                    #outQueue.put(report.lat)
                    test = str(report.lat)

        except KeyError:
            pass
        except KeyboardInterrupt:
            quit()
        except StopIteration:
            session = None
            print("GPSD has terminated")

