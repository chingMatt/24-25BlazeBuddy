import RPi.GPIO as GPIO
import pigpio
import time
from robot_config import *
from flame_sensor import get_flame_values
from motor_control import delay


# ---- Constants ----
MIN_PULSE = 1250
MAX_PULSE = 1625
STEP_DELAY = 0.1

# ---- Setup ----

# Initialize pigpio and GPIO
pi = pigpio.pi()
if not pi.connected:
    raise RuntimeError("Cannot connect to pigpio daemon")

GPIO.setmode(GPIO.BCM)
pi.set_mode(12, pigpio.OUTPUT)

# ---- Extinguish Function ----
def extinguish():
    print("Extinguishing...")

    # Turn on the pump
    pi.write(12, 1)
    print("Pump ON")

    start_time = time.time()

    while time.time() - start_time < 12.5:
        # Sweep servo from 67.5 to 112.5 (1250 to 1625 us) in 50 us steps
        for pulse in range(MIN_PULSE, MAX_PULSE + 1, 50):
            pi.set_servo_pulsewidth(frontServo, pulse)
            time.sleep(STEP_DELAY)

        # Sweep back from 112.5 to 67.5 (1625 to 1250 us)
        for pulse in range(MAX_PULSE, MIN_PULSE - 1, -50):
            pi.set_servo_pulsewidth(frontServo, pulse)
            time.sleep(STEP_DELAY)