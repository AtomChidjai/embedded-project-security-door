from time import *
import lcddriver
import RPi.GPIO as GPIO
import time

SERVO_PIN = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

servo = GPIO.PWM(SERVO_PIN, 50) # set up frequency
servo.start(0)

lcd = lcddriver.lcd()

def update_lcd(message1, message2=None):
    lcd.lcd_clear()
    if message2 is None:
        lcd.lcd_display_string(message1, 1)
    else:
        lcd.lcd_display_string(message1, 1)
        lcd.lcd_display_string(message2, 2)


def control_servo(angle):
    duty = 2 + (angle / 18)
    GPIO.output(SERVO_PIN, True)
    servo.ChangeDutyCycle(duty)
    time.sleep(0.5)
    GPIO.output(SERVO_PIN, False)
    servo.ChangeDutyCycle(0)

def open_door():
    set_angle(90)

def close_door():
    set_angle(0)