import gc

SNMP_VER1 = const(0x00)
ASN1_INT = const(0x02)
ASN1_OCTSTR = const(0x04)
ASN1_OID = const(0x06)
ASN1_NULL = const(0x05)
ASN1_SEQ = const(0x30)
ASN1_OCTSTR_BIN = const(0xff)
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

gc.collect()

def pack(p):
    t,v = p
    if type(v) is list:
        v = v[:]
        for i, val in enumerate(v):
            v[i] = pack(val)
    return pack_tlv(t,v)

gc.collect()

def pack_tlv(t, v):
    b=bytearray()
    if t in (ASN1_SEQ, SNMP_GETREQUEST, SNMP_GETRESPONSE, SNMP_GETNEXTREQUEST, SNMP_SETREQUEST, SNMP_TRAP):
        for block in v:
            b.extend(block)
    elif t == ASN1_OCTSTR:
        b = bytearray(map(ord, v))
    elif t == ASN1_OCTSTR_BIN:
        ptr = 0
        b = bytearray()
        while ptr<len(v):
            b.append( int(v[ptr:ptr+2], 16) )
            ptr += 2
        t = ASN1_OCTSTR
    elif t in (ASN1_INT, SNMP_COUNTER, SNMP_GUAGE, SNMP_TIMETICKS):
        if v < 0:
            raise Exception("-ve int")
        else:
            b.append(v & 0xff)
            v //= 0x100
            while v > 0:
                b = bytearray([v & 0xff]) + b
                v //= 0x100
            if b[0]&0x80==0x80:
                b = bytearray([0x0]) + b
    elif t == ASN1_NULL:
        l = 0x0
    elif t == ASN1_OID:
        oid = v.split(".")
        oid = list(map(int, oid))
        b.append(oid[0]*40 + oid[1])
        for id in oid[2:]:
            if 0 <= id <= 0x7f:
                b.append(id)
            elif 0x7f < id < 0x7fff:
                b.append(id//0x80+0x80)
                b.append(id&0x7f)
            else:
                raise ValueError("oid chunk out of bounds")
    elif t == SNMP_IPADDR:
        for byte in map(int, v.split(".")):
            b.append(byte)
    elif t in (SNMP_OPAQUE, SNMP_NSAPADDR):
        raise Exception("not implemented", t)
    return bytearray([t]) + pack_len(len(b)) + b

gc.collect()

def pack_len(l):
    if l < 0x80:
        return bytearray([l])
    else:
        b = bytearray()
        while l>0:
            b = bytearray([l&0xff]) + b
            l //= 0x100
        return bytearray([0x80+len(b)]) + b

gc.collect()

def unpack(b):
    t,l,v = unpack_tlv(b)
    if type(v) is list:
        for i, val in enumerate(v):
            v[i] = unpack(val)
    elif type(v) is bytearray:
        v = unpack(v)
    return [t,v]

gc.collect()

def unpack_tlv(b):
    ptr = 0
    t = b[ptr]
    l, l_incr = unpack_len(b)
    ptr +=  1 + l_incr
    if t in (ASN1_SEQ, SNMP_GETREQUEST, SNMP_GETRESPONSE, SNMP_GETNEXTREQUEST, SNMP_SETREQUEST, SNMP_TRAP):
        v = []
        while ptr < len(b):
            lb, lb_incr = unpack_len( b[ptr:] )
            v.append( b[ptr : ptr+1+lb_incr+lb] )
            ptr += 1 + lb + lb_incr
    elif t == ASN1_OCTSTR:
        printable = True
        for byte in b[ptr:]:
            if not 128>byte>31:
                printable = False
                break
        if not printable:
            t = ASN1_OCTSTR_BIN
            v = ""
            for byte in b[ptr : ptr+l]:
                if byte<0x10:
                    v += "0" + hex(byte)[2:]
                else:
                    v += hex(byte)[2:]
        else:
            v = bytes(b[ptr : ptr+l]).decode()
    elif t in (ASN1_INT, SNMP_COUNTER, SNMP_GUAGE, SNMP_TIMETICKS):
        v=0
        for byte in b[ptr:]:
            v = v*0x100 + byte
    elif t == ASN1_NULL:
        if b[1]==0 and len(b)==2:
            v=None
        else:
            raise Exception("bad null encoding")
    elif t == ASN1_OID:
        v = str( b[ptr]//0x28 ) + "." + str( b[ptr]%0x28 )
        ptr += 1
        high_septet = 0
        for byte in b[ptr:]:
            if byte&0x80 == 0x80:
                high_septet = byte - 0x80
            else:
                v += "." + str(high_septet*0x80 + byte)
                high_septet = 0
    elif t == SNMP_IPADDR:
        v = str(b[ptr])
        for byte in b[ptr+1:]:
            v += "." + str(byte)
    elif t in (SNMP_OPAQUE, SNMP_NSAPADDR):
        raise Exception("not implemented", t)
    else:
        raise Exception("invalid type", t)
    return t, 1+l+l_incr, v

gc.collect()

def unpack_len(v):
    if v[1]&0x80 == 0x80:
        l = 0
        for i in v[2 : 2+v[1]&0x7f]:
            l = l*0x100 + i
        return l, 1 + v[1]&0x7f
    else:
        return v[1], 1

gc.collect()

