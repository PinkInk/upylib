#DER encoded Asn.1 codec, for [Micropython](www.micropython.org)

Codes and decodes a subset of DER encoded Asn.1 datatypes into to/from 
binary format - little use in issolation, intended to be subclassed to
implement specific protocols.  In the spirit of minimal; only the Asn.1 
data types that I've thus far encountered in The Real World&trade; (aka
are used by SNMPv1) are implemented i.e.;

- Null ... Asn1DerNull as standalone Singleton
- Int ... Asn1DerInt as subclass of python int
- OctStr ... Asn1DerOctStr as subclass of python bytes
- OID ... Asn1DerOid as subclass of python bytes
- SEQuence ... Asn1DerSeq as subclass of python list

The generic `decode` function takes an arbitary chunk of Asn.1 DER encoded
binary data and returns the decoded data as a list.  This function 
necessarily utilises recursion to decode SEQuences (which in turn commonly
contain more SEQuences).  On a constrained system it may be sane to 
pre-process binary data into logical units before decoding it.

##known-issues

This is a micro module, for constrained environements.

Garbage In, Garbage Out.

Minimal to non-existent parameter checks.

Classes are derivatives of builtins.  Unexpected behaviour results from
utilising instances of module classes on the right-hand side of an 
operation.

e.g.

```python
>>> p = asn1der.Asn1DerInt(23)
>>> p
23
>>> p+3
26
>>> 3+p
TypeError: unsupported types for __add__: 'int', 'Asn1DerInt'
```

This behaviour may be mitigable.  However undoubtedly not in a way
consistent with a micro philosophy.  Or maybe not; my python isn't that 
good, and this is part and parcel of a Learning Experience&trade;.

##the Asn.1 DER format

Each Asn.1 data-type/value is encoded in a string of bytes as 
`Type, Length, Value` (`t,l,v`).
 
`Type` (`t`) is a single byte who's value identifies the type of data 
encoded in `Value` (`v`) i.e. Int, Null, OctStr etc.  
<BR/>Each type has a unique encoding scheme.

`Length` (`l`) encodes the number of bytes required to host `Value` (`v`)
<BR/>The number of bytes required to encode `l` is variable.

The encoding of the `Value` (`v`) is dependent on, and specific to, 
`Type` (`t`). 

Each class in the `asn1der` module implements some common functionality,
in a way that allows it to be subclassed to implement specific protocols
that rely on its encoding mechanism.

##common class properties

`typecode` property (`int`)

The Asn.1 DER encoding `Type` (`t`) code for the class (the first byte
of any `t,l,v` bytes sequence that can decode into the class should match
the value of `typecode`).


##module properties and related functions

The lists `TypeName`, `TypeCodes` and `TypeClasses` are ordered lists of;

- `TypeName` Human&trade; readable names for each data-type e.g. `OctStr`
- `TypeCodes` the corresponding Asn.1 DER type-codes
- `TypeClasses` the corresponding classes

These lists are expected to be extended to accomodate data-type classes 
implemented in derivative/extension modules i.e. `decode()` can decode any
data-type who's name, type and class is appended (in order), as long as it
corresponding class implements the common methods noted hereunder.

The related helper-functions `typecode_for_type()`, `check_typecode()` 
and `class_for_typecodeat()` use three lists (and any extension thereof, 
in a derivative module).

`int typecode_for_type(str)` 

Passed a str Name of a data-type, returns the Asn.1 DER type-code.

```python
>>> asn1der.typecode_for_type('Seq')
48 # == 0x30
```

`bool check_typecode(b int, t int)` 

Parsed the first byte from `t,l,v` chunk of Asn.1 DER encoded data as 
`b` returns True if matches `t`, False otherwise.  

Normally used in combination with `typecode_for_type()` for readability.  

Function is used in the standard implementation of `from_bytes(self)`
within all classes, and is expected to be used in derrivative 
classes/modules, refer source for examples.

```python
>>> b = asn1der.Asn1DerInt(23).to_bytes()
>>> b
b'\x02\x01\x17'
>>> asn1der.check_typecode(b[0], asn1der.typecode_for_type('Int'))
True
```

`<class> class_for_typecodeat(b bytes, ptr int)` passed a chunk of Asn.1 DER 
encoded data as `b` and a pointer to the start of a valid `t,l,v` block, 
returns the class required to decode it.

