
import time
import socket
import cv2



def videoStream(ipadress,port):
    cam = cv2.VideoCapture(0)
    cam.set(cv2.CAP_PROP_FPS,30)
    UDP_IP = ipadress
    UDP_PORT = port
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)



    # warmup camera
    time.sleep(0.1)
    while True:
        ret_val, img = cam.read(0)

        img = cv2.flip(img, 1)
        img = cv2.resize(img, (320, 240))

        x = [int(cv2.IMWRITE_JPEG_QUALITY), 80]
        _, compressed = cv2.imencode(".jpg", img, x)
        sock.sendto(compressed, (UDP_IP, UDP_PORT))

    rawCapture.truncate(0)



#if __name__ == "__main__": main()



