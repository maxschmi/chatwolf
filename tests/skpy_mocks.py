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
#           Mock class definitions for the skpy package                 #
#                                                                       #
#-----------------------------------------------------------------------#

# libraries
import random as rd
import re
import logging
import string

# logger
log = logging.getLogger("Test")

# new Skype classes

class Data(object):
    userId = "8: game master"
    username = ("Game", "Master")
    contactuserIds = ['live:maxmul_13', 'live:joe.4', 'live:anna.b', 
           'live:Pedro.ola', 'live:Herta.immer', 'live:Mark.polo97',
           'live:34526664738819gfet', 'live:markkling', 'live:Kängu.Viet', 'live:Karl.Otto']

    names = [("Max", "Muller"), ("Joe", ""), ("Anna","Bella"), 
            ("Pedro", "Olander"), ("Herta", "Immer"), ("Marko", "Polo"),
            (None, None), ("Mark","Kling"), ("Käng","Guru"), ("Karlchens", "Otto")]
    random_msgs = ["you are so cool", "I want to kill 3", "let's kill Max",
                "I am so in love", "Where shall we go", "Throw your arrow at yourself", 
                "to kill is easy (2)"]
    chatid = '19:3gf94f3ba215466aa082243763x67234@thread.skype'

class Skype(object):
    def __init__(self):
        self.conn = SkypeConnection()
        self.contacts = SkypeContacts(self)
        self.chats = SkypeChats(self)
        self.userId = Data.userId
        Skype.last_instance = self
        
        #for collecting data during game run
        self.active_chat = None
        self.received_msgs = []

class SkypeConnection(object):
    def __init__(self):
        self.connected = True

    def setTokenFile(self, file):
        pass

    def writeToken(self):
        pass



class SkypeChats(object):
    def __init__(self, sk = None):
        self.sk = sk
        self.ids = []
        self.chats = []

        for c in sk.contacts:
            self.chats.append(c.chat)

        self.groupchat = SkypeChat(Data.contactuserIds + [Data.userId], self.sk)
        self.groupchat.id = Data.chatid
        self.chats.append(self.groupchat)

    def __getitem__(self, id):
        if type(id) == str:
            for c in self.chats:
                if c.id == id:
                    return c
        
            raise AttributeError("No such attribute in chats: " + id)
        elif type(id) == int:
            return self.chats[id]

    def create(self, userIds):
        exists = False
        if len(userIds)==1 :
            for c in self.chats:
                if userIds in c.userIds:
                    exists = True
                    return c

        if not exists:
            chat = SkypeChat(userIds, self.sk)
            self.chats.append(chat)
            return chat


class SkypeChat(object):
    def __init__(self, userIds, sk = None):
        self.sk = sk
        if type(userIds) == list:
            self.userIds = userIds
        else:
            self.userIds = [userIds]

        if len(self.userIds)==1:
            self.id = "8:" + self.userIds[0]
            self.userId = self.userIds[0]
        else:
            self.id = '19:' + "".join(rd.sample(list(map(str , range(10))) + list(string.ascii_lowercase), 32)) +'@thread.skype'


    def sendMsg(self, text):
        self.sk.received_msgs.append(text)
        self.sk.active_chat = self
        log.info("called: sendMsg(\n\t"+ text +")\n\t to chat " + self.id)

        if "I am still waiting until" in text:
            SkypeContacts.do_SkypeUser = False

    def sendFile(self, file, name = None):
        log.info("called: sendFile() \n\t to chat " + self.id)

    def setTopic(self, name):
        log.info("called: sendTopic(" + name + ") \n\t to chat " + self.id)



