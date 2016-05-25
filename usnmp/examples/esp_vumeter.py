#-----------------------------------------------
# Display utilisation of selected remote agent
# interface on a string of neopixels, vu meter
# style.
#
# Requires: usnmp.py & usnmp_codec.py
#-----------------------------------------------
import gc, usnmp, time, socket, machine, neopixel
gc.collect()

def main():

    #-----------------------------------------------
    #RUN PARAMETERS ... edit;
    #
    #agent to poll
    agent_ip = "192.168.1.1"
    agent_port = 161
    agent_community = "public"
    #oid of interface in/out octet to monitor
    #   "1.3.6.1.2.1.2.2.1.10.6" == ifInOctets::6
    #   (my home routers wan interface, vlan1)
    oid_if_inoct = "1.3.6.1.2.1.2.2.1.10.6"
    #expected interface peak throughput in bps
    #   16Mbps;
    bandwidth=16*1024*1024
    #pin number that neopixel data-in is connected to
    np_pin = 4
    #number of neopixels in string
    np_count = 8
    #inter-poll delay, in seconds
    delay = 0.1
    #-----------------------------------------------

    #oid of agent uptime
    #   used to calculate throughput as bits per 1/100s
    #   use agent, rather than mcu (manager), time to 
    #   negate impact of nw latency
    oid_uptime = "1.3.6.1.2.1.1.3.0"

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

    gc.collect()

    greq = usnmp.SnmpPacket(type=usnmp.SNMP_GETREQUEST, community=agent_community, id=time.ticks_us())
    for i in (oid_uptime, oid_if_inoct):
        greq.varbinds[i] = None

    s.sendto(greq.tobytes(), (agent_ip, agent_port))
    d = s.recvfrom(1024)
    gresp = usnmp.SnmpPacket(d[0])

    while True:
    
        last_ut = gresp.varbinds[oid_uptime][1]
        last_in8 = gresp.varbinds[oid_if_inoct][1]

        gc.collect()

        time.sleep(delay)

        greq.id=time.ticks_us()
        s.sendto(greq.tobytes(), (agent_ip, agent_port))
        d = s.recvfrom(1024)

        gresp = usnmp.SnmpPacket(d[0])

        if greq.id == gresp.id:

            ut = gresp.varbinds[oid_uptime][1]
            in8 = gresp.varbinds[oid_if_inoct][1]

            bps = (in8-last_in8)//(ut-last_ut)*100*8
            level = bps*np_count//bandwidth

            for i in range(np_count):
                np[i] = vu[i] if level>i else (0,0,0)

            np.write()

main()