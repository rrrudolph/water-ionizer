from machine import ADC, Pin, PWM
from ionizer import Ionizer
import utime

electrode_A =   PWM(Pin(14, Pin.OUT))
electrode_B =   PWM(Pin(15, Pin.OUT))
electrode_A.duty_u16(0)
electrode_B.duty_u16(0)
ionizer = Ionizer(electrode_A, electrode_B, int(0.5 * 65025))

while True:
    ionizer.run()
    utime.sleep(10)
    ionizer.stop()
