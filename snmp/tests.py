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

a11 = snmp.SnmpVarBinds()
a11[snmp.Asn1DerOid(b'1.3.1.2.2.1.3.1')] = snmp.SnmpCounter(23)
a11[snmp.Asn1DerOid(b'1.3.1.2.2.1.3.2')] = snmp.SnmpGuage(5346346)
a11.to_bytes()
snmp.SnmpVarBinds.from_bytes( a11.to_bytes() )

a=OrderedDict()
a['a']=23
a['b']=25
b=OrderedDict()
b['a']=23
b['b']=25
a==b assert 'micropython not patched'

b=b"0?\x02\x01\x00\x04\x06public\xa22\x02\x01\x00\x02\x01\x00\x02\x01\x000'0\x13\x06\n+\x06\x01\x02\x01\x02\x02\x01\n\x06A\x05\x00\xe0\x0f\xfd\x950\x10\x06\x08+\x06\x01\x02\x01\x01\x03\x00C\x04\x01\x0f|\x9a"
c=snmp.decode(b)
assert type(c[0][2]) == snmp.SnmpGetResponse, 'decoded as wrong type'

import utime
a10 = snmp.SnmpGetRequest()
a.id = utime.ticks_us()
a10.varbinds.append(snmp.Asn1DerSeq([snmp.Asn1DerOid(b'1.3.1.2.2.1.12.1'), snmp.Asn1DerNull()]))
a10.varbinds.append(snmp.Asn1DerSeq([snmp.Asn1DerOid(b'1.3.1.2.2.1.12.2'), snmp.Asn1DerNull()]))
