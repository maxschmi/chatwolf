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
from getpass import getpass, getuser

# open Skype connection
#sk = Skype('fred.vH78@yahoo.com', getpass())
try:
	sk = Skype(tokenFile = "temp/token.txt")
except SkypeAuthException:
	sk = Skype(input("username"), getpass())

# get properties and start the game
	# for testing
#chatid = '19:3db90f3ba215466aa082243848d24289@thread.skype' # test
#chatid = '19:1bbbf7d5f9464a588eb0b25bf9bea93c@thread.skype' # Werewolf-Spiel
chatid = '19:41d3c2b327b14538b01e647dd9b8288b@thread.skype' # Werewolf-Spiel-9-4-2020
game = Game(sk, chatid, numwerewolfs = 2, amor = True, witch = True, prostitute = True, visionary = True, lang = "en", wait_mult = 1)
game.start()

# ideas to add:
## window programm
## start_console fixing
## tell activated roles in greeting all
## intro text with tips: no sound for messages

# print role in night

# delete villager from th elist or add a number of them

# more waiting time ass takes long

# run on server

# dont call dead rolls

# rolls number of times

# save game with rolls to be restarted



