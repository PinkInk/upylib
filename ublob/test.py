import ublob

b = bytearray([x for x in range(1,17)])
ub = ublob.ublob(b, buf=15, blocksize=15)

ub[0], ub[1], ub[2]
ub[:0], ub[:1], ub[:2]
ub[0:2], ub[:-6], ub[3:-6]
ub[::2]
ub['s']

repr(ub)
len(ub)
len(ub._b), len(ub._mb)

ub
del(ub[0])
del(b[0])
bytes(ub) == bytes(b)

del(ub[:2])
del(b[:2])
bytes(ub) == bytes(b)

del(ub[3:])
del(b[3:])
bytes(ub) == bytes(b)

#test out of range
del(ub[5:])
del(b[5:])
bytes(ub) == bytes(b)

len(ub), len(ub._b), bytes(ub)
ub._buf_align(len(ub))
len(ub), len(ub._b), bytes(ub)

b = bytearray([x for x in range(1,17)])
ub = ublob.ublob(b, buf=15, blocksize=15)

del(ub[:-2])
del(b[:-2])
bytes(ub) == bytes(b)

b = bytearray([x for x in range(1,17)])
ub = ublob.ublob(b, buf=15, blocksize=15)

del(ub[-3:-2])
del(b[-3:-2])
bytes(ub) == bytes(b)

b = bytearray([x for x in range(1,17)])
ub = ublob.ublob(b, buf=15, blocksize=15)

b[2:10] = bytes([1,2,3])
ub[2:10] = bytes([1,2,3])
bytes(ub) == bytes(b)

b = bytearray([x for x in range(1,17)])
ub = ublob.ublob(b, buf=15, blocksize=15)

b[2:5] = bytes([1,2,3,4,5,6,7])
ub[2:5] = bytes([1,2,3,4,5,6,7])
bytes(ub) == bytes(b)

