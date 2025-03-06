# This file contains debug declarations for running the
# game while not using the Pi.

class PWMLED:
    def __init__(self, pin):
        self.pin = pin
        self.value = 0
    
    def on(self):
        if __debug__: print(" # LED pin %d on!" % self.pin)
        
    def off(self):
        if __debug__: print(" # LED pin %d off!" % self.pin)

class Button:
    def __init__(self, pin):
        class Pin:
            def __init__(self, num):
                self.number = num
        self.pin = Pin(pin)
        self.is_pressed = False

class TM1637:
    def __init__(self, clk, dio):
        self.clk = clk
        self.dio = dio
        self.time = 0
    
    def numbers(self, num1, num2, colon):
        if __debug__ and num2 != self.time: print(" # Clock: %d" % num2)
        self.time = num2
    
    def write(self, num):
        pass
