# Security Door System v3 — Project Summary

## Overview
A Raspberry Pi-based security door system with keypad entry, Telegram approval, servo-controlled door, IR sensor, LCD display, LEDs, and buzzer.

## File Inventory

| File | Purpose |
|------|---------|
| `main.py` | Main loop — state machine driver |
| `input.py` | All hardware I/O: GPIO, keypad, servo, LEDs, buzzer, sensor, Telegram API |
| `config.py` | All tunable constants: pins, passwords, tokens, timing |
| `state_manager.py` | State machine logic with file persistence and event logging |
| `display.py` | LCD wrapper with caching and temporary display support |
| `lcddriver.py` | Low-level I2C LCD driver (HD44780 compatible) |
| `i2c_lib.py` | SMBus I2C communication driver |
| `state.json` | Current state (auto-created, not for editing) |
| `events.log` | Timestamped event log (auto-created) |
| `state.md` | State diagram documentation |
| `test_lcd.py` | Quick LCD test script (not part of main system) |
| `README.md` | Placeholder (minimal) |

## State Machine

```
LOCKED → (correct keypad) → PENDING_APPROVAL
PENDING_APPROVAL → (telegram "yes") → OPEN
PENDING_APPROVAL → (telegram "no" / timeout) → LOCKED
OPEN → (sensor detects entry) → LOCKED
LOCKED → (sensor detects exit from inside) → OPEN_EXIT
OPEN_EXIT → (sensor clears) → LOCKED
```

## Hardware Wiring (GPIO BCM)

| Component | Pin |
|-----------|-----|
| Keypad Rows | 5, 6, 13, 19 |
| Keypad Cols | 12, 16, 20, 21 |
| Servo | 18 |
| Green LED | 23 |
| Red LED | 24 |
| Buzzer | 25 |
| IR Sensor | 17 |
| LCD (I2C) | Bus 1, Address 0x3F |

## Config Values

- **Password:** `123456`
- **Telegram timeout:** 30 seconds
- **Sensor cooldown:** 3 seconds
- **Servo duty:** Open=7, Close=2
- **Exit open time:** 10 seconds

## Dependencies
- `RPi.GPIO` — GPIO control
- `requests` — Telegram API calls
- `smbus` — I2C communication

## How to Run
```bash
cd version_3
sudo python3 main.py
```
(`sudo` required for GPIO access)

## Known Issues Fixed (2026-04-17)
- `KeyError: 'result'` in `reset_telegram_updates()` and `check_reply()` — changed `res["result"]` to `res.get("result")`
- Added error handling (try/except, timeouts, status code checks) to all Telegram functions in `input.py`
- Added console logging (`[TELEGRAM]` prefix) for debugging send/receive failures
