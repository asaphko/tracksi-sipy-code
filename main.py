import pycom
import time
import os
import micropython
import state
import audiovisual
from state import State
from pytrack import Pytrack
from LIS2HH12 import LIS2HH12
from audiovisual import AV

# set aside mem for emergancy buffer
#micropython.alloc_emergency_exception_buf(100)

py = Pytrack()
state = State()
av = AV()

def main():
    # default sleep = 10 hours
    config = state.getState()
    if config['state'] >= 1:
        if config['state'] == 1:
            av.warning()
            state.trigger()
        else:
            if config['state'] == 2:
                state.notify()
                av.alarm()
            else:
                state.upone()
                av.alarm()
    #check BLE
    state.bt_check()
    #go to sleep
    py.setup_sleep(3600)
    py.go_to_sleep()

py.setup_int_wake_up(True, True)
acc = LIS2HH12()
# set accelereation threshold to 40mG and the min duration to 20ms
acc.enable_activity_interrupt(40, 20)

# check if we were awaken due to activity
if acc.activity():
    main()
