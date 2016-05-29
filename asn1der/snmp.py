from asn1der import *

TypeNames.extend(['Counter', 'Guage', 'TimeTicks'])
TypeCodes.extend([0x41, 0x42, 0x43])


class SnmpCounter(Asn1DerInt):    
    der_type = TypeCodes[TypeNames.index('Counter')]
    
    @staticmethod
    def frombytes(b, t=TypeCodes[TypeNames.index('Counter')]):
        if b[0] != t:
            raise ValueError('expected type ' + str(t) + ' got', b[0])
        ptr = 1+frombytes_lenat(b,0)[1]
        return SnmpCounter(int.from_bytes(b[ptr:]))


class SnmpGuage(Asn1DerInt):    
    der_type = TypeCodes[TypeNames.index('Guage')]
    
    @staticmethod
    def frombytes(b, t=TypeCodes[TypeNames.index('Guage')]):
        if b[0] != t:
            raise ValueError('expected type ' + str(t) + ' got', b[0])
        ptr = 1+frombytes_lenat(b,0)[1]
        return SnmpGuage(int.from_bytes(b[ptr:]))


class SnmpTimeTicks(Asn1DerInt):    
    der_type = TypeCodes[TypeNames.index('TimeTicks')]
    
    @staticmethod
    def frombytes(b, t=TypeCodes[TypeNames.index('TimeTicks')]):
        if b[0] != t:
            raise ValueError('expected type ' + str(t) + ' got', b[0])
        ptr = 1+frombytes_lenat(b,0)[1]
        return SnmpTimeTicks(int.from_bytes(b[ptr:]))


TypeClasses.extend([SnmpCounter, SnmpGuage, SnmpTimeTicks])