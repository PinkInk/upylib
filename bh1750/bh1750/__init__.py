# adapted for micropython from 
# https://gist.github.com/oskar456/95c66d564c58361ecf9f

from ustruct import unpack
from utime import sleep


class BH1750():

    PWR_OFF = 0x00
    PWR_ON  = 0x01
    RESET   = 0x07 # reset data register

    # modes
    CONT_LOWRES = 0x13  # continuous 4 lx resln, takes 16ms
    CONT_HIRES_1 = 0x10 # continuous 1 lx resln, takes 120ms
    CONT_HIRES_2 = 0x11 # continuous .5 lx resln, takes 120ms
    ONCE_HIRES_1 = 0x20 # single 1 lx resln and pwr off, takes 120ms
    ONCE_HIRES_2 = 0x21 # single .5 lx resln and pwr off, takes 120ms
    ONCE_LOWRES = 0x23  # single 1 lx resln and pwr off, takes 120ms(?)

    # default addr=0x23 if addr pin floating or pulled to ground
    # addr=0x5c if addr pin pulled high 
    def __init__(self, bus, addr=0x23):
        self.bus = bus
        self.addr = addr
        self._sensitivity = 69
        self.off()
        self.set_sensitivity(self._sensitivity)

    def off(self):
        self.set_mode(self.PWR_OFF)

    def on(self):
        self.set_mode(self.PWR_ON)

    def reset(self):
        self.on() # power on before resetting
        self.set_mode(self.RESET)

    def set_mode(self, mode):
        self.mode = mode
        self.bus.writeto(self.addr, bytes([self.mode]))

    def set_sensitivity(self, sensitivity=69):
        if sensitivity < 31:
            self._sensitivity = 31
        elif sensitivity > 254:
            self._sensitivity = 254
        else:
            self._sensitivity = sensitivity
        self.on()
        self.set_mode(0x40 | (self._sensitivity >> 5))
        self.set_mode(0x60 | (self._sensitivity & 0x1f))
        self.off()

    def _wait_for_reading(self, additional=0):
        basetime = 0.018 if (self.mode & 0x03) == 0x03 else 0.132 # 0.128
        sleep(basetime * (self._sensitivity/69.0) + additional)

    def read(self):
        # Return current mode measurement result in lx.
        # needs to be on and mode set first   
        data = unpack('>H', self.bus.readfrom(self.addr, 2))[0]
        count = data >> 8 | (data&0xff)<<8
        mode2coeff =  2 if (self.mode & 0x03) == 0x01 else 1
        ratio = 1/(1.2 * (self._sensitivity/69.0) * mode2coeff)
        return ratio*count

    def get_measurement(self, mode=ONCE_LOWRES, additional_delay=0):
        self.reset()
        self.set_mode(mode)
        self._wait_for_reading(additional=additional_delay)
        return self.read()
