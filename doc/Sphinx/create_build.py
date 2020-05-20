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
#                   prepare data for Sphinx                             #
#              copy all the necessary data in doc/Sphinx/data           #
#-----------------------------------------------------------------------#

# copy all the necessary data in doc/Sphinx/data

#libraries
import os
from pathlib import Path
import re

sphinx_path = Path(os.path.abspath(__file__)).parent
chatwolf_path = sphinx_path.parent.parent
# get copies of docs from top
top_files = ["README.md", "LICENSE.txt", "CHANGELOG.txt", "Dependecies_Licenses.txt"]
for file_name in top_files:
    cont = open(str(chatwolf_path) + "/" + file_name, "r").read()
    file_build = open(str(sphinx_path) + "/data/" + file_name, "w")
    file_build.write(cont)
    file_build.close()
del cont

#delete hyperref from readme
with open(str(sphinx_path) + "/data/Readme.md", "r") as f:
    cont = []
    for l in f.readlines():
        if not re.search("(Documentation Status)+", l):
            cont.append(l)

with open(str(sphinx_path) + "/data/Readme.md", "w") as f:
    f.writelines(cont)