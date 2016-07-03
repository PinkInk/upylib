from rfb.utils import *

def dispatch_msgs(self, msg):

    # handle multiple messages
    ptr = 0
    while ptr < len(msg):

        # ClientSetPixelFormat(self, bpp, depth, big, true, masks, shifts)
        if msg[ptr] == 0:
            if hasattr(self, 'ClientSetPixelFormat'):
                self.ClientSetPixelFormat(
                    msg[ptr+4],
                    msg[ptr+5],
                    msg[ptr+6] == 1,
                    msg[ptr+7] == 1,
                    (
                        bytes_to_int( msg[ptr+8:ptr+10] ),
                        bytes_to_int( msg[ptr+10:ptr+12] ),
                        bytes_to_int( msg[ptr+12:ptr+14] ),
                    ),
                    (
                        msg[ptr+14],
                        msg[ptr+15],
                        msg[ptr+16]
                    )
                )
            ptr += 20 # includes trailing padding

        # ClientSetEncodings(self, encodings)
        elif msg[ptr] == 2:
            count = bytes_to_int( msg[ptr+2:ptr+4] )
            encodings = [
                bytes_to_int( msg[ptr+4+i : ptr+8+i] )
                for i in range(0, count*4, 4)
            ]
            self.encodings = encodings
            if hasattr(self, 'ClientSetEncodings'):
                self.ClientSetEncodings(encodings)
            ptr += 4 + (count*4)

        # ClientFrameBufferUpdateRequest(self, incr, x, y, w, h)
        elif msg[ptr] == 3:
            if hasattr(self, 'ClientFrameBufferUpdateRequest'):
                self.ClientFrameBufferUpdateRequest(
                    msg[ptr+1] == 1,
                    bytes_to_int( msg[ptr+2:ptr+4] ),
                    bytes_to_int( msg[ptr+4:ptr+6] ),
                    bytes_to_int( msg[ptr+6:ptr+8] ),
                    bytes_to_int( msg[ptr+8:ptr+10] )
                )
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

        # ClientCutText(self, text)
        elif msg[ptr] == 6:
            l = bytes_to_int( msg[2:6] )
            if hasattr(self, 'ClientCutText'):
                self.ClientCutText(
                    msg[ptr+6 : ptr+l]
                )
            ptr += 6 + len

        elif msg[ptr] > 6 and hasattr(self, 'ClientOtherMsg'):
            # skip all messages
            # ... no way to tell how long the msg is ... 
            ptr = len(msg)