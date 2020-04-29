#-------------------#
#                   #
#    werewolf game  #
#     per skype     #
#     Max Schmit    #
#    march 2020     #
#                   #
# main Game classes #
#-------------------#


# librarys
from skpy import Skype, SkypeEventLoop, SkypeNewMessageEvent, SkypeUser, SkypeContacts
import time
import random as rd
import re
import logging
import datetime
import shelve
import sys

#Game Class definition = Gamemaster
#---------------------
	# testvalues
	# chatid = '19:3db90f3ba215466aa082243848d24289@thread.skype'

class Game:
	def __init__(self, sk, chatid, numwerewolfs, amor = False, witch = False, prostitute = False, visionary = False, 
			  lang = "en", wait_mult = 1, log_dir = "logs", bkp_dir = "bkp", do_debug = True):
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

		self.logfilename = log_dir + "/Game_" + self.starttime.strftime("%Y-%m-%d_%H-%M-%S")
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
							#format='%(asctime)s - %(levelname)s - %(message)s',
							level=logging.DEBUG)

		#Players
		self.player_ids = self.chat.userIds
		if self.sk.userId in self.player_ids:
			self.player_ids.remove(self.sk.userId)
		self.numplayers = len(self.player_ids)
		self.players = list()
		for i in range(self.numplayers):
			self.players.append(Player(self.player_ids[i], self))

		#Roles
		self.numroles = numwerewolfs + amor + witch + prostitute + visionary
		if self.numroles > self.numplayers:
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
				self.chat.sendMsg(self.msg(error))
				if (i%6 == 0) or (i == 0):
					self.chat.sendMsg(self.msg("error_request").format(" & ".join(pl_error)))
			else:
				break

			i +=1
			time.sleep(4)
		
		#Greet players
		self.chat.sendMsg(self.msg("greeting_all") % {"numplayers": self.numplayers, "numwerwolfs": self.numwerewolfs})
		time.sleep(20*self.wait_mult)

		self.dist_roles()

		self.chat.sendMsg(self.msg("greeting_all_roles") + (" & ".join(self.get_roles())))
		
		self.log.info("Rolls got distributed: \n"+ " "*30 + ("\n" + " "*30).join(self.get_players_role()))
		# greet Roles
		for r in self.roles:
			r.greeting(self)
		self.bkp()

		time.sleep(40*self.wait_mult) # so everyone can get ready and has read his role
		self.chat.sendMsg(self.msg("greeting_start10s"))
		time.sleep(10*self.wait_mult)

		self.day()

	def dist_roles(self):
		# distribute rols in order of appearence in the night
		rd.shuffle(self.players)
		
		self.roles = list()
		i = 0

		if self.prostitute: 
			self.roles.append(Prostitute(self.players[i], self))
			i += 1

		self.werewolfs = Werewolf(self.players[i:(self.numwerewolfs+i)], self)
		self.roles.append(self.werewolfs)
		i += self.numwerewolfs
		
		if self.amor: 
			self.roles.append(Amor(self.players[i], self))
			i += 1

		if self.witch: 
			self.roles.append(Witch(self.players[i], self))
			i += 1

		if self.visionary: 
			self.roles.append(Visionary(self.players[i], self))
			i += 1
		
		for j in range(i, self.numplayers):
			self.roles.append(Villager(self.players[j], self))
	
	def restart(self):
		self.__init__(self.sk, self.chatid, self.numwerewolfs, self.amor, self.witch, self.prostitute, self.visionary, 
				self.lang, self.wait_mult, self.log_dir, self.bkp_dir, du_debug = self.do_debug)

		self.log.info("Game got restarted")

		self.start()

	def night(self):
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
			msg = msg + "\n" + self.msg("night_resume", line = 2) % {"names": " & ".join(killed)}
			self.log.info("Resume night: "+" & ".join(killed) + " got killed during the night")
		self.chat.sendMsg(msg)

		time.sleep(5*self.wait_mult)
		if not self.is_end():
			self.bkp()
			self.day()

	def day(self):
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
			self.chat.sendMsg(self.msg("day_killed", 0) + " " + self.msg("day_killed", 1).join(killed))
			self.log.info(" & ".join(killed)+"got killed.")
		
		time.sleep(4*self.wait_mult)
		if not self.is_end():
			self.bkp()
			self.chat.sendMsg(self.msg("day_end"))
			while not self.skc.ask("bool"): pass
			time.sleep(3*self.wait_mult)
			self.night()

	def is_end(self):
		#test if one Party won
		alive = self.get_alive()
		
		# test if all are dead -> noone wins
		if len(alive) == 0:
			self.chat.sendMsg(self.msg("end_noone"))
			self.log.info("The Game ends, because all players are dead!\nNo one won!")
			time.sleep(2*self.wait_mult)
			self.end()
			return True

		#Test love Win
		if len(alive)==2:
			if (alive[0].love == True) and (alive[1].love == True):
				self.chat.sendMsg(self.msg("end_love").format(alive[0].name, alive[1].name))
				self.log.info("The Game ends, because only the loving players are alive!\nThe love won!")
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
			self.log.info("The Game ends, because only werewolfs are alive!\nThe werewolfs won!")
			time.sleep(2*self.wait_mult)
			self.end()
			return True

		# Test villager win?
		if werwolf_count == 0:
			self.chat.sendMsg(self.msg("end_villager"))
			self.log.info("The Game ends, because only villagers are alive!\nThe villagers won!")
			time.sleep(2*self.wait_mult)
			self.end()
			return True

		return False
		pass

	def end(self):
		self.chat.sendMsg(self.msg("end_intro"))
		time.sleep(5*self.wait_mult)
		self.chat.sendMsg("\n".join(self.get_players_role()))
		self.chat.sendFile(open(self.logfilename+".txt", "r"), name = "log_file.txt")
		
		#log the players that are still alive
		self.log.info("still alive were: " + " & ".join(self.get_players_role(all = False)))

	def get_players_role(self, all = True):
		# return list +Role: Player
		list = []
		for player in self.players:
			if all:
				list.append(player.get_name_role())
			elif not all:
				if player.alive:
					list.append(player.get_name_role())

		return list
		pass

	def changeRoles(self, numwerewolfs = None, amor = None, witch = None, prostitute = None):
		if numwerewolfs != None:
			self.numwerewolfs = numwerewolfs
		if amor != None:
			self.amor = amor
		if witch != None:
			self.witch = witch
		if prostitute != None:
			self.prostitute = prostitute

	def get_alive(self):
		alive = []
		for p in self.players:
			if p.alive == True:
				alive.append(p)
		return alive

	def get_alive_string(self, noone=True):
		alive_players = self.get_alive()

		if noone:
			alive_string = ["0 : No one"]
		else:
			alive_string = []

		for i in range(len(alive_players)):
			alive_string.append(str(i+1) + " : " + alive_players[i].name)
		return "\n".join(alive_string)

	def get_roles(self):
		ls =[]
		for role in self.roles:
			ls.append(role.role)
		st = set(ls)
		if "Werewolf" in st:st.remove("Werewolf")
		if "Villager" in st: st.remove("Villager")
		ls = list(st)
		ls.append(str(len(self.players)-len(ls)-self.numwerewolfs) + " Villager(s)")
		ls.append(str(self.numwerewolfs) + " Werewolf(s)")

		return ls

	def msg(self, file, line = "all"):
		try:
			if line == "all":
				return open("messages/"+self.lang+"/"+file+".txt", "r").read()
			elif type(line) == int:
				return open("messages/"+self.lang+"/"+file+".txt", "r").readlines()[line].replace("\n", "")
		except FileNotFoundError:
			try:
				if line == "all":
					return open("messages/en/"+file+".txt", "r").read()
				elif type(line) == int:
					return open("messages/en/"+file+".txt", "r").readlines()[line].replace("\n", "")
			except FileNotFoundError:
				print("no such file defined in any language")

	def bkp(self):
		bkp = shelve.open(self.bkp_dir+"/backup_" + self.starttime.strftime("%Y-%m-%d_%H-%M-%S"))
		bkp["game"] = self
		bkp.close()

	def load_bkp(file):
		#class methode to load a game from a backup
		bkp = shelve.open(file)
		game = bkp["game"]
		bkp.close()
		return game

	def continue_bkp(self):
		# methode to continue the game that was loaded from a backup file because the game is not finished yet
		self.log.info("The game continues from a backupfile")

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


