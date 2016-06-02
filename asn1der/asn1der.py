#Ordered list of implemented type names for lookup
#extend in subclasses to add types
TypeNames = [
        'Int', 
        'OctStr', 
        'Null', 
        'Oid', 
        'Seq'
    ]

#Ordered list of implemented type codes for lookup
#extend in subclasses to add types
TypeCodes = [
        0x02, 
        0x04, 
        0x05, 
        0x06, 
        0x30
    ]


def typecode_for_type(t):
    """
    typecode_for_type(t)
    --------------------
    Return type code(int) of type-name(t)
    """
    return TypeCodes[TypeNames.index(t)]

def check_typecode(b, t):
    """
    check_typecode(b, t)
    --------------------
    Check b(int), first byte of a t,l,v block, is of expected type(t)
    """
    if b != t:
        raise ValueError('expected typecode '+hex(t)+' got '+hex(b))

class Asn1DerBaseClass:
    """
    class Asn1DerBaseClass
    ----------------------
    Base class for Asn.1 DER useable classes
    """
    
    #Placeholder for derived class type-code(int)
    typecode = None

    @staticmethod
    def from_bytes(b, t=None):
    #def from_bytes(b, t=typecode_for_type('')):
        """
        from_bytes(b, t=typecode_for_type('<typename>'))
        --------------------------------------
        Placeholder for derived class from_bytes method
        
        Subclasses are expected to override with method
        that returns instance of self, decoded from bytes
        """
        pass
    
    #expects children to implement _to_bytes(self)
    #returning byte encoded payload (which it wraps in t,l)
    def to_bytes(self):
        """
        to_bytes(self)
        --------------
        Returns t,l,v encoded as bytes, for transmission on nw
        by wrapping output of subclass._to_bytes() in t,l 
        """
        b = self._to_bytes()
        return self.typecode.to_bytes(1) + to_bytes_len(len(b)) + b

    def _to_bytes(self):
        """
        _to_bytes(self)
        ---------------
        Return type-specific value bytes encoding
        Subclasses are expected to override this method        
        """
        pass
  


def tlv_v_to_int(b):
    """
    tlv_v_to_int
    ------------
    Return an int from the encoded v element of a t,l,v block
    Used by Asn1DerInt and derivative classes
    """
    ptr = 1 + from_bytes_lenat(b,0)[1]
    return int.from_bytes(b[ptr:] if b[ptr]!=0 else b[ptr+1:])

