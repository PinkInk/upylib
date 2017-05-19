try:
    const(1)
except:
    def const(v):
        return v

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

#ASN.1 sequence and SNMP derivatives
_SNMP_SEQs = bytes([ASN1_SEQ,
                    SNMP_GETREQUEST,
                    SNMP_GETRESPONSE,
                    SNMP_GETNEXTREQUEST,
                    SNMP_SETREQUEST,
                    SNMP_TRAP
                  ])

#ASN.1 int and SNMP derivatives
_SNMP_INTs = bytes([ASN1_INT,
                    SNMP_COUNTER,
                    SNMP_GUAGE,
                    SNMP_TIMETICKS
                  ])


def tobytes_tv(t, v=None):
    if t in _SNMP_SEQs:
        b = v
    elif t == ASN1_OCTSTR:
        if type(v) is str:
            b = bytes(v,'utf-8')
        elif type(v) in (bytes, bytearray):
            b = v
        else:
            raise ValueError('string or buffer required')
    elif t in _SNMP_INTs:
        if v < 0:
            raise ValueError('ASN.1 ints must be >=0')
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
        oid = v.split('.')
        #first two indexes are encoded in single byte
        b = bytes([int(oid[0])*40 +(int(oid[1]) if len(oid)>1 else 0)])
        for id in oid[2:]:
            id = int(id)
            ob = bytes() if id>0 else bytes([0])
            while id > 0:
                ob = bytes([id&0x7f if len(ob)==0 else 0x80+(id&0x7f)]) + ob
                id //= 0x80
            b += ob
    elif t == SNMP_IPADDR:
        b = bytes()
        for octet in v.split('.'):
            octet = int(octet)
            b = b + bytes([octet])
    elif t in (SNMP_OPAQUE, SNMP_NSAPADDR):
        raise Exception('not implemented', t)
    else:
        raise TypeError('invalid type', t)
    return bytes([t]) + tobytes_len(len(b)) + b

def tobytes_len(l):
    if l < 0x80:
        return bytes([l])
    else:
        b = bytes()
        while l > 0:
            b = bytes([l&0xff]) + b
            l //= 0x100
        return bytes([0x80+len(b)]) + b

def frombytes_tvat(b, ptr):
    t = b[ptr]
    l, l_incr = frombytes_lenat(b, ptr)
    end = ptr+1+l_incr+l
    ptr +=  1+l_incr
    if t in _SNMP_SEQs:
        v = bytes(b[ptr:end])
    elif t == ASN1_OCTSTR:
        try:
            v = str(b[ptr:end], 'utf-8')
        except: #UnicodeDecodeError:
            v = bytes(b[ptr:end])
    elif t in _SNMP_INTs:
        v=0
        while ptr < end:
            v = v*0x100 + b[ptr]
            ptr += 1
    elif t == ASN1_NULL:
        v=None
    elif t == ASN1_OID:
        #first 2 indexes are encoded in single byte
        v = str( b[ptr]//0x28 )
        if b[ptr]%0x28 != 0:
            v += '.' + str( b[ptr]%0x28 )
        ptr += 1
        ob = 0
        while ptr < end:
            if b[ptr]&0x80 == 0x80:
                ob = ob*0x80 + (b[ptr]&0x7f)
            else:
                v += '.' + str((ob*0x80)+b[ptr])
                ob = 0
            ptr += 1
    elif t == SNMP_IPADDR:
        v = ''
        while ptr < end:
            v += '.' + str(b[ptr]) if v!='' else str(b[ptr])
            ptr += 1
    elif t in (SNMP_OPAQUE, SNMP_NSAPADDR):
        raise Exception('not implemented', t)
    else:
        raise TypeError('invalid type', t)
    return t, v

def frombytes_lenat(b, ptr):
    if b[ptr+1]&0x80 == 0x80:
        l = 0
        for i in b[ptr+2 : ptr+2+b[ptr+1]&0x7f]:
            l = l*0x100 + i
        return l, 1 + b[ptr+1]&0x7f
    else:
        return b[ptr+1], 1
