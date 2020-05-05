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
        super().__init__()
        self.iconphoto(True, PhotoImage(master = self, file = "data/icon.png"))
        self.title("Skype-Werewolf - game properties")
        self.tab_parent = Notebook(self)

        # main game settings
        self.tabgame = Frame(self.tab_parent)
    
        # skype login
        self.b_login = Button(self.tabgame, text = "login Skype", 
                              bg = "#FF0040", command = self.click_b_login)
        self.b_login.grid(row = 0)
        self.l_sk = Label(self.tabgame, text = "You are not loged in!")
        self.l_sk.grid(row = 0, column = 1, columnspan = 4, sticky = "w")

        #select chat
        Label(self.tabgame, text = "Select your groupchat:").grid(row = 1)

        Label(self.tabgame, text = " "*100).grid(row = 2, column = 3) # to expand the lb_chats
        self.fr_chats = Frame(self.tabgame, height = 800, width = 1000)
        self.lb_chats = Listbox(self.fr_chats, selectmode = "single", 
                                height = 5, width = 100)
        lb_chats_vsc = Scrollbar(self.lb_chats, orient="vertical", 
                                 command = self.lb_chats.yview)
        lb_chats_vsc.pack(side=RIGHT, fill=Y)
        lb_chats_hsc = Scrollbar(self.lb_chats, orient="horizontal", 
                                 command = self.lb_chats.xview)
        lb_chats_hsc.pack(side = BOTTOM, fill = X)
        self.lb_chats.config(yscrollcommand = lb_chats_vsc.set, 
                             xscrollcommand = lb_chats_hsc.set)
        self.lb_chats.pack(side = LEFT, fill = BOTH, expand = 1)
        self.fr_chats.grid(row = 1, column = 1, columnspan = 5, sticky = "nwse")

        #roles
        Label(self.tabgame, text="number of werewolfs").grid(row=2)
        self.e_numwerewolfs = Entry(self.tabgame, validate= "focusout", 
                                    validatecommand= self.check_e_numwerewolfs)
        self.e_numwerewolfs.grid(row=2, column=1, sticky = "w")

        Label(self.tabgame, text = "select your roles:").grid(row = 3, column = 0, columnspan = 2, sticky = "w")

        self.amor = BooleanVar()
        self.b_amor = Checkbutton(self.tabgame, 
                                  text="amor", 
                                  variable = self.amor)
        self.b_amor.grid(row=4, column = 0, sticky = "w")

        self.witch = BooleanVar()
        self.b_witch = Checkbutton(self.tabgame, 
                                   text = "witch", 
                                   variable = self.witch)
        self.b_witch.grid(row=5, column = 0, sticky = "w")

        self.visionary = BooleanVar()
        self.b_visionary = Checkbutton(self.tabgame, 
                                       text="visionary", 
                                       variable = self.visionary)
        self.b_visionary.grid(row=6, column = 0, sticky = "w")

        self.prostitute = BooleanVar()
        self.b_prostitute = Checkbutton(self.tabgame, 
                                        text="prostitute", 
                                        variable = self.prostitute)
        self.b_prostitute.grid(row=7, column = 0, sticky = "w")
    
        #start button
        self.b_start = Button(self.tabgame, text = "start the game", 
                              command = self.start_game)
        self.b_start.grid(row = 8, column = 1)

        # other settings tab
        #-------------------
        self.tabexpert = Frame(self.tab_parent)
        self.tabexpert.pack()
        Label(self.tabexpert, text = "other settings:").grid(row = 0, columnspan = 2)

        #Language
        self.lang_dic = {"English": "en", "Deutsch": "de"}
        Label(self.tabexpert, text="language: ").grid(row=1, column = 0)
        self.sb_lang= Spinbox(self.tabexpert, values = tuple(self.lang_dic.keys()))
        self.sb_lang.grid(row=1, column = 1, sticky = "w")

        #waiting multiplier
        Label(self.tabexpert, text="waiting multiplier: ").grid(row=2, column = 0, sticky = "w")
        self.e_wait_mult = Entry(self.tabexpert, validate= "focusout", 
                                 validatecommand= self.check_e_wait_mult)
        self.e_wait_mult.insert(0, "1")
        self.e_wait_mult.grid(row=2, column = 1, sticky = "e")

        #directory for the logging file
        Label(self.tabexpert, text="directory for logging file: ").grid(row=3, column = 0)
        self.log_dir = os.getcwd() + "\\logs"
        self.e_log_dir = Entry(self.tabexpert, validate= "focusout", 
                               validatecommand= self.check_e_log_dir, width = 60)
        self.e_log_dir.insert(0, self.log_dir)
        self.e_log_dir.grid(row = 3, column = 1, columnspan = 4)
        self.b_get_log_dir = Button(self.tabexpert, text = "get directory", 
                                    command = lambda: self.get_dir(self.e_log_dir))
        self.b_get_log_dir.grid(row=3, column = 5)

        #directory for backup file:
        Label(self.tabexpert, text="directory for backup file: ").grid(row=4, column = 0)
        self.bkp_dir = os.getcwd() + "\\bkp"
        self.e_bkp_dir = Entry(self.tabexpert, validate= "focusout", validatecommand= self.check_e_bkp_dir, width = 60)
        self.e_bkp_dir.insert(0, self.bkp_dir)
        self.e_bkp_dir.grid(row = 4, column = 1, columnspan = 4)
        self.b_get_bkp_dir = Button(self.tabexpert, text = "get directory", command = lambda: self.get_dir(self.e_bkp_dir))
        self.b_get_bkp_dir.grid(row=4, column = 5)

        #Debug logging file yes/no
        self.do_debug = BooleanVar()
        self.do_debug.set(True)
        self.cb_do_debug = Checkbutton(self.tabexpert, text = "write a debug logging file", variable = self.do_debug)
        self.cb_do_debug.grid(row = 5, column = 0, columnspan = 2)

        #restart from Backup
        self.b_restart_bkp = Button(self.tabexpert, text = "restart from Backup", 
                                    command = self.click_b_bkp)
        self.b_restart_bkp.grid(row = 7, column = 1)

        #About page
        #----------
        self.tababout = Frame(self.tab_parent)
        #initialise tabs
        self.tab_parent.add(self.tabgame, text = "main")
        self.tab_parent.add(self.tabexpert, text ="expert")
        self.tab_parent.pack(expand=1, fill='both')

    def click_b_login(self):
        self.w_log = TlLog(self)
        self.w_log.grab_set()

    def click_b_bkp(self):
        self.w_bkp = TlBkp(self)
        self.w_bkp.grab_set()

    def start_game(self):
        if self.check_start():
            self.game = Game(sk = self.sk, chatid = self.get_chatid(), 
                            numwerewolfs = int(self.e_numwerewolfs.get()), 
                            amor = self.amor.get(), 
                            witch = self.witch.get(), 
                            prostitute = self.prostitute.get(), 
                            visionary = self.visionary.get(), 
                            lang = self.lang_dic[self.sb_lang.get()], 
                            wait_mult = int(self.e_wait_mult.get()),
                            log_dir = self.e_log_dir.get(), 
                            bkp_dir = self.e_bkp_dir.get(), 
                            do_debug = self.do_debug.get())

            self.start_w_run()
            if hasattr(self, "wbkp"): 
                self.wbkp.destroy()

            try:
                self.game.start()
            except:
                self.w_error("There was an error, please load the backup and restart." +
                             "\nTo get more information about the error, please read the documentations!")

            self.wrun.destroy()

    def get_dir(self, entry_widget):
        dir = filedialog.askdirectory()
        if os.path.isdir(dir):
            entry_widget.delete(0, END)
            entry_widget.insert(0, dir)


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

    def check_e_log_dir(self):
        if os.path.isdir(self.e_log_dir.get()):
            self.e_log_dir.config(bg = "#FFFFFF")
            return True
        else:
            self.e_log_dir.config(bg = "#F78181")
            return False

    def check_e_bkp_dir(self):
        if os.path.isdir(self.e_bkp_dir.get()):
            self.e_bkp_dir.config(bg = "#FFFFFF")
            return True
        else:
            self.e_bkp_dir.config(bg = "#F78181")
            return False

    def check_e_wait_mult(self):
        try:
            int(self.e_wait_mult.get())
            self.e_wait_mult.config(bg = "#FFFFFF")
            return True
        except ValueError:
            self.e_wait_mult.config(bg = "#F78181")
            return False


    def check_start(self):
        if (self.check_e_numwerewolfs() + self.check_sk() + 
            self.check_e_wait_mult() + self.check_lb_chats() + 
            self.check_e_log_dir() + self.check_e_bkp_dir()) < 6:
            return False
        
        #check if there are not to many roles selected for the selected chat
        chatid = self.get_chatid()
        numroles = (self.amor.get() + self.visionary.get() + self.witch.get() + 
                    self.prostitute.get() + int(self.e_numwerewolfs.get()))

        if numroles > (len(self.sk.chats[chatid].userIds)-1):
            self.w_error("You have choosen too many roles for the amount of players")
            return False

        return True

    def login_succes(self):
        self.b_login.config(bg = "#40FF00")
        self.fill_chatid()
        first = self.sk.user.name.first
        first = first if first else ""
        last = self.sk.user.name.last
        last = last if last else ""
        name = first + " " + last
        self.l_sk.config(text = ("You are loged in as " + name + " (" + self.sk.user.id + ")"))
        try:
            self.w_log.destroy()
        except:
            pass

    # other functions
    def get_chatid(self):
        chat_sel = int(self.lb_chats.curselection()[0])
        chat_key = self.lb_chats.get(chat_sel)
        return self.d_chats[chat_key]

    def fill_chatid(self):
        # empty if already filled
        while not self.lb_chats.get("end") == "":
            self.lb_chats.delete("end")

        self.d_chats = self.dict_chats()
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

    def start_w_run(self):
        self.w_run = Toplevel(self)
        self.w_run.title("Skype-Werewolf - the game is on")
        self.w_run.grab_set()
        Label(self.w_run, text = "the game is now running, so go to Skype and play." +
              "\n!!!!Leave this window open!!!!").pack()
    
    @staticmethod
    def w_error(msg):
        messagebox.showinfo(title  = "Skype-Werewolf - error", message = msg)

