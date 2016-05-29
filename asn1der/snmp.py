from asn1der import *
from collections import OrderedDict
try:
    const(1)
except:
    def const(v):
        return v

ERR_NOERROR = const(0x00)
ERR_TOOBIG = const(0x01)
ERR_NOSUCHNAME = const(0x02)
ERR_BADVALUE = const(0x03)
ERR_READONLY = const(0x04)
ERR_GENERR = const(0x05)

TRAP_COLDSTART = const(0x0)
TRAP_WARMSTART = const(0x10)
TRAP_LINKDOWN = const(0x2)
TRAP_LINKUP = const(0x3)
TRAP_AUTHFAIL = const(0x4)
TRAP_EGPNEIGHLOSS = const(0x5)

TypeNames.extend([
        'IPAddr',
        'Counter', 
        'Guage', 
        'TimeTicks',
        'GetRequest',
        'GetNextRequest',
        'GetResponse',
        'SetRequest',
        'Trap'
    ])

TypeCodes.extend([
        0x41, 
        0x42, 
        0x43,
        0xa0,
        0xa1,
        0xa2,
        0xa3,
        0xa4
    ])


def bytes2ip(b):
    ptr = 1+frombytes_lenat(b,0)[1]
    v = ''
    while ptr < len(b):
        v += '.' + str(b[ptr]) if v!='' else str(b[ptr])
        ptr += 1
    return v

class SnmpIPAddr(Asn1DerBaseClass, str):
    typecode = TypeCodes[TypeNames.index('IPAddr')]

    @staticmethod
    def frombytes(b, t=TypeCodes[TypeNames.index('IPAddr')]):
        super().frombytes(b, t=t)
        return SnmpIPAddr( bytes2ip(b) )

    def self2bytes(self):
        b = bytes()
        for i in self.split('.'):
            b = b + bytes([int(i)])
        return b


class SnmpCounter(Asn1DerInt):    
    typecode = TypeCodes[TypeNames.index('Counter')]
    
    @staticmethod
    def frombytes(b, t=TypeCodes[TypeNames.index('Counter')]):
        super().frombytes(b, t=t)
        return SnmpCounter( bytes2int(b) )


class SnmpGuage(Asn1DerInt):    
    typecode = TypeCodes[TypeNames.index('Guage')]
    
    @staticmethod
    def frombytes(b, t=TypeCodes[TypeNames.index('Guage')]):
        super().frombytes(b, t=t)
        return SnmpGuage( bytes2int(b) )


class SnmpTimeTicks(Asn1DerInt):    
    typecode = TypeCodes[TypeNames.index('TimeTicks')]
    
    @staticmethod
    def frombytes(b, t=TypeCodes[TypeNames.index('TimeTicks')]):
        super().frombytes(b, t=t)
        return SnmpTimeTicks( bytes2int(b) )


#------------------------------------------------------------------
def bytes2getrequest(b, t):
    pass

class SnmpGetRequest(Asn1DerBaseClass, OrderedDict):
    typecode = TypeCodes[TypeNames.index('GetRequest')]

    @staticmethod
    def frombytes(b, t=TypeCodes[TypeNames.index('GetRequest')]):
        super().frombytes(b, t=t)
        return SnmpGetNextRequest( bytes2getrequest(b) )
    
    def self2bytes(self):
        pass
#------------------------------------------------------------------

class SnmpGetNextRequest(SnmpGetRequest):
    typecode = TypeCodes[TypeNames.index('GetNextRequest')]

    @staticmethod
    def frombytes(b, t=TypeCodes[TypeNames.index('GetNextRequest')]):
        super().frombytes(b, t=t)
        return SnmpGetNextRequest( bytes2getrequest(b) )


TypeClasses.extend([
        SnmpIPAddr,
        SnmpCounter, 
        SnmpGuage, 
        SnmpTimeTicks,
        SnmpGetRequest,
        SnmpGetNextRequest
    ])