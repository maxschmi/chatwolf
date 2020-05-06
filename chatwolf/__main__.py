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

#-----------------------------------------------------------------------#
#                                                                       #
#                         main Game classes                             #
#                                                                       #
#-----------------------------------------------------------------------#


#libraries
import json
import os

#iport config
conf_json = open("chatwolf\\data\\conf.json", "w")
conf = json.load(conf_json)

# create directories if not yet done
if not conf["is_dir_created"]:
    dir_main = os.getenv('LOCALAPPDATA') + "\\chatwolf\\"
    log_dir = dir_main + "\\logs"
    bkp_dir = dir_main + "\\bkp"
    if not os.path.isdir(dir_main): os.mkdir(dir_main)
    if not os.path.isdir(log_dir): os.mkdir(log_dir)
    if not os.path.isdir(bkp_dir): os.mkdir(bkp_dir)
    conf["main_dir"] = main_dir
    conf["log_dir"] = log_dir
    conf["bkp_dir"] = bkp_dir
    conf["is_dir_"] = True
    json.dump(conf, conf_json)

conf_json.close()

# delete old logs and backups
for file in os.listdir(conf["log_dir"]):
    os.path.getatime(conf["log_dir"] + "\\" + file)