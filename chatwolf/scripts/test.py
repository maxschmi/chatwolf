#-----------------------------------------------------------------------#
#                         Chatwolf                                      #
#                     author:  Max Schmit                               #
#                                                                       #
#-----------------------------------------------------------------------#
# license information:                                                  #
# "Chatwolf" unofficial game to play the popular werewolf game on Skype #
#  Copyright (C) 2020 Max Schmit                                        #
#                                                                       #
#This program is free software: you can redistribute it and/or modify   #
#it under the terms of the GNU General Public License as published by   #
#the Free Software Foundation, either version 3 of the License, or      #
#(at your option) any later version.                                    #
#                                                                       #
#This program is distributed in the hope that it will be useful,        #
#but WITHOUT ANY WARRANTY; without even the implied warranty of         #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
#GNU General Public License for more details.                           #
#                                                                       #
#You should have received a copy of the GNU General Public License      #
#along with this program.  If not, see <https://www.gnu.org/licenses/>. #
#
#-----------------------------------------------------------------------#
#                                                                       #
#             to do a test-run with only one account                    #
#    create a group chat, but only one account will be several players  #
#-----------------------------------------------------------------------#

# librarys
from skpy import Skype, SkypeAuthException
from chatwolf import Game, Player, _conf
from getpass import getpass

# open Skype connection
try:
    sk = Skype(tokenFile = _conf["temp_dir"] + "/token.txt")
except SkypeAuthException:
    sk = Skype(input("username"), getpass())

# get properties and start the game
chatid = #enter here your chatid. to get your latest chats: sk.chats.recent()
player_user_id =  #enter here your id of the player who tests the game

game = Game(sk, 
            chatid, 
            num_werewolfs = 1, num_amor = 0, num_witch = 0, 
            num_prostitute = 0, num_visionary = 0, lang = "en", 
            wait_mult = 0.2)

# add only one player to the game
game.players = []
for i in range(10):
    game.players.append(Player(player_user_id, game))

#set the roles again
game.num_werewolfs = 1
game.num_amor = 2
game.num_witch = 2
game.num_prostitute = 2
game.num_visionary = 2

#game.dist_roles() manualy distribute roles, is also done in start methode
game.start()

# restart from bkp
#game = Game.load_bkp("C:/Users/User/chatwolf/bkp/...") # enter the correct file
