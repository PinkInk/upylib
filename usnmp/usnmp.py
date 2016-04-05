#SNMP versions
SNMP_VER1 = 0x00

#ASN.1 primitives
ASN1_INT = 0x02
ASN1_OCTSTR = 0x04 #OctetString
ASN1_OID = 0x06 #ObjectIdentifier
ASN1_NULL = 0x05
ASN1_SEQ = 0x30 #sequence

#library fudge specific binary octstr
#------------------------------------
#labelling of binary decoded ocstr vals
#as discrete from string decoded is req'd
#to allow unpack/pack to return same result
ASN1_OCTSTR_BIN = 0xff

#SNMP specific SEQUENCE types
SNMP_GETREQUEST = 0xa0
SNMP_GETRESPONSE = 0xa2
SNMP_GETNEXTREQUEST = 0xa1

#SNMP specific integer types
SNMP_COUNTER = 0x41
SNMP_GUAGE = 0x42
SNMP_TIMETICKS = 0x43

#SNMP specific other types
SNMP_IPADDR = 0x40
SNMP_OPAQUE = 0x44 #not handled
SNMP_NSAPADDR = 0x45 #not handled

#SNMP error codes
SNMP_ERR_NOERROR = 0x00
SNMP_ERR_TOOBIG = 0x01
SNMP_ERR_NOSUCHNAME = 0x02
SNMP_ERR_BADVALUE = 0x03
SNMP_ERR_READONLY = 0x04
SNMP_ERR_GENERR = 0x05

class GetRequest():
    #should request classes derive from "SnmpPacket" or similar?
    def __init__(self, data=None, \
                       ver=SNMP_VER1, community="public", request_id=1, mibs=[]
                ):
        if type(data) is bytearray:
            self._rawpacket = data
            unpacked = unpack(data)
            self.ver = unpacked[1][1]
            self.community = unpacked[2][1]
            self.request_id = unpacked[3][1][1]
            self.error_status = unpacked[3][2][1]
            self.index = unpacked[3][3][1]
            if self.error_status == SNMP_ERR_NOERROR:
                self.mibs = []
                for seq in unpacked[3][4][1:]:
                    self.mibs.append(seq[1][1])
        else:
            self.ver = ver
            self.community = community
            self.request_id = request_id
            self.error_status = SNMP_ERR_NOERROR
            self.index = 0
            self.mibs = mibs
    @property
    def ver(self):
        return self._ver
    @ver.setter
    def ver(self, ver):
        if ver != SNMP_VER1:
            raise Exception("unsupported value")
        else:
            return self._ver

class _SnmpPacket():
    def __init__(self, version, community, type, request_id):
        self.version(version)
        self.community(community)
        self.type(type)
    @property
    def version(self):
        return self._version
    @version.setter
    def version(self, version)
        self._version = version
    @property
    def community(self):
        return self._community
    @community.setter
    def community(self, community)
        self._community = community
    @property
    def type(self):
        return self._type
    @type.setter
    def type(self, type):
        self._type = type

class _MibCollection():
    def __init__(self):
        self._mibs = {}
    def __setitem__(self, mib, tv):
        if type(tv) not in (tuple, list):
            raise Exception("__setitem__ requires tuple")
        self._mibs[mib] = tv
    def __getitem__(self, mib):
        if callable(self._mibs[mib][1]):
            return self._mibs[mib][0], self._mibs[mib][1]()
        else:
            return self._mibs[mib]
    def pack(self):
        pass

def pack(packet):
    pass

