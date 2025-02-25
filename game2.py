import random
import time
import sys
from clock import Clock

# These libraries only load on the Pi, so we use dummy declarations
# to debug off the Pi.
try:
    from tm1637 import TM1637
    from gpiozero import LED, Button
    RASPBERRY_PI = True
except Exception as e:
    from dummy import *
    RASPBERRY_PI = False
    print("Failed to import library: " + str(e))

# Change these constants to modify pins.
PIN_LED_R = 16
PIN_LED_G = 25
PIN_LED_B = 24

PIN_BUTTON_P1_R = 15
PIN_BUTTON_P1_G = 23
PIN_BUTTON_P2_R = 14
PIN_BUTTON_P2_G = 26

PIN_TIMER_1_CLK = 17
PIN_TIMER_1_DIO = 18
PIN_TIMER_2_CLK = 5
PIN_TIMER_2_DIO = 4

# Constants for readability
PLAYER_1 = 0
PLAYER_2 = 1
RIPE    = 0
UNRIPE  = 1

COLOR_RIPENESS  = 0 # for color table indices
COLOR_RGB       = 1

STATE_START             = 0 # for play state
STATE_WAIT_FOR_INPUT    = 1
STATE_CHECK_INPUT       = 2
STATE_RESET_INPUTS      = 3
STATE_END               = 4

# Look-up tables
color_table = { # colors: ripeness, (R,G,B)
    "blue":              (UNRIPE, (0,0,1)),
    "green":             (UNRIPE, (0,1,0)),
    "candy apple red":   (RIPE,   (1,0,0)),
    "phoenician yellow": (RIPE,   (1,1,0)),
    "fuschia":           (RIPE,   (1,0,1)),
    "maroon":            (UNRIPE, (1,1,1)), # TODO: LED probably can't display this well
}

button_to_player = {
    PIN_BUTTON_P1_G: PLAYER_1,
    PIN_BUTTON_P1_R: PLAYER_1,
    PIN_BUTTON_P2_G: PLAYER_2,
    PIN_BUTTON_P2_R: PLAYER_2,
}

button_to_color = {
    PIN_BUTTON_P1_G: RIPE,
    PIN_BUTTON_P1_R: UNRIPE,
    PIN_BUTTON_P2_G: RIPE,
    PIN_BUTTON_P2_R: UNRIPE,
}

class Game:
    def __init__(self, duration=30):
        # LED assignment
        self.r = LED(PIN_LED_R)
        self.g = LED(PIN_LED_G)
        self.b = LED(PIN_LED_B)
        self.led = (self.r, self.g, self.b)

        # Button assignment
        self.red_button_1   = Button(PIN_BUTTON_P1_R)
        self.green_button_1 = Button(PIN_BUTTON_P1_G)
        self.red_button_2   = Button(PIN_BUTTON_P2_R)
        self.green_button_2 = Button(PIN_BUTTON_P2_G)

        self.first_press     = [0, 0] # stores when player first pressed button in nanoseconds
        self.input_pressed   = [None, None] # stores whether player pressed ripe or unripe
        
        def pressed(button):
            pin = button.pin.number
            if self.first_press[button_to_player[pin]] == 0:
                self.first_press[button_to_player[pin]] = float(time.time())
                self.input_pressed[button_to_player[pin]] = button_to_color[pin]

        self.red_button_1.when_pressed = pressed
        self.green_button_1.when_pressed = pressed
        self.red_button_2.when_pressed = pressed
        self.green_button_2.when_pressed = pressed

        # Clock assignment
        self.tm1 = TM1637(clk=PIN_TIMER_1_CLK, dio=PIN_TIMER_1_DIO)
        self.clock = Clock(duration, self.tm1)

        # Misc. variables
        self.state = STATE_START
        self.scores = [0, 0]
        self.current_color = "blue"

    def do_intro(self):
        """ Game introduction for coding / debugging purposes.
            Note that for the actual exhbit, directions will be displayed
            on the wood.
        """
        print(" # Welcome to Ripe Reaction! The goal is to harvest more ripe "
              "cacao pods by being faster than your opponent.")
        print(" # Hit green button for ripe, red button for not ripe.")
        print(" # Ripe colors: ...\n")

    def display_color(self):
        self.current_color = random.choice(list(color_table.keys()))
        print("You find a %s cacao pod!" % self.current_color)

        # Update LEDs.
        for i in range(len(self.led)):
            if color_table[self.current_color][COLOR_RGB][i] == 1:
                self.led[i].on()
            else:
                self.led[i].off()

    def check_for_press(self):
        if self.first_press[PLAYER_1] == 0 and self.first_press[PLAYER_2] == 0:
            return False
        else:
            return True

    def get_fastest_player(self):
        if self.first_press[PLAYER_1] < self.first_press[PLAYER_2]:
            return PLAYER_1
        else:
            return PLAYER_2

    def check_input(self, answer, color):
        ripe = color_table[color][COLOR_RIPENESS]
        if answer == RIPE:
            return ripe
        elif answer == UNRIPE:
            return not ripe
        else:
            return False
    
    def play(self):
        try:
            while True:
                if self.state == STATE_START:
                    self.do_intro()
                    self.clock.start()
                    self.display_color()
                    self.state = STATE_WAIT_FOR_INPUT

                elif self.state == STATE_WAIT_FOR_INPUT:
                    if self.check_for_press() == True:
                        self.state = STATE_CHECK_INPUT
                    if self.clock.get_time() <= 0:
                        self.state = STATE_END
                        self.clock.stop()
                        print("Time's up!")
                        print("Score: " + str(self.scores))

                elif self.state == STATE_CHECK_INPUT:
                    first_player = self.get_fastest_player()
                    time.sleep(0.1) # give 100ms for other player to press
                    if self.check_input(self.input_pressed[first_player], self.current_color):
                        self.scores[first_player] += 1
                    elif self.check_input(self.input_pressed[first_player ^ 1], self.current_color) and self.first_press[first_player ^ 1] > 0:
                        self.scores[first_player ^ 1] += 1
                    self.state = STATE_RESET_INPUTS

                if self.state == STATE_RESET_INPUTS:
                    self.first_press = [0, 0]
                    self.input_pressed = [None, None]
                    for i in range(len(self.led)):
                        self.led[i].off()
                    time.sleep(0.5) # Clear LED and wait for half a second.
                    self.display_color()
                    self.state = STATE_WAIT_FOR_INPUT

                if self.state == STATE_END:
                    pass
                    # TODO: handle input between games

        # Exit gracefully if interrupted.
        except KeyboardInterrupt:
            print("\n # Interrupted!")
            self.clock.stop()
            for i in range(len(self.led)):
                self.led[i].off()
            time.sleep(0.5)
            print("Score: " + str(self.scores))
            sys.exit()

if __name__=="__main__":
    game = Game()
    game.play()
