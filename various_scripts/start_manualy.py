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
#                script to start the game manualy                       #
#                                                                       #
#-----------------------------------------------------------------------#

# librarys
from skpy import Skype, SkypeAuthException
from chatwolf.game import *
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
#game.continue_bkp()





