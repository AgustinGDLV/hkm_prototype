from gpiozero import LED, Button
# import tm1637
import time

r = LED(17)
g = LED(27)
b = LED(22)

r.on()
time.sleep(1)
r.off()

r.on()
g.on()
time.sleep(1)
b.on()

time.sleep(1)
r.off()
g.off()
b.off()


