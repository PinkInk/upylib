import pyb, pwm

FORWARDS  =  255
BACKWARDS = -FORWARDS
STOP      = 0

#possible dcmotor configurations, depends on skin orientation
Y1 = {'enable_pin':pyb.Pin.board.Y8, 'enable_timer':12, 'enable_channel':2, 'control0':pyb.Pin.board.Y6,'control1':pyb.Pin.board.Y7}
Y2 = {'enable_pin':pyb.Pin.board.Y3, 'enable_timer':10, 'enable_channel':1, 'control0':pyb.Pin.board.Y2,'control1':pyb.Pin.board.Y1}
X1 = {'enable_pin':pyb.Pin.board.X8, 'enable_timer':14, 'enable_channel':1, 'control0':pyb.Pin.board.X6,'control1':pyb.Pin.board.X7}
X2 = {'enable_pin':pyb.Pin.board.X3, 'enable_timer':9,  'enable_channel':1, 'control0':pyb.Pin.board.X2,'control1':pyb.Pin.board.X1}

class DCMOTOR:
	"""dirty DC Motor Class"""

	def __init__(self, pins_dict, reverse_pols=False, pwm_freq=100):

		self._enable_pin     = pins_dict['enable_pin']
		self._enable_timer   = pins_dict['enable_timer']
		self._enable_channel = pins_dict['enable_channel']
		self._pwm_freq       = pwm_freq
		self._control0       = pins_dict['control0'] if not reverse_pols else pins_dict['control1']
		self._control1       = pins_dict['control1'] if not reverse_pols else pins_dict['control0']

		self._timer          = pyb.Timer(self._enable_timer, freq=self._pwm_freq)
		self._timer_channel  = self._timer.channel(self._enable_channel, pyb.Timer, pin=self._enable_pin, pulse_width=0)
		self._control0.init(pyb.Pin.OUT_PP)
		self._control0.low()
		self._control1.init(pyb.Pin.OUT_PP)
		self._control1.low()

	def state(self,value=None):
		"""get or set motor state as -ve|0|+ve as backwards|stop|forwards"""
		if value == None:
			if self._pwm.duty() > 0:
				if self._control0.value() and not self._control1.value():
					return -self._pwm.duty()
				elif not self._control0.value() and self._control1.value():
					return self._pwm.duty()
				else:
					raise ValueError('Inconsistent state')
				else:
					return 0
			elif value < 0:
				self._control0.high()
				self._control1.low()
				self._pwm.duty(abs(value))
			elif value > 0:
				self._control0.low()
				self._control1.high()
				self._pwm.duty(value)
			elif value == 0:
				self._pwm.duty(0)
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
			self._control0.value(int(not(self._control0.value())))
			self._control1.value(int(not(self._control1.value())))
			pyb.delay(brakes_for)
			self.stop()
