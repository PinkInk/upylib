import pyb

class CharLCDPlate():

  MCP23017_IOCON_BANK0    = 0x0A
  MCP23017_IOCON_BANK1    = 0x15
  MCP23017_GPIOA          = 0x09
  MCP23017_IODIRB         = 0x10
  MCP23017_GPIOB          = 0x19
  SELECT                  = 0
  RIGHT                   = 1
  DOWN                    = 2
  UP                      = 3
  LEFT                    = 4
  OFF                     = 0x00
  RED                     = 0x01
  GREEN                   = 0x02
  BLUE                    = 0x04
  YELLOW                  = RED + GREEN
  TEAL                    = GREEN + BLUE
  VIOLET                  = RED + BLUE
  WHITE                   = RED + GREEN + BLUE
  ON                      = RED + GREEN + BLUE
  LCD_CLEARDISPLAY        = 0x01
  LCD_RETURNHOME          = 0x02
  LCD_ENTRYMODESET        = 0x04
  LCD_DISPLAYCONTROL      = 0x08
  LCD_CURSORSHIFT         = 0x10
  LCD_FUNCTIONSET         = 0x20
  LCD_SETCGRAMADDR        = 0x40
  LCD_SETDDRAMADDR        = 0x80
  LCD_DISPLAYON           = 0x04
  LCD_DISPLAYOFF          = 0x00
  LCD_CURSORON            = 0x02
  LCD_CURSOROFF           = 0x00
  LCD_BLINKON             = 0x01
  LCD_BLINKOFF            = 0x00
  LCD_ENTRYRIGHT          = 0x00
  LCD_ENTRYLEFT           = 0x02
  LCD_ENTRYSHIFTINCREMENT = 0x01
  LCD_ENTRYSHIFTDECREMENT = 0x00
  LCD_DISPLAYMOVE         = 0x08
  LCD_CURSORMOVE          = 0x00
  LCD_MOVERIGHT           = 0x04
  LCD_MOVELEFT            = 0x00

  def __init__(self, busnum, addr):
      self.i2c = pyb.I2C(busnum,pyb.I2C.MASTER)
      self.address = addr
      self.porta, self.portb, self.ddrb = 0, 0, 0b00010000
      self.i2c.mem_write(0,self.address,self.MCP23017_IOCON_BANK1)
      registers =[ 0b00111111, self.ddrb, 0b00111111, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 
                   0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00111111, 0b00000000, 
                   0b00000000, 0b00000000, 0b00000000, 0b00000000, self.porta, self.portb, self.porta, 
                   self.portb ]
      for register in registers:
        self.i2c.mem_write(0,self.address,register)
      self.i2c.mem_write(0b10100000, self.address, self.MCP23017_IOCON_BANK0)
      self.displayshift   = (self.LCD_CURSORMOVE | self.LCD_MOVERIGHT)
      self.displaymode    = (self.LCD_ENTRYLEFT | self.LCD_ENTRYSHIFTDECREMENT)
      self.displaycontrol = (self.LCD_DISPLAYON | self.LCD_CURSOROFF | self.LCD_BLINKOFF)
      self.write(0x33)
      self.write(0x32)
      self.write(0x28)
      self.write(self.LCD_CLEARDISPLAY)
      self.write(self.LCD_CURSORSHIFT    | self.displayshift)
      self.write(self.LCD_ENTRYMODESET   | self.displaymode)
      self.write(self.LCD_DISPLAYCONTROL | self.displaycontrol)
      self.write(self.LCD_RETURNHOME)

  flip = ( 0b00000000, 0b00010000, 0b00001000, 0b00011000,
           0b00000100, 0b00010100, 0b00001100, 0b00011100,
           0b00000010, 0b00010010, 0b00001010, 0b00011010,
           0b00000110, 0b00010110, 0b00001110, 0b00011110 )

  def out4(self, bitmask, value):
      hi = bitmask | self.flip[value >> 4]
      lo = bitmask | self.flip[value & 0x0F]
      return [hi | 0b00100000, hi, lo | 0b00100000, lo]

  pollables = ( LCD_CLEARDISPLAY, LCD_RETURNHOME )

  def write(self, value, char_mode=False):
    if self.ddrb & 0b00010000:
      lo = (self.portb & 0b00000001) | 0b01000000
      hi = lo | 0b00100000
      self.i2c.mem_write(lo,self.address,self.MCP23017_GPIOB)
      while True:
        self.i2c.send(hi,self.address)
        bits = self.i2c.recv(1,self.address)
        self.i2c.mem_write(bytearray([lo,hi,lo]),self.address,self.MCP23017_GPIOB)
        if (bits[0] & 0b00000010) == 0: break
      self.portb = lo
      self.ddrb &= 0b11101111
      self.i2c.mem_write(self.ddrb,self.address,self.MCP23017_IODIRB)
    bitmask = self.portb & 0b00000001
    if char_mode: bitmask |= 0b10000000
    if isinstance(value, str):
      last = len(value) - 1
      data = []
      for i, v in enumerate(value):
        data.extend(self.out4(bitmask, ord(v)))
        if (len(data) >= 32) or (i == last):
          self.i2c.mem_write(bytearray(data),self.address,self.MCP23017_GPIOB)
          self.portb = data[-1]
          data       = []
    elif isinstance(value, list):
      last = len(value) - 1
      data = []
      for i, v in enumerate(value):
        data.extend(self.out4(bitmask, v))
        if (len(data) >= 32) or (i == last):
          self.i2c.mem_write(data,self.address,self.MCP23017_GPIOB)
          self.portb = data[-1]
          data       = []
    else:
      data = self.out4(bitmask, value)
      self.i2c.mem_write(bytearray(data),self.address,self.MCP23017_GPIOB)
      self.portb = data[-1]
    if (not char_mode) and (value in self.pollables):
      self.ddrb |= 0b00010000
      self.i2c.mem_write(self.ddrb,self.address,self.MCP23017_IODIRB)

  def begin(self, cols, lines):
    self.currline = 0
    self.numlines = lines
    self.clear()

  def clear(self):
    self.write(self.LCD_CLEARDISPLAY)

  def home(self):
    self.write(self.LCD_RETURNHOME)

  row_offsets = ( 0x00, 0x40, 0x14, 0x54 )

  def setCursor(self, col, row):
    if row > self.numlines: row = self.numlines - 1
    elif row < 0:           row = 0
    self.write(self.LCD_SETDDRAMADDR | (col + self.row_offsets[row]))

  def display(self):
    self.displaycontrol |= self.LCD_DISPLAYON
    self.write(self.LCD_DISPLAYCONTROL | self.displaycontrol)

  def noDisplay(self):
    self.displaycontrol &= ~self.LCD_DISPLAYON
    self.write(self.LCD_DISPLAYCONTROL | self.displaycontrol)

  def cursor(self):
    self.displaycontrol |= self.LCD_CURSORON
    self.write(self.LCD_DISPLAYCONTROL | self.displaycontrol)

  def noCursor(self):
    self.displaycontrol &= ~self.LCD_CURSORON
    self.write(self.LCD_DISPLAYCONTROL | self.displaycontrol)

  def ToggleCursor(self):
    self.displaycontrol ^= self.LCD_CURSORON
    self.write(self.LCD_DISPLAYCONTROL | self.displaycontrol)

  def blink(self):
    self.displaycontrol |= self.LCD_BLINKON
    self.write(self.LCD_DISPLAYCONTROL | self.displaycontrol)

  def noBlink(self):
    self.displaycontrol &= ~self.LCD_BLINKON
    self.write(self.LCD_DISPLAYCONTROL | self.displaycontrol)

  def ToggleBlink(self):
    self.displaycontrol ^= self.LCD_BLINKON
    self.write(self.LCD_DISPLAYCONTROL | self.displaycontrol)

  def scrollDisplayLeft(self):
    self.displayshift = self.LCD_DISPLAYMOVE | self.LCD_MOVELEFT
    self.write(self.LCD_CURSORSHIFT | self.displayshift)

  def scrollDisplayRight(self):
    self.displayshift = self.LCD_DISPLAYMOVE | self.LCD_MOVERIGHT
    self.write(self.LCD_CURSORSHIFT | self.displayshift)

  def leftToRight(self):
    self.displaymode |= self.LCD_ENTRYLEFT
    self.write(self.LCD_ENTRYMODESET | self.displaymode)

  def rightToLeft(self):
    self.displaymode &= ~self.LCD_ENTRYLEFT
    self.write(self.LCD_ENTRYMODESET | self.displaymode)

  def autoscroll(self):
    self.displaymode |= self.LCD_ENTRYSHIFTINCREMENT
    self.write(self.LCD_ENTRYMODESET | self.displaymode)

  def noAutoscroll(self):
    self.displaymode &= ~self.LCD_ENTRYSHIFTINCREMENT
    self.write(self.LCD_ENTRYMODESET | self.displaymode)

  def createChar(self, location, bitmap):
    self.write(self.LCD_SETCGRAMADDR | ((location & 7) << 3))
    self.write(bitmap, True)
    self.write(self.LCD_SETDDRAMADDR)

  def message(self, text):
    lines = str(text).split('\n')
    for i, line in enumerate(lines):
      if i > 0:
        self.write(0xC0)
      self.write(line, True)

  def backlight(self, color):
    c          = ~color
    self.porta = (self.porta & 0b00111111) | ((c & 0b011) << 6)
    self.portb = (self.portb & 0b11111110) | ((c & 0b100) >> 2)
    self.i2c.mem_write(self.porta,self.address,self.MCP23017_GPIOA)
    self.i2c.mem_write(self.portb,self.address,self.MCP23017_GPIOB)

  def buttonPressed(self, b):
    return (self.i2c.mem_read(1,self.address,self.MCP23017_GPIOA,timeout=100)[0] >> b) & 1

  def buttons(self):
    return self.i2c.mem_read(1,self.address,self.MCP23017_GPIOA,timeout=100)[0] & 0b11111
