import ASN1

class VarBinds:

    def __init__(self, b, buf=128, blocksize=64):
        self.blocksize = blocksize
        self._b = bytearray( self._buf_calcsize( len(b) if len(b)>0 else buf ) )
        self._b[0:len(b)] = b
        self._last = len(b)-1

    #def __bytes__(self):
    def tobytes(self):
        return bytes( self._b[:self._last+1] )

    def __getitem__(self, oid):
        ptr = self._seek_oidtv(oid)
        ptr += 1+ASN1.frombytes_lenat(self._b, ptr)[1]
        ptr += 1+sum(ASN1.frombytes_lenat(self._b, ptr))
        t,v = ASN1.frombytes_tvat(self._b, ptr)
        return t,v

    def __setitem__(self, oid, tv):
        t,v = tv
        boid = ASN1.tobytes_tv(ASN1.OID, oid)
        btv = ASN1.tobytes_tv(t,v)
        b = bytes([ASN1.SEQ]) + ASN1.tobytes_len(len(boid) + len(btv)) + boid + btv
        try:
            start = self._seek_oidtv(oid)
            stop = start + 1 + sum(ASN1.frombytes_lenat(self._b, start))
        except KeyError:
            start = stop = self._last+1
        stop -= len(b)
        vec = start-stop
        if vec < 0:
            self._b[start : self._last+1+vec] = self._b[stop : self._last+1]
        elif vec > 0:
            self.buflen(self._last+1+vec)
            self._b[start+vec : self._last+1+vec] = self._b[start : self._last+1]
        self._b[start : start+len(b)] = b
        self._last += vec

    def __iter__(self):
        ptr = 0
        while ptr < self._last+1:
            l, l_incr = ASN1.frombytes_lenat(self._b, ptr)
            yield ASN1.frombytes_tvat(self._b, ptr+1+l_incr)[1]
            ptr += 1+l+l_incr

    def __delitem__(self, oid):
        start = self._seek_oidtv(oid)
        stop = start + 1 + sum(ASN1.frombytes_lenat(self._b, start))
        vec = start-stop
        self._b[start : self._last+1+vec] = self._b[stop : self._last+1]
        self._last += vec

    def buflen(self, size=None):
        if size != None:
            newsize = self._buf_calcsize(size)
            if newsize > self._last+1:
                self._b.extend( bytearray(newsize-self._last+1) )
        return len(self._b)

    def _seek_oidtv(self, oid):
        ptr = 0
        #compile oid to seek, negate interpreting every tlv
        c = ASN1.tobytes_tv(ASN1.OID, oid)
        lc, lc_incr = ASN1.frombytes_lenat(c,0)
        while ptr < self._last+1:
            l, l_incr = ASN1.frombytes_lenat(self._b, ptr)
            lo, lo_incr = ASN1.frombytes_lenat(self._b, ptr+1+l_incr)
            if c[1+lc_incr:] == self._b[ptr+2+l_incr+lo_incr:ptr+2+l_incr+lo+lo_incr]:
                return ptr
            ptr += 1+l_incr+l
        raise KeyError(oid)

    def _buf_calcsize(self, size):
        return ((size-1)//self.blocksize+1)*self.blocksize
