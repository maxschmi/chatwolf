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
chatid = '19:3db90f3ba215466aa082243848d24289@thread.skype' # test
# chatid ='19:9718b408a11b43f780aa71bf6c50156e@thread.skype'

game = Game(sk, 
			chatid, 
			numwerewolfs = 1, amor = False, witch = False, prostitute = False, visionary = False, lang = "en", wait_mult = 0)

#game.dist_roles() manualy distribute roles, is also done in strat methode
game.start()

# restart from bkp
#game = Game.load_bkp("C:/Users/Max/source/repos/maxschmi/Skype-Werewolf/bkp/backup_2020-04-22_21-50-54") # enter the correct file





