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
import time

#import config
try:
    conf_json = open("chatwolf\\data\\conf.json", "r")
except:
    conf_json = open("chatwolf\\data\\conf_root.json", "r")

conf = json.load(conf_json)
conf_json.close()

# create directories if not yet done
if not conf["is_dir_created"]:
    main_dir = os.getenv('LOCALAPPDATA') + "\\chatwolf\\"
    log_dir = main_dir + "\\logs"
    bkp_dir = main_dir + "\\bkp"
    temp_dir = main_dir + "\\temp"
    if not os.path.isdir(main_dir): os.mkdir(main_dir)
    if not os.path.isdir(log_dir): os.mkdir(log_dir)
    if not os.path.isdir(bkp_dir): os.mkdir(bkp_dir)
    if not os.path.isdir(temp_dir): os.mkdir(temp_dir)
    conf["main_dir"] = main_dir
    conf["log_dir"] = log_dir
    conf["bkp_dir"] = bkp_dir
    conf["temp_dir"] = temp_dir
    conf["is_dir_created"] = True
    conf_json = open("chatwolf\\data\\conf.json", "w")
    json.dump(conf, conf_json)
    conf_json.close()

# delete old logs, backups and tokens
limit_time = time.time() - (86400 * conf["days_keep_log"])
for file in os.listdir(conf["log_dir"]):
    file = conf["log_dir"] + "\\" + file
    if os.path.getmtime(file) > limit_time:
        os.remove(file)

limit_time = time.time() - (86400 * conf["days_keep_bkp"])
for file in os.listdir(conf["bkp_dir"]):
    file = conf["bkp_dir"] + "\\" + file
    if os.path.getmtime(file) > limit_time:
        os.remove(file)

limit_time = time.time() - (86400 * conf["days_keep_temp"])
for file in os.listdir(conf["temp_dir"]):
    file = conf["temp_dir"] + "\\" + file
    if os.path.getmtime(file) > limit_time:
        os.remove(file)