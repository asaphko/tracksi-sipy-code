from machine import PWM
import time
import pycom

class AV:
    def do(self, freq=2000, duty=0.1, duration=0.1, pause=0.1, repeat=1, color=0x0000ff):
        pycom.heartbeat(False)
        for i in range(repeat):
            pycom.rgbled(color)
            pwm = PWM(0, freq)
            pin = pwm.channel(0, pin='P10', duty_cycle=duty)
            time.sleep(duration)
            pycom.heartbeat(False)
            pin.duty_cycle(0)
            time.sleep(pause)

    def beep(self):
        self.do()

    def longbeep(self):
        self.do(2000,0.1,0.3,0,1,0x007f00)

    def warning(self):
        self.do(2000,0.7,0.2,1,2,0x7f0000)

    def alarm(self):
        self.do(2000,0.8,0.4,0.2,7,0x7f0000)

    def locked(self):
        self.do(2000,0.1,0.1,0.1,2,0x007f00)

    def unlocked(self):
        self.do(2000,0.1,0.1,0.1,3,0x007f00)

    def blue(self):
        pycom.heartbeat(False)
        pycom.rgbled(0x0000FF)

    def off(self):
        pycom.heartbeat(False)
