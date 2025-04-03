from gpiozero import PWMLED

color = [255, 255, 255]

r = PWMLED(22)
g = PWMLED(27)
b = PWMLED(17)

try:
    while True:
        raw = input('Enter color as "R G B": ')
        color = [float(x) for x in raw.split(' ')]
        r.value = color[0]/255.0
        g.value = color[1]/255.0
        b.value = color[2]/255.0
except:
    print('\n')
