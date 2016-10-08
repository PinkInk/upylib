try:
    from ucollections import OrderedDict
except:
    try:
        from collections import OrderedDict
    except:
        pass

from usnmp_codec import *

_SNMP_PROPS = ('ver', 'community')
_SNMP_TRAP_PROPS = ('enterprise', 'agent_addr', 'generic_trap', 'specific_trap', 'timestamp')
_SNMP_GETSET_PROPS = ('id', 'err_status', 'err_id')
#packet templates, refer utils/template.py
_SNMP_GETSET_TEMPL = b'0\x14\x02\x00\x04\x06public\xa0\x08\x02\x00\x02\x00\x02\x000\x00'
_SNMP_TRAP_TEMPL = b'0%\x02\x01\x00\x04\x06public\xa4\x18\x06\x05+\x06\x01\x04\x01@\x04\x7f\x00\x00\x01\x02\x01\x00\x02\x01\x00C\x01\x000\x00' 

class SnmpPacket:

    def __init__(self, *args, **kwargs):
        if len(args) == 1 and type(args[0]) in (bytes, bytearray, memoryview):
            b = memoryview(args[0])
        elif 'type' in kwargs:
            if kwargs['type'] == SNMP_TRAP:
                b = memoryview(_SNMP_TRAP_TEMPL)
            else:
                b = memoryview(_SNMP_GETSET_TEMPL)
        else:
            raise ValueError('buffer or type=x required')
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
