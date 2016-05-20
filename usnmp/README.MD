#Simple Network Management Protocol v1 packet codec, for [Micropython](www.micropython.org)

Codes and encodes SNMP v1 packets received from, or to send on, the network.  

_Not_ a server - sending or receiving packets on the network is outside of 
its scope (but trivial; refer examples hereunder).

Note: _only_ SNMPv1 is supported.  SNMPv1 is not encrypted; data is sent
to the network, including the internet if you so choose, 'in the clear' - 
be sure that you understand the consequences thereof before utilising this 
module, or SNMPv1 in general, on a network that you don't trust.

Target is for it to be minimal enough to load, compile and run on the 
micropython esp8266 port, with adequate resources remaining for other tasks 
(I can't envisage any scenario where SNMP would be the only function of an 
embedded device), whilst retaining a useable api.

_I plan to further optimise the module through use of memoryviews, when a 
general-availability release of the esp8266 port with working memoryview 
support is released._

##usnmp.SnmpPacket() class

Represents an SNMP packet.  Can be initialised in one of two ways i.e.;

- with a buffer (bytes, bytearray or memoryview) of data received from the network
- by defining the SNMP type and type specific properties and variable bindings (data)

###Create and encode an SNMP packet from scratch;

Create a GETREQUEST packet to request; 

- ifInOctets::4 (OID: 1.3.6.1.2.1.2.2.1.10.4 - Count of packets inbound to Interface 4)
- sysUpTime (OID: 1.3.6.1.2.1.1.3.0)

... from an agent @ 192.168.1.1 using the **public** community.

```python
import usnmp
greq = usnmp.SnmpPacket(usnmp.SNMP_GETREQUEST)
greq.ver
```

Note that the module has provided reasonable defaults that match this simple
case; 

'''python
greq.ver
0 #usnmp.SNMP_VER1
greq.community
'public'
greq.id
0
'''

But these can be changed, either via subsequent assignment;

'''python
greq.community 'somethingelse'
greq.id = 5436235
'''

... or in the class initialisation itself;

'''python
greq = usnmp.SnmpPacket(type=usnmp.GET_REQUEST, community='public', id=654235)
'''

Populate the **.varbinds** object (a collections.OrderedDict) with the OIDs
being requested;

'''python
greq.varbinds['1.3.6.1.2.1.2.2.1.10.4'] = usnmp.ASN1_NULL, None
greq.varbinds['1.3.6.1.2.1.1.3.0'] = usnmp.ASN1_NULL, None
'''

