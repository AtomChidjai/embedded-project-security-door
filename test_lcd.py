import lcddriver
from time import *
import time
import RPi.GPIO as GPIO

# adc = Adafruit_ADS1x15.ADS1115()

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

# range from 0 to 30687
lcd = lcddriver.lcd()

lcd.lcd_display_string("HI eiei", 1)

