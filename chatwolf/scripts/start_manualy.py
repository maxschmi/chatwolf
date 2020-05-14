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
from chatwolf import Game, _conf
from getpass import getpass

# open Skype connection
try:
    sk = Skype(tokenFile = _conf["temp_dir"] + "/token.txt")
except SkypeAuthException:
    sk = Skype(input("username"), getpass())

# get properties and start the game
chatid = ###enter your chatid, get a list of actual chats with sk.chats.recent()

game = Game(sk, 
            chatid, 
            numwerewolfs = 1, amor = False, witch = False, prostitute = False, 
            visionary = True, lang = "en", wait_mult = 1)

game.start()

# restart from bkp
#-----------------

# enter the correct file, without ending, normally in chatwolf/user_data/bkp if not changed
#game = Game.load_bkp(".../bkp/backup_2020-04-22_21-50-54") 
#game.continue_bkp() #to continue the game

