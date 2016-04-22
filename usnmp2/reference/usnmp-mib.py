def pack_alphanum(s):
    b = b""
    for i in s:
        i = ord(i)
        if 48<=i<=57: 
            b += bytes([i-48])
        elif 65<=i<=90: 
            b += bytes([i-55])
        elif 97<=i<=122: 
            b += bytes([i-61])
    return b

def unpack_alphanum(b):
    s=""
    for i in b:
        if 0<=i<=9: 
            s += chr(i+48)
        elif 10<=i<=35:
            s += chr(i+55)
        elif 36<=i<=61: 
            s += chr(i+61)
    return s

s = "AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789"
a = pack_alphanum(s)
print(a)
b = unpack_alphanum(a)
print(b)
print(s==b)