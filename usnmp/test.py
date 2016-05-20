import ubinascii, gc, usnmp

#getresponse
s="3081d20201000403414643a281c702043821eea10201000201003081b8300f060a2b0601020102020101010201013013060a2b0601020102020102010405566c616e31300f060a2b0601020102020103010201353010060a2b060102010202010401020205dc3012060a2b06010201020201050142043b9aca003014060a2b0601020102020106010406001b8ff4d1c0300f060a2b060102010202010701020102300f060a2b0601020102020108010201023010060a2b06010201020201090143022c06300f060a2b060102010202010a01410100"

b=bytes(ubinascii.unhexlify(s))

usnmp.frombytes_tvat(b,0)
usnmp.frombytes_tvat(b,3)
usnmp.frombytes_tvat(b,6)
usnmp.frombytes_tvat(b,11)
usnmp.frombytes_tvat(b,14)
usnmp.frombytes_tvat(b,20)
usnmp.frombytes_tvat(b,23)
usnmp.frombytes_tvat(b,26)

usnmp.tobytes_tv(4, "hello world")
usnmp.frombytes_tvat(usnmp.tobytes_tv(4, b"hello world"),0)

usnmp.frombytes_tvat(usnmp.tobytes_tv(usnmp.ASN1_INT,12311),0)[1] == 12311
usnmp.frombytes_tvat(usnmp.tobytes_tv(usnmp.SNMP_GUAGE,23),0)[1] == 23
usnmp.frombytes_tvat(usnmp.tobytes_tv(usnmp.SNMP_TIMETICKS,65783634),0)[1] == 65783634
usnmp.frombytes_tvat(usnmp.tobytes_tv(usnmp.ASN1_NULL,None),0)[1] == None
usnmp.frombytes_tvat(usnmp.tobytes_tv(usnmp.ASN1_OID,"1.3.1.2.2.4324.2"),0)[1] == "1.3.1.2.2.4324.2"
usnmp.frombytes_tvat(usnmp.tobytes_tv(usnmp.SNMP_IPADDR,"172.26.235.23"),0)[1] == "172.26.235.23"

p = usnmp.SnmpPacket(b)
p.ver
p.community
p.type
p.id
p.err_status
p.err_id
p.varbinds["1.3.6.1.2.1.2.2.1.4.1"]
for oid in p.varbinds: print(oid, p.varbinds[oid])

p.varbinds["1.3.6.1.2.1.2.2.1.1.1"]=usnmp.ASN1_INT,23
del(p.varbinds["1.3.6.1.2.1.2.2.1.4.1"])
try:
    p.varbinds["1.3.6.1.2.1.2.2.1.4.1"]
except KeyError:
    print("Deleted!")

for oid in p.varbinds: print(oid, p.varbinds[oid])

p.varbinds["1.3.6.1.2.1.2.2.1.2.1"] = (usnmp.ASN1_OCTSTR, "vlan23")
p.varbinds["1.3.6.1.2.1.2.2.1.2.1"]

p.varbinds["1.3.6.1.2.1.2.2.1.4.1"] = (usnmp.ASN1_INT, 23232)
p.varbinds["1.3.6.1.2.1.2.2.1.4.1"]

p.varbinds["1.3.6.1.2.1.2.2.1.11.1"] = (usnmp.ASN1_INT, 23232)
p.varbinds["1.3.6.1.2.1.2.2.1.11.1"]

p.tobytes()
p1 = usnmp.SnmpPacket( p.tobytes() )
p1.community
p1.id
for i in p1.varbinds: print(i, p1.varbinds[i])

#trap
s="303b02010004067075626c6963a42e06092b0601040181f4690040047f000001020100020100430400000000300f300d06082b06010201020100020121"
b=bytes(ubinascii.unhexlify(s))

t=usnmp.SnmpPacket(b)
t.enterprise
t.agent_addr
t.generic_trap
t.specific_trap
t.timestamp
for i in t.varbinds: print(i, t.varbinds[i])

t1=usnmp.SnmpPacket(type=usnmp.SNMP_TRAP)
t1.ver
t1.community
t1.enterprise
t1.agent_addr

t=usnmp.SnmpPacket(type=usnmp.SNMP_GETREQUEST)
t.varbinds['1.3.6.1.2.1.3.1.1.1.453.13576.1.192.168.1.133']=usnmp.ASN1_OCTSTR,"Gotcha!"
t.varbinds['1.3.6.1.2.1.3.1.1.1.453.13576.1.192.168.1.133']

#single item get-request
s="30260201000403414643a01c020433783ac0020100020100300e300c06082b060102010101000500"
a=bytes(ubinascii.unhexlify(s))
b=usnmp.SnmpPacket(a)
a==b.tobytes()
b.ver, b.community, b.type
for i in b.varbinds: print(i, b.varbinds[i])

