import serial

# Try with the likely serial device
ser = serial.Serial('/dev/ttyAMA0', baudrate=9600, timeout=1)

try:
    while True:
        if ser.in_waiting:
            data = ser.readline().decode('utf-8', errors='replace').strip()
            print(f"Received: {data}")
except KeyboardInterrupt:
    print("Stopping...")
finally:
    ser.close()
