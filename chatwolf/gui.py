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
#                               GUI                                     #
#                                                                       #
#-----------------------------------------------------------------------#

# own libraries
from .game import Game

# other libraries
from skpy import Skype, SkypeAuthException, SkypeGroupChat
import os
from tkinter import *
from tkinter import messagebox, filedialog
from tkinter.ttk import Notebook, Frame

# class definitions
#------------------

class GUI(Tk):
    def __init__(self):
        super.__init__(self)
        self.iconphoto(True, PhotoImage(master = self, file = "data/icon.png"))
        self.title("Skype-Werewolf - game properties")
        self.tab_parent = Notebook(self)

        # main game settings
        self.tabgame = Frame(self.tab_parent)
    
        # skype login
        self.blogin = Button(self.tabgame, text = "login Skype", bg = "#FF0040", 
                            command = self.click_b_login)
        self.blogin.grid(row = 0)
        self.lsk = Label(self.tabgame, text = "You are not loged in!")
        self.lsk.grid(row = 0, column = 1, columnspan = 4, sticky = "w")

        #select chat
        Label(self.tabgame, text = "Select your chat:").grid(row = 1)

        Label(self.tabgame, text = " "*100).grid(row = 2, column = 3) # to expand the lb_chats
        self.frchats = Frame(self.tabgame, height = 800, width = 1000)
        self.lb_chats = Listbox(self.frchats, selectmode = "single", height = 5, width = 100)
        lb_chats_vsc = Scrollbar(self.lb_chats, orient="vertical", command = self.lb_chats.yview)
        lb_chats_vsc.pack(side=RIGHT, fill=Y)
        lb_chats_hsc = Scrollbar(self.lb_chats, orient="horizontal", command = self.lb_chats.xview)
        lb_chats_hsc.pack(side = BOTTOM, fill = X)
        self.lb_chats.config(yscrollcommand = lb_chats_vsc.set, xscrollcommand = lb_chats_hsc.set)
        self.lb_chats.pack(side = LEFT, fill = BOTH, expand = 1)
        self.frchats.grid(row = 1, column = 1, columnspan = 5, sticky = "nwse")

        #roles
        Label(self.tabgame, text="number of werewolfs").grid(row=2)
        self.e_numwerewolfs = Entry(self.tabgame, validate= "focusout", validatecommand= self.check_e_numwerewolfs)
        self.e_numwerewolfs.grid(row=2, column=1, sticky = "w")

        Label(self.tabgame, text = "select your roles:").grid(row = 3, column = 0, columnspan = 2, sticky = "w")
        self.amor = BooleanVar()
        self.bamor = Checkbutton(self.tabgame, text="amor", variable = self.amor)
        self.bamor.grid(row=4, column = 0, sticky = "w")

        self.witch = BooleanVar()
        self.bwitch = Checkbutton(self.tabgame, text = "witch", variable = self.witch)
        self.bwitch.grid(row=5, column = 0, sticky = "w")

        self.visionary = BooleanVar()
        self.bvisionary = Checkbutton(self.tabgame, text="visionary", variable = self.visionary)
        self.bvisionary.grid(row=6, column = 0, sticky = "w")

        self.prostitute = BooleanVar()
        self.bprostitute = Checkbutton(self.tabgame, text="prostitute", variable = self.prostitute)
        self.bprostitute.grid(row=7, column = 0, sticky = "w")
    
        #start button
        self.bstart = Button(self.tabgame, text = "start the game", command = self.start_game).grid(row = 8, column = 1)

        # other settings tab
        #-------------------
        self.tabexpert = Frame(tab_parent)
        self.tabexpert.pack()
        Label(self.tabexpert, text = "other settings:").grid(row = 0, columnspan = 2)

        #Language
        self.lang_dic = {"English": "en", "Deutsch": "de"}
        Label(self.tabexpert, text="language: ").grid(row=1, column = 0)
        self.sblang = Spinbox(self.tabexpert, values = tuple(self.lang_dic.keys()))
        self.sblang.grid(row=1, column = 1, sticky = "w")

        #waiting multiplier
        Label(self.tabexpert, text="waiting multiplier: ").grid(row=2, column = 0, sticky = "w")
        self.ewait_mult = Entry(self.tabexpert, validate= "focusout", validatecommand= self.check_ewait_mult)
        self.ewait_mult.insert(0, "1")
        self.ewait_mult.grid(row=2, column = 1, sticky = "e")

        #directory for the logging file
        Label(self.tabexpert, text="directory for logging file: ").grid(row=3, column = 0)
        self.log_dir = os.getcwd() + "\\logs"
        self.elog_dir = Entry(self.tabexpert, validate= "focusout", validatecommand= self.check_elog_dir, width = 60)
        self.elog_dir.insert(0, log_dir)
        self.elog_dir.grid(row = 3, column = 1, columnspan = 4)
        self.b_get_log_dir = Button(self.tabexpert, text = "get directory", command = lambda: get_dir(self.elog_dir))
        self.b_get_log_dir.grid(row=3, column = 5)

        #directory for backup file:
        Label(self.tabexpert, text="directory for backup file: ").grid(row=4, column = 0)
        self.bkp_dir = os.getcwd() + "\\bkp"
        self.ebkp_dir = Entry(self.tabexpert, validate= "focusout", validatecommand= self.check_ebkp_dir, width = 60)
        self.ebkp_dir.insert(0, bkp_dir)
        self.ebkp_dir.grid(row = 4, column = 1, columnspan = 4)
        self.b_get_bkp_dir = Button(self.tabexpert, text = "get directory", command = lambda: get_dir(self.ebkp_dir))
        self.b_get_bkp_dir.grid(row=4, column = 5)

        #Debug logging file yes/no
        self.do_debug = BooleanVar()
        self.do_debug.set(True)
        self.cb_do_debug = Checkbutton(self.tabexpert, text = "write a debug logging file", variable = self.do_debug)
        self.cb_do_debug.grid(row = 5, column = 0, columnspan = 2)

        #restart from Backup
        self.b_restart_bkp = Button(self.tabexpert, text = "restart from Backup", command = self.w_bkp)
        self.b_restart_bkp.grid(row = 7, column = 1)

        #initialise tabs
        self.tab_parent.add(self.tabgame, text = "main")
        self.tab_parent.add(self.tabexpert, text ="expert")
        self.tab_parent.pack(expand=1, fill='both')

        #initialise other variables
        self.sk = None

    def click_b_login(self):
        self.wlog = TlLog(self)

    def start_game(self):
        if self.check_start():
            self.game = Game(sk = self.sk, chatid = self.get_chatid(), 
                            numwerewolfs = int(self.e_numwerewolfs.get()), 
                            amor = self.amor.get(), 
                            witch = self.witch.get(), 
                            prostitute = self.prostitute.get(), 
                            visionary = self.visionary.get(), 
                            lang = self.lang_dic[self.sblang.get()], 
                            wait_mult = int(self.ewait_mult.get()),
                            log_dir = self.elog_dir.get(), 
                            bkp_dir = self.ebkp_dir.get(), 
                            do_debug = self.do_debug.get())

            self.w_run()
            if hasattr(self, "wbkp"): self.wbkp.withdraw()

            try:
                self.game.start()
            except:
                self.w_error("There was an error, please load the backup and restart." +
                             "\nTo get more information about the error, please read the")

            self.wrun.withdraw()

    def get_dir(entry_widget):
        dir = filedialog.askdirectory()
        if os.path.isdir(dir):
            entry_widget.delete(0, END)
            entry_widget.insert(0, dir)

    def get_bkp_file(self):
        file = filedialog.askopenfilename(filetypes = (("Backup file", "*.dat"),))
        if os.path.isfile(file):
            file = file[0:-4] # delete ending
            self.ebkp_file.delete(0, END)
            self.ebkp_file.insert(0, file)


    # check functions
    #----------------
    def check_e_numwerewolfs(self):
        num = self.e_numwerewolfs.get()
        try:
            num = int(num)
            if num >0:
                self.e_numwerewolfs.config(bg = "#FFFFFF")
                return True
            else:
                raise ValueError
        except ValueError:
            self.e_numwerewolfs.config(bg = "#F78181")
            return False

    def check_lb_chats(self):
        chat_sel = self.lb_chats.curselection()
        if len(chat_sel)==0:
            self.lb_chats.config(bg = "#F78181")
            return False
        else:
            self.lb_chats.config(bg = "#FFFFFF")
            return True

    def check_sk(self):
        if hasattr(self, "sk"):
            return True
        else:
            return False

    def check_elog_dir(self):
        if os.path.isdir(self.elog_dir.get()):
            self.elog_dir.config(bg = "#FFFFFF")
            return True
        else:
            self.elog_dir.config(bg = "#F78181")
            return False

    def check_ebkp_dir(self):
        if os.path.isdir(self.ebkp_dir.get()):
            self.ebkp_dir.config(bg = "#FFFFFF")
            return True
        else:
            self.ebkp_dir.config(bg = "#F78181")
            return False

    def chack_ebkp_file(self):
        if os.path.isfile(self.ebkp_file.get()):
            self.ebkp_file.config(bg = "#FFFFFF")
            return True
        else:
            self.ebkp_file.config(bg = "#F78181")
            return False

    def check_ewait_mult(self):
        try:
            int(self.ewait_mult.get())
            self.ewait_mult.config(bg = "#FFFFFF")
            return True
        except ValueError:
            self.ewait_mult.config(bg = "#F78181")
            return False


    def check_start(self):
        if (self.check_e_numwerewolfs() + self.check_sk() + 
            self.check_ewait_mult() + self.check_lb_chats() + 
            self.check_elog_dir() + self.check_ebkp_dir()) < 6:
            return False
        
        #check if there are not to many roles selected for the selected chat
        chatid = self.get_chatid()
        numroles = (self.amor.get() + self.visionary.get() + self.witch.get() + 
                    self.prostitute.get() + int(self.e_numwerewolfs.get()))

        if numroles > (len(self.sk.chats[chatid].userIds)-1):
            self.w_error("You have choosen too many roles for the amount of players")
            return False

        return True


    # other functions
    def get_chatid(self):
        chat_sel = int(self.lb_chats.curselection()[0])
        chat_key = self.lb_chats.get(chat_sel)
        return self.d_chats[chat_key]

    def fill_chatid(self):
        # empty if already filled
        while not self.lb_chats.get("end") == "":
            self.lb_chats.delete("end")

        self.d_chats = dict_chats()
        for chat in list(self.d_chats.keys()):
            self.lb_chats.insert("end", chat)

    def dict_chats(self):
        dict = {}
        if hasattr(self, "sk"):
            rec = self.sk.chats.recent()
            for id in rec:
                if type(rec[id]) == SkypeGroupChat:
                    dict.update({"chat = " + rec[id].topic + 
                                ", Users: " + " & ".join(rec[id].userIds): id})
            return dict
        else:
            return "you are not yet loged in to Skype!"

    def list_chatid(self):
        list = []
        if hasattr(self, "sk"):
            rec = self.sk.chats.recent()
            for id in rec:
                if type(rec[id]) == SkypeGroupChat:
                    list.append(id)
            return list
        else:
            return "you are not yet loged in to Skype!"

    def w_run():
        self.wrun = Toplevel(self)
        self.wrun.title("Skype-Werewolf - the game is on")
        self.wrun.grab_set()
        Label(self.wrun, text = "the game is now running, so go to skype and play." +
              "\n!!!!Leave this window open!!!!").pack()
    
    @staticmethod
    def w_error(msg):
        messagebox.showinfo(title  = "Skype-Werewolf - error", message = msg)

