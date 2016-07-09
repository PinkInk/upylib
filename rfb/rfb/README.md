#Remote Framebuffer Protocol for [Micropython](www.micropython.org)

Supports;
- multiple concurrent RFB Client sessions on micropython and cpython
- **true** (RGB8) ~~and indexed~~ colour
- sending messages ('encodings') to the RFB Client;
    - **FrameBufferUpdate**_s_
        - **RawRect**_angle_ of pixels
        - **CopyRect**_angle_ from another area in the RFB 
        - block colour **RRERect**_angle_, optionally with **RRESubRect**_angle's_
    - cut buffer text
    - bell ring
- receiving messages from the RFB Client;
    - requests for RFB updates<BR/>
      _updates can be sent irrespective of whether a request is pending_
    - keyboard events
    - mouse events
    - paste buffer text
- bitmap fonts (6x8 and 4x6)

###Example walk-through

**Set up and serve a simple 'do nothing' RFB server bound to port 5900 (RFB Protocol default);**

```python
import rfb
svr = rfb.RfbServer(255, 255, name=b'hello world')
svr.serve()
``` 

Multiple RFB Client sessions can be connected to this server, and will display
a 255x255 pixel main window with title 'hello world'.  

_Note: the RFB protocol does not specify a default colour for pixels in the client buffer, initial state (normally white or black) can vary between RFB Client implementations, and cannot be assumed._

**Start building a custom session handler** which doesn't (yet) do any more than the above example;

```python
import rfb

class my_session(rfb.RfbSession):
    pass

svr = rfb.RfbServer(255, 255, handler=my_session, name=b'custom')
svr.serve()
```

Each time the main server loop cycles `RfbSession.update()` is called and
can be used to send rectangles of pixels encoded in various schemes to the
client.

**Over-ride `RfbSession.update()` and send a random rectangle on each cycle**
using RRERect encoding (an efficient encoding that tells the client to display
a rectangle of a single colour, without sending every pixel).;

```python
import rfb
# import the getrandbits for micropython or cpython
try:
    from urandom import getrandbits
except:
    from random import getrandbits

class my_session(rfb.RfbSession):

    # override init to add rectangles property to class instances
    def __init__(self, conn, w, h, name):
        super().__init__(conn, w, h, name)
        self.rectangles = []
    
    def update(self):
        # choose random dimensions;
        x,y = getrandbits(8), getrandbits(8)
        w = h = getrandbits(5)
        # co-erce x,y to ensure rectangle doesn't overflow
        # framebuffer size (client will error out if it does)
        x = x if x<self.w-w else x-w
        y = y if y<self.h-h else y-h
        # choose random colour;
        bgcolour = (getrandbits(8), getrandbits(8), getrandbits(8))
        self.rectangles.append(
            rfb.RRERect(
                x, y, 
                w, h, 
                bgcolour,
                # let the rectangle know the session properties
                # required for encoding to bytes (ref doc's)
                self.bpp, self.depth, 
                self.big, self.true,
                self.masks, self.shifts
            )
        )
        # send a framebuffer update to the client
        # ServerFrameBufferUpdate requires a list of rectangles to send ...
        self.send( rfb.ServerFrameBufferUpdate( self.rectangles ) )
        # once a rectangle is sent to the RFB it is persistent in the 
        # RFB until over-written, therefore we don't need to retain
        # ones we've already sent;
        self.rectangles.clear()

svr = rfb.RfbServer(255, 255, handler=my_session, name=b'custom')
svr.serve()
```

Overridding RfbSession.update() is useful for animations, but can be freely
mixed with sending server messages in response to events (client messages).

Client messages can be responded to by attaching methods to the session
class for example 'ClientPointerEvent(self, buttons, x, y)' will receive the state
of buttons, and pointer co-ordinates, of the mouse whilst the RFB Client window
is in focus.

**Add a mouse event handler to the my_session class;**

```python
class my_session(rfb.RfbSession):

    def __init__(self, conn, w, h, name):
        # ... same code as above    

    def update(self):
        # ... same code as above

    # respond to mouse events
    def ClientPointerEvent(self, buttons, x, y):
        w = h = 4
        # paint with the mouse
        if 0+w < x < self.w-w and 0+h < y < self.h-h:
            # self.send() is a shortuct to self.conn.send()
            self.send(
                rfb.ServerFrameBufferUpdate(
                    [
                        rfb.RRERect(
                            x, y,
                            w, h,
                            (255,255,255),
                            self.bpp, self.depth, 
                            self.big, self.true,
                            self.masks, self.shifts
                        )
                    ]
                )
            )
        # ring the bell if a button is pressed
        if buttons > 0:
            self.send(
                rfb.ServerBell()
            ) 
```

Text can be sent to the RFB Client using the built-in bitmap fonts **mono6x8** and
**mono4x6**.

Font classes implement the method **`getbitmap_str(ascii_character_code)`**
which returns a string of 1's and 0's that can be rendered into a `RawRect`.

**Write random characters to the RFB;**

