from machine import Pin, PWM
from time import time
import ujson
from components import Ionizer, DrainValve

MAX_COUNT = 25000
flow_sensor = Pin(28, Pin.IN, Pin.PULL_DOWN)
COUNT = 0
OFF_TIME = 0

signal_led = PWM(Pin(16))
potentiometer = Pin(17)
polarity_relays = Pin(18)
ionizer_pwm = PWM(Pin(19))
ionizer_pwm.freq(1000)
ionizer = Ionizer(polarity_relays, ionizer_pwm, potentiometer, signal_led)
POLARITY = True

try: 
    with open("flow.txt", 'r') as f:
        x = f.read()
        data = ujson.loads(x)
        COUNT = data['count']
        POLARITY = data['polarity']
except:
    pass 

def counter(flow_sensor):
    global COUNT, OFF_TIME
    COUNT += 1
    print(COUNT)
    OFF_TIME = time() + 2

flow_sensor.irq(trigger=Pin.IRQ_RISING, handler=counter)

# use the OFF_TIME to see if the water is running
while True:
    if time() < OFF_TIME:
        # waters running
        ionizer.run(POLARITY)



    else:
        ionizer.stop()
        if COUNT > MAX_COUNT:
            COUNT = 0
            POLARITY = not POLARITY

        with open("flow.txt", 'w') as f:
            f.write(ujson.dumps(
                {
                    'count': str(COUNT), 
                    'polarity': POLARITY
                }
            ))


