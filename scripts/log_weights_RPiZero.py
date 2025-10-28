"""
RS232 Scale Data Logger - Automatic Stable Weight Capture

This script connects to an electronic scale via RS232 serial port, which is configured
to send stable weight readings automatically when the measurement settles (no manual button press needed).

Features:
- Connects to serial port (default /dev/ttyAMA0 at 9600 baud)
- Parses lines of the form: "Gross: 1.23lb", "Tare: 0.00lb", "Net: 1.23lb"
- Collects a complete set of Gross, Tare, and Net weights before saving a record
- Stores data in a pandas DataFrame and exports to scale_weights.csv on exit
- Prints each recorded measurement row as it is added
- Timeout set for 2 seconds on serial read to balance responsiveness and CPU usage

Usage:
- Intended for use with a Raspberry Pi Zero
- Ensure pyserial and pandas are installed (`pip install pyserial pandas`)
- Adjust serial port path if needed

Note:
- The scale must be configured to send data automatically upon stable readings.
- Additional filtering or validation of incoming data may be necessary for noisy environments.
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

# ================================================================================================
#                                       Serial Setup & Parsing
# ================================================================================================
ser = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=1)

def parse_weight_line(line):
    """
    Parse a single line from scale output.
    Expected: "Gross: 1.23lb", "Tare: 0.00lb", "Net: 1.23lb"
    Returns: (label, value, unit) or None
    """
    match = re.search(r"(Gross|Tare|Net):\s*([\d\.]+)(lb|kg)?", line)
    if match:
        label = match.group(1)
        value = float(match.group(2))
        unit = match.group(3) if match.group(3) else ""
        return label, value, unit
    return None

def clean_line(raw_bytes):
    """Decode serial bytes and remove ASCII control characters"""
    line = raw_bytes.decode("utf-8", errors="ignore")
    line = re.sub(r'[\x00-\x1F\x7F]', '', line).strip()
    return line

# ================================================================================================
#                                       USB Mounting
# ================================================================================================
def get_usb_mount_path():
    """
    Returns the path of the first mounted USB drive under /media/{username}/
    Returns None if no drive is mounted.
    """
    username = "moorcroftlab"
    base_path = f"/media/{username}/"
    
    if not os.path.exists(base_path):
        print(f"Base path {base_path} does not exist")
        return None

    devices = os.listdir(base_path)
    if not devices:
        print("No devices found under /media/moorcroftlab/")
        return None

    for device in devices:
        device_path = os.path.join(base_path, device)
        if os.path.ismount(device_path):
            print(f"Detected mounted USB at: '{device_path}'")
            return device_path

    print("No USB drives mounted")
    return None

# ================================================================================================
#                                       Main Loop
# ================================================================================================
df = pd.DataFrame(columns=["Timestamp", "Gross", "Tare", "Net", "Unit"])

try:
    print("Waiting for scale data...")

    weights = {}
    current_unit = ""

    while True:
        # Read a raw line from the scale
        raw_line = ser.readline()
        if not raw_line:
            continue

        # Clean the line from control characters
        line = clean_line(raw_line)
        if not line:
            continue

        print("Received:", line)

        # Parse weight values
        result = parse_weight_line(line)
        if result:
            label, value, unit = result
            weights[label] = value
            current_unit = unit

        # If all three values are available, process
        if all(k in weights for k in ("Gross", "Tare", "Net")):
            net_weight = weights["Net"]

            if net_weight > 0:
                timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                new_row = pd.DataFrame([{
                    "Timestamp": timestamp,
                    "Gross": weights["Gross"],
                    "Tare": weights["Tare"],
                    "Net": net_weight,
                    "Unit": current_unit
                }])

                # Append to in-memory DataFrame
                df = pd.concat([df, new_row], ignore_index=True)
                print("Row ready to save:", new_row)

                # BLOCK until USB is available
                usb_path = get_usb_mount_path()
                while not usb_path:
                    print("WARNING: No USB drive detected. Waiting for insertion...")
                    time.sleep(1)
                    usb_path = get_usb_mount_path()

                # Save to CSV on USB
                file_path = os.path.join(usb_path, "scale_weights.csv")
                new_row.to_csv(file_path, mode='a', header=not os.path.exists(file_path), index=False)
                print(f"Saved to {file_path}")

            # Clear weights for the next set of readings
            weights.clear()

except KeyboardInterrupt:
    print("\nStopped by user.")

finally:
    ser.close()
