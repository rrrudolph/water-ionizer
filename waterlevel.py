class WaterLevel:
    def __init__(self, pot, sensor):
        self.pot = pot
        self.sensor = sensor

    # Convert IR sensor readings to pot voltage
    def map_range(self, x, ir_empty=1.0, ir_full=2.3, pot_min=0.25, pot_max=3.3):
        return (x - ir_empty) * (pot_max - pot_min) // (ir_full - ir_empty) + pot_min

    def is_low(self):
        desired = self.pot.read_u16() * 3.3 / 65536
        level = self.map_range(self.sensor.read_u16() * 3.3 / 65536)
        if level < desired:
            print('is low')
            return True
        else:
            print('is full')
