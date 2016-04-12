import socket
import usnmp
import sys
import time

iso = 1
org = 3
dod = 6
internet = 1
mgmt = 2
mib-2 = 1
    system = 1
    interfaces = 2
    at = 3
    ip = 4
    icmp = 5

def sysDescr():
    return (usnmp.ASN1_OCTSTR,
        sys.implementation.name + " v" + sys.version + " on " + sys.platform
    )

def sysUptime():
    return (usnmp.SNMP_TIMETICKS, time.tick_ms*10)

def sysName():
    return (usnmp.ASN1_OCTSTR, sys.platform)

mib={
    "1.3.6.1.2.1.1.1.0": sysDescr,
    "1.3.6.1.2.1.1.3.0": sysUptime,
    "1.3.6.1.2.1.1.4.0": (usnmp.ASN1_OCTSTR, "me@mydomain.com"),
    "1.3.6.1.2.1.1.5.0": sysName,
    "1.3.6.1.2.1.1.6.0": (usnmp.ASN1_OCTSTR, "Unknown"),
    "1.3.6.1.2.1.1.7.0": (usnmp.ASN1_INT, 2**(4-1)),
    "1.3.6.1.2.1.2.1.0": (usnmp.ASN1_INT, 1),
    "1.3.6.1.2.1.2.2.1.1.1": (usnmp.ASN1_iNT, 1),
    "1.3.6.1.2.1.2.2.1.2.1": (usnmp.ASN1_OCTSTR, "wlan"),
    "1.3.6.1.2.1.2.2.1.3.1": (usnmp.ASN1_INT, 6),
    "1.3.6.1.2.1.2.2.1.4.1": (usnmp.ASN1_iNT, 1500),
    "1.3.6.1.2.1.2.2.1.5.1": (usnmp., ),
    "1.3.6.1.2.1.2.2.1.6.1": (usnmp., ),
    "1.3.6.1.2.1.2.2.1.7.1": (usnmp., ),
    "1.3.6.1.2.1.2.2.1.8.1": (usnmp., ),
    "1.3.6.1.2.1.2.2.1.9.1": (usnmp., ),
    "1.3.6.1.2.1.2.2.1.10.1": (usnmp., ),
    "1.3.6.1.2.1.2.2.1.11.1": (usnmp., ),
    "1.3.6.1.2.1.2.2.1.12.1": (usnmp., ),
    "1.3.6.1.2.1.2.2.1.13.1": (usnmp., ),
    "1.3.6.1.2.1.2.2.1.14.1": (usnmp., ),
    "1.3.6.1.2.1.2.2.1.15.1": (usnmp., ),
    "1.3.6.1.2.1.2.2.1.16.1": (usnmp., ),
    "1.3.6.1.2.1.2.2.1.17.1": (usnmp., ),
    "1.3.6.1.2.1.2.2.1.18.1": (usnmp., ),
    "1.3.6.1.2.1.2.2.1.19.1": (usnmp., ),
    "1.3.6.1.2.1.2.2.1.20.1": (usnmp., ),
    "1.3.6.1.2.1.2.2.1.21.1": (usnmp., ),
    "1.3.6.1.2.1.2.2.1.22.1": (usnmp., ),
}
