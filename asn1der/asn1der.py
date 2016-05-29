TypeNames   = ['Int', 'OctStr', 'Null', 'Oid', 'Seq']
TypeCodes   = [0x02, 0x04, 0x05, 0x06, 0x30]


class _Asn1DerBaseClass:
    der_type = None

    def tobytes(self):
        b = self._tobytes()
        l = len(b)
        if l < 0x80:
            lb = bytes([l])
        else:
            lb = bytes()
            while l>0:
                lb = bytes([l&0xff]) + lb
                l //= 0x100
            lb = bytes([0x80+len(lb)]) + lb
        return bytes([self.der_type]) + lb + b


class Asn1DerInt(_Asn1DerBaseClass, int):
    der_type = TypeCodes[TypeNames.index('Int')]

    @staticmethod
    def frombytes(b, t=TypeCodes[TypeNames.index('Int')]):
        if b[0] != t:
            raise ValueError('expected type ' + str(t) + ' got', b[0])
        ptr = 1+frombytes_lenat(b,0)[1]
        return Asn1DerInt(int.from_bytes(b[ptr:]))

    def _tobytes(self):
        b = super().to_bytes((len(hex(self+0))-1)//2)
        return bytes(1)+b if b[0]&0x80 == 0x80 else b 


class Asn1DerOid(_Asn1DerBaseClass, str):
    der_type = TypeCodes[TypeNames.index('Oid')]

    @staticmethod
    def frombytes(b, t=TypeCodes[TypeNames.index('Oid')]):
        if b[0] != t:
            raise ValueError('expected type ' + str(t) + ' got', b[0])
        ptr = 1+frombytes_lenat(b,0)[1]
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
        return Asn1DerOid(v)

    def _tobytes(self):
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


class Asn1DerOctStr(_Asn1DerBaseClass, bytes):
    der_type = TypeCodes[TypeNames.index('OctStr')]

    @staticmethod
    def frombytes(b, t=TypeCodes[TypeNames.index('OctStr')]):
        if b[0] != t:
            raise ValueError('expected type ' + str(t) + ' got', b[0])
        ptr = 1+frombytes_lenat(b,0)[1]
        return Asn1DerOctStr(b[ptr:])

    def _tobytes(self):
        return bytes(self)


class Asn1DerSeq(_Asn1DerBaseClass, list):
     der_type = TypeCodes[TypeNames.index('Seq')]

     @staticmethod
     def frombytes(b, t=TypeCodes[TypeNames.index('Seq')]):
         if b[0] != t:
             raise ValueError('expected type ' + str(t) + ' got', b[0])
         ptr = 1+frombytes_lenat(b,0)[1]
         v = Asn1DerSeq([])
         while ptr < len(b):
            l, l_incr = frombytes_lenat(b, ptr)
            v.append( TypeClasses[TypeCodes.index(b[ptr])].frombytes(b[ptr:ptr+1+l_incr+l]) )
            ptr += 1+l_incr+l
         return v

     def _tobytes(self):
         b = bytes()
         for i in self:
            b += i.tobytes()
         return b


#no python primitive ... consider singleton
#so `is Asn1DerNull` can be tested
class Asn1DerNull(_Asn1DerBaseClass):
    der_type = TypeCodes[TypeNames.index('Null')]

    @staticmethod
    def frombytes(b, t=TypeCodes[TypeNames.index('Null')]):
        if b[0] != t:
            raise ValueError('expected type ' + str(t) + ' got', b[0])
        return Asn1DerNull()

    def _tobytes(self):
        return bytes()


TypeClasses = [Asn1DerInt, Asn1DerOctStr, Asn1DerNull, Asn1DerOid, Asn1DerSeq]

def frombytes_lenat(b, ptr):
    if b[ptr+1]&0x80 == 0x80:
        l = 0
        for i in b[ptr+2 : ptr+2+b[ptr+1]&0x7f]:
            l = l*0x100 + i
        return l, 1 + b[ptr+1]&0x7f
    else:
        return b[ptr+1], 1

def decode(b):
    v, ptr = [], 0
    while ptr < len(b):
        l, l_incr = frombytes_lenat(b, ptr)
        v.append( TypeClasses[TypeCodes.index(b[ptr])].frombytes(b[ptr:ptr+1+l_incr+l]) )
        ptr += 1+l_incr+l
    return v
