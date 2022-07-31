import json
import os
import sys
from pygame.locals import Color


def getFilePath():
    if getattr(sys, 'frozen', False):  # for when .exe
        return os.path.dirname(sys.executable)
    return os.path.dirname(__file__)


# dump config file to json for saving
def dump(data):
    with open('config.json', 'w') as f:
        json.dump(data, f)


# Load the config from json
with open('config.json') as f:
    config = json.load(f)

# constants
GAMEFOLDER = getFilePath()
FONTFOLDER = os.path.join(GAMEFOLDER, "fonts")
ASSETSFOLDER = os.path.join(GAMEFOLDER, 'assets')
MAPSFOLDER = os.path.join(GAMEFOLDER, 'maps')
AUDIOFOLDER = os.path.join(GAMEFOLDER, 'audio')
MUSICFOLDER = os.path.join(AUDIOFOLDER, 'music')

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

BACKGROUNDCOLORS = {
    "Black": {
        "color": BLACK,
        "darkMode": True
    },
    "White": {
        "color": CREAM,
        "darkMode": False
    },
    "Grey": {
        "color": TEMPGREY,
        "darkMode": False
    },
    "Red": {
        "color": TEMPRED,
        "darkMode": True
    },
    "Blue": {
        "color": BLUE,
        "darkMode": True
    },
    "Green": {
        "color": TEMPGREEN,
        "darkMode": False
    }
}
DEFAULTBACKGROUND = CREAM

# Colors for each of the different layers.
LAYERCOLORS = {
    1: {
        "color": RED,
        "name": "red"
    },
    2: {
        "color": GREY,
        "name": "grey"
    },
    3: {
        "color": GREEN,
        "name": "green"
    }
}

# Colors for each temporary connection on each layer.
TEMPLAYERCOLORS = {
    1: {
        "color": TEMPRED,
        "name": "red"
    },
    2: {
        "color": TEMPGREY,
        "name": "grey"
    },
    3: {
        "color": TEMPGREEN,
        "name": "green"
    }
}

SCANLINESGREEN = (38, 127, 0, 20)
SCANLINESBLUE = (0, 102, 255, 20)
SCANLINES = SCANLINESGREEN


DEFAULTLIVES = 3

DEFAULTBOARDWIDTH = 18
DEFAULTBOARDHEIGHT = 10

# Default layer names for the grid
LAYERNAMES = [
    'Metro',
    'Roads',
    'Trams',
    'Overview'
]

# Layer, node pairs that defines which node types can be added to each of the
# individual layers.
LAYERNODEMAPPINGS = {
    1: ["metro", "airport", "house", "office", "school", "shop"],
    2: [
        "bus", "noWalkNode", "airport", "house", "office", "school",
        "shop"],
    3: ["tram", "airport", "house", "office", "school", "shop"]
}

# Layer, node pairs that defines which transport types can be added to each of
# the individual layers.
LAYERTRANSPORTMAPPINGS = {
    1: ["metro"],
    2: ["bus", "taxi"],
    3: ["tram"]
}


# The default level config for any new maps being added
DEFAULTLEVELCONFIG = {
    "mapName": "",
    "options": {
        # If we want the level to have lives or not:
        # (if it doesn't we don't need the timer to be shown for
        # each person since there is no limit as no lives)
        "lives": True,
        "limitPeople": False,  # Limit the No. people who can spawn
        "setSpawn": False  # Set the spawn to a specific node
    },
    "locked": {"isLocked": False, "unlock": 0},  # Amount to unlock

    # Map can / cannot be deleted; maps that can't be
    # deleted can't be opened in the editor
    "deletable": True,

    "saved": False,  # Has the map been saved before
    "width": 18,
    "height": 10,
    "difficulty": 1,  # Out of 4
    "total": 8,  # Total to complete the level
    "score": 0,
    "completion": {"completed": False},
    "backgrounds": {
        "layer 1": DEFAULTBACKGROUND,  # Default color: CREAM :)
        "layer 2": DEFAULTBACKGROUND,
        "layer 3": DEFAULTBACKGROUND,
        "layer 4": DEFAULTBACKGROUND
    },
    "connections": {},
    "transport": {},
    "stops": {},
    "destinations": {},
    "specials": {}  # For special ndes, such as no walk nodes etc.
}  # Level data to be stored, for export to JSON
