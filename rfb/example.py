import rfb

class my_session(rfb.RfbSession):
    pass

svr = rfb.RfbServer(150, 150, handler=my_session, name=b'custom')
svr.serve()
