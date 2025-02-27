from gpiozero import Button, LED

def pressed(button):
    print("Button %d% pressed!" % button.pin.number)

button1 = Button(18)
button2 = Button(24)
button3 = Button(25)
button4 = Button(26)

button1.when_pressed = pressed
button2.when_pressed = pressed
button3.when_pressed = pressed
button4.when_pressed = pressed

while True:
    pass
