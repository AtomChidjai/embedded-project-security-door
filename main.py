import time
import config
import input
import state_manager as sm
import display

# Try to import dashboard (optional, requires Flask)
try:
    import dashboard
    DASHBOARD_ENABLED = True
except ImportError:
    DASHBOARD_ENABLED = False
    print("[MAIN] dashboard.py not available (Flask not installed?)")

entered_password = ""
last_state_change = 0
sensor_cooldown_until = 0


def cooldown_active():
    """Check if we're in sensor cooldown period."""
    return time.time() < sensor_cooldown_until


def set_cooldown(seconds=config.SENSOR_COOLDOWN):
    """Set sensor cooldown."""
    global sensor_cooldown_until
    sensor_cooldown_until = time.time() + seconds


def handle_keypad(key):
    """Handle keypad input in LOCKED state."""
    global entered_password

    if key == '#':  # Submit
        print("Submitting password (len={})".format(len(entered_password)))
        if entered_password == config.CORRECT_PASSWORD:
            sm.log_event("Correct password entered")
            input.send_telegram("Someone at the door. Let them in? (yes/no)")
            input.reset_telegram_updates()  # Ignore old messages
            sm.transition_to(sm.PENDING_APPROVAL, "Correct password, waiting for Telegram")
            display.show("Access Granted", "Ask approval..")
            set_cooldown(1)
        else:
            sm.log_event("Wrong password entered: " + entered_password)
            input.access_denied()
            display.show("Wrong Password!", "Try again", temp=2)
            input.buzzer_on()
            time.sleep(2)
            input.buzzer_off()
        entered_password = ""
    elif key == '*':  # Clear
        entered_password = ""
        display.show("Enter Password", "Cleared")
        sm.log_event("Password cleared")
    else:
        entered_password += key
        display.show("Enter Password", "*" * len(entered_password))
        print("Password so far: " + "*" * len(entered_password))


def handle_telegram_approval():
    """Check Telegram for approval in PENDING_APPROVAL state."""
    global last_state_change

    # Check timeout
    if time.time() - last_state_change > config.TELEGRAM_TIMEOUT:
        sm.log_event("Telegram approval timed out")
        input.access_denied()
        display.show("Approval Timeout", "Access Denied", temp=2)
        sm.transition_to(sm.LOCKED, "Approval timed out")
        return

    reply = input.check_reply()
    if reply is None:
        return

    if reply.strip().lower() == "yes":
        sm.log_event("Telegram approved entry")
        input.access_granted()
        input.open_door()
        display.show("APPROVED!", "Door opening..")
        sm.transition_to(sm.OPEN, "Door opened for incoming person")
        set_cooldown(2)
    elif reply.strip().lower() == "no":
        sm.log_event("Telegram denied entry")
        input.access_denied()
        display.show("Entry DENIED", "By owner", temp=2)
        sm.transition_to(sm.LOCKED, "Entry denied via Telegram")


def handle_open_state():
    """Handle OPEN state - waiting for person to enter."""
    global last_state_change

    if cooldown_active():
        return

    # If sensor detected person passing through
    if input.sensor_triggered():
        sm.log_event("Sensor detected person entered, closing door")
        display.show("Person entered", "Closing door..")
        input.close_door()
        input.access_denied()  # Reset LEDs
        sm.transition_to(sm.LOCKED, "Person entered, door closed")
        return

    # If no one passes within EXIT_OPEN_TIME, close automatically
    elapsed = time.time() - last_state_change
    if elapsed > config.EXIT_OPEN_TIME:
        sm.log_event("No one passed through, auto-closing door ({}s timeout)".format(config.EXIT_OPEN_TIME))
        display.show("Timeout", "Closing door..")
        input.close_door()
        input.access_denied()  # Reset LEDs
        sm.transition_to(sm.LOCKED, "Auto-closed after timeout")


def handle_locked_sensor():
    """Handle sensor in LOCKED state - detect person wanting to exit."""
    if cooldown_active():
        return

    if input.sensor_triggered():
        sm.log_event("Sensor detected person inside wanting to exit")
        input.access_granted()
        input.open_door()
        display.show("Exit detected", "Door opening..")
        sm.transition_to(sm.OPEN_EXIT, "Door opened for exit")
        set_cooldown(2)


def handle_open_exit():
    """Handle OPEN_EXIT state - waiting for person to leave."""
    global last_state_change

    if cooldown_active():
        return

    # If sensor is no longer triggered, person has left
    if not input.sensor_triggered():
        sm.log_event("Person exited, closing door")
        display.show("Person exited", "Closing door..")
        input.close_door()
        input.access_denied()  # Reset LEDs
        sm.transition_to(sm.LOCKED, "Person exited, door closed")
        set_cooldown(2)
        return

    # If no one exits within EXIT_OPEN_TIME, close automatically
    elapsed = time.time() - last_state_change
    if elapsed > config.EXIT_OPEN_TIME:
        sm.log_event("No one exited, auto-closing door ({}s timeout)".format(config.EXIT_OPEN_TIME))
        display.show("Timeout", "Closing door..")
        input.close_door()
        input.access_denied()  # Reset LEDs
        sm.transition_to(sm.LOCKED, "Auto-closed after timeout")


# ---- Main Loop ----
print("Security Door System v6 Started")
display.show("Security Door", "v6 Starting...")
time.sleep(1)
sm.log_event("========== System boot (v6) ==========")
sm.save_state(sm.LOCKED, "System started (v6)")
display.show("LOCKED", "Enter Password")

# Start web dashboard if available
if DASHBOARD_ENABLED:
    dashboard.start_dashboard(port=5000)
    sm.log_event("Web dashboard started on port 5000")

last_state_change = time.time()

try:
    while True:
        current_state = sm.get_current_state()

        # Always read keypad (only acts in LOCKED state)
        key = input.read_keypad()
        if key:
            print("Pressed:", key)
            if current_state == sm.LOCKED:
                handle_keypad(key)

        # State-specific behavior
        if current_state == sm.PENDING_APPROVAL:
            handle_telegram_approval()

        elif current_state == sm.OPEN:
            handle_open_state()

        elif current_state == sm.LOCKED:
            handle_locked_sensor()
            # Show idle locked screen only when no key was pressed
            if not key:
                display.show("LOCKED", "Enter Password")

        elif current_state == sm.OPEN_EXIT:
            handle_open_exit()

        # Track state changes for timeout logic
        new_state = sm.get_current_state()
        if new_state != current_state:
            last_state_change = time.time()
            print("State changed:", current_state, "->", new_state)

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nShutting down...")
    display.show("System OFF", "Goodbye!")
    time.sleep(1)
    sm.log_event("System shutdown (Ctrl+C)")
    display.cleanup()
    input.cleanup()
