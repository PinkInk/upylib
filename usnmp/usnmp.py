_getset_templ = "3014020004067075626c6963a0080200020002003000"
_trap_templ = "3020020004067075626c6963a41406042b06010440047f0000010200020043003000"

from sys import implementation
if implementation.name == "cpython":
    def const(val):
        return val
    #refer template.py
    import binascii
    _getset_templ = binascii.unhexlify(_getset_templ)
    _trap_templ = binascii.unhexlify(_trap_templ)
else:
    import ubinascii
    _getset_templ = ubinascii.unhexlify(_getset_templ)
    _trap_templ = ubinascii.unhexlify(_trap_templ)

SNMP_VER1 = const(0x00)
ASN1_INT = const(0x02)
ASN1_OCTSTR = const(0x04)
ASN1_OID = const(0x06)
ASN1_NULL = const(0x05)
ASN1_SEQ = const(0x30)
SNMP_GETREQUEST = const(0xa0)
SNMP_GETNEXTREQUEST = const(0xa1)
SNMP_GETRESPONSE = const(0xa2)
SNMP_SETREQUEST = const(0xa3)
SNMP_TRAP = const(0xa4)
SNMP_COUNTER = const(0x41)
SNMP_GUAGE = const(0x42)
SNMP_TIMETICKS = const(0x43)
SNMP_IPADDR = const(0x40)
SNMP_OPAQUE = const(0x44)
SNMP_NSAPADDR = const(0x45)
SNMP_ERR_NOERROR = const(0x00)
SNMP_ERR_TOOBIG = const(0x01)
SNMP_ERR_NOSUCHNAME = const(0x02)
SNMP_ERR_BADVALUE = const(0x03)
SNMP_ERR_READONLY = const(0x04)
SNMP_ERR_GENERR = const(0x05)
SNMP_TRAP_COLDSTART = const(0x0)
SNMP_TRAP_WARMSTART = const(0x10)
SNMP_TRAP_LINKDOWN = const(0x2)
SNMP_TRAP_LINKUP = const(0x3)
SNMP_TRAP_AUTHFAIL = const(0x4)
SNMP_TRAP_EGPNEIGHLOSS = const(0x5)


class SnmpPacket:

    def __init__(self, *args, **kwargs):
        if len(args) == 1 and type(args[0]) in (bytes, bytearray, memoryview):
            b = args[0]
        elif "type" in kwargs:
            b = _trap_templ if kwargs["type"]==SNMP_TRAP else _getset_templ
        else:
            raise ValueError("buffer or type=x required")
        ptr = 1 + frombytes_lenat(b, 0)[1]
        ptr = self._frombytes_props(b, ptr, ("ver", "community"))
        self.type = b[ptr]
        ptr += 1 + frombytes_lenat(b, ptr)[1]
        if self.type == SNMP_TRAP:
            ptr = self._frombytes_props(b, ptr,
                  ("enterprise", "agent_addr", "generic_trap", "specific_trap", "timestamp"))
        else:
            ptr = self._frombytes_props(b, ptr,
                  ("id", "err_status", "err_id"))
        ptr += 1 + frombytes_lenat(b, ptr)[1] #to varbinds
        self.varbinds = _VarBinds(b[ptr:])
        for arg in kwargs:
            if hasattr(self, arg):
                setattr(self, arg, kwargs[arg])

    #def __bytes__(self):
    def tobytes(self):
        b = tobytes_tv(ASN1_SEQ, self.varbinds.tobytes())
        if self.type == SNMP_TRAP:
            b = tobytes_tv(ASN1_OID, self.enterprise) + \
                tobytes_tv(SNMP_IPADDR, self.agent_addr) + \
                tobytes_tv(ASN1_INT, self.generic_trap) + \
                tobytes_tv(ASN1_INT, self.specific_trap) + \
                tobytes_tv(SNMP_TIMETICKS, self.timestamp) + b
        else:
            b = tobytes_tv(ASN1_INT, self.id) + \
            tobytes_tv(ASN1_INT, self.err_status) + \
            tobytes_tv(ASN1_INT, self.err_id) + b
        b = tobytes_tv(self.type, b)
        b = tobytes_tv(ASN1_INT, self.ver) + \
            tobytes_tv(ASN1_OCTSTR, self.community) + b
        b = tobytes_tv(ASN1_SEQ, b)
        return b

    def _frombytes_props(self, b, ptr, properties):
        for prop in properties:
            setattr(self, prop, frombytes_tvat(b, ptr)[1])
            ptr += 1 + sum(frombytes_lenat(b, ptr))
        return ptr


