# Adapted from
# https://github.com/lucien2k/wipy-urllib/blob/master/urllib.py
# (c) Alex Cowan <acowan@gmail.com>

def urlparse(url):
    scheme,url = url.split("://") if url.count("://") else ("",url) 
    host = url.split("/")[0]
    host,port = host.split(":") if host.count(":") else (host,"")
    path,query = "/", ""
    if host != url:
        path = path.join(url.split("/")[1:])
        if path.count("?"):
            if path.count("?") > 1:
                raise Exception("malformed url, too many ?")
            path, query = path.split("?")
    file = path.split("/")[path.count("/")]
    if file.count("."):
        path = "/".join(
            [dir for dir in path.split("/") if dir != ""][:-1]
        )
    else:
        file = ""
    path = path if path != "/" else ""
    return (scheme, host, port, path, file, query)