#single item get-response, long string
s="3081ea0201000403414643a281df020433783ac00201000201003081d03081cd06082b060102010101000481c0436973636f20494f5320536f6674776172652c20433337353020536f667477617265202843333735302d414456495053455256494345534b392d4d292c2056657273696f6e2031322e322834362953452c2052454c4541534520534f4654574152452028666332290d0a436f707972696768742028632920313938362d3230303820627920436973636f2053797374656d732c20496e632e0d0a436f6d70696c6564205468752032312d4175672d30382031353a3433206279206e616368656e"
a=bytes(ubinascii.unhexlify(s))
b=usnmp.SnmpPacket(a)
a==b.tobytes()
b.ver, b.community, b.type
for i in b.varbinds: print(i, b.varbinds[i])

#single item get-response, OID
s="302f0201000403414643a225020433783ac30201000201003017301506082b0601020101020006092b0601040109018404"
a=bytes(ubinascii.unhexlify(s))
b=usnmp.SnmpPacket(a)
a==b.tobytes()
b.ver, b.community, b.type
for i in b.varbinds: print(i, b.varbinds[i])

#single item get-response, timeticks
s="302a0201000403414643a220020433783ac60201000201003012301006082b06010201010300430415f8605a"
a=bytes(ubinascii.unhexlify(s))
b=usnmp.SnmpPacket(a)
a==b.tobytes()
b.ver, b.community, b.type
for i in b.varbinds: print(i, b.varbinds[i])

#multi item get-response (response to prior get-next-request)
s="3081d20201000403414643a281c702043821eea10201000201003081b8300f060a2b0601020102020101010201013013060a2b0601020102020102010405566c616e31300f060a2b0601020102020103010201353010060a2b060102010202010401020205dc3012060a2b06010201020201050142043b9aca003014060a2b0601020102020106010406001b8ff4d1c0300f060a2b060102010202010701020102300f060a2b0601020102020108010201023010060a2b06010201020201090143022c06300f060a2b060102010202010a01410100"
a=bytes(ubinascii.unhexlify(s))
b=usnmp.SnmpPacket(a)
a==b.tobytes()
b.ver, b.community, b.type
for i in b.varbinds: print(i, b.varbinds[i])

#multi item get-next-request
s="3081b00201000403414643a181a5020433783ac9020100020100308196300d06092b06010201020201010500300d06092b06010201020201020500300d06092b06010201020201030500300d06092b06010201020201040500300d06092b06010201020201050500300d06092b06010201020201060500300d06092b06010201020201070500300d06092b06010201020201080500300d06092b06010201020201090500300d06092b060102010202010a0500"
a=bytes(ubinascii.unhexlify(s))
b=usnmp.SnmpPacket(a)
a==b.tobytes()
b.ver, b.community, b.type
for i in b.varbinds: print(i, b.varbinds[i])

#simple trap, with odd timestamp encoding of 0
s="303b02010004067075626c6963a42e06092b0601040181f4690040047f000001020100020100430400000000300f300d06082b06010201020100020121"
a=bytes(ubinascii.unhexlify(s))
b=usnmp.SnmpPacket(a)
a==b.tobytes() #fails due to unnecessary 3 byte 0x00,0x00,0x00 encoding of timestamp in source packet
b.ver, b.community, b.type
for i in b.varbinds: print(i, b.varbinds[i])

s="303202010004067075626c6963a4250601004004c0a80177020102020100430264003010300e06092b0601020102020101020103"
a=bytes(ubinascii.unhexlify(s))
b=usnmp.SnmpPacket(a)
a==b.tobytes()
b.ver, b.community, b.type
for i in b.varbinds: print(i, b.varbinds[i])

#problem packet, with long OID that doesn't seek
s='303702010004067075626c6963a22a020100020100020100301f301d06152b060102010301010182c5ea1c018140812801810902047fff6310'
a=bytes(ubinascii.unhexlify(s))
b=usnmp.SnmpPacket(a)
a==b.tobytes()
b.ver, b.community, b.type
for i in b.varbinds: print(i, b.varbinds[i])

import socket
s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.settimeout(1)

p=usnmp.SnmpPacket(community="public", type=usnmp.SNMP_GETREQUEST)
vbs=["1.3.6.1.2.1.2.2.1.10.4", "1.3.6.1.2.1.2.2.1.16.4", "1.3.6.1.2.1.1.3.0"]
for vb in vbs:
    p.varbinds[vb] = (usnmp.ASN1_NULL, None)

s.sendto(p.tobytes(), (b"192.168.1.1", 161))
d=s.recvfrom(1024)
r=usnmp.SnmpPacket(d[0])
print(r.community)
print(r.ver)
for oid in r.varbinds:
    print(oid, r.varbinds[oid])

r=usnmp.SnmpPacket(community="public", type=usnmp.SNMP_GETNEXTREQUEST)
rsize=2048
oid = "1.3.6.1.2.1.1.1"
r.varbinds[oid]=(usnmp.ASN1_NULL,None)
s.sendto(r.tobytes(), (b'192.168.1.1',161))
d=s.recvfrom(rsize)
while True:
    gc.collect()
    r=usnmp.SnmpPacket(d[0])
    try:
        r.varbinds[oid]
    except KeyError:
        pass
    for oid in r.varbinds:
        print(oid, r.varbinds[oid])
    r.type=usnmp.SNMP_GETNEXTREQUEST
    s.sendto(r.tobytes(), (b'192.168.1.1',161))
    d=s.recvfrom(rsize)
