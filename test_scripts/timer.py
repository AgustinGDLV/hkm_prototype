# Importing modules and classes
import tm1637
import time
import numpy as np
from datetime import datetime
from gpiozero import CPUTemperature, LED

# Creating 4-digit 7-segment display object
tm = tm1637.TM1637(clk=15, dio=18)  # Using GPIO pins 18 and 17
clear = [0, 0, 0, 0]  # Defining values used to clear the display

#tm.write([127, 255, 127, 127])
tm.number(7788)
time.sleep(1)
tm.write(clear)

# Displaying a rolling string
# tm.write(clear)
# time.sleep(1)
# s = 'This is pretty cool'
# tm.scroll(s, delay=250)
# time.sleep(2)

# Displaying CPU temperature
# cpu = CPUTemperature()
# tm.write(clear)
# time.sleep(1)
# tm.temperature(int(np.round(cpu.temperature)))
# time.sleep(2)

# Displaying current time
# tm.write(clear)
# time.sleep(1)
# now = datetime.now()
# hh = int(datetime.strftime(now,'%H'))
# print(hh)
# mm = int(datetime.strftime(now,'%M'))
# tm.numbers(hh, mm, colon=True)
# time.sleep(2)
# tm.write(clear)
