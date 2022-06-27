import RPi.GPIO as GPIO
import time


class CameraServoController():
    def __init__(self):


        self.servo = 22

        GPIO.setmode(GPIO.BOARD)

        GPIO.setup(self.servo, GPIO.OUT)
        # in servo motor,
        # 1ms pulse for 0 degree (LEFT)
        # 1.5ms pulse for 90 degree (MIDDLE)
        # 2ms pulse for 180 degree (RIGHT)

        # so for 50hz, one frequency is 20ms
        # duty cycle for 0 degree = (1/20)*100 = 5%
        # duty cycle for 90 degree = (1.5/20)*100 = 7.5%
        # duty cycle for 180 degree = (2/20)*100 = 10%

        self.p = GPIO.PWM(self.servo, 50)  # 50hz frequency

        self.p.start(2.5)  # starting duty cycle ( it set the servo to 0 degree )


    def changeToForwardPos(self):
        self.p.changeDutyCycle (2.5)

    def changeToRovPos(self):
        self.p.changeDutyCycle (13)