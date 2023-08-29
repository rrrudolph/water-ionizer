from machine import Pin, PWM, ADC
from utime import sleep, time

# p0.on()                 # set pin to "on" (high) level
# p0.off()                # set pin to "off" (low) level
# led = Pin(25, Pin.OUT)
# while True:
#     led.on()
#     sleep(2)
#     led.off()
#     sleep(1)


# light_sensor = ADC(Pin(26))
# fan_power = Pin(2, Pin.OUT)
# fan_pwm = PWM(Pin(4, Pin.OUT))
# fan_pwm.freq(25000)


minute = 60
hour = 60 * minute

class WaterLevel:
    pot =    ADC(Pin(27))
    sensor = ADC(Pin(26))

    # Convert IR sensor readings to pot voltage
    def map_range(x, ir_empty=1.0, ir_full=2.3, pot_min=0.25, pot_max=3.3):
        return (x - ir_empty) * (pot_max - pot_min) // (ir_full - ir_empty) + pot_min

    def is_low():
        desired = WaterLevel.pot.read_u16() * 3.3 / 4096
        level = WaterLevel.map_range(WaterLevel.sensor.read_u16() * 3.3 / 4096)
        if level < desired:
            return True
        
class Ionizer:
    electrode_A =   PWM(Pin(13, Pin.OUT)).freq(100)
    electrode_B =   PWM(Pin(14, Pin.OUT)).freq(100)
    cathode_is_A =  True
    ionization_period = 0
    ionizer_turn_off_time = 0

    def increment_count():
        file = open("ionizer_cycles.txt", 'w+')
        count = file.read()
        count = int(count) + 1 if count else None
        file.write(str(count))
        file.close()

    def run():
        if Ionizer.cathode_is_A:
            Ionizer.electrode_A.duty_u16(0)
            Ionizer.electrode_B.duty_u16(int(0.5 * 65025))
        else:
            Ionizer.electrode_A.duty_u16(int(0.5 * 65025))
            Ionizer.electrode_B.duty_u16(0)
        
        sleep(Ionizer.ionization_period)
        Ionizer.electrode_A.duty_u16(0)
        Ionizer.electrode_B.duty_u16(0)
        Ionizer.cathode_is_A = not Ionizer.cathode_is_A
        Ionizer.increment_count()

class Chambers:
    fill_AB =           Pin(7, Pin.OUT)
    drain_alkaline_A =  Pin(8, Pin.OUT)  # B's acid drain will also connect to this pin
    drain_alkaline_B =  Pin(9, Pin.OUT)  # ...
    fill_period =       0
    drain_period =      0

    def open_valve(valve, period):
        valve.on()
        sleep(period)
        valve.off()
    
    def fill():
        Chambers.open_valve(Chambers.fill_AB, Chambers.fill_period)
    
    def drain():
        if Ionizer.cathode_is_A:
            Chambers.open_valve(Chambers.drain_alkaline_A, Chambers.drain_period)
        else:
            Chambers.open_valve(Chambers.drain_alkaline_B, Chambers.drain_period)



# check the water level
# if water level below desired level
# fill the chambers, sleeping for fill period
# run the ionizer, sleeping for run period, turn off ionizer
# check the value of Ionizer.cathode_is_A for which drains to activate
# drain the chambers, sleep for drain period


# weaknesses:
# 1. if system restarts when the ionizer chamber is full it will re-fill and waste all that water
    # - restarts are required because I want to run the vortexer, or the stir bar has disconnected. if I can fix those problems I won't need to restart
    # FIXES  - add a button to trigger the vortex
    #        - measure the fan speed to see when the stir bar has been thrown 
# 2. if the power goes out while I am filling the ionizer chamber it will overflow 
#     FIX - add ball valves to the entry ports


# ideas:
    # 1. web server showing pot reading, IR reading, ionizer cycles, approx total water usage, state (on/off)
    # 2. send a /disable request that will turn everything off (might need to run it on a diff core)
    # 3. put float valves on the chamber input lines 