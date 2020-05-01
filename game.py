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
#                         main Game classes                             #
#                                                                       #
#-----------------------------------------------------------------------#


# librarys
from skpy import Skype, SkypeEventLoop, SkypeNewMessageEvent
from skpy import SkypeUser, SkypeContacts
import time
import random as rd
import re
import logging
import datetime
import shelve
import sys

class Game(object):  
    """
    This is the main game class, that starts all the other necessary classes to play!
    
    Attributes:
        sk {skpy.Skype} -- logged in Skype Object of the Game-master
        chatid {str} -- chatid of the group-chat, where all players and the game-master are in
        chat {SkypeChat} -- the group chat
        skc {SkypeCommands} -- object of the SkypeCommands class for the group chat
        numwerewolfs {int} -- number of werewolfs for the game
        amor {bool} -- should the amor role be in the game
        witch {bool} -- should the witch role be in the game
        prostitute {bool} -- should the prostitute role be in the game
        visionary {bool} -- should the visionary role be in the game
        lang {str} -- language to use for the messages of the Game-master
        wait_mult {int} -- multiplier for the waiting seequences
        log_dir {str} -- directory path as str for the logging file
        logfilename {str} -- filepath of the logger file
        bkp_dir {str} -- directory path as str for the backup file 
        do_debug {bool} -- should a debug logging file be created
        starttime {datetime} -- starttime of the game (time when the Game object was created)
        nn {int} -- number of nights played
        nd {int} -- number of days played 
        log {Logger} -- the Logger of the game
        players {list of Players} -- list of all players of the game
        roles {list of Roles} -- list of all the roles in the game
    """

    def __init__(self, sk, chatid, numwerewolfs, 
                 amor = False, witch = False, prostitute = False,
                 visionary = False, lang = "en", wait_mult = 1, 
                 log_dir = "logs", bkp_dir = "bkp", do_debug = True):
        """initialize the game.

        Does:
            Save all the input variables
            save the token from Skype, for faster logins
            start the logging
            initialize the players
            check if number of players are enough for selected roles
            start night and day counters

        Arguments:
            sk {skpy.Skype} -- logged in Skype Object of the Game-master
            chatid {str} -- chatid of the group-chat, where all players and the game-master are in
            numwerewolfs {int} -- number of werewolfs for the game

        Keyword Arguments:
            amor {bool} -- should the amor role be in the game (default: {False})
            witch {bool} -- should the witch role be in the game (default: {False})
            prostitute {bool} -- should the prostitute role be in the game (default: {False})
            visionary {bool} -- should the visionary role be in the game (default: {False})
            lang {str} -- language to use for the messages of the Game-master (default: {"en"})
            wait_mult {int} -- multiplier for the waiting seequences (default: {1})
            log_dir {str} -- directory path as str for the logging file (default: {"logs"})
            bkp_dir {str} -- directory path as str for the backup file (default: {"bkp"})
            do_debug {bool} -- should a debug logging file be created (default: {True})

        Raises:
            ValueError: if too many roles for the amount of players were selected
        """

        # Chat
        self.lang = lang
        self.sk = sk
        self.chatid = chatid
        self.chat = sk.chats[chatid]
        self.sk.conn.setTokenFile("temp/token.txt")
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
            raise ValueError('You entered to many roles for the amount of players')
        self.numwerewolfs = numwerewolfs
        self.amor = amor
        self.witch = witch
        self.prostitute = prostitute
        self.visionary = visionary

        # counters for days and night
        self.nd = 0 # number of days played
        self.nn = 0 # number of nights played

        #other arguments
        self.bkp_dir = bkp_dir

    def start(self):
        """start the game!
        
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
            r.greeting(self)
        self.bkp()

        time.sleep(40*self.wait_mult) # so everyone can get ready and has read his role
        self.chat.sendMsg(self.msg("greeting_start10s"))
        time.sleep(10*self.wait_mult)

        self.day()

    def dist_roles(self):
        """distribute the roles to the players"""
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
            self.roles.append(Amor(self.players[i], self))
            i += 1
    
    def restart(self):
        """start a new game with the same settings"""
        self.__init__(self.sk, self.chatid, self.numwerewolfs, 
                      self.amor, self.witch, self.prostitute, self.visionary, 
                      self.lang, self.wait_mult, self.log_dir, self.bkp_dir, 
                      do_debug = self.do_debug)

        self.log.info("Game got restarted")

        self.start()

    def night(self):
        """do a night phase

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
        """do a day phase!

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
        """check if game is over!

        Returns:
            bool -- True: game is over, on party won; 
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
        """end the game!"""
        self.chat.sendMsg(self.msg("end_intro"))
        time.sleep(5*self.wait_mult)
        self.chat.sendMsg("\n".join(self.get_players_role()))
        self.chat.sendFile(open(self.logfilename+".txt", "r"), 
                           name = "log_file.txt")
        
        #log the players that are still alive
        self.log.info("still alive were: " + 
                      " & ".join(self.get_players_role(all = False)))

    def get_players_role(self, all = True):
        """get a list of all players with their roles!

        Keyword Arguments:
            all {bool} -- True: every player of the game is listed; False: only the living players are listed (default: {True})

        Returns:
            list of str -- a list with one entry per player with: "name (role)"
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
        """get a list of players that are alive!

        Returns:
            list of Player -- list of players that are alive.
        """

        alive = []
        for p in self.players:
            if p.alive == True:
                alive.append(p)
        return alive

    def get_alive_string(self, noone=True):
        """get a list of players that are still alive as string entries with their number!

        Keyword Arguments:
            noone {bool} -- True: add "0: noone" to the list; 
                            False: only players without "0: noone"  (default: {True})

        Returns:
            list of str -- list with one entry per player, 
                           each entry is the number in the alive list + 1 and the name of the player
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
        """get a list of the activated roles of the game

        Returns:
            list of str -- list of the activated roles of the game
        """

        ls =[]
        for role in self.roles:
            ls.append(role.role)
        st = set(ls)
        if "Werewolf" in st:st.remove("Werewolf")
        if "Villager" in st: st.remove("Villager")
        ls = list(st)
        numvillagers = len(self.players)-len(ls)-self.numwerewolfs
        ls.append(str(numvillagers) + " Villager(s)")
        ls.append(str(self.numwerewolfs) + " Werewolf(s)")

        return ls

    def msg(self, filepath, line = "all"):
        """get the coresponding message in the selected language

        Arguments:
            filepath {str} -- the name of the message file, 
                          e.g. "greeting_all" for the first group message, 
                          this file needs to exist at least in the "msg/en/" folder

        Keyword Arguments:
            line {str or int} -- specify if the whole message should be returned ("all") 
                                 or only a specific line(int) (default: {"all"})

        Returns:
            str -- message in the selected language (self.lang) or in english if there is no translation
        """

        try:
            file = open("messages/"+self.lang+"/"+filepath+".txt", "r")
            if line == "all":
                msg = file.read()
            elif type(line) == int:
                msg = file.readlines()[line].replace("\n", "")
            file.close()
            return msg
        except FileNotFoundError:
            try:
                file = open("messages/en/"+filepath+".txt", "r")
                if line == "all":
                    msg = file.read()
                elif type(line) == int:
                    msg = file.readlines()[line].replace("\n", "")
                file.close()
                return msg
            except FileNotFoundError:
                print("no such file defined in any language")
                self.log.debug("the choosen message " + 
                               filepath + "didn't exist")

    def bkp(self):
        """backup the game!"""
        bkp = shelve.open(self.bkp_dir+"/backup_" + 
                          self.starttime.strftime("%Y-%m-%d_%H-%M-%S"))
        bkp["game"] = self
        bkp.close()

    @staticmethod
    def load_bkp(filepath):
        """load a backup-file

        Arguments:
            filepath {str} -- filepath of the backup-file to be loaded

        Returns:
            Game -- the old Game object
        """  

        #class methode to load a game from a backup
        bkp = shelve.open(filepath)
        game = bkp["game"]
        bkp.close()
        return game

    def continue_bkp(self):
        """continue a game that was loaded from a backup-file!"""
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


