import pygame
import json
import os, sys



"""
    To do: 
        --- load config from json
        --- dump config to json on save
"""

pygame.init()

def getFilePath():
    if getattr(sys, 'frozen', False): #for when .exe
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(__file__)


with open('config.json') as f:
    config = json.load(f)

# constants
GAMEFOLDER = getFilePath()
FONTFOLDER = os.path.join(GAMEFOLDER, "fonts")
ASSETSFOLDER = os.path.join(GAMEFOLDER, 'assets')
MAPSFOLDER = os.path.join(GAMEFOLDER, 'maps')

# colours
TRUEBLACK = (0, 0, 0)
BLACK = (65, 62, 75)
GREEN = (0, 169, 132)
BLUE = (0, 89, 179)
CREAM = (246, 246, 238)
RED = (255, 102, 102)
YELLOW = (238, 220, 55)
GREY = (201, 199, 209)
HOVERGREY = (153, 153, 153)

# dump config file to json for saving
def dump(data):
    with open('config.json', 'w') as f:
        json.dump(data, f)