class Nightactions:
	def __init__(self, alive, game, noone = True):
		self.game = game
		self.alive = alive #list of Players that are alive
		# create a string with the Players numbers, that can be printed
		self.alive_names = []

		self.noone = noone
		if self.noone:
			self.alive_string = ["0 : No one"]
		else:
			self.alive_string = []

		for i in range(len(alive)):
			self.alive_names.append(alive[i].name)
			self.alive_string.append(str(i+1) + " : " + self.alive[i].name)
		self.alive_string = "\n".join(self.alive_string)

		# create the lists to log
		self.lskill = [False]*len(alive)
		self.lstogether = []

	def kill(self, person_number):
		if not person_number == 0:
			self.lskill[person_number-1] = True

	def save(self, person_number):
		if not person_number == 0:
			self.lskill[person_number-1] = False

	def together(self, person_notsave_number, person_save_number):
		#person_save_number: prostitute, does not die unless person_notsave_number dies
		# convention in tuple first is unsave, second is save unless other dies
		if (not person_notsave_number == 0) and (not person_save_number  == 0):
			self.lstogether.append((person_notsave_number-1, person_save_number-1))

	def finish_night(self):
		# save the persons that were not at home
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
		pass

	def get_killed_id(self):
		for i in range(len(self.alive)):
			if self.lskill[i]:
				return i
				pass

