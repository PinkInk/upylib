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
                and opts["Upgrade"] == "websocket" \
            and "Connection" in opts \
                and opts["Connection"] == "Upgrade" \
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
    print(req)
    method,path,ver = str(req.strip(), "utf-8").split(" ")
    return Request(
        method,
        uri(path),
        HttpVer(*map(int, ver.split("/")[1].split("."))),
        options,
        data
    )


Uri = namedtuple("Uri", ("path", "file", "query", "frag"))

def uri(uri):
    if uri.count("/") and uri.count(".") and uri.rfind(".") > uri.rfind("/"):
        path,file = uri.rsplit("/", 1)
    elif not uri.count("."):
        path,file = uri,""
    else:
        path,file = "", uri
    if path and path[0] == "/":
        path = path[1:]
    # assume uri is valid and only contains one ?
    if file.count("?"):
        file,query = file.split("?")
    else:
        query = ""
    if query.count("#"):
        query,frag = query.split("#")
    elif file.count("#"):
        file,frag = file.split("#")
    else:
        frag = ""
    return Uri(path, file, query, frag)

