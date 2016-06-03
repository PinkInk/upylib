import asn1der

v1 = 235235
a1 = asn1der.Asn1DerInt(v1)
assert type(a1) == asn1der.Asn1DerInt, 'incorrect type'
assert v1 == asn1der.Asn1DerInt.from_bytes( a1.to_bytes() ), 'wrong value'

v2 = '1.3.1.2.2.1.234.746344.1.22'
a2 = asn1der.Asn1DerOid(v2)
assert type(a2) == asn1der.Asn1DerOid, 'incorrect type'
#why need to convert string?
assert v2 == str(asn1der.Asn1DerOid.from_bytes( a2.to_bytes())), 'wrong value'
#assert v2 == asn1der.Asn1DerOid.from_bytes( a2.to_bytes()), 'wrong value'

v3 = b'hello world'
a3 = asn1der.Asn1DerOctStr(v3)
assert type(a3) == asn1der.Asn1DerOctStr, 'incorrect type'
assert v3 == asn1der.Asn1DerOctStr.from_bytes( a3.to_bytes()), 'wrong value'

a4 = asn1der.Asn1DerNull()
assert a4 is asn1der.Asn1DerNull, 'not a Null'
asn1der.Asn1DerNull.from_bytes( a4.to_bytes())

v5 = [a1, a2, a3, a4]
a5 = asn1der.Asn1DerSeq(v5)
assert type(a5) == asn1der.Asn1DerSeq, 'incorrect type'
assert v5 == asn1der.Asn1DerSeq.from_bytes( a5.to_bytes() ), 'fails because subclasses of str do not compare'

v6 = a5.to_bytes() + a4.to_bytes() + a3.to_bytes() + a2.to_bytes() + a1.to_bytes()
a6 = asn1der.decode(v6)
assert a6[0] == a5, 'fails because subclasses of str do not compare'
assert a6[1] == a4, 'incorrect item'
assert a6[2] == a3, 'incorrect item'
#why need to convert string?
assert a6[3] == a2, 'fails because subclasses of str do not compare'
assert str(a6[3]) == str(a2), 'incorrect item'
assert a6[4] == a1, 'incorrect item'

import snmp

v7 = b'172.26.236.1'
a7 = snmp.SnmpIPAddr(v7)
assert type(a7) == snmp.SnmpIPAddr, 'incorrect type'
assert v7 == snmp.SnmpIPAddr.from_bytes( a7.to_bytes() ), 'wrong value'

v8 = 673633462
a8 = snmp.SnmpCounter(v8)
assert type(a8) == snmp.SnmpCounter, 'incorrect type'
assert v8 == snmp.SnmpCounter.from_bytes( a8.to_bytes() ), 'wrong value'

v9 = 255
a9 = snmp.SnmpGuage(v9)
assert type(a9) == snmp.SnmpGuage, 'incorrect type'
assert v9 == snmp.SnmpGuage.from_bytes( a9.to_bytes() ), 'wrong value'

v10 = 96782
a10 = snmp.SnmpTimeTicks(v10)
assert type(a10) == snmp.SnmpTimeTicks, 'incorrect type'
assert v10 == snmp.SnmpTimeTicks.from_bytes( a10.to_bytes() ), 'wrong value'

import utime
a10 = snmp.SnmpGetRequest()
a.id = utime.ticks_us()
a10.varbinds.append(snmp.Asn1DerSeq([snmp.Asn1DerOid(b'1.3.1.2.2.1.12.1'), snmp.Asn1DerNull()]))
a10.varbinds.append(snmp.Asn1DerSeq([snmp.Asn1DerOid(b'1.3.1.2.2.1.12.2'), snmp.Asn1DerNull()]))
