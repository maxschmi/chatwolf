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
#                         Nightactions classe                           #
#                                                                       #
#-----------------------------------------------------------------------#

# class definition
class Nightactions(object):
    """Class to log all the actions that happen in the night and resume.

    Attributes:
        game (Game): the main Game object
        alive (list of Players): list of players that are still alive
        alive_string (list of str): list of players, that are still alive as "id: Name"
                                       id is place in alive list + 1
        lskill (list of bool): list of one bool for every player if (s)he got killed in the night
                                 e.g. lskill[1] says if player[1] got killed
        lstogether (list of tuple of int): list of players ids that stayed together during the night.
                                            always as tuple of two ids, first one is the player who stays at home
    """

    def __init__(self, alive, game, noone = True):
        """Create a Nightaction logbbok for the night.

        Args:
            alive (list of Players): list of players that are still alive
            game (Game): the main Game object

        Keyword Args:
            noone (bool, optional): should there be an entry "0: noone" . Defaults to True.
        """

        self.game = game
        self.alive = alive 
        self.alive_string = game.get_alive_string(noone = noone)
        
        # create the lists to log
        self.lskill = [False]*len(alive)
        self.lstogether = []

    def kill(self, player_number):
        """Kill a player.

        Args:
            player_number ([type]): number of the player in the alive_string
        """        

        if not player_number == 0:
            self.lskill[player_number-1] = True

    def save(self, player_number):
        """Save a player.

        Args:
            player_number ([type]): number of the player in the alive_string
        """   
        if not player_number == 0:
            self.lskill[player_number-1] = False

    def together(self, player_home_number, player_visit_number):
        """Set 2 people together for this night.

        Args:
            player_home_number (int): the number in the alive_string of the player, who's at home
            player_visit_number (int): the number in the alive_string of the player, who's visiting the other
        """        
        #player_visit_number: prostitute, does not die unless player_home_number dies
        # convention in tuple first is unsave, second is save unless other dies
        if (not player_home_number == 0) and (not player_visit_number  == 0):
            self.lstogether.append((player_home_number-1, player_visit_number-1))

    def finish_night(self):
        """Finish the night and get the name(group) of the plaers that died.

        Returns:
            list of str: A list of all the players that died this night as name(group)
        """       
         
        # save the players that were not at home
        for tog in self.lstogether: 
            self.lskill[tog[1]] = False

        killed = []
        for i in range(len(self.alive)):
            if self.lskill[i]:
                killed += self.alive[i].die()
                for tog in self.lstogether: # if someone else visited the player, (s)he dies to
                    if i == tog[0]:
                        killed += self.alive[tog[1]].die()
        return set(killed)

    def get_killed_id(self):
        """Get the id of the killed player.

        Returns:
            int: id of the killed player
        """      

        for i in range(len(self.alive)):
            if self.lskill[i]:
                return i