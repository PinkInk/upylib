try:
    from ucollections import namedtuple
except:
    from collections import namedtuple


# test http request for parameters required by rfc6455
# indicating request is request to create websocket
def is_websocket_request(request):
    opts = request.options
    if "Sec-WebSocket-Key" in opts \
            and "Upgrade" in opts \
                and opts["Upgrade"].lower() == "websocket" \
            and "Connection" in opts \
                and opts["Connection"].lower() == "upgrade" \
            and "Sec-WebSocket-Version" in opts \
                and opts["Sec-WebSocket-Version"] == "13" \
            and "Origin" in opts \
            and "Host" in opts \
            and request.ver.major >= 1 \
                and request.ver.minor >= 1:
        return True
    return False


Request = namedtuple("Request", ("method", "uri", "ver", "options", "data"))
HttpVer = namedtuple("HttpVer", ("major", "minor"))

def request(req, options, data=None):
    # method,path,ver = str(req.strip(), "utf-8").split(" ")
    method,path,ver = req.strip().split(b" ")
    return Request(
        method,
        uri(path),
        HttpVer(*map(int, ver.split(b"/")[1].split(b"."))),
        options,
        data
    )


# browser does not send uri fragments to server
Uri = namedtuple("Uri", ("path", "file", "query"))

def uri(uri):
    if uri.count(b"/") and uri.count(b".") and uri.rfind(b".") > uri.rfind(b"/"):
        path,file = uri.rsplit(b"/", 1)
    elif not uri.count(b"."):
        path,file = uri,b""
    else:
        path,file = b"", uri
    if path and path[0] == b"/":
        path = path[1:]
    # assume uri is valid and only contains one ?
    if file.count(b"?"):
        file,query = file.split(b"?")
    else:
        query = b""
    return Uri(path, file, query)

