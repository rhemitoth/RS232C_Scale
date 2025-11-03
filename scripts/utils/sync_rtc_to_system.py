import smbus2
from datetime import datetime

# ==========================
# Configuration
# ==========================
I2C_BUS = 1
RTC_ADDR = 0x68  # Default I2C address for DS1307/DS3231
bus = smbus2.SMBus(I2C_BUS)

# ==========================
# Helper functions
# ==========================
def int_to_bcd(val):
    """Convert integer to BCD format for RTC registers"""
    return ((val // 10) << 4) | (val % 10)

def detect_rtc():
    """
    Detect whether the connected chip is DS1307 or DS3231.
    DS3231 has registers beyond 0x0E; DS1307 does not.
    """
    try:
        bus.read_byte_data(RTC_ADDR, 0x0E)  # DS3231 Control Register
        return "DS3231"
    except Exception:
        return "DS1307"

def ensure_clock_running():
    """For DS1307, clear the CH (Clock Halt) bit if set."""
    sec_reg = bus.read_byte_data(RTC_ADDR, 0x00)
    if sec_reg & 0x80:
        print("Clock Halt bit detected — clearing to start the DS1307 clock.")
        bus.write_byte_data(RTC_ADDR, 0x00, sec_reg & 0x7F)

def set_rtc_time(dt):
    """
    Set RTC time for DS1307 or DS3231.
    dt: datetime object in UTC
    """
    # Prepare 7 bytes for registers 0x00–0x06
    data = [
        int_to_bcd(dt.second),
        int_to_bcd(dt.minute),
        int_to_bcd(dt.hour),
        int_to_bcd(dt.isoweekday()),  # 1=Mon, 7=Sun
        int_to_bcd(dt.day),
        int_to_bcd(dt.month),
        int_to_bcd(dt.year - 2000),
    ]
    bus.write_i2c_block_data(RTC_ADDR, 0x00, data)
    print(f"RTC time set to: {dt.isoformat()} UTC")

# ==========================
# Main Logic
# ==========================
if __name__ == "__main__":
    rtc_type = detect_rtc()
    print(f"Detected RTC: {rtc_type}")

    if rtc_type == "DS1307":
        ensure_clock_running()

    # Get current system time (UTC)
    system_time = datetime.utcnow()
    print(f"System UTC time: {system_time.isoformat()}")

    set_rtc_time(system_time)
