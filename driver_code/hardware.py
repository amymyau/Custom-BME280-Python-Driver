import time
import struct
from smbus2 import SMBus


class BME280_Driver:
    def __init__(self, bus_id=1, addr=0x76):
        self.bus = SMBus(bus_id)
        self.addr = addr
        self.cal_T = []
        self.cal_P = []
        self.cal_H = []
        self.t_fine = 0.0  # Used to carry temperature data to pressure/humidity calcs
        self.load_calibration()

    def load_calibration(self):
        # Temperature: 6 bytes from 0x88
        d = self.bus.read_i2c_block_data(self.addr, 0x88, 6)
        self.cal_T = struct.unpack("<Hhh", bytes(d))

        # Pressure: 18 bytes from 0x8E
        d = self.bus.read_i2c_block_data(self.addr, 0x8E, 18)
        self.cal_P = struct.unpack("<Hhhhhhhhh", bytes(d))

        # Humidity: Fragmented registers (0xA1, 0xE1-0xE7)
        h1 = self.bus.read_byte_data(self.addr, 0xA1)
        d = self.bus.read_i2c_block_data(self.addr, 0xE1, 7)
        h2 = struct.unpack("<h", bytes(d[0:2]))[0]
        h3 = d[2]
        h4 = (d[3] << 4) | (d[4] & 0x0F)
        h5 = (d[5] << 4) | (d[4] >> 4)
        h6 = struct.unpack("<b", bytes([d[6]]))[0]
        self.cal_H = [h1, h2, h3, h4, h5, h6]

    def set_power_mode(self, mode="forced"):
        """
        Manages power consumption.
        'forced' mode takes one measurement and returns to sleep.
        """
        # Config: Humidity oversampling x1 (0x01)
        self.bus.write_byte_data(self.addr, 0xF2, 0x01)
        # Control: Pressure x1, Temp x1, Forced Mode (0x25)
        # Binary: 001 (P) 001 (T) 01 (Forced) = 0x25
        self.bus.write_byte_data(self.addr, 0xF4, 0x25)

    def read_raw_data(self):
        self.set_power_mode()  # Trigger measurement
        time.sleep(0.05)  # Wait for conversion
        # Read all data in one burst (0xF7 to 0xFE: Press, Temp, Hum)
        return self.bus.read_i2c_block_data(self.addr, 0xF7, 8)

    def compensate_temp(self, adc_T):
        v1 = (adc_T / 16384.0 - self.cal_T[0] / 1024.0) * self.cal_T[1]
        v2 = ((adc_T / 131072.0 - self.cal_T[0] / 8192.0) ** 2) * self.cal_T[2]
        self.t_fine = v1 + v2
        return self.t_fine / 5120.0

    def compensate_pressure(self, adc_P):
        v1 = (self.t_fine / 2.0) - 64000.0
        v2 = v1 * v1 * self.cal_P[5] / 32768.0
        v2 = v2 + v1 * self.cal_P[4] * 2.0
        v2 = (v2 / 4.0) + (self.cal_P[3] * 65536.0)
        v1 = (self.cal_P[2] * v1 * v1 / 524288.0 + self.cal_P[1] * v1) / 524288.0
        v1 = (1.0 + v1 / 32768.0) * self.cal_P[0]

        if v1 == 0: return 0

        p = 1048576.0 - adc_P
        p = ((p - (v2 / 4096.0)) * 6250.0) / v1
        v1 = self.cal_P[8] * p * p / 2147483648.0
        v2 = p * self.cal_P[7] / 32768.0
        p = p + (v1 + v2 + self.cal_P[6]) / 16.0
        return p / 100.0  # Return in hPa

    def compensate_humidity(self, adc_H):
        h = self.t_fine - 76800.0
        h = (adc_H - (self.cal_H[3] * 64.0 + self.cal_H[4] / 16384.0 * h)) * \
            (self.cal_H[1] / 65536.0 * (1.0 + self.cal_H[5] / 67108864.0 * h * \
                                        (1.0 + self.cal_H[2] / 67108864.0 * h)))
        h = h * (1.0 - self.cal_H[0] * h / 524288.0)
        return max(0, min(100, h))  # Clamp between 0-100%


# --- Running the Driver ---
sensor = BME280_Driver()
print("BME280 Initialized. Mode: Forced (Low Power)")
---
try:
    while True:
        data = sensor.read_raw_data()

        # Split burst read into raw components
        raw_press = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        raw_temp = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
        raw_hum = (data[6] << 8) | data[7]

        # Calculate compensated values
        temp = sensor.compensate_temp(raw_temp)
        press = sensor.compensate_pressure(raw_press)
        hum = sensor.compensate_humidity(raw_hum)

        print(f"Temp: {temp:.2f}°C | Pressure: {press:.2f}hPa | Humidity: {hum:.1f}%")
        print(f"Status: Sensor entering Sleep Mode to save power...")

        time.sleep(2)
except KeyboardInterrupt:
    print("\nDriver Terminated.")