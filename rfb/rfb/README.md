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
- bitmap fonts (6x8 and 4x6 implemented)
