print('WAKEUP')

import machine, dht, time, json
from umqtt.simple import MQTTClient

broker = '192.168.0.80'
broker_port = 1883
client = 't_h_probe'
topic_t = '/ae/dxb/emirates_hills/springs1/street8/villa4/garden/temperature'
topic_h = '/ae/dxb/emirates_hills/springs1/street8/villa4/garden/humidity'

# DEBUG: remove  loop for production
while True:

    # json data structures
    #  TODO: ntp timestamp?
    payload_t = {
        't': None,
        'raw_t': [],
    }
    payload_h = {
        'h': None,
        'raw_h': []
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

    # average readings 
    try:
        payload_t['t'] = sum(payload_t['raw_t']) / len(payload_t['raw_t'])
        payload_h['h'] = sum(payload_h['raw_h']) / len(payload_h['raw_h'])
    except:
        pass

    c = MQTTClient(client, broker, port=broker_port)
    try:
        c.connect()
        c.publish(topic_t,json.dumps(payload_t))
        c.publish(topic_h,json.dumps(payload_h))
        c.disconnect()
        print('MQTT: PUBLISH SUCCEEDED!')
    except:
        print('MQTT: PUBLISH FAILED!')

    # debugging
    # TODO: deepsleep 10 mins
    time.sleep(30)
