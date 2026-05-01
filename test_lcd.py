import lcddriver
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

lcd = lcddriver.lcd()

lcd.lcd_display_string("HI eiei", 1)