```python
import rfb
from rfb.fonts.mono6x8 import mono6x8 as font
try:
    from urandom import getrandbits
except:
    from random import getrandbits

class AlphabetSoup(rfb.RfbSession):

    def __init__(self, conn, w, h, name):
        super().__init__(conn, w, h, name)
        # raw rectangle to hold character bitmap
        self.rectangle = rfb.RawRect(
                                   0, 0, font.w, font.h,
                                   self.bpp, self.depth, 
                                   self.big, self.true,
                                   self.masks, self.shifts
                                  )
        self.rectangles = [ self.rectangle ]

    def update(self):

        char = getrandbits(7)
        self.rectangle.x = getrandbits(8)//font.w*font.w
        self.rectangle.y = getrandbits(8)//font.h*font.h

        # just skip this update if character isn't implemented
        # or x/y less font width/height outside buffer
        if char > 32 \
                and char < 32+font.count() \
                and self.rectangle.x+font.w < self.w \
                and self.rectangle.y+font.h < self.h:
            
            # returns the character bitmap as a string of 1's and 0's
            bits = font.getbitmap_str(char)

            # set characer pixels in rectangle
            for idx, bit in enumerate(bits):
                self.rectangle.setpixel(
                    idx%font.w, idx//font.w,
                    (255,255,255) if int(bit) else (0,0,0)
                )

            self.send( rfb.ServerFrameBufferUpdate( self.rectangles ) )                


svr = rfb.RfbServer(255, 255, handler=AlphabetSoup, name=b'custom')
svr.serve()
```

### RfbServer class

```python
RfbServer(
    w, h, # width, height (in pixels) of the remote framebuffer
    name = b'rfb', # name of the remote framebuffer (cannot be '')
    handler = RfbSession, # client session handler
    addr = ('0.0.0.0', 5900), # address and port to bind the server to (refer micro/python socket.bind)
    backlog = 3 # number of queued connections allowed (refer python socket.listen)
)
```

**RfbServer.accept()** (Non-blocking)

Check for new incoming connections, and add an instance of **handler** to 
**RfbServer.sessions** (list) for each.

**RfbServer.service()** (Non-blocking)

'Service' each of the instances of **handler** in the **RfbServer.sessions** list, by
calling the handlers **service_msg_queue()** and **update()** methods. 

**RfbServer.serve()** (Blocking)

Call **RfbServer.accept()** and **RfbServer.service()** methods in a loop i.e.
accept and setup new sessions and service existing ones.

`RfbServer.serve()` is the 'normal' method of starting the RFB server, however it is **blocking** 
therefore **accept()** and **service()** are exposed in order that they can be called
at user discretion within a custom main loop.

### RfbServer class

Initialisation of `RfbSession` objects is normally handled by `RfbServer`.

```python
RfbSession(
    conn, # network connection object (refer python socket.accept)
    w, h, # server framebuffer width, height in pixels
    name # server framebuffer name (cannot be '')
)
```

**RfbSession.conn** and **RfbSession.addr**

Raw python socket connection and address.

_Note: not expected to be used directly (refer send and recv methods) or overridden in user sub-class implementations._  

**RfbSession.w** 

RFB width (in pixels) property

**RfbSession.h**

RFB height (in pixels) property

**RfbSession.bpp**

Bits per pixel, may be either 8, 16 or 32 but is constrained by implementation to 32.

**RfbSession.depth**

Number of significant (used) bits in Bits Per Pixel.

Constrained by implementation 24 (as 3 x 8-bit colour channels for Red, Green, Blue).

**RfbSession.big**

Endianness of session.

This is negotiated between server and client during session init.  

**RfbSession.true** == True

Session is true-colour? (alternative; indexed (colourmap) is not implemented).  

**RfbSession.masks**

3-tuple of bitmasks to extract each colour channel from a true-colour pixel.

Constrained by implementation to (255, 255, 255) 

**RfbSession.shifts**

3-tuple of bit shift values to rotate each colour channel out of a pixel value.

Constrained by implementation to (16, 8, 0).

**RfbSession.security** == 1 (read-only)

Session security type (1 == None i.e. No Security)

**RfbSessions.encodings**

If the client sends a list of rectangle encodings that it supports (it normally
will) this list will be populated with them.

