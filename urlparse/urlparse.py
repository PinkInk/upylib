try: # micropython
    from ucollections import namedtuple
except: # cpython
    from collections import namedtuple

Url = namedtuple("Url", ("scheme", "host", "port", "path", "file", "query"))

# urlparse derived from
# https://github.com/lucien2k/wipy-urllib/blob/master/urllib.py
# (c) Alex Cowan <acowan@gmail.com>

# scheme:[//host[:port]][/]path[/filename][?query]
def urlparse(url):
    scheme,url = url.split("://") if url.count("://") else ("",url)
    host = url.split("/")[0]
    host,port = host.split(":") if host.count(":") else (host,"")
    path,query = "/",""
    if host != url:
        path = path.join(url.split("/")[1:])
        if path.count("?"):
            if path.count("?") > 1:
                raise Exception("malformed url, too many ?")
            path, query = path.split("?")
    if not path.count("/"):
        path,file = "", path
    elif path.rfind(".") > path.rfind("/"):
        path,file = path[:path.rfind("/")], path[path.rfind("/")+1:]
    else:
        file = ""
        if path[-1] == "/":
            path = path[:-1]
    path = path if path != "/" else ""
    return Url(scheme, host, port, path, file, query)
