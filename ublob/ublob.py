_MP = False
from sys import implementation, platform
if implementation.name == "micropython":
    _MP = True
    import gc

class ublob:

    def __init__(self, b=None, buf=128, blocksize=32):
        self.blocksize = blocksize
        if type(b) in (bytearray, bytes):
            self._b = bytearray( self._buf_calcsize(len(b)) )
            self._mb = memoryview(self._b)
            self._mb[0 : len(b)] = memoryview(b)
            self._last = len(b) - 1
        else:
            self._b = bytearray( self._buf_calcsize(buf) )
            self._mb = memoryview(self._b)
            self._last = -1

    def __len__(self):
        return self._last+1
    
    def __bytes__(self):
        return bytes( self._mb[:len(self)] )
    
    #memory hungry but useful for repl debugging
    def __repr__(self):
        return 'bytearray(' + repr(bytes(self)) + ')'
    
    def __getitem__(self, key):
        return self._b[:len(self)][key]

    def __delitem__(self, key):
        start, stop = self._coerce_slice(key)
        if stop != None:
            vec = start - stop
            if vec < 0:
                self._mb[start : len(self)+vec] = self._mb[stop : len(self)]
                self._last += vec
        else:
            self._mb[start : len(self)-1] = self._mb[start+1 : len(self)]
            self._last -= 1

    def __setitem__(self, key, v):
        if type(v) not in (int, bytes, bytearray, memoryview):
            raise TypeError("can assign only bytes, buffer or int in range(0,256)")
        start, stop = self._coerce_slice(key)
        if stop != None:
            stop = stop - len(v)
            vec = start - stop
            if vec < 0:
                self._mb[start : len(self)+vec] = self._mb[stop : len(self)]
            elif vec > 0:
                self.buflen(len(self) + vec)
                self._mb[start+vec : len(self)+vec] = self._mb[start : len(self)]
            self._mb[start : start+len(v)] = memoryview(v)
            self._last += vec            
        else:
            if type(v) is int and 0<=v<256:
                self._mb[key] = v
            else:
                raise TypeError("int in range(0,256) required")

    def buflen(self, size=None, shrink=False):
        if size != None:
            newsize = self._buf_calcsize(size)
            if newsize > len(self._b):
                del(self._mb)
                self._b.extend( bytearray(newsize-len(self._b)) )
                self._mb = memoryview(self._b)
            elif shrink and newsize < len(self._b) and newsize >= len   (self):
                del(self._mb)
                del(self._b[newsize:])
                self._mb = memoryview(self._b)
            if _MP:
                gc.collect()
        return(len(self._mb))
    
    def _buf_calcsize(self, size):
        return ((size-1)//self.blocksize+1)*self.blocksize    

    def _coerce_slice(self, key):
        if type(key) is slice:
            if key.step != None:
                raise TypeError("step not supported")
            start = key.start if key.start!=None else 0
            start = start if start>=0 else len(self)+start
            stop = key.stop if key.stop!=None else len(self)
            stop = stop if stop>=0 else len(self)+stop
        elif type(key) is int:
            start = key if key>=0 else len(self)+key
            stop = None
        else:
            raise TypeError("indices must be int or slice")
        if start < 0 or start > self._last:
            raise IndexError("index out of range")
        return start, stop
