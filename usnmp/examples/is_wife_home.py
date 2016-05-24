#-----------------------------------------------
# Display whether a "selected family member"
# is at, or approaching, home, by polling 
# routers Physical Address Table for their
# smartphone MAC Address.
#
# Requires: usnmp.py, usnmp_codec.py
#-----------------------------------------------
#agent to poll
agent_ip = "192.168.1.1"
agent_port = 161
#wifes (not my wifes) smartphone MAC Address
mac = b"f437b76dbc64"
#pin number that neopixel data-in is connected to
np_pin = 4
#number of neopixels in string
np_count = 8
#inter-poll delay, in seconds
delay = 1
#-----------------------------------------------
#the oids in the PAT table
oids_pat = ("1.3.6.1.2.1.3.1.1.1","1.3.6.1.2.1.3.1.1.2","1.3.6.1.2.1.3.1.1.3")
#the oid in the table that contains the mac
oid_mac = "1.3.6.1.2.1.3.1.1.2"
#the oid of the next entry after the end of the table
oid_next = "1.3.6.1.2.1.4.1.0"

import gc, usnmp, time, socket, machine, neopixel, ubinascii
gc.collect()

np = neopixel.NeoPixel(machine.Pin(np_pin), np_count)

s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.settimeout(1)

gc.collect()

greq = usnmp.SnmpPacket(type=usnmp.SNMP_GETNEXTREQUEST, id=time.ticks_us())
for oid in oids_pat: greq.varbinds[oid] = None

while True:
    
    gc.collect()
    
    #send the preformatted get request
    s.sendto(greq.tobytes(), (agent_ip, agent_port))
    d = s.recvfrom(1024)
    
    gresp = usnmp.SnmpPacket(d[0])
    
    #prime the loop
    ishome = False
    endpat = False
    while endpat == False:
    
        gc.collect()
        
        #walk the returned oid/values
        for oid in gresp.varbinds:
        
            #if this is the one that contains the mac
            if oid.startswith(oid_mac):
                #compare it to the mac we're searching for
                if ubinascii.hexlify(gresp.varbinds[oid][1]) == mac:
                    ishome = True
            
            #check for the end of the table
            if oid.startswith(oid_next):
                endpat = True 
        
        #turn the response into a request ...
        gresp.type = usnmp.SNMP_GETNEXTREQUEST
        gresp.id = time.ticks_us()
        #turn the oids into the right format
        for oid in gresp.varbinds: gresp.varbinds[oid] = None
        
        s.sendto(gresp.tobytes(), (agent_ip, agent_port))
        d = s.recvfrom(1024)
        gresp = usnmp.SnmpPacket(d[0])
    
    #light the led according to the
    for i in range(np_count):
        np[i] = (255,0,0) if ishome else (0,255,0)
    np.write()

    #wait before doing it again
    time.sleep(delay)

