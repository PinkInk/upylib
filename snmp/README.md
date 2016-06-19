#SNMP v1 codec, for [Micropython](www.micropython.org)

Encodes and decodes SMTP v1 between python object and binary formats.  

Requires and inherits from [asn1der](https://github.com/PinkInk/upylib/tree/master/asn1der).

Refer asn1der [readme](https://github.com/PinkInk/upylib/tree/master/asn1der)
for reference to implementation of the Asn.1 DER encoded base-types used 
natively by SNMP v1.

This module implements;

- classes, as derivatives of Asn.1 DER primitives, representing SNMP v1
specific data types
- classes, as derivatives of Asn.1 DER SEQuence primative, representing
SNMP v1 specific packet payload structures
- a generic `SnmpPacket` helper class that wraps 

##known-issues

Significant memory footprint (for esp8266 Micropython port).  Alternative
[usnmp](https://github.com/PinkInk/upylib/tree/master/usnmp) implementation
is more basic, but fully functional and has a smaller footprint.

Garbage In, Garbage Out. Minimal to non-existent parameter checking.

Classes are derivatives of builtins.  Micropython support for subclassing
builtins is limited and resulting instances have limited compatibility
with builtins and exhibit some 'odd' (but manageable) behaviour.

##install and import

Copy [asn1der.py](https://github.com/PinkInk/upylib/blob/master/asn1der/asn1der.py)
and the entire [snmp](https://github.com/PinkInk/upylib/tree/master/snmp/snmp) subdirectory
to your micropython library/module path.

`import snmp`

