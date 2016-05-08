###ublob.py (micro Binary Large OBject library)

A buffered mutable bytearray like object that trades a configurable buffer overhead, of typically a few bytes, for the ability to perform destructive/constructive slice assignment operations using (an internal) memoryview.  The buffer is extended only if a slice assignment would cause overflow.

Intended to be used to simplify the manipulation of binary data (for e.g. from the network) in memory constrained systems.

#####ublob.ublob(b=None, buf=128, blocksize=32)

Create a ublob, with initial buffer size as whatever multiple of **blocksize** will accomodate either a passed-in bytes or bytearray object, or **buf**. 

As an empty ublob;

```python
>>> import ublob
>>>
>>> ub = ublob.ublob(buf=32, blocksize=16)
>>> ub
b''
```
From an existing bytes or bytearray object;

```python
>>> import ublob
>>>
>>> b = bytearray([x for x in range(1,17)])
>>> ub = ublob.ublob(b, blocksize=16)
>>> bytes(b) == bytes(ub)
True
```

Convert a ublob to a bytes, or bytearray object (for e.g. to send over network);

```python
b'\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10'
>>> bytes(ub)
b'\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10'
>>> bytearray(ub)
bytearray(b'\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10')
```

Items and slices (including slices with step) return bytearrays;

```python
>>> b = bytearray([x for x in range(1,17)])
>>> ub = ublob.ublob(b, buf=15, blocksize=15)
>>>
>>> ub[0] == b[0]
True
>>> ub[1] == b[1]
True
>>> ub[2] == b[2]
True
>>> ub[:0] == b[:0]
True
>>> ub[:1] == b[:1]
True
>>> ub[:2] == b[:2]
True
>>> ub[0:2] == b[0:2]
True
>>> ub[:-6] == b[:-6]
True
>>> ub[3:-6] == b[3:-6]
True
>>> ub[::2] == b[::2]
True
>>>
>>> #expect error
>>> ub['s']
TypeError: bytearray indices must be integers or slices, not str
>>>
```

Note; 
- returns bytearrays, not memoryviews ... memoryviews would become inconsistent if the ublob was manipulated and could prevent internal operataions e.g. extending buffer
- the internal memoryview can be accessesed as ub._mb - but it is inadvisable to do so without extreme caution

Items and slices can be assigned to.  Including unequal slice assignments (but assignment to a slice with a step is not supported, and will raise an exception).  

Internally assignments occur by sliding data around within the buffer, using a memoryview.  Note that this can/does result in areas of the buffer beyond ublob[:len(ub)] containing garbage, but the balance data in the buffer is only accessible by abusing ublob._b or ublob._mb.  

The buffer automatically grows, to the next adequate multiple of **blocksize**, if required to accomodate new data.  The buffer is never shrunk automatically, but ref ublob.buflen() method hereunder.  On micropython a **gc.collect()** is automatically issued after the buffer is grown or shrunk.

Item assignment requires integers;

```python
>>> ub[0]=10
>>> ub[0]=bytes([1,2,3])
TypeError: int in range(0,256) required

```

Bytes or bytearray's can be assigned to slices, there is no need for assignment length to equal slice length, the buffer may grow, if necessary;

```python
>>> b = bytearray([x for x in range(1,17)])
>>> ub = ublob.ublob(b, buf=15, blocksize=15)
>>>
>>> b[2:10] = bytes([1,2,3])
>>> ub[2:10] = bytes([1,2,3])
>>> bytes(ub) == bytes(b)
True
>>>
>>> b = bytearray([x for x in range(1,17)])
>>> ub = ublob.ublob(b, buf=15, blocksize=15)
>>>
>>> b[2:5] = bytes([1,2,3,4,5,6,7])
>>> ub[2:5] = bytes([1,2,3,4,5,6,7])
>>> bytes(ub) == bytes(b)
True```

Unlike bytearrays ublob **does not** support assignment out of range(0,len(ub)-1);

```python
>>> len(ub)
16
>>> ub[len(ub)]=23
IndexError: index out of range
>>> ub[len(ub)-1]=23
>>>
```

Items or slices can be deleted from the buffer;

```python
>>> b = bytearray([x for x in range(1,17)])
>>> ub = ublob.ublob(b, buf=15, blocksize=15)
>>> del(ub[0])
>>> del(b[0])
>>> bytes(ub) == bytes(b)
True
>>>
>>> del(ub[:2])
>>> del(b[:2])
>>> bytes(ub) == bytes(b)
True
>>>
>>> del(ub[3:])
>>> del(b[3:])
>>> bytes(ub) == bytes(b)
True
>>>
>>> #test out of range
>>> del(ub[5:])
IndexError: index out of range
>>> del(b[5:])
>>> bytes(ub) == bytes(b)
True #still True as out of range ignorred by bytearray i.e. no change occured 
>>>```

#####ublob.buflen(size=None, shrink=False)

Get the buffer length;

```python
>>> len(ub)
16
>>> ub.buflen()
30
```

Grow the buffer to accomodate size as multiple of ublob.blocksize (no change if size<ublob.buflen()) and return the new buffer length;

```python
>>> ub.buflen(39)
45
```

Shrink buffer to nearest multiple of ublob.blocksize that can accomodate size (example is 'best fit for data'), won't shrink the buffer to less than len(ublob);

```python
>>> ub.buflen(len(ub),shrink=True)
30
```