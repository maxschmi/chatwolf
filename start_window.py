#-------------------#
#                   #
#    werewolf game  #
#     per skype     #
#     Max Schmit    #
#     march 2020    #
#                   #
#-------------------#

# librarys
from skpy import Skype, SkypeAuthException, SkypeGroupChat
import os
from Werewolf import *
#from getpass import getpass, getuser
from tkinter import *
from tkinter import messagebox, filedialog
from tkinter.ttk import Notebook, Frame

# command functions
#--------------------------------------------------
def login_skype():
	try:
		global sk
		sk = Skype(user.get(), pwd.get())
		login_succes()
	except SkypeAuthException:
		w_error("please try again, your login credentials weren't right!")

def login_skype_token():
	try:
		global sk
		sk = Skype(tokenFile = "temp/token.txt")
		login_succes()
	except SkypeAuthException:
		w_error("It didn\'t work to connect with your token! \nplease enter your login credentials!")

def start_game():
	if check_start():
		global game 
		#get variables

		game = Game(sk, chatid = get_chatid(), numwerewolfs = int(enumwerewolfs.get()), 
			  amor = amor.get(), witch = witch.get(), prostitute = prostitute.get(), visionary = visionary.get(), 
			  lang = lang_dic[sblang.get()], wait_mult = int(ewait_mult.get()))
		game.start()

# check functions
def check_enumwerewolfs():
	num = enumwerewolfs.get()
	try:
		num = int(num)
		if num >0:
			enumwerewolfs.config(bg = "#FFFFFF")
			return True
	except ValueError:
		enumwerewolfs.config(bg = "#F78181")
		return False

def check_lbchats():
	chat_sel = lbchats.curselection()
	if chat_sel == None:
		lbchats.config(bg = "#F78181")
		return False
	else:
		lbchats.config(bg = "#FFFFFF")
		return True

def check_sk():
	if "sk" in globals():
		return True
	else:
		return False

def check_elog_dir():
	if os.path.isdir(elog_dir.get()):
		elog_dir.config(bg = "#F78181")
		return True
	else:
		elog_dir.config(bg = "#FFFFFF")
		return False

def check_ebkp_dir():
	if os.path.isdir(ebkp_dir.get()):
		ebkp_dir.config(bg = "#F78181")
		return True
	else:
		ebkp_dir.config(bg = "#FFFFFF")
		return False

def check_ewait_mult():
	try:
		int(ewait_mult.get())
		ewait_mult.config(bg = "#F78181")
		return True
	except ValueError:
		ewait_mult.config(bg = "#FFFFFF")
		return False


def check_start():
	if not (check_enumwerewolfs() or check_sk() or check_ewait_mult() or check_lbchats() or check_elog_dir()):
		return False
	
	chatid = get_chatid()
	numroles = amor.get() + visionary.get() + witch.get() + prostitute.get() + int(enumwerewolfs.get())

	if numroles > (len(sk.chats[chatid].userIds)-1):
		w_error("You have choosen too many roles for the amount of players")
		return False

	return True


# other functions
def get_chatid():
	chat_sel = int(lbchats.curselection()[0])
	chat_key = lbchats.get(chat_sel)
	return dchats[chat_key]

def fill_chatid():
	# empty if already filled
	while not lbchats.get("end") == "":
		lbchats.delete("end")

	global dchats
	dchats = dict_chats()
	for chat in list(dchats.keys()):
		lbchats.insert("end", chat)

def dict_chats():
	dict = {}
	if "sk" in globals():
		rec = sk.chats.recent()
		for id in rec:
			if type(rec[id]) == SkypeGroupChat:
				dict.update({"chat = " + rec[id].topic + ", Users: " + " & ".join(rec[id].userIds): id})
		return dict
	else:
		return "you are not yet loged in to Skype!"

def list_chatid():
	list = []
	if "sk" in globals():
		rec = sk.chats.recent()
		for id in rec:
			if type(rec[id]) == SkypeGroupChat:
				list.append(id)
		return list
	else:
		return "you are not yet loged in to Skype!"

def login_succes():
	blogin.config(bg = "#40FF00")
	fill_chatid()
	first = sk.user.name.first
	first = first if first else ""
	last = sk.user.name.last
	last = last if last else ""
	name = first + " " + last
	lsk.config(text = ("You are loged in as " + name + " (" + sk.user.id + ")"))
	try:
		wlog.withdraw()
	except:
		pass

# Window definitions
# ------------------

#  zum login
def w_log():
	global wlog
	wlog = Toplevel()
	wlog.title("Skype-Werewolf - login")

	Label(wlog, text = "please log in to your Skype account").grid(row = 0, column = 0, columnspan = 2)
	#Label(wlog, text = " to your Skype account").grid(row = 0, column = 1)

	global user, pwd
	Label(wlog, text="username:").grid(row=1)
	user = Entry(wlog)
	user.grid(row = 1, column = 1)
	Label(wlog, text="password:").grid(row=2)
	pwd = Entry(wlog, show = "*")
	pwd.grid(row = 2, column = 1)

	Button(wlog, text = "login", command = login_skype).grid(row=3, column=0)
	Button(wlog, text = "try token", command = login_skype_token).grid(row=3, column=1)
	#Button(wlog, text='Quit', command=wlog.quit).grid(row=3, column=1)

	wlog.mainloop()

