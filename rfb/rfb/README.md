#(Micro) Remote Framebuffer Protocol for [Micropython](www.micropython.org)

Supports;
- multiple concurrent RFB Client sessions on micropython and cpython
- **true** (RGB8) and **indexed** (latter on To-Do list) colour
- sending commands ('encodings') to the RFB Client;
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

This following documentation walks through the components of the module 
building out an example micropython script which demonstrates all of the 
module features.

### RfbServer

```python
RfbServer(
    w, h, # width, height (in pixels) of the remote framebuffer
    colourmap = None, # colourmap as (colour1, colour2 ... colourn) or None for true-colour
    name = b'rfb', # name of the remote framebuffer (cannot be '')
    handler = RfbSession, # client session handler
    addr = ('0.0.0.0', 5900), # address and port to bind the server to (refer python socket.bind)
    backlog = 3 # number of queued connections allowed (refer python socket.listen)
)
```

_Note: RFB colourmap mode (i.e. indexed colour) is not currently supported, and 
should always be set to `None`._

**RfbServer.accept()** (Non-blocking)

Check for new incoming connections, and add an instance of **handler** to 
**RfbServer.sessions** (list) for each.

**RfbServer.service()** (Non-blocking)

'Service' each of the instances of **handler** in the **RfbServer.sessions** list, by
calling the handlers **service_msg_queue()** and **update()** methods. 

**RfbServer.serve()** (Blocking)

Call **RfbServer.accept()** and **RfbServer.service()** methods in a continous loop i.e.
accept and setup new sessions and service existing ones.

This is the normal method of starting the RFB server, however it is **blocking** 
therefore **accept()** and **service()** are exposed in order that they can be called
at user discretion within a custom main loop.

Example; set up and serve a simple 'do nothing', 150x150 pixel, rfb server 
bound to default RFB protocol port (5900) and all interfaces, ;

```python
import rfb
svr = rfb.RfbServer(150, 150, name='hello world')
svr.serve()
``` 

Multiple RFB Client sessions can be connected to this server, and will display
a 150x150 pixel main window with title 'hello world'.  

Note: the RFB protocol does not specify a default colour for pixels in the
client buffer, initial state (normally white or black) can vary between
RFB Client implementations, and cannot be assumed.

### RfbServer

Initialisation of `RfbSession` objects is normally handled by `RfbServer`.

```python
RfbSession(
    conn, # network connection object (refer python socket.accept)
    w, h, # server framebuffer width, height in pixels
    colourmap, # server colourmap as (colour1, colour2 ... colourn) or None for true-colour
    name # server framebuffer name (cannot be '')
)
```

**RfbSession.w** 

RFB width (in pixels) property

**RfbSession.h**

RFB height (in pixels) property

**RfbSession.colourmap** 

RFB colourmap (indexed colour - not currently working) or None for true-colour.

Colourmap is as a list 3-tuple's of 8-bit unisigned integer blue,green,red channel
values e.g. `[(0,0,0), (255,255,255), (255,0,0)]` for white, black, blue.

Blue, Green, Red (BGR) instead of Red, Green, Blue (RGB) colour representation
is an 'anomoly' of the current implementation.

**RfbSession.** - 

**RfbSession.** - 

**RfbSession.** - 
