#Remote Framebuffer Protocol for [Micropython](www.micropython.org)

_Unsecured_ micro [Remote Framebuffer Protocol](https://github.com/rfbproto/rfbproto/blob/master/rfbproto.rst) 
(RFB) server implementations (the protocol use by VNC)
for [Micropython](www.micropython.org) (and cpython), tested (to-date) only on micropython 
unix port (and cpython);

- [**rfb**](rfb)<BR/>
'micro' implementation for unix (hopefully WiPy) micropython ports, and cpython.

- [**urfb**](urfb)<BR/>
'nano' implementation for esp8266 micropython port. 

Refer README.md in each sub-directory for useage example walk-through and implementation specifics.

###Installation

Copy the desired micro (rfb) or nano (urfb) directory (less README.md) to the 
library path of your module or cpython distribution;

### Examples

In this directory;

|               |                                                                                     | target lib | cpython | mpy unix | mpy wipy | mpy esp8266 |
|---------------|-------------------------------------------------------------------------------------|------------|---------|----------|----------|-------------|
| typewriter.py | a simple typewriter, demonstrating/testing bitmap fonts, RawRect, CopyRect, RRERect | rfb        | yes     | yes      | yes      | no          |
| randomise.py  | demonstration/testing of RawRect fill() and setpixel() methods                      | rfb        | yes     | yes      | yes      | no          |
| randomrre.py  | demonstration/testing of RRERect's                                                  | rfb        | yes     | yes      | yes      | no          |
| snow.py       | demonstration of RRERect/RRESubRect animation                                       | rfb        | yes     | yes      | mem      | no          |
| bounce.py     | demonstration of RRERect/SubRect animation                                          | rfb        | yes     | yes      | yes      | no          |

###Known-Issues

- ~~true colours reversed i.e. (b,g,r) instead of (r,g,b)~~ (resolved)
- ~~indexed (colourmap) colour does not work~~ (resolved by removing support for it)

###TO-DO

- complete documentation
- testing on ~~WiPy &~~ Pyboard/cc3000
- implement nano version for esp8266 (/urfb)
