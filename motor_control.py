import RPi.GPIO as GPIO
import pigpio
import time
from robot_config import *

# Initialize PWM for motors
power_a = GPIO.PWM(ena, 100)
power_b = GPIO.PWM(enb, 100)
power_a.start(0)
power_b.start(0)

# Initialize PWM for servo
pi = pigpio.pi()
pi.set_PWM_range(sense, 20000)
pi.set_PWM_frequency(sense, 50)
pi.set_PWM_dutycycle(sense, 1500)  # Start in the middle position
power_a.ChangeDutyCycle(5) # Used to be 10
power_b.ChangeDutyCycle(15) # USed to be 20

def delay(val):
    start = time.time()
    while time.time() - start < val:
        pass

def brake():
    power_a.ChangeDutyCycle(0)
    power_b.ChangeDutyCycle(0)
    GPIO.output(in1, GPIO.LOW)
    GPIO.output(in2, GPIO.LOW)
    GPIO.output(in3, GPIO.LOW)
    GPIO.output(in4, GPIO.LOW)

def forward():
    power_a.ChangeDutyCycle(5) # Used to be 10
    power_b.ChangeDutyCycle(15) # USed to be 20
    pi.set_PWM_dutycycle(sense, 1500)
    GPIO.output(in1, GPIO.HIGH)
    GPIO.output(in2, GPIO.LOW)
    GPIO.output(in3, GPIO.HIGH)
    GPIO.output(in4, GPIO.LOW)

def backward():
    power_a.ChangeDutyCycle(5) # Used to be 10
    power_b.ChangeDutyCycle(15) # USed to be 20
    GPIO.output(in1, GPIO.LOW)
    GPIO.output(in2, GPIO.HIGH)
    GPIO.output(in3, GPIO.LOW)
    GPIO.output(in4, GPIO.HIGH)

def leftTurn():
    power_a.ChangeDutyCycle(5) # Used to be 10
    power_b.ChangeDutyCycle(15) # USed to be 20
    pi.set_PWM_dutycycle(sense, 1000)
    GPIO.output(in1, GPIO.HIGH)
    GPIO.output(in2, GPIO.LOW)
    GPIO.output(in3, GPIO.HIGH)
    GPIO.output(in4, GPIO.LOW)

def rightTurn():
    power_a.ChangeDutyCycle(5) # Used to be 10
    power_b.ChangeDutyCycle(15) # USed to be 20
    pi.set_PWM_dutycycle(sense, 2000)
    GPIO.output(in1, GPIO.HIGH)
    GPIO.output(in2, GPIO.LOW)
    GPIO.output(in3, GPIO.HIGH)
    GPIO.output(in4, GPIO.LOW)

def slow():
    power_a.ChangeDutyCycle(5)
    power_b.ChangeDutyCycle(15)
    GPIO.output(in1, GPIO.HIGH)
    GPIO.output(in2, GPIO.LOW)
    GPIO.output(in3, GPIO.HIGH)
    GPIO.output(in4, GPIO.LOW)