class Asn1DerInt(Asn1DerBaseClass, int):
    """
    Asn1DerInt
    ----------
    Asn.1 DER encoded integer class
    Does not support -ve values
    """
    typecode = typecode_for_type('Int')

    @staticmethod
    def from_bytes(b, t=typecode_for_type('Int')):
        check_typecode(b[0], t)
        return Asn1DerInt( tlv_v_to_int(b) )

    def _to_bytes(self):
        b = (self+0).to_bytes( (len(hex(self+0))-1)//2 )
        return bytes(1)+b if b[0]&0x80 == 0x80 else b 


def tlv_v_to_oid(b):
    """
    tlv_v_to_oid
    ------------
    Return an OID from the encoded v element of a t,l,v block
    Used by Asn1DerOid and derivative classes (unlikely)
    """
    ptr = 1 + from_bytes_lenat(b,0)[1]
    #first 2 indexes are encoded in single byte
    v = str(b[ptr]//0x28 )
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
    return bytes(v, 'utf-8') #coerce to bytes

#subclass of bytes 
#subclasses of str do not behave as expected 
#in current micropython version  
class Asn1DerOid(Asn1DerBaseClass, bytes):
# class Asn1DerOid(Asn1DerBaseClass, str):
    """
    Asn1DerOid
    ----------
    Asn.1 DER encoded Oid class
    """
    typecode = typecode_for_type('Oid')

    @staticmethod
    def from_bytes(b, t=typecode_for_type('Oid')):
        check_typecode(b[0], t)
        return Asn1DerOid( tlv_v_to_oid(b) )

    def _to_bytes(self):
        oid = self.split(b'.')
        #first two indexes are encoded in single byte
        b = bytes([ int(oid[0])*40 + (int(oid[1]) if len(oid)>1 else 0) ])
        for id in oid[2:]:
            id = int(id)
            ob = bytes() if id>0 else bytes([0])
            while id > 0:
                ob = bytes([ id&0x7f if len(ob)==0 else 0x80+(id&0x7f) ]) + ob
                id //= 0x80
            b += ob
        return b


def tlv_v_to_octstr(b):
    """
    tlv_v_to_octstr
    ---------------
    Return bytes from the encoded v element of a t,l,v Octet String block
    Used by Asn1DerOctStr and derivative classes (unlikely)
    """
    ptr = 1 + from_bytes_lenat(b,0)[1]
    return b[ptr:]

class Asn1DerOctStr(Asn1DerBaseClass, bytes):
    """
    Asn1DerOctStr
    -------------
    Asn.1 DER encoded Octet String class
    Octet Strings can contain non-printables (e.g. MAC Addresses)
    hence implementation as bytes derivative
    """
    typecode = typecode_for_type('OctStr')

    @staticmethod
    def from_bytes(b, t=typecode_for_type('OctStr')):
        check_typecode(b[0], t)
        return Asn1DerOctStr( tlv_v_to_octstr(b) )

    def _to_bytes(self):
        return bytes(self)


def tlv_v_to_seq(b):
    """
    tlv_v_to_seq
    ------------
    Return list from the encoded v element of a t,l,v Sequence block
    Used by Asn1DerSeq and derivative classes
    """
    v = []
    ptr = 1 + from_bytes_lenat(b,0)[1] #skip into sequence
    while ptr < len(b):
        l, l_incr = from_bytes_lenat(b, ptr)
        c = class_for_typecodeat(b, ptr)
        v.append( c.from_bytes(b[ptr:ptr+1+l_incr+l]) )
        ptr += 1+l_incr+l
    return v
    
class Asn1DerSeq(Asn1DerBaseClass, list):
    """
    Asn1DerSeq
    ----------
    Asn.1 DER encoded Sequence class
    Sequences are containers for other t,l,v's
    hence implementation as list derivative
    """
    typecode = typecode_for_type('Seq')

    @staticmethod
    def from_bytes(b, t=typecode_for_type('Seq')):
        check_typecode(b[0], t)
        return Asn1DerSeq( tlv_v_to_seq(b) )

    def _to_bytes(self):
        b = bytes()
        for i in self:
            b += i.to_bytes()
        return b


class Asn1DerNull(Asn1DerBaseClass):
    """
    Asn1DerNull
    ----------
    Asn.1 DER encoded Null class
    Implemented as a Singleton, to mimic behaviour of None
    """
    typecode = typecode_for_type('Null')

    @staticmethod
    def from_bytes(b, t=typecode_for_type('Null')):
        check_typecode(b[0], t)
        return Asn1DerNull()

    def _to_bytes(v):
        return b''
    
    def __call__(self):
        return self

#turn into Singleton
Asn1DerNull = Asn1DerNull()


#Ordered list of implemented type classes for lookup
#extend in subclasses to add types
TypeClasses = [
        Asn1DerInt, 
        Asn1DerOctStr, 
        Asn1DerNull, 
        Asn1DerOid, 
        Asn1DerSeq
    ]

def class_for_typecodeat(b, ptr):
    """
    class_for_typecodeat
    --------------------
    Return type-class (class) of t,l,v starting @ at ptr in b
    """
    return TypeClasses[TypeCodes.index(b[ptr])]

def from_bytes_lenat(b, ptr):
    """
    from_bytes_lenat
    ----------------
    Return length (int) of t,l,v starting @ ptr in b
    """
    if b[ptr+1]&0x80 == 0x80:
        l = 0
        for i in b[ptr+2 : ptr+2+b[ptr+1]&0x7f]:
            l = l*0x100 + i
        return l, 1 + b[ptr+1]&0x7f
    else:
        return b[ptr+1], 1

def to_bytes_len(l):
    """
    to_bytes_len
    ------------
    Return byte encoded l (int) of t,l,v block
    """
    if l < 0x80:
        return bytes([l])
    else:
        b = bytes()
        while l>0:
            b = bytes([l&0xff]) + b
            l //= 0x100
        return bytes([0x80+len(b)]) + b

def decode(b):
    """
    decode
    ------
    Recursively decode Asn.1 DER encoded binary data into list
    of appropriate types  
    """
    v, ptr = [], 0
    while ptr < len(b):
        l, l_incr = from_bytes_lenat(b, ptr)
        c = class_for_typecodeat(b, ptr)
        v.append( c.from_bytes(b[ptr:ptr+1+l_incr+l]) )
        ptr += 1+l_incr+l
    return v