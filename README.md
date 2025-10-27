# RS232C_Scale

This repository contains code to program a Raspberry Pi to read data from an electronic scale via an RS232C connection.

## Supported Hardware

- **Electronic scale with RS232C port** – Tested with the [Brecknell PS-1000 Veterinary Floor Scale](https://www.scalesplus.com/brecknell-ps-1000-veterinary-floor-scale-1000-lb-x-0-5-lb/)
- **Raspberry Pi 5 or Raspberry Pi Zero**
- **RS232C Hat** – [Serial Pi Plus for Pi 5](https://www.robotshop.com/products/rs232-serial-pi-plus-converter-raspberry-pi?srsltid=AfmBOoooojX3TRSq1hJXdAEGcPuRIxkYIwap9Js9unGpf-04l6-NioCf) or [Serial Pi Zero](https://thepihut.com/products/serial-pizero) for Pi Zero. [Assembly video for Serial Pi Plus](https://www.youtube.com/watch?v=fvNaVA14km0)
- **RS232C cable**
- **SD card and USB SD card reader** – For saving weight measurements
- **Optional e-paper Hat** – Tested with the 2.13-inch e-Paper Hat from [Waveshare](https://www.waveshare.com/2.13inch-e-paper-hat-plus.htm)

---

## Python Scripts

### log_weights_RPi5.py / log_weights_RPiZero.py

These scripts read weight data automatically from the scale through the RS232C interface.

#### Features

- Connects to the scale via serial port (`/dev/ttyAMA0` by default, adjust if necessary)
- Reads stable weight measurements automatically sent by the scale
- Parses Gross, Tare, and Net weight readings along with units (`lb` or `kg`)
- Saves readings with timestamps to a CSV file (`scale_weights.csv`)
- Prints measurements in real-time to the terminal
- Safely closes the serial connection and saves data on exit (Ctrl+C)

#### Usage

1. Install required Python packages:

   pip install pyserial pandas

2. Connect your scale to the Raspberry Pi via the RS232C Hat and cable

3. Run the appropriate script:

   For Raspberry Pi 5:  
   python log_weights_RPi5.py

   For Raspberry Pi Zero:  
   python log_weights_RPiZero.py

4. The script will continuously wait for stable weight data

5. Press `Ctrl+C` to stop and save the recorded data to `scale_weights.csv`

#### Notes

- Ensure your scale is configured to send stable weight readings automatically through the RS232C port
- Adjust the serial port device path (`/dev/ttyAMA0`) if needed depending on your Raspberry Pi setup



