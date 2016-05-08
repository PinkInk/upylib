from sys import implementation
if implementation.name == "cpython":
    def const(val):
        return val

#SNMP versions
SNMP_VER1 = const(0x00)

#ASN.1 primitives
ASN1_INT = const(0x02)
ASN1_OCTSTR = const(0x04)
ASN1_OID = const(0x06)
ASN1_NULL = const(0x05)
ASN1_SEQ = const(0x30)

#library fudge specific binary octstr
#------------------------------------
#labelling of binary decoded ocstr vals
#as discrete from string decoded is reqd
#to allow unpack/pack to return same result
ASN1_OCTSTR_BIN = const(0xff)

#SNMP specific SEQUENCE types
SNMP_GETREQUEST = const(0xa0)
SNMP_GETNEXTREQUEST = const(0xa1)
SNMP_GETRESPONSE = const(0xa2)
SNMP_SETREQUEST = const(0xa3)
SNMP_TRAP = const(0xa4)

#SNMP specific integer types
SNMP_COUNTER = const(0x41)
SNMP_GUAGE = const(0x42)
SNMP_TIMETICKS = const(0x43)

#SNMP specific other types
SNMP_IPADDR = const(0x40)
SNMP_OPAQUE = const(0x44) #not implemented
SNMP_NSAPADDR = const(0x45) #not implemented

#SNMP error codes
SNMP_ERR_NOERROR = const(0x00)
SNMP_ERR_TOOBIG = const(0x01)
SNMP_ERR_NOSUCHNAME = const(0x02)
SNMP_ERR_BADVALUE = const(0x03)
SNMP_ERR_READONLY = const(0x04)
SNMP_ERR_GENERR = const(0x05)

#SNMP Generic Trap codes
SNMP_TRAPGENERIC_COLDSTART = const(0x0)
SNMP_TRAPGENERIC_WARMSTART = const(0x10)
SNMP_TRAPGENERIC_LINKDOWN = const(0x2)
SNMP_TRAPGENERIC_LINKUP = const(0x3)
SNMP_TRAPGENERIC_AUTHENTICATIONFAILURE = const(0x4)
SNMP_TRAPGENERIC_EGPNEIGHBORLOSS = const(0x5)


class SnmpPacket:
    def __init__(self, *args, **kwargs):
        if len(args) == 1 and type(args[0]) in (bytes, bytearray):
            self.unpacked = unpack(args[0])
        elif "type" in kwargs:
            if kwargs["type"] != SNMP_TRAP:
                #get/set types
                self.unpacked = unpack(_SNMP_GETSET_PROTOTYPE)
            elif kwargs["type"] == SNMP_TRAP:
                self.unpacked = unpack(_SNMP_TUPLE_PROTOTYPE)
            else:
                raise Exception("Invalid type")
            for arg in kwargs:
                if arg not in ["varbinds", "unpacked", "packed"] \
                        and hasattr(self, arg):
                    #non type specific kwargs silently ignored by properties
                    setattr(self, arg, kwargs[arg])
        else:
            raise Exception("Bytearray or type=xxx required")
        if self.type != SNMP_TRAP:
            #get/set types
            self.varbinds = _VarBinds(self.unpacked[1][2][1][3][1])
        else:
            self.varbinds = _VarBinds(self.unpacked[1][2][1][5][1])
    #get|set specific properties
    @property
    def id(self):
        if self.type != SNMP_TRAP:
            return self.unpacked[1][2][1][0][1]
    @id.setter
    def id(self, v):
        if self.type != SNMP_TRAP:
            self.unpacked[1][2][1][0][1] = v
    @property
    def err_status(self):
        if self.type != SNMP_TRAP:
            return self.unpacked[1][2][1][1][1]
    @err_status.setter
    def err_status(self, v):
        if self.type != SNMP_TRAP:
            self.unpacked[1][2][1][1][1] = v
    @property
    def err_id(self):
        if self.type != SNMP_TRAP:
            return self.unpacked[1][2][1][2][1]
    @err_id.setter
    def err_id(self, v):
        if self.type != SNMP_TRAP:
            self.unpacked[1][2][1][2][1] = v
    #trap specific properties
    @property
    def enterprise(self):
        if self.type == SNMP_TRAP:
            return self.unpacked[1][2][1][0][1]
    @enterprise.setter
    def enterprise(self, v):
        if self.type == SNMP_TRAP:
            self.unpacked[1][2][1][0][1] = v
    @property
    def agent_addr(self):
        if self.type == SNMP_TRAP:
            return self.unpacked[1][2][1][1][1]
    @agent_addr.setter
    def agent_addr(self, v):
        if self.type == SNMP_TRAP:
            self.unpacked[1][2][1][1][1] = v
    @property
    def generic_trap(self):
        if self.type == SNMP_TRAP:
            return self.unpacked[1][2][1][2][1]
    @generic_trap.setter
    def generic_trap(self, v):
        if self.type == SNMP_TRAP:
            self.unpacked[1][2][1][2][1] = v
    @property
    def specific_trap(self):
        if self.type == SNMP_TRAP:
            return self.unpacked[1][2][1][3][1]
    @specific_trap.setter
    def specific_trap(self, v):
        if self.type == SNMP_TRAP:
            self.unpacked[1][2][1][3][1] = v
    @property
    def time_stamp(self):
        if self.type == SNMP_TRAP:
            return self.unpacked[1][2][1][4][1]
    @time_stamp.setter
    def time_stamp(self, v):
        if self.type == SNMP_TRAP:
            self.unpacked[1][2][1][4][1] = v
    #common properties
    @property
    def packed(self):
        return pack(self.unpacked)
    @property
    def ver(self):
        return self.unpacked[1][0][1]
    @ver.setter
    def ver(self, v):
        self.unpacked[1][0][1] = v
    @property
    def community(self):
        return self.unpacked[1][1][1]
    @community.setter
    def community(self, v):
        self.unpacked[1][1][1] = v
    @property
    def type(self):
        return self.unpacked[1][2][0]
    @type.setter
    def type(self, v):
        self.unpacked[1][2][0] = v


