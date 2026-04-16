import time
import input

entered_password = ""

try:
    while True:
        if entered_password = "":
            output.update_lcd("Enter Password")

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
                        output.update_lcd("Access Granted!")
                        input.open_door()
                    else:
                        input.access_denied()
                        output.update_lcd("Access Denied!")
                else:
                    input.access_denied()
                    output.update_lcd("Incorrect", "Password...")
                    time.sleep(2)

                entered_password = ""

            else:
                entered_password += key
                output.update_lcd("Enter Password", key)

        # sensor auto close
        if input.sensor_triggered():
            print("Object detected → closing door")
            input.close_door()

        time.sleep(0.1)

except KeyboardInterrupt:
    input.cleanup()