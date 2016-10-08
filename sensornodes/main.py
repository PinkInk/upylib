print('WAKEUP')

import machine, dht, time, json, ntptime
from umqtt.simple import MQTTClient

# ----------------------------------------------------------------
broker = '192.168.0.80'
broker_port = 1883
topic = '/ae/dxb/emirates_hills/springs1/street8/villa4/garden'
client = 't_h_probe'
# sleepfor = 30 # seconds
sleepfor = 60*10 # seconds
# ----------------------------------------------------------------

# json data structures
#  TODO: ntp timestamp?
payload_t = {
    'type': 'temperature',
    't': None,
    'raw_t': [],
    'timestamp': '',
}
payload_h = {
    'type': 'humidity',
    'h': None,
    'raw_h': [],
    'timestamp': '',
}

# power the sensor
print('SENSOR: POWER ON')
p12 = machine.Pin(12, machine.Pin.OUT)
p12.value(1)

# init sensor
print('SENSOR: INIT')
time.sleep(2)
d=dht.DHT11(machine.Pin(4))
time.sleep(2)

# 10 readings @ 2s
for i in range(10):
    try:
        d.measure()
        payload_t['raw_t'].append(d.temperature())
        payload_h['raw_h'].append(d.humidity())
        print('SENSOR: READ {} SUCCESS'.format(i+1))
    except:
        pass
        print('SENSOR: READ {} FAIL'.format(i+1))
    time.sleep(2)

# sensor off
print('SENSOR: POWER OFF')
p12.value(0)

# timestamp
print('SETTIME')
ntptime.settime() # UTC from pool0.ntp.org
payload_t['timestamp'] = payload_h['timestamp'] = \
    '{:0>4d}-{:0>2d}-{:0>2d}T{:0>2d}:{:0>2d}:{:0>2d}Z'.format(*time.localtime())

# average readings 
try:
    payload_t['t'] = sum(payload_t['raw_t']) / len(payload_t['raw_t'])
    payload_h['h'] = sum(payload_h['raw_h']) / len(payload_h['raw_h'])
except:
    pass

c = MQTTClient(client, broker, port=broker_port)
for _ in range(5):
    try:
        print('MQTT: CONNECTING ...')
        c.connect()
        print('MQTT: CONNECTION SUCCEEDED')
        break
    except:
        print('MQTT: CONNECTION FAILED')
        time.sleep(2)

try:
    c.ping()
    c.publish(topic, json.dumps(payload_t))
    c.publish(topic, json.dumps(payload_h))
    print('MQTT: MESSAGE SENT')
    c.disconnect()
except:
    print('MQTT: MESSAGE FAILED')

print('SLEEP')
rtc = machine.RTC()
rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
rtc.alarm(rtc.ALARM0, sleepfor*1000)
machine.deepsleep()