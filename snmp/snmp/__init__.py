from asn1der import *
from snmp.getset import * 
from snmp.trap import *

try:
    const(1)
except:
    def const(v):
        return v

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


_SnmpPacketTemplate = [
    Asn1DerInt(SNMP_VER1),
    Asn1DerOctStr(b'community'),
    SnmpGetRequest()
]

class SnmpPacket(Asn1DerSeq):

    def __init__(self, t=None):
        if len(self) == 0: #no args
            for i in _SnmpPacketTemplate:
                self.append(i)
        else: #args, validate
            for i,j in enumerate(self):
                if type(j) != type(_SnmpPacketTemplate[i]):
                    raise ValueError('invalid initialisation data')
        self.data = self[2] #expose object directly

    def ver(self, ver=None):
        if ver == None:
            return self[0]
        else:
            if type(ver) is Asn1DerInt:
                self[0] = ver
            else:
                raise ValueError('expected an Asn1DerInt')

    def community(self, community=None):
        if community == None:
            return self[1]
        else:
            if type(community) is Asn1DerOctStr:
                self[1] = community
            else:
                raise ValueError('expected an Asn1DerOctStr')
