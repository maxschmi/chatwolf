from setuptools import setup
#import os

#messages =[]
#for file in os.walk("messages", topdown=False):
#    if os.path.isfile(file):
#        print(file)
#        messages.append(file)

setup(name="Chatwolf",
      version = "0.1.0",
      description="An unofficial game, to play Werewolf on Skype",
      long_description=open("README.md", "r").read(),
      packages=["chatwolf"],
      #package_dir={"chatwolf": "chatwolf"},
      package_data={'chatwolf': ['data/messages/en/*.txt',
                                 "data/icon.png",
                                 "data/conf_root.json",
                                 ]},
      install_requires=["skpy"],
      python_requires='>=3',
      author = "Max Schmit",
      author_email = "maxschm@hotmail.com",
      url="https://github.com/maxschmi/chatwolf",
      project_urls={ 
        'Github': 'https://github.com/maxschmi/chatwolf',
        'Docs': ''},
      entry_points={  # Optional
        'console_scripts': ['chatwolf=chatwolf.__main__:main',
        ],},
      license = "GPL-3.0-or-later",
      classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Natural Language :: English",
        "Topic :: Communications",
        "Topic :: Communications :: Chat",
        "Topic :: Communications :: Conferencing",
        "Topic :: Games/Entertainment",
        "Topic :: Games/Entertainment :: Role-Playing"],
      keywords = "chat werewolf game multiplayer online skype",
        )

