import snmpv1
import time

s=snmpv1.snmpv1("192.168.1.1","public")
# 3 - eth0
# 4 - eth1
# 5 - vlan0
# 6 - vlan1 - wan interface
# 7 - br0   - lan interface
# 8 - etherip0
s.mibs.append("1.3.6.1.2.1.2.2.1.10.6")
s.mibs.append("1.3.6.1.2.1.2.2.1.16.6")
s.mibs.append("1.3.6.1.2.1.2.2.1.10.7")
s.mibs.append("1.3.6.1.2.1.2.2.1.16.7")
s.mibs.append("1.3.6.1.2.1.1.3.0")

mr = s.poll()
ots = mr["1.3.6.1.2.1.1.3.0"]
oib106 = mr["1.3.6.1.2.1.2.2.1.10.6"]
oib166 = mr["1.3.6.1.2.1.2.2.1.16.6"]
oib107 = mr["1.3.6.1.2.1.2.2.1.10.7"]
oib167 = mr["1.3.6.1.2.1.2.2.1.16.7"]

while True:
    time.sleep(1)
    try:
        mr = s.poll()
        ts = mr["1.3.6.1.2.1.1.3.0"]
        ib106 = mr["1.3.6.1.2.1.2.2.1.10.6"]
        ib166 = mr["1.3.6.1.2.1.2.2.1.16.6"]
        ib107 = mr["1.3.6.1.2.1.2.2.1.10.7"]
        ib167 = mr["1.3.6.1.2.1.2.2.1.16.7"]
        print(6,((ib106-oib106)*8//(ts-ots))*100, ((ib166-oib166)*8//(ts-ots))*100)
        print(7,((ib107-oib107)*8//(ts-ots))*100, ((ib167-oib167)*8//(ts-ots))*100)
        #print("10: " + str((ib10-oib10)*8) + "b in " + str(ts-ots) + "/100s = " + \
        #        str( \
        #            ((ib10-oib10)*8//(ts-ots))*100 \
        #        ) + "bps" \
        #     )
        #print("16: " + str((ib16-oib16)*8) + "b in " + str(ts-ots) + "/100s = " + \
        #        str( \
        #            ((ib16-oib16)*8//(ts-ots))*100 \
        #        ) + "bps" \
        #     )
        ots=ts
        oib106=ib106
        oib166=ib166
        oib107=ib107
        oib167=ib167
    except:
        pass