class _VarBinds:
    def __init__(self, vbs):
        self.vbs = vbs
    def __getitem__(self, oid):
        for oid_tv in self.vbs:
            if oid_tv[1][0][1] == oid:
                if callable(oid_tv[1][1]):
                    return oid_tv[1][1]
                else:
                    return oid_tv[1][1][0], oid_tv[1][1][1]
        return None
    def __setitem__(self, oid, tv):
        existing = False
        for oid_tv in self.vbs:
            if oid_tv[1][0][1] == oid:
                existing = True
                oid_tv[1][1] = tv
                break
        if not existing:
            if callable(tv):
                self.vbs.append([ASN1_SEQ, [[ASN1_OID, oid], tv]])
            else:
                self.vbs.append([ASN1_SEQ, [[ASN1_OID, oid], list(tv)]])
    def __repr__(self):
        s = "{"
        for oid_tv in self.vbs:
            if len(s) > 1:
                s += ", "
            s += "\'" + oid_tv[1][0][1] + "\': "
            if callable(oid_tv[1][1]):
                s += repr(oid_tv[1][1])
            else:
                #force to look like tuple returned by __getitem__
                s += repr(oid_tv[1][1]).replace( "[", "(" ).replace( "]", ")" )
        return s + "}"
    def __iter__(self):
        for oid_tv in self.vbs:
            yield oid_tv[1][0][1]
    def __delitem__(self, oid):
        for i, oid_tv in enumerate(self.vbs):
            if oid_tv[1][0][1] == oid:
                del(self.vbs[i])

def pack(p):
    if callable(p):
        t,v = p()
    else:
        t,v = p
    if type(v) is list:
        #deepcopy the list
        v = v[:]
        for i, val in enumerate(v):
            v[i] = pack(val)
    return pack_tlv(t,v)

def pack_tlv(t, v=None):
    b=bytearray()
    if callable(t) and v==None:
        t,v = t()
    if t in (ASN1_SEQ, \
             SNMP_GETREQUEST, SNMP_GETRESPONSE, SNMP_GETNEXTREQUEST, \
             SNMP_SETREQUEST, SNMP_TRAP):
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
    #int types
    elif t in (ASN1_INT, SNMP_COUNTER, SNMP_GUAGE, SNMP_TIMETICKS):
        #cant eecode -ve (do -ve values occur in snmp?)
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
    #null type
    elif t == ASN1_NULL:
        l = 0x0
    #OIDs
    elif t == ASN1_OID:
        oid = v.split(".")
        oid = list(map(int, oid))
        #first two indexes are encoded in single byte
        b.append(oid[0]*40 + oid[1])
        for id in oid[2:]:
            if 0 <= id <= 0x7f:
                b.append(id)
            #check RFCs for correct upperbound
            elif 0x7f < id < 0x7fff:
                b.append(id//0x80+0x80)
                b.append(id&0x7f)
            else:
                raise ValueError("oid chunk out of bounds")
    #IP addr
    elif t == SNMP_IPADDR:
        for byte in map(int, v.split(".")):
            b.append(byte)
    #not implemented
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
    #bugfix: waiting upy fix for memoryview?
    #mb = memoryview(b)
    #t,l,v = unpack_tlv(mb)
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
             SNMP_GETREQUEST, SNMP_GETRESPONSE, SNMP_GETNEXTREQUEST, \
             SNMP_SETREQUEST, SNMP_TRAP):
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
        for byte in b[ptr:]:
            if not 128>byte>31:
                printable = False
                break
        #if l == 6 or not printable:
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
    #integer types
    elif t in (ASN1_INT, SNMP_COUNTER, SNMP_GUAGE, SNMP_TIMETICKS):
        #cant decode -ve (do -ve values occur in snmp?)
        v=0
        for byte in b[ptr:]:
            v = v*0x100 + byte
    #null type
    elif t == ASN1_NULL:
        if b[1]==0 and len(b)==2:
            v=None
        else:
            raise Exception("bad null encoding")
    #OIDs
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
    #IP addr
    elif t == SNMP_IPADDR:
        v = str(b[ptr])
        for byte in b[ptr+1:]:
            v += "." + str(byte)
    #unimplemented
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

#internals - template packets
_SNMP_GETSET_PROTOTYPE = pack_tlv(ASN1_SEQ,[
    pack_tlv(ASN1_INT, SNMP_VER1),
    pack_tlv(ASN1_OCTSTR, ""),
    pack_tlv(SNMP_GETREQUEST,[
        pack_tlv(ASN1_INT,1),
        pack_tlv(ASN1_INT,0),
        pack_tlv(ASN1_INT,0),
        pack_tlv(ASN1_SEQ,[])
    ])
])
_SNMP_TUPLE_PROTOTYPE = pack_tlv(ASN1_SEQ,[
    pack_tlv(ASN1_INT, SNMP_VER1),
    pack_tlv(ASN1_OCTSTR, ""),
    pack_tlv(SNMP_TRAP,[
        pack_tlv(ASN1_OID,"1.3.6.1.4.1"),
        pack_tlv(SNMP_IPADDR,"127.0.0.1"),
        pack_tlv(ASN1_INT,0),
        pack_tlv(ASN1_INT,0),
        pack_tlv(ASN1_INT,0),
        pack_tlv(ASN1_SEQ,[])
    ])
])

