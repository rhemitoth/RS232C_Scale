# RS232C_Scale

This repository contains code to program a Raspberry Pi to read data from an electronic scale via an RS232C connection.

## Supported Hardware

- **Electronic scale with RS232C port** – Tested with the [Brecknell PS-1000 Veterinary Floor Scale](https://www.scalesplus.com/brecknell-ps-1000-veterinary-floor-scale-1000-lb-x-0-5-lb/)
- **Raspberry Pi 5 or Raspberry Pi Zero**
- **RS232C Hat** – [Serial Pi Plus for Pi 5](https://www.robotshop.com/products/rs232-serial-pi-plus-converter-raspberry-pi?srsltid=AfmBOoooojX3TRSq1hJXdAEGcPuRIxkYIwap9Js9unGpf-04l6-NioCf) or [Serial Pi Zero](https://thepihut.com/products/serial-pizero) for Pi Zero. [Assembly video for Serial Pi Plus](https://www.youtube.com/watch?v=fvNaVA14km0)
- **RS232C cable**
- **SD card and USB SD card reader** – For saving weight measurements
- **Optional e-paper Hat** – Tested with the 2.13-inch e-Paper Hat from [Waveshare](https://www.waveshare.com/2.13inch-e-paper-hat-plus.htm)
- **Optional RTC Module** - If the system is not going to be connected to WiFi during deployment, you should configure your Raspberry Pi to use a Real Time Clock. [This tutorial](https://pimylifeup.com/raspberry-pi-rtc/) describes how to set one up.
---

## Serial Port Setup

This project communicates with the RS232 scale through the Raspberry Pi’s UART interface, which is exposed on the GPIO header and used by the Serial Pi HAT. You must enable the UART (serial port) before the scale can be read.

### 1. Enable UART 

1. Open the Raspberry Pi configuration tool:

   ```bash
   sudo raspi-config
   ```

2. Navigate to:

   ```
   Interface Options → Serial Port
   ```

3. When prompted:
   - "Would you like a login shell to be accessible over serial?" → **No**
   - "Would you like the serial port hardware to be enabled?" → **Yes**

4. Exit the tool and reboot:

   ```bash
   sudo reboot
   ```

---

### 2. Determine the Serial Port Device

After rebooting, check for available serial devices:

   ```bash
   ls /dev/serial*
   ```

On most Raspberry Pi Zero systems, you’ll see:

   ```bash
   /dev/serial0
   ```

`/dev/serial0` is a symbolic link to the active UART (on Pi Zero, this is usually `/dev/ttyS0` or `/dev/ttyAMA0`, depending on model and configuration). Using `/dev/serial0` ensures your code works across Raspberry Pi models.

---

### 3. Configure the Serial Port in Your Script

Recommended for Raspberry Pi Zero (and most models):

   ```python
   import serial
   ser = serial.Serial("/dev/serial0", baudrate=9600, timeout=2)
   ```

If your setup requires direct access to the main UART device (for example, on a Pi 5 with Serial Pi Plus), you can use:

   ```python
   ser = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=2)
   ```

---

## Python Virtual Environment Setup

To keep dependencies organized and avoid conflicts, it is recommended to use a Python virtual environment for this project. This setup works on both Raspberry Pi 5 and Raspberry Pi Zero.

### 1. Create the environment

python3 -m venv ~/scale

This will create a virtual environment called `scale` in your home directory.

### 2. Activate the environment

 log
Your shell prompt will indicate that `scale` is active.

### 3. Upgrade pip

pip install --upgrade pip

### 4. Install required packages

pip install pyserial pandas

> Note: Packages like `re`, `datetime`, `random`, `os`, and `time` are part of the Python standard library and do not require installation.

### 5. Verify the environment

python -c "import serial, re, pandas, datetime, random, os, time; print('All imports work!')"

If you see `All imports work!`, the environment is correctly set up.

### 6. Using the environment

- Activate the environment whenever you work on this project:

source ~/scale/bin/activate

- Deactivate it when done:

deactivate

-- 

## Python Scripts

### log_weights_RPi5.py / log_weights_RPiZero.py

These scripts read weight data automatically from the scale through the RS232C interface.

### Features

- Connects to the scale via serial port (`/dev/ttyAMA0` by default; adjust if needed)
- Reads stable weight measurements automatically sent by the scale
- Parses Gross, Tare, and Net weight readings along with units (`lb` or `kg`)
- Saves readings with timestamps to a CSV file (`scale_weights.csv`) on the SD card or connected USB drive
- Prints measurements to the terminal in real-time
- On Raspberry Pi 5 with e-paper HAT:
  - Displays weight messages 
  - Displays waiting or warning messages if no USB/SD is detected
- Safely closes serial connection and puts e-paper HAT to sleep on exit (Ctrl+C)

### Usage

1. Connect your scale to the Raspberry Pi via the RS232C Hat and cable.

2. Run the appropriate script:

   For Raspberry Pi 5:
   python log_weights_RPi5.py

   For Raspberry Pi Zero:
   python log_weights_RPiZero.py

3. The script will continuously wait for stable weight data.

4. Weight measurements are logged immediately to `scale_weights.csv` as stable measurements are recorded.

5. Press Ctrl+C to stop the script.



#### Notes

- Ensure your scale is configured to send stable weight readings automatically through the RS232C port
- Adjust the serial port device path (`/dev/ttyAMA0`) if needed depending on your Raspberry Pi setup

## Setting up `scale_logger.service` on the Raspberry Pi

The `scale_logger.service` file allows your Raspberry Pi to automatically start the RS232 Scale Data Logger on boot and manage it as a background system service.

### 1. Move the service file to the correct system directory
From your project folder (for example, `scripts/utils`), copy the service file to the systemd directory:

```
sudo cp scripts/utils/scale_logger.service /etc/systemd/system/
```

### 2. Reload systemd to register the new service
```
sudo systemctl daemon-reload
```

### 3. Enable the service to start automatically on boot
```
sudo systemctl enable scale_logger.service
```

### 4. Start or stop the service manually
```
sudo systemctl start scale_logger.service
sudo systemctl stop scale_logger.service
```

### 5. Check the service status or logs
```
sudo systemctl status scale_logger.service
```

Log outputs are saved to:
- **Standard output:** `/home/moorcroftlab/log_output.txt`
- **Error output:** `/home/moorcroftlab/log_error.txt`

---

### Notes
- Before installing, update any hard-coded paths in `scale_logger.service` to match your username and directory structure.  
  For example, if your username is `pi`, replace `/home/moorcroftlab/` with `/home/pi/`.
- Ensure the working directory path points to your local clone of the project:
  ```
  /home/<your-username>/Documents/RS232C_Scale/scripts
  ```
- The service runs as **root** and automatically starts 5 seconds after boot (`ExecStartPre=/bin/sleep 5`).
- After editing the service file, reload and restart it:
  ```
  sudo systemctl daemon-reload
  sudo systemctl restart scale_logger.service
  ```




