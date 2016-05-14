#usnmp.py (micro Simple Network Protocol module)

SNMP version1 packet codec for micropython (_not_ an SNMP 'server', you need to send/recv packets independently).

Note: I'm tinkering with this at the moment hence absence of documentation - the v1_* version (in v1 dir) is fully tested, and documented, but is exceedingly bloated and inneficient.

##Revision history

v2 - Tim Pelling 5/16 - enhanced, less bloated version (but refer to-do), targetting micropython/esp8266 useability

v1 - Tim Pelling 3/16 - initial PoC implementation, archived as v1/v1_* for posterity/functionality testing/memory metrics

##To-do

- re-implement utilisation of memoryview's, when ga release of micropython for esp8266 is available that doesn't have memoryview bug
- full 'ptr to buffered bytearray via memoryview' implementation (extension of techniques used in _VarBinds)