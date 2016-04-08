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
SNMP_OPAQUE = 0x44 #not implemented
SNMP_NSAPADDR = 0x45 #not implemented

#SNMP error codes
SNMP_ERR_NOERROR = 0x00
SNMP_ERR_TOOBIG = 0x01
SNMP_ERR_NOSUCHNAME = 0x02
SNMP_ERR_BADVALUE = 0x03
SNMP_ERR_READONLY = 0x04
SNMP_ERR_GENERR = 0x05


class GetResponse(oldSNMPPacket):
    def __init__(self, data=None, \
                       ver=SNMP_VER1, community="public", pid=1
                ):
        if data == None:
            SNMPPacket.__init__(self, \
                ver=ver, ptype=SNMP_GETRESPONSE, community=community, pid=pid \
            )
        else:
            SNMPPacket.__init__(self, data=data)
            if self.type != SNMP_GETRESPONSE:
                raise Exception("not a GetResponse packet")
            if self.err_status == SNMP_ERR_NOERROR:
                self._unpacked_getoids(unpack(data))


class GetRequest(oldSNMPPacket):
    def __init__(self, data=None, \
                       ver=SNMP_VER1, community="public", pid=1, oids=[]
                ):
        if data == None:
            SNMPPacket.__init__(self, \
                ver=ver, ptype=SNMP_GETREQUEST, community=community, pid=pid \
            )
            for oid in oids:
                self.setoid(oid)
        else:
            SNMPPacket.__init__(self, data=data)
            if self.type != SNMP_GETREQUEST:
                raise Exception("not a GetRequest packet")
            if self.err_status == SNMP_ERR_NOERROR:
                self._unpacked_getoids(unpack(data))


class oldSNMPPacket():
    def __init__(self, data=None, \
                       ver=SNMP_VER1, ptype=None, community="public", pid=1
                ):
        self._ver = None
        self._community = None
        self._type = None
        self._id = None
        self._err_status = None
        self._err_id = None
        self._oids = {}
        #self._packet = None
        if data == None:
            if ptype == None:
                raise Exception("type not specified")
            self.ver = ver
            self.community = community
            self.type = ptype
            self.id = pid
            self.err_status = SNMP_ERR_NOERROR
            self.err_id = 0x0
        else:
            #self._packet = data
            up = unpacked(unpack(data))
            self.ver = up.ver
            self.community = up.community
            self.type = up.type
            self.id = up.id
            self.err_status = up.err_status
            self._err_id = up.err_id
    #methods to get & set oid dictionary members
    def getoid(self, oid, evaluate=False):
        #-------------------------------------------------
        #TO IMPLEMENT
        #if evaluate == True and tv or v is callable
        # call and return results
        #-------------------------------------------------
        try:
            return self._oids[oid]
        except:
            return None
    def setoid(self, oid, tv=None):
        if tv == None:
            self._oids[oid] = ASN1_NULL, None
        else:
            self._oids[oid] = tv
    #method to itterate over oid dictionary
    def __iter__(self):
        return self._oids.__iter__()
    def getpacket(self):
        return pack_tlv(ASN1_SEQ, [
                                pack_tlv(ASN1_INT, self.ver),
                                pack_tlv(ASN1_OCTSTR, self.community),
                                self._pack_payload()
        ])
    #helper methods for packet assembly
    def _pack_payload(self):
        return pack_tlv(self.type, [
                                pack_tlv(ASN1_INT, self.id),
                                pack_tlv(ASN1_INT, self.err_status),
                                pack_tlv(ASN1_INT, self.err_id),
                                self._pack_oids()
        ])
    def _pack_oids(self):
        oids = []
        for oid in self:
            tv = self.getoid(oid)
            if callable(tv):
                t,v = tv()
            else:
                t,v = tv
            if callable(v):
                t,v = t, v()
            oids.append( pack_tlv(ASN1_SEQ, [
                                    pack_tlv(ASN1_OID, oid),
                                    pack_tlv(t,v)
                                 ]) \
                       )
        return pack_tlv(ASN1_SEQ, oids)
    #standard snmp public properties
    @property
    def ver(self): return self._ver
    @ver.setter
    def ver(self, ver): self._ver = ver
    @property
    def community(self): return self._community
    @community.setter
    def community(self, community): self._community = community
    @property
    def type(self): return self._type
    @type.setter
    def type(self, type): self._type = type
    @property
    def id(self): return self._id
    @id.setter
    def id(self, pid): self._id = pid
    @property
    def err_status(self): return self._err_status
    @err_status.setter
    def err_status(self, err_status): self._err_status = err_status
    @property
    def err_id(self): return self._err_id
    @err_id.setter
    def err_id(self, err_id): self._err_id = err_id