This list can be checked for the constants `rfb.RAWRECT`, `rfb.COPYRECT` and `rfb.RRERECT`
(corresponding to the rectangle encodings `rfb.RawRect`, `rfb.CopyRect and `rfb.RRERect`)
in order to ensure that the Client supports any given encoding.

However; VNC/RFB Clients are **required** to implement all three encodings included
in this library, hence checking is superfluous (until proven otherwise).

**RfbSession.recv(blocking=False)**

Wait for (if blocking=True, which is required by the internals of the 
protocol initialisation phase) receive and return any bytes received from the 
RFB Client.

_Note: not expected to be used directly, or over-ridden by user sub-class implementations._

**RfbSession.send(bytes)**

Send bytes to the RFB Client (shortcut to RfbSession.conn.send()).

**RfbSession.service_msg_queue()**

Dispatch queue of messages from RFB Client to optional user-implemented handler methods;

- **ClientSetPixelFormat**(self, bpp, depth, big, true, masks, shifts)<BR/>
  _Called when Client asks to set pixel format, unlikely to be overridden by user implementation, used during session init to signal client pixel properties_

```python
rfb.RfbSession.ClientSetPixelFormat(self,
    bpp, # bits-per-pixel (8, 16 or 32)
    depth, # number of bits in bpp that actually contain colour data (i.e. 24 or RGB8)
    big, # big-endian True/False
    true, # true-colour True/False
    masks, # bitmasks for each colour value in colour (i.e. (255,255,255) for RGB8)
    shifts # bits to rotate pixel data in order to get each channel to LSB (i.e. (16,8,0) for RGB8) 
)
```

- **ClientSetEncodings**(self, encodings)<BR/>
  _Called when Client asks to set encodings - Unlikely to be overridden by user implementation, used during session init to signal client supported encodings_
- **ClientFrameBufferUpdateRequest**(self, incr, x, y, w, h)<BR/>
  _Called when the client requests a frame-buffer update, normally ignorred as updates can be sent whether a request is pending service or not_
- **ClientKeyEvent**(self, down, key)<BR/>
  _Called on RFB Client keyboard event, when client window has focus_
- **ClientPointerEvent**(self, buttons, x, y)
  _Called on RFB Client mouse event, when client window has focus_
- **ClientCutText**(self, text)
  _Called when copy-buffer text is pasted into the Client window_
- **ClientOtherMsg**(self, msg)
  _Called when the session receives a message it doesn't know how to handle - if implemented must return the length of the message encoding_

### Server Messages

Server messages take relevant arguments and return bytes representation encoded as
required by the RFB Protocol, to be sent to the VNC/RFB Client by **RfbSession.send()**.

**ServerSetPixelFormat(bpp, depth, big, true, masks, shifts)**

Only used during session init, to communicate servers preference for pixel fomat,
often overruled by corresponding ClientSetPixelFormat message from client.

**ServerFrameBufferUpdate(rectangles)**

Return the members of list **rectangles** encoded as bytes, each member of the list
must be an instance of one of the classes described under **Encodings** hereunder.

**ServerBell()**

Return message bytes required to cause client to ring bell/beep.

**ServerCutText(text)**

Send text to the VNC/RFB Clients copy buffer.

### Encodings

The RFB protocol allows for sending arbitary rectangles of updated pixels to the 
Remote Framebuffer, with a number of differenet encodings with different purposes.

Only a small subset of simple/efficient Encoding specified in the RFB Protocol are implemented.

#### RawRect class

A rectangle of specific pixel colours, each of which can be individually set or flood filled, before sending to the VNC/RFB Client.

_Note: this class maintains, and sends on the wire, a mutable buffer of pixel values, and is therefore expensive in terms of memory consumption and network bandwiddth.  For e.g. a RawRect of width/height 20/20 consumes 1.5Kb Ram._

_Therefore RawRect should be used sparingly and only as an option of last resort when one of the other encodings won't suffice._

```python
rfb.RawRect(
    x, y, # x,y co-ordinates, in pixels, of the top-left corner of the rectangle, in relation to the clients framebuffer
    w, h, # width and height of the rectangle, in pixels
    bpp, depth, # session bits-per-pixel and depth
    big, true, # session endianess and true-colour flag values
    masks, shifts # session masks and shifts 3-tuples 
)
```

**RawRect.fill(colour)**

Fill the rectangle with pixels of colour (r,g,b).

**RawRect.setpixel(x, y, colour)**

Set pixel at x,y co-ordinate to colour (r,g,b).

**RawRect.to_bytes()**

Return bytes encoding of the rectangle.  

Normally called by `ServerFrameBufferUpdate(rectangles)` for each member of `rectangles` list.

#### CopyRect class

An efficient Encoding which instructs the client to copy a rectangle existing pixels from one point in the remote framebuffer to another.

```python
rfb.CopyRect(
    x, y, # x,y of top-left of target pixel rectangle
    w, h, # w,h of rectangle
    src_x, src_y, # x,y of source pixel rectangle 
)
``` 

#### RRERect class, and RRESubRect class

An efficient Encoding which instructs the client to paint an arbitary rectangle
of coloured pixels, optionally overlaid with RRESubRect's of different colours.

```python
rfb.RRERect(
    x, y, # x,y coordinates of top-left of rectangle, relative to framebuffer
    w, h, # rectangle width, height
    bgcolour, # rectangle colour (r,g,b) 
    bpp, depth, # session bits-per-pixel and depth
    big, true, # session endianess and true-colour flag values
    masks, shifts # session masks and shifts 3-tuples 
)
```

**RRERect.subrectangles** is a list of subrectangles of different colours which _must_ be
of type `rfb.RRESubRect`

```python
rfb.RRESubRect(
    x, y, # x,y coordinates of top-left of rectangle, relative to parent RRERect
    w, h, # rectangle width, height (x+w and y+h must be less than width and height of parent RRERect) 
    colour, # rectangle colour (r,g,b) 
    bpp, depth, # session bits-per-pixel and depth
    big, true, # session endianess and true-colour flag values
    masks, shifts # session masks and shifts 3-tuples 
)
```
