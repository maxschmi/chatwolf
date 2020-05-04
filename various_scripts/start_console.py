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
#             script to start the game from console                     #
#                                                                       #
#-----------------------------------------------------------------------#

# librarys
from skpy import Skype, SkypeAuthException
from chatwolf.game import *
from getpass import getpass, getuser

# define functions
def boolean(str):
    str = str.lower()
    if ("yes" in str) or ("y" in str) or ("1" in str) or ("j" in str):
        return True
    elif ("no" in str) or ("n" in str) or ("0" in str):
        return False

# open Skype connection
#sk = Skype('fred.vH78@yahoo.com', getpass())
try:
    sk = Skype(tokenFile = "temp/token.txt")
except SkypeAuthException:
    sk = Skype(input("username"), getpass())

# get properties and start the game

#get chatid
name = input("What is the Name of your group?")
chats = sk.chats.recent()
for chat in chats:
    if name in chats[chat].topic:
        chatid = chat

if not "chatid" in locals():
    print(chats)
    chatid = input("Error I couldn't find the group\nGive the id of your Group chat (you find a list of your recent chats above):")

numwerewolfs = int(input("How many Werewolfs do you want to have?"))

if boolean(input("Do you want some special characters in the game?(Yes/No or y/n or 1/0)")):
    amor = boolean(input("Do you want to have an amor? (Yes/No or y/n or 1/0)"))
    witch = boolean(input("Do you want to have a witch? (Yes/No or y/n or 1/0)"))
    prostitute = boolean(input("Do you want to have a prostitute? (Yes/No or y/n or 1/0)"))
    visionary = boolean(input("Do you want to have a visionary? (Yes/No or y/n or 1/0)"))
    game = Game(sk, chatid, numwerewolfs, amor, witch, prostitute, visionary)
else:
    game = Game(sk, chatid, numwerewolfs)

game.start()

#print("to restart the game you: game.restart()")
while boolean(input("Do you want to restart the game with the same properties? (Yes/No or y/n or 1/0)")):
    game.restart()
