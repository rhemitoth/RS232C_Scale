#!/bin/bash
# run_logger.sh

# Wait a bit for I2C bus to initialize
sleep 2

# Attempt to reset I2C bus if RTC not detected
if ! i2cdetect -y 1 | grep -q 68; then
    echo "RTC not detected, resetting I2C bus..."
    sudo rmmod i2c_bcm2835
    sudo modprobe i2c_bcm2835
    sleep 1
fi

# Activate virtual environment
source /home/moorcroftlab/scale/bin/activate

# Run Python script
exec python /home/moorcroftlab/Documents/RS232C_Scale/scripts/log_weights_RPi.py
