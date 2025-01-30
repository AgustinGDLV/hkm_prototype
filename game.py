import random
import timer

class Game:
    def __init__(self, time=30):
        # TODO: Assign pin IDs

        self.score = 0
        self.time_limit = time # in seconds
        self.current_color = "blue"
        self.last_input = "R"

        self.colors = { # colors: ripeness
            "blue": False,
            "green": False,
            "candy apple red": True,
        }

    def do_intro(self):
        """ Introduces game and instructions.
            TODO: How to do this in exhibit? """
        print("Press Y if the color is ripe and N if it is unripe!")

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
    hello_world()
    game = Game()
    game.play()
