###usnmp (Micro Simple Network Management Protocol library)

I thought it would be a nice idea to physically indicate to my kids that they were burning up our meager internet connection.  It got out of control.  It's not sane, extensible, complete or bug free - but it does seem to work.

Before you dig in, know this;
- Supports SNMP Version 1 (unsecure) only.
- It's been (lightly) tested only on CPython and a WiPy, it'll be tested on an esp8266 when the (as of writing) in-progress kickstarter bears first-fruit, if my shipment ever arrives from China.
- It's based on an immature understanding of SNMP in general.
- It (as yet) has no concept of a MIB, just OIDs.
- It can't interpret Opaque or NsapAddr encoding - I've yet to find a sample to analyse
- I used 'micro' as an excuse not to implement any error handling ... then ignored 'micro' and used recursion ;o)

TO DO:
- diagnose, and submit as bug, micropython specific issue with nested memoryview corruption
- re-implement to replace list of nested list exclusively with pointers to memoryview (challenging), or file io on bytearray(?)
- compact MIB class, def parser

###Concepts

Derivatives of the words 'pack' and 'unpack' are used extensively throughout the library, conceptually;

Something **packed** is a bytearray of SNMP formatted data either received from the network (socket) or ready to send over the network.

The action of **pack**ing something creates the **packed** form.

Something **unpacked** is a nested list structure representing valid SNMP data in a python manipulatable format.  Each element of the **unpacked** structure is a list of two elements **[t,v]** where;
- **t** is a code (for which there are Constants & related expectations, refer hereunder) indicating the SNMP type of **v**
- **v** is a value, whose python type depends on the SNMP type indicated by **t** (refer Constants & related expectations, hereunder)

The action of **unpack**ing something creates the **unpacked** form.

###Examples

It's always better by example ...

####Get some data from an agent

Import the library, create a UDP socket;
```python
>>> import socket
>>> import usnmp
>>> s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
>>> s.settimeout(1)
```

Construct an SNMP GetRequest packet to query a device supporting a read-only community named 'public' for 3 OIDs;
- ifInOctets (1.3.6.1.2.1.2.2.1.10.4) - total octets of data received by the interface
- ifOutOctets (1.3.6.1.2.1.2.2.1.16.4) - total octets of data transmitted by the interface
- sysUptime (1.3.6.1.2.1.1.3.0) - number of 100th's of seconds the system has been up

First; create the packet object;
```python
>>> p=usnmp.SnmpPacket(type=usnmp.SNMP_GETREQUEST, community="public")
```

*Note: SNMP packets contain a block ("VarBind"ings) of one or more OIDs each with an associated Type and Value pair.  When requesting (GetRequest or GetNextRequest) values from an agent Type must be set to ASN1_NULL (the corresponding python type/value for which is None).*

Then load the packets objects varbindings with OIDs;
```python
>>> oids=["1.3.6.1.2.1.2.2.1.10.4", "1.3.6.1.2.1.2.2.1.16.4", "1.3.6.1.2.1.1.3.0"]
>>> for oid in oids:
...     p.varbinds[oid] = (usnmp.ASN1_NULL, None)
...
```
Send a packed representation of the packet object to the agent (device) and (hopefully) receive its response;
```python
>>> s.sendto(p.packed, (b"192.168.1.1", 161))
72
>>> d=s.recvfrom(1024)
```
Unpack the response into another packet object and inspect some of its properties:
```python
>>> r=usnmp.SnmpPacket(d[0])
>>> print(r.community)
public
>>> print(r.ver)
0
```
*Note:SNMP_VER1 == 0x0*

Iterate over the good-stuff (aka the OIDs and values in the varbinding):
```python
>>> for oid in r.varbinds:
...     print(oid, r.varbinds[oid])
...
1.3.6.1.2.1.2.2.1.10.4 (65, 1546470168)
1.3.6.1.2.1.2.2.1.16.4 (65, 3249742414)
1.3.6.1.2.1.1.3.0 (67, 105264014)
```
For each OID in the VarBinding the device returned a type and a value (first and second values in the tuple, respectively).
- 65 == 0x41 == SNMP_COUNTER, with an integer value
- 67 == 0x43 == SNMP_TIMETICKS, with an integer value representing 100th's of seconds

####Walk the entire database of an agent

