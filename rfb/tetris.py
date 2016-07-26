
class Tetrimino:
    def __init__(self,x,y,w,h,colour,bits):
        self.x,self.y = x,y
        self.w,self.h = w,h
        self.colour = colour
        self.bits = bits

tetriminos = [
    Tetrimino(10,0, 4,1, (255,0,0), b'\x01\x01\x01\x01'),
    
]