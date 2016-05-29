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
            lb = bytes([0x80+len(b)]) + lb
        return bytes([self.der_type]) + lb + b


class Asn1DerInt(_Asn1DerBaseClass, int):
    der_type = Asn1DerTypes{'INT'}
    
    @staticmethod
    def frombytes(b, t=Asn1DerTypes{'INT'}):
        if b[0] != t:
            raise ValueError('expected type ' + str(t) + ' got', b[0])
        ptr = 1+frombytes_lenat(b,0)[1]
        v=0
        while ptr < len(b):
            v = v*0x100 + b[ptr]
            ptr += 1
        return Asn1DerInt(v)
    
    def _tobytes(self):
        v = self+0
        b = bytes() if v!=0 else bytes(1)
        while v > 0:
             b = bytes([v & 0xff]) + b
             v //= 0x100
        if len(b)>0 and b[0]&0x80 == 0x80:
            b = bytes(1) + b
        return b

class Asn1DerOid(_Asn1DerBaseClass, str):
    der_type = Asn1DerTypes{'OID'}
    
    @staticmethod
    def frombytes(b, t=Asn1DerTypes{'OID'}):
        if b[0] != t:
            raise ValueError('expected type ' + str(t) + ' got', b[0])
        ptr = 1+frombytes_lenat(b,0)[1]
        #first 2 indexes are encoded in single byte
        v = str( b[ptr]//0x28 )
        if b[ptr]%0x28 != 0:
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
    der_type = Asn1DerTypes{'OCTSTR'}
    
    @staticmethod
    def frombytes(b, t=Asn1DerTypes{'OCTSTR'}):
        if b[0] != t:
            raise ValueError('expected type ' + str(t) + ' got', b[0])
        ptr = 1+frombytes_lenat(b,0)[1]
        return Asn1DerOctStr(b[ptr:])
    
    def _tobytes(self):
        return bytes(self)


class Asn1DerSeqAsBytes(_Asn1DerBaseClass, bytes):
    der_type = Asn1DerTypes{'SEQ'}
    
    @staticmethod
    def frombytes(b, t=Asn1DerTypes{'SEQ'}):
        if b[0] != t:
            raise ValueError('expected type ' + str(t) + ' got', b[0])
        ptr = 1+frombytes_lenat(b,0)[1]
        return Asn1DerOctStr([bptr:])
    
    def _tobytes(self):
        return bytes(self)

#fully unpack sequence recursively into list of
#Asn1DerTypes 
# class Asn1DerSeq(_Asn1DerBaseClass, list):
#     der_type = 0x30
    
#     @staticmethod
#     def frombytes(b, t=0x30):
#         if b[0] != t:
#             raise ValueError('expected type ' + str(t) + ' got', b[0])
#         ptr = 1+frombytes_lenat(b,0)[1]
#         pass
    
#     def _tobytes(self):
#         pass


# class Asn1DerNull(_Asn1DerBaseClass):
#     der_type = 0x05
    
#     @staticmethod
#     def frombytes(b, t=0x05):
#         if b[0] != t:
#             raise ValueError('expected type ' + str(t) + ' got', b[0])
#         return Asn1DerNull()
    
#     def _tobytes(self):
#         return bytes()
 

 
# class SnmpCounter(Asn1DerInt):
#     typecode = 0x04
#     def frombytes(b, t=0x04):
#         return super().from_bytes(b, t=t)

def frombytes_lenat(b, ptr):
    if b[ptr+1]&0x80 == 0x80:
        l = 0
        for i in b[ptr+2 : ptr+2+b[ptr+1]&0x7f]:
            l = l*0x100 + i
        return l, 1 + b[ptr+1]&0x7f
    else:
        return b[ptr+1], 1

#only implemented types
Asn1DerTypes = {
    'INT':      (0x02, Asn1DerInt),
    'OCTSTR':   (0x04, Asn1DerOctStr),
    'NULL':     (0x05, Asn1DerNull),
    'OID':      (0x06, Asn1DerOid),
    'SEQ':      (0x30, Asn1DerSeqAsBytes),
}