# extension : (mimetype, encoding)
types_map = {
    "htm"  :    ("text/html", None),
    "html" :    ("text/html", None),
    "css"  :    ("text/css", None),
    "txt"  :    ("text/plain", None),
    "xml"  :    ("application/xml", None),
    "js"   :    ("application/x-javascript", None),
    "pdf"  :    ("application/pdf", None),
    "py"   :	("text/x-python", None),
    "png"  :    ("image/png", None),
    "gif"  :    ("image/gif", None),
    "jpeg" :	("image/jpeg", None),
    "jpg"  :    ("image/jpeg", None),
    "bmp"  :	("image/x-ms-bmp", None),
}

def guess_type(url):
    # cpython mimetypes returns (None,None) 
    # if url contains query or fragment ...
    ext = url[ url.rfind(".")+1: ]
    if ext in types_map:
        return types_map[ext]
    else:
        return None,None