```python
>>> r=usnmp.SnmpPacket(community="public", type=usnmp.SNMP_GETNEXTREQUEST)
>>> oid = "1.3.6.1.2.1.1.1"
>>> r.varbinds[oid]=(usnmp.ASN1_NULL,None)
>>> s.sendto(r.packed, (b'192.168.1.1',161))
39
>>> d=s.recvfrom(1024)
>>> while True:
...     r=usnmp.SnmpPacket(d[0])
...     if r.varbinds[oid] != None:
...         break
...     else:
...         for i in r.varbinds: oid=i
...     print(r.varbinds)
...     r.type=usnmp.SNMP_GETNEXTREQUEST
...     s.sendto(r.packed, (b'192.168.1.1',161))
...     d=s.recvfrom(1024)
...
{'1.3.6.1.2.1.1.1.0': (4, Linux He 2.4.37 #13196 Sat Aug 7 01:42:25 CEST 2010 mips)}
96
{'1.3.6.1.2.1.1.2.0': (6, 1.3.6.1.4.1.8072.3.2.10)}
50
{'1.3.6.1.2.1.1.3.0': (67, 105348680)}
44
{'1.3.6.1.2.1.1.4.0': (4, root)}
44
{'1.3.6.1.2.1.1.5.0': (4, dd-wrt)}
```
*Note: this code relies (to exit) on the fact that when GetNextRequest reaches the end of an agents MIB it will return the same OID, not the next one.  Exiting the loop this way won't work for requests for multiple OIDs.*

*Note: the above examples gloss over the fact that SNMP is a  UDP protocol and there is therefore no concept of a connection ... how did we know that the packet(s) we received were related to the packets we sent? ... Answer: we didn't, we just relied on timing.*

*SNMP replies can be matched to requests via their request_id (.id) value - a reply has the same request_id (.id) as the corresponding request.*

*A quick fix might be to set .id on the request to an integer value based on the uptime of the MCU (micropython time.ticks_us() for example) and check .id on the response matches.*

Constants & related expectations
---

**SNMP_VER1** = 0x0

Only SNMP Version 1 is supported.

**ASN1_INT** = 0x02<BR>
**SNMP_COUNTER** = 0x41<BR>
**SNMP_GUAGE** = 0x42<BR>
**SNMP_TIMETICKS** = 0x43

ASN.1 Integer data type and SNMP derived types, value represented by a python **Int**eger type.

**ASN1_OCTSTR** = 0x04<BR>
**SNMP_IPADDR** = 0x40

OctetString data type, value represented by a python **Str**ing type.

Note: ASN.1 Octet Strings in packed form can contain character values outside of the ASCII range, for example to represent a mac address.

SNMP_IPADDR is a derived type hosting an IP (4 only?) Address as a human readable string.

When a bytearray is unpacked Octet String's that contain non-ASCII characters are marked as **ASN1_OCTSTR_BIN** type (which is library specific, and not part of any standard) and decoded as a string of hex digits.  The helper function **hex2str** can be used to attempt to convert these values to readable text.

**ASN1_OCTSTR_BIN** = 0xff

OctetString (containing non-ASCII characters) data type, value represented by a python **Str**ing of hex value pairs.  Packed to a ASN1_OCTSTR.

**ASN1_OID** = 0x06

OID data type, value represented by a python **Str**ing type as a dot seperated OID in standard notation e.g. "1.3.6.1.2.1.1.5.0" (note the absence of a leading ".").

**ASN1_NULL** = 0x05

NULL data type, value reprsented by a python **None**.

**ASN1_SEQ** = 0x30<BR>
**SNMP_GETREQUEST** = 0xa0<BR>
**SNMP_GETNEXTREQUEST** = 0xa1<BR>
**SNMP_GETRESPONSE** = 0xa2<BR>
**SNMP_SETREQUEST** = 0xa3<BR>
**SNMP_TRAP** == 0xa4

ASN.1 sequence of data blocks type and SNMP derived types, value represented by a python **List**.

The sequence of sub-blocks required inside get/set sequences and trap sequences differs and is SNMP specific - the SnmpPacket class hides the implementation details from the library user.

**SNMP_OPAQUE** = 0x44<BR>
**SNMP_NSAPADDR** = 0x45

Unimplemented data types.

**SNMP_ERR_NOERROR** = 0x00<BR>
**SNMP_ERR_TOOBIG** = 0x01<BR>
**SNMP_ERR_NOSUCHNAME** = 0x02<BR>
**SNMP_ERR_BADVALUE** = 0x03<BR>
**SNMP_ERR_READONLY** = 0x04<BR>
**SNMP_ERR_GENERR** = 0x05

