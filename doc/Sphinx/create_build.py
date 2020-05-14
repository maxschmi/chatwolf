# copy all the necessary data in doc/Sphinx/data

#libraries
import os
from pathlib import Path
import re

sphinx_path = Path(os.path.abspath(__file__)).parent
chatwolf_path = sphinx_path.parent.parent
# get copies of docs from top
top_files = ["Readme.md", "LICENSE.txt", "CHANGELOG.txt", "Dependecies_Licenses.txt"]
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