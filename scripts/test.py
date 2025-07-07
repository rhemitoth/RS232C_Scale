import serial

# Adjust baudrate if necessary
ser = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=2)

try:
    print("Waiting for scale data. Press 'Hold/Print' on the scale...")
    while True:
        line = ser.readline().decode("utf-8", errors="ignore").strip()
        if line:
            print("Weight:", line)
except KeyboardInterrupt:
    print("\nStopped.")
finally:
    ser.close()