SNMP error codes returned/set in SnmpPacket.err_status.

**SNMP_TRAPGENERIC_COLDSTART** = 0x0<BR>
**SNMP_TRAPGENERIC_WARMSTART** = 0x1<BR>
**SNMP_TRAPGENERIC_LINKDOWN** = 0x2<BR>
**SNMP_TRAPGENERIC_LINKUP** = 0x3<BR>
**SNMP_TRAPGENERIC_AUTHENTICATIONFAILURE** = 0x4<BR>
**SNMP_TRAPGENERIC_EGPNEIGHBORLOSS** = 0x5

SNMP generic trap codes.

###SnmpPacket class

Represents an SNMP data packet and expects to be instantiated in one of two ways;

**o=SnmpPacket(bytearray)**

To manipulate a raw-packet (passed as bytearray) captured from the network socket.

**o=SnmpPacket(type=val[,property=val,...)**

To create a custom packet from scratch.  The **type** property *must* be specified, other properties *may* be specified.  The following have the same net result:

```python
>>> o=usnmp.SnmpPacket(type=usnmp.SNMP_GETREQUEST)
>>> o.community='public'
>>> o.id=65255
```

```python
>>> o=usnmp.SnmpPacket(type=usnmp.SNMP_GETREQUEST, community='public', id=65255)
```

SNMP_GETxxx type packets have different properties from SNMP_TRAP packets;

- **set**ing a property not associated with the packet type is silently ignorred
- **get**ing a property not associated with the packet type, returns **None**

####SnmpPacket.varbinds

An SnmpPackets' **varbinds** property behaves similarly to a dictionary (although it is actually manipulating the structure in SnmpPacket.unpacked) and stores OIDs and their corresponding;

- (t,v) tuple (t=Type, v=Value), or
- a callable that returns a (t,v) tuple

Assignment to .varbinds will add an oid to the database if it doesn't exist, or change it's (t,v), or callable, if it does.

Sample manipulations:

```python
>>> o=usnmp.SnmpPacket(community='public', type=usnmp.SNMP_GETREQUEST, id=65255)
>>> o.varbinds
{}
>>> o.varbinds['1.3.6.1.2.1.1.9.1.3.9'] = usnmp.ASN1_INT, 0
>>> o.varbinds
{'1.3.6.1.2.1.1.9.1.3.9': (2, 0)}
>>> o.varbinds['1.3.6.1.2.1.1.9.1.4.1'] = usnmp.ASN1_OCTSTR, "hello world"
>>> o.varbinds
{'1.3.6.1.2.1.1.9.1.3.9': (2, 0), '1.3.6.1.2.1.1.9.1.4.1': (4, 'hello world')}
>>> for oid in o.varbinds:  print(oid, o.varbinds[oid])
...
1.3.6.1.2.1.1.9.1.3.9 (2, 0)
1.3.6.1.2.1.1.9.1.4.1 (4, 'hello world')
>>> def test(): return usnmp.ASN1_OCTSTR, "goodbye cruel world"
...
>>> o.varbinds['1.3.6.1.2.1.1.9.1.4.1'] = test
>>> o.varbinds
{'1.3.6.1.2.1.1.9.1.3.9': (2, 0), '1.3.6.1.2.1.1.9.1.4.1': <function test at 0x200366e0>}
>>> o.varbinds['1.3.6.1.2.1.1.9.1.4.1']
<function test at 0x200366e0>
>>> o.varbinds['1.3.6.1.2.1.1.9.1.4.1']()
(4, 'goodbye cruel world')
>>> usnmp.unpack(o.packed)
[48, [[2, 0], [4, 'public'], [160, [[2, 65255], [2, 0], [2, 0], [48, [[48, [[6, '1.3.6.1.2.1.1.9.1.3.9'], [2, 0]]], [48, [[6, '1.3.6.1.2.1.1.9.1.4.1'], [4, 'goodbye cruel world']]]]]]]]]
>>>
```

You can delete a varbinding from the varbinds database;

```python
>>> o.varbinds['1.3.6.1.2.1.1.9.1.4.1']
(4, 'goodbye cruel world')
>>> del(o.varbinds['1.3.6.1.2.1.1.9.1.4.1'])
>>> o.varbinds['1.3.6.1.2.1.1.9.1.4.1']
>>>
```


####SnmpPacket.unpacked

Access to the internal nested list of lists represntation of the SNMP packet.  Don't mess with it directly, unless you're really sure you know what you're doing - the properties and .varbinds database are better ways to manipulate it.

```python
>>> o.unpacked
[48, [[2, 0], [4, 'public'], [160, [[2, 65255], [2, 0], [2, 0], [48, [[48, [[6, '1.3.6.1.2.1.1.9.1.4.1'], [4, 'hello world']]]]]]]]]
>>>
```

####SnmpPacket.packed

Returns a bytearray representation of the current state of the object, fit for sending on the network.

If .varbinds contains callables they are evaluated when you get this property, and whatever value the callable returned is packed into the bytearray.

```python
>>> o.packed
bytearray(b'05\x02\x01\x00\x04\x06public\xa0(\x02\x03\x00\xfe\xe7\x02\x01\x00\x02\x01\x000\x1b0\x19\x06\n+\x06\x01\x02\x01\x01\t\x01\x04\x01\x04\x0bhello world')
```

If the SnmpPacket.varbinds database contains callables, they will be evaluated and the point-in-time values returned by the callable(s) will be packed into the bytearray.

####SnmpPacket general properties

**SnmpPacket.ver** _= int_ - get/set the SNMP Version (only Version 1 supported, via SNMP_VER1).

**SnmpPacket.community** _= str_ - get/set the community string.

**SnmpPacket.type** _= int_ - get/set the packet type (e.g. SNMP_GETREQUEST, SNMP_GETRESPONSE etc.).

####SnmpPacket get and set type packet specific properties

**SnmpPacket.id** _= int_ - get/set the packet request_id.

**SnmpPacket.err_status** _= int_ - get/set the error_status (e.g. SNMP_ERR_NOERROR, SNMP_ERR_TOOBIG etc.).

**SnmpPAcket.err_id** _= int_ - get/set the error_id.

####SnnpPacket trap type packet specific properties

**SnmpPacket.enterprise** _= str_ - get/set the trap packet enterprise OID.  A string in a dot-delimited OID standard format without leading dot e.g. 1.3.6.1.4.1.312785.1

**SnmpPacket.agent_addr** _= str_ - get/set the trap packet agent IP address. A string in a dot delimited standard IP4 address format e.g. 127.0.0.1

**SnmpPacket.generic_trap** _= int_ - get/set the trap packet generic trap type (e.g. SNMP_TRAPGENERIC_COLDSTART, SNMP_TRAPGENERIC_WARMSTART, etc.)

**SnmpPacket.specific_trap** _= int_ - get/set the trap packet specific trap type.

**SnmpPacket.time_stamp** _= int_ - get/set the the trap packet time stamp.

###Raw packing and unpacking functions
The library contains a few exposed functions normally used by the internals of the SnmpPacket class to pack/unpack binary data from/to the nested list format.  These are exposed because they may be useful for more refined manipulation of SNMP data.

Data is encoded in SNMP packets as nested Type,Length,Value blocks (nested by the ASN1_SEQ and its SNMP specfic derived types), these functions convert between data in this raw format and python lists of Type,Value.

#####unpack_len(bytearray)

Passed a bytearray representing a raw-packet, or a subset of one on a valid boundary and returns a tuple of the length of the first payload in bytes and the length of the length encoding itself in bytes.  The length of the length encoding is required to allow the next level unpacker to skip past the length to the payload (length in bytes of length encoding can vary).

#####unpack_tlv(bytearray)

Passed a bytearray representing a raw-packet, or a subset of one on a valid boundary and returns a list of Type, Value (as a python object - refer Constants & related considerations).

#####unpack(bytearray)

Passed a bytearray representing a raw-packet, or a subset of one on a valid boundary, recursively passes it through unpack_tlv and returns a fully unpacked list of nested lists.

#####pack_len(int)

Passed a payload length as integer and returns a bytearray encoding of that length.

#####pack_tlv(int, payload)
#####pack_tlv(callable)

Passed an SNMP type as integer and a payload as a relevant python object and returns a bytearray encoding of the block.

**Or;** passed a callable that returns an SNMP type as integer and payload as relevant python objecct type and returns a bytearray encoding of the block.


For ASN1_SEQ, and its related SNMP specific derived types, payload must be a list of pre-packed bytearrays, via pack_tlv.

#####pack(list)

Passed an unpacked python list of nested lists representation of an SNMP packet, recursively calls pack_tlv and returns a bytearray.
