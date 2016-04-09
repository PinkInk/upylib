usnmp (Micro Simple Network Management Protocol library)
===
I thought it would be a nice idea to physically indicate to my kids that they were burning up our meager internet connection and that they could therefore expect Steam to be 'laggy' (their words, not mine).  It got out of control.  It's not sane, extensible, complete or bug free - but it does seem to work.

Before you dig in, know this;
- It only supports SNMP Version 1 - whilst this still seems to be supported by most, if not all, devices - you should be aware that it has no security; data is relayed (over the internet if you so choose) in the clear.
- It's been tested on a WiPy, and will be tested on an esp8266 when the (as of writing) in-progress kickstarter bears first-fruit, if my shipment ever arrives from China.
- It's based on an immature understanding of SNMP in general and very hasty skim-reading of the various RFC's and other references.
- (as of date) It's only been tested on a limited set of SNMP poll operations (namely get-request, get-response, get-nextresponse),  it *may* be useable for traps, but I haven't tried that (yet).
- It (as yet) has no concept of a MIB, just OIDs, - it would be unwieldy to implement an SNMP agent that could be polled for anything other than a small set of OIDs.
- Due to its shortfalls it should probably have been called usnmppacket, usnmpv1packet, usnmpv1getpacket or similar, but I was feeling brave, and I *may* extend it, someday.
- It can't interpret Opaque or NsapAddr value encoding - I've yet to find a device that will generate samples (if you have such a device - please submit!)
- I used 'micro' as an excuse not to implement any error handling ... then ignored 'micro' and used recursion ;o)
- Oh, and I only dabble with Python occasionally; if you're a pro; pointers would be appreciated.

TO DO:
- compact MIB class
- OIDs in MIBs as callables

Concepts
---
Derivatives of the words 'pack' and 'unpack' are used extensively throughout the library, conceptually;

Something **packed** is a bytearray of SNMP formatted data either received from the network (socket) or ready to send over the network.

The action of **pack**ing something creates the **packed** form.

Something **unpacked** is a nested list structure representing valid SNMP data in a python manipulatable format.  Each element of the **unpacked** structure is a list of two elements **[t,v]** where;
- **t** is a code (for which there are Constants & related expectations, refer hereunder) indicating the SNMP type of **v**
- **v** is a value, whose python type depends on the SNMP type indicated by **t** (refer Constants & related expectations, hereunder)

The action of **unpack**ing something creates the **unpacked** form.

Examples
---
It's always better by example ...

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
>>> p=usnmp.SnmpPacket(community="public", type=usnmp.SNMP_GETREQUEST)
```

*Note: all SNMP packets contain a block of one or more OIDs (a MIB, in my terminology) each with an associated Type and Value pair.  When requesting (GetRequest or GetNextRequest) the values from an SNMP agent Type is ASN1_NULL, the corresponding python type/value for which is None.*

Then load the packets objects mib with OIDs;
```python
>>> mibs=["1.3.6.1.2.1.2.2.1.10.4", "1.3.6.1.2.1.2.2.1.16.4", "1.3.6.1.2.1.1.3.0"]
>>> for mib in mibs:
...     p.mib[mib] = (usnmp.ASN1_NULL, None)
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

Iterate over the good-stuff (aka the returned values against OIDs):
```python
>>> for oid in r.mib:
...     print(oid, r.mib[oid])
...
1.3.6.1.2.1.2.2.1.10.4 (65, 1546470168)
1.3.6.1.2.1.2.2.1.16.4 (65, 3249742414)
1.3.6.1.2.1.1.3.0 (67, 105264014)
```
For each OID in the MIB (my terminology) the device has returned a type and a value (first and second values in the tuple, respectively).
- 65 == 0x41 == SNMP_COUNTER, with an integer value
- 67 == 0x43 == SNMP_TIMETICKS, with an integer value representing 100th's of seconds

*Repeat the above and calculate the delta between the returned values, and divide by the delta in time - and you know the average number of octets that passed through the interfaces each 100th of a second.*

Walk the entire MIB tree of a device:
```python
>>> r=usnmp.SnmpPacket(community="public", type=usnmp.SNMP_GETNEXTREQUEST)
>>> mib = "1.3.6.1.2.1.1.1"
>>> r.mib[mib]=(usnmp.ASN1_NULL,None)
>>> s.sendto(r.packed, (b'192.168.1.1',161))
39
>>> d=s.recvfrom(1024)
>>> while True:
...     r=usnmp.SnmpPacket(d[0])
...     if r.mib[mib] != None:
...         break
...     else:
...         for i in r.mib: mib=i
...     print(r.mib)
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

Constants & related expectations
---
###SNMP Version

**SNMP_VER1** = 0x0

Only SNMP Version 1 is supported.

###ASN.1 primitive data types

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
**SNMP_GETRESPONSE** = 0xa2<BR>
**SNMP_GETNEXTREQUEST** = 0xa1

ASN.1 sequence of data blocks type and SNMP derived types, value represented by a python **List**.

**SNMP_OPAQUE** = 0x44<BR>
**SNMP_NSAPADDR** = 0x45

Unimplemented data types.

**SNMP_ERR_NOERROR** = 0x00<BR>
**SNMP_ERR_TOOBIG** = 0x01<BR>
**SNMP_ERR_NOSUCHNAME** = 0x02<BR>
**SNMP_ERR_BADVALUE** = 0x03<BR>
**SNMP_ERR_READONLY** = 0x04<BR>
**SNMP_ERR_GENERR** = 0x05

SNMP error codes returned/set in SnmpPacket.err_status (or SnmpPacket.err_id?).

Classes
-------

Functions
---------
