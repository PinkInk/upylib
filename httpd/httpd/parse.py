try:
    from ucollections import namedtuple
except:
    from collections import namedtuple


Request = namedtuple("Request", ("method", "uri", "ver", "options", "data"))
HttpVer = namedtuple("HttpVer", ("major", "minor"))

def request(req, options, data=None):
    method,path,ver = str(req.strip(), "utf-8").split(" ")
    return Request(
        method,
        uri(path),
        HttpVer(*map(int, ver.split("/")[1].split("."))),
        options,
        data
    )


Uri = namedtuple("Uri", ("path", "file"))

def uri(uri):
    if uri.count("/") and uri.count(".") and uri.rfind(".") > uri.rfind("/"):
        path,file = uri.rsplit("/", 1)
    elif not uri.count("."):
        path,file = uri,""
    else:
        path,file = "", uri
    print(path,file)
    if path and path[0] == "/":
        path = path[1:]
    return Uri(path, file)
