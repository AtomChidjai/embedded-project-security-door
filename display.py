import time
import lcddriver

lcd = lcddriver.lcd()

# Cache to avoid redundant writes
_cache_line1 = None
_cache_line2 = None


def show(line1, line2="", temp=0):
    """
    Display text on LCD (16 chars max per line).
    Use temp=N to show briefly then restore previous display.
    """
    global _cache_line1, _cache_line2

    if temp > 0:
        # Save what's currently showing
        prev1, prev2 = _cache_line1, _cache_line2
        lcd.lcd_clear()
        lcd.lcd_display_string(line1.ljust(16)[:16], 1)
        lcd.lcd_display_string(line2.ljust(16)[:16], 2)
        time.sleep(temp)
        # Restore previous display
        _cache_line1, _cache_line2 = None, None
        if prev1 is not None:
            show(prev1, prev2 or "")
        return

    # Skip if nothing changed
    if line1 == _cache_line1 and line2 == _cache_line2:
        return

    lcd.lcd_clear()
    lcd.lcd_display_string(line1.ljust(16)[:16], 1)
    lcd.lcd_display_string(line2.ljust(16)[:16], 2)
    _cache_line1 = line1
    _cache_line2 = line2


def clear():
    lcd.lcd_clear()


def cleanup():
    lcd.lcd_clear()
