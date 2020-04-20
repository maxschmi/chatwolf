#-------------------#
#                   #
#    werewolf game  #
#     per skype     #
#     Max Schmit    #
#     march 2020    #
#                   #
#-------------------#

# librarys
from skpy import Skype, SkypeAuthException
from Werewolf import *
#from getpass import getpass, getuser
from tkinter import *

# Command Functions
def loginSkype():
	try:
		global sk
		sk = Skype(user.get(), pwd.get())
	except SkypeAuthException:
		werror("please try again, your login credentials weren't right!")

def startGame():
	global game = Game(sk, chatid, numwerewolfs = 1, amor = True, witch = False, prostitute = False, visionary = False, lang = "en", wait_mult = 1))
# Fenster
# ----------

#  zum login
def wlog():
	wlog = Tk()
	wlog.title("Skype-Werewolf - login")
	wlog.iconphoto(False, PhotoImage(file = "data/icon.png"))
	Label(wlog, text = "please log in").grid(row = 0, column = 0)
	Label(wlog, text = " to your Skype account").grid(row = 0, column = 1)

	Label(wlog, text="username:").grid(row=1)
	global user
	user = Entry(wlog)
	user.grid(row = 1, column = 1)
	Label(wlog, text="password:").grid(row=2)
	global pwd
	pwd = Entry(wlog, show = "*")
	pwd.grid(row = 2, column = 1)

	Button(wlog, text = "login", command = loginSkype).grid(row=3, column=0)
	#Button(wlog, text='Quit', command=wlog.quit).grid(row=3, column=1)

	wlog.mainloop()

# error window
def werror(msg):
	werror = Tk()
	werror.title("Skype-Werewolf - error")
	Label(werror, text = msg).pack()

# game window
def wgame():
	wgame = Tk()
	wgame.title("Skype-Werewolf - game properties")
