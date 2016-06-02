from asn1der import *

try:
    const(1)
except:
    const = lambda x : x

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
        # 'Opaque',
        # 'NsApAddr',
        'GetRequest',
        'GetNextRequest',
        'GetResponse',
        'SetRequest',
        'Trap'
    ])

TypeCodes.extend([
        0x40,
        0x41, 
        0x42, 
        0x43,
        # 0x44,
        # 0x45,
        0xa0,
        0xa1,
        0xa2,
        0xa3,
        0xa4
    ])


def tlv_v_to_ipaddr(b):
    ptr = 1 + from_bytes_lenat(b, 0)[1]
    v = ''
    while ptr < len(b):
        v += '.' + str(b[ptr]) if v!='' else str(b[ptr])
        ptr += 1
    return bytes(v, 'utf-8')

#subclass of bytes 
#subclasses of str do not behave as expected 
#in current micropython version      
class SnmpIPAddr(Asn1DerBaseClass, bytes):
# class SnmpIPAddr(Asn1DerBaseClass, str):
    typecode = typecode_for_type('IPAddr')

    @staticmethod
    def from_bytes(b, t=typecode_for_type('IPAddr')):
        check_typecode(b[0], t)
        return SnmpIPAddr( tlv_v_to_ipaddr(b) )

    def _to_bytes(self):
        b = bytes()
        for i in self.split(b'.'):
            b = b + bytes([int(i)])
        return b


class SnmpCounter(Asn1DerInt):    
    typecode = typecode_for_type('Counter')
    
    @staticmethod
    def from_bytes(b, t=typecode_for_type('Counter')):
        check_typecode(b[0], t)    
        return SnmpCounter( tlv_v_to_int(b) )


class SnmpGuage(Asn1DerInt):    
    typecode = typecode_for_type('Guage')
    
    @staticmethod
    def from_bytes(b, t=typecode_for_type('Guage')):
        check_typecode(b[0], t)    
        return SnmpGuage( tlv_v_to_int(b) )


class SnmpTimeTicks(Asn1DerInt):    
    typecode = typecode_for_type('TimeTicks')
    
    @staticmethod
    def from_bytes(b, t=typecode_for_type('TimeTicks')):
        check_typecode(b[0], t)    
        return SnmpTimeTicks( tlv_v_to_int(b) )


_SnmpGetSetTemplate = [
    Asn1DerInt(0),  #request_id
    Asn1DerInt(0),  #error_status
    Asn1DerInt(0),  #error_id
    Asn1DerSeq([])  #variable_bindings
]

class _SnmpGetSetBaseClass(Asn1DerSeq):
    
    def __init__(self):
        if len(self) == 0:
            #assume we were initialised without arg
            for i in _SnmpGetSetTemplate:
                self.append(i)
        else:
            #validate structure
            for i,j in enumerate(self):
                if type(j) != type(_SnmpGetSetTemplate[i]):
                    raise ValueError('invalid initialisation data')
        #micropython doesn't implements __getattr__, not __setattr__
        self.id = self[0]
        self.err_status = self[1]
        self.err_id = self[2]
        self.varbinds = self[3]


class SnmpGetRequest(_SnmpGetSetBaseClass):
    typecode = typecode_for_type('GetRequest')
    
    @staticmethod
    def frombytes(b, t=typecode_for_type('GetRequest')):
        check_typecode(b[0], t)    
        return SnmpGetNextRequest( tlv_v_to_seq(b) )
    

class SnmpGetNextRequest(_SnmpGetSetBaseClass):
    typecode = typecode_for_type('GetNextRequest')

    @staticmethod
    def frombytes(b, t=typecode_for_type('GetNextRequest')):
        check_typecode(b[0], t)    
        return SnmpGetNextRequest( tlv_v_to_seq(b) )


class SnmpGetResponse(_SnmpGetSetBaseClass):
    typecode = typecode_for_type('GetResponse')

    @staticmethod
    def frombytes(b, t=typecode_for_type('GetResponse')):
        check_typecode(b[0], t)    
        return SnmpGetNextRequest( tlv_v_to_seq(b) )


class SnmpSetRequest(_SnmpGetSetBaseClass):
    typecode = typecode_for_type('SetRequest')

    @staticmethod
    def frombytes(b, t=typecode_for_type('SetRequest')):
        check_typecode(b[0], t)    
        return SnmpSetRequest( tlv_v_to_seq(b) )

_SnmpTrapTemplate = [
    Asn1DerOid(b'1.3.6.1.4.1'), #enterprise_oid
    SnmpIPAddr(b'127.0.0.1'),   #ip_address
    Asn1DerInt(0),              #generic_type
    Asn1DerInt(0),              #specific_type
    SnmpTimeTicks(0),           #timestamp
    Asn1DerSeq([])              #variable_bindings
]

class _SnmpTrapBaseClass(Asn1DerSeq):
    
    def __init__(self):
        if len(self) == 0:
            #assume we were initialised without arg
            for i in _SnmpTrapTemplate:
                self.append(i)
        else:
            #validate structure
            for i,j in enumerate(self):
                if type(j) != type(_SnmpTrapTemplate[i]):
                    raise ValueError('invalid initialisation data')
        #micropython doesn't implements __getattr__, not __setattr__
        self.enterprise = self[0]
        self.agent_addr = self[1]
        self.generic_trap = self[2]
        self.specific_trap = self[3]
        self.timestamp = self[4]
        self.varbinds = self[5]


class SnmpTrap(_SnmpTrapBaseClass):
    typecode = typecode_for_type('Trap')

    @staticmethod
    def frombytes(b, t=typecode_for_type('Trap')):
        check_typecode(b[0], t)    
        return SnmpTrap( tlv_v_to_seq(b) )


TypeClasses.extend([
        SnmpIPAddr,
        SnmpCounter, 
        SnmpGuage, 
        SnmpTimeTicks,
        # SnmpOpaque,
        # SnmpNsApAddr,
        SnmpGetRequest,
        SnmpGetNextRequest,
        SnmpGetResponse,
        SnmpSetRequest,
        SnmpTrap
    ])
