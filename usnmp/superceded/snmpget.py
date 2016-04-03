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

#encode_xxx return encoded bytearray (type, len, data)
#decode_xxx return tuple (decoded_data, pointer_increment)
#           consider (type, decoded_data, pointer_increment)

def decode_seq(data, object_type=ASN1_SEQ):
    """
        Passed a Sequence datablock as bytearray,
        optionally a derived type-code as int,
        returns tuple of list of sub-datablocks as bytearrays
        and a pointer incrementor as int,
        optionally prefixed as specified derived type
    """
    ptr = 0
    if data[ptr] != object_type:
        raise Exception("SNMP, not a sequence, or derivative type, datablock")
    else:
        #l_seq, l_incr = decode_len(data)
        l, l_incr = decode_len(data)
        ptr +=  1 + l_incr
        subdata = []
        while ptr < len(data):
            l, l_incr = decode_len( data[ptr:] )
            subdata.append( data[ptr : ptr+1+l_incr+l] )
            ptr += 1 + l_incr + l
        return subdata, len(data)

def encode_getrequest(data):
    return encode_seq(data, object_type=SNMP_GETREQUEST)

def encode_seq(blocks, object_type=ASN1_SEQ):
    """
        Passed a list of pre-encoded datablocks as bytearrays,
        returns Sequence datablock as bytearray
    """
    data = bytearray()
    for block in blocks:
        data.extend(block)
    return bytearray([object_type]) + encode_len(len(data)) + data

def decode_octstr(data):
    """
        Passed an OctetString datablock as bytearray,
        returns tuple of OctetString as str
        and pointer incrementor as int
    """
    ptr = 0
    if data[ptr] != ASN1_OCTSTR:
        raise Exception("SNMP, not an OctetString datablock")
    else:
        l, l_incr = decode_len(data)
        ptr +=  1 + l_incr
        bs = data[ptr : ptr+l]
        return bs.decode(), len(bs)

def encode_octstr(s):
    """
        Passed an Octet String as str,
        returns OcttetString datablock as bytearray
    """
    s = bytearray(map(ord,s))
    return bytearray([ASN1_OCTSTR]) + encode_len(len(s)) + s

#decode SNMP types derived from ASN.1 integer
def decode_timeticks(data):
    return decode_int(data, object_type=SNMP_TIMETICKS)

def decode_gauge(data):
    return decode_int(data, object_type=SNMP_GUAGE)

def decode_counter(data):
    return decode_int(data, object_type=SNMP_COUNTER)

def decode_int(data, object_type=ASN1_INT):
    """
        Passed an Integer datablock as bytearray,
        optionally a derived type-code as int,
        returns tuple of Integer as int
        and pointer incrementor as int
    """
    ptr = 0
    if data[ptr] != object_type:
        raise Exception("SNMP, not an integer, or derivative, datablock")
    else:
        l, l_incr = decode_len(data)
        ptr += 1 + l_incr
        i=0
        for b in data[ptr:]:
            i = i*0x100 + b
            ptr += 1
        return i, ptr

#encode SNMP types derived from ASN.1 integer
def encode_timeticks(v):
    return encode_ind(v, object_type=SNMP_TIMETICKS)

def encode_gauge(v):
    return encode_int(v, object_type=SNMP_GUAGE)

def encode_counter(v):
    return encode_int(v, object_type=SNMP_COUNTER)

def encode_int(v, object_type=ASN1_INT):
    """
        Passed an Integer as int,
        optionally a derived type-code as int,
        returns Integer datablock as bytearray,
        optionally prefixed as specified derived type
    """
    if v < 0:
        raise Exception("SNMP, -ve int")
    else:
        data = bytearray([v&0xff])
        v //= 0x100
        while v > 0:
            #micropython has no bytearray.reverse method
            #data.append(v&0xff)
            data = bytearray([v&0xff]) + data
            v //= 0x100
            #data.reverse()
            return bytearray([object_type]) + encode_len(len(data)) + data

def encode_null():
    """
        Returns Null datablock as bytearray
    """
    return bytearray([ASN1_NULL, 0x0])

def decode_null(data):
    """
        Passed a Null datablock as bytearray,
        returns tuple of None
        and pointer intrementor as int
    """
    if data[0] != ASN1_NULL:
        raise Exception("SNMP, not a null")
    elif data[1] != 0:
        raise Exception("SNMP, null with non-zero len")
    else:
        return None, 2

def encode_oid(oid):
    """
        Passed an OID as string,
        returns OID datablock as bytearray
    """
    oid = oid.split(".")
    oid = list(map(int,oid))
    b = bytearray([oid[0]*40 + oid[1]])
    for id in oid:
        if 0 < id < 0x7f:
            b.append(id)
            #check RFC's for correct upperbound
        elif 0x7f < id < 0x7fff:
            b.append(id//0x80+0x80)
            b.append(id&0x7f)
        else:
            raise Exception("SNMP, OID value out of range")
    return bytearray([ASN1_OID]) + encode_len(len(b)) + b

def decode_oid(data):
    """
        Passed an OID datablock as bytearray,
        returns tuple of OID as string
        and pointer incrementor as int
    """
    ptr=0
    if data[ptr] != ASN1_OID:
        raise Exception("SNMP, not an OID")
    else:
        l, l_incr = decode_len(data)
        ptr += 1 + l_incr
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
            ptr+=1
        return oid, ptr

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
        raise Exception("SNMP, payload len out of bounds")

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

snmp1 fn's
==========
    GetRequest
    SetRequest
    GetNextRequest
    GetBulkRequest
    GetResponse
    Trap

ASN.1 PRIMITIVES
================
    #https://msdn.microsoft.com/en-us/library/windows/desktop/bb648640(v=vs.85).aspx
    ASN.1

    0x02 INTEGER
        len
            1 or 2 bytes
                if byte&0x80 == 0x80
                    len is 2 bytes, val = ((byte&0x7f) & 0x80) + nextbyte
                else
                    len is 1 byte,  val  = byte
        payload
            if byte1 = 0x00
                value is positive, but with 0x80 set
            binary number of len
                if first bit (0x80) of leading byte is 1
                and payload is not prefixed by 0x00
                    then negative

    0x04 OCTET STRING
        len
            1 or 2 bytes
                if byte&0x80 == 0x80
                    len is 2 bytes, val = ((byte&0x7f) & 0x80) + nextbyte
                else
                    len is 1 byte,  val  = byte
        payload
            bytestring of len

    0x6 OBJECT IDENTIFIER / OID
        len #never 2 bytes, but can be treated same way as other types
        payload
            first two nodes as 1 byte
                encode: node1*40 + node2
                decode:
                    node1: int(val/40) or val//40
                    node2: val%40
            balance nodes:
                1 or 2 bytes
                    if byte&0x80 == 0x80
                        len is 2 bytes, val = ((byte&0x7f) & 0x80) + nextbyte
                    else
                        len is 1 byte,  val  = byte

    0x05 NULL
        len = 0x00

    0x30 SEQUENCE
        len
            1 or 2 bytes
                if byte&0x80 == 0x80
                    len is 2 bytes, val = ((byte&0x7f) & 0x80) + nextbyte
                else
                    len is 1 byte,  val  = byte
        payload
            multiple primitives