class SkypeContacts(object):
    do_SkypeUser = True

    def __init__(self, sk = None):
        self.sk = sk
        ids = Data.contactuserIds + [Data.userId]
        names_raw = Data.names + [Data.username]
        names = []
        for i in range(len(names_raw)):
            names.append(Name(names_raw[i][0], names_raw[i][1]))
        
        self.contacts = []
        for i in range(len(ids)):
            if self.do_SkypeUser:
                self.contacts.append(SkypeUser(ids[i], names[i], sk))
            else:
                self.contacts.append(SkypeContact(ids[i], names[i], sk))

        self.dict = dict(zip(ids, self.contacts))

    def __getitem__(self, id):
        if type(id) == str:
            for c in self.contacts:
                if c.id == id:
                    return c
            else:
                raise AttributeError("No such attribute: " + id)
        elif type(id) == int:
            return self.contacts[id]

class SkypeUser(object):
    def __init__(self, userId, name, sk = None):
        self.sk = sk
        self.userid = userId
        self.id = userId
        self.name = name
        self.chat = SkypeChat(userId, sk)

    def invite(self, msg = "None"):
        log.info(self.userid + " got invited with message:\n\t " + msg)

class SkypeContact(object):
    def __init__(self, userId, name, sk = None):
        self.sk = sk
        self.userid = userId
        self.id = userId
        self.name = name
        self.chat = SkypeChat(userId, sk)

class Name(object):
    def __init__(self, first, last):
        self.first = first
        self.last = last





class SkypeEventLoop(object):
    def __init__(self, tokenFile = None):
        pass

    def getEvents(self):
        self.autoAck = True
        events = []
        for i in rd.sample(range(4), 1):
            events.append(SkypeNewMessageEvent(Skype.last_instance))
        return events

class Event(object):
    def __init__(self, sk = None):
        self.sk = sk
        self = SkypeNewMessageEvent(sk)

    def ack(self):
        pass

class SkypeNewMessageEvent(Event):
    def __init__(self, sk = None):
        self.sk = sk
        self.msg = SkypeMessage(sk)

class SkypeMessage(object):
    def __init__(self, sk = None):
        self.sk = sk
        self.corect_userIds = self.sk.active_chat.userIds
        if Data.userId in self.corect_userIds:
            self.corect_userIds.remove(Data.userId)

        if rd.randint(0,15)<10:
            self.random_msg()
        else:
            self.corect_msg()
        log.info("SkypeMessage-Mock returned: \n\t"+ self.content +
                "\n\t from " + self.user.id + "\n\t in chat: " + self.chat.id)

    def random_msg(self):
        self.content = rd.sample(Data.random_msgs, 1)[0]
        rdint = rd.randint(0,15)
        if rdint<=8: #wrong chat
            self.user = self.sk.contacts[rd.sample(self.sk.contacts.contacts, 1)[0].id]
            self.chat = self.user.chat
        else: #correct chat, but game-master can also message
            list_ids = self.sk.active_chat.userIds
            self.user = self.sk.contacts[rd.sample(list_ids, 1)[0]]
            self.chat = self.sk.active_chat
        self.chat = self.user.chat

    def corect_msg(self):
        list_ids = self.sk.active_chat.userIds
        self.user = self.sk.contacts[rd.sample(list_ids, 1)[0]]
        self.chat = self.sk.active_chat

        i = len(self.sk.received_msgs)-1
        self.content = None
        while self.content == None and i>=0:
            msg = self.sk.received_msgs[i]
            if 'Send me: "Yes" / "No"' == msg:
                self.content = rd.sample(["yes", "no"], 1)[0]

            elif "Send me: \"" in msg:
                match = re.search(r"^[a-z]+", msg[10:])
                if match:
                    command = match[0]
                    num_ids = len(re.findall("number", msg))
                    list = self.sk.received_msgs[i-1]
                    min_id = int(list[0])
                    max_id = len(re.findall("\n", list))+min_id

                    ids = []
                    for i in range(num_ids):
                        ids.append(str(rd.randint(min_id, max_id)))

                    self.content = (command + 
                                rd.sample([":", " ", ": ", " : "], 1)[0] + 
                                rd.sample([",", " ", ", "], 1)[0].join(ids))

            i -= 1

        if not self.content:
            self.random_msg()

def sleep(sek):
    pass

def super_skypeeventloop():
    return SkypeEventLoop()