#https://tools.ietf.org/html/rfc1592
#http://www.binarytides.com/programming-udp-sockets-in-python/
#https://msdn.microsoft.com/en-us/library/windows/desktop/bb648640(v=vs.85).aspx

cmty="public"
#if inoctets, if outoctets, timestamp
mibs=["1.3.6.1.2.1.2.2.1.10.4", "1.3.6.1.2.1.2.2.1.16.4", "1.3.6.1.2.1.1.3.0"]

varbinds=[]
for mib in mibs:
    mib = mib.split(".")
    if mib[:2] == ["1", "3"]:
        mib = mib[2:]
        varbind = bytearray([0x06, len(mib)+1, 0x2b])
    #ignore (for now) mib octets > 0xff, unknown encoding
    for idx in mib:
        varbind.append(int(idx))



msg = bytearray([
    0x30, 0x45, #get-request sequence, len

        0x02, 0x01, 0x00, #SNMP version, len, actual version
        0x04, 0x03, ord("A"), ord("F"), ord("C"), #community name

        0xa0, 0x3b, #SNMP GET request, lenth of contained block = 59

            0x02, 0x01, 0x01, #SNMP request ID
            0x02, 0x01, 0x00, #SNMP error status
            0x02, 0x01, 0x00, #SNMP index

            0x30, 0x30, #varbind list, length=0x30 (48) ... length in bytes of following block

                0x30, 0x0f, #varbind, 15 length of contained request

                    0x06, 0x0b, #object id, length=0x0b (11) ... length in bytes of MIB
                        0x2b, 0x06, 0x01, 0x02, 0x01, 0x02, 0x02, 0x01, 0x0a, 0xcf, 0x07, #1.3.6.1.2.1.2.2.1.10.10119  In Octets
                    0x05, 0x00, #value null

                0x30, 0x0f, #varbind, 15 length of contained request

                    0x06, 0x0b, #object id, length=0x0b (11)  ... length in bytes of MIB
                        0x2b, 0x06, 0x01, 0x02, 0x01, 0x02, 0x02, 0x01, 0x10, 0xcf, 0x07, #1.3.6.1.2.1.2.2.1.16.10119 Out Octets
                    0x05, 0x00, #value null

                0x30, 0x0c, #varbind, 12 - length of contained request

                    0x06, 0x08, #object id, length=0x08 (8) ... length in bytes of MIBs
                        0x2b, 0x06, 0x01, 0x02, 0x01, 0x01, 0x03, 0x00, #1.3.6.1.2.1.1.3.0
                    0x05, 0x00, #value null

])

msg = bytearray([
    0x30, 0x45, 0x02, 0x01, 0x00, 0x04, 0x03,
    ord("A"), ord("F"), ord("C"), 0xa0, 0x3b,
    0x02, 0x01, 0x01, 0x02, 0x01, 0x00, 0x02,
    0x01, 0x00, 0x30, 0x30, 0x30, 0x0f, 0x06,
    0x0b, 0x2b, 0x06, 0x01, 0x02, 0x01, 0x02,
    0x02, 0x01, 0x0a, 0xcf, 0x07, 0x05, 0x00,
    0x30, 0x0f, 0x06, 0x0b, 0x2b, 0x06, 0x01,
    0x02, 0x01, 0x02, 0x02, 0x01, 0x10, 0xcf,
    0x07, 0x05, 0x00, 0x30, 0x0c, 0x06, 0x08,
    0x2b, 0x06, 0x01, 0x02, 0x01, 0x01, 0x03,
    0x00, 0x05, 0x00,
])

import socket
s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto(msg, (b"192.168.1.1", 161))
d=s.recvfrom(1024)

r=d[0]

#response analysis
#0x30   #header
#0x51   #response length = 81
#   0x2, 0x1 #version header
#   0x0 #actual version
#   0x4 #community string header
#   0x3 #community string len
#   0x41, 0x46, 0x43, #community string
#   0xa2, 0x47 #snmp get-response, length=71
#       0x2, 0x1, 0x1 #request id 1
#       0x2, 0x1, 0x0 #error status = no error
#       0x2, 0x1, 0x0   #error index = no error
#       0x30, 0x3c #varbind list, length = 60
#           0x30, 0x13 #varbind, length=19
#               0x6, 0xb #objectid, length=11
#               0x2b, 0x6, 0x1, 0x2, 0x1, 0x2, 0x2, 0x1, 0xa, 0xcf, 0x7 #1.3.6.1.2.1.2.2.1.10.10119  In Octets
#               0x41, 0x4 #guess value, lenth 4
#                   0x26, 0xea, 0xe9, 0x3b #value
#                   #convert to value
#                   #val=0
#                   #for i in [0x26, 0xea, 0xe9, 0x3b]:
#                   #  val=(val*0x100)+i
#           0x30,  0x13 #varbind, length=19
#               0x6, 0xb  #objectid, length=11
#               0x2b, 0x6, 0x1, 0x2, 0x1, 0x2, 0x2, 0x1, 0x10, 0xcf, 0x7 #1.3.6.1.2.1.2.2.1.16.10119  In Octets
#               0x41, 0x4 #value, len=4
#                   0x12, 0x45, 0x1d, 0x7 #value
#           0x30, 0x10 #varbind, length=16
#               0x6, 0x8 #objectid, length=8
#               0x2b, 0x6, 0x1, 0x2, 0x1, 0x1, 0x3, 0x0
#               0x43, 0x4 #value, len=4
#                   0x11, 0xf5, 0x2e, 0x6a

#home router
#1.3.6.1.2.1.2.2.1.10.[1,8, ?]
#1.3.6.1.2.1.2.2.1.10.[1,8, ?]

asn1_hdr, pdu_len, snmp_ver, cm_hdr, cm_len = struct.unpack("BB3sBB", r[:struct.calcsize("BB3sBB"))
cm_name, = struct.unpack_from(str(cm_len)+"s",r,struct.calcsize("BB3sBB"))


def snmpReponse(packet):
  community_string = packet[7, 7+packet[6]].decode()
  if not(packet[6+packet[6]+8]):
    pointer = 6+r[6]+12 #points to beginning of first varbind block
    MIBlen = r[pointer+5]
    MIBhex = r[pointer+5:pointer+6+MIBlen]
    ValueLen = r[pointer+6+Miblen+2]

  else:
    raise Exception("SNMP Error", r[6+r[6]+8])
