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
- Ensure pyserial and pandas are installed (`pip install pyserial pandas`)
- Adjust serial port path if needed
- Run script and stop with Ctrl+C to save collected data

Note:
- The scale must be configured to send data automatically upon stable readings.
- For longer deployments, consider adding periodic autosave to CSV to avoid data loss.
- Additional filtering or validation of incoming data may be necessary for noisy environments.
"""

# ================================================================================================
#                                       Import modeuls
# ================================================================================================

import serial
import re
import pandas as pd
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import random
import os
import time
from waveshare_epd import epd2in13_V4

# ================================================================================================
#                                       Setup e-Paper Display
# ================================================================================================

epd = epd2in13_V4.EPD()
epd.init()
epd.Clear(0xFF)

EPD_WIDTH = epd.height
EPD_HEIGHT = epd.width

# Use built-in font or one from your system
small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
large_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)

# ================================================================================================
#                                       Display Functions (Text Only)
# ================================================================================================

def display_fat_deer_message(weight, epd):
    image = Image.new("1", (EPD_WIDTH, EPD_HEIGHT), 255)  # white background
    draw = ImageDraw.Draw(image)

    if weight >= 10:
        message = random.choice([
            ["Someone's been eating", "a lot of corn..."],
            ["Wait...are you sure", "you're not a red deer?"],
            ["Feeding site addict", "detected!"]
        ])
    else:
        message = ["All 4 hooves on the", "platform, please!"]

    # Draw each line of the message
    y = 5
    for line in message:
        draw.text((5, y), line, font=small_font, fill=0)
        line_height = small_font.getbbox(line)[3] - small_font.getbbox(line)[1]
        y += line_height + 2


    # Draw weight
    draw.text((25, 60), f"{int(weight):d}", font=large_font, fill=0)
    draw.text((145, 90), "kg", font=small_font, fill=0)

    epd.display(epd.getbuffer(image))

def display_waiting_message(epd):
    image = Image.new("1", (EPD_WIDTH, EPD_HEIGHT), 255)
    draw = ImageDraw.Draw(image)

    draw.text((10, 20), "Waiting for stable weight...", font=small_font, fill=0)
    epd.display(epd.getbuffer(image))

# ================================================================================================
#                                       Serial Setup & Parsing
# ================================================================================================

ser = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=2)

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


# ================================================================================================
#                                       USB Mounting
# ================================================================================================

def get_usb_mount_path():
    base_path = "/media/moocroftlab/"
    if os.path.exists(base_path):
        devices = os.listdir(base_path)
        if devices:
            return os.path.join(base_path, devices[0])  # Return first mounted device
    return None

def display_no_usb_warning(epd):
    image = Image.new("1", (EPD_WIDTH, EPD_HEIGHT), 255)
    draw = ImageDraw.Draw(image)

    warning_text = ["WARNING!", "No SD Card detected", "Please insert USB to continue."]
    y = 10
    for line in warning_text:
        draw.text((10, y), line, font=small_font, fill=0)
        y += 20

    epd.display(epd.getbuffer(image))


# ================================================================================================
#                                       Main Loop
# ================================================================================================

df = pd.DataFrame(columns=["Timestamp", "Gross", "Tare", "Net", "Unit"])

try:
    print("Waiting for scale data...")
    display_waiting_message(epd)

    weights = {}
    current_unit = ""

    while True:
        line = ser.readline().decode("utf-8", errors="ignore").strip()
        if line:
            result = parse_weight_line(line)
            if result:
                label, value, unit = result
                weights[label] = value
                current_unit = unit

                if all(k in weights for k in ("Gross", "Tare", "Net")):
                    net_weight = weights["Net"]

                    if net_weight > 0:

                        display_fat_deer_message(net_weight, epd)

                        new_row = pd.DataFrame([{
                            "Timestamp": datetime.now(),
                            "Gross": weights["Gross"],
                            "Tare": weights["Tare"],
                            "Net": net_weight,
                            "Unit": current_unit
                        }])

                        # Append new row to DataFrame
                        df = pd.concat([df, new_row], ignore_index=True)
                        print(df.tail(1))

                        # Append to CSV immediately (without header if file exists)
                        # Try saving to USB
                        usb_path = get_usb_mount_path()
                        if usb_path:
                            file_path = os.path.join(usb_path, "scale_weights.csv")
                            new_row.to_csv(file_path, mode='a', header=not os.path.exists(file_path), index=False)
                        else:
                            display_no_usb_warning(epd)
                            print("WARNING: No USB drive detected. Waiting for re-insertion...")

                            # Wait loop until USB is inserted
                            while not get_usb_mount_path():
                                time.sleep(1)
                            display_waiting_message(epd)


                    else:
                        display_waiting_message(epd)

                    weights.clear()

except KeyboardInterrupt:
    print("\nStopped by user.")

finally:
    ser.close()
    epd.sleep()
