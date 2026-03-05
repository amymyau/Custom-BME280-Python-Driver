
# Custom-BME280-Python-Driver

This project features a lightweight, custom Python driver designed to interface a Raspberry Pi 4 with the BME280 environmental sensor via the I2C bus.

# Project Highlights

Low-Level I2C Communication: Built using the smbus2 library to handle raw data transfer between the Broadcom BCM2711 SoC and the sensor.

Hardware Abstraction: Implements a read_temp_driver() function that encapsulates the complexity of opening the I2C bus (/dev/i2c-1), sampling raw data, and handling device resources using Python context managers (with SMBus...).

Linux Permission Management: Optimized for secure execution by utilizing the Linux i2c user group, allowing for hardware interaction without requiring root/sudo privileges.

How it Works
I2C Initialization: The driver targets device address 0x76 (or 0x77) on bus 1.

Calibration: It retrieves factory-set calibration parameters from the BME280's non-volatile memory to ensure high-precision readings.

Data Processing: Raw digital signals for temperature, pressure, and humidity are read from the sensor registers and converted into human-readable metric units.


# Installation & Usage

```bash
1. Enable I2C
Open the Raspberry Pi configuration tool to enable the I2C interface:
sudo raspi-config
# Navigate to: Interface Options -> I2C -> Enable

2. Set Permissions
Allow the current user to access the I2C hardware without needing sudo every time:
sudo usermod -aG i2c $USER
newgrp i2c

3. Install Dependencies
pip install smbus2

4. Run the Driver
Execute the hardware script to begin reading temperature, pressure, and humidity:
python3 I2C_BME280/hardware.py

Note: If you see temperature readings near 1°C on a warm day, ensure you have pulled the latest version. The driver now includes the mandatory factory calibration coefficient logic (BME280 Datasheet Section 4.2).

```

# Known Issues & Fixes

linux group permission error:
Python script is trying to talk to the I2C hardware at /dev/i2c-1, but by default, Ubuntu only allows the root user (or members of the i2c group) to touch that file.
give the user account permission to use the I2C bus permanently
Add your user to the group:
sudo usermod -aG i2c $USER 

Encountered inaccurate environmental data during the integration of a BME280 sensor, where the temperature output was consistently near-freezing (1.1°C) despite ambient room conditions
Refactored the sensor driver to correctly read the factory calibration parameters upon initialization

