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
#                            test framework                             #
#                                                                       #
#-----------------------------------------------------------------------#
#
## libraries
import logging
import unittest
import datetime
from unittest.mock import patch
from os import mkdir
from shutil import rmtree
from os.path import isdir

#chatwolf libraries
from test.skpy_mocks import (Skype, SkypeEventLoop, SkypeUser, SkypeContacts, 
                             SkypeNewMessageEvent, Data, sleep, super_skypeeventloop)
import chatwolf

# logger
log_dir="./test/test_log/" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "/"
if not isdir("./test/test_log/"): mkdir("./test/test_log/")
mkdir(log_dir)
log_filepath = log_dir + "testlog.txt"
log = logging.getLogger("Test")
log.setLevel(logging.DEBUG)
logfh = logging.FileHandler(log_filepath)
log.addHandler(logfh)

log_game = logging.getLogger("Werewolf")
log_game.addHandler(logfh)

#Test Class
class ChatwolfTest(unittest.TestCase):
    def setUp(self):
        self.patcher = []
        self.patcher.append(patch('chatwolf.game.SkypeUser', SkypeUser))
        self.patcher.append(patch('chatwolf.game.SkypeContacts', SkypeContacts))
        self.patcher.append(patch('chatwolf.game.sleep', sleep))
        self.patcher.append(patch('chatwolf.player.SkypeUser', SkypeUser))
        self.patcher.append(patch('chatwolf.roles.sleep', sleep))
        self.patcher.append(patch('chatwolf.skypecommands.SkypeEventLoop', SkypeEventLoop))
        self.patcher.append(patch('chatwolf.skypecommands.SkypeNewMessageEvent', SkypeNewMessageEvent))
        self.patcher.append(patch('chatwolf.skypecommands.sleep', sleep))
        self.patcher.append(patch('chatwolf.skypecommands.SkypeCommands.getEvents', SkypeEventLoop.getEvents))
        self.patcher.append(patch('chatwolf.skypecommands.super', super_skypeeventloop))

        for patcher in self.patcher:
            self.addCleanup(patcher.stop)
            patcher.start()

        self.sk = Skype()

    def test_game_easy(self):
        log.info("#"*40 + " test_game_easy starts " + "#"*40)
        game = chatwolf.Game(sk = self.sk, chatid = Data.chatid,
                             num_werewolfs= 1, num_amor = 1,
                             num_witch = 1, num_prostitute = 1,
                             num_visionary = 1, 
                             lang = "en", wait_mult = 0, 
                             log_dir = log_dir, do_debug = True,
                             bkp_dir = log_dir,
                             do_save_conf = False)
        game.start()
        self.assertTrue(game.is_end)

        #do more runs
        for i in range(5):
            game.restart()
            self.assertTrue(game.is_end)

    def test_game_complex(self):
        log.info("#"*40 + " test_game_complex starts " + "#"*40)
        game = chatwolf.Game(sk = self.sk, chatid = Data.chatid,
                        num_werewolfs= 2, num_amor = 2,
                        num_witch = 2, num_prostitute = 2,
                        num_visionary = 2, 
                        lang = "en", wait_mult = 0, 
                        log_dir = log_dir, do_debug = True,
                        bkp_dir = log_dir,
                        do_save_conf = False)
        game.start()
        self.assertTrue(game.is_end)

        #do more runs
        for i in range(5):
            game.restart()
            self.assertTrue(game.is_end)

    def test_roles(self):
        log.info("#"*40 + " test_roles starts " + "#"*40)
        game = chatwolf.Game(sk = self.sk, chatid = Data.chatid,
                             num_werewolfs= 1, num_amor = 1,
                             num_witch = 1, num_prostitute = 1,
                             num_visionary = 1, 
                             lang = "en", wait_mult = 0, 
                             log_dir = log_dir, do_debug = True,
                             bkp_dir = log_dir,
                             do_save_conf = False)
        game.dist_roles()
        na = chatwolf.Nightactions(game.get_alive(), game)
        log.info("#"*20 + " test prostitute" + "#"*20)
        prostitute = chatwolf.Prostitute(game.players[0], game)
        prostitute.greeting()
        prostitute.night(na)

        log.info("#"*20 + " test amor" + "#"*20)
        amor = chatwolf.Amor(game.players[0], game)
        amor.greeting()
        amor.night(na)

        log.info("#"*20 + " test witch" + "#"*20)
        witch = chatwolf.Witch(game.players[0], game)
        witch.greeting()
        witch.night(na)

        log.info("#"*20 + " test visionary" + "#"*20)
        visionary = chatwolf.Visionary(game.players[0], game)
        visionary.greeting()
        visionary.night(na)


if __name__ == '__main__':
    unittest.main()


