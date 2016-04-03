#SNMP versions
SNMP_VER1 = 0x0

#ASN.1 primitives
ASN1_INT = 0x02
ASN1_OCTSTR = 0x04 #OctetString
ASN1_OID = 0x06 #ObjectIdentifier
ASN1_NULL = 0x05
ASN1_SEQ = 0x30 #sequence

#SNMP specific SEQUENCE types
SNMP_GETREQUEST = 0xa0

#SNMP specific integer types
SNMP_COUNTER = 0x41
SNMP_GUAGE = 0x42
SNMP_TIMETICKS = 0x43

#SNMP specific other types
SNMP_IPADDR = 0x40
SNMP_OPAQUE = 0x44 #not handled
SNMP_NSAPADDR = 0x45 #not handled

#SNMP error codes
SNMP_ERR_NOERROR = 0x00
SNMP_ERR_TOOBIG = 0x01
SNMP_ERR_NOSUCHNAME = 0x02
SNMP_ERR_BADVALUE = 0x03
SNMP_ERR_READONLY = 0x04
SNMP_ERR_GENERR = 0x05

def encode_getrequest(community, req_id, mibs, ver=SNMP_VER1):
    seq_mbmrs = []
    for mib in mibs:
        seq_mbmrs.append( \
            encode(ASN1_SEQ, \
                [encode(ASN1_OID, mib), encode(ASN1_NULL, None)] \
            ) \
        )
    mib_seqb = encode(ASN1_SEQ, seq_mbmrs)
    gr = encode(SNMP_GETREQUEST, \
                    [ \
                        encode(ASN1_INT, req_id), \
                        encode(ASN1_INT, 0x00), \
                        encode(ASN1_INT, 0x00), \
                        mib_seqb\
                    ] \
               )
    packet = encode(SNMP_SEQ, \
                        [ \
                            encode(SNMP_INT, ver), \
                            encode(SNMP_OCTSTR, community), \
                            gr \
                        ] \
                   )
    return packet

def unpack(data):
    pass

def decode(data):
    ptr = 0
    code = data[ptr]
    l, l_incr = decode_len(data)
    ptr +=  1 + l_incr
    #sequence types
    if code in (ASN1_SEQ, SNMP_GETREQUEST):
        subdata = []
        while ptr < len(data):
            l, l_incr = decode_len( data[ptr:] )
            subdata.append( data[ptr : ptr+1+l_incr+l] )
            ptr += 1 + l_incr + l
        return code, len(data), subdata
    #octet string
    elif code == ASN1_OCTSTR:
        subdata = data[ptr : ptr+l]
        return code, len(subdata), subdata.decode()
    #integer types
    elif code in (ASN1_INT, SNMP_COUNTER, SNMP_GUAGE, SNMP_TIMETICKS):
        i=0
        for b in data[ptr:]:
            i = i*0x100 + b
            ptr += 1
        return code, ptr, i
    elif code == ASN1_NULL:
        if data[1]==0 and len(data)==2:
            return code, 2, None
        else:
            raise Exception("SNMP, bad null encoding")
    elif code == ASN1_OID:
        #first 2 indexes are incoded in single byte
        oid = str(data[ptr]//0x28) + "." + str(data[ptr]%0x28)
        ptr += 1
        high_septet = 0
        for byte in data[ptr:]:
            if byte&0x80 == 0x80:
                high_septet = byte - 0x80
            else:
                oid += "." + str(high_septet*0x80 + byte)
                high_septet = 0
            ptr += 1
        return code, ptr, oid
    else:
        raise Exception("SNMP invalid block code to decode")

def pack(data):
    pass

def encode(code, data):
    #sequence types
    if code in (ASN1_SEQ, SNMP_GETREQUEST):
        b = bytearray()
        for block in data:
            b.extend(block)
        return bytearray([code]) + encode_len(len(b)) + b
    #octet string
    elif code == ASN1_OCTSTR:
        b = bytearray(map(ord,data))
        return bytearray([code]) + encode_len(len(b)) + b
    #integer types
    elif code in (ASN1_INT, SNMP_COUNTER, SNMP_GUAGE, SNMP_TIMETICKS):
        if data < 0:
            raise Exception("SNMP, -ve int")
        else:
            b = bytearray([data&0xff])
            data //= 0x100
            while data > 0:
                #micropython has no bytearray.reverse method
                #data.append(v&0xff)
                b = bytearray([data&0xff]) + b
                data //= 0x100
                #data.reverse()
            return bytearray([code]) + encode_len(len(b)) + b
    elif code == ASN1_NULL:
        return bytearray([code, 0x0])
    elif code == ASN1_OID:
        oid = data.split(".")
        oid = list(map(int,oid))
        b = bytearray([oid[0]*40 + oid[1]])
        for id in oid:
            if 0 <= id < 0x7f:
                b.append(id)
                #check RFC's for correct upperbound
            elif 0x7f < id < 0x7fff:
                b.append(id//0x80+0x80)
                b.append(id&0x7f)
            else:
                raise Exception("SNMP, OID value out of range")
        return bytearray([ASN1_OID]) + encode_len(len(b)) + b

def encode_len(l):
    """
        Passed a datablock length as integer,
        returns length encoded as bytearray
    """
    if 0 < l < 0x7f:
        return bytearray([l])
    #check RFC's for correct upperbound
    elif 0x7f < l < 0x7fff:
        return bytearray([l//0x80+0x80, l&0x7f])
    else:
        raise Exception("SNMP, length out of bounds")

def decode_len(data):
    """
        Passed a datablock as bytearray,
        returns tuple of data length as int
        and pointer incrementor as int
    """
    ptr=1
    if data[ptr]&0x80 == 0x80:
        return ((data[ptr]-0x80)*0x80) + data[ptr+1], 2
    else:
        return data[ptr], 1
