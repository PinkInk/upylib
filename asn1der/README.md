#DER encoded Asn.1 codec, for [Micropython](www.micropython.org)

Codes and decodes a subset of DER encoded Asn.1 datatypes into to/from 
binary format.  In the spirit of minimal; only the Asn.1 data types that 
I've so far encountered in the real-world&trade; (aka are used by SNMPv1) 
are implemented i.e.;

- Null (Asn1DerNull as standalone Singleton)
- Int (Asn1DerInt as subclass of python int)
- OctStr (Asn1DerOctStr as subclass of python bytes)
- OID (Asn1DerOid as subclass of python bytes)
- SEQuence (Asn1DerSeq as subclass of python list)

Asn.1 types are implemented as classes in order that they can be 
subclassed to implement specific protocols (surprise e.g. SNMPv1).

A generic .decode function is provided that takes any arbitary chunk of
DER encoded Asn.1 data as a bytes array and returns the decoded data 
as a list.  This function necessarily utilises recursion to decode
SEQuences, on a constrained system the source data may need to be 
broken into logical units before decoding. 