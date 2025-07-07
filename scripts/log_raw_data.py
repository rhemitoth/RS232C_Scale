import serial
from datetime import datetime

ser = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=1)

with open("raw_scale_data.log", "w") as f:
    print("Logging raw serial data from scale. Press Ctrl+C to stop.")
    try:
        while True:
            line = ser.readline()
            if line:
                timestamp = datetime.now().isoformat()
                decoded_line = line.decode("utf-8", errors="ignore").strip()
                log_line = f"{timestamp} | {decoded_line}"
                print(log_line)
                f.write(log_line + "\n")
    except KeyboardInterrupt:
        print("Logging stopped.")
    finally:
        ser.close()
