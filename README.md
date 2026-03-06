
## 🚀 Recent Enhancements

I have upgraded the BME280 driver from a basic temperature-only script to a full-featured environmental monitoring tool. 

### 🛠 Key Improvements
* **Full Sensor Support**: Added compensation logic for **Humidity** (%) and **Barometric Pressure** (hPa).
* **Power Optimization (Forced Mode)**: Configured the sensor to use "Forced Mode." The chip now triggers a measurement, delivers data, and immediately enters **Sleep Mode (~0.1 µA consumption)** between reads, making it ideal for battery-powered Raspberry Pi projects.
* **Data Integrity (Burst Reads)**: Implemented an 8-byte burst read across the I2C bus. This ensures that Temperature, Pressure, and Humidity values are captured at the exact same millisecond to prevent "data skew."
* **Refined Calibration**: Integrated all 18 internal factory-trimmed calibration registers ($P_1$-$P_9$ and $H_1$-$H_6$) for high-precision output.

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
pip install -r requirements.txt

4. Run the Driver
Execute the hardware script to begin reading temperature, pressure, and humidity:
python3 I2C_BME280/hardware.py

Note: If you see temperature readings near 1°C on a warm day, ensure you have pulled the latest version. The driver now includes the mandatory factory calibration coefficient logic (BME280 Datasheet Section 4.2).

```

# Technical Decision

Hardware Integration & Safety SummaryThe Issue: 

The BME280 breakout board is marketed as a "5V part" because it includes an XC6206 (662K) LDO regulator and MOSFET-based logic level shifters. While this allows it to work with 5V microcontrollers, the Raspberry Pi's GPIO pins are strictly 3.3V tolerant.

The Risk: Powering the module with 5V causes the onboard level shifters to pull the I2C bus (SDA/SCL) toward 5V. Over time, this "over-voltage" on the Pi’s processor pins can lead to hardware degradation or immediate failure.

The Solution: * Moved the $V_{IN}$ connection from the Pi's 5V rail to the 3.3V rail.Result: Since the BME280 chip operates down to 1.71V, the small voltage drop across the 662K regulator still leaves plenty of overhead for the sensor to function perfectly, while ensuring the I2C logic levels never exceed the Pi's 3.3V limit.

# Known Issues & Fixes

linux group permission error:
Python script is trying to talk to the I2C hardware at /dev/i2c-1, but by default, Ubuntu only allows the root user (or members of the i2c group) to touch that file.
give the user account permission to use the I2C bus permanently
Add your user to the group:
sudo usermod -aG i2c $USER 

Encountered inaccurate environmental data during the integration of a BME280 sensor, where the temperature output was consistently near-freezing (1.1°C) despite ambient room conditions
Refactored the sensor driver to correctly read the factory calibration parameters upon initialization

# Safe Wiring Guide

### ## How to Connect to Raspberry Pi (Safe 3.3V Method)

Since the Raspberry Pi GPIO pins are **not 5V tolerant**, this project uses the 3.3V rail. This ensures that the I2C logic levels remain at a safe 3.3V, bypassing any risk from the 5V-to-3.3V level shifting circuitry.

| BME280 Pin | Raspberry Pi Pin | Function |
| :--- | :--- | :--- |
| **VIN** | **Pin 1** | 3.3V Power |
| **GND** | **Pin 9** | Ground |
| **SCL** | **Pin 5** | I2C Clock (SCL) |
| **SDA** | **Pin 3** | I2C Data (SDA) |


> **Why Pin 1 instead of Pin 2?** > While the breakout board includes a **662K (3.3V LDO)** regulator that *can* handle 5V, using **Pin 1 (3.3V)** ensures that the onboard pull-up resistors reference a 3.3V source. This prevents 5V logic "leakage" into the Pi's SDA/SCL lines, protecting the Pi's processor from long-term damage.

# Technical Specifications (BME280)

The BME280 is a combined digital humidity, pressure, and temperature sensor. This driver implements the factory-trimming compensation logic required for high-accuracy readings.

### Technical Specifications

| Parameter | Range | Accuracy |
| :--- | :--- | :--- |
| **Temperature** | -40°C to +85°C | ±1.0°C |
| **Humidity** | 0% to 100% RH | ±3% RH |
| **Pressure** | 300 hPa to 1100 hPa | ±1.0 hPa |
| **I2C Address** | 0x76 (default) or 0x77 | N/A |
| **Supply Voltage** | 1.71V to 3.6V (Chip) | N/A |
