uHTTPsrv
========
Minimal micropython http server for the WiPy.

Subclass and implement required HTTP responses, for e.g. GET, as class methods.

Methods are passed two arguments;
- a tuple of (ip4_address, port)
- the fully http request as list of bytearrays

And are expected to return a tuple of;
- HTTP response code as an integer
- reponse data/body as string or bytearray (or '' / b'')

uHTTPsrv will wrap the response code in a simple HTTP header, send it followed by the response body/data and close.

Call .serve_one() for testing, .serve() to serve forever.

Set .DEBUG=True to dump request/response to stdout/terminal.

myhttpsrv.py contains minimalist example.
