import json
import os
import sys
from pygame.locals import Color


def getFilePath():
    if getattr(sys, 'frozen', False):  # for when .exe
        return os.path.dirname(sys.executable)
    return os.path.dirname(__file__)


def dump(data):
    with open('config.json', 'w') as f:
        json.dump(data, f)


with open('config.json') as f:
    config = json.load(f)

# constants
GAMEFOLDER = getFilePath()
FONTFOLDER = os.path.join(GAMEFOLDER, "fonts")
ASSETSFOLDER = os.path.join(GAMEFOLDER, 'assets')
MAPSFOLDER = os.path.join(GAMEFOLDER, 'maps')
AUDIOFOLDER = os.path.join(GAMEFOLDER, 'audio')

# colours
TRUEBLACK = (0, 0, 0)
BLACK = (65, 62, 75)
WHITE = Color("white")
GREEN = (0, 169, 132)
TEMPGREEN = (0, 230, 180)
LIGHTGREEN = (176, 212, 194)
# GREEN = (0, 204, 160)
BLUE = (0, 89, 179)
CREAM = (246, 246, 238)
RED = (255, 102, 102)
TEMPRED = (255, 153, 153)
YELLOW = (238, 220, 55)
GREY = (201, 199, 209)
TEMPGREY = (228, 227, 232)
HOVERGREY = (153, 153, 153)

SCANLINESGREEN = (38, 127, 0, 20)
SCANLINESBLUE = (0, 102, 255, 20)
SCANLINES = SCANLINESGREEN

DEFAULTLIVES = 3
# DEFAULTLIVES = 1

# dump config file to json for saving
