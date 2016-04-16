import usnmp
import socket

from sys import implementation
if implementation.name == "micropython":
    from machine import rng
    def _id(): 
        return machine.rng()
elif implementation.name == "cpython":
    from random import random
    def _id():
        return int(random()*0xffffffff)
else:
    raise Exception("unknown python implementation")

def get(agent=None, community="", oids=None, timeout=1, retries=3):

    if agent==None or community=="" or oids==None:
        raise Exception("agent ip, community and oid to poll required")

    req = usnmp.SnmpPacket(type=usnmp.SNMP_GETREQUEST, community=community)

    if type(oids) is list:
        for oid in oids:
            req.varbinds[oid] = usnmp.ASN1_NULL, None
    else:
        req.varbinds[oids] = usnmp.ASN1_NULL, None

    req.id = _id()

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(timeout)

    resp = None
    for i in range(retries):
        try:
            s.sendto(req.packed, (agent, 161))
            d = s.recvfrom(1024)
        except socket.timeout:
            pass
        else:
            resp = usnmp.SnmpPacket(d[0])
            if resp.id == req.id:
                break

    if resp == None:
        raise Exception("no response, or invalid response, from agent")
    else:
        v = {}
        for oid in resp.varbinds:
            v[oid] = resp.varbinds[oid]
        return v