# This file contains the class for the global game timer.
import time
import math
from threading import Thread
try:
    from tm1637 import TM1637
except:
    from dummy import TM1637

class Clock:
    def __init__(self, duration, tm1, tm2=None):
        self.time_out = math.inf
        self.duration = duration
        self.thread = None # is this bad lol
        self.is_active = False

        self.tm1 = tm1
        self.tm2 = tm2
    
    def _count(self):
        while self.time_out - time.time() >= 0 and self.is_active:
            self.tm1.number(int(self.time_out - time.time()))
            if self.tm2 is not None:
                self.tm2.number(int(self.time_out - time.time()))
        self.stop()

    def start(self):
        if self.thread is None:
            print(" # Clock started!")
            self.is_active = True
            self.time_out = time.time() + self.duration
            self.thread = Thread(target = self._count, args=())
            self.thread.start()
        else:
            raise Exception("Clock already started!")
    
    def stop(self):
        if self.thread is not None:
            print(" # Clock stopped!")
            self.is_active = False
            self.thread = None
            self.tm1.write([0,0,0,0])
            if self.tm2 is not None:
                self.tm2.write([0,0,0,0])
    
    def get_time(self):
        return self.time_out - time.time()
