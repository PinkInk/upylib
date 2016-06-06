import asn1der

v1 = 235235
a1 = asn1der.Asn1DerInt(v1)
assert type(a1) == asn1der.Asn1DerInt, 'incorrect type'
assert v1 == asn1der.Asn1DerInt.from_bytes( a1.to_bytes() ), 'wrong value'

v2 = b'1.3.1.2.2.1.234.746344.1.22'
a2 = asn1der.Asn1DerOid(v2)
assert type(a2) == asn1der.Asn1DerOid, 'incorrect type'
#why need to convert string?
assert v2 == asn1der.Asn1DerOid.from_bytes( a2.to_bytes()), 'wrong value'
#assert v2 == asn1der.Asn1DerOid.from_bytes( a2.to_bytes()), 'wrong value'

v3 = b'hello world'
a3 = asn1der.Asn1DerOctStr(v3)
assert type(a3) == asn1der.Asn1DerOctStr, 'incorrect type'
assert v3 == asn1der.Asn1DerOctStr.from_bytes( a3.to_bytes()), 'wrong value'

a4 = asn1der.Asn1DerNull()
assert a4 is asn1der.Asn1DerNull, 'not a Null'
asn1der.Asn1DerNull.from_bytes( a4.to_bytes())

v5 = [a1, a2, a3, a4]
a5 = asn1der.Asn1DerSeq(v5)
assert type(a5) == asn1der.Asn1DerSeq, 'incorrect type'
assert v5 == asn1der.Asn1DerSeq.from_bytes( a5.to_bytes() ), 'fails because subclasses of str do not compare'

v6 = a5.to_bytes() + a4.to_bytes() + a3.to_bytes() + a2.to_bytes() + a1.to_bytes()
a6 = asn1der.decode(v6)
assert a6[0] == a5, 'fails because subclasses of str do not compare'
assert a6[1] == a4, 'incorrect item'
assert a6[2] == a3, 'incorrect item'
#why need to convert string?
assert a6[3] == a2, 'fails because subclasses of str do not compare'
assert str(a6[3]) == str(a2), 'incorrect item'
assert a6[4] == a1, 'incorrect item'

