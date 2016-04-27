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


class SnmpPacket:

    def __init__(self, b=None, buf=512, blocksize=64):
        self._blocksize = blocksize
        if type(b) in (bytearray, bytes):
            buflen = ((len(b)-1)//self._blocksize+1)*self._blocksize
            self._b = bytearray(buflen)
            self._mb = memoryview(self._b)
            self._mb[0:len(b)] = b
        else:
            buflen = ((buf-1)//self._blocksize+1)*self._blocksize
            self._b = bytearray(buflen)
            self._mb = memoryview(self._b)

    def _get_lenat(self, ptr):
        mb = self._mb
        if mb[ptr+1]&0x80 == 0x80:
            l = 0
            offset = 2+mb[ptr+1]&0x7f
            for i in mb[2 : offset]:
                l = l*0x100 + i
        else:
            l = mb[ptr+1]
            offset = 2
        del(mb)
        return l, offset

    def _get_payloadat(self, ptr):
        mb = self._mb
        t = mb[ptr]
        l, offset = self._get_lenat(ptr)
        end = ptr + offset + l
        ptr += offset
        #sequence types
        if t in (ASN1_SEQ, \
                 SNMP_GETREQUEST, SNMP_GETRESPONSE, SNMP_GETNEXTREQUEST, \
                 SNMP_SETREQUEST, SNMP_TRAP):
            v = []
            while ptr < end:
                lb, lb_offset = self._get_lenat(ptr)
                v.append( bytes( mb[ptr : ptr+lb_offset+lb]) )
                ptr += lb + lb_offset
        #octet string
        elif t == ASN1_OCTSTR:
            #if binary data contains unprintables (e.g. a mac-addr)
            #decode as a string of hex value pairs
            #else decode as python string
            printable = True
            for byte in mb[ptr:end]:
                if not 128>byte>31:
                    printable = False
                    break
            if not printable:
                v = ""
                for byte in mb[ptr : ptr+l]:
                    if byte < 0x10:
                        v += '0' + hex(byte)[2:]
                    else:
                        v += hex(byte)[2:]
            else:
                v = bytes(mb[ptr : ptr+l]).decode()
        #integers
        elif t in (ASN1_INT, SNMP_COUNTER, SNMP_GUAGE, SNMP_TIMETICKS):
            v = 0
            #for byte in mb[ptr : ptr+l]:
            for byte in mb[ptr:end]:
                v = v*0x100 + byte
        #null
        elif t == ASN1_NULL:
            if mb[ptr-1]==0 and l==0:
                v = None
            else:
                raise BadNullEncoding
        #oid
        elif t == ASN1_OID:
            #first 2 indexes are encoded in single byte
            v = str( self._mb[ptr]//0x28 ) + "." + str( self._mb[ptr]%0x28 )
            ptr += 1
            high_septet = 0
            for byte in mb[ptr:end]:
                if byte&0x80 == 0x80:
                        high_septet = byte - 0x80
                else:
                    v += "." + str(high_septet*0x80 + byte)
                    high_septet = 0
        #ip address
        elif t == SNMP_IPADDR:
            v = ""
            for byte in mb[ptr:end]:
                if len(v) > 0:
                    v += "." + str(byte)
                else:
                    v += str(byte)
        elif t in (SNMP_OPAQUE, SNMP_NSAPADDR):
            raise UnimplementedType(t)
        else:
            raise InvalidType(t)
        del(mb)
        return t, v

    def __len__(self):
        return sum(self._get_lenat(0))
    
    def __bytes__(self):
        return bytes( self._mb[:len(self)] )

    #extend buffer (if necessary) to nearest multiple
    #of _blocksize that will accomodate size
    def _buf_extend(self, size):
        idealsize = ((size-1)//self._blocksize+1)*self._blocksize
        if idealsize > len(self._b):
            del(self._mb)
            self._b.extend( bytearray(size-len(self._b)) )
            self._mb = memoryview(self._b)

    #serves _insertat if passed l=0
    #serves _cutat if passed b where len(b)==0 aka b''
    def _replaceat(self, ptr, l, b):
        pl, poffset = self._get_lenat(0)
        self._buf_extend( pl+offset+l )
        mb = self._mb
        vector = l-len(b)
        for i in range(abs(vector)):
            if vector>0:
                mb[pl+l-i] = mb[pl-i]
            else:
                mb[pl-i] = mb[pl+l-i]
        del(mb)


class InvalidType(Exception):
    pass

class UnimplementedType(Exception):
    pass

class BadNullEncoding(Exception):
    pass

class InternalError(Exception):
    pass