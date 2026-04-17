# Setup & Telegram Config
import RPi.GPIO as GPIO
import time
import requests
import config

GPIO.setmode(GPIO.BCM)

# Telegram Functions
last_update_id = 0

def send_telegram(message):
    url = 'https://api.telegram.org/bot{}/sendMessage'.format(config.BOT_TOKEN)
    try:
        r = requests.post(url, data={"chat_id": config.CHAT_ID, "text": message}, timeout=10)
        if r.status_code != 200:
            print("[TELEGRAM] send failed: {} - {}".format(r.status_code, r.text))
            return False
        print("[TELEGRAM] Message sent: {}".format(message))
        return True
    except Exception as e:
        print("[TELEGRAM] send error: {}".format(e))
        return False

def check_reply():
    global last_update_id
    url = 'https://api.telegram.org/bot{}/getUpdates'.format(config.BOT_TOKEN)
    try:
        r = requests.get(url, params={"offset": last_update_id + 1}, timeout=10)
        res = r.json()
    except Exception as e:
        print("[TELEGRAM] check_reply error: {}".format(e))
        return None

    if not res.get("result"):
        return None

    # Walk through new updates, keep only the latest text message
    latest_text = None
    for update in res["result"]:
        last_update_id = update["update_id"]
        if "message" in update and "text" in update["message"]:
            latest_text = update["message"]["text"]

    return latest_text.lower() if latest_text else None

def reset_telegram_updates():
    """Mark all current updates as read so next check_reply() only sees new ones."""
    global last_update_id
    url = 'https://api.telegram.org/bot{}/getUpdates'.format(config.BOT_TOKEN)
    try:
        r = requests.get(url, timeout=10)
        res = r.json()
        if res.get("result"):
            last_update_id = res["result"][-1]["update_id"]
            print("[TELEGRAM] Reset updates, last_update_id={}".format(last_update_id))
    except Exception as e:
        print("[TELEGRAM] reset error: {}".format(e))

# Servo Control
GPIO.setup(config.SERVO_PIN, GPIO.OUT)
servo = GPIO.PWM(config.SERVO_PIN, 50)
servo.start(0)

def open_door():
    servo.ChangeDutyCycle(config.SERVO_OPEN_DUTY)
    time.sleep(1)

def close_door():
    servo.ChangeDutyCycle(config.SERVO_CLOSE_DUTY)
    time.sleep(1)

# LED + Buzzer
GPIO.setup(config.GREEN_LED, GPIO.OUT)
GPIO.setup(config.RED_LED, GPIO.OUT)
GPIO.setup(config.BUZZER, GPIO.OUT)

def access_granted():
    GPIO.output(config.GREEN_LED, 1)
    GPIO.output(config.RED_LED, 0)

def access_denied():
    GPIO.output(config.GREEN_LED, 0)
    GPIO.output(config.RED_LED, 1)

# Sensor
GPIO.setup(config.SENSOR_PIN, GPIO.IN)

def sensor_triggered():
    """Debounced sensor read - requires 5 consecutive HIGH readings."""
    count = 0
    for _ in range(5):
        if GPIO.input(config.SENSOR_PIN) == 1:
            count += 1
        time.sleep(0.05)
    return count >= 5

def cleanup():
    servo.stop()
    GPIO.cleanup()

# Rows as INPUT with pull-up (idle=HIGH, pressed=LOW)
for r in config.ROW_PINS:
    GPIO.setup(r, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Columns as OUTPUT, default HIGH
for c in config.COL_PINS:
    GPIO.setup(c, GPIO.OUT)
    GPIO.output(c, 1)


def read_keypad():
    for i, col_pin in enumerate(config.COL_PINS):
        GPIO.output(col_pin, 0)
        for j, row_pin in enumerate(config.ROW_PINS):
            if GPIO.input(row_pin) == 0:
                # Wait for release (debounce)
                while GPIO.input(row_pin) == 0:
                    time.sleep(0.02)
                GPIO.output(col_pin, 1)
                return config.KEYPAD[j][i]
        GPIO.output(col_pin, 1)
    return None


def buzzer_on():
    GPIO.output(config.BUZZER, 1)


def buzzer_off():
    GPIO.output(config.BUZZER, 0)
