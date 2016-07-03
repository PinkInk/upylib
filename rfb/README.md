#Remote Framebuffer Protocol for [Micropython](www.micropython.org)

_Unsecured_ micro Remote Framebuffer Protocol (RFB) implementations, and examples,
for [Micropython](www.micropython.org), tested (to-date) only on micropython 
unix port.

- [**rfb**](rfb) directory<BR/>
'micro' implementation for unix (hopefully WiPy) micropython ports. 

- [**urfb**](urfb) directory<BR/>
'nano' implementation for esp8266 micropython port. 

Refer README.md in each sub-directory for implementation specifics.
Python files in this directory contain examples and functionality tests.

**Installation**

Copy the desired micro (rfb) or nano (urfb) directory (less README.md) to the 
library path of your module and;

```python
>>> import rfb
```

**Known-Issues**

- true colours reversed i.e. (b,g,r) instead of (r,g,b)
- indexed colour does not work (may be resolved by removing support)

**TO-DO**

- documentation
- testing on WiPy & Pyboard with cc3000
- paired-down micro version for esp8266 (/urfb)