# Window definitions
# ------------------

#  zum login
class TlLog(Toplevel):
    def __init__(self, root):
        super.__init__(self, root)
        self.title("Skype-Werewolf - login")
        self.grab_set()
        self.root = root

        Label(self, text = "\nplease log in to the Skype account" +
              "\n of the game-master").grid(row = 0, column = 0, columnspan = 2)
        
        Label(self, text="username:").grid(row=1)
        self.user = Entry(self)
        self.user.grid(row = 1, column = 1)
        Label(self, text="password:").grid(row=2)
        self.pwd = Entry(self, show = "*")
        self.pwd.grid(row = 2, column = 1)

        Button(self, text = "login", command = self.login_skype).grid(row=3, column=0)
        Button(self, text = "try token", command = self.login_skype_token).grid(row=3, column=1)

    def login_skype(self):
        try:
            self.root.sk = Skype(self.user.get(), self.pwd.get())
            if self.root.sk.conn.connected:
                self.root.login_succes()
            else:
                raise Exception("you are not connected")
        except:
            GUI.w_error("please try again, your login credentials weren't right!")

    def login_skype_token(self):
        try:
            self.root.sk = Skype(tokenFile = "temp/token.txt")
            if self.root.sk.conn.connected:
                self.root.login_succes()
            else:
                raise Exception("you are not connected")
        except:
            GUI.w_error("It didn\'t work to connect with your token!" + 
                        "\nplease enter your login credentials!")

# start from Backup window
class TlBkp(Toplevel):
    def __init__(self, root):
        super.__init__(self, root) 
        self.root = root
        self.wbkp.title("Skype-Werewolf - restart from backup")
        self.grab_set()

        Label(self, text = "").grid(row = 0)
        Label(self, text = "select the Backup file to reload from").grid(row = 1)
        self.ebkp_file = Entry(self, validate = "focusout", 
                        validatecommand = root.check_ebkp_dir, width = 60)
        self.ebkp_file.grid(row = 1, column = 1, columnspan = 4)
        Button(self, text = "get file", 
            command = root.get_bkp_file).grid(row = 1, column = 6)

        Button(self, text = "restart from Backup", 
               command = self.restart_bkp).grid(row = 3, column = 1)

    def restart_bkp(self):
        if not self.check_ebkp_file():
            file = self.ebkp_file.get()
            self.game = Game.load_bkp(file)
            self.game.continue_bkp()