def pack_tlv(t, v):
    b=bytearray()
    if t in (ASN1_SEQ, \
             SNMP_GETREQUEST, SNMP_GETRESPONSE, SNMP_GETNEXTREQUEST):
        for block in v:
            b.extend(block)
    elif t == ASN1_OCTSTR:
        #octet strings that unpack as strings
        b = bytearray(map(ord, v))
    elif t == ASN1_OCTSTR_BIN:
        #octet strings that string of hex pairs
        ptr = 0
        b = bytearray()
        while ptr<len(v):
            b.append( int(v[ptr:ptr+2], 16) )
            ptr += 2
        t = ASN1_OCTSTR
    elif t in (ASN1_INT, SNMP_COUNTER, SNMP_GUAGE, SNMP_TIMETICKS):
        #can't eecode -ve (do -ve values occur in snmp?)
        if v < 0:
            raise Exception("SNMP, -ve int")
        else:
            b.append(v & 0xff)
            v //= 0x100
            while v > 0:
                b = bytearray([v & 0xff]) + b
                v //= 0x100
            #+ve values with high 0rder bit set are prefixed by 0x0
            #observed in snmp, indicating -ve snmp ints are possible?
            if b[0]&0x80==0x80:
                b = bytearray([0x0]) + b
    elif t == ASN1_NULL:
        l = 0x0
    elif t == ASN1_OID:
        oid = v.split(".")
        oid = list(map(int, oid))
        #first two indexes are encoded in single byte
        b.append(oid[0]*40 + oid[1])
        for id in oid[2:]:
            if 0 <= id < 0x7f:
                b.append(id)
                #check RFC's for correct upperbound
            elif 0x7f < id < 0x7fff:
                b.append(id//0x80+0x80)
                b.append(id&0x7f)
            else:
                raise ValueError("SNMP, oid out of bounds")
    elif t == SNMP_IPADDR:
        for byte in map(int, v.split(".")):
            b.append(byte)
    elif t in (SNMP_OPAQUE, SNMP_NSAPADDR):
        raise Exception("SNMP, OPAQUE and NSAPADDR encoding not implemented")
    return bytearray([t]) + pack_len(len(b)) + b

def pack_len(l):
    #msdn.microsoft.com/en-us/library/windows/desktop/bb648641(v=vs.85).aspx
    #indicates encoding that differs from observation, for snmp
    #length of 0 valid for ASN1_NULL type
    if 0 <= l < 0x7f:
        return bytearray([l])
    #check RFC's for correct upperbound
    elif 0x7f < l < 0x7fff:
        return bytearray([l//0x80+0x80, l&0x7f])
    else:
        raise Exception("SNMP, length out of bounds")

def unpack(b):
    ptr = 0
    t,l,v = unpack_tlv(b)
    if type(v) is list:
        packet = [t]+v
    else:
        packet = [t,v]
    if type(v) is bytearray:
        packet[1] = unpack(v)
    elif type(v) is list:
        for i,val in enumerate(packet[1:]):
            packet[1+i] = unpack(val)
    return packet

def unpack_tlv(b):
    ptr = 0
    t = b[ptr]
    l, l_incr = unpack_len(b)
    ptr +=  1 + l_incr
    #sequence types
    if t in (ASN1_SEQ, \
             SNMP_GETREQUEST, SNMP_GETRESPONSE, SNMP_GETNEXTREQUEST):
        v = []
        while ptr < len(b):
            lb, lb_incr = unpack_len( b[ptr:] )
            v.append( b[ptr : ptr+1+lb_incr+lb] )
            ptr += 1 + lb + lb_incr
    #octet string
    elif t == ASN1_OCTSTR:
        #commonly accepted fudge:
        #if len == 6 or any 128>byte>31
        #decode as string of hex vals (common case: mac address)
        #else decode as string
        printable = True
        for byte in b[ptr:ptr+1]:
            if not 128>byte>31:
                printable = False
                break
        if l == 6 or not printable:
            t = ASN1_OCTSTR_BIN
            v = ""
            for byte in b[ptr : ptr+l]:
                if byte<0x10:
                    v += '0' + hex(byte)[2:]
                else:
                    v += hex(byte)[2:]
        else:
            v = bytes(b[ptr : ptr+l]).decode()
    elif t in (ASN1_INT, SNMP_COUNTER, SNMP_GUAGE, SNMP_TIMETICKS):
        #can't decode -ve (do -ve values occur in snmp?)
        v=0
        for byte in b[ptr:]:
            v = v*0x100 + byte
    elif t == ASN1_NULL:
        if b[1]==0 and len(b)==2:
            v=None
        else:
            raise Exception("SNMP, unpack - bad null encoding")
    elif t == ASN1_OID:
        #first 2 indexes are encoded in single byte
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
        raise Exception("SNMP, unpack - OPAQUE & NSAPADDR not implemented")
    else:
        raise Exception("SNMP, unpack - invalid block code encountered")
    return t, 1+l+l_incr, v

def unpack_len(v):
    #msdn.microsoft.com/en-us/library/windows/desktop/bb648641(v=vs.85).aspx
    #indicates encoding that differs from observation, for snmp
    ptr=1
    if v[ptr]&0x80 == 0x80:
        return ((v[ptr]-0x80)*0x80) + v[ptr+1], 2
    else:
        return v[ptr], 1
