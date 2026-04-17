import json
import os
import time
from datetime import datetime

# File paths
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.json")
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "events.log")

# Valid states
LOCKED = "LOCKED"
PENDING_APPROVAL = "PENDING_APPROVAL"
OPEN = "OPEN"
OPEN_EXIT = "OPEN_EXIT"

VALID_STATES = [LOCKED, PENDING_APPROVAL, OPEN, OPEN_EXIT]


def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _write_log(message):
    """Append event to log file."""
    with open(LOG_FILE, "a") as f:
        f.write("[{}] {}\n".format(_now(), message))


def load_state():
    """Load state from file. Returns dict with state and metadata."""
    if not os.path.exists(STATE_FILE):
        state = {
            "state": LOCKED,
            "last_updated": _now(),
            "last_event": "System started (no state file, defaulting to LOCKED)"
        }
        save_state(LOCKED, "System started")
        return state

    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(new_state, event=""):
    """Save state to file and log the event."""
    if new_state not in VALID_STATES:
        raise ValueError("Invalid state: {}".format(new_state))

    data = {
        "state": new_state,
        "last_updated": _now(),
        "last_event": event
    }

    with open(STATE_FILE, "w") as f:
        json.dump(data, f, indent=2)

    log_msg = "STATE: -> {} | {}".format(new_state, event) if event else "STATE: -> {}".format(new_state)
    _write_log(log_msg)

    return data


def get_current_state():
    """Get just the current state string."""
    data = load_state()
    return data["state"]


def log_event(message):
    """Log an event without changing state."""
    _write_log("EVENT: {}".format(message))


def transition_to(new_state, event=""):
    """Transition to a new state with validation."""
    current = get_current_state()

    # Validate transitions
    valid_transitions = {
        LOCKED: [PENDING_APPROVAL, OPEN_EXIT],
        PENDING_APPROVAL: [OPEN, LOCKED],
        OPEN: [LOCKED],
        OPEN_EXIT: [LOCKED]
    }

    if new_state not in valid_transitions.get(current, []):
        log_event("WARNING: Invalid transition {} -> {} (keeping {})".format(current, new_state, current))
        return False

    save_state(new_state, event)
    return True
