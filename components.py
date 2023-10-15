from time import time, sleep
from machine import Pin


class FlowSensor:
    def __init__(self, sensor):
        self.count = 0 
        self.off_time = 0

        sensor.irq(trigger=Pin.IRQ_RISING, handler=self.increment)

        try: 
            with open("flow.txt", 'r') as f:
                self.count = int(f.read())
        except:
            pass 

    def increment(self):
        self.count += 1
        self.off_time = time() + 2
    
    def is_on(self):
        if time() < self.off_time:
            return True
        
        # save the count but set a 'window of opportunity' so it doesn't happen endlessly
        if self.off_time < time() < self.off_time + 3:
            with open("flow.txt", 'w') as f:
                f.write(str(self.count))



class Ionizer:
    def __init__(self, relays, pwm, pot):
        self.relays = relays
        self.pwm = pwm
        self.pot = pot
        self.max_power = 65536 * 0.5
        self.min_power = 65536 * 0.1

    def map_range(self, x, pot_min=0.25, pot_max=3.3):
        """Maps the potentionmeter voltage to the pwm value"""
        return (x - pot_min) * (self.max_power - self.min_power) // (pot_max - pot_min) + self.min_power
    
    def run(self, reverse=False):
        if reverse:
            self.relays(1)

        power = self.map_range(self.pot.read_u16() * 3.3 / 65536) 
        self.pwm.duty_u16(power)
    
    def stop(self):
        self.pwm.duty_u16(0)
        self.relays(0)



class DrainValve:
    def __init__(self, hall1, hall2, response, step1, step2, step3, step4):
        self.hall_1 = hall1
        self.hall_2 = hall2
        self.at_hall_1 = False
        self.at_hall_2 = False
        self.hall_response = response
        self.s1 = step1
        self.s2 = step2
        self.s3 = step3
        self.s4 = step4
        self.steps_pos = 0
        self.steps = [
            [0,0,0,1],
            [0,0,1,1],
            [0,0,1,0],
            [0,1,1,0],
            [0,1,0,0],
            [1,1,0,0],
            [1,0,0,0],
            [1,0,0,1],
            [0,0,0,0]
        ]

        # verify the shaft is in a good spot
        self.hall_1(1)
        if self.hall_response:
            self.at_hall_1 = True
        else:
            self.hall_2(1)
            if self.hall_response:
                self.at_hall_2 = True

        self.hall_1(0)
        self.hall_2(0)

        if not self.at_hall_1 or self.at_hall_2:
            self.hall_1(1)
            while not self.hall_response:
                self.step()

        self.at_hall_1 = True
        self.hall_1(0)
            
    def step(self):
        """If your motor just buzzes or runs incorrectly, the connections are probably wrong.
        In the software the steps need to be initialized as 1-3-2-4"""
        self.s1(self.steps[self.steps_pos][0])
        self.s2(self.steps[self.steps_pos][2])
        self.s3(self.steps[self.steps_pos][1])
        self.s4(self.steps[self.steps_pos][4])
        sleep(0.001)
        self.s1(0)
        self.s2(0)
        self.s3(0)
        self.s4(0)

        self.pos += 1 if self.pos < len(self.steps) else 0
    
    def toggle_drain(self):
        if self.at_hall_1:
            self.hall_2(1)
            while not self.hall_response:
                self.step()
        
            self.hall_2(0)
            self.at_hall_1 = False
            self.at_hall_2 = True

        elif self.at_hall_2:
            self.hall_1(1)
            while not self.hall_response:
                self.step()
        
            self.hall_1(0)
            self.at_hall_1 = True
            self.at_hall_2 = False
