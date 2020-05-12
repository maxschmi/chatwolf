import os
from pathlib import Path
chatwolf_path = Path(os.path.abspath('.')).parent.parent

# get copies of docs from top
top_files = ["Readme.md", "LICENSE.txt", "CHANGELOG.txt", "Dependecies_Licenses.txt"]
for file_name in top_files:
    cont = open(str(chatwolf_path) + "/" + file_name, "r").read()
    file_build = open("data/" + file_name, "w")
    file_build.write(cont)
    file_build.close()