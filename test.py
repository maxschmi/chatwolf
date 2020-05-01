#-------------------------------------------------#
#                                                 #
#             werewolf game per skype             #
#              author:  Max Schmit                #
#     to do a test-run with only one account      #
#-------------------------------------------------#

# librarys
from skpy import Skype, SkypeAuthException
from Game import *
from getpass import getpass

# open Skype connection
try:
    sk = Skype(tokenFile = "temp/token.txt")
except SkypeAuthException:
    sk = Skype(input("username"), getpass())

# get properties and start the game
chatid = '19:3db90f3ba215466aa082243848d24289@thread.skype' # test

game = Game(sk, 
            chatid, 
            numwerewolfs = 1, amor = False, witch = False, prostitute = False, visionary = False, lang = "en", wait_mult = 0)

# add only me to the game
for i in range(5):
    game.players.append(Player('live:maxschm_1', game))
game.players.remove(game.players[1])

#set the roles again
game.numwerewolfs = 1
game.amor = True
game.witch = True
game.prostitute = True
game.visionary = True
game.numplayers = len(game.players)

#game.dist_roles() manualy distribute roles, is also done in strat methode
game.start()

# restart from bkp
#game = Game.load_bkp("C:/Users/Max/source/repos/maxschmi/Skype-Werewolf/bkp/backup_2020-04-22_21-50-54") # enter the correct file
