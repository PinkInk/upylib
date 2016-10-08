def bytes_to_int(b): #big-endian
    i = 0
    for b8 in b:
        i <<= 8
        i += b8
    return i

def dispatch_msgs(self, msg):

    # handle multiple messages
    ptr = 0
    while ptr < len(msg):

        # ClientSetPixelFormat - handled directly
        if msg[ptr] == 0:
            self.bpp = msg[ptr+4]
            self.depth = msg[ptr+5]
            self.big = msg[ptr+6] == 1
            self.true = msg[ptr+7] == 1
            self.masks = (
                bytes_to_int( msg[ptr+8:ptr+10] ),
                bytes_to_int( msg[ptr+10:ptr+12] ),
                bytes_to_int( msg[ptr+12:ptr+14] ),
            )
            self.shifts = (msg[ptr+14], msg[ptr+15], msg[ptr+16]) 
            ptr += 20 # includes trailing padding

        # ClientSetEncodings - ignorred
        elif msg[ptr] == 2:
            ptr += 4 + (bytes_to_int( msg[ptr+2:ptr+4] )*4)

        # ClientFrameBufferUpdateRequest - ignorred
        elif msg[ptr] == 3:
            ptr += 10

        # ClientKeyEvent(self, down, key)
        elif msg[ptr] == 4:
            if hasattr(self, 'ClientKeyEvent'):
                self.ClientKeyEvent(
                    msg[ptr+1] == 1,
                    bytes_to_int( msg[ptr+4:ptr+8] )
                )
            ptr += 8

        # ClientPointerEvent(self, buttons, x, y)
        elif msg[ptr] == 5:
            if hasattr(self, 'ClientPointerEvent'):
                self.ClientPointerEvent(
                    msg[ptr+1],
                    bytes_to_int( msg[ptr+2:ptr+4] ),
                    bytes_to_int( msg[ptr+4:ptr+6] )
                )
            ptr += 6

        # ClientCutText - ignorred
        elif msg[ptr] == 6:
            ptr += 6 + bytes_to_int( msg[2:6] )

        # any other msg type, ignore all msgs
        elif msg[ptr] > 6:
            ptr = len(msg)
