#extension : (mimetype, isbinary?)
mimetypes = {
    "htm"  :    ("text/html", False),
    "html" :    ("text/html", False),
    "css"  :    ("text/css", False),
    "txt"  :    ("text/plain", False),
    "xml"  :    ("application/xml", False),
    "js"   :    ("application/x-javascript", False),
    "pdf"  :    ("application/pdf", True),
    "py"   :	("text/x-python", False),
    "png"  :    ("image/png", True),
    "gif"  :    ("image/gif", True),
    "jpeg" :	("image/jpeg", True),
    "jpg"  :    ("image/jpeg", True),
    "bmp"  :	("image/x-ms-bmp", True),
}

def type(file):
    return mimetypes[ file.split(".")[1] ]