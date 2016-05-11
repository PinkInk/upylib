import binascii
s="3081b00201000403414643a181a5020433783ac9020100020100308196300d06092b06010201020201010500300d06092b06010201020201020500300d06092b06010201020201030500300d06092b06010201020201040500300d06092b06010201020201050500300d06092b06010201020201060500300d06092b06010201020201070500300d06092b06010201020201080500300d06092b06010201020201090500300d06092b060102010202010a0500"
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

usnmp2.tobytes_tv(4, 'hello world')
usnmp2.frombytes_tvat(usnmp2.tobytes_tv(4, b'hello world'),0)

usnmp2.frombytes_tvat(usnmp2.tobytes_tv(usnmp2.ASN1_INT,12311),0)[1] == 12311 
usnmp2.frombytes_tvat(usnmp2.tobytes_tv(usnmp2.SNMP_GUAGE,23),0)[1] == 23 
usnmp2.frombytes_tvat(usnmp2.tobytes_tv(usnmp2.SNMP_TIMETICKS,65783634),0)[1] == 65783634 
usnmp2.frombytes_tvat(usnmp2.tobytes_tv(usnmp2.ASN1_NULL,None),0)[1] == None 
usnmp2.frombytes_tvat(usnmp2.tobytes_tv(usnmp2.ASN1_OID,"1.3.1.2.2.4324.2"),0)[1] == "1.3.1.2.2.4324.2" 
usnmp2.frombytes_tvat(usnmp2.tobytes_tv(usnmp2.SNMP_IPADDR,"172.26.235.23"),0)[1] == "172.26.235.23" 
