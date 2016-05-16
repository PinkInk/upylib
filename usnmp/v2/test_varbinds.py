import ASN1
import varbinds

b=ASN1.tobytes_tv(ASN1.SEQ, ASN1.tobytes_tv(ASN1.OID,"1.3.1.2.1.2.3.5435.1.1") + ASN1.tobytes_tv(ASN1.NULL,None))
b=b+ASN1.tobytes_tv(ASN1.SEQ, ASN1.tobytes_tv(ASN1.OID,"1.3.1.2.1.2.3.5435.2.1") + ASN1.tobytes_tv(ASN1.INT,2342334))

t=varbinds.VarBinds(b)
for i in t: print(i, t[i])