# Window definitions
# ------------------

#  zum login
class TlLog(Toplevel):
    def __init__(self, root):
        super().__init__(root)
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
        super().__init__(root) 
        self.root = root
        self.title("Skype-Werewolf - restart from backup")
        self.grab_set()

        # login to Skype
        self.b_login = Button(self, text = "login Skype", 
                              bg = "#FF0040", command = self.click_b_login)
        self.b_login.grid(row = 0)
        self.l_sk = Label(self, text = "You are not loged in!")
        self.l_sk.grid(row = 0, column = 1, columnspan = 4, sticky = "w")
        self.check_login()

        # get the bkp file
        Label(self, text = "").grid(row = 0)
        Label(self, text = "select the Backup file to reload from").grid(row = 1)
        self.e_bkp_file = Entry(self, validate = "focusout", 
                        validatecommand = self.check_e_bkp_file, width = 60)
        self.e_bkp_file.grid(row = 1, column = 1, columnspan = 4)
        Button(self, text = "get file", 
            command = self.get_bkp_file).grid(row = 1, column = 6)

        Button(self, text = "restart from Backup", 
               command = self.restart_bkp).grid(row = 3, column = 1)

    def restart_bkp(self):
        if not self.check_e_bkp_file():
            file = self.e_bkp_file.get()
            try:
                self.game = Game.load_bkp(file)
                self.game.sk = self.root.sk
                self.game.continue_bkp()
            except:
                self.root.w_error("Something went wrong, \n" + 
                                "please check if you are loged in to Skype in the main window")

    def check_e_bkp_file(self):
        bkp_file = self.e_bkp_file.get()

        if bkp_file[-4:-1]==".dat":
            self.e_bkp_file.delete(len(bkp_file)-4, END)
        else:
            bkp_file += ".dat"

        if os.path.isfile(bkp_file):
            self.e_bkp_file.config(bg = "#FFFFFF")
            return True
        else:
            self.e_bkp_file.config(bg = "#F78181")
            return False

    def get_bkp_file(self):
        file = filedialog.askopenfilename(filetypes = (("Backup file", "*.dat"),))
        if os.path.isfile(file):
            file = file[0:-4] # delete ending
            self.e_bkp_file.delete(0, END)
            self.e_bkp_file.insert(0, file)

    def click_b_login(self):
        self.w_log = TlLog(self)
        self.w_log.grab_set()

    def check_login(self):
        if hasattr(self.root, "sk"):
            if self.root.sk.conn.connected:
                self.sk = self.root.sk
                self.login_succes()
                return True
            else:
                return False

    def login_succes(self):
        #give sk to root
        self.root.sk = self.sk
        self.root.login_succes()

        #set login succes for self
        self.b_login.config(bg = "#40FF00")
        first = self.root.sk.user.name.first
        first = first if first else ""
        last = self.root.sk.user.name.last
        last = last if last else ""
        name = first + " " + last
        self.l_sk.config(text = ("You are loged in as " + name + 
                                 " (" + self.root.sk.user.id + ")"))

        try:
            self.w_log.destroy()
        except:
            pass

#root = GUI()
#root.mainloop()