import serial
import re
import pandas as pd
from datetime import datetime

ser = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=2)

def parse_weight_line(line):
    match = re.search(r"(Gross|Tare|Net):\s*([\d\.]+)(lb|kg)?", line)
    if match:
        label = match.group(1)
        value = float(match.group(2))
        unit = match.group(3) if match.group(3) else ""
        return label, value, unit
    return None

df = pd.DataFrame(columns=["Timestamp", "Gross", "Tare", "Net", "Unit"])

try:
    print("Waiting for scale data. Press 'Hold/Print' on the scale...")
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
                    new_row = pd.DataFrame([{
                        "Timestamp": datetime.now(),
                        "Gross": weights["Gross"],
                        "Tare": weights["Tare"],
                        "Net": weights["Net"],
                        "Unit": current_unit
                    }])
                    df = pd.concat([df, new_row], ignore_index=True)
                    print(df.tail(1))
                    weights.clear()
except KeyboardInterrupt:
    print("\nStopped.")
finally:
    ser.close()
    df.to_csv("scale_weights.csv", index=False)
    print("Saved data to scale_weights.csv")
