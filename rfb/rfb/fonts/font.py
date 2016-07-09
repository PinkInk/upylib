from rfb.utils import *

class Font:
    w = 0
    h = 0
    bitmaps = b''

    def count(self):
        # required by WiPy, which doesn't support floats, but
        # will return erroneous result on fonts whose bitmap
        # is not a multiple of 8 bits
        # TODO: fix ... 
        # return int(len(self.bitmaps) // ((self.w*self.h)/8))
        return int(len(self.bitmaps) // ((self.w*self.h)//8))

    def getbitmap_bytes(self, c):
        c -= 32 # start at ascii 32(' ')
        if 0 <= c <= self.count():
            startbyte, startbit = divmod(c*self.w*self.h, 8)
            stopbyte, stopbit = divmod((c*self.w*self.h)+(self.w*self.h), 8)
            if stopbit > 0:
                stopbyte += 1
            b = bytearray(self.bitmaps[startbyte:stopbyte])
            b[0] = b[0] & (0xff>>startbit) # clean leading bits
            # bit-shift out 8-stopbits
            if stopbit > 0:
                for i in range(len(b)):
                    b[len(b)-i] = b[len(b)-i]>>8-stopbit
                    if i < len(b)-1:
                        b[len(b)-i] = b[len(b)-i] | ( b[len(b)-i-1] & (0xff>>stopbit) ) 
            return bytes(b)
        else:
            raise ValueError('bad bitmap code', c)
    
    def getbitmap_str(self, c):
        bits = bin( bytes_to_int(self.getbitmap_bytes(c)) )[2:]
        return (((self.w*self.h)-len(bits))*'0') + bits
