import ujson

class Ionizer:
    def __init__(self, electrode_A_pin, electrode_B_pin, pwm_freq):
        self.electrode_A = electrode_A_pin
        self.electrode_B = electrode_B_pin
        self.last_cathode =  ''
        self.current_cathode =  ''
        self.total_cycles = 0
        self.pwm_freq = pwm_freq

    def _read_data(self):
        try: 
            open("ionizer_cycles.txt", 'r')
        except:
            with open("ionizer_cycles.txt", 'w') as f:
                f.write(ujson.dumps(
                    {
                        'current_cathode': 'A', 
                        'total_cycles': 0
                    }
                ))
        
        with open("ionizer_cycles.txt", 'r') as f:
            x = f.read()
            data = ujson.loads(x)
            self.last_cathode = data['current_cathode']
            self.total_cycles = data['total_cycles']
        
    def _write_data(self, data):
        with open("ionizer_cycles.txt", 'w') as f:
            f.write(ujson.dumps(data))

    def run(self):
        self._read_data()
        
        if self.last_cathode == 'A':
            # self.electrode_B(1)
            self.electrode_B.duty_u16(self.pwm_freq)
            self.current_cathode = 'B'
        else:
            # self.electrode_A(1)
            self.electrode_A.duty_u16(self.pwm_freq)
            self.current_cathode = 'A'
        
        self._write_data(
            {
                'current_cathode': self.current_cathode, 
                'total_cycles': self.total_cycles + 1
            }
        )
    
    def stop(self):
        self.electrode_A.duty_u16(0)
        self.electrode_B.duty_u16(0)
