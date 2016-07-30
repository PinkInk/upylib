from collections import namedtuple


Request = namedtuple("Request", ("method", "uri", "ver", "options", "data"))
# wipy doesn't support floats e.g. 1.1
HttpVer = namedtuple("HttpVer", ("major", "minor"))

def request(req, options, data=None):
    # return Request(*str(b.strip(), "utf-8").split(" "))
    method,uri,ver = str(req.strip(), "utf-8").split(" ")
    return Request(
        method,
        url(uri),
        HttpVer(*map(int, ver.split("/")[1].split("."))),
        options,
        data
    )


# urlparse derived from
# https://github.com/lucien2k/wipy-urllib/blob/master/urllib.py
# (c) Alex Cowan <acowan@gmail.com>
# 
# full url scheme:[//[user:password@]host[:port]][/]path[?query][#fragment]
# implemented url scheme:[//host[:port]][/]path[/filename][?query]
Url = namedtuple("Url", ("scheme", "host", "port", "path", "file", "query"))

def url(url):
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
