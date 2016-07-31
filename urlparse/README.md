#Url parse module for [Micropython](http://www.micropython.org)

Derived from 
[urllib](# https://github.com/lucien2k/wipy-urllib/blob/master/urllib.py) for micropyhton 
(c) Alex Cowan.

Passed a url returns a `namedtuple` of components;

```python
scheme:[//host[:port]][/]path[/filename][?query]
```

##Example

```python
>>> from urlparse import urlparse
>>> url = urlparse("https://www.google.com:801/1/2/index.asp?a=1&b=2&c=3")
>>> url
Url(scheme='https', host='www.google.com', port='801', path='1/2', file='index.asp', query='a=1&b=2&c=3')
>>> url.scheme
'https'
>>> url.host
'www.google.com'
>>> url.path+"/"+url.file
'1/2/index.asp'
```

##TO-DO
* implement full url schema `scheme:[//[user:password@]host[:port]][/]path[?query][#fragment]`

