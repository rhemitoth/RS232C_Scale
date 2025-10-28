#!/bin/bash
# set_RTC.sh
# Sync system time to DS3231 RTC on Raspberry Pi Zero
# Works even if hwclock is not installed

set -e

I2C_BUS=1
RTC_ADDR=0x68

# Install i2c-tools if missing
if ! command -v i2cset &> /dev/null; then
    echo "i2c-tools not found. Installing..."
    sudo apt update
    sudo apt install -y i2c-tools
fi

# Detect DS3231 (allow for 'UU' if kernel driver owns the device)
if ! i2cdetect -y $I2C_BUS | grep -E -q "68|UU"; then
    echo "DS3231 not detected on I2C bus $I2C_BUS (expected 0x68 or UU)"
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

# Only write to RTC if i2c-tools can access it (kernel overlay may block direct writes)
if i2cdetect -y $I2C_BUS | grep -q "68"; then
    sudo i2cset -y $I2C_BUS $RTC_ADDR 0x00 $(dec2bcd $s)
    sudo i2cset -y $I2C_BUS $RTC_ADDR 0x01 $(dec2bcd $m)
    sudo i2cset -y $I2C_BUS $RTC_ADDR 0x02 $(dec2bcd $h)
    sudo i2cset -y $I2C_BUS $RTC_ADDR 0x04 $(dec2bcd $D)
    sudo i2cset -y $I2C_BUS $RTC_ADDR 0x05 $(dec2bcd $M)
    sudo i2cset -y $I2C_BUS $RTC_ADDR 0x06 $(dec2bcd $((Y-2000)))
    echo "RTC successfully updated!"
else
    echo "RTC is bound to kernel driver (UU). You can use timedatectl to sync system time from RTC."
fi

# Optional: show RTC info via system interface
echo "RTC status via timedatectl:"
timedatectl status
