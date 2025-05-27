import RPi.GPIO as GPIO

# Motor Pin Definitions
in1 = 13  #  Left Motor +
in2 = 6   #  Left Motor -
in3 = 22  #  Right Motor +
in4 = 10  #  Right Motor -
ena = 5   #  Left Motor PWM
enb = 27  #  Right Motor PWM

# Encoder Pins
enc1a = 21  #  Right Encoder A
enc1b = 20  #  Right Encoder B
enc2a = 4   #  Left Encoder A
enc2b = 17  #  Left Encoder B

# Servo & Sensor Pins
sense = 19  #  Sense Wire for LD-3015MG servo motor
u1_echo = 16  #  Front Receiver
u1_trig = 26  #  Front Transmitter
u2_echo = 23  #  Left Receiver
u2_trig = 24  #  Left Transmitter
u3_echo = 14  #  Right Receiver
u3_trig = 15  #  Right Receiver
pump = 12     #  Pump Pin
frontServo = 25 #  Extinguishing servo
# GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(ena, GPIO.OUT)
GPIO.setup(in1, GPIO.OUT)
GPIO.setup(in2, GPIO.OUT)
GPIO.setup(enb, GPIO.OUT)
GPIO.setup(in3, GPIO.OUT)
GPIO.setup(in4, GPIO.OUT)