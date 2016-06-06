from asn1der import *
from snmp.integers import *
from snmp.ipaddr import *
from snmp.varbinds import *

TypeNames.extend([
        'Trap'
    ])

TypeCodes.extend([
        0xa4
    ])


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
        SnmpTrap
    ])