```python
>>> asn1der.class_for_typecodeat(b, 0)
<class 'Asn1DerInt'>
```

For each class there exists an exposed function which takes a (properly
encoded) `t,l,v` block as bytes and decodes it into the corresponding 
python type, expected by the counterpart class, for e.g.; 
`int tlv_v_to_int(b bytes)` and `list tlv_v_to_seq(b bytes)` etc.

_Warning: these functions do not check that `t` is the correct typecode 
(that is expected of the wrapping class method, refer source code).  Hence
if `tlv_v_to_int()` is passed an SEQuence, it will either fail, or more 
likely, return garbage._

#common class methods

Each type class implements `from_bytes()` (static) and `to_bytes()` methods.

`from_bytes()` decodes an Asn.1 DER encoded `t,l,v` bytes block into an
instance of the corresponding class.

```python
>>> p = asn1der.Asn1DerInt.from_bytes(b)
>>> p
23
>>> type(p)
<class 'Asn1DerInt'>
>>> p.typecode == asn1der.typecode_for_type('Int')
True
```

Alternatively;

```python
>>> p = asn1der.class_for_typecodeat(b,0).from_bytes(b)
>>> p
23
>>> type(p)
<class 'Asn1DerInt'>
>>> p.typecode == asn1der.typecode_for_type('Int')
True
```

`to_bytes()` returns the Asn.1 DER encoded bytes representation
of a class instance.

```python
>>> p.to_bytes()
b'\x02\x01\x17
>>> asn1der.Asn1DerOid(b'1.3.1.2.2.1.23.1').to_bytes()
b'\x06\x07+\x01\x02\x01\x17\x01'
```

#data-type classes

***`asn1der.Asn1DerInt`***

Derivative of python int, with general properties inherited from 
the builtin int class.

__Note: python int's may be -ve, Asn1DerInt's _may not_.

Instances can either be created from python int values, or Asn.1 
DER encoded bytes;

```python
>>> asn1der.Asn1DerInt(23)
23
>>> asn1der.Asn1DerInt.from_bytes(b'\x02\x01\x17)
23
```

***`asn1der.Asn1DerOid`***

Derivative of python bytes, with general properties inherited
from the builtin bytes class.

Instances can either be created from a python bytes representation
of an OID, or Asn.1 DER encoded bytes;

```python
>>> asn1der.Asn1DerOid(b'1.3.1.2.2.1.23.1')
b'1.3.1.2.2.1.23.1'
>>> asn1der.Asn1DerOid.from_bytes(b'\x06\x07+\x01\x02\x01\x17\x01')
b'1.3.1.2.2.1.23.1'
```

***`asn1der.Asn1DerOctStr'***

Derivative of python bytes (Octet Strings can contain non-printable
data, for e.g. in SNMP MAC Addresses), with general properties
inherited from the builtin bytes class.

Instances can either be created from an arbitary python bytes object,
or Asn.1 DER encoded bytes;

```python
>>> asn1der.Asn1DerOctStr(b'hello world')
b'hello world'
>>> asn1der.Asn1DerOctStr(b'\x04\x0bhello world')
b'hello world
```

***`asn1der.Asn1DerSeq`***

Derivative of python list, with general properties inherited from
the builtin list class.

Instances can either be created from a list of other Asn.1 class 
instances (including other `Asn1DerSeq`'s), or Asn1.DER encoded
bytes.

```python
>>> p = asn1der.Asn1DerSeq()
>>> p
[]
>>> p.append( asn1der.Asn1DerInt(23) )
>>> p.append( asn1der.Asn1DerOctStr(b'hello') )
>>> p
[23, b'hello']
>>> p.to_bytes()
b'0\n\x02\x01\x17\x04\x05hello'
>>> asn1der.Asn1DerSeq.from_bytes(b'0\n\x02\x01\x17\x04\x05hello')
[23, b'hello']
```

***`Asn1DerNull`***

Singleton Null data-type, without any payload bytes and length of 0.

Always returns the same encoded sequence instances can be compared
to the class (similar to behaviour of python `None`).

```python
>>> p = asn1der.Asn1DerNull()
>>> p
<Asn1DerNull object at 1d36820>
>>> p is asn1der.Asn1DerNull
True
>>> p.to_bytes()
b'\x05\x00'
>>> m = asn1der.Asn1DerNull.from_bytes(b'\x05\x00')
>>> m is asn1der.Asn1DerNull
True
```