# Skype message waiting class
# --------------------------

#token "temp/token.txt"
class SkypeCommands(SkypeEventLoop):
	def __init__(self, chatid, game, tokenFile = "temp/token.txt"):
		super().__init__(tokenFile = tokenFile)
		self.game = game
		self.chatid = chatid
		self.chat = self.game.sk.chats[self.chatid]

	def ask(self, command, alive = [None], num_ids = 1, min_id = 0):
		self.game.log.debug("SkypeCommand.ask("+ command + ") got called")
		# command can be "kill: 1" or "save: 1" 
		# or "bool" for boolean answer		
		if command == "bool":
			self.chat.sendMsg(self.game.msg("ask", 0) + "\"Yes\" / \"No\"")
		else:
			self.chat.sendMsg(self.game.msg("ask", 0) + "\"" + command + ":" + self.game.msg("ask", 1) * num_ids + "\"")
		
		# check previous
		events = self.getEvents()
		for event in events:
			event.ack()

		while True:
			events = self.getEvents()

			for event in events:
				if type(event) == SkypeNewMessageEvent:
					if (event.msg.chat.id == self.chatid) and (not event.msg.user.id == self.game.sk.user.id):
						msg = event.msg.content
						self.game.log.debug("the message the SkypeCommands methode ask() received was :" + msg)
						self.game.log.debug("from event: " + repr(event))
						if command == "bool":
							answer = self.get_bool(msg)
						elif command == "name":
							answer = self.get_name(msg)
						else:
							answer = self.get_id(msg, command, alive, num_ids, min_id)
						if not answer == None:
							return answer
				if self.autoAck:
					event.ack()
			time.sleep(3)

	def get_id(self, msg, command, alive = [None], num_ids=1, min_id = 0):
		#check for command and number with regular expression
		pat = (r"^" + command + r"[: ]+[\d]+" + "(" + (r"[, ]+[\d]+"*(num_ids-1)) + r"[ ]*)$")
		mat = re.match(pat, msg)
		if mat:
			ids = re.findall("\d+", mat[0])

			if (len(ids)==1) and (num_ids==1):			#if list is not allowed?-> only one
				id = int(ids[0])
				if (id >= min_id) and (id <= len(alive)):#check if number in list
					if id == 0:
						self.chat.sendMsg(self.game.msg("ask", 2) % {"command" : command})
					else:
						self.chat.sendMsg(self.game.msg("ask", 3) % {"command" : command, "name" : alive[id-1].name})
					return id
				else: 
					self.chat.sendMsg(self.game.msg("ask", 4))

			elif (len(ids)==num_ids) and (len(set(ids))==num_ids):					#if list is allowed
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
				# print("error:" + msg) #for searching of errors
				self.chat.sendMsg(self.game.msg("ask", 7)) # error

	def get_bool(self, msg):
		if "yes" in msg.lower():
			self.chat.sendMsg(self.game.msg("ask", 6) + "\"yes\"!")
			return True
		elif "no" in msg.lower():
			self.chat.sendMsg(self.game.msg("ask", 6) + "\"no\"!")
			return False
		elif not (self.game.msg("ask", 7) in msg):
			self.chat.sendMsg(self.game.msg("ask", 7))

	def get_name(self, msg):
		re.sub("name: ", "", msg)
		re.sub("Name: ", "", msg)
		re.sub("name:", "", msg)
		re.sub("Name:", "", msg)
		re.sub("Name ", "", msg)
		re.sub("name ", "", msg)
		return msg

