try:
    from uarray import array
except:
    from array import array

try:
    LOOP = const(8)
    POLYNOMIAL_ARRAY_SIZE = const(8)
    UZ_ARRAY_SIZE = const(8)
except:
    LOOP = 8
    POLYNOMIAL_ARRAY_SIZE = 8
    UZ_ARRAY_SIZE = 8

characteristic_polynomial = b"100000000008101840085118000000001" 
xsadd_jump_base_step = b"1FA2A1CF67B5FB863"

class F2_POLYNOMIAL_T:
    def __init__(self):
        self.ar = array("L", [0] * POLYNOMIAL_ARRAY_SIZE)

f2_polynomial = F2_POLYNOMIAL_T

class UZ_T:
    def __init__(self):
        self.ar = array("H", [0] * UZ_ARRAY_SIZE)

uz = UZ_T

class xsadd:

    sh1 = 15
    sh2 = 18
    sh3 = 11

    def __init__(self, seed):
        self.state = array("L", [0] * 4)
        self.state[0] = seed
        self.state[1] = 0
        self.state[2] = 0
        self.state[3] = 0
        for i in range(1, LOOP):
            self.state[i&3] ^= i + 1812433253 \
                               * ( \
                                    self.state[(i-1)&3] \
                                    ^ (self.state[(i-1)&3]>>30) \
                               )
        self.period_certification()
        for i in range(LOOP):
            self.next_state()
    
    def jump(self, mul_step, base_step):
        # returns a bytes(200)
        jump_str = self.calculate_jump_polynomial(mul_step, base_step)
        self.jump_by_polynomial(self, jump_str)
    
    @staticmethod
    def calculate_jump_poplynomial(mul_step, base_step):
        jump_str = bytes(200)
        jump_poly = f2_poplynomial()
        characteristic = f2_polynomial()
        tee = f2_polynomial()
        base = uz()
        mul = uz()
        step = uz()
        self.strtopolynomial( characteristic, characteristic_polynomial )
        self.clear( tee ) # not necessar python inits at 0
        tee.ar[0] = 2 
        


        ...

        return jump_str
    
    @staticmethod
    def clear(dest):
        for i in range(POLYNOMIAL_ARRAY_SIZE):
            dest.ar[i] = 0

    
    @staticmethod
    def strtopolynomial(poly, string):
        buffer = bytearray( POLYNOMIAL_ARRAY_SIZE * 8 + 1 )
        length = len(string[:POLYNOMIAL_ARRAY_SIZE*8])
        buffer[:length] = string
        buffer[POLYNOMIAL_ARRAY_SIZE*8] = 0
        errno = 0
        pos = length-8
        i = 0
        while pos >= 0 and i < POLYNOMIAL_ARRAY_SIZE):
            poly.ar[i] = int.from_bytes(buffer[pos:pos+1], 'little')
            buffer[pos] = 0
            pos -= 8
            i += 1
        if pos+8 > 0:
            poly.ar[i] = int.from_bytes(buffer[:2], 'little')
            i += 1
        while i < POLYNOMIAL_ARRAY_SIZE:
            poly.ar[i] = 0
            i += 1        


    def period_certification(self):
        if self.state == 0 \
                and self.state[1] == 0 \
                and self.state[2] == 0 \
                and self.state[3] == 0:
            self.state[0] = ord('X')
            self.state[1] = ord('S')
            self.state[2] = ord('A')
            self.state[3] = ord('D')
    
    def next_state(self):
        t = self.state[0] 
        t ^= t << self.sh1
        t ^= t >> self.sh2
        t ^= self.state[3] << sh3
        self.state[0] = self.state[1]
        self.state[1] = self.state[2]
        self.state[2] = self.state[3]
        self.state[3] = t 



