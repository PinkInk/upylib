#this file ignorred by micropython
import rfb

if __name__ == "__main__":
    s = rfb.RfbServer(160, 120, name=b'desktop')
    s.serve()

