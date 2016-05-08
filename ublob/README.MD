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
>>> ub[0]
1
>>> ub[2]
3
>>> ub[:-3]
bytearray(b'\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r')
>>> ub[-3:-2]
bytearray(b'\x0e')
>>> ub[::2]
bytearray(b'\x01\x03\x05\x07\t\x0b\r\x0f')
```

Note; 
- not memoryviews, memoryviews would become inconsistent if the ublob was manipulated and could prevent internal operataions e.g. extending buffer
- the internal memoryview can be accessesed as ub._mb - but it is inadvisable to do so without extreme caution

Items and slices can be assigned to.  Including unequal slice assignments (but assignment to a slice with a step is not supported, and will raise an error).  Internally assignments occur by shifting data within the buffer, using a memoryview.  The buffer automatically grows, to the next adequate multiple of **blocksize**, if required to accomodate new data.  The buffer is never shrunk automatically (ref hereunder for an internal call which can be used to shrink the buffer if desirable).

Item assignment requires integers (just like bytearray);

```python
>>> ub[0]=10
>>> ub[0]=bytes([1,2,3])
TypeError: int in range(0,256) required

```

Bytes or bytearray's can be assigned to slices, there is no need for assignment length to equal slice length, the buffer may grow, if necessary;

```python
>>> ub[0:0]=bytes([1,2,3])
>>> ub[:-2]=bytes([1,2,3])
```

Unlike bytearrays ublob does not support assignment beyond the end of the valid data;

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
>>> del(ub[3])
>>> del(ub[2:3])
```

The buffer can be shrunk to fit the data by leveraging an internal call;

```python
>>> ub._buf_align(len(ub), shrink=True)
```