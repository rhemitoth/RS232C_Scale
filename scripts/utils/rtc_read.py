import smbus2
from datetime import datetime

# I2C setup
bus = smbus2.SMBus(1)  # Use 1 for modern Pi boards
I2C_ADDR = 0x68        # Common for DS1307 / DS3231

# --- Helper functions ---
def bcd_to_int(bcd):
    return (bcd >> 4) * 10 + (bcd & 0x0F)

def detect_rtc():
    """Detect if the connected device is DS1307 or DS3231."""
    try:
        # Read control register (0x0E) — only DS3231 has this
        ctrl = bus.read_byte_data(I2C_ADDR, 0x0E)
        # If read succeeds, it’s a DS3231
        return "DS3231"
    except Exception:
        # DS1307 doesn’t have register 0x0E, will NACK this
        return "DS1307"

def ensure_clock_running():
    """For DS1307, clear CH (Clock Halt) bit if set."""
    sec_reg = bus.read_byte_data(I2C_ADDR, 0x00)
    if sec_reg & 0x80:
        print("Clock Halt bit set — clearing to start the clock.")
        bus.write_byte_data(I2C_ADDR, 0x00, sec_reg & 0x7F)

def read_rtc_time():
    data = bus.read_i2c_block_data(I2C_ADDR, 0x00, 7)
    second = bcd_to_int(data[0] & 0x7F)  # Mask CH bit
    minute = bcd_to_int(data[1])
    hour = bcd_to_int(data[2] & 0x3F)    # 24-hour mode only
    day = bcd_to_int(data[4])
    month = bcd_to_int(data[5] & 0x1F)
    year = bcd_to_int(data[6]) + 2000
    return datetime(year, month, day, hour, minute, second)

# --- Main logic ---
rtc_type = detect_rtc()
print(f"Detected RTC: {rtc_type}")

if rtc_type == "DS1307":
    ensure_clock_running()

try:
    rtc_time = read_rtc_time()
    print("RTC time (UTC):", rtc_time)
except Exception as e:
    print("Error reading RTC:", e)
