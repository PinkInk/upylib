import ubinascii
from usnmp_codec import *
try:
    from ucollections import OrderedDict
except:
    pass

_SNMP_PROPS = ("ver", "community")
_SNMP_TRAP_PROPS = ("enterprise", "agent_addr", "generic_trap", "specific_trap", "timestamp")
_SNMP_GETSET_PROPS = ("id", "err_status", "err_id")
#packet templates, refer template.py
_SNMP_GETSET_TEMPL = ubinascii.unhexlify(b"3014020004067075626c6963a0080200020002003000")
_SNMP_TRAP_TEMPL = ubinascii.unhexlify(b"302502010004067075626c6963a41806052b0601040140047f0000010201000201004301003000")

class SnmpPacket:

    def __init__(self, *args, **kwargs):
        if len(args) == 1 and type(args[0]) in (bytes, bytearray, memoryview):
            b = args[0]
        elif "type" in kwargs:
            if kwargs["type"] == SNMP_TRAP:
                b = _SNMP_TRAP_TEMPL
            else:
                b = _SNMP_GETSET_TEMPL
        else:
            raise ValueError("buffer or type=x required")
        ptr = 1 + frombytes_lenat(b, 0)[1]
        ptr = self._frombytes_props(b, ptr, _SNMP_PROPS)
        self.type = b[ptr]
        ptr += 1 + frombytes_lenat(b, ptr)[1] #step into seq
        if self.type == SNMP_TRAP:
            ptr = self._frombytes_props(b, ptr, _SNMP_TRAP_PROPS)
        else:
            ptr = self._frombytes_props(b, ptr, _SNMP_GETSET_PROPS)
        ptr += 1 + frombytes_lenat(b, ptr)[1]
        try:
            self.varbinds = OrderedDict()
        except:
            self.varbinds = {}
        while ptr < len(b):
            ptr += 1 + frombytes_lenat(b, ptr)[1] #step into seq
            oid = frombytes_tvat(b, ptr)[1]
            ptr += 1 + sum(frombytes_lenat(b, ptr))
            tv = frombytes_tvat(b, ptr)
            ptr += 1 + sum(frombytes_lenat(b, ptr))
            self.varbinds[oid] = tv
        for arg in kwargs:
            if hasattr(self, arg):
                setattr(self, arg, kwargs[arg])

    def tobytes(self):
        b = bytes()
        for oid in self.varbinds:
            if self.varbinds[oid] == None:
                t,v = ASN1_NULL, None
            else:
                t,v = self.varbinds[oid]
            b += tobytes_tv(ASN1_SEQ, tobytes_tv(ASN1_OID, oid) + tobytes_tv(t,v))
        b = tobytes_tv(ASN1_SEQ, b)
        if self.type == SNMP_TRAP:
            b = tobytes_tv(ASN1_OID, self.enterprise) \
                + tobytes_tv(SNMP_IPADDR, self.agent_addr) \
                + tobytes_tv(ASN1_INT, self.generic_trap) \
                + tobytes_tv(ASN1_INT, self.specific_trap) \
                + tobytes_tv(SNMP_TIMETICKS, self.timestamp) \
                + b
        else:
            b = tobytes_tv(ASN1_INT, self.id) \
                + tobytes_tv(ASN1_INT, self.err_status) \
                + tobytes_tv(ASN1_INT, self.err_id) \
                + b
        return tobytes_tv(ASN1_SEQ, tobytes_tv(ASN1_INT, self.ver) \
                + tobytes_tv(ASN1_OCTSTR, self.community) \
                + tobytes_tv(self.type, b))

    def _frombytes_props(self, b, ptr, properties):
        for prop in properties:
            setattr(self, prop, frombytes_tvat(b, ptr)[1])
            ptr += 1 + sum(frombytes_lenat(b, ptr))
        return ptr
