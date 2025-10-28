import serial
from datetime import datetime

ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=1)

try:
    while True:
        line = ser.readline()
        if line:
            decoded = line.decode('utf-8', errors='ignore').strip()
            print(f"{datetime.utcnow()} -> {decoded}")
except KeyboardInterrupt:
    pass
finally:
    ser.close()