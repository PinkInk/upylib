from esp import osdebug
osdebug(False)

def do_connect():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect('Opal', 'Indig01234')
        while not sta_if.isconnected():
            pass
    return sta_if.ifconfig()