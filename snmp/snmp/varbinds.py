from asn1der import *
from ucollections import OrderedDict


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
