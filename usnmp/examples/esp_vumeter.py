#-----------------------------------------------
# Display utilisation of selected remote agent
# interface on a string of neopixels, vu meter
# style.
#
# Requires: usnmp.py, usnmp_codec.py & neopixel_.py
#       (corrected neopixel driver - refer
#       forum.micropython.org)   
#-----------------------------------------------
#agent to poll
agent_ip = "192.168.1.1"
agent_port = 161
#oid of agent uptime
#   used to calculate throughput as bits per 1/100s
#   use agent, rather than mcu (manager), time to 
#   negate impact of nw latency
oid_uptime = "1.3.6.1.2.1.1.3.0"
#oid of interface in/out octet to monitor
#   "1.3.6.1.2.1.2.2.1.10.6" == ifInOctets::6
#   (my home routers wan interface, vlan1)
oid_if_inoct = "1.3.6.1.2.1.2.2.1.10.6"
#expected interface peak throughput per 1/100s
#   or trial and error in this case ;o)
peak=1200
#pin number that neopixel data-in is connected to
np_pin = 4
#number of neopixels in string
np_count = 8
#inter-poll delay, in seconds
delay = 0.1
#-----------------------------------------------

import gc, usnmp, time, socket, machine, neopixel_
gc.collect()

np = neopixel_.NeoPixel(machine.Pin(np_pin), np_count)

s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.settimeout(1)

vu = []
for i in range(np_count):
    if i < np_count*60//100:
        vu.append((0,100,0)) #green
    elif i < np_count*80//100:
        vu.append((100,15,0)) #orange
    else:
        vu.append((100,0,0)) #red 

greq = usnmp.SnmpPacket(type=usnmp.SNMP_GETREQUEST, id=time.ticks_us())
for i in (oid_uptime, oid_if_inoct):
    greq.varbinds[i] = None

s.sendto(greq.tobytes(), (agent_ip, agent_port))
d = s.recvfrom(1024)
gresp = usnmp.SnmpPacket(d[0])
last_ut = gresp.varbinds[oid_uptime][1]
last_in8 = gresp.varbinds[oid_if_inoct][1]

while True:
    gc.collect()
    time.sleep(delay)
    greq.id=time.ticks_us()
    s.sendto(greq.tobytes(), (b'192.168.1.1', 161))
    d = s.recvfrom(1024)
    gresp = usnmp.SnmpPacket(d[0])
    if greq.id == gresp.id:
        ts = gresp.varbinds[oid_uptime][1]
        in8 = gresp.varbinds[oid_if_inoct][1]
        v = int((((in8-last_in8)//(ts-last_ut))/peak)*8)
        for i in range(np_count):
            np[i] = vu[i] if v>=i else 0,0,0
        np.write()
        last_ut = ts
        last_in8 = in8
