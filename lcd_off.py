#!/usr/bin/env python3
"""
lcd_off.py - Display shutdown message and clear LCD.
Usage: sudo python3 lcd_off.py
"""

import time
import lcddriver

def main():
    lcd = lcddriver.lcd()
    
    # Show shutdown message
    lcd.lcd_clear()
    lcd.lcd_display_string("System OFF", 1)
    lcd.lcd_display_string("Goodbye!", 2)
    
    # Wait so user can see the message
    time.sleep(2)
    
    # Clear display and turn off backlight
    lcd.lcd_clear()
    
    # Turn off backlight by writing NOBACKLIGHT
    lcd.lcd_device.write_cmd(lcddriver.LCD_NOBACKLIGHT)
    
    print("[lcd_off] LCD cleared and backlight off.")

if __name__ == "__main__":
    main()
