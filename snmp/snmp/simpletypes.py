from asn1der import *

TypeNames.extend([
        'IPAddr',
        'Counter',
        'Guage',
        'TimeTicks',
    ])

TypeCodes.extend([
        0x40,
        0x41,
        0x42,
        0x43,
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


TypeClasses.extend([
        SnmpIPAddr,
        SnmpCounter,
        SnmpGuage,
        SnmpTimeTicks,
    ])
