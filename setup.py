from setuptools import setup
#import os

#messages =[]
#for file in os.walk("messages", topdown=False):
#    if os.path.isfile(file):
#        print(file)
#        messages.append(file)

setup(name="Chatwolf",
      version = "0.1",
      description="An unofficial game, to play Werewolf on Skype",
      long_description=open("README.md", "r").read(),
      packages=["chatwolf"],
      #package_dir={"chatwolf": "chatwolf"},
      package_data={'chatwolf': ['data/messages/en/*.txt',
                                 "data/icon.png",
                                 "data/conf_root.json",]},
      install_requires=["skpy"],
      author = "Max Schmit",
      author_email = "maxschm@hotmail.com",
      url="https://github.com/maxschmi/chatwolf",
      license = "GPL-3.0-or-later")

