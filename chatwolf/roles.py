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
#                              Role classes                             #
#                                                                       #
#-----------------------------------------------------------------------#

# own libraries
from .skypecommands import SkypeCommands

#other libraries
import time
import random as rd

# class definitions
#------------------

class Role(object):
    """Main class for the roles.

    Attributes:
        role (str): the name of the role
        group (str): the name of the group "Werewolf"/"Villager"
        player (list of Player): all the players that belong to this role
        game (Game): the main Game object
        chatid (str): SkypeChat id of the player(s) chat
        game (Game): the main Game object
        chat (SkypeChat): group/single SkypeChat of the player(s)
        skc (SkypeCommands): object of the SkypeCommands class for this role
    """ 

    role = "not set"
    group = "not set"

    def __init__(self, player, game):
        """Initilaize the Role object.

        Args:
            player (list of Player): all the players that belong to this role
            game (Game): the main Game object
            chatid (str): SkypeChat id of the player(s) chat
            game (Game): the main Game object
            chat (SkypeChat): group/single SkypeChat of the player(s)
            skc (SkypeCommands): object of the SkypeCommands class for this role
        """        
        self.game = game
        # add Player(s)
        if type(player)==list:
            self.players = player
        else:
            self.players = [player]

        #add Skype Chat variables
        if len(self.players) > 1:
            player_ids = []
            for pl in self.players:
                player_ids.append(pl.id)
            self.chatid = self.game.sk.chats.create(player_ids).id
            self.game.sk.chats[self.chatid].setTopic(self.role + "_group")
        else:
            self.chatid = self.players[0].chatid
        self.chat = self.game.sk.chats[self.chatid]
        self.skc = SkypeCommands(self.chatid, self.game)

        # add role to the player(s)
        for player in self.players:
            player.role = self
        
    def greeting(self):
        """Inform players about their role."""
        self.chat.sendMsg(self.game.msg("greeting_"+ self.role.lower()))

    def night(self, nightactions):
        """Do the corresponding night phase.

        Args:
            nightactions (Nightactions): log of all the actions that happen(d) in the night
        """

        pass

    def get_names(self):
        """Get the names of the players of this role.

        Returns:
            list of str: list of all the names of the roles players
        """

        names = []
        for i in range(len(self.players)):
            names.append(self.players[i].name)
        return names

    def msg_group_night(self):
        """Send a notification to the group chat, which role got called."""        
        self.game.chat.sendMsg("I call the {0}".format(self.role))
        # test if a player of the role is still alive
        test_alive = False
        for p in self.players:
            if p.alive:
                test_alive = True
        # wait a random time, so it is not possible to know if a role is already dead
        if not test_alive:
            sleeptime = rd.gauss(15, 5)
            while sleeptime <7:
                sleeptime = rd.gauss(15, 5)
            time.sleep(sleeptime * self.game.wait_mult)


class Werewolf(Role):
    """
    Class of the werewolf role.

    Attributes:
        role (str): the name of the role
        group (str): the name of the group "Werewolf"/"Villager"
        player (list of Player): all the players that belong to this role
        game (Game): the main Game object
        chatid (str): SkypeChat id of the player(s) chat
        game (Game): the main Game object
        chat (SkypeChat): group/single SkypeChat of the player(s)
        skc (SkypeCommands): object of the SkypeCommands class for this role
    """  

    role = "Werewolf"
    group = "Werewolf"
    
    def night(self, nightactions):
        """Do the Werewolfs night phase.

        ask whome to kill this night

        Args:
            nightactions (Nightactions): log of all the actions that happen(d) in the night
        """

        self.msg_group_night()
        self.chat.sendMsg(self.game.msg("night_"+ self.role.lower()))
        self.chat.sendMsg(nightactions.alive_string)
        id = self.skc.ask("kill", nightactions.alive)
        nightactions.kill(id)
        self.chat.sendMsg(self.game.msg("night_sleep"))

        #log
        if id == 0:
            self.game.log.info("The werewolf(s) killed noone")
        else:
            self.game.log.info("The werewolf(s) killed " + 
                               nightactions.alive[id-1].get_name_group())

class Villager(Role):
    """Class for the Villager role.

    Attributes:
        role (str): the name of the role
        group (str): the name of the group "Werewolf"/"Villager"
        player (list of Player): all the players that belong to this role
        game (Game): the main Game object
        chatid (str): SkypeChat id of the player(s) chat
        game (Game): the main Game object
        chat (SkypeChat): group/single SkypeChat of the player(s)
        skc (SkypeCommands): object of the SkypeCommands class for this role
    """ 

    role = "Villager"
    group = "Villager"

class Amor(Villager):
    """Class for the Amor role.

    Attributes:
        role (str): the name of the role
        group (str): the name of the group "Werewolf"/"Villager"
        player (list of Player): all the players that belong to this role
        game (Game): the main Game object
        chatid (str): SkypeChat id of the player(s) chat
        game (Game): the main Game object
        chat (SkypeChat): group/single SkypeChat of the player(s)
        skc (SkypeCommands): object of the SkypeCommands class for this role
    """ 

    role = "Amor"

    def greeting(self):
        """inform player about their role and give amor the oportunity to throw his arrow"""
        super().greeting()
        alive = self.game.get_alive()
        alive_string = self.game.get_alive_string(noone = False)
        self.chat.sendMsg(alive_string)
        ids = self.skc.ask("arrow", alive, num_ids = 2, min_id = 1)
        alive[ids[0]-1].love_arrow(alive[ids[1]-1])
        alive[ids[1]-1].love_arrow(alive[ids[0]-1])

        #log
        self.game.log.info("Amor trows his arrow to "+ 
                           " & ".join([alive[ids[0]-1].name, 
                                       alive[ids[1]-1].name]))

