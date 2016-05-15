from sys import implementation
if implementation.name == "cpython":
    def const(val):
        return val

INT = const(0x02)
OCTSTR = const(0x04)
OID = const(0x06)
NULL = const(0x05)
SEQ = const(0x30)
    
SEQUENCES = (SEQ,)
INTEGERS = (INT,)

def tobytes_tv(t, v=None, seqs=SEQUENCES, ints=INTEGERS):
    if t in (seqs):
        b = v
    elif t == OCTSTR:
        if type(v) is str:
            b = bytes(v,"utf-8")
        elif type(v) in (bytes, bytearray):
            b = v
        else:
            raise ValueError("string or buffer required")
    elif t in (ints):
        if v < 0:
            raise ValueError("ASN.1 ints must be >=0")
        else:
            b = bytes()
            while v > 0:
                b = bytes([v & 0xff]) + b
                v //= 0x100
            if len(b)>0 and b[0]&0x80 == 0x80:
                b = bytes([0x0]) + b
    elif t == NULL:
        b = bytes()
    elif t == OID:
        oid = v.split(".")
        #first two indexes are encoded in single byte
        b = bytes([int(oid[0])*40 + int(oid[1])])
        for id in oid[2:]:
            id = int(id)
            b = b + bytes([id] if id<=0x7f else [id//0x80+0x80,id&0x7f])
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

def frombytes_tvat(b, ptr, seqs=SEQUENCES, ints=INTEGERS):
    t = b[ptr]
    l, l_incr = frombytes_lenat(b, ptr)
    end = ptr+1+l+l_incr
    ptr +=  1+l_incr
    if t in seqs:
        v = bytes(b[ptr:end])
    elif t == OCTSTR:
        try:
            v = str(b[ptr:end], "utf-8")
        except: #UnicodeDecodeError:
            v = bytes(b[ptr:end])
    elif t in ints:
        v=0
        while ptr < end:
            v = v*0x100 + b[ptr]
            ptr += 1
    elif t == NULL:
        v=None
    elif t == OID:
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
