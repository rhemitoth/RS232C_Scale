import smbus2
from datetime import datetime

# ==========================
# Configuration
# ==========================
I2C_BUS = 1
RTC_ADDR = 0x68  # DS3231 default

bus = smbus2.SMBus(I2C_BUS)

# ==========================
# Helper functions
# ==========================
def int_to_bcd(val):
    """Convert integer to BCD format for DS3231 registers"""
    return ((val // 10) << 4) | (val % 10)

def set_rtc_time(dt):
    """
    Set DS3231 RTC time.
    dt: datetime object in UTC
    """
    data = [
        int_to_bcd(dt.second),
        int_to_bcd(dt.minute),
        int_to_bcd(dt.hour),
        int_to_bcd(dt.isoweekday()),  # 1 = Monday, 7 = Sunday
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
    # Get current system time (in UTC)
    system_time = datetime.utcnow()
    print(f"System UTC time: {system_time.isoformat()}")
    set_rtc_time(system_time)
