from asn1der import *

TypeNames.extend(['Counter', 'Guage', 'TimeTicks'])
TypeCodes.extend([0x41, 0x42, 0x43])


class SnmpCounter(Asn1DerInt):    
    der_type = TypeCodes[TypeNames.index('Counter')]
    
    @staticmethod
    def frombytes(b, t=TypeCodes[TypeNames.index('Counter')]):
        return super().frombytes(b, t=t)


class SnmpGuage(Asn1DerInt):    
    der_type = TypeCodes[TypeNames.index('Guage')]
    
    @staticmethod
    def frombytes(b, t=TypeCodes[TypeNames.index('Guage')]):
        return super().frombytes(b, t=t)


class SnmpTimeTicks(Asn1DerInt):    
    der_type = TypeCodes[TypeNames.index('TimeTicks')]
    
    @staticmethod
    def frombytes(b, t=TypeCodes[TypeNames.index('TimeTicks')]):
        return super().frombytes(b, t=t)

#b'B\x03#\xe2O'

TypeClasses.extend([SnmpCounter, SnmpGuage, SnmpTimeTicks])