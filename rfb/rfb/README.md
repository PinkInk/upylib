#(Micro) Remote Framebuffer Protocol for [Micropython](www.micropython.org)

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
    
    def update(self):
        x,y = getrandbits(8), getrandbits(8)
        w = h = getrandbits(5)
        # co-erce x,y to ensure rectangle doesn't overflow
        # framebuffer size (client will error out if it does)
        x = x if x<self.w-w else x-w
        y = y if y<self.h-h else y-h
        bgcolour = (getrandbits(8), getrandbits(8), getrandbits(8))
        rectangles = [
            rfb.RRERect(
                x, y, 
                w, h, 
                bgcolour,
                # let the rectangle know the session properties
                # required for encoding to bytes
                self.bpp, self.depth, self.true,
            )
        ]
        # send a framebuffer update to the client
        # ServerFrameBufferUpdate requires a list of rectangles to send ...
        self.send( rfb.ServerFrameBufferUpdate( rectangles ) )

svr = rfb.RfbServer(255, 255, handler=my_session, name=b'custom')
svr.serve()
```

Overridding RfbSession.update() is useful for animations, but can be freely
mixed with sending server messages in response to events (client messages).

Client messages can be responded to by attaching methods to the session
class for example 'ClientPointerEvent(self, buttons, x, y)' receives the state
of buttons and pointer co-ordinates of the mouse, whilst the RFB Client window
is in the foreground.

**Add a mouse event handler to the my_session class;**

```python
class my_session(rfb.RfbSession):
    
    def update(self):
        # ... same code as above

    # respond to mouse events
    def ClientPointerEvent(self, buttons, x, y):
        w = h = 4
        # paint with the mouse
        if 0+w < x < self.w-w and 0+h < y < self.h-h:
            self.send(
                rfb.ServerFrameBufferUpdate(
                    [
                        rfb.RRERect(
                            x, y,
                            w, h,
                            (255,255,255),
                            self.bpp, self.depth, self.true,
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





### RfbServer class

```python
RfbServer(
    w, h, # width, height (in pixels) of the remote framebuffer
    name = b'rfb', # name of the remote framebuffer (cannot be '')
    handler = RfbSession, # client session handler
    addr = ('0.0.0.0', 5900), # address and port to bind the server to (refer python socket.bind)
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

**RfbSession.big** = True (read-only)

Endianness of session i.e. big-endian long integers and words are used.

**RfbSession.bpp**

Bits per pixel, either 8, 16 or 32.

Constrained by implementation to 32 bits.

**RfbSession.depth**

Number of bits in Bits Per Pixel that actually contain colour information.

Constrained by implementation 24 (as 3 x 8-bit colour channels for Blue, Green & Red)

**RfbSession.shift**

3-tuple of bit shift values to rotate each colour channel out of a pixel value.

Constrained by implementation to (0, 8, 16).

_Note: irrespective of protocol endianness for true-colour these values are inverted by client (hence BGR instead of RGB)_

**RfbSession.security** = 1 (read-only)

Session security type (1 == None i.e. No Security)

**RfbSessions.encodings**

If the client sends a list of rectangle encodings that it supports (it normally
will) this list will be populated with them.

_Note: cannot gaurantee that this is populated immediately post session initialisation._

**RfbSession.recv(blocking=False)**

Wait for (if blocking=True, which is required by the internals of the 
protocol initialisation phase) receive and return any bytes received from the 
RFB Client.

_Note: not expected to be used directly, or over-ridden by user sub-class implementations._

**RfbSession.send(bytes)**

Send bytes to the RFB Client (a shortcut to RfbSession.conn.send()).

Might be used directly to send data 

