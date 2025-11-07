"""
RS232 Scale Data Logger - Automatic Stable Weight Capture

This script connects to an electronic scale via RS232 serial port, which is configured
to send stable weight readings automatically when the measurement settles (no manual button press needed).

Features:
- Connects to serial port (default /dev/ttyAMA0 at 9600 baud)
- Parses lines of the form: "Gross: 1.23lb", "Tare: 0.00lb", "Net: 1.23lb"
- Collects a complete set of Gross, Tare, and Net weights before saving a record
- Uses DS3231 RTC via I2C (smbus2) for accurate timestamps
- Stores data in a pandas DataFrame and exports to scale_weights.csv on exit
- Prints each recorded measurement row as it is added

Usage:
- Intended for use with a Raspberry Pi Zero
- Ensure pyserial, pandas, and smbus2 are installed (`pip install pyserial pandas smbus2`)
- Ensure the DS3231 is connected via I2C and overlay is disabled
"""

# ================================================================================================
#                                       Import modules
# ================================================================================================
import serial
import re
import pandas as pd
from datetime import datetime
import os
import time
import smbus2
import RPi.GPIO as GPIO

# ================================================================================================
#                                       LED Setup (GPIO 18)
# ================================================================================================
LED_PIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

# ================================================================================================
#                                       Serial Setup & Parsing
# ================================================================================================
ser = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=1)

def parse_weight_line(line):
    """Parse a line from scale: 'Gross: 1.23lb', 'Tare: 0.00lb', 'Net: 1.23lb'"""
    match = re.search(r"(Gross|Tare|Net):\s*([\d\.]+)(lb|kg)?", line)
    if match:
        label = match.group(1)
        value = float(match.group(2))
        unit = match.group(3) if match.group(3) else ""
        return label, value, unit
    return None

def clean_line(raw_bytes):
    """Decode serial bytes and remove control characters"""
    line = raw_bytes.decode("utf-8", errors="ignore")
    return re.sub(r'[\x00-\x1F\x7F]', '', line).strip()

# ================================================================================================
#                                       USB Mounting
# ================================================================================================
def get_usb_mount_path():
    username = "moorcroftlab"
    base_path = f"/media/{username}/"
    if not os.path.exists(base_path):
        return None
    devices = os.listdir(base_path)
    for device in devices:
        device_path = os.path.join(base_path, device)
        if os.path.ismount(device_path):
            return device_path
    return None

# ================================================================================================
#                                       RTC via SMBus (DS3231)
# ================================================================================================
I2C_BUS = 1
RTC_ADDR = 0x68
bus = smbus2.SMBus(I2C_BUS)

def bcd_to_int(bcd):
    """Convert BCD byte to integer"""
    return ((bcd >> 4) * 10) + (bcd & 0x0F)

def get_rtc_time():
    """Read time from DS3231 RTC via I2C and return UTC datetime"""
    try:
        data = bus.read_i2c_block_data(RTC_ADDR, 0x00, 7)
        second = bcd_to_int(data[0] & 0x7F)
        minute = bcd_to_int(data[1])
        hour = bcd_to_int(data[2] & 0x3F)
        day = bcd_to_int(data[4])
        month = bcd_to_int(data[5] & 0x1F)
        year = 2000 + bcd_to_int(data[6])
        return datetime(year, month, day, hour, minute, second)
    except Exception as e:
        print(f"Failed to read RTC: {e}")
        return datetime.utcnow()

# ================================================================================================
#                                       USB Flash
# ================================================================================================

def flash_led(times=2):
    """Flash the LED connected to GPIO 18."""
    for _ in range(times):
        GPIO.output(LED_PIN, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(LED_PIN, GPIO.LOW)
        time.sleep(0.5)


# ================================================================================================
#                                       Main Loop
# ================================================================================================
df_columns = ["Timestamp", "Gross", "Tare", "Net", "Unit", "Timezone"]
df = pd.DataFrame(columns=df_columns)

try:
    print("Waiting for scale data...")

    weights = {}
    current_unit = ""

    while True:
        raw_line = ser.readline()
        if not raw_line:
            continue

        line = clean_line(raw_line)
        if not line:
            continue

        print("Received:", line)

        result = parse_weight_line(line)
        if result:
            label, value, unit = result
            weights[label] = value
            current_unit = unit

        if all(k in weights for k in ("Gross", "Tare", "Net")):
            net_weight = weights["Net"]
            if net_weight > 0:
                # Get timestamp from DS3231
                rtc_dt = get_rtc_time()
                timestamp = rtc_dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + " UTC"

                new_row = pd.DataFrame([{
                    "Timestamp": timestamp,
                    "Gross": weights["Gross"],
                    "Tare": weights["Tare"],
                    "Net": net_weight,
                    "Unit": current_unit,
                    "Timezone": "UTC"
                }], columns=df_columns)

                # Append to in-memory DataFrame
                df = pd.concat([df, new_row], ignore_index=True)
                print("Row ready to save:", new_row)

                # BLOCK until USB is available
                usb_path = get_usb_mount_path()
                while not usb_path:
                    print("WARNING: No USB drive detected. Waiting...")
                    time.sleep(1)
                    usb_path = get_usb_mount_path()

                # Save to CSV on USB (header written only once)
                file_path = os.path.join(usb_path, "scale_weights.csv")
                new_row.to_csv(file_path, mode='a', header=not os.path.exists(file_path), index=False)
                print(f"Saved to {file_path}")
                flash_led(2)

            # Clear weights for the next reading
            weights.clear()

except KeyboardInterrupt:
    print("\nStopped by user.")

finally:
    ser.close()
    bus.close()
    GPIO.cleanup()
