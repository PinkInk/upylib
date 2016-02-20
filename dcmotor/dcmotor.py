import pyb

#<skin_position><motor>=enable pin, enable pin timer, channel, control0, control1
Y1='Y8', 12, 2, 'Y6', 'Y7'
Y2='Y3', 10, 1, 'Y1', 'Y2'
X1='X8', 14, 1, 'X6', 'X7'
X2='X3', 9, 1, 'X1', 'X2'

class DCMOTOR:
    """dirty DC Motor Class"""

    def __init__(self, params, reverse=False, freq=1000):
        self._enable = pyb.Pin(params[0])
        self._timer = pyb.Timer(params[1], freq=freq)
        self._channel = self._timer.channel(params[2], pyb.Timer.PWM, pin=self._enable)
        self._c0 = pyb.Pin(params[3] if not reverse else params[4], pyb.Pin.OUT_PP)
        self._c0.low()
        self._c1 = pyb.Pin(params[4] if not reverse else params[3], pyb.Pin.OUT_PP)
        self._c0.low()

    def freq(self, val=None):
        """set pwm frequency"""
        if val != None:
            self._timer.freq(val)
        return self._timer.freq()

    def state(self, val=None):
        """set (and/or get) motor state between +ve/-ve 100%"""
        if val != None:
            if val == 0:
                self._channel.pulse_width_percent(0)
            elif 0 < val <= 100:
                self._channel.pulse_width_percent(val)
                self._c0.low()
                self._c1.high()
            elif 0 > val >= -100:
                self._channel.pulse_width_percent(abs(val))
                self._c0.high()
                self._c1.low()
            else:
                raise ValueError('-100<=state<=100 only')
        if self._c1.value() or self._channel.pulse_width_percent() == 0:
            return self._channel.pulse_width_percent()
        else:
            return -self._channel.pulse_width_percent()
