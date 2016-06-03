from asn1der import *

try:
    from ucollection import OrderedDict
except:
    from collection import OrderedDict

try:
    const(1)
except:
    const = lambda x : x

SNMP_VER1 = const(0x0)

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

#------------------------------------------------
# consider comments at top of asn1der.py first
# and refactor all (reduction in code lines and
# complexity) before further work
#
def tlv_v_to_varbinds(b):
    v = {}
    ptr = 1 + from_bytes_lenat(b,0)[1] #skip into sequence
    while ptr < len(b):
        l, l_incr = from_bytes_lenat(b, ptr)
        
    return v

class SnmpVarBinds(Asn1DerBaseClass, OrderedDict):
    typecode = typecode_for_type('Seq')
    
    @staticmethod
    def from_bytes(b, t=typecode_for_type('Seq')):
        check_typecode(b[0], t)
        return Asn1DerSeq( tlv_v_to_varbinds(b) )
    
    def _to_bytes(self):
        pass

#------------------------------------------------


_SnmpGetSetTemplate = [
    Asn1DerInt(0),  #request_id
    Asn1DerInt(0),  #error_status
    Asn1DerInt(0),  #error_id
    Asn1DerSeq([])  #variable_bindings
]

class _SnmpGetSetBaseClass(Asn1DerSeq):
    
    def __init__(self):
        if len(self) == 0:
            #initd without arg, load template
            for i in _SnmpGetSetTemplate:
                self.append(i)
        else:
            #initd with arg, validate
            for i,j in enumerate(self):
                if type(j) != type(_SnmpGetSetTemplate[i]):
                    raise ValueError('invalid initialisation data')
        #mpy implements __getattr__ but not __setattr__
        #assignment must be appropriate class
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
            #initd without arg, load template
            for i in _SnmpTrapTemplate:
                self.append(i)
        else:
            #initd with arg, validate
            for i,j in enumerate(self):
                if type(j) != type(_SnmpTrapTemplate[i]):
                    raise ValueError('invalid initialisation data')
        #mpy implements __getattr__ but not __setattr__
        #assignment must be appropriate class
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


_SnmpPacketTemplate = [
    Asn1DerInt(SNMP_VER1),
    Asn1DerOctStr(b'community'),
    None
]

class SnmpPacket(Asn1DerSeq):

    def __init__(self, t=None):
        if len(self) == 0:
            #initd without arg, load template
            for i in _SnmpPacketTemplate:
                self.append(i)
        else:
            #initd with arg, validate
            for i,j in enumerate(self):
                if type(j) != type(_SnmpPacketTemplate[i]):
                    raise ValueError('invalid initialisation data')
        #mpy implements __getattr__ but not __setattr__
        #assignment must be appropriate class
        self.ver = self[0]
        self.community = self[1]
        self.varbinds = self[2]                
    

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
