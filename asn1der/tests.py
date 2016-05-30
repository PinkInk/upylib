import asn1der

v1 = 235235
a1 = asn1der.Asn1DerInt(v1)
assert type(a1) == asn1der.Asn1DerInt, 'incorrect type'
assert v1 == asn1der.Asn1DerInt.frombytes( a1.tobytes() ), 'wrong value'

v2 = '1.3.1.2.2.1.234.746344.1.22'
a2 = asn1der.Asn1DerOid(v2)
assert type(a2) == asn1der.Asn1DerOid, 'incorrect type'
#why need to convert string?
assert v2 == str(asn1der.Asn1DerOid.frombytes( a2.tobytes())), 'wrong value'

v3 = b'hello world'
a3 = asn1der.Asn1DerOctStr(v3)
assert type(a3) == asn1der.Asn1DerOctStr, 'incorrect type'
assert v3 == asn1der.Asn1DerOctStr.frombytes( a3.tobytes()), 'wrong value'

v4 = None 
a4 = asn1der.Asn1DerNull(v4)
assert type(a4) == asn1der.Asn1DerNull, 'incorrect type'
asn1der.Asn1DerNull.frombytes( a4.tobytes())

v5 = [a1, a2, a3, a4]
a5 = asn1der.Asn1DerSeq(v5)
assert type(a5) == asn1der.Asn1DerSeq, 'incorrect type'
assert v5 == asn1der.Asn1DerSeq.frombytes( a5.tobytes() ), 'fails because Asn1DerNull is not a Singleton'

v6 = a5.tobytes() + a4.tobytes() + a3.tobytes() + a2.tobytes() + a1.tobytes()
a6 = asn1der.decode(v6)
assert a6[0] == a5, 'fails because Asn1DerNull is not a Singleton'
assert a6[1] == a4, 'fails because Asn1DerNull is not a Singleton'
assert a6[2] == a3, 'incorrect item'
#why need to convert string?
assert str(a6[3]) == str(a2), 'incorrect item'
assert a6[4] == a1, 'incorrect item'

import snmp

v7 = '172.26.236.1'
a7 = snmp.SnmpIPAddr(v7)
assert type(a7) == snmp.SnmpIPAddr, 'incorrect type'
#why need to convert string
assert v7 == str(snmp.SnmpIPAddr.frombytes( a7.tobytes() )), 'wrong value'

v8 = 673633462
a8 = snmp.SnmpCounter(v8)
assert type(a8) == snmp.SnmpCounter, 'incorrect type'
assert v8 == snmp.SnmpCounter.frombytes( a8.tobytes() ), 'wrong value'

v9 = 255
a9 = snmp.SnmpGuage(v9)
assert type(a9) == snmp.SnmpGuage, 'incorrect type'
assert v9 == snmp.SnmpGuage.frombytes( a9.tobytes() ), 'wrong value'

v10 = 96782
a10 = snmp.SnmpTimeTicks(v10)
assert type(a10) == snmp.SnmpTimeTicks, 'incorrect type'
assert v10 == snmp.SnmpTimeTicks.frombytes( a10.tobytes() ), 'wrong value'

