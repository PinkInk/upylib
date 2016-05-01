import binascii
import ublob

#fudge
a=ublob.ublob(buf=15,blocksize=20)
for i in range(15):
    a._mb[i] = i+1

a._last=14

