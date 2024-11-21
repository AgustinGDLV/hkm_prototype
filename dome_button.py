from gpiozero import Button, LED

button = Button(23)

while True:
    if button.is_pressed:
        print("Button is pressed!")
    else:
        print("Button is not pressed.")
