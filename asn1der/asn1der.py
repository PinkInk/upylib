TypeNames = [
        'Int', 
        'OctStr', 
        'Null', 
        'Oid', 
        'Seq'
    ]

TypeCodes = [
        0x02, 
        0x04, 
        0x05, 
        0x06, 
        0x30
    ]

def typecode_for_type(t):
    return TypeCodes[TypeNames.index(t)]

def check_typecode(b, t):
    if b != t:
        raise ValueError('expected typecode '+hex(t)+' got '+hex(b))

class Asn1DerBaseClass:
    typecode = None
    
    #expects children to implement _to_bytes(self)
    #returning byte encoded payload (which it wraps in t,l)
    def to_bytes(self):
        b = self._to_bytes()
        return self.typecode.to_bytes(1) + to_bytes_len(len(b)) + b


def tlv2int(b):
    ptr = 1 + from_bytes_lenat(b,0)[1]
    return int.from_bytes(b[ptr:] if b[ptr]!=0 else b[ptr+1:])

class Asn1DerInt(Asn1DerBaseClass, int):
    typecode = typecode_for_type('Int')

    @staticmethod
    def from_bytes(b, t=typecode_for_type('Int')):
        check_typecode(b[0], t)
        return Asn1DerInt( tlv2int(b) )

    def _to_bytes(self):
        b = (self+0).to_bytes( (len(hex(self+0))-1)//2 )
        return bytes(1)+b if b[0]&0x80 == 0x80 else b 


def tlv2oidstr(b):
    ptr = 1 + from_bytes_lenat(b,0)[1]
    #first 2 indexes are encoded in single byte
    v = str( b[ptr]//0x28 )
    if b[ptr]%0x28 != 0: #fringe case: OID == "1"
        v += '.' + str( b[ptr]%0x28 )
    ptr += 1
    ob = 0
    while ptr < len(b):
        if b[ptr]&0x80 == 0x80:
            ob = ob*0x80 + (b[ptr]&0x7f)
        else:
            v += '.' + str((ob*0x80)+b[ptr])
            ob = 0
        ptr += 1
    return v

#switch to subclass of bytes
#---------------------------
#equality test instance of subclass of str 
#to instance of str's always returns False
#in micropyhton (todo: raise ticket) 
class Asn1DerOid(Asn1DerBaseClass, str):
    typecode = typecode_for_type('Oid')

    @staticmethod
    def from_bytes(b, t=typecode_for_type('Oid')):
        check_typecode(b[0], t)
        return Asn1DerOid( tlv2oidstr(b) )

    def _to_bytes(self):
        oid = self.split('.')
        #first two indexes are encoded in single byte
        b = bytes([int(oid[0])*40 +(int(oid[1]) if len(oid)>1 else 0)])
        for id in oid[2:]:
            id = int(id)
            ob = bytes() if id>0 else bytes([0])
            while id > 0:
                ob = bytes([id&0x7f if len(ob)==0 else 0x80+(id&0x7f)]) + ob
                id //= 0x80
            b += ob
        return b


def tlv2bytes(b):
    ptr = 1 + from_bytes_lenat(b,0)[1]
    return b[ptr:]

class Asn1DerOctStr(Asn1DerBaseClass, bytes):
    typecode = typecode_for_type('OctStr')

    @staticmethod
    def from_bytes(b, t=typecode_for_type('OctStr')):
        check_typecode(b[0], t)
        return Asn1DerOctStr( tlv2bytes(b) )

    def _to_bytes(self):
        return bytes(self)


class Asn1DerSeq(Asn1DerBaseClass, list):
    typecode = typecode_for_type('Seq')

    @staticmethod
    def from_bytes(b, t=typecode_for_type('Seq')):
        check_typecode(b[0], t)
        l, l_incr = from_bytes_lenat(b,0)
        if len(b) > 1+l_incr+l:
            raise OverflowError('bytes contain multiple sequential tlv blocks')
        ptr = 1 + l_incr
        return decode(b[ptr:])

    def _to_bytes(self):
        b = bytes()
        for i in self:
            b += i.to_bytes()
        return b


class Asn1DerNull(Asn1DerBaseClass):
    typecode = typecode_for_type('Null')

    @staticmethod
    def from_bytes(b, t=typecode_for_type('Null')):
        check_typecode(b[0], t)
        return Asn1DerNull()

    def _to_bytes(v):
        return b''
    
    def __call__(self):
        return self

#singleton
Asn1DerNull = Asn1DerNull()


TypeClasses = [
        Asn1DerInt, 
        Asn1DerOctStr, 
        Asn1DerNull, 
        Asn1DerOid, 
        Asn1DerSeq
    ]

def class_for_typecodeat(b, ptr):
    return TypeClasses[TypeCodes.index(b[ptr])]

def from_bytes_lenat(b, ptr):
    if b[ptr+1]&0x80 == 0x80:
        l = 0
        for i in b[ptr+2 : ptr+2+b[ptr+1]&0x7f]:
            l = l*0x100 + i
        return l, 1 + b[ptr+1]&0x7f
    else:
        return b[ptr+1], 1

def to_bytes_len(l):
    if l < 0x80:
        return bytes([l])
    else:
        b = bytes()
        while l>0:
            b = bytes([l&0xff]) + b
            l //= 0x100
        return bytes([0x80+len(b)]) + b

def decode(b):
    v, ptr = [], 0
    while ptr < len(b):
        l, l_incr = from_bytes_lenat(b, ptr)
        c = class_for_typecodeat(b, ptr)
        v.append( c.from_bytes(b[ptr:ptr+1+l_incr+l]) )
        ptr += 1+l_incr+l
    return v
