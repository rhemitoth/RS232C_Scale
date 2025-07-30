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

# ================================================================================================
#                                       Load e-Paper Displaydriver
# ================================================================================================

# Driver
from waveshare_epd import epd2in13_V4  
epd = epd2in13_V4.EPD()
epd.init()
epd.Clear(0xFF)

# font
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)

# ================================================================================================
#                                       Load Deer Image
# ================================================================================================

deer_img = Image.open("/home/moorcroftlab/Documents/RS232C_Scale/deer_image/epaper_display.bmp").resize((50,100)).convert("1")

# ================================================================================================
#                                       Fat Deer Message
# ================================================================================================

def display_fat_deer_message(weight, epd, deer_img):
    # Use pre-designed background image with speech bubble and black rectangle
    image = deer_img.convert("1").copy()
    draw = ImageDraw.Draw(image)

    # Font setup
    small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    large_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)


    # Pick message
    if weight >= 10:
        message = random.choice([
            "Someone has been eating too much corn...",
            "Wait...are you sure you're not a red deer?",
            "Looks like we've got ourselves another feeding site addict"
        ])
    else:
        message = "All four hooves on the platform, please!"

    # Draw message in speech bubble (assumes white background)
    draw.text((125, 20), message, font=small_font, fill=0)

    # Draw weight in large white numbers (on pre-existing black rectangle)
    draw.text((130, 70), f"{int(weight):d}", font=large_font, fill=255)

    # Draw "kg" in smaller white font below the number
    draw.text((130, 115), "kg", font=small_font, fill=255)

    # Display final image
    epd.display(epd.getbuffer(image))

   
# ================================================================================================
#                                       waiting message
# ================================================================================================

def display_waiting_message(weight, epd, deer_img):
    # Use pre-designed background image with speech bubble and black rectangle
    image = deer_img.convert("1").copy()
    draw = ImageDraw.Draw(image)

    # Font setup
    small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    large_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)


    message = "I'm waiting..."

    # Draw message in speech bubble (assumes white background)
    draw.text((125, 20), message, font=small_font, fill=0)

    # Draw weight in large white numbers (on pre-existing black rectangle)
    draw.text((130, 70), f"{int(weight):d}", font=large_font, fill=255)

    # Draw "kg" in smaller white font below the number
    draw.text((130, 115), "kg", font=small_font, fill=255)

    # Display final image
    epd.display(epd.getbuffer(image))


# Open serial connection to the scale
# Adjust "/dev/ttyAMA0" if your device is on a different port
ser = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=2)

def parse_weight_line(line):
    """
    Parse a single line of text from the scale's serial output.

    Expected format examples:
      "Gross:  1.23lb"
      "Tare:   0.00lb"
      "Net:    1.23lb"

    Returns:
      tuple (label, value, unit) if matched, e.g. ("Gross", 1.23, "lb")
      None if the line does not match expected pattern.
    """
    match = re.search(r"(Gross|Tare|Net):\s*([\d\.]+)(lb|kg)?", line)
    if match:
        label = match.group(1)
        value = float(match.group(2))
        unit = match.group(3) if match.group(3) else ""
        return label, value, unit
    return None

# Initialize an empty DataFrame to store weight data
df = pd.DataFrame(columns=["Timestamp", "Gross", "Tare", "Net", "Unit"])

try:
    print("Waiting for scale data... The scale will send stable readings automatically.")
    display_waiting_message(0.0, epd, deer_img)


    weights = {}        # Temporary dict to collect Gross, Tare, Net values
    current_unit = ""   # Store unit of measurement for each reading

    while True:
        # Read line from serial port with 2-second timeout
        line = ser.readline().decode("utf-8", errors="ignore").strip()
        if line:
            result = parse_weight_line(line)
            if result:
                label, value, unit = result
                weights[label] = value
                current_unit = unit

                # Once all three weights are collected, save them as a new row
                if all(k in weights for k in ("Gross", "Tare", "Net")):
                    net_weight = weights["Net"]

                    new_row = pd.DataFrame([{
                        "Timestamp": datetime.now(),
                        "Gross": weights["Gross"],
                        "Tare": weights["Tare"],
                        "Net": net_weight,
                        "Unit": current_unit
                    }])
                    df = pd.concat([df, new_row], ignore_index=True)
                    print(df.tail(1))

                    # Show deer message on e-paper
                    display_fat_deer_message(net_weight, epd, deer_img)

                    weights.clear()


except KeyboardInterrupt:
    print("\nStopped by user.")

finally:
    ser.close()
    df.to_csv("scale_weights.csv", index=False)
    print("Saved data to scale_weights.csv")