class Nightactions(object):
    """Class to log all the actions that happen in the night and resume

    Attributes:
        game {Game} -- the main Game object
        alive {list of Players} -- list of players that are still alive
        alive_string {list of str} -- list of players, that are still alive as "id: Name"
                                       id is place in alive list + 1
        lskill {list of bool} -- list of one bool for every player if (s)he got killed in the night
                                 e.g. lskill[1] says if player[1] got killed
        lstogether {list of tuple of int} -- list of players ids that stayed together during the night.
                                            always as tuple of two ids, first one is the player who stays at home
    """

    def __init__(self, alive, game, noone = True):
        """create a Nightaction logbbok for the night

        Arguments:
            alive {list of Players} -- list of players that are still alive
            game {Game} -- the main Game object

        Keyword Arguments:
            noone {bool} -- should there be an entry "0: noone" (default: {True})
        """

        self.game = game
        self.alive = alive 
        self.alive_string = game.get_alive_string(noone = noone)
        
        # create the lists to log
        self.lskill = [False]*len(alive)
        self.lstogether = []

    def kill(self, player_number):
        """kill a player

        Arguments:
            player_number {[type]} -- number of the player in the alive_string
        """        

        if not player_number == 0:
            self.lskill[player_number-1] = True

    def save(self, player_number):
        """save a player

        Arguments:
            player_number {[type]} -- number of the player in the alive_string
        """   
        if not player_number == 0:
            self.lskill[player_number-1] = False

    def together(self, player_home_number, player_visit_number):
        """set 2 people together for this night

        Arguments:
            player_home_number {int} -- the number in the alive_string of the player, who's at home
            player_visit_number {int} -- the number in the alive_string of the player, who's visiting the other
        """        
        #player_visit_number: prostitute, does not die unless player_home_number dies
        # convention in tuple first is unsave, second is save unless other dies
        if (not player_home_number == 0) and (not player_visit_number  == 0):
            self.lstogether.append((player_home_number-1, player_visit_number-1))

    def finish_night(self):
        """finish the night and get the name(group) of the plaers that died

        Returns:
            list of str -- A list of all the players that died this night as name(group)
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
        """get the id of the killed player

        Returns:
            int -- id of the killed player
        """      

        for i in range(len(self.alive)):
            if self.lskill[i]:
                return i

# Skype message waiting class
# --------------------------

class SkypeCommands(SkypeEventLoop):
    """Class to ask players for answers in Skype

    Attributes:
        chatid {str} -- chatid of the corresponding chat
        game {Game} -- the main Game object
        chat {SkypeChat} -- the group chat
    """

    def __init__(self, chatid, game, tokenFile = "temp/token.txt"):
        """initialize the object

        Arguments:
            chatid {str} -- chatid of the corresponding chat
            game {Game} -- the main Game object

        Keyword Arguments:
            tokenFile {str} -- the filepath of the token of the current Skype connection (default: {"temp/token.txt"})
        """

        super().__init__(tokenFile = tokenFile)
        self.game = game
        self.chatid = chatid
        self.chat = self.game.sk.chats[self.chatid]

    def ask(self, command, alive = [None], num_ids = 1, min_id = 0):
        """ask for an answer in the corresponding chat

        Arguments:
            command {str} -- command to ask for, 
                             e.g. "kill" for "kill: number" -- return int
                                or "bool" for "yes/no" -- return bool
                                or "name" for "name:" -- retrun str

        Keyword Arguments:
            alive {list of Player} -- all the alive Players that are at disponible (default: {[None]})
            num_ids {int} -- number of ids that must be asked for and returned (default: {1})
            min_id {int} -- the smallest id possible to choose from, 
                            basicaly if theire is an id 0 for "noone" disponible (default: {0})

        Returns:
            int or bool or str -- either the number(s) of the corresponding player(s) (alive[return-1])
                                  or a bool, depending on the command
                                  or a name(str), if command = "name"
        """      

        self.game.log.debug("SkypeCommand.ask("+ command + ") got called")

        # send explanation of the command	
        if command == "bool":
            self.chat.sendMsg(self.game.msg("ask", 0) + "\"Yes\" / \"No\"")
        else:
            self.chat.sendMsg(self.game.msg("ask", 0) + "\"" + command + ":" 
                              + self.game.msg("ask", 1) * num_ids + "\"")
        
        # check previous
        events = self.getEvents()
        for event in events:
            event.ack()

        # check the incoming events
        while True:
            events = self.getEvents()

            for event in events:
                if type(event) == SkypeNewMessageEvent:
                    if ((event.msg.chat.id == self.chatid) and 
                        (not event.msg.user.id == self.game.sk.user.id)):
                        msg = event.msg.content
                        self.game.log.debug("the message the SkypeCommands methode ask() received was :" + msg)
                        self.game.log.debug("from event: " + repr(event))
                        if command == "bool":
                            answer = self.get_bool(msg)
                        elif command == "name":
                            answer = self.get_name(msg)
                        else:
                            answer = self.get_id(msg, command, alive, 
                                                 num_ids, min_id)
                        if not answer == None:
                            return answer
                if self.autoAck:
                    event.ack()
            time.sleep(3)

    def get_id(self, msg, command, alive = [None], num_ids=1, min_id = 0):
        """check the message for an id and return it if the message was right

        Arguments:
            msg {str} -- the message text someone send to the chat
            command {str} -- command that was asked for, 
                             e.g. "kill" for "kill: number"

        Keyword Arguments:
            alive {list of Player} -- all the alive Players that are at disponible (default: {[None]})
            num_ids {int} -- number of ids that must be asked for and returned (default: {1})
            min_id {int} -- the smallest id possible to choose from, 
                            basicaly if theire is an id 0 for "noone" disponible (default: {0})

        Returns:
            int or None -- the number(s) of the corresponding player(s) (alive[return-1])
                           or None if the message wasn't a correct answer
        """

        #check for command and number with regular expression
        pat = (r"^" + command + r"[: ]+[\d]+" + r"(" + (r"[, ]+[\d]+"*(num_ids-1)) + r"[ ]*)$")
        match = re.match(pat, msg)
        if match:
            ids = re.findall(r"\d+", match[0])

            if (len(ids)==1) and (num_ids==1):			#if list is not allowed?-> only one
                id = int(ids[0])
                if (id >= min_id) and (id <= len(alive)):#check if number in list
                    if id == 0:
                        self.chat.sendMsg(self.game.msg("ask", 2) % 
                                          {"command" : command})
                    else:
                        self.chat.sendMsg(self.game.msg("ask", 3) % 
                                          {"command" : command, 
                                           "name" : alive[id-1].name})
                    return id
                else: 
                    self.chat.sendMsg(self.game.msg("ask", 4))

            elif (len(ids)==num_ids) and (len(set(ids))==num_ids):          	#if list is allowed
                list_id = []
                for id in ids:
                    id = int(id)
                    if (id >= min_id) and (id <= len(alive)):
                        list_id.append(id)
                    else: 
                        self.chat.sendMsg(self.game.msg("ask", 5) % {"id" : id})
                    if len(list_id)==num_ids:
                        self.chat.sendMsg(self.game.msg("ask", 6) + "!")
                        return list_id

            else:
                self.chat.sendMsg(self.game.msg("ask", 7))

    def get_bool(self, msg):
        """check if the message received was a "yes/no" answer and return it

        Arguments:
            msg {str} -- the message text someone send to the chat

        Returns:
            bool or None -- the answer to the question "yes":True; "no":False
                            or None if the message wasn't a correct answer
        """

        if re.match(r"^([ ]*(yes))", msg.lower()):
            self.chat.sendMsg(self.game.msg("ask", 6) + "\"yes\"!")
            return True
        elif re.match(r"^([ ]*(no))", msg.lower()):
            self.chat.sendMsg(self.game.msg("ask", 6) + "\"no\"!")
            return False
        else:
            self.chat.sendMsg(self.game.msg("ask", 7))

    def get_name(self, msg):
        """get the name the player sended

        Arguments:
            msg {str} -- the message text someone send to the chat

        Returns:
            str or None -- the Name entered
                           or None if the message was not a correct answer
        """

        match = re.match(r"^([ ]*(name)+[: ]+)", msg.lower())
        if match:
            return msg[match.span()[1]:]
        else:
            return None

#---------------------------------------------------------------
# Player definition
#---------------------------------------------------------------
class Player(object):
    """
    class for every player
    
    Attributes:
        chatid {str} -- chatid of the corresponding skpy.SkypeSingleChat of the player
        id {str} -- Skype id of the player
        game {Game} -- the main Game object
        chat {SkypeChat} -- the single chat of the player
        skc {SkypeCommands} -- object of the SkypeCommands class for the single chat of the player
        name {str} -- Name of the player
        alive {bool} -- True: the player is alive ; False: the player is dead
        love {bool} -- True: the player is in love with someone
        lover {Player} -- The player (s)he is in love with
        role {Role} -- The role the player has got for the game
    """    

    def __init__(self, id, game):
        """initilalize the player

        Arguments:
            id {str} -- Skype id of the player
            game {Game} -- the main Game object
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
        """throw an arrow at this player, so (s)he fells in love

        Arguments:
            lover {Player} -- The player (s)he fells in love with
        """        
        self.love = True
        self.lover = lover #Player object
        self.chat.sendMsg(self.game.msg("player_arrow") + lover.name)

    def die(self, answer = True):
        """the player dies

        Keyword Arguments:
            answer {bool} -- should the methode return the name and the group of the player
                             e.g. True: the methode returns "name (group)"  (default: {True})

        Returns:
            str or None -- "name (group)" of the player or None if the answer argument is False
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
        """get a string with the name and the group of the player

        Returns:
            str -- "name (group)" of the player
        """  

        return self.name + "("+self.role.group+")"

    def get_name_role(self):
        """get a string with the name and role of the player

        Returns:
            str -- "name (role)" of the player
        """  

        return self.name + "("+self.role.role+")"


#------------------------------------------------------------------------------------------------
# Role definitions
#------------------------------------------------------------------------------------------------

class Role(object):
    """main class for the roles

    Attributes:
        role {str} -- the name of the role
        group {str} -- the name of the group "Werewolf"/"Villager"
        player {list of Player} -- all the players that belong to this role
        game {Game} -- the main Game object
        chatid {str} -- SkypeChat id of the player(s) chat
        game {Game} -- the main Game object
        chat {SkypeChat} -- group/single SkypeChat of the player(s)
        skc {SkypeCommands} -- object of the SkypeCommands class for this role
    """ 

    role = "not set"
    group = "not set"

    def __init__(self, player, game):
        """initilaize the Role object

        Arguments:
            player {list of Player} -- all the players that belong to this role
            game {Game} -- the main Game object
            chatid {str} -- SkypeChat id of the player(s) chat
            game {Game} -- the main Game object
            chat {SkypeChat} -- group/single SkypeChat of the player(s)
            skc {SkypeCommands} -- object of the SkypeCommands class for this role
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
        """inform players about their role"""        
        self.chat.sendMsg(self.game.msg("greeting_"+ self.role.lower()))

    def night(self, nightactions):
        """do the corresponding night phase

        Arguments:
            nightactions {Nightactions} -- log of all the actions that happen(d) in the night
        """

        pass

    def get_names(self):
        """get the names of the players of this role

        Returns:
            list of str -- list of all the names of the roles players
        """

        names = []
        for i in range(len(self.players)):
            names.append(self.players[i].name)
        return names

    def msg_group_night(self):
        """send a notification to the group chat, which role got called"""        
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
    """class of the werewolf role

    Attributes:
        role {str} -- the name of the role
        group {str} -- the name of the group "Werewolf"/"Villager"
        player {list of Player} -- all the players that belong to this role
        game {Game} -- the main Game object
        chatid {str} -- SkypeChat id of the player(s) chat
        game {Game} -- the main Game object
        chat {SkypeChat} -- group/single SkypeChat of the player(s)
        skc {SkypeCommands} -- object of the SkypeCommands class for this role
    """  

    role = "Werewolf"
    group = "Werewolf"
    
    def night(self, nightactions):
        """do the Werewolfs night phase

        ask whome to kill this night

        Arguments:
            nightactions {Nightactions} -- log of all the actions that happen(d) in the night
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
    """class for the Villager role

    Attributes:
        role {str} -- the name of the role
        group {str} -- the name of the group "Werewolf"/"Villager"
        player {list of Player} -- all the players that belong to this role
        game {Game} -- the main Game object
        chatid {str} -- SkypeChat id of the player(s) chat
        game {Game} -- the main Game object
        chat {SkypeChat} -- group/single SkypeChat of the player(s)
        skc {SkypeCommands} -- object of the SkypeCommands class for this role
    """ 

    role = "Villager"
    group = "Villager"

class Amor(Villager):
    """class for the Amor role

    Attributes:
        role {str} -- the name of the role
        group {str} -- the name of the group "Werewolf"/"Villager"
        player {list of Player} -- all the players that belong to this role
        game {Game} -- the main Game object
        chatid {str} -- SkypeChat id of the player(s) chat
        game {Game} -- the main Game object
        chat {SkypeChat} -- group/single SkypeChat of the player(s)
        skc {SkypeCommands} -- object of the SkypeCommands class for this role
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
    """class for the Prostitute role

    Attributes:
        role {str} -- the name of the role
        group {str} -- the name of the group "Werewolf"/"Villager"
        player {list of Player} -- all the players that belong to this role
        game {Game} -- the main Game object
        chatid {str} -- SkypeChat id of the player(s) chat
        game {Game} -- the main Game object
        chat {SkypeChat} -- group/single SkypeChat of the player(s)
        skc {SkypeCommands} -- object of the SkypeCommands class for this role
    """ 

    role = "Prostitute"

    def night(self, nightactions):
        """do the Prostetutes night phase

        ask where (s)he wants to stay

        Arguments:
            nightactions {Nightactions} -- log of all the actions that happen(d) in the night
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
    """class for the Witch role

    Attributes:
        role {str} -- the name of the role
        group {str} -- the name of the group "Werewolf"/"Villager"
        player {list of Player} -- all the players that belong to this role
        game {Game} -- the main Game object
        chatid {str} -- SkypeChat id of the player(s) chat
        game {Game} -- the main Game object
        chat {SkypeChat} -- group/single SkypeChat of the player(s)
        skc {SkypeCommands} -- object of the SkypeCommands class for this role
        elixier {bool} -- True: the witchs elixier is still available
                          False: the witchs elixier got already used
        poison {bool} -- True: the witchs elixier is still available
                         False: the witchs elixier got already used
    """ 
    
    role = "Witch"
    
    def greeting(self):
        """inform player about their role and initialize the poison and elixier"""
        super().greeting()
        self.poison = True
        self.elixier = True

    def night(self, nightactions):
        """do the witchs night phase

        tell her whos going to die
        ask if he wants to save, by using her elixier
        ask if he wants to kill someone, by using her poison

        Arguments:
            nightactions {Nightactions} -- log of all the actions that happen(d) in the night
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
    """class for the Visionary role

    Attributes:
        role {str} -- the name of the role
        group {str} -- the name of the group "Werewolf"/"Villager"
        player {list of Player} -- all the players that belong to this role
        game {Game} -- the main Game object
        chatid {str} -- SkypeChat id of the player(s) chat
        game {Game} -- the main Game object
        chat {SkypeChat} -- group/single SkypeChat of the player(s)
        skc {SkypeCommands} -- object of the SkypeCommands class for this role
    """ 
    
    role = "Visionary"

    def night(self, nightactions):
        """do the visionarys night phase

        ask whome (s)he wants to see
        tell him/her the group of this player

        Arguments:
            nightactions {Nightactions} -- log of all the actions that happen(d) in the night
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

# To do
    # define more roles