# error window
def w_error(msg):
	messagebox.showinfo(title  = "Skype-Werewolf - error", message = msg)

# game window
def root():
	global root
	root = Tk()
	root.iconphoto(True, PhotoImage(master = root, file = "data/icon.png"))
	root.title("Skype-Werewolf - game properties")
	tab_parent = Notebook(root)

	# main game settings
	tabgame = Frame(tab_parent)
	
	# skype login
	global blogin, lbchats, lsk
	global chatid, enumwerewolfs, bamor, bwitch, bprostitute, bvisionary
	blogin = Button(tabgame, text = "login Skype", bg = "#FF0040", command = w_log)
	blogin.grid(row = 0)
	lsk = Label(tabgame, text = "You are not loged in!")
	lsk.grid(row = 0, column = 1, columnspan = 4, sticky = "w")

	#select chat
	global lbchats
	Label(tabgame, text = "Select your chat:").grid(row = 1)

	frchats = Frame(tabgame, height = 800, width = 1000)
	frchats.grid(row = 1, column = 1, columnspan = 4, sticky = "nwse")
	lbchats = Listbox(frchats, selectmode = "single", height = 5, width = 100)
	lbchats_vsc = Scrollbar(lbchats, orient="vertical", command = lbchats.yview)
	lbchats_vsc.pack(side=RIGHT, fill=Y)
	lbchats_hsc = Scrollbar(lbchats, orient="horizontal", command = lbchats.xview)
	lbchats_hsc.pack(side = BOTTOM, fill = X)
	lbchats.config(yscrollcommand = lbchats_vsc.set, xscrollcommand = lbchats_hsc.set)
	lbchats.pack(side = LEFT, fill = BOTH, expand = 1)


	#roles
	global enumwerewolfs, bamor, bwitch, bprostitute, bvisionary, amor, witch, prostitute, visionary
	Label(tabgame, text="number of werewolfs").grid(row=2)
	enumwerewolfs = Entry(tabgame, validate= "focusout", validatecommand= check_enumwerewolfs)
	enumwerewolfs.grid(row=2, column=1, sticky = "w")

	Label(tabgame, text = "select your roles:").grid(row = 3, column = 0, columnspan = 2, sticky = "w")
	amor = BooleanVar()
	bamor = Checkbutton(tabgame, text="amor", variable = amor)
	bamor.grid(row=4, column = 0, sticky = "e")

	witch = BooleanVar()
	bwitch = Checkbutton(tabgame, text = "witch", variable = witch)
	bwitch.grid(row=5, column = 0, sticky = "e")

	visionary = BooleanVar()
	bvisionary = Checkbutton(tabgame, text="visionary", variable = visionary)
	bvisionary.grid(row=6, column = 0, sticky = "e")

	prostitute = BooleanVar()
	bprostitute = Checkbutton(tabgame, text="prostitute", variable = prostitute)
	bprostitute.grid(row=7, column = 0, sticky = "e")
	
	#start button
	Button(tabgame, text = "start the game", command = start_game).grid(row = 8, column = 1)

	#other settings tab
	global sblang, ewait_mult, elog_dir, lang_dic, ebkp_dir
	tabother = Frame(tab_parent)
	tabother.pack()
	Label(tabother, text = "other settings:").grid(row = 0, columnspan = 2)

	lang_dic = {"English": "en", "Deutsch": "de"}
	Label(tabother, text="language: ").grid(row=1, column = 0)
	sblang = Spinbox(tabother, values = tuple(lang_dic.keys()))
	sblang.grid(row=1, column = 1, sticky = "w")

	Label(tabother, text="waiting multiplier: ").grid(row=2, column = 0, sticky = "w")
	ewait_mult = Entry(tabother, validate= "focusout", validatecommand= check_ewait_mult)
	ewait_mult.insert(0, "1")
	ewait_mult.grid(row=2, column = 1, sticky = "e")

	Label(tabother, text="directory for logging file: ").grid(row=3, column = 0)
	log_dir = os.getcwd() + "\\logs"
	elog_dir = Entry(tabother, validate= "focusout", validatecommand= check_elog_dir)
	elog_dir.insert(0, log_dir)
	elog_dir.grid(row = 3, column = 1, columnspan = 4)

	Label(tabother, text="directory for backup file: ").grid(row=4, column = 0)
	bkp_dir = os.getcwd() + "\\bkp"
	ebkp_dir = Entry(tabother, validate= "focusout", validatecommand= check_ebkp_dir)
	ebkp_dir.insert(0, bkp_dir)
	ebkp_dir.grid(row = 4, column = 1, columnspan = 4)


	#initialise window
	tab_parent.add(tabgame, text = "main")
	tab_parent.add(tabother, text ="expert")
	tab_parent.pack(expand=1, fill='both')
	root.mainloop()

root()

# popup if the game is running
# possibility to load a backup file