import binascii
#trap
s="303b02010004067075626c6963a42e06092b0601040181f4690040047f000001020100020100430400000000300f300d06082b06010201020100020121"
#getrequest
s="3081b00201000403414643a181a5020433783ac9020100020100308196300d06092b06010201020201010500300d06092b06010201020201020500300d06092b06010201020201030500300d06092b06010201020201040500300d06092b06010201020201050500300d06092b06010201020201060500300d06092b06010201020201070500300d06092b06010201020201080500300d06092b06010201020201090500300d06092b060102010202010a0500"
#getresponse
s="3081d20201000403414643a281c702043821eea10201000201003081b8300f060a2b0601020102020101010201013013060a2b0601020102020102010405566c616e31300f060a2b0601020102020103010201353010060a2b060102010202010401020205dc3012060a2b06010201020201050142043b9aca003014060a2b0601020102020106010406001b8ff4d1c0300f060a2b060102010202010701020102300f060a2b0601020102020108010201023010060a2b06010201020201090143022c06300f060a2b060102010202010a01410100"

b=bytes(binascii.unhexlify(s))

import usnmp2
usnmp2.frombytes_tvat(b,0)
usnmp2.frombytes_tvat(b,3)
usnmp2.frombytes_tvat(b,6)
usnmp2.frombytes_tvat(b,11)
usnmp2.frombytes_tvat(b,14)
usnmp2.frombytes_tvat(b,20)
usnmp2.frombytes_tvat(b,23)
usnmp2.frombytes_tvat(b,26)

usnmp2.tobytes_tv(4, "hello world")
usnmp2.frombytes_tvat(usnmp2.tobytes_tv(4, b"hello world""),0)

usnmp2.frombytes_tvat(usnmp2.tobytes_tv(usnmp2.ASN1_INT,12311),0)[1] == 12311 
usnmp2.frombytes_tvat(usnmp2.tobytes_tv(usnmp2.SNMP_GUAGE,23),0)[1] == 23 
usnmp2.frombytes_tvat(usnmp2.tobytes_tv(usnmp2.SNMP_TIMETICKS,65783634),0)[1] == 65783634 
usnmp2.frombytes_tvat(usnmp2.tobytes_tv(usnmp2.ASN1_NULL,None),0)[1] == None 
usnmp2.frombytes_tvat(usnmp2.tobytes_tv(usnmp2.ASN1_OID,"1.3.1.2.2.4324.2"),0)[1] == "1.3.1.2.2.4324.2" 
usnmp2.frombytes_tvat(usnmp2.tobytes_tv(usnmp2.SNMP_IPADDR,"172.26.235.23"),0)[1] == "172.26.235.23" 

p = usnmp2.SnmpPacket(b)
p.ver
p.community
p.type
p.req_id
p.err_stat
p.err_id
p.varbinds["1.3.6.1.2.1.2.2.1.4.1"]
for oid in p.varbinds:
    print(oid, p.varbinds[oid])

del(p.varbinds["1.3.6.1.2.1.2.2.1.4.1"])
try:
    p.varbinds["1.3.6.1.2.1.2.2.1.4.1"]
except KeyError:
    print("Deleted!")

for oid in p.varbinds:
    print(oid, p.varbinds[oid])

p.varbinds["1.3.6.1.2.1.2.2.1.4.1"] = (usnmp2.ASN1_INT, 23232)

