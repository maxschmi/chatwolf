## Chatwolf
[![Documentation Status](https://readthedocs.org/projects/chatwolf/badge/?version=latest)](https://chatwolf.readthedocs.io/en/latest/?badge=latest) ![Upload Python Package](https://github.com/maxschmi/chatwolf/workflows/Upload%20Python%20Package/badge.svg)
Chatwolf is a small bot to play the popular Werewolf game in a group over a videochat.
Until now it only works on Skype, but maybe I will add other chat services.

# Rules of the game
Here you can find the basic rules of the werewolf game in german language:
[www.werwolfspielen.info](http://www.werwolfspielen.info/spielregeln.html)

# install the executable distribution (easiest way)
1. download the latest distribution from [here](https://github.com/maxschmi/chatwolf/releases)
2. unzip the folder to where you want to have the program 
It is standalone, so you do not need to install. To unistall simply delete the whole folder.
3. do to the folder and run the "chatwolf.exe" file

# install by source
1. you need Python3 installed. 
  If you haven't got it install it from [here](https://www.python.org/downloads/)
2. open the terminal and install chatwolf from pypi with:
```
pip install chatwolf
```
You can now use it ass a package. 

3. start the GUI or use the "start_manualy.py" script, which is in "chatwolf/scripts/".

To start the GUI just enter `chatwolf` in the terminal.

If this doesn't work, open python.exe and enter:
```python
import chatwolf
root = chatwolf.GUI()
root.mainloop()
```

# Quickstart with GUI:
- you need one additional Skype account, wich will be the Game-master-Account. 
  Create one or just ask a friend whos not playing to give you his/her account
- create a group in Skype with your friends and the Game-master-Account.
- log in with the Skype account of the Game-master-Account in the program
- select the groupchat, the number of werewolfs and the roles you want
- start the game and play on Skype. 
  You will get all further commands over Skype from the Game-master-Account
  
# Tip:
- if you want to use another Videochat service for the Videocalls, you can do so. 
  Just use Skype to talk to the Game-master-Account.
