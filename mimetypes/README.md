#Minimal mimetypes module for [Micropython](http://www.micropython.org)

Passed a url returns a `tuple` of `mimetype` and `encoding`;

```python
>>> import mimetypes
>>> mimetypes.guess_type("index.html")
('text/html', None)
>>> mimetypes.guess_type("https://www.google.com:8080/1/e/test.png")
('image/png', None)
>>>
>>>
>>> # like cpython mimetypes does not handle 
>>> # url query or fragment gracefully
>>> mimetypes.guess_type("https://www.google.com:8080/1/e/test.png?a=1")
(None, None)
>>> mimetypes.guess_type("https://www.google.com:8080/1/e/test.png#index")
(None, None)
>>>
>>>
>>> # the built in types map
>>> for key in mimetypes.types_map: print(key,mimetypes.types_map[key])
...
xml ('application/xml', None)
gif ('image/gif', None)
bmp ('image/x-ms-bmp', None)
py ('text/x-python', None)
jpg ('image/jpeg', None)
html ('text/html', None)
txt ('text/plain', None)
css ('text/css', None)
js ('application/x-javascript', None)
bin ('application/octet-stream', None)
jpeg ('image/jpeg', None)
htm ('text/html', None)
png ('image/png', None)
pdf ('application/pdf', None)
>>>
>>>
>>> # add a type
>>> mimetypes.types_map["bin"] = ("application/octet-stream",None)
>>> mimetypes.guess_type("test.bin")
('application/octet-stream', None)
```


