import ASN1
import varbinds

b=ASN1.tobytes_tv(ASN1.SEQ, ASN1.tobytes_tv(ASN1.OID,"1.3.1.2.1.2.3.23432.1.1") + ASN1.tobytes_tv(ASN1.NULL,None))
b=b+ASN1.tobytes_tv(ASN1.SEQ, ASN1.tobytes_tv(ASN1.OID,"1.3.1.2.1.2.3.23432.2.1") + ASN1.tobytes_tv(ASN1.INT,2342334))
b=ASN1.tobytes_tv(ASN1.SEQ, b)

v=varbinds.VarBinds(b)