#---------------------------------------------------------------
# Player definition
#---------------------------------------------------------------
class Player:
	def __init__(self, id, game):
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
		if self.name == " ":
			self.name = skc.ask("name")
		
		self.alive = True
		self.love = False
		self.role = None

	def love_arrow(self, lover):
		self.love = True
		self.lover = lover #Player object
		self.chat.sendMsg(self.game.msg("player_arrow") + lover.name)

	def die(self, answer = True):
		self.alive = False
		self.game.log.info(self.name + " dies")
		if self.love:
			self.lover.alive = False
			self.game.log.info(self.name + " was in love with " + self.lover.name + ", therefor (s)he died too!")
			if answer: 
				return [self.name + "(" + self.role.group + ")", self.lover.name+ "(" + self.lover.role.group + ")"]
		else:
			if answer:
				return [self.name+ "(" + self.role.group + ")"]

	def get_name_group(self):
		return self.name + "("+self.role.group+")"

	def get_name_role(self):
		return self.name + "("+self.role.role+")"


#------------------------------------------------------------------------------------------------
# Role definitions
#------------------------------------------------------------------------------------------------

class Role:
	role = "not set"
	group = "not set"

	def __init__(self, player, game):
		self.game = game
		# add Player(s)
		if type(player)==list:
			self.players = player
		else:
			self.players = [player]

		#add Skype Chat variables
		if len(self.players) > 1:
			self.player_ids = []
			for pl in self.players:
				self.player_ids.append(pl.id)
			self.chatid = self.game.sk.chats.create(self.player_ids).id
			self.game.sk.chats[self.chatid].setTopic(self.role + "_group")
		else:
			self.chatid = self.players[0].chatid
		self.chat = self.game.sk.chats[self.chatid]
		self.skc = SkypeCommands(self.chatid, self.game)

		for player in self.players:
			player.role = self
		
	def greeting(self, game = None):
		self.chat.sendMsg(self.game.msg("greeting_"+ self.role.lower()))

	def night(self, nightactions):
		pass

	def getNames(self):
		names = []
		for i in range(len(self.players)):
			names.append(self.players[i].name)
		return names

	def msg_group_night(self):
		self.game.chat.sendMsg("I call the {0}".format(self.role))
		# test if a player of the role is still alive
		test_alive = False
		for p in self.players:
			if p.alive:
				test_alive = True
		# wait a random time, so it is not possible to know if a role is already dead
		if not test_alive:
			sleeptime = rd.gauss(15, 5)
			while st <7:
				sleeptime = rd.gauss(15, 5)
			time.sleep(sleeptime * self.wait_mult)


