"""
Driver for the MPR121 capacitive touch sensor.
This chip is on the LCD32MKv1 skin.
"""

import pyb

# register definitions
TOUCH_STATUS = const(0x00)
ELE0_FILT_DATA = const(0x04)
ELE0_TOUCH_THRESH = const(0x41)
DEBOUNCE = const(0x5b)
ELEC_CONFIG = const(0x5e)

class MPR121:
    def __init__(self, i2c):
        self.i2c = i2c
        self.addr = 90 # I2C address of the MPR121

        # enable ELE0 - ELE3
        self.enable_elec(4)

    def enable_elec(self, n):
        """Enable the first n electrodes."""
        self.i2c.mem_write(n & 0xf, self.addr, ELEC_CONFIG)

    def threshold(self, elec, touch, release):
        """
        Set touch/release threshold for an electrode.
        Eg threshold(0, 12, 6).
        """
        buf = bytearray((touch, release))
        self.i2c.mem_write(buf, self.addr, ELE0_TOUCH_THRESH + 2 * elec)

    def debounce(self, touch, release):
        """
        Set touch/release debounce count for all electrodes.
        Eg debounce(3, 3).
        """
        self.i2c.mem_write((touch & 7) | (release & 7) << 4, self.addr, DEBOUNCE)

    def touch_status(self, elec=None):
        """Get the touch status of an electrode (or all electrodes)."""
        status = self.i2c.mem_read(2, self.addr, TOUCH_STATUS)
        status = status[0] | status[1] << 8
        if elec is None:
            return status
        else:
            return status & (1 << elec) != 0

    def elec_voltage(self, elec):
        """Get the voltage on an electrode."""
        data = self.i2c.mem_read(2, self.addr, ELE0_FILT_DATA + 2 * elec)
        return data[0] | data[1] << 8

