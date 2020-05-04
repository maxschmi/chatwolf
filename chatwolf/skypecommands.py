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
#                     SkypeCommands classe                              #
#                                                                       #
#-----------------------------------------------------------------------#

# other libraries
from skpy import SkypeEventLoop, SkypeNewMessageEvent
import re
import time


# Skype message waiting class
# --------------------------

class SkypeCommands(SkypeEventLoop):
    """Class to ask players for answers in Skype.

    Attributes:
        chatid (str): chatid of the corresponding chat
        game (Game): the main Game object
        chat (SkypeChat): the group chat
    """

    def __init__(self, chatid, game, tokenFile = "temp/token.txt"):
        """Initialize the object.

        Args:
            chatid (str): chatid of the corresponding chat
            game (Game): the main Game object

        Keyword Args:
            tokenFile (str, optional): the filepath of the token of the current Skype connection . Defaults to "temp/token.txt".
        """

        super().__init__(tokenFile = tokenFile)
        self.game = game
        self.chatid = chatid
        self.chat = self.game.sk.chats[self.chatid]

    def ask(self, command, alive = [None], num_ids = 1, min_id = 0):
        """Ask for an answer in the corresponding chat.

        Args:
            command (str): command to ask for, e.g. "kill" for "kill: number": return int
                           or "bool" for "yes/no": return bool
                           or "name" for "name:": retrun str

        Keyword Args:
            alive (list of Player, optional): all the alive Players that are at disponible . Defaults to [None].
            num_ids (int, optional): number of ids that must be asked for and returned . Defaults to 1.
            min_id (int, optional): the smallest id possible to choose from, 
                            basicaly if theire is an id 0 for "noone" disponible . Defaults to 0.

        Returns:
            int or bool or str: either the number(s) of the corresponding player(s) (alive[return-1]) 
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
        """Check the message for an id and return it if the message was right.

        Args:
            msg (str): the message text someone send to the chat
            command (str): command that was asked for, 
                             e.g. "kill" for "kill: number"

        Keyword Args:
            alive (list of Player, optional): all the alive Players that are at disponible . Defaults to [None].
            num_ids (int, optional): number of ids that must be asked for and returned . Defaults to 1.
            min_id (int, optional): the smallest id possible to choose from, 
                            basicaly if theire is an id 0 for "noone" disponible . Defaults to 0.

        Returns:
            int or None: the number(s) of the corresponding player(s) (alive[return-1])
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
        """Check if the message received was a "yes/no" answer and return it.

        Args:
            msg (str): the message text someone send to the chat

        Returns:
            bool or None: the answer to the question "yes":True; "no":False
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
        """Get the name the player sended.

        Args:
            msg (str): the message text someone send to the chat

        Returns:
            str or None: the Name entered
                           or None if the message was not a correct answer
        """

        match = re.match(r"^([ ]*(name)+[: ]+)", msg.lower())
        if match:
            return msg[match.span()[1]:]
        else:
            return None
