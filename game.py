import random
import time
from gpiozero import LED, Button
from datetime import datetime
import tm1637


class Game:
    def __init__(self, time=30):
        # TODO: Assign pin IDs

        r = LED(17)
        g = LED(27)
        b = LED(22)

        # all four buttons, but change port to match breadboard
        user1_red_button = Button(23)
        user1_green_button = Button(24)
        user2_red_button = Button(25)
        user2_green_button = Button(26)

        # Creating 4-digit 7-segment display object
        tm = tm1637.TM1637(clk=17, dio=18)  # Using GPIO pins 18 and 17
        clear = [0, 0, 0, 0]  # Defining values used to clear the display
        # idea, display message: press button to start

        self.score = 0
        self.time_limit = time # in seconds
        self.current_color = "blue"
        self.last_input = "R"

        self.colors = { # colors: ripeness
            "blue": False,
            "green": False,
            "candy apple red": True,
            "phoenician yellow": True,
            "fuschia": True,
            "maroon": False,

        }

    def do_intro(self):
        """ 
        Game introduction for coding/debugging purposes.
        Note that for the actual exhbit, directions will be displayed on the wood
        """
        print("Welcome to Ripe Reaction! The goal is to harvest more ripe cacao pods by being faster than your opponent.")
        print("Hit Green button for ripe, red button for not ripe.")
        print("Ripe colors: ")

    def display_color(self):
        """ Updates current color and display.
            TODO: Connect to GPIO output """
        self.current_color = random.choice(list(self.colors.keys()))
        print("You find a %s cacao pod!" % self.current_color)

    def wait_for_input(self):
        """ Halts and polls for next input.
            TODO: Connect to GPIO input """
        self.last_input = input("Is it ripe? ")

    def check_input(self, input, color):
        """ Checks last input against current color.
            TODO: Use global/class variables or arguments? """
        ripe = self.colors[color]
        if input == "Y":
            return ripe
        else:
            return not ripe
    
    def play(self):
        self.do_intro()
        while True:
            self.display_color()
            self.wait_for_input()
            if self.check_input(self.last_input, self.current_color):
                print("You got it!")
                self.score += 1
            else:
                print("*buzzer*")
            print("Score: %s\n" % self.score)


  
if __name__=="__main__":
    game = Game()
    game.play()
