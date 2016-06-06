from asn1der import *
from snmp.integers import *
from snmp.varbinds import *

TypeNames.extend([
        'GetRequest',
        'GetNextRequest',
        'GetResponse',
        'SetRequest',
    ])

TypeCodes.extend([
        0xa0,
        0xa1,
        0xa2,
        0xa3,
    ])


_SnmpGetSetTemplate = [
    Asn1DerInt(0),          #request_id
    Asn1DerInt(0),          #error_status
    Asn1DerInt(0),          #error_id
    SnmpVarBinds({})        #variable_bindings
]

class _SnmpGetSetBaseClass(Asn1DerSeq):

    def __init__(self):
        if len(self) == 0: #no args
            for i in _SnmpGetSetTemplate:
                self.append(i)
        else: #args, validate
            for i,j in enumerate(self):
                if type(j) != type(_SnmpGetSetTemplate[i]):
                    raise ValueError('invalid initialisation data')
        self.varbinds = self[3] #expose object directly

    def id(self, id=None):
        if id == None:
            return self[0]
        else:
            if type(id) is Asn1DerInt:
                self[0] = id
            else:
                raise ValueError('expected an Asn1DerInt')

    def err_status(self, err_status=None):
        if err_status == None:
            return self[1]
        else:
            if type(err_status) is Asn1DerInt:
                self[1] = err_status
            else:
                raise ValueError('expected an Asn1DerInt')

    def err_id(self, err_id=None):
        if err_id == None:
            return self[2]
        else:
            if type(err_id) is Asn1DerInt:
                self[2] = err_id
            else:
                raise ValueError('expected an Asn1DerInt')


class SnmpGetRequest(_SnmpGetSetBaseClass):
    typecode = typecode_for_type('GetRequest')

    @staticmethod
    def frombytes(b, t=typecode_for_type('GetRequest')):
        check_typecode(b[0], t)
        return SnmpGetNextRequest( tlv_v_to_seq(b) )


class SnmpGetNextRequest(_SnmpGetSetBaseClass):
    typecode = typecode_for_type('GetNextRequest')

    @staticmethod
    def frombytes(b, t=typecode_for_type('GetNextRequest')):
        check_typecode(b[0], t)
        return SnmpGetNextRequest( tlv_v_to_seq(b) )


class SnmpGetResponse(_SnmpGetSetBaseClass):
    typecode = typecode_for_type('GetResponse')

    @staticmethod
    def frombytes(b, t=typecode_for_type('GetResponse')):
        check_typecode(b[0], t)
        return SnmpGetNextRequest( tlv_v_to_seq(b) )


class SnmpSetRequest(_SnmpGetSetBaseClass):
    typecode = typecode_for_type('SetRequest')

    @staticmethod
    def frombytes(b, t=typecode_for_type('SetRequest')):
        check_typecode(b[0], t)
        return SnmpSetRequest( tlv_v_to_seq(b) )


TypeClasses.extend([
        SnmpGetRequest,
        SnmpGetNextRequest,
        SnmpGetResponse,
        SnmpSetRequest,
    ])
