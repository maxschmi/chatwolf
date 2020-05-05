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
#                         Player classe                                 #
#                                                                       #
#-----------------------------------------------------------------------#

# library
from .skypecommands import SkypeCommands

# depencies
from skpy import SkypeUser

# class definition

class Player(object):
    """
    Class for every player.
    
    Attributes:
        chatid (str): chatid of the corresponding skpy.SkypeSingleChat of the player
        id (str): Skype id of the player
        game (Game): the main Game object
        chat (SkypeChat): the single chat of the player
        skc (SkypeCommands): object of the SkypeCommands class for the single chat of the player
        name (str): Name of the player
        alive (bool): True: the player is alive ; False: the player is dead
        love (bool): True: the player is in love with someone
        lover (Player): The player (s)he is in love with
        role (Role): The role the player has got for the game
    """    

    def __init__(self, id, game):
        """Initilalize the player.

        Args:
            id (str): Skype id of the player
            game (Game): the main Game object
        """  

        self.game = game
        # Skype arguments
        self.id = id
        self.chatid = self.game.sk.contacts[self.id].chat.id

        if type(self.game.sk.contacts[self.id]) == SkypeUser:
            self.game.sk.contacts[self.id].invite(self.game.msg("welcome_player"))
        
        self.chat = self.game.sk.chats[self.chatid]
        self.skc = SkypeCommands(self.chatid, self.game)

        # get the name
        first = self.game.sk.contacts[self.id].name.first
        first = first if first else ""
        last = self.game.sk.contacts[self.id].name.last
        last = last if last else ""
        self.name = " ".join([first, last])
        if self.name == "":
            self.name = self.skc.ask("name")
        
        self.alive = True
        self.love = False
        self.role = None

    def love_arrow(self, lover):
        """Throw an arrow at this player, so (s)he fells in love.

        Args:
            lover (Player): The player (s)he fells in love with
        """        
        self.love = True
        self.lover = lover #Player object
        self.chat.sendMsg(self.game.msg("player_arrow") + lover.name)

    def die(self, answer = True):
        """The player dies.

        Keyword Args:
            answer (bool, optional): should the methode return the name and the group of the player
                             e.g. True: the methode returns "name (group)"  . Defaults to True.

        Returns:
            str or None: "name (group)" of the player or None if the answer argument is False
        """        

        self.alive = False
        self.game.log.info(self.name + " dies")
        if self.love:
            self.lover.alive = False
            self.game.log.info(self.name + " was in love with " + 
                               self.lover.name + ", therefor (s)he died too!")
            if answer: 
                return [self.name + "(" + self.role.group + ")", 
                        self.lover.name+ "(" + self.lover.role.group + ")"]
        else:
            if answer:
                return [self.name+ "(" + self.role.group + ")"]

    def get_name_group(self):
        """Get a string with the name and the group of the player.

        Returns:
            str: "name (group)" of the player
        """  

        return self.name + "(" + self.role.group + ")"

    def get_name_role(self):
        """Get a string with the name and role of the player.

        Returns:
            str: "name (role)" of the player
        """  

        return self.name + "(" + self.role.name + ")"