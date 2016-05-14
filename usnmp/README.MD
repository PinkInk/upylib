#usnmp.py (micro Simple Network Protocol module)

SNMP packet codec for micropython, note: that an 'SNMP server' is not implemented, you need to send/recv packets independently, this will be covered in revised documentation 'imminently'.

Note: that I'm tinkering with this at the moment and it is not yet tested on micropython.

##Revision history

v2 - Tim Pelling 5/16 - code-size and mem use enhanced version (but refer to-do), targetting realistic use on micropython/esp8266

v1 - Tim Pelling 3/16 - initial PoC implementation, archived as v1_* files for posterity/functionality testing/memory metrics

##To-do

- re-implement utilisation of memoryview's, when ga release of micropython for esp8266 is available that doesn't have memoryview bug
- full 'ptr to buffered bytearray via memoryview' implementation