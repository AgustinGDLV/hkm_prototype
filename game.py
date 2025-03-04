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

PIN_BUTTON_R = 15
PIN_BUTTON_G = 23

PIN_TIMER_1_CLK = 17
PIN_TIMER_1_DIO = 18
PIN_TIMER_2_CLK = 5
PIN_TIMER_2_DIO = 4

# Constants for readability
COLOR_RIPENESS = 0
COLOR_RGB = 1

class Game:
    def __init__(self, duration=30):
        # LED assignment
        self.r = LED(PIN_LED_R)
        self.g = LED(PIN_LED_G)
        self.b = LED(PIN_LED_B)
        self.led = (self.r, self.g, self.b)

        # Button assignment
        self.red_button = Button(PIN_BUTTON_R)
        self.green_button = Button(PIN_BUTTON_G)

        # Clock assignment
        self.tm1 = TM1637(clk=PIN_TIMER_1_CLK, dio=PIN_TIMER_1_DIO)
        self.clock = Clock(duration, self.tm1)

        # Misc. variables
        self.score = 0
        self.current_color = "blue"
        self.last_input = "R"

        # Color table
        self.colors = { # colors: ripeness, (R,G,B)
            "blue":              (False, (0,0,1)),
            "green":             (False, (0,1,0)),
            "candy apple red":   (True,  (1,0,0)),
            "phoenician yellow": (True,  (1,1,0)),
            "fuschia":           (True,  (1,0,1)),
            "maroon":            (False, (1,1,1)), # TODO: LED probably can't display this well
        }

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
        self.current_color = random.choice(list(self.colors.keys()))
        print("You find a %s cacao pod!" % self.current_color)

        # Update LEDs.
        for i in range(len(self.led)):
            if self.colors[self.current_color][COLOR_RGB][i] == 1:
                self.led[i].on()
            else:
                self.led[i].off()

    def wait_for_input(self):
        # Read keyboard input if debugging.
        if not RASPBERRY_PI:
            self.last_input = input("Is it ripe?\n") == "T" # True / False
        else:
            while True:
                if self.green_button.is_pressed:
                    break
                if self.red_button.is_pressed:
                    break
            self.last_input = self.green_button.is_pressed
            
    def check_input(self, input, color):
        ripe = self.colors[color][COLOR_RIPENESS]
        if input == True:
            return ripe
        else:
            return not ripe
    
    def play(self):
        self.do_intro()
        self.clock.start()
        while self.clock.get_time() > 0:
            try:
                self.display_color()
                self.wait_for_input()
                if self.check_input(self.last_input, self.current_color):
                    if __debug__: print("You got it!")
                    self.score += 1
                elif __debug__:
                    print("*buzzer*")
                if  __debug__:
                    print("Score: %s\n" % self.score)
                time.sleep(0.5)

            # Exit gracefully if interrupted.
            except KeyboardInterrupt:
                print("\n # Interrupted!")
                self.clock.stop()
                sys.exit()

        print("Time's up!")
        print("Score: %d" % self.score)

if __name__=="__main__":
    game = Game()
    game.play()
