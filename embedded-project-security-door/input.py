# Setup & Telegram Config
import RPi.GPIO as GPIO
import time
import requests

GPIO.setmode(GPIO.BCM)

# Telegram config
BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"
CORRECT_PASSWORD = "12345"
entered_password = ""

# GPIO Mapping (Will prob adjust the pin number again later after the board is assembled)
# Keypad
ROW_PINS = [5, 6, 13, 19]
COL_PINS = [12, 16, 20, 21]
# Components
SERVO_PIN = 18
GREEN_LED = 23
RED_LED = 24
BUZZER = 25
SENSOR_PIN = 17

# Telegram Functions
def send_telegram(message):
    url = f"https://api.telegram.org/bot8642517842:AAG_CUdd0tQcgDQoTnByaPJd6HT48yL589E/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message})

def check_reply():
    url = f"https://api.telegram.org/bot8642517842:AAG_CUdd0tQcgDQoTnByaPJd6HT48yL589E/getUpdates"
    res = requests.get(url).json()
    
    if res["result"]:
        last_msg = res["result"][-1]["message"]["text"]
        return last_msg.lower()
    
    return None

# Servo Control
GPIO.setup(SERVO_PIN, GPIO.OUT)
servo = GPIO.PWM(SERVO_PIN, 50)
servo.start(0)

def open_door():
    servo.ChangeDutyCycle(7)  # adjust angle
    time.sleep(1)

def close_door():
    servo.ChangeDutyCycle(2)  # adjust angle
    time.sleep(1)

# LED + Buzzer
GPIO.setup(GREEN_LED, GPIO.OUT)
GPIO.setup(RED_LED, GPIO.OUT)
GPIO.setup(BUZZER, GPIO.OUT)

def access_granted():
    GPIO.output(GREEN_LED, 1)
    GPIO.output(RED_LED, 0)

def access_denied():
    GPIO.output(GREEN_LED, 0)
    GPIO.output(RED_LED, 1)
    GPIO.output(BUZZER, 1)
    time.sleep(2)
    GPIO.output(BUZZER, 0)

# Sensor
GPIO.setup(SENSOR_PIN, GPIO.IN)

def monitor_sensor():
    if GPIO.input(SENSOR_PIN):
        print("Object detected → closing door")
        close_door()

# Keypad
KEYPAD = [
    ['1','2','3','A'],
    ['4','5','6','B'],
    ['7','8','9','C'],
    ['*','0','#','D']
]

for r in ROW_PINS:
    GPIO.setup(r, GPIO.OUT)
    GPIO.output(r, 1)

for c in COL_PINS:
    GPIO.setup(c, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


def read_keypad():
    for i, row in enumerate(ROW_PINS):
        GPIO.output(row, 0)
        for j, col in enumerate(COL_PINS):
            if GPIO.input(col) == 1:
                GPIO.output(row, 1)
                return KEYPAD[i][j]
        GPIO.output(row, 1)
    return None