import random
import math
import time
import sys
from clock import Clock

# These libraries only load on the Pi, so we use dummy declarations
# to debug off the Pi.
try:
    from tm1637 import TM1637
    from gpiozero import PWMLED, Button
    RASPBERRY_PI = True
except Exception as e:
    from dummy import *
    RASPBERRY_PI = False
    print("Failed to import library: " + str(e))

# Change these constants to modify pins.
PIN_LED_R = 22
PIN_LED_G = 27
PIN_LED_B = 17

PIN_BUTTON_P1_R = 3
PIN_BUTTON_P1_G = 4
PIN_BUTTON_P2_R = 23
PIN_BUTTON_P2_G = 24

# clock timers
PIN_TIMER_1_CLK = 19
PIN_TIMER_1_DIO = 26
PIN_TIMER_2_CLK = 25
PIN_TIMER_2_DIO = 8

# score timers
PIN_TIMER_3_CLK = 6
PIN_TIMER_3_DIO = 13
PIN_TIMER_4_CLK = 15
PIN_TIMER_4_DIO = 18

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
STATE_HANDLE_SCORE      = 4
STATE_WAIT_TO_START     = 5

# Look-up tables
color_table = { # colors: ripeness, (R,G,B)
    "blue":              (UNRIPE, (0,   0,   255)),
    "green":             (UNRIPE, (0,   255, 0)),
    "candy apple red":   (RIPE,   (255, 0,   10)),
    "phoenician yellow": (RIPE,   (255, 128, 0)),
    "fuschia":           (RIPE,   (255, 0,   100)),
    "maroon":            (UNRIPE, (128, 0,   1)), # TODO: LED probably can't display this well
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
        self.r = PWMLED(PIN_LED_R)
        self.g = PWMLED(PIN_LED_G)
        self.b = PWMLED(PIN_LED_B)
        self.led = (self.r, self.g, self.b)

        # Button assignment
        self.red_button_1   = Button(PIN_BUTTON_P1_R)
        self.green_button_1 = Button(PIN_BUTTON_P1_G)
        self.red_button_2   = Button(PIN_BUTTON_P2_R)
        self.green_button_2 = Button(PIN_BUTTON_P2_G)

        self.first_press     = [0, 0]                             # stores when player first pressed button in nanoseconds
        self.input_pressed   = [None, None]                       # stores whether player pressed ripe or unripe      
        self.held            = [False, False]                     # tracks whether player is holding button

        def pressed(button):
            pin = button.pin.number
            if self.first_press[button_to_player[pin]] == 0 and self.held[button_to_player[pin]] == False:
                self.first_press[button_to_player[pin]] = float(time.time())
                self.input_pressed[button_to_player[pin]] = button_to_color[pin]
                self.held[button_to_player[pin]] = True
        
        def released(button):
            self.held[button_to_player[button.pin.number]] = False

        self.red_button_1.when_pressed = pressed
        self.green_button_1.when_pressed = pressed
        self.red_button_2.when_pressed = pressed
        self.green_button_2.when_pressed = pressed

        self.red_button_1.when_released = released
        self.green_button_1.when_released = released
        self.red_button_2.when_released = released
        self.green_button_2.when_released = released

        # Clock assignment
        self.tm1 = TM1637(clk=PIN_TIMER_1_CLK, dio=PIN_TIMER_1_DIO)
        self.tm2 = TM1637(clk=PIN_TIMER_2_CLK, dio=PIN_TIMER_2_DIO)
        self.clock = Clock(duration, self.tm1, self.tm2)

        # Score tracker assignment
        self.score_1 = TM1637(clk=PIN_TIMER_3_CLK, dio=PIN_TIMER_3_DIO)
        self.score_2 = TM1637(clk=PIN_TIMER_4_CLK, dio=PIN_TIMER_4_DIO)

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
            self.led[i].value = color_table[self.current_color][COLOR_RGB][i]/255

    def check_for_press(self):
        if self.first_press[PLAYER_1] == 0 and self.first_press[PLAYER_2] == 0:
            return False
        else:
            return True

    def get_fastest_player(self):
        if self.first_press[PLAYER_1] is None:
            return PLAYER_2
        elif self.first_press[PLAYER_2] is None:
            return PLAYER_1
        elif self.first_press[PLAYER_1] < self.first_press[PLAYER_2]:
            return PLAYER_1
        else:
            return PLAYER_2

    def check_input(self, answer, color):
        ripe = color_table[color][COLOR_RIPENESS]
        if answer == RIPE:
            return ripe
        elif answer == UNRIPE:
            return not ripe
        else: # None check
            return False
    
    def play(self):
        try:
            while True:
                if self.state == STATE_START:
                    self.do_intro()
                    self.clock.start()
                    self.score_1.number(0)
                    self.score_2.number(0)
                    self.display_color()
                    self.state = STATE_WAIT_FOR_INPUT

                elif self.state == STATE_WAIT_FOR_INPUT:
                    if self.check_for_press() == True:
                        self.state = STATE_CHECK_INPUT
                    if self.clock.get_time() <= 0:
                        self.state = STATE_HANDLE_SCORE
                        self.clock.stop()
                        print("Time's up!")
                        print("Score: " + str(self.scores))

                elif self.state == STATE_CHECK_INPUT:
                    first_player = self.get_fastest_player()
                    time.sleep(0.2) # give 200ms for other player to press

                    # Scoring gives the fastest correct player a point and removes
                    # points from any incorrect players.
                    if not self.input_pressed[first_player] is None:
                        if self.check_input(self.input_pressed[first_player], self.current_color):
                            self.scores[first_player] += 1
                        else:
                            if self.check_input(self.input_pressed[first_player ^ 1], self.current_color):
                                self.scores[first_player ^ 1] += 1
                            else:
                                if self.scores[first_player ^ 1] > 0: self.scores[first_player ^ 1] -= 1
                            if self.scores[first_player] > 0: self.scores[first_player] -= 1

                    self.score_1.number(self.scores[PLAYER_1]) # Write to timers
                    self.score_2.number(self.scores[PLAYER_2])
                    self.state = STATE_RESET_INPUTS

                if self.state == STATE_RESET_INPUTS:
                    self.first_press = [0, 0]
                    self.input_pressed = [None, None]
                    for i in range(len(self.led)):
                        self.led[i].off()
                    time.sleep(0.5) # Clear LED and wait for half a second.
                    self.display_color()
                    self.state = STATE_WAIT_FOR_INPUT

                if self.state == STATE_HANDLE_SCORE:
                    for i in range(len(self.led)):
                        self.led[i].off()
                    # if (self.scores[PLAYER_1] > self.scores[PLAYER_2]):
                    #    self.tm1.show('uuin')
                    # elif (self.scores[PLAYER_2] < self.scores[PLAYER_1]):
                    #    self.tm2.show('uuin')
                    # else:
                    #    self.tm1.show('tie')
                    #    self.tm2.show('tie')
                    time.sleep(1)
                    self.state = STATE_WAIT_TO_START

                if self.state == STATE_WAIT_TO_START:
                    if self.red_button_1.is_pressed or self.red_button_2.is_pressed or self.green_button_1.is_pressed or self.green_button_2.is_pressed:
                        self.scores = [0,0]
                        self.first_press = [0,0]
                        self.input_pressed = [None, None]
                        self.held = [True, True, True, True]
                        time.sleep(3)
                        self.state = STATE_START

        # Exit gracefully if interrupted.
        except KeyboardInterrupt:
            print("\n # Interrupted!")
            self.clock.stop()
            self.score_1.write([0, 0, 0, 0])
            self.score_2.write([0, 0, 0, 0])
            for i in range(len(self.led)):
                self.led[i].off()
            time.sleep(0.5)
            print("Score: " + str(self.scores))
            sys.exit()

if __name__=="__main__":
    game = Game()
    game.state = STATE_WAIT_TO_START
    game.play()
