# Security Door System v6 - Project Summary

## Overview

Embedded security door system สำหรับ Raspberry Pi ที่ควบคุมด้วย **keypad**, **servo motor**, **Telegram bot**, และ **sensor** เพื่อจัดการการเข้า-ออกประตูอย่างปลอดภัย

---

## System Architecture

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   Keypad     │───▶│              │───▶│  Servo Motor │
│  (4x4 matrix)│    │              │    │  (SG90)      │
└─────────────┘    │              │    └─────────────┘
                    │   main.py    │
┌─────────────┐    │  (Main Loop) │    ┌─────────────┐
│   Sensor     │───▶│              │───▶│  LED + Buzzer│
│  (IR/PIR)    │    │              │    └─────────────┘
└─────────────┘    │              │
                    │              │    ┌─────────────┐
┌─────────────┐    │              │───▶│  LCD 16x2    │
│  Telegram    │◀──▶│              │    │  (I2C)       │
│  Bot API     │    └──────────────┘    └─────────────┘
└─────────────┘            │
                    ┌──────────────┐
                    │  Web Dashboard│
                    │  (Flask:5000) │
                    └──────────────┘
```

---

## State Machine

```
                    +-----------+
           +------>|   LOCKED  |<------+
           |       +-----------+       |
           |         |  ^   |  ^       |
           |    keypad ok  |  |       |
           |         v  |   |  |       |
           |  +--------------+ |       |
           |  |PENDING_APPROVAL| |      |
           |  +--------------+ |       |
           |    |          |   |       |
           |   yes      no/timeout     |
           |    v          +---+       |
           | +------+                  |
           | | OPEN |                  |
           | +------+                  |
           |    |                      |
           | sensor  +-----------------+
           |    +----+
           |
           | sensor detects (inside)
           |    v
           | +----------+
           +>| OPEN_EXIT|
             +----------+
                 |
            sensor clears
                 +-----> LOCKED
```

| State | Description |
|-------|-------------|
| `LOCKED` | ประตูปิด รอกรอก password |
| `PENDING_APPROVAL` | รหสถูกต้อง รอ Telegram approve |
| `OPEN` | ประตูเปิดให้เข้า รอ sensor ตรวจจับ |
| `OPEN_EXIT` | ประตูเปิดให้ออก รอ sensor ว่าง |

---

## File Structure

| File | Purpose |
|------|---------|
| `main.py` | Main loop - state machine logic, keypad handler, sensor handler |
| `config.py` | Configuration: pin mapping, password, timing, servo duty |
| `input.py` | Hardware I/O: GPIO, keypad scan, servo, LED, buzzer, sensor, Telegram |
| `display.py` | LCD display wrapper with caching and temp display support |
| `state_manager.py` | State machine: load/save state, transition validation, event logging |
| `dashboard.py` | Web dashboard (Flask) - real-time status, logs, statistics |
| `lcddriver.py` | Low-level HD44780 LCD driver (I2C via PCF8574) |
| `i2c_lib.py` | I2C bus communication (smbus) |
| `lcd_off.py` | Shutdown script - shows goodbye message, clears LCD, turns off backlight |
| `test_lcd.py` | LCD test utility |
| `state.json` | Current state file (auto-generated) |
| `events.log` | Timestamped event log |
| `state.md` | State diagram documentation |

---

## Hardware Configuration

### GPIO Pin Mapping (BCM)

| Pin | Component |
|-----|-----------|
| GPIO 5, 6, 13, 19 | Keypad Rows |
| GPIO 12, 16, 20, 21 | Keypad Columns |
| GPIO 18 | Servo Motor (PWM) |
| GPIO 23 | Green LED (Access Granted) |
| GPIO 24 | Red LED (Access Denied) |
| GPIO 25 | Buzzer |
| GPIO 17 | IR/PIR Sensor |

### I2C Devices

| Address | Device |
|---------|--------|
| 0x3F | LCD 16x2 (PCF8574) |

### Servo (SG90)

| State | Duty Cycle | Pulse | Position |
|-------|------------|-------|----------|
| Open | 5% | 1.0ms | 0° |
| Closed | 11% | 2.0ms | 180° |

---

## Configuration (`config.py`)

```python
TELEGRAM_TIMEOUT = 30    # seconds to wait for Telegram reply
SENSOR_COOLDOWN  = 3     # seconds to ignore sensor after state change
EXIT_OPEN_TIME   = 30    # seconds door stays open before auto-close
```

---

## Flow Diagrams

### Entry Flow (คนเข้า)

```
1. กด password บน keypad
2. ถ้าถูกต้อง → ส่ง Telegram "Someone at the door. Let them in?"
3. รอ reply (timeout 30s)
4. Reply "yes" → servo เปิดประตู → แสดง "APPROVED!"
5. รอ sensor ตรวจจับคนเข้า → ปิดประตู → กลับ LOCKED
6. Reply "no" → แสดง "Entry DENIED" → กลับ LOCKED
7. Timeout → แสดง "Approval Timeout" → กลับ LOCKED
```

### Exit Flow (คนออก)

```
1. Sensor ตรวจจับคนจากด้านใน
2. แสดง "Exit detected" → servo เปิดประตู
3. รอ sensor ว่าง (คนเดินออก)
4. แสดง "Person exited" → ปิดประตู → กลับ LOCKED
5. Timeout 30s → auto-close → กลับ LOCKED
```

---

## Web Dashboard

- **URL:** `http://<raspberry-pi-ip>:5000`
- **Auto-refresh:** ทุก 5 วินาที
- **Features:**
  - สถานะประตูปัจจุบัน (สีบอก state)
  - สถิติวันนี้ (events, denied attempts, uptime)
  - 20 log entries ล่าสุด

---

## Key Design Decisions

1. **Servo หมุนกลับ** — SG90 ติดตั้งย้อนทิศ ทำให้ duty ต่ำ = เปิด, duty สูง = ปิด
2. **LCD clear delay** — HD44780 ต้องการ ~1.52ms หลัง clear command จึงเพิ่ม `sleep(0.002)`
3. **Sensor debounce** — อ่าน sensor 5 ครั้ง ต้อง HIGH ครบ 5 ครั้งถึงจะ trigger
4. **PWM stop after move** — เปลี่ยน duty เป็น 0 หลัง servo หมุนเสร็จ เพื่อป้องกัน servo ร้อน
5. **Display caching** — `display.py` เก็บ cache ของข้อความล่าสุด ไม่เขียนซ้ำถ้าไม่เปลี่ยน
6. **Telegram reset** — ล้าง update เก่าก่อนรอ reply ใหม่ ป้องกันอ่านข้อความเก่า

---

## Commands

```bash
# Start system
cd version_6
nohup sudo python3 main.py >> events.log 2>&1 &

# Stop system
sudo pkill -2 -f "python3 main.py"
python3 lcd_off.py

# Check status
ps aux | grep "[p]ython3 main.py"
cat state.json
tail -20 events.log

# View dashboard
# Open browser: http://<ip>:5000
```

---

## Dependencies

```
RPi.GPIO
requests
smbus
flask (optional - for dashboard)
```

---

## Version History

| Version | Changes |
|---------|---------|
| v6 | Current version with Telegram approval, exit sensor, web dashboard, LCD timing fix, exit display delay |

---

*Project: Embedded Security Door System*
*Platform: Raspberry Pi*
*Language: Python 3*
