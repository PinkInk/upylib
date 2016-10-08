import pyb

#motor/orientation tuple index
_ENABLE_PIN = 0
_ENABLE_TIMER = 1
_ENABLE_TCHANNEL = 2
_CONTROL_0 = 3
_CONTROL_1 = 4

#motor 1 & 2 configs for skin orientation
Y1 = "Y8", 12, 2, "Y6", "Y7"
Y2 = "Y3", 10, 1, "Y1", "Y2"
X1 = "X8", 14, 1, "X6", "X7"
X2 = "X3", 9, 1, "X1", "X2"

class DCMOTOR:
    """dirty DC Motor Class"""

    def __init__(self, params, reverse=False, freq=1000):
        if params not in [X1, X2, Y2, Y3]:
            raise ValueError("invalid parameters")
        self._enable = pyb.Pin(params[_ENABLE_PIN])
        self._timer = pyb.Timer(params[_ENABLE_TIMER], freq=freq)
        self._channel = self._timer.channel(
            params[_ENABLE_TIMER],
            pyb.Timer.PWM,
            pin=self._enable
        )
        self._c0 = pyb.Pin(params[_CONTROL_0]
            if not reverse else params[_CONTROL_1], pyb.Pin.OUT_PP)
        self._c0.low()
        self._c1 = pyb.Pin(params[_CONTROL_1]
            if not reverse else params[_CONTROL_0], pyb.Pin.OUT_PP)
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
                raise ValueError("Outside allowed range (-100% - 100%)")
        if self._c1.value() or self._channel.pulse_width_percent() == 0:
            return self._channel.pulse_width_percent()
        else:
            return -self._channel.pulse_width_percent()
