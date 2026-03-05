import time
import struct
from smbus2 import SMBus


class BME280_Driver:
    def __init__(self, bus_id=1, addr=0x76):
        self.bus = SMBus(bus_id)
        self.addr = addr
        self.cal_T = [] # Store calibration constants
        self.load_calibration()

    def load_calibration(self):
        # Read 6 bytes starting at 0x88 (T1, T2, T3)
        d = self.bus.read_i2c_block_data(self.addr, 0x88, 6)
        # Unpack: T1 is <H (unsigned short), T2/T3 are <h (signed short)
        self.cal_T = struct.unpack("<Hhh", bytes(d))
        print(f"Calibration Loaded: T1={self.cal_T[0]}, T2={self.cal_T[1]}, T3={self.cal_T[2]}")

    def read_raw_temp(self):
        # Force a measurement
        self.bus.write_byte_data(self.addr, 0xF4, 0x21)
        time.sleep(0.05)
        # Read 3 bytes from 0xFA
        d = self.bus.read_i2c_block_data(self.addr, 0xFA, 3)
        return (d[0] << 12) | (d[1] << 4) | (d[2] >> 4)

    def compensate_temp(self, adc_T):
        # The specific Bosch datasheet formula (Integer math version)
        v1 = (adc_T / 16384.0 - self.cal_T[0] / 1024.0) * self.cal_T[1]
        v2 = ((adc_T / 131072.0 - self.cal_T[0] / 8192.0) * (adc_T / 131072.0 - self.cal_T[0] / 8192.0)) * self.cal_T[2]
        t_fine = v1 + v2
        return t_fine / 5120.0

# --- Running the Driver ---
sensor = BME280_Driver()
try:
    while True:
        raw = sensor.read_raw_temp()
        temp = sensor.compensate_temp(raw)
        print(f"Accurate Temp: {temp:.2f} °C")
        time.sleep(1)
except KeyboardInterrupt:
    print("Driver Terminated.")