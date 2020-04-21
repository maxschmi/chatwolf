#-------------------#
#                   #
#    werewolf game  #
#     per skype     #
#     Max Schmit    #
#     march 2020    #
#                   #
#-------------------#

# librarys
from skpy import Skype, SkypeAuthException
from Werewolf import *
from getpass import getpass

# open Skype connection
try:
	sk = Skype(tokenFile = "temp/token.txt")
except SkypeAuthException:
	sk = Skype(input("username"), getpass())

# get properties and start the game
#chatid = '19:3db90f3ba215466aa082243848d24289@thread.skype' # test

game = Game(sk, 
			chatid, 
			numwerewolfs = 1, amor = True, witch = False, prostitute = False, visionary = False, lang = "en", wait_mult = 0)

#game.dist_roles() manualy distribute roles, is also done in strat methode
game.start()

# restart from bkp
game = Game.load_bkp("backup_2020-04-12_16-26-14") # enter the correct file

# ideas to add:
## window programm
## start_console fixing
## intro text with tips: no sound for messages

# delete villager from the list or add a number of them

# more waiting time ass takes long

# run on server

# dont call dead rolls

# rolls number of times