class Werewolf(Role):
	role = "Werewolf"
	group = "Werewolf"
	
	def night(self, nightactions):
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
			self.game.log.info("The werewolf(s) killed " + nightactions.alive[id-1].get_name_group())

class Villager(Role):
	role = "Villager"
	group = "Villager"

class Amor(Villager):
	role = "Amor"

	def greeting(self, game):
		super().greeting()
		alive = game.get_alive()
		alive_string = game.get_alive_string(noone = False)
		self.chat.sendMsg(alive_string)
		ids = self.skc.ask("arrow", alive, num_ids = 2, min_id = 1)
		alive[ids[0]-1].love_arrow(alive[ids[1]-1])
		alive[ids[1]-1].love_arrow(alive[ids[0]-1])

		#log
		self.game.log.info("Amor trows his arrow to "+ " & ".join([alive[ids[0]-1].name, alive[ids[1]-1].name]))

class Prostitute(Villager):
	role = "Prostitute"

	def night(self, nightactions):
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
	role = "Witch"
	
	def greeting(self, game = None):
		super().greeting()
		self.poison = True
		self.elixier = True

	def night(self, nightactions):
		self.msg_group_night()
		self.chat.sendMsg(self.game.msg("night_"+ self.role.lower()) % {"elixier": int(self.elixier), "poison": int(self.poison)})
		
		killed_id = nightactions.get_killed_id()
		if (killed_id == None):
			self.chat.sendMsg(self.game.msg("night_witch_noone"))
		else:
			killed_name = nightactions.alive[killed_id].name
			time.sleep(1*self.game.wait_mult)
			if self.elixier:
				self.chat.sendMsg(self.game.msg("night_witch_save", 0) % {"killed": killed_name} + self.game.msg("night_witch_save", 1))
				if self.skc.ask("bool"):
					nightactions.save(killed_id+1)
					self.elixier = False
					self.game.log.info("The witch uses her elixier and saves " + killed_name)
			else:
					self.chat.sendMsg(self.game.msg("night_witch_save", 0) % {"killed": killed_name} + self.game.msg("night_witch_save", 2))

		time.sleep(1*self.game.wait_mult)
		if self.poison:
			self.chat.sendMsg(self.game.msg("night_"+ self.role.lower()+"_kill"))
			time.sleep(1*self.game.wait_mult)
			if self.skc.ask("bool"):
				self.chat.sendMsg(self.game.msg("night_"+ self.role.lower()+"_kill_list"))
				self.chat.sendMsg(nightactions.alive_string)
				id = self.skc.ask("kill", nightactions.alive)
				if not id == 0:
					nightactions.kill(id)
					self.poison = False
					self.game.log.info("The witch uses her poison to kill " + nightactions.alive[id-1].name)
		time.sleep(2*self.game.wait_mult)
		self.chat.sendMsg(self.game.msg("night_sleep"))
		
class Visionary(Villager):
	role = "Visionary"

	def night(self, nightactions):
		self.msg_group_night()
		self.chat.sendMsg(self.game.msg("night_"+ self.role.lower()))
		self.chat.sendMsg(nightactions.alive_string)
		id = self.skc.ask("see", nightactions.alive)
		if not id == 0:
			id -= 1
			self.chat.sendMsg(nightactions.alive[id].get_name_group())
			self.game.log.info("The visionary sees "+ nightactions.alive[id].get_name_group())

# To do
	# Klasse mit einzelnem Werwolf erstellen, Ausnahme
	# Mehr Rollen definieren