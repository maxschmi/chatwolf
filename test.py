#test logging

import logging
import sys, os 

os.fi
log = logging.getLogger("Test.")
log.setLevel(logging.ERROR)
fh = logging.FileHandler("logs/test.txt")
fh.setLevel(logging.DEBUG)
log.addHandler(fh)
log.error("error test")
log.info("info test")
log.debug("debug test")



# test SkypeEventLoop
from skpy import Skype, SkypeEventLoop

class MySkype(SkypeEventLoop):
	def onEvent(self, event):
		print(repr(event))

msk = MySkype(tokenFile = "temp/token.txt")
msk.loop()

# test nightaction
na = Nightactions(game.players)
na.together(2,1)
na.kill(1)
na.finish_night()

# test reinitiating an object in class

class Test:
	def __init__(self, val):
		self.val = val

	def reinit(self, val):
		self.__init__(val)
# this worked
