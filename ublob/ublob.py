class ublob:

    def __init__(self, b=None, buf=512, blocksize=64):
        self.blocksize = blocksize
        self._b = bytearray()
        self._mb = memoryview(self._b)
        if type(b) in (bytearray, bytes):
            self.accomodate(len(b))
            self._mb[0 : len(b)] = b
            self._last = len(b)-1 
        else:
            self.accomodate(buf)
            self._last = 0

    def __len__(self):
        return self._last+1
    
    def __bytes__(self):
        return bytes( self._mb[:len(self)] )
    
    def __getitem__(self, key):
        if type(key) is slice:
            return self._b[:len(self)][key.start:key.stop:key.step]
        elif type(key) is int:
            return self._b[:len(self)][key]
        else:
            raise TypeError("invalid slice key")

    #if reqd extend buffer to accomodate size 
    #as nearest multiple of blocksize 
    def accomodate(self, size):
        newsize = ((size-1)//self.blocksize+1)*self.blocksize
        if newsize > len(self._b):
            del(self._mb)
            self._b.extend( bytearray(newsize-len(self._b)) )
            self._mb = memoryview(self._b)

    #serves _insertat if passed l=0
    #serves _cutat if passed b where len(b)==0 aka b''
    def _replaceat(self, ptr, l, b):
        self.accomodate( len(self)+len(b)-l )
        vec = len(b)-l
        self._mb[ptr : len(self)-1+vec] = self._mb[ptr+len(b) : len(self)-1+len(b)+vec]
