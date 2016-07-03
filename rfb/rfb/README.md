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
    w, h, # width, height of the remote framebuffer
    colourmap = None, # colourmap as (colour1, colour2 ... colourn) or None for true-colour
    name = b'rfb', # name of the remote framebuffer (cannot be '')
    handler = RfbSession, # client session handler
    addr = ('0.0.0.0', 5900), # address and port to bind the server to (refer python socket.bind)
    backlog = 3 # number of queued connections allowed (refer python socket.listen)
)
```

