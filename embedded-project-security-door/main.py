import time
import input

entered_password = ""

try:
    while True:
        key = input.read_keypad()

        if key:
            print("Pressed:", key)

            if key == '#':  # # = submit
                if entered_password == input.CORRECT_PASSWORD:
                    input.send_telegram("Password correct. Are you the one? (yes/no)")

                    time.sleep(5)
                    reply = input.check_reply()

                    if reply == "yes":
                        input.access_granted()
                        input.open_door()
                    else:
                        input.access_denied()
                else:
                    input.access_denied()

                entered_password = ""

            else:
                entered_password += key

        # sensor auto close
        if input.sensor_triggered():
            print("Object detected → closing door")
            input.close_door()

        time.sleep(0.1)

except KeyboardInterrupt:
    input.cleanup()