class SnmpPacket():
    def __init__(self, pl):
        self._unpacked = None
        self.unpacked = pl
    @property
    def unpacked(self):
        l = self._unpacked.copy()
        l[1][2][1][3][1] = mib_to_list(l[1][2][1][3][1])
        return l
    @unpacked.setter
    def unpacked(self, v):
        v = v.copy()
        v[1][2][1][3][1] = list_to_mib(v[1][2][1][3][1])
        self._unpacked = v
    @property
    def mib(self):
        return self._unpacked[1][2][1][3][1]
    @mib.setter
    def mib(self, v):
        if type(v) is list:
            self._unpacked[1][2][1][3][1] = list_to_mib(v)
        elif type(v) is dict:
            self._unpacked[1][2][1][3][1] = v
    @property
    def ver(self): return self._unpacked[1][0][1]
    @ver.setter
    def ver(self, v): self._unpacked[1][0][1] = v
    @property
    def community(self): return self._unpacked[1][1][1]
    @community.setter
    def community(self, v): self._unpacked[1][1][1] = v
    @property
    def type(self): return self._unpacked[1][2][0]
    @type.setter
    def type(self, v): self._unpacked[1][2][0] = v
    @property
    def id(self): return self._unpacked[1][2][1][0][1]
    @id.setter
    def id(self, v): self._unpacked[1][2][1][0][1] = v
    @property
    def err_status(self): return self._unpacked[1][2][1][1][1]
    @err_status.setter
    def err_status(self, v): self._unpacked[1][2][1][1][1] = v
    @property
    def err_id(self): return self._unpacked[1][2][1][2][1]
    @err_id.setter
    def err_id(self, v): self._unpacked[1][2][1][2][1] = v

def mib_to_list(mib):
    l = []
    for k in mib:
        l.append([ASN1_SEQ, [[ASN1_OID, k], list(mib[k])]])
    return l

def list_to_mib(data):
    mib = {}
    for oid_tv in data:
        oid = oid_tv[1][0][1]
        t = oid_tv[1][1][0]
        v = oid_tv[1][1][1]
        mib[oid] = (t, v)
    return mib

def pack(p):
    t,v = p
    if type(v) is list:
        for i, val in enumerate(v):
            v[i] = pack(val)
    return pack_tlv(t,v)

def pack_tlv(t, v):
    b=bytearray()
    if t in (ASN1_SEQ, \
             SNMP_GETREQUEST, SNMP_GETRESPONSE, SNMP_GETNEXTREQUEST):
        for block in v:
            b.extend(block)
    #octet strings that unpack as python strings
    elif t == ASN1_OCTSTR:
        b = bytearray(map(ord, v))
    #octet strings that unpack as string of hex value pairs
    elif t == ASN1_OCTSTR_BIN:
        ptr = 0
        b = bytearray()
        while ptr<len(v):
            b.append( int(v[ptr:ptr+2], 16) )
            ptr += 2
        t = ASN1_OCTSTR
    elif t in (ASN1_INT, SNMP_COUNTER, SNMP_GUAGE, SNMP_TIMETICKS):
        #can't eecode -ve (do -ve values occur in snmp?)
        if v < 0:
            raise Exception("-ve int")
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
                raise ValueError("oid chunk out of bounds")
    elif t == SNMP_IPADDR:
        for byte in map(int, v.split(".")):
            b.append(byte)
    elif t in (SNMP_OPAQUE, SNMP_NSAPADDR):
        raise Exception("SNMP_[OPAQUE & NSAPADDR] not implemented")
    return bytearray([t]) + pack_len(len(b)) + b

def pack_len(l):
    if l < 0x80:
        return bytearray([l])
    else:
        b = bytearray()
        while l>0:
            b = bytearray([l&0xff]) + b
            l //= 0x100
        return bytearray([0x80+len(b)]) + b

def unpack(b):
    t,l,v = unpack_tlv(b)
    if type(v) is list:
        for i, val in enumerate(v):
            v[i] = unpack(val)
    elif type(v) is bytearray:
        v = unpack(v)
    return [t,v]

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
        #if binary data contains unprintables (e.g. a mac-addr)
        #  decode as a string of hex value pairs
        #  return a non-standard type-code as a hint to pack_tlv
        #else decode as python string
        printable = True
        for byte in b[ptr:ptr+1]:
            if not 128>byte>31:
                printable = False
                break
        #if l == 6 or not printable:
        if not printable:
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
            raise Exception("bad null encoding")
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
        raise Exception("SNMP_[OPAQUE & NSAPADDR] not implemented")
    else:
        raise Exception("invalid type", t)
    return t, 1+l+l_incr, v

def unpack_len(v):
    if v[1]&0x80 == 0x80:
        l = 0
        for i in v[2 : 2+v[1]&0x7f]:
            l = l*0x100 + i
        return l, 1 + v[1]&0x7f
    else:
        return v[1], 1

def hex2str(v):
    ptr = 0
    s = ""
    while ptr<len(v):
        s += chr( int(v[ptr:ptr+2], 16) )
        ptr += 2
    return s
