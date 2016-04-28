import binascii
s="303b02010004067075626c6963a42e06092b0601040181f4690040047f000001020100020100430400000000300f300d06082b06010201020100020121"
b=bytes(binascii.unhexlify(s))

import usnmp
usnmp.unpack(b)

import usnmp2
a=usnmp2.SnmpPacket(b)

assert len(a) == len(b), "incorrectly reporting packet length"
a._get_payloadat(2)
a._get_payloadat(5)
a._get_payloadat(13)
a._get_payloadat(15)
a._get_payloadat(26)
usnmp.unpack(bytes(a))
bytes(a) == b
usnmp.unpack(b) == usnmp.unpack(b)

a._buf_extend(62)
len(a)
len(a._b)
a._buf_extend(65)
len(a)
len(a._b)

a._get_payloadat(3) #should raise exception

a._buf_extend(62)
len(a)
len(a._b)
a._buf_extend(129)
len(a)
len(a._b)

a._replaceat(0,0,b'hello world')