from gpiozero import LED, Button
import tm1637
import time
from random import uniform
from threading import Thread

led = LED(4)
right_button = Button(14)
left_button = Button(23)
left_name = input('left player name is ')
right_name = input('right player name is ')

tm = tm1637.TM1637(clk=17, dio=18)  # Using GPIO pins 18 and 17
clear = [0, 0, 0, 0]  # Defining values used to clear the display

score = [0,0]
button_pressed = False
state = 0

def pressed(button):
	global state
	if state != 1:
		return

	if button.pin.number == 14:
		score[0] += 1
	else:
		score[1] += 1
	state = 2

right_button.when_pressed = pressed
left_button.when_pressed = pressed

time_out = time.time() + 20

def count_timer():
	while time_out - time.time() >= 0:
		tm.numbers(int(0), int(time_out - time.time()), colon=True)

thread = Thread(target = count_timer, args=())
thread.start()

while time.time() <= time_out:
	if state == 0:      # waiting for LED
		time.sleep(uniform(2,3))
		led.on()
		state = 1
	elif state == 1:    # waiting for press
		pass
	else: # state == 2 -- button pressed!
		print(f'{left_name}: {score[0]}')
		print(f'{right_name}: {score[1]}')
		led.off()
		state = 0

if score[0] > score[1]:
	print(f'{left_name} won with {score[0]} points')
	print(f'{right_name} had {score[1]} points')
else:
	print(f'{right_name} won with {score[1]} points')
	print(f'{left_name} had {score[0]} points')
