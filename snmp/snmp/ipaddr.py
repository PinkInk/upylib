from asn1der import *

TypeNames.extend([
        'IPAddr',
    ])

TypeCodes.extend([
        0x40,
    ])


def tlv_v_to_ipaddr(b):
    ptr = 1 + from_bytes_lenat(b, 0)[1]
    v = ''
    while ptr < len(b):
        v += '.' + str(b[ptr]) if v!='' else str(b[ptr])
        ptr += 1
    return bytes(v, 'utf-8')

class SnmpIPAddr(Asn1DerBaseClass, bytes):
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


TypeClasses.extend([
        SnmpIPAddr,
    ])
