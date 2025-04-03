from gpiozero import Button, LED

def pressed(button):
    print("Button %d pressed!" % button.pin.number)

button1 = Button(3)
button2 = Button(4)
button3 = Button(23)
button4 = Button(24)

button1.when_pressed = pressed
button2.when_pressed = pressed
button3.when_pressed = pressed
button4.when_pressed = pressed

while True:
    pass