If you were building an equivalent GETRESPONSE packet, you'd need to 
specify the Type & Value against each OID (refering to 
[MIB-2](https://www.ietf.org/rfc/rfc1213.txt));

'''python
greq.varbinds['1.3.6.1.2.1.2.2.1.10.4'] = usnmp.SNMP_COUNTER, 3523441234
greq.varbinds['1.3.6.1.2.1.1.3.0'] = usnmp.SNMP_TIMETICKS, 908452344
'''

Note that as above even GETREQUEST packets require a value against each OID, 
formally this is an usnmp.ASN1_NULL, but there is a convenience alternative
accepted by the module;

'''python
greq.varbinds['1.3.6.1.2.1.2.2.1.10.4'] = None
greq.varbinds['1.3.6.1.2.1.1.3.0'] = None
'''

###Decode a packet received from the network;

First lets send the packet created above to the agent, and hopefully receive
its response.

Formally; we should compare the **id** of the response to the **id** of the 
request in order to verify the relationship (seeding this from the likes of 
micropython's time.ticks_us() may be useful).


'''python
import socket, time
s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.settimeout(1)
greq.id = time.ticks_us()
s.sendto(greq.tobytes(), (b'192.168.1.1', 161))
b = s.recvfrom(1024)[0]
'''

**b** now (hopefully) contains the GETRESPONSE to our GREQUEST;

'''python
gresp = usnmp.SnmpPacket(b)
gresp.type == usnmp.SNMP_GETRESPONSE
True
'''

Compare id's;

'''python
gresp.id == greq.id
True
'''

Retrieve the data;

'''python
for oid in gresp.varbinds:
    print(oid, gresp.varbinds[oid][1])

'1.3.6.1.2.1.2.2.1.10.4'   5425233412
'1.3.6.1.2.1.1.3.0'	1359284344
'''

##SNMP v1 general and packet type specific variables

**All** SNMP packets define **ver**sion and **community**.

'''python
p.ver
0 #usnmp.SNMP_VER1
p.community
'public'
'''

SNMP **GET** and **SET** type packets define request_**id**, 
**err**or**_status** and **err**or**_id**.

'''python
p.id
756345346
p.err_status
0 #usnmp.SNMP_ERR_NOERROR - general error
p.err_id
0 #agent specific error code
'''

SNMP **TRAP** type packets define **enterprise**_oid, **generic_trap**, 
**specific_trap** and **timestamp**.

'python
p.enterprise
'1.3.6.1.4.1.32513'
p.generic_trap
0 #usnmp.SNMP_TRAP_COLDSTART
p.specific_trap
0 #agent specific trap type code
p.timestamp
683436
'''

##Constants

The module contains publically accessible constants useful for encoding and
decoding SNMP data.

###General constants

**SNMP_VER1** = 0x0 indicates SNMP Version 1 (the only version supported by this module).

###Constants for DER encoded ASN.1 primitive types

**ASN1_OCTSTR** = 0x04 

ASN.1 DER primative data type for encoding strings, and bytes data.  

Note that Octet Strings can contain non-printable characters, therefore if 
a packet with an Octet String encoded OID value is received from the network, 
when it's decoded if it contains only printable characters it'll be decoded 
as a **str**ing, otherwise a **bytes** object.

MAC Addresses are commonly encoded as non-printable Octet Strings.
**binascii.unhexlify** and **binascii.hexlify** are useful in these cases.

**ASN1_OID** 0x06

ASN.1 DER primative data type for encoding OID's.

**ASN1_NULL** = 0x05

ASN.1 DER primative data type for encoding Null values, used in GETREQUEST type 
SNMP packets.

**ASN1_SEQ** = 0x30

ASN.1 DER primative data type for encoding SEQuences (lists) of other data types.

###Constants for SNMP specific types, derived from ASN.1 primitives

**SNMP_GETREQUEST** = 0xa0

SNMP packet type (derived from ASN.1 SEQuence) for SNMP GETREQUESTs.

A request from a Manager to an Agent to provide the current value of one or
more OID's.

'''python
p=usnmp.SnmpPacket(type=usnmp.SNMP_GETREQUEST)
'''

**SNMP_GETNEXTREQUEST** = 0xa1

SNMP packet type (derived from ASN.1 SEQuence) for SNMP GETNEXTREQUESTs.

A request from a Manager to an Agent to provide the current value of the OID(s) 
that follow the ones in the request.  This packet type allows a Manager to
'walk' the MIB tree of an agent, without knowing it in advance.  Or retrieve
the values in a variable length table (e.g. the Interfaces or Connections table)
row by row.

'''python
p=usnmp.SnmpPacket(type=usnmp.SNMP_GETNEXTREQUEST)
'''

Corresponding response should include the next OID(s) available (and their 
values) on the agent, after the one(s) specified in this request.

If response contains the same OID(s) as requested - end of available OIDs has
been reached.

**SNMP_GETRESPONSE** = 0xa2

SNMP packet type (derived from ASN.1 SEQuence) for SNMP GETRESPONSEs.

'''python
p=usnmp.SnmpPacket(type=usnmp.SNMP_GETRESPONSE)
'''

Response from agent to Manager to either a GETREQUEST, GETNEXTREQUEST or
SETREQUEST packet, containing the request variables (OID values).

**SNMP_SETREQUEST** = 0xa3

SNMP packet type (derived from ASN.1 SEQuence) for SNMP SETREQUESTs.

'''python
p=usnmp.SnmpPacket(type=usnmp.SNMP_SETREQUEST)
'''

Requests to set the value of **writeable** agent variable(s) (OID values).  

Refer Mib-2 to determine which OIDs are writeable.

**SNMP_TRAP** = 0xa4

SNMP packet type (derived from ASN.1 SEQuence) for SNMP TRAPs.

'''python
p=usnmp.SnmpPacket(type=usnmp.SNMP_TRAP)
'''

All the above GET|SET type SNMP packets are **poll** operations i.e. 
a 'Manager' polls (asks for) the value of a specific OID (or OID's) on
an 'Agent'.

TRAPs are used to **push** information from an agent to its Manager.

Typically, for example, an agent might be configured to push a TRAP to its
manager when a network interface is connected (usnmp.SNMP_TRAP_LINKUP) or 
disconnected (usnmp.SNMP_TRAP_LINKDOWN) or identifying that it has rebooted
and how (usnmp.SNMP_TRACK[COLDSTART|WARMSTART]).

**SNMP_COUNTER** = 0x41

SNMP data type used to represent a 'forever increasing' value for e.g. 
ifInOctets, which holds the number of octets of data received at an 
interface since it started counting them.

Represented in micropython by an **int**eger.

'''python
p.varbinds["1.3.6.1.2.1.2.2.1.10.4"] = 1252341
'''

**SNMP_GUAGE** = 0x42

SNMP data type used to represent values that show current point-in-time 
utilisation, values (for e.g. 'current throughput of an interface') vary
with time and may go down (although not below zero), as well as up between
polls.

Represented in micropython by an **int**eger.

**SNMP_TIMETICKS** = 0x43

SNMP data type representing elapsed time in 100ths of seconds since a 
particular event (normally agent startup, as SNMP has no concept of
'human time').

Represented in micropython by an **int**eger.

**SNMP_IPADDR** = 0x40

SNMP data type representing an IP Address.

Represented in micropython by a **str**ing in normal IP Address format 
e.g. "172.26.1.1" or "255.255.255.0";

'''python
p.varbinds['1.3.6.1.2.1.6.13.1.2.11'] = usnmp.SNMP_IPADDR, "172.26.1.1"
'''

**SNMP_OPAQUE** = 0x44<BR>
**SNMP_NSAPADDR** = 0x45

Unimplemented SNMP data types, encountering them will cause SnmpPacket to 
raise an exception.

SNMP_ERR_NOERROR = 0x00<BR>
SNMP_ERR_TOOBIG = 0x01<BR>
SNMP_ERR_NOSUCHNAME = 0x02<BR>
SNMP_ERR_BADVALUE = 0x03<BR>
SNMP_ERR_READONLY = 0x04<BR>
SNMP_ERR_GENERR = 0x05

Possible SNMP **GET|SET** packet **err_id** values.

SNMP_TRAP_COLDSTART = 0x0<BR>
SNMP_TRAP_WARMSTART = 0x10<BR>
SNMP_TRAP_LINKDOWN = 0x2<BR>
SNMP_TRAP_LINKUP = 0x3<BR>
SNMP_TRAP_AUTHFAIL = 0x4<BR>
SNMP_TRAP_EGPNEIGHLOSS = 0x5

Possible SNMP **TRAP** packet **generic_trap** values.


##Utility Functions

May be useful for deeper analysis of SNMP packets received from the network
and are used by the **SnmpPacket** class to decode and encode data.

###usnmp.tobytes_tv(type, data)

Return binary payload encoding of python format ASN.1/SNMP type and value pair.

'''python
usnmp.tobytes_tv(usnmp.ASN1_OID, "1.3.1.2.1.1.11.2")
b'\x06\x07+\x01\x02\x01\x01\x0b\x02'
usnmp.tobytes_tv(usnmp.SNMP_IPADDR, "172.26.23.1")
b'@\x04\xac\x1a\x17\x01'
'''

###usnmp.tobytes_len(len)

Return binary encoding of the length of a data block.

'''python
usnmp.tobytes_len(23)
b'\x17'
usnmp.tobytes_len(2754)
b'\x82\n\xc2'
'''

Note that the number of bytes required to encode a data blocks length is
variable, hence the behaviour of the counterpart usnmp.frombytes_lenat 
function described hereunder.

###usnmp.frombytes_tvat(bytes, ptr)

Return the type and value found at **ptr** within **bytes**.

'''python
usnmp.frombytes_tvat(usnmp.tobytes_tv(usnmp.SNMP_IPADDR, "172.26.23.1"), 0)
(64, '172.26.23.1')
64 == usnmp.SNMP_IPADDR
True
import binascii
#single item get-request, captured from nw
b = b'0&\x02\x01\x00\x04\x03AFC\xa0\x1c\x02\x043x:\xc0\x02\x01\x00\x02\x01\x000\x0e0\x0c\x06\x08+\x06\x01\x02\x01\x01\x01\x00\x05\x00'
usnmp.frombytes_tvat(b, 5)
(4, 'AFC') #community string
'''

###usnmp.frombytes_lenat(bytes, ptr)

Return the length of the payload encoded at **ptr** in **bytes** and also the
number of bytes the legnth was encoded in.

'''python
import binascii
#single item get-request, captured from nw
b = b'0&\x02\x01\x00\x04\x03AFC\xa0\x1c\x02\x043x:\xc0\x02\x01\x00\x02\x01\x000\x0e0\x0c\x06\x08+\x06\x01\x02\x01\x01\x01\x00\x05\x00'
usnmp.frombytes_lenat(b, 5)
(3, 1) #three bytes long, length encoded in a single byte
'''

The full length of the data-block starting at **ptr** is 1 (the length of 
type byte) + the sum of the outputs of this function.

'''python
1+sum(usnmp.frombytes_lenat(b, 5))
5
'''

##SNMP v1 packet structure

SNMP packets structure is derived from the DER encoded ASN.1 standard.

There are two general packet structures;

- GET and SET type packets (GETREQUEST, GETRESPONSE, GETNEXTREQUEST and SETREQUEST)
- TRAP packets

Each ASN.1 primitive, or SNMP derived type, is encoded in 3 elements - Type, 
Length and Payload;

T - one byte indicating type of the data
L[L1, L2 ... Ln] - length of Payload, can take more than one byte to encode
P[P1, P2 ... Pn] - Payload bytes

The ASN.1 type SEQuence, is a container for multiple sub data elements, each
encoded to the above described scheme (which _can_ include other SEQuences).

The SNMP protocol defines a number of derivatives of ASN.1 SEQuence which 
are also containers e.g. the SNMP_GETxxx, SNMP_SETREQUEST and SNMP_TRAP types.

T - SEQ
L[..Ln] - length of all the encoded sub data elements
    TL[..Ln]P[...Pn]
    TL[..Ln]P[...Pn]
    etc.

The SNMP GET and SET type packet format;

SEQ
    INT version
    OCTSTR community
    TYPE e.g. SNMP_GETREQUEST (i.e. a SEQuence derivative)
    	INT id
    	INT err_status
    	INT err_id
    	SEQ container for Variable Bindings (varbinds)
    	   SEQ 1
    	   	OID
    	   	DATA
    	   SEQ 2
    	   	OID
    	   	DATA
    	   etc.

The SNMP TRAP type packet format is unique;

SEQ
    INT version
    OCTSTR community
    TYPE e.g. SNMP_GETREQUEST (i.e. a SEQuence derivative)
    	OID enterprise oid
    	IPADDR agent IP address
    	INT generic trap type
    	INT specific trap type
    	TIMETICKS timestamp of the event
    	SEQ container for Variable Bindings (varbinds)
    	   SEQ 1
    	   	OID
    	   	DATA
    	   SEQ 2
    	   	OID
    	   	DATA
    	   etc.

Variable Bindings (varbinds) associate specific agent properties with their
value for e.g. 1.3.6.1.2.1.2.2.1.10.4 is defined by MIB-2 as ifInOctets 
for interface No. 4 as a Counter i.e. the number of octets of data that were
recorded inbound to the 4th interface up to the point in time the property was 
requested.

If you are requesting to know this value from an agent a GETxxx type SNMP 
packet will fill the data value with an ASN.1 NULL type e.g.;

'''python
import usnmp
p = usnmp.SnmpPacket(type=usnmp.SNMP_GETREQUEST)
p.varbinds['1.3.6.1.2.1.2.2.1.10.4'] = usnmp.ASN1_NULL, None
'''

Or for brevity;

'''python
p.varbinds['1.3.6.1.2.1.2.2.1.10.4'] = None
'''

If you are acting as an agent (i.e. responding to such a get request), or are
interpreting data received in response to the request, the DATA element will
be of type SNMP_COUNTER (because the specific OID is of type Counter), a 
derivative of the ASN.1 INT type, which can represent an integer e.g.;

'''python
p = usnmp.SnmpPacket(type=usnmp.SNMP_GETRESPONSE)
p.varbinds['1.3.6.1.2.1.2.2.1.10.4'] = usnmp.SNMP_COUNTER, 12345678 #some value
'''




