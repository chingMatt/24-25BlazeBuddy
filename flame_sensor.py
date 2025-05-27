import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Initialize I2C
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)

# Define flame sensor inputs
left_sensor = AnalogIn(ads, ADS.P0)
front_sensor = AnalogIn(ads, ADS.P1)
right_sensor = AnalogIn(ads, ADS.P2)

def get_flame_values():
    return left_sensor.value, front_sensor.value, right_sensor.value