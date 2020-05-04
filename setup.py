from setuptools import setup
from os import path

setup(name="Chatwolf",
      versin = "0.1",
      description="An unofficial game, to play Werewolf on Skype",
      long_description=open(".README.md", "r").read(),
      packages=["chatwolf"],
      install_requires=["skpy"],
      author = "Max Schmit",
      author_email = "maxschm@hotmail.com",
      url="https://github.com/maxschmi/chatwolf")
