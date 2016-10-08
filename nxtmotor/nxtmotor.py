#Reference
#http://www.brickengineer.com/pages/2008/09/05/lego-nxt-motor-wiring/
#
#                                TI SN 754410 NE
#                                 Quad H-bridge
#                            -----------------------
#                            |1 1,2EN        +ve 16| -> Vin
#                            |2 1A            4A 15| -> Pin Y11
#                            |3 1Y            4Y 14| -> NXT Mtr / Black Wire / Motor Pole 1
# Gnd & -ve Bat via diode <- |4 Gnd          Gnd 13| -> Gnd & -ve Bat via diode
# Gnd & -ve Bat via diode <- |5 Gnd          Gnd 12| -> Gnd & -ve Bat via diode
#                            |6 2Y            3Y 11| -> NXT Mtr / White Wire / Motor Pole 2
#                            |7 2A            3A 10| -> Pin Y10
#        +ve Bat <- diode <- |8 +ve Bat    3,4EN  9| -> Pin Y9
#                            -----------------------
#
# Lego NXT cable termination block
# -------
# |     + -> Black Wire  / Motor Pole 1 -> H-Bridge Pin 14 (Y4)
# |     + -> White Wire  / Motor Pole 2 -> H-Bridge Pin 11 (3Y)
# |     + -> Green Wire  / Power for sensor / pyboard 3.3v Pin
# |     + -> Red Wire    / Gnd for sensro   / to Gnd
# |     + -> Blue Wire   / Rotary Encoder Tack 0 / Pin Y8
# |     + -> Yellow Wire / Rotary Encoder Tack 1 / Pin Y7
# -------
#
# LED
# Pin Y12 -> Led -> Gnd (no current limiting resistor, living dangerous!)

#
# v1 T.Pelling 29/07/14 - first issue
# v2 T.Pelling 30/07/14 - removed confused calibration concept
# v3 T.Pelling 01/08/14 -
import pyb, pwm

#these values relate to pwm range, don't change without changing pwm.py
FORWARDS     = 255
BACKWARDS    = -FORWARDS
STOP         = 0

#led statuses
LED_ON       = 1
LED_OFF      = 0

#speed we want the clock to count at in Hz
TIMER_FREQ   = 1000000

#each tack of the encoder counts 2deg/tick | 180 ticks = 360deg
DEG_PER_TICK = 2

#possible nxt motor shield configurations, depends on skin orientation
Y = { 'enable':   pyb.Pin.board.Y9, \
      'control0': pyb.Pin.board.Y10, \
      'control1': pyb.Pin.board.Y11, \
      'led':      pyb.Pin.board.Y12, \
      'tack0':    pyb.Pin.board.Y8, \
      'tack1':    pyb.Pin.board.Y7 \
    }
X = { 'enable':   pyb.Pin.board.X9, \
      'control0': pyb.Pin.board.X10, \
      'control1': pyb.Pin.board.X11, \
      'led':      pyb.Pin.board.X12, \
      'tack0':    pyb.Pin.board.X8, \
      'tack1':    pyb.Pin.board.X7 \
    }

class NXTMOTOR:
  """dirty NXT Motor class"""

  def __init__(self, pins_dict, timer=6, reverse_pols=False):

    self.__enable = pwm.PWM(pins_dict['enable'])

    self.__control0 = pins_dict['control0'] if not reverse_pols else pins_dict['control1']
    self.__control0.init(pyb.Pin.OUT_PP)
    self.__control0.low()
    self.__control1 = pins_dict['control1'] if not reverse_pols else pins_dict['control0']
    self.__control1.init(pyb.Pin.OUT_PP)
    self.__control1.low()

    self.__led = pins_dict['led']
    self.__led.init(pyb.Pin.OUT_PP)

    self.__tack0 = pins_dict['tack0'] if not reverse_pols else pins_dict['tack1']
    self.__tack1 = pins_dict['tack1'] if not reverse_pols else pins_dict['tack0']
    self.__tack1.init(pyb.Pin.IN)

    #pyb.millis doesn't have enough resolution
    #start timer at TIMER_FREQ, with max possible period
    if timer in [1,8,9,10,11]:
      self.__ucounter   = pyb.Timer(timer, prescaler=int(pyb.freq()[3]/TIMER_FREQ), period=0x7fffffff)
    elif timer in [2,3,4,5,6,7,12,13,14]:
      self.__ucounter   = pyb.Timer(timer, prescaler=int(pyb.freq()[2]/TIMER_FREQ), period=0x7fffffff)
    self.__tim_rollover = False
    #set a callback on the timer which sets __tim_rollover true if it overflows
    #i.e. it counts past it's period, without a tack occuring.
    #if so we assume speed is zero as we can no longer measure it
    self.__ucounter.callback(self.__ISR_TIMER_SPEED)
    self.__pulsetime    = 0  #this is measured speed ... we are at rest
    self.__pulsedir     = 0  #at init doesn't matter what direction this indicates
    #register interrupt on tack0
    self.__extint       = pyb.ExtInt(self.__tack0, pyb.ExtInt.IRQ_RISING, pyb.Pin.PULL_UP, self.__ISR_TACK_SPEED)

  def speed(self):
    if self.__tim_rollover:
      return 0
    else:
      sign = +1 if self.__pulsedir else -1 #account for direction
      return sign * (1 / ((self.__pulsetime/TIMER_FREQ) * (360 / DEG_PER_TICK)))

  @micropython.native
  def __ISR_TIMER_SPEED(self, timer):
    self.__tim_rollover = True

  @micropython.native
  def __ISR_TACK_SPEED(self, line):
    self.__pulsetime = self.__ucounter.counter()
    self.__ucounter.counter(0)
    self.__tim_rollover = False
    self.__pulsedir = self.__tack1.value()

  def drive(self, value=None):
    """get or set motor drive as -ve|0|+ve as backwards|stop|forwards"""
    if value == None:
      if self.__enable.duty() > 0:
        if self.__control0.value() and not self.__control1.value():
          return -self.__enable.duty()
        elif not self.__control0.value() and self.__control1.value():
          return self.__enable.duty()
        else:
          return ValueError('Inconsistent drive state')
      else:
        return 0
    elif value < 0:
      self.__control0.high()
      self.__control1.low()
      self.__enable.duty(abs(value))
    elif value > 0:
      self.__control0.low()
      self.__control1.high()
      self.__enable.duty(abs(value))
    elif value == 0:
      self.__enable.duty(0)
    else:
      raise ValueError('Invalid drive state value')

  def backwards(self, value=-BACKWARDS):
    self.drive(-value)

  def forwards(self, value=FORWARDS):
    self.drive(value)

  def stop(self):
    self.drive(STOP)

  def led(self, value=None):
    if value == None:
      return self.__led.value()
    else:
      self.__led.value(value)


