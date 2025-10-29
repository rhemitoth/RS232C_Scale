import smbus2
from datetime import datetime

# I2C bus (1 for Pi Zero)
bus = smbus2.SMBus(1)
address = 0x68  # DS3231 I2C address

# Helper functions
def bcd_to_int(bcd):
    return (bcd >> 4) * 10 + (bcd & 0x0F)

def read_rtc_time():
    data = bus.read_i2c_block_data(address, 0x00, 7)
    second = bcd_to_int(data[0])
    minute = bcd_to_int(data[1])
    hour = bcd_to_int(data[2])
    day = bcd_to_int(data[4])
    month = bcd_to_int(data[5] & 0x1F)
    year = bcd_to_int(data[6]) + 2000
    return datetime(year, month, day, hour, minute, second)

# Read RTC
rtc_time = read_rtc_time()
print("RTC time (UTC):", rtc_time)
