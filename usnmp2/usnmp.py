#https://en.wikipedia.org/wiki/Abstract_Syntax_Notation_One

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
#as discrete from string decoded is req'd
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


#class blob(bytearray):
#    def insertat(self,ptr,b):
#        if ptr<0 or ptr>=len(self):
#            raise IndexError("index out of range")
#        self.extend( bytearray( len(b)) )
#        mb = memoryview(self)
#        for i in range(len(b)):
#             mb[ptr+len(b)+i] = mb[ptr+i]
#             mb[ptr+i] = b[i]
#    def cutat(self,ptr,l):
#        if ptr<0 or ptr>=len(self):
#            raise IndexError("index out of range")
#        mb = memoryview(self)
#        for i in range(l):
#            mb[ptr+i] = mb[ptr+l+i]
            

def get_len(b, ptr):
    if b[ptr+1]&0x80 == 0x80:
        l = 0
        offset = 2+b[ptr+1]&0x7f
        mb = memoryview(b)
        for i in mb[2 : offset]:b
            l = l*0x100 + i
        del(mb)
    else:
        l = b[ptr+1]
        offset = 2
    return l, offset

def get_payload(b, ptr):
    t = b[ptr]
    l, offset = get_len(b,ptr)
    end = ptr + l
    ptr += offset
    mb = memoryview(b)
    #sequence types
    if t in (ASN1_SEQ, \
             SNMP_GETREQUEST, SNMP_GETRESPONSE, SNMP_GETNEXTREQUEST, \
             SNMP_SETREQUEST, SNMP_TRAP):
        v = []
        while ptr < end:
            lb, lb_offset = get_len( mb, ptr )
            v.append( bytes(mb[ptr : ptr+lb_offset+lb]) )
            ptr += lb + lb_offset
    #octet string
    elif t == ASN1_OCTSTR:
        #if binary data contains unprintables (e.g. a mac-addr)
        #decode as a string of hex value pairs
        #else decode as python string
        printable = True
        for byte in mb[ptr:]:
            if not 128>byte>31:
                printable = False
                break
        if not printable:
            v = ""
            for byte in mb[ptr : ptr+l]:
                if byte<0x10:
                    v += '0' + hex(byte)[2:]
                else:
                    v += hex(byte)[2:]
        else:
            v = bytes(mb[ptr : ptr+l]).decode()
    #integers
    elif t in (ASN1_INT, SNMP_COUNTER, SNMP_GUAGE, SNMP_TIMETICKS):
        v = 0
        for byte in mb[ptr : ptr+l]:
            v = v*0x100 + byte
    #null
    elif t == ASN1_NULL:
        if mb[ptr-1]==0 and l==0:
            v = None
        else:
            raise Exception("bad null encoding")
    #oid
    elif t == ASN1_OID:
        #first 2 indexes are encoded in single byte
        v = str( mb[ptr]//0x28 ) + "." + str( mb[ptr]%0x28 )
        ptr += 1
        high_septet = 0
        for byte in mb[ptr:]:
            if byte&0x80 == 0x80:
                high_septet = byte - 0x80
            else:
                v += "." + str(high_septet*0x80 + byte)
                high_septet = 0
    #ip address            
    elif t == SNMP_IPADDR:
        v = str( mb[ptr] )
        for byte in mb[ptr+1 : ptr+len]:
            v += "." + str(byte)
    elif t in (SNMP_OPAQUE, SNMP_NSAPADDR):
        raise Exception("SNMP_[OPAQUE & NSAPADDR] not implemented")
    else:
        raise Exception("invalid type", t)
    del(mb)
    return v
