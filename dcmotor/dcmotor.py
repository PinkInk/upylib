import pyb, pwm

FORWARDS  =  255
BACKWARDS = -FORWARDS
STOP      = 0

#possible dcmotor configurations, depends on skin orientation
Y1 = {'enable':pyb.Pin.board.Y8,'control0':pyb.Pin.board.Y6,'control1':pyb.Pin.board.Y7}
Y2 = {'enable':pyb.Pin.board.Y3,'control0':pyb.Pin.board.Y2,'control1':pyb.Pin.board.Y1}
X1 = {'enable':pyb.Pin.board.X8,'control0':pyb.Pin.board.X6,'control1':pyb.Pin.board.X7}
X2 = {'enable':pyb.Pin.board.X3,'control0':pyb.Pin.board.X2,'control1':pyb.Pin.board.X1}

class DCMOTOR:
  """dirty DC Motor Class"""

  def __init__(self, pins_dict, reverse_pols=False):

    self.__enable   = pins_dict['enable']
    self.__control0 = pins_dict['control0'] if not reverse_pols else pins_dict['control1']
    self.__control1 = pins_dict['control1'] if not reverse_pols else pins_dict['control0']

    self.__pwm = pwm.PWM(self.__enable)
    self.__control0.init(pyb.Pin.OUT_PP)
    self.__control0.low()
    self.__control1.init(pyb.Pin.OUT_PP)
    self.__control1.low()

  def state(self,value=None):
    """get or set motor state as -ve|0|+ve as backwards|stop|forwards"""
    if value == None:
      if self.__pwm.duty() > 0:
        if self.__control0.value() and not self.__control1.value():
          return -self.__pwm.duty()
        elif not self.__control0.value() and self.__control1.value():
          return self.__pwm.duty()
        else:
          raise ValueError('Inconsistent state')
      else:
        return 0
    elif value < 0:
      self.__control0.high()
      self.__control1.low()
      self.__pwm.duty(abs(value))
    elif value > 0:
      self.__control0.low()
      self.__control1.high()
      self.__pwm.duty(value)
    elif value == 0:
      self.__pwm.duty(0)
    else:
      raise ValueError('Invalid state value passed')

  def backwards(self,value=-BACKWARDS):
    self.state(-value)

  def forwards(self,value=FORWARDS):
    self.state(value)

  def stop(self):
    self.state(STOP)

  def emergency_stop(self,brakes_for=50):
    if self.state() != 0:
      self.__control0.value(int(not(self.__control0.value())))
      self.__control1.value(int(not(self.__control1.value())))
      pyb.delay(brakes_for)
      self.stop()
