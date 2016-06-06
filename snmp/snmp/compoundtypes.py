from asn1der import *
from snmp.simpletypes import *
from ucollections import OrderedDict

TypeNames.extend([
        'GetRequest',
        'GetNextRequest',
        'GetResponse',
        'SetRequest',
        'Trap'
    ])

TypeCodes.extend([
        0xa0,
        0xa1,
        0xa2,
        0xa3,
        0xa4
    ])


def tlv_v_to_varbinds(b):
    v = OrderedDict()
    ptr = 1 + from_bytes_lenat(b,0)[1] #skip into sequence
    for ov in decode(b[ptr:]):
        v[ov[0]] = ov[1]
    return v

class SnmpVarBinds(Asn1DerBaseClass, OrderedDict):
    typecode = typecode_for_type('Seq')

    @staticmethod
    def from_bytes(b, t=typecode_for_type('Seq')):
        check_typecode(b[0], t)
        return SnmpVarBinds( tlv_v_to_varbinds(b) )

    def _to_bytes(self):
        b = bytes()
        for i in self:
            b += Asn1DerSeq([ i, self[i] ]).to_bytes()
        return b


_SnmpGetSetTemplate = [
    Asn1DerInt(0),          #request_id
    Asn1DerInt(0),          #error_status
    Asn1DerInt(0),          #error_id
    SnmpVarBinds({})        #variable_bindings
]

class _SnmpGetSetBaseClass(Asn1DerSeq):

    def __init__(self):
        if len(self) == 0: #no args
            for i in _SnmpGetSetTemplate:
                self.append(i)
        else: #args, validate
            for i,j in enumerate(self):
                if type(j) != type(_SnmpGetSetTemplate[i]):
                    raise ValueError('invalid initialisation data')
        self.varbinds = self[3] #expose object directly

    def id(self, id=None):
        if id == None:
            return self[0]
        else:
            if type(id) is Asn1DerInt:
                self[0] = id
            else:
                raise ValueError('expected an Asn1DerInt')

    def err_status(self, err_status=None):
        if err_status == None:
            return self[1]
        else:
            if type(err_status) is Asn1DerInt:
                self[1] = err_status
            else:
                raise ValueError('expected an Asn1DerInt')

    def err_id(self, err_id=None):
        if err_id == None:
            return self[2]
        else:
            if type(err_id) is Asn1DerInt:
                self[2] = err_id
            else:
                raise ValueError('expected an Asn1DerInt')


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
    SnmpVarBinds({})            #variable_bindings
]

class _SnmpTrapBaseClass(Asn1DerSeq):

    def __init__(self):
        if len(self) == 0: #no args
            for i in _SnmpTrapTemplate:
                self.append(i)
        else: #args, validate
            for i,j in enumerate(self):
                if type(j) != type(_SnmpTrapTemplate[i]):
                    raise ValueError('invalid initialisation data')
        self.varbinds = self[5]

    def enterprise(self, enterprise=None):
        if enterprise == None:
            return self[0]
        else:
            if type(enterpise) is Asn1DerOid:
                self[0] = enterprise
            else:
                raise ValueError('expected an Asn1DerOid')
    
    def agent_ip(self, agent_ip=None):
        if agent_ip == None:
            return self[1]
        else:
            if type(agent_ip) is SnmpIPAddr:
                self[1] = agent_ip
            else:
                raise ValueError('expected an SnmpIPAddr') 

    def generic_trap(self, generic_trap=None):
        if generic_trap == None:
            return self[2]
        else:
            if type(generic_trap) is Asn1DerInt:
                self[2] = generic_trap
            else:
                raise ValueError('expected an Asn1DerInt')
    
    def specific_trap(self, specific_trap=None):
        if specific_trap == None:
            return self[3]
        else:
            if type(specific_trap) is Asn1DerInt:
                self[3] = specific_trap
            else:
                raise ValueError('expected an Asn1DerInt')

    def timestamp(self, timestamp=None):
        if timestamp == None:
            self[4] = timestamp
        else:
            if type(timestamp) is SnmpTimeTicks:
                self[4] = timestamp
            else:
                raise ValueError('expected an SnmpTimeTicks')            


class SnmpTrap(_SnmpTrapBaseClass):
    typecode = typecode_for_type('Trap')

    @staticmethod
    def frombytes(b, t=typecode_for_type('Trap')):
        check_typecode(b[0], t)
        return SnmpTrap( tlv_v_to_seq(b) )


TypeClasses.extend([
        SnmpGetRequest,
        SnmpGetNextRequest,
        SnmpGetResponse,
        SnmpSetRequest,
        SnmpTrap
    ])
