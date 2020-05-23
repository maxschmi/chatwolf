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
#                   create a new release                                #
#            don't forget to enter the new Version                      #
#-----------------------------------------------------------------------#

#libraries
import os
import re
from pathlib import Path
import shutil

# inputs
new_version = "0.1.5"

#setup
os.chdir(Path(os.path.abspath(__file__)).parent.parent)

# version parts
ver_major, ver_minor, ver_patch = re.split(r"[.]", new_version)

#change version in setup.py
content = []
with open(os.path.realpath("setup.py"), "r") as f:
    for line in f:
        if re.search(r"(version)+[ ]*[=]+[ ]*[\".\d]*", line):
            line = re.sub(r"(\"\d.\d.\d\")+", 
                          '"' + new_version + '"', line)
        content.append(line)

with open(os.path.realpath("setup.py"),"w") as f:
    for i in range(len(content)):
        f.write(content[i])
del content

#change version in doc/Sphinx/conf.py
content = []
with open(os.path.realpath("doc/Sphinx/conf.py"), "r") as f:
    for line in f:
        if re.search(r"(release)+[ ]*[=]+[ ]*[\'.\d]*", line):
            line = re.sub(r"('\d.\d.\d')+", 
                          "'" + new_version + "'", line)
        content.append(line)

with open(os.path.realpath("doc/Sphinx/conf.py"),"w") as f:
    for i in range(len(content)):
        f.write(content[i])
del content

#change version in install/file_version_info.txt (4times)
content = open("install/file_version_info.txt", "r").read()

repl = "filevers=(" + ver_major + ", " + ver_minor + ", " + ver_patch + ", 0)"
content = re.sub(r"filevers=\(\d+, \d+, \d+, \d+\)", repl, content)

repl = "prodvers=(" + ver_major + ", " + ver_minor + ", " + ver_patch + ", 0)"
content = re.sub(r"prodvers=\(\d+, \d+, \d+, \d+\)", repl, content)

repl = "u'FileVersion', u'" + new_version + "'"
content = re.sub(r"u'FileVersion', u'\d+.\d+.\d+'", repl, content)

repl = "u'ProductVersion', u'" + new_version + "'"
content = re.sub(r"u'ProductVersion', u'\d+.\d+.\d+'", repl, content)

with open("install/file_version_info.txt", "w") as f:
    f.write(content)

# create docs
#-------------

# uninstall and install actual chatwolf version
os.system("pip uninstall chatwolf")
os.system("pip install .")

#empty latex folder
for f in os.listdir("doc/latex"):
    if os.path.isfile(f):
        os.remove(f)
    elif os.path.isdir(f):
        os.rmdir(f)

#create docs
os.system("Sphinx-build -b latex doc/Sphinx doc/latex")
os.system("Sphinx-build -b html doc/Sphinx doc/html")
os.chdir("doc/pdf/")
print(os.getcwd())
os.system("texify -cp ../latex/chatwolf.tex --pdf")
os.chdir("../..")
print(os.getcwd())

# create standalone distribution
os.system('pyinstaller --add-data="README.md;." --add-data="LICENSE.txt;." '+
    '--add-data="install/UNINSTALL.txt;." '+
    '--add-data="doc/pdf/chatwolf.pdf;doc/" '+
    '--add-data="chatwolf/data/messages;chatwolf/data/messages" '+
    '--add-data="chatwolf/data/conf_root.json;chatwolf/data/" '+
    '--add-data="chatwolf/data/icon.png;chatwolf/data/" '+
    '--name="Chatwolf" '+
    #'--specpath="install/" ' +
    '--icon="install/icon.ico" --version-file="install/file_version_info.txt" ' +
    '--onedir --noconfirm --hidden-import="pkg_resources.py2_warn" ' +
    '--windowed --clean run.pyw')

#zip folder
os.chdir("dist")
shutil.make_archive(base_name="chatwolf_win_" + re.sub(r"\.", "-", new_version), 
                    format='zip', 
                    base_dir="chatwolf")
shutil.rmtree("chatwolf")
