#Remote Framebuffer Protocol for [Micropython](www.micropython.org)

_Unsecured_ micro [Remote Framebuffer Protocol](https://github.com/rfbproto/rfbproto/blob/master/rfbproto.rst) 
(RFB) server implementations (the protocol used by VNC)
for [Micropython](www.micropython.org) (and cpython).

- [**rfb**](rfb)<BR/>
for micropython ports with networking and reasonable RAM reserves (tested on unix and WiPy), and cpython.

- [**urfb**](urfb)<BR/>
for esp8266 micropython port. 

Refer README.md in each sub-directory for useage example walk-through and library details.

###Installation

Copy the directory (less README.md) to the library path of your module, or cpython, distribution.

### Examples

|               |                                                                                     | target lib | cpython | mpy unix | mpy wipy | mpy esp8266 |
|---------------|-------------------------------------------------------------------------------------|------------|---------|----------|----------|-------------|
| typewriter.py | a simple typewriter, demonstrating/testing bitmap fonts, RawRect, CopyRect, RRERect | rfb        | yes     | yes      | yes      | no          |
| randomise.py  | demonstration/testing of RawRect fill() and setpixel() methods                      | rfb        | yes     | yes      | yes*     | no          |
| randomrre.py  | demonstration/testing of RRERect's                                                  | rfb        | yes     | yes      | yes*     | no          |
| snow.py       | demonstration of RRERect/RRESubRect animation                                       | rfb        | yes     | yes      | mem*     | no          |
| bounce.py     | demonstration of RRERect/SubRect animation                                          | rfb        | yes     | yes      | yes      | no          |
! esp_bounce.py ! demo of urfb (still WIP) for esp8266 micropython port                               ! urfb       ! no      ! no       ! no       ! yes         !

*demo's purposefully constrained to work within limited RAM available on WiPy

###Known-Issues

- ~~true colours reversed i.e. (b,g,r) instead of (r,g,b)~~ (resolved)
- ~~indexed (colourmap) colour does not work~~ (resolved by removing support for it)

###TO-DO

- complete documentation
- testing on ~~WiPy &~~ Pyboard/cc3000
- ~~implement nano version for esp8266 (/urfb)~~ (still being refined)