class Prostitute(Villager):
    """Class for the Prostitute role.

    Attributes:
        role (str): the name of the role
        group (str): the name of the group "Werewolf"/"Villager"
        player (list of Player): all the players that belong to this role
        game (Game): the main Game object
        chatid (str): SkypeChat id of the player(s) chat
        game (Game): the main Game object
        chat (SkypeChat): group/single SkypeChat of the player(s)
        skc (SkypeCommands): object of the SkypeCommands class for this role
    """ 

    role = "Prostitute"

    def night(self, nightactions):
        """Do the Prostetutes night phase.

        ask where (s)he wants to stay

        Args:
            nightactions (Nightactions): log of all the actions that happen(d) in the night
        """

        self.msg_group_night()
        self.chat.sendMsg(self.game.msg("night_"+ self.role.lower()))
        self.chat.sendMsg(nightactions.alive_string)
        id = self.skc.ask("visit", nightactions.alive)
        if not id == 0:
            self_id = nightactions.alive.index(self.players[0])+1
            if not self_id == id:
                nightactions.together(id, self_id)
                self.game.log.info("The prostitute goes to " + nightactions.alive[id-1].name)
        self.chat.sendMsg(self.game.msg("night_sleep"))

class Witch(Villager):
    """Class for the Witch role.

    Attributes:
        role (str): the name of the role
        group (str): the name of the group "Werewolf"/"Villager"
        player (list of Player): all the players that belong to this role
        game (Game): the main Game object
        chatid (str): SkypeChat id of the player(s) chat
        game (Game): the main Game object
        chat (SkypeChat): group/single SkypeChat of the player(s)
        skc (SkypeCommands): object of the SkypeCommands class for this role
        elixier (bool): True: the witchs elixier is still available
                          False: the witchs elixier got already used
        poison (bool): True: the witchs elixier is still available
                         False: the witchs elixier got already used
    """ 
    
    role = "Witch"
    
    def greeting(self):
        """Inform player about their role and initialize the poison and elixier."""
        super().greeting()
        self.poison = True
        self.elixier = True

    def night(self, nightactions):
        """Do the witchs night phase.

        tell her whos going to die
        ask if he wants to save, by using her elixier
        ask if he wants to kill someone, by using her poison

        Args:
            nightactions (Nightactions): log of all the actions that happen(d) in the night
        """

        self.msg_group_night()
        self.chat.sendMsg(self.game.msg("night_"+ self.role.lower()) % 
                          {"elixier": int(self.elixier), 
                           "poison": int(self.poison)})
        
        killed_id = nightactions.get_killed_id()
        if (killed_id == None):
            self.chat.sendMsg(self.game.msg("night_witch_noone"))
        else:
            killed_name = nightactions.alive[killed_id].name
            time.sleep(1*self.game.wait_mult)
            if self.elixier:
                self.chat.sendMsg(self.game.msg("night_witch_save", 0) % 
                                  {"killed": killed_name} + 
                                  self.game.msg("night_witch_save", 1))
                if self.skc.ask("bool"):
                    nightactions.save(killed_id+1)
                    self.elixier = False
                    self.game.log.info("The witch uses her elixier and saves " +
                                      killed_name)
            else:
                    self.chat.sendMsg(self.game.msg("night_witch_save", 0) % 
                                      {"killed": killed_name} + 
                                      self.game.msg("night_witch_save", 2))

        time.sleep(1*self.game.wait_mult)
        if self.poison:
            self.chat.sendMsg(self.game.msg("night_witch_kill"))
            time.sleep(1*self.game.wait_mult)
            if self.skc.ask("bool"):
                self.chat.sendMsg(self.game.msg("night_witch_kill_list"))
                self.chat.sendMsg(nightactions.alive_string)
                id = self.skc.ask("kill", nightactions.alive)
                if not id == 0:
                    nightactions.kill(id)
                    self.poison = False
                    self.game.log.info("The witch uses her poison to kill " + 
                                       nightactions.alive[id-1].name)
        time.sleep(2*self.game.wait_mult)
        self.chat.sendMsg(self.game.msg("night_sleep"))
        
class Visionary(Villager):
    """
    Class for the Visionary role.

    Attributes:
        role (str): the name of the role
        group (str): the name of the group "Werewolf"/"Villager"
        player (list of Player): all the players that belong to this role
        game (Game): the main Game object
        chatid (str): SkypeChat id of the player(s) chat
        game (Game): the main Game object
        chat (SkypeChat): group/single SkypeChat of the player(s)
        skc (SkypeCommands): object of the SkypeCommands class for this role
    """ 
    
    role = "Visionary"

    def night(self, nightactions):
        """Do the visionarys night phase.

        ask whome (s)he wants to see
        tell him/her the group of this player

        Args:
            nightactions (Nightactions): log of all the actions that happen(d) in the night
        """

        self.msg_group_night()
        self.chat.sendMsg(self.game.msg("night_"+ self.role.lower()))
        self.chat.sendMsg(nightactions.alive_string)
        id = self.skc.ask("see", nightactions.alive)
        if not id == 0:
            id -= 1
            self.chat.sendMsg(nightactions.alive[id].get_name_group())
            self.game.log.info("The visionary sees "+ 
                               nightactions.alive[id].get_name_group())
