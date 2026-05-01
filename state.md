# Security Door - State Diagram

## States

| State | Description |
|-------|-------------|
| `LOCKED` | Door closed. Waiting for keypad input. Sensor monitors for exit. |
| `PENDING_APPROVAL` | Correct password entered. Waiting for Telegram yes/no. |
| `OPEN` | Door opened for incoming person. Waiting for sensor to confirm entry. |
| `OPEN_EXIT` | Door opened for person exiting. Waiting for sensor to clear. |

## State Diagram

```
                    +-----------+
           +------>|   LOCKED  |<------+
           |       +-----------+       |
           |         |  ^   |  ^       |
           |         |  |   |  |       |
           |    keypad ok  |  |       |
           |         |  |   |  |       |
           |         v  |   |  |       |
           |  +--------------+ |       |
           |  |PENDING_APPROVAL| |       |
           |  +--------------+ |       |
           |    |          |   |       |
           | telegram   telegram      |
           |   yes        no/timeout  |
           |    |          |   |       |
           |    v          +---+       |
           | +------+                  |
           | | OPEN |                  |
           | +------+                  |
           |    |                      |
           | sensor detects            |
           | person entered            |
           |    |                      |
           |    +----------------------+
           |
           | sensor detects (from inside)
           |    |
           |    v
           | +----------+
           +>| OPEN_EXIT|
             +----------+
                 |
            sensor clears
            (person left)
                 |
                 +-----> back to LOCKED
```

## Transitions

| From | To | Trigger |
|------|----|---------|
| LOCKED | PENDING_APPROVAL | Correct password entered |
| LOCKED | OPEN_EXIT | Sensor detects person inside |
| PENDING_APPROVAL | OPEN | Telegram reply "yes" |
| PENDING_APPROVAL | LOCKED | Telegram reply "no" or timeout |
| OPEN | LOCKED | Sensor detects entry or timeout |
| OPEN_EXIT | LOCKED | Sensor clears or timeout |

## File Locations

| File | Purpose |
|------|---------|
| `state.json` | Current state (auto-created by state_manager.py) |
| `events.log` | Timestamped log of all state changes and events |
| `state.md` | This file - state diagram documentation |
| `state_manager.py` | State machine logic |
| `main.py` | Main loop |
| `input.py` | Hardware control (GPIO, keypad, servo, telegram) |
| `dashboard.py` | Web dashboard (Flask, port 5000) |
