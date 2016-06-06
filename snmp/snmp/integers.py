from asn1der import *

TypeNames.extend([
        'Counter',
        'Guage',
        'TimeTicks',
    ])

TypeCodes.extend([
        0x41,
        0x42,
        0x43,
    ])


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
        SnmpCounter,
        SnmpGuage,
        SnmpTimeTicks,
    ])
