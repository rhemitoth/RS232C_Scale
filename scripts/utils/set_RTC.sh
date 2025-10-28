#!/bin/bash
# ds3231-sync.sh
# Sync system time <-> DS3231 RTC on Raspberry Pi Zero

# Exit if any command fails
set -e

# I2C bus and RTC address
I2C_BUS=1
RTC_ADDR=0x68

# Check if i2c-tools is installed
if ! command -v i2cset &> /dev/null; then
    echo "i2c-tools not found. Installing..."
    sudo apt update
    sudo apt install -y i2c-tools
fi

# Check if DS3231 is detected
if ! i2cdetect -y $I2C_BUS | grep -q "$RTC_ADDR"; then
    echo "DS3231 not detected on I2C bus $I2C_BUS at address $RTC_ADDR"
    exit 1
fi

# Get current system time components
Y=$(date +%Y)
M=$(date +%m)
D=$(date +%d)
h=$(date +%H)
m=$(date +%M)
s=$(date +%S)

echo "Writing system time $Y-$M-$D $h:$m:$s to DS3231..."

# Convert decimal to BCD for DS3231
dec2bcd() {
    printf "%02x" $(( (10#$1 / 10 << 4) | (10#$1 % 10) ))
}

# Write time to DS3231
sudo i2cset -y $I2C_BUS $RTC_ADDR 0x00 $(dec2bcd $s)
sudo i2cset -y $I2C_BUS $RTC_ADDR 0x01 $(dec2bcd $m)
sudo i2cset -y $I2C_BUS $RTC_ADDR 0x02 $(dec2bcd $h)
sudo i2cset -y $I2C_BUS $RTC_ADDR 0x04 $(dec2bcd $D)
sudo i2cset -y $I2C_BUS $RTC_ADDR 0x05 $(dec2bcd $M)
sudo i2cset -y $I2C_BUS $RTC_ADDR 0x06 $(dec2bcd $((Y-2000)))

echo "RTC successfully updated!"

# Optional: read back RTC time and display
echo "Reading RTC time..."
for reg in 0x00 0x01 0x02 0x04 0x05 0x06; do
    val=$(i2cget -y $I2C_BUS $RTC_ADDR $reg)
    echo "Register $reg: $val"
done

echo "Done."
