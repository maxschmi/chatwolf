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
#                         main Game classes                             #
#                                                                       #
#-----------------------------------------------------------------------#


# own libraries
from .player import Player
from .roles import Role, Werewolf, Villager, Witch, Visionary, Amor, Prostitute
from .skypecommands import SkypeCommands
from .nightactions import Nightactions
from ._conf import _conf

#other libraries
from skpy import Skype, SkypeEventLoop, SkypeNewMessageEvent
from skpy import SkypeUser, SkypeContacts
import time
import random as rd
import logging
import datetime
import shelve
import json
from pkg_resources import resource_string as res_str
from pkg_resources import resource_filename as res_file

# game class definition
#----------------------

class Game(object):  
    """This is the main game class, that starts all the other necessary classes to play!
    
    Attributes:
        sk (skpy.Skype): logged in Skype Object of the Game-master
        chatid (str): chatid of the group-chat, where all players and the game-master are in
        chat (SkypeChat): the group chat
        skc (SkypeCommands): object of the SkypeCommands class for the group chat
        numwerewolfs (int): number of werewolfs for the game
        amor (bool): should the amor role be in the game
        witch (bool): should the witch role be in the game
        prostitute (bool): should the prostitute role be in the game
        visionary (bool): should the visionary role be in the game
        lang (str): language to use for the messages of the Game-master
        wait_mult (int): multiplier for the waiting seequences
        log_dir (str): directory path as str for the logging file
        logfilename (str): filepath of the logger file
        bkp_dir (str): directory path as str for the backup file 
        do_debug (bool): should a debug logging file be created
        starttime (datetime): starttime of the game (time when the Game object was created)
        nn (int): number of nights played
        nd (int): number of days played 
        log (Logger): the Logger of the game
        players (list of Players): list of all players of the game
        roles (list of Roles): list of all the roles in the game
    """

    def __init__(self, sk, chatid, numwerewolfs, 
                 amor = False, witch = False, prostitute = False,
                 visionary = False, lang = _conf["lang"], wait_mult = 1, 
                 log_dir = _conf["log_dir"], bkp_dir = _conf["bkp_dir"], 
                 do_debug = _conf["do_debug"]):
        """Initialize the game.

        Does:
            Save all the input variables
            save the token from Skype, for faster logins
            start the logging
            initialize the players
            check if number of players are enough for selected roles
            start night and day counters

        Args:
            sk (skpy.Skype): logged in Skype Object of the Game-master
            chatid (str): chatid of the group-chat, where all players and the game-master are in
            numwerewolfs (int): number of werewolfs for the game

        Keyword Args:
            amor (bool, optional): should the amor role be in the game . Defaults to False.
            witch (bool, optional): should the witch role be in the game . Defaults to False.
            prostitute (bool, optional): should the prostitute role be in the game . Defaults to False.
            visionary (bool, optional): should the visionary role be in the game . Defaults to False.
            lang (str, optional): language to use for the messages of the Game-master . Defaults to "en".
            wait_mult (int, optional): multiplier for the waiting seequences . Defaults to 1.
            log_dir (str, optional): directory path as str for the logging file . Defaults to "logs".
            bkp_dir (str, optional): directory path as str for the backup file . Defaults to "bkp".
            do_debug (bool, optional): should a debug logging file be created . Defaults to True.

        Raises:
            ValueError: if too many roles for the amount of players were selected
        """

        # Chat
        self.lang = lang
        self.sk = sk
        self.chatid = chatid
        self.chat = sk.chats[chatid]
        self.sk.conn.setTokenFile(_conf["temp_dir"] +"/token.txt")
        self.sk.conn.writeToken()
        self.skc = SkypeCommands(chatid, self)
        self.wait_mult = wait_mult

        #logging
        self.do_debug = do_debug
        self.starttime = datetime.datetime.now()
        self.log_dir = log_dir

        self.logfilename = (log_dir + "/Game_" + 
                            self.starttime.strftime("%Y-%m-%d_%H-%M-%S"))
        self.log = logging.getLogger("Werewolf")
        self.log.setLevel(logging.INFO)
        fhl = logging.FileHandler(self.logfilename+".txt")
        fhl.setLevel(logging.INFO)
        fhl.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.log.addHandler(fhl)

        if self.do_debug:
            self.log.setLevel(logging.DEBUG)

            #get all the errors to log in the file
            open(self.logfilename + "_debug.txt", "w+") # create the file
            logging.basicConfig(filename = self.logfilename+"_debug.txt",
                            filemode = 'a',
                            level=logging.DEBUG)

        #Players
        player_ids = self.chat.userIds
        if self.sk.userId in player_ids:
            player_ids.remove(self.sk.userId)
        self.players = list()
        for i in range(len(player_ids)):
            self.players.append(Player(player_ids[i], self))

        #Roles
        self.numroles = numwerewolfs + amor + witch + prostitute + visionary
        if self.numroles > len(player_ids):
            raise ValueError('You entered too many roles for the amount of players')
        self.numwerewolfs = numwerewolfs
        self.amor = amor
        self.witch = witch
        self.prostitute = prostitute
        self.visionary = visionary

        # counters for days and night
        self.nd = 0 # number of days played
        self.nn = 0 # number of nights played

        #other arguments and config
        self.bkp_dir = bkp_dir
        self.save_config()

    def start(self):
        """Start the game!
        
        does:
            check if players did already accept the game-master as contact
            send greeting to the group
            distribute roles by calling Game.dist_roles()
            inform players of them, by calling Role.greeting()
            start first day
        """

        self.log.info("Game starts")

        # test if players did all accept the Game-master
        i = 0
        while True:
            self.sk.contacts = SkypeContacts(self.sk) #to reload the contacts-list, to prevent using the cached data
            pl_error = []
            for player in self.players:
                if type(self.sk.contacts[player.id]) == SkypeUser:
                    pl_error.append(player.name)
            
            if len(pl_error)>0:
                self.chat.sendMsg(self.msg("error"))
                if (i%6 == 0) or (i == 0):
                    self.chat.sendMsg(self.msg("error_request").format(" & ".join(pl_error)))
            else:
                break

            i +=1
            time.sleep(4)
        
        #Greet players
        self.chat.sendMsg(self.msg("greeting_all") % 
                          {"numplayers": len(self.players),
                           "numwerwolfs": self.numwerewolfs})
        time.sleep(20*self.wait_mult)

        self.dist_roles()

        self.chat.sendMsg(self.msg("greeting_all_roles") + 
                          (" & ".join(self.get_roles())))
        
        self.log.info("Rolls got distributed: \n"+ " "*30 + 
                      ("\n" + " "*30).join(self.get_players_role()))
        # greet Roles
        for r in self.roles:
            r.greeting()
        self.bkp()

        time.sleep(40*self.wait_mult) # so everyone can get ready and has read his role
        self.chat.sendMsg(self.msg("greeting_start10s"))
        time.sleep(10*self.wait_mult)

        self.day()

    def dist_roles(self):
        """Distribute the roles to the players."""
        # in order of appearence in the night
        rd.shuffle(self.players)
        
        self.roles = list()
        i = 0

        if self.prostitute: 
            self.roles.append(Prostitute(self.players[i], self))
            i += 1

        self.werewolfs = Werewolf(self.players[i:(self.numwerewolfs+i)], self)
        self.roles.append(self.werewolfs)
        i += self.numwerewolfs

        if self.witch: 
            self.roles.append(Witch(self.players[i], self))
            i += 1

        if self.visionary: 
            self.roles.append(Visionary(self.players[i], self))
            i += 1
        
        for j in range(i, len(self.players) - self.amor):
            self.roles.append(Villager(self.players[j], self))

        if self.amor:  #last because this greeting methode takes longer
            self.roles.append(Amor(self.players[j+1], self))
    
    def restart(self):
        """Start a new game with the same settings."""
        self.__init__(self.sk, self.chatid, self.numwerewolfs, 
                      self.amor, self.witch, self.prostitute, self.visionary, 
                      self.lang, self.wait_mult, self.log_dir, self.bkp_dir, 
                      do_debug = self.do_debug)

        self.log.info("Game got restarted")

        self.start()

    def night(self):
        """Do a night phase.

        Does:
            create a Nightaction object as na
            call every Role.night(na)
            resume the night
            if game not over, start a day phase by calling game.day()
        """

        self.nn +=1
        self.log.info("="*30+" Night number {0} starts:".format(self.nn))

        # ask every role for night action
        na = Nightactions(alive = self.get_alive(), game = self)
        for r in self.roles:
            r.night(na)

        killed = na.finish_night()

        time.sleep(5*self.wait_mult)
        msg = self.msg("night_resume", line = 0)
        time.sleep(2*self.wait_mult)
        if len(killed) == 0:
            msg = msg + "\n" + self.msg("night_resume", line = 1)
            self.log.info("Resume night: No one got killed during the night")
        else:
            msg = (msg + "\n" + self.msg("night_resume", line = 2) %
                  {"names": " & ".join(killed)})
            self.log.info("Resume night: "+" & ".join(killed) + 
                          " got killed during the night")
        self.chat.sendMsg(msg)

        time.sleep(5*self.wait_mult)
        if not self.is_end():
            self.bkp()
            self.day()

    def day(self):
        """Do a day phase!

        Does:
            ask whom to kill this day
            if game not over, start a night phase by calling Game.night()
        """

        self.nd +=1
        self.log.info("="*30+" Day number {0} starts:".format(self.nd))
        alive_players = self.get_alive() 
        #talk to players
        self.chat.sendMsg(self.msg("day_start_all"))
        self.chat.sendMsg(self.get_alive_string())
        id = self.skc.ask("kill", alive_players)
        if id == 0:
            self.log.info("No one got killed during the day")
        else:
            id -= 1
            killed = alive_players[id].die()
            time.sleep(2*self.wait_mult)
            self.chat.sendMsg(self.msg("day_killed", 0) + " " + 
                              self.msg("day_killed", 1).join(killed))
            self.log.info(" & ".join(killed)+"got killed.")
        
        time.sleep(4*self.wait_mult)
        if not self.is_end():
            self.bkp()
            self.chat.sendMsg(self.msg("day_end"))
            while not self.skc.ask("bool"): pass
            time.sleep(3*self.wait_mult)
            self.night()

    def is_end(self):
        """Check if game is over!

        Returns:
            bool: True: game is over, on party won; 
                    False: Noone won yet, the game is still on
        """

        #test if one Party won
        alive = self.get_alive()
        
        # test if all are dead -> noone wins
        if len(alive) == 0:
            self.chat.sendMsg(self.msg("end_noone"))
            self.log.info("The Game ends, because all players are dead!" +
                          "\nNo one won!")
            time.sleep(2*self.wait_mult)
            self.end()
            return True

        #Test love Win
        if len(alive)==2:
            if (alive[0].love == True) and (alive[1].love == True):
                self.chat.sendMsg(self.msg("end_love").format(alive[0].name, 
                                                              alive[1].name))
                self.log.info("The Game ends, because only the loving players " +
                              "are alive!\nThe love won!")
                time.sleep(2*self.wait_mult)
                self.end()
                return True

        # Test werewolf win
        werwolf_count = 0
        for player in self.werewolfs.players:
            if player.alive:
                werwolf_count += 1
        if (werwolf_count == len(alive)) and (werwolf_count >= 1):
            self.chat.sendMsg(self.msg("end_werewolfs"))
            self.log.info("The Game ends, because only werewolfs are alive!" +
                          "\nThe werewolfs won!")
            time.sleep(2*self.wait_mult)
            self.end()
            return True

        # Test villager win?
        if werwolf_count == 0:
            self.chat.sendMsg(self.msg("end_villager"))
            self.log.info("The Game ends, because only villagers are alive!" +
                          "\nThe villagers won!")
            time.sleep(2*self.wait_mult)
            self.end()
            return True

        return False

    def end(self):
        """End the game!"""
        self.chat.sendMsg(self.msg("end_intro"))
        time.sleep(5*self.wait_mult)
        self.chat.sendMsg("\n".join(self.get_players_role()))
        self.chat.sendFile(open(self.logfilename+".txt", "r"), 
                           name = "log_file.txt")
        
        #log the players that are still alive
        self.log.info("still alive were: " + 
                      " & ".join(self.get_players_role(all = False)))

    def get_players_role(self, all = True):
        """Get a list of all players with their roles!

        Keyword Args:
            all (bool, optional): True: every player of the game is listed; False: only the living players are listed . Defaults to True.

        Returns:
            list of str: a list with one entry per player with: "name (role)"
        """

        # return list Player(Role)
        list = []
        for player in self.players:
            if all:
                list.append(player.get_name_role())
            elif not all:
                if player.alive:
                    list.append(player.get_name_role())

        return list

    def get_alive(self):
        """Get a list of players that are alive!

        Returns:
            list of Player: list of players that are alive.
        """

        alive = []
        for p in self.players:
            if p.alive == True:
                alive.append(p)
        return alive

    def get_alive_string(self, noone=True):
        """Get a list of players that are still alive as string entries with their number!

        Keyword Args:
            noone (bool, optional): True: add "0: noone" to the list; False: only players without "0: noone"  . Defaults to True.

        Returns:
            list of str: list with one entry per player, each entry is the number in the alive list + 1 and the name of the player
        """ 

        alive_players = self.get_alive()

        if noone:
            alive_string = ["0 : No one"]
        else:
            alive_string = []

        for i in range(len(alive_players)):
            alive_string.append(str(i+1) + " : " + alive_players[i].name)
        return "\n".join(alive_string)

    def get_roles(self):
        """Get a list of the activated roles of the game.

        Returns:
            list of str: list of the activated roles of the game
        """

        ls =[]
        for role in self.roles:
            ls.append(role.name)
        st = set(ls)
        if "Werewolf" in st:st.remove("Werewolf")
        if "Villager" in st: st.remove("Villager")
        ls = list(st)
        numvillagers = len(self.players)-len(ls)-self.numwerewolfs
        ls.append(str(numvillagers) + " Villager(s)")
        ls.append(str(self.numwerewolfs) + " Werewolf(s)")

        return ls

    def msg(self, filename, line = "all"):
        """Get the coresponding message in the selected language.

        Args:
            filename (str): the name of the message file, 
                          e.g. "greeting_all" for the first group message, 
                          this file needs to exist at least in the "msg/en/" folder

        Keyword Args:
            line (str or int, optional): specify if the whole message should be returned ("all") 
                                 or only a specific line(int) . Defaults to "all".

        Returns:
            str: message in the selected language (self.lang) or in english if there is no translation
        """
        try:
            file = open(res_file("chatwolf", 
                           "data/messages/"+self.lang+"/"+
                           filename+".txt"), "r")
            if line == "all":
                msg = file.read()
            elif type(line) == int:
                msg = file.readlines()[line].replace("\n", "")
            file.close()
            return msg
        except FileNotFoundError:
            try:
                file = open(res_file("chatwolf", 
                               "data/messages/en/"+
                               filename+".txt"), "r")
                if line == "all":
                    msg = file.read()
                elif type(line) == int:
                    msg = file.readlines()[line].replace("\n", "")
                file.close()
                return msg
            except FileNotFoundError:
                print("no such file defined in any language")
                self.log.debug("the choosen message " + 
                               filename + " didn't exist")

    def bkp(self):
        """Backup the game."""
        bkp = shelve.open(self.bkp_dir+"/backup_" + 
                          self.starttime.strftime("%Y-%m-%d_%H-%M-%S"))
        bkp["game"] = self
        bkp.close()

    @staticmethod
    def load_bkp(filepath):
        """Load a backup-file.

        Args:
            filepath (str): filepath of the backup-file to be loaded

        Returns:
            Game: the old Game object
        """  

        #class methode to load a game from a backup
        bkp = shelve.open(filepath)
        game = bkp["game"]
        bkp.close()
        return game

    def continue_bkp(self):
        """Continue a game that was loaded from a backup-file."""
        self.log.info("The game continues from a backup-file")

        if self.is_end():
            self.log.debug("The game was already finished")
            print("The game is already over")
        else:
            if self.nd == 0:
                self.day()
            elif self.nd > self.nn:
                self.nd -= 1
                self.day()
            elif self.nd == self.nn:
                self.nn -= 1
                self.night()

    def save_config(self):
        _conf["do_debug"] = self.do_debug
        _conf["log_dir"] = self.log_dir
        _conf["bkp_dir"] = self.bkp_dir
        _conf["do_debug"] = self.do_debug
        json.dump(_conf, open(res_file("chatwolf", "/data/conf.json"), "w"))







