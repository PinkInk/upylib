import usnmp

t_names = bytearray()
name_ptr = 0
t_oids = bytearray()
oid_ptr = 0

f=open("mib2.csv","r")

l=f.readline()
while l != "":
    c = l.split(",")
    b_name = usnmp.tobytes_tv(usnmp.ASN1_OCTSTR, c[0])
    b_oid = usnmp.tobytes_tv(usnmp.ASN1_OID, c[1])
    b_type = usnmp.tobytes_tv(usnmp.ASN1_INT, int(c[2]))
    b_flags = usnmp.tobytes_tv(usnmp.ASN1_INT, int(c[3]) + (int(c[4])<<1) + (int(c[5])<<2) + (int(c[6])<<3))
    b_c_name = usnmp.tobytes_tv(usnmp.ASN1_SEQ, b_name + usnmp.tobytes_tv(usnmp.ASN1_INT, oid_ptr))
    b_c_oid = usnmp.tobytes_tv(usnmp.ASN1_SEQ, b_oid + b_type + b_flags + usnmp.tobytes_tv(usnmp.ASN1_INT, name_ptr))
    t_names += b_c_name
    t_oids += b_c_oid
    name_ptr += len(b_c_name)
    oid_ptr += len(b_c_oid)
    l = f.readline()

f.close()