class _VarBinds:

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
        ptr += 1+frombytes_lenat(self._b, ptr)[1]
        ptr += 1+sum(frombytes_lenat(self._b, ptr))
        t,v = frombytes_tvat(self._b, ptr)
        return t,v

    def __setitem__(self, oid, tv):
        t,v = tv
        boid = tobytes_tv(ASN1_OID, oid)
        btv = tobytes_tv(t,v)
        b = bytes([ASN1_SEQ]) + tobytes_len(len(boid) + len(btv)) + boid + btv
        try:
            start = self._seek_oidtv(oid)
            stop = start + 1 + sum(frombytes_lenat(self._b, start))
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
            l, l_incr = frombytes_lenat(self._b, ptr)
            yield frombytes_tvat(self._b, ptr+1+l_incr)[1]
            ptr += 1+l+l_incr

    def __delitem__(self, oid):
        start = self._seek_oidtv(oid)
        stop = start + 1 + sum(frombytes_lenat(self._b, start))
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
        c = tobytes_tv(ASN1_OID, oid)
        lc, lc_incr = frombytes_lenat(c,0)
        while ptr < self._last+1:
            l, l_incr = frombytes_lenat(self._b, ptr)
            lo, lo_incr = frombytes_lenat(self._b, ptr+1+l_incr)
            print(c[1+lc_incr:])
            print(bytes(self._b[ptr+2+l_incr+lo_incr:ptr+2+l_incr+lo+lo_incr]))
            if c[1+lc_incr:] == self._b[ptr+2+l_incr+lo_incr:ptr+2+l_incr+lo+lo_incr]:
                return ptr
            ptr += 1+l_incr+l
        raise KeyError(oid)

    def _buf_calcsize(self, size):
        return ((size-1)//self.blocksize+1)*self.blocksize


def tobytes_tv(t, v=None):
    if t in (ASN1_SEQ, SNMP_GETREQUEST, SNMP_GETRESPONSE, SNMP_GETNEXTREQUEST, SNMP_SETREQUEST, SNMP_TRAP):
        b = v
    elif t == ASN1_OCTSTR:
        if type(v) is str:
            b = bytes(v,"utf-8")
        elif type(v) in (bytes, bytearray):
            b = v
        else:
            raise ValueError("string or buffer required")
    elif t in (ASN1_INT, SNMP_COUNTER, SNMP_GUAGE, SNMP_TIMETICKS):
        if v < 0:
            raise ValueError("ASN.1 ints must be >=0")
        else:
            b = bytes() if v!=0 else bytes(1)
            while v > 0:
                b = bytes([v & 0xff]) + b
                v //= 0x100
            if len(b)>0 and b[0]&0x80 == 0x80:
                b = bytes([0x0]) + b
    elif t == ASN1_NULL:
        b = bytes()
    elif t == ASN1_OID:
        oid = v.split(".")
        #first two indexes are encoded in single byte
        b = bytes([int(oid[0])*40 + int(oid[1])])
        for id in oid[2:]:
            id = int(id)
            b = b + bytes([id] if id<=0x7f else [id//0x80+0x80,id&0x7f])
    elif t == SNMP_IPADDR:
        b = bytes()
        for octet in v.split("."):
            octet = int(octet)
            b = b + bytes([octet])
    elif t in (SNMP_OPAQUE, SNMP_NSAPADDR):
        raise Exception("not implemented", t)
    else:
        raise TypeError("invalid type", t)
    return bytes([t]) + tobytes_len(len(b)) + b

def tobytes_len(l):
    if l < 0x80:
        return bytes([l])
    else:
        b = bytes()
        while l>0:
            b = bytes([l&0xff]) + b
            l //= 0x100
        return bytes([0x80+len(b)]) + b

def frombytes_tvat(b, ptr):
    t = b[ptr]
    l, l_incr = frombytes_lenat(b, ptr)
    end = ptr+1+l+l_incr
    ptr +=  1+l_incr
    if t in (ASN1_SEQ, SNMP_GETREQUEST, SNMP_GETRESPONSE, SNMP_GETNEXTREQUEST, SNMP_SETREQUEST, SNMP_TRAP):
        v = bytes(b[ptr:end])
    elif t == ASN1_OCTSTR:
        try:
            v = str(b[ptr:end], "utf-8")
        except: #UnicodeDecodeError:
            v = bytes(b[ptr:end])
    elif t in (ASN1_INT, SNMP_COUNTER, SNMP_GUAGE, SNMP_TIMETICKS):
        v=0
        while ptr < end:
            v = v*0x100 + b[ptr]
            ptr += 1
    elif t == ASN1_NULL:
        v=None
    elif t == ASN1_OID:
        #first 2 indexes are encoded in single byte
        v = str( b[ptr]//0x28 ) + "." + str( b[ptr]%0x28 )
        ptr += 1
        while ptr < end:
            if b[ptr]&0x80 == 0x80:
                v += "." + str((b[ptr]-0x80)*0x80 + b[ptr+1])
                ptr += 2
            else:
                v += "." + str(b[ptr])
                ptr += 1
    elif t == SNMP_IPADDR:
        v = ""
        while ptr < end:
            v += "." + str(b[ptr]) if v!="" else str(b[ptr])
            ptr += 1
    elif t in (SNMP_OPAQUE, SNMP_NSAPADDR):
        raise Exception("not implemented", t)
    else:
        raise TypeError("invalid type", t)
    return t, v

def frombytes_lenat(b, ptr):
    if b[ptr+1]&0x80 == 0x80:
        l = 0
        for i in b[ptr+2 : ptr+2+b[ptr+1]&0x7f]:
            l = l*0x100 + i
        return l, 1 + b[ptr+1]&0x7f
    else:
        return b[ptr+1], 1