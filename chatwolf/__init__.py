#-----------------------------------------------------------------------#
#                         Chatwolf                                      #
#                     author:  Max Schmit                               #
#             email: maxschm (at) hotmail (dot) com                     #
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
#                             __init__                                  #
#                                                                       #
#-----------------------------------------------------------------------#
"""Chatwolf is a game to play Werewolf on Skype!

To start it you can do this:
import chatwolf
root = chatwolf.GUI()
root.mainloop() # if not already started
"""
# libraries
from chatwolf.check_conf import check_conf
check_conf() # create directories and create configuration file, if not already done
from chatwolf.game import Game
from chatwolf.player import Player
from chatwolf.roles import Role, Werewolf, Villager, Witch, Visionary, Amor, Prostitute
from chatwolf.skypecommands import SkypeCommands
from chatwolf.nightactions import Nightactions
from chatwolf.gui import GUI
from chatwolf._conf import _conf