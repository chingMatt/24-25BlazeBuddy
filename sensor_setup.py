from gpiozero import DistanceSensor
from robot_config import *

# Initialize ultrasonic sensors
u1 = DistanceSensor(echo=u1_echo, trigger=u1_trig)  # front
u2 = DistanceSensor(echo=u2_echo, trigger=u2_trig)  # left
u3 = DistanceSensor(echo=u3_echo, trigger=u3_trig)  # right