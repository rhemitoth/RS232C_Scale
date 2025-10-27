# RS232C_Scale

This repository contains code to program a Raspberry Pi to read data from an electronic scale via an RS232C connection.

## Raspberry-Pi 5 Configuration

### Materials

- **Electronic scale with an RS232C Port:** This repository was developed using the [Brecknell PS-1000 Veterinary Floor Scale](https://www.scalesplus.com/brecknell-ps-1000-veterinary-floor-scale-1000-lb-x-0-5-lb/)
- **Raspberry Pi 5**
- **RS232C Hat:** This repository was developed using the [Serial Pi Plus](https://www.robotshop.com/products/rs232-serial-pi-plus-converter-raspberry-pi?srsltid=AfmBOoooojX3TRSq1hJXdAEGcPuRIxkYIwap9Js9unGpf-04l6-NioCf). An assembly video for the Serial Pi Plus can be found [here](https://www.youtube.com/watch?v=fvNaVA14km0)
- **RS232C Cable**
- **SD Card and USB SD Card Reader:** For saving weight measurements.
- **e-paper Hat*:* This repository was developed using the 2.13 inch e-Paper hat from [Waveshare](https://www.waveshare.com/2.13inch-e-paper-hat-plus.htm)

### log_weights_RPi5.py

`log_weights_RPi5.py` is the main script for reading weight data automatically from the scale through the RS232C interface.

#### Features

- Connects to the scale via serial port (`/dev/ttyAMA0` by default, adjust if necessary).
- Listens for stable weight measurements automatically sent by the scale without needing manual button presses.
- Parses Gross, Tare, and Net weight readings along with their units (`lb` or `kg`).
- Saves each complete set of readings with timestamps into a CSV file (`scale_weights.csv`).
- Prints each captured measurement to the terminal for real-time feedback.
- Cleanly closes the serial connection and saves data when stopped (e.g., by pressing Ctrl+C).

#### Usage

1. Ensure required Python packages are installed:

   pip install pyserial pandas

2. Connect your scale to the Raspberry Pi via the Serial Pi Plus HAT and RS232C cable.

3. Run the script:

   python log_weights.py

4. The script will continuously wait for stable weight data sent automatically by the scale.

5. To stop the script and save data, press `Ctrl+C`. The recorded data will be saved to `scale_weights.csv` in the script’s directory.

#### Notes

- Make sure your scale is configured to send stable weight readings automatically through the RS232C port.
- You may need to adjust the serial port device path (`/dev/ttyAMA0`) in the script depending on your Raspberry Pi setup.

## Raspberry Pi Zero Configuration

### Materials

- **Electronic scale with an RS232C Port:** This repository was developed using the [Brecknell PS-1000 Veterinary Floor Scale](https://www.scalesplus.com/brecknell-ps-1000-veterinary-floor-scale-1000-lb-x-0-5-lb/)
- **Raspberry Pi Zero**
- **RS232C Hat:** This repository was developed using the [Serial Pi Zero](https://thepihut.com/products/serial-pizero). An assembly video for the Serial Pi Plus can be found [here](https://www.youtube.com/watch?v=fvNaVA14km0)
- **RS232C Cable**
- **SD Card and USB SD Card Reader:** For saving weight measurements.


