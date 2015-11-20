Minimal micropython http server for the WiPy.

Subclass and implement required HTTP responses, for e.g. GET, as methods.

Methods are passed request as list of bytearray lines in incoming request and must return tuple of HTTP response code as int, and body of response as string.
