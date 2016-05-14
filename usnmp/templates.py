#construct compiled template packets used in main module

from usnmp import *
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
gs = tobytes_tv(ASN1_SEQ, b'')
gs = tobytes_tv(ASN1_INT, 0) + \
        tobytes_tv(ASN1_INT, 0) + \
        tobytes_tv(ASN1_INT, 0) + gs 
gs = tobytes_tv(SNMP_GETREQUEST, gs)
gs = tobytes_tv(ASN1_INT, SNMP_VER1) + \
        tobytes_tv(ASN1_OCTSTR, "public") + gs
gs = tobytes_tv(ASN1_SEQ, gs)
gs
binascii.hexlify(gs)

# SEQ
#   INT version = SNMP_VER1
#   STR community = "public"
#   TYPE [trap] = SNMP_TRAP
#       OID enterprise oid = "1.3.6.1.4"
#       IP ip address = 127.0.0.1
#       INT trap generic type = 0
#       INT trap specific type = 0
#       TIME time = 0
#       SEQ
#           of variable bindings
trap = tobytes_tv(ASN1_SEQ, b'')
trap = tobytes_tv(ASN1_OID, "1.3.6.1.4") + \
        tobytes_tv(SNMP_IPADDR, "127.0.0.1") + \
        tobytes_tv(ASN1_INT, 0) + \
        tobytes_tv(ASN1_INT, 0) + \
        tobytes_tv(SNMP_TIMETICKS, 0) + trap
trap = tobytes_tv(SNMP_TRAP, trap)
trap = tobytes_tv(ASN1_INT, SNMP_VER1) + \
        tobytes_tv(ASN1_OCTSTR, "public") + trap
trap = tobytes_tv(ASN1_SEQ, trap)
trap
binascii.hexlify(trap)