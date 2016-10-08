#construct compiled template packets used in main module

import usnmp
import binascii

# SEQ
#   INT version = SNMP_VER1
#   STR community = "public"
#   TYPE [get|set] = SNMP_GETREQUEST
#       INT request_id = 0
#       INT error status = 0
#       INT error index = 0
#       SEQ 
#           of variable binding = empty
gs = usnmp.tobytes_tv(usnmp.ASN1_SEQ, b'')
gs = usnmp.tobytes_tv(usnmp.ASN1_INT, 0) + \
        usnmp.tobytes_tv(usnmp.ASN1_INT, 0) + \
        usnmp.tobytes_tv(usnmp.ASN1_INT, 0) + gs 
gs = usnmp.tobytes_tv(usnmp.SNMP_GETREQUEST, gs)
gs = usnmp.tobytes_tv(usnmp.ASN1_INT, usnmp.SNMP_VER1) + \
        usnmp.tobytes_tv(usnmp.ASN1_OCTSTR, "public") + gs
gs = usnmp.tobytes_tv(usnmp.ASN1_SEQ, gs)
gs
binascii.hexlify(gs)

# SEQ
#   INT version = SNMP_VER1
#   STR community = "public"
#   TYPE [trap] = SNMP_TRAP
#       OID enterprise oid = "1.3.6.1.4.1" (root of enterprise oid's)
#       IP ip address = 127.0.0.1
#       INT trap generic type = 0
#       INT trap specific type = 0
#       TIME time = 0
#       SEQ
#           of variable bindings
trap = usnmp.tobytes_tv(usnmp.ASN1_SEQ, b'')
trap = usnmp.tobytes_tv(usnmp.ASN1_OID, "1.3.6.1.4.1") + \
        usnmp.tobytes_tv(usnmp.SNMP_IPADDR, "127.0.0.1") + \
        usnmp.tobytes_tv(usnmp.ASN1_INT, 0) + \
        usnmp.tobytes_tv(usnmp.ASN1_INT, 0) + \
        usnmp.tobytes_tv(usnmp.SNMP_TIMETICKS, 0) + trap
trap = usnmp.tobytes_tv(usnmp.SNMP_TRAP, trap)
trap = usnmp.tobytes_tv(usnmp.ASN1_INT, usnmp.SNMP_VER1) + \
        usnmp.tobytes_tv(usnmp.ASN1_OCTSTR, "public") + trap
trap = usnmp.tobytes_tv(usnmp.ASN1_SEQ, trap)
trap
binascii.hexlify(trap)