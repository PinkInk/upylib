import uctypes

#ServerInit
desc = {
    'width' : uctypes.UINT16 | 0,
    'height': uctypes.UINT16 | 2, 
}

data = bytearray( uctypes.sizeof(desc) )

si = uctypes.struct(
    uctypes.addressof(data),
    desc,
    uctypes.BIG_ENDIAN
)

si.width=24
si.height=26

bytes(si)