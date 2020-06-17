import pygame
from pygame.locals import *
from config import *
import os
import json

from layer import *
from clickManager import *
from node import *
from gridManager import *
from menu import *

vec = pygame.math.Vector2

class Renderer:
    def __init__(self, game):
        self.game = game
        self.width = config["graphics"]["displayWidth"]
        self.height = config["graphics"]["displayHeight"]
        self.windowWidth = config["graphics"]["displayWidth"]
        self.windowHeight = config["graphics"]["displayHeight"]

        self.monitorWidth = pygame.display.Info().current_w
        self.monitorHeight = pygame.display.Info().current_h

        self.screen = pygame.display.set_mode((self.windowWidth, self.windowHeight), pygame.RESIZABLE)
        self.gameDisplay = pygame.Surface((self.width, self.height))

        self.scale = 1
        self.surfaces = []

        self.fpsFont = pygame.font.Font(pygame.font.get_default_font(), 30)
        self.fontImage = self.fpsFont.render(str(int(self.game.clock.get_fps())), False, RED)



    # Prepare the gamedisplay for blitting to, this means overriding it with a new color
    def prepareSurface(self, color):
        self.gameDisplay.fill(color)


    # Add a surface to the gameDisplay
    def addSurface(self, surface, pos = tuple()):
        self.surfaces.append((surface, vec(pos[0], pos[1])))


    def setWidth(self, width):
        self.width = width


    def setHeight(self, height):
        self.height = height


    def getScale(self):
        return self.scale


    def getDifference(self):
        difx = (self.windowWidth - self.width) / 2
        dify = (self.windowHeight - self.height) / 2
        return (difx, dify)
    

    def getHeight(self):
        return self.height


    def setFullscreen(self):
        self.setScale((self.monitorWidth, self.monitorHeight), True)


    def unsetFullscreen(self):
        self.setScale((config["graphics"]["displayWidth"], config["graphics"]["displayHeight"]))


    def setScale(self, size, fullscreen = False):
        size = list(size)
        if size[0] < config["graphics"]["minDisplayWidth"]: size[0] = config["graphics"]["minDisplayWidth"]
        if size[1] < config["graphics"]['minDisplayHeight']: size[1] = config["graphics"]["minDisplayHeight"]

        self.scale = round(min(size[1] / config["graphics"]["displayHeight"], size[0] / config["graphics"]["displayWidth"]), 1)
        
        self.width = (config["graphics"]["displayWidth"] * self.scale)
        self.height = (config["graphics"]["displayHeight"] * self.scale)
        self.windowWidth = size[0]
        self.windowHeight = size[1]
        if fullscreen:
            self.screen = pygame.display.set_mode((int(self.windowWidth), int(self.windowHeight)), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
        else:
            self.screen = pygame.display.set_mode((int(self.windowWidth), int(self.windowHeight)), pygame.RESIZABLE | pygame.DOUBLEBUF)
        self.gameDisplay = pygame.Surface((self.width, self.height))  


    # on tick function
    def render(self):
        for surface in self.surfaces:    
            self.gameDisplay.blit(surface[0], (surface[1].x, surface[1].y))

        self.gameDisplay.blit(self.fontImage, (10, 10))

        self.screen.blit(self.gameDisplay, (0 + self.getDifference()[0], 0 + self.getDifference()[1]))
        self.surfaces = []
        
        pygame.display.update()

        self.fontImage = self.fpsFont.render(str(int(self.game.clock.get_fps())), False, RED)


class SpriteRenderer():
    #loads all the sprites into groups and stuff
    def __init__(self, game):
        self.allSprites = pygame.sprite.Group()
        self.layer1 = pygame.sprite.Group() # layer 1
        self.layer2 = pygame.sprite.Group() # layer 2
        self.layer3 = pygame.sprite.Group() # layer 3
        self.layer4 = pygame.sprite.Group() # layer 4 is all layers combined
        self.game = game
        self.currentLayer = 4

        self.level = ""

        # Hud for when the game is running
        self.hud = GameHud(self.game)

        self.clickManager = GameClickManager(self.game)

        self.rendering = False

        self.setDefaultMap()


    def setDefaultMap(self):
        self.levelData = {
            "mapName": "", 
            "deletable": True, # Map can / cannot be deleted; maps that cant be deleted cant be opened in the editor
            "saved": False, # Has the map been saved before 
            "connections": {}, 
            "transport": {}, 
            "stops": {}
        } # Level data to be stored, for export to JSON


    def setRendering(self, rendering):
        self.rendering = rendering
        self.hud.main() if self.rendering else self.hud.close()


    def getHud(self):
        return self.hud

    def getLevel(self):
        return self.level

    def getLevelData(self):
        return self.levelData

    def getClickManager(self):
        return self.clickManager


    def clearLevel(self):
        self.allSprites.empty()
        self.layer1.empty()
        self.layer2.empty()
        self.layer3.empty()
        self.layer4.empty()

        # Reset the layers to show the top layer
        self.currentLayer = 4
        self.setDefaultMap()


    def createLevel(self, level, debug = False):
        self.clearLevel()

        if debug:
            self.hud = PreviewHud(self.game)
        else:
            self.hud = GameHud(self.game)

        # ordering matters -> stack
        self.gridLayer4 = Layer4(self, (self.allSprites, self.layer4), level)
        self.gridLayer3 = Layer3(self, (self.allSprites, self.layer3, self.layer4), level)
        self.gridLayer1 = Layer1(self, (self.allSprites, self.layer1, self.layer4), level)
        self.gridLayer2 = Layer2(self, (self.allSprites, self.layer2, self.layer4), level) # walking layer at the bottom so nodes are drawn above metro stations

        self.gridLayer1.grid.loadTransport("layer 1")
        self.gridLayer2.grid.loadTransport("layer 2")
        self.gridLayer3.grid.loadTransport("layer 3")

        self.removeDuplicates()

        self.gridLayer2.addPerson()


        # Set the name of the level
        self.level = self.gridLayer4.getGrid().getLevelName()

        # Set the level data
        self.levelData = self.gridLayer4.getGrid().getMap()



    def getGridLayer(self, connectionType):
        if connectionType == "layer 1":
            return self.gridLayer1
        if connectionType == "layer 2":
            return self.gridLayer2
        if connectionType == "layer 3":
            return self.gridLayer3


    # Remove duplicate nodes on layer 4 for layering
    def removeDuplicates(self):
        seen = {}
        dupes = []

        layer1Nodes = self.gridLayer1.getGrid().getNodes()
        layer2Nodes = self.gridLayer2.getGrid().getNodes()
        layer3Nodes = self.gridLayer3.getGrid().getNodes()

        allnodes = layer1Nodes + layer2Nodes + layer3Nodes

        # Make sure stops are at the front of the list, so they are not removed 
        allnodes = sorted(allnodes, key=lambda x:isinstance(x, MetroStation))
        allnodes = sorted(allnodes, key=lambda x:isinstance(x, BusStop))
        allnodes = allnodes[::-1] # Reverse the list so they're at the front

        for node in allnodes:
            if node.getNumber() not in seen:
                seen[node.getNumber()] = 1
            else:
                if seen[node.getNumber()] == 1:
                    dupes.append(node)

        for node in dupes:
            self.layer4.remove(node)


    def update(self):
        if self.rendering:
            self.allSprites.update()


    def showLayer(self, layer):
        self.currentLayer = layer
        self.resize() #redraw the nodes so that the mouse cant collide with them


    def getLayer(self):
        return self.currentLayer


    def resize(self):
        # If a layer has any images, they must be resized here
        if self.rendering:
            self.gridLayer1.resize()
            self.gridLayer2.resize()
            self.gridLayer3.resize()    
            self.gridLayer4.resize()
            self.hud.resize()

            for sprite in self.allSprites:
                sprite.dirty = True


    def renderLayer(self, layer, group):
        if self.currentLayer == layer:
            for sprite in group:
                sprite.draw()


    def render(self):
        if self.rendering:
            self.renderLayer(1, self.layer1)
            self.renderLayer(2, self.layer2)
            self.renderLayer(3, self.layer3)
            self.renderLayer(4, self.layer4)


            # Render the hud above all the other sprites
            self.hud.display()
            


class ImageLoader:
    def __init__(self):
        self.images = {}

        self.loadAllImages()

    def loadAllImages(self):
        for key, image in config["images"].items():
            i = pygame.image.load(os.path.join(ASSETSFOLDER, image)).convert_alpha()
            self.images[key] = i

    def getImage(self, key):
        return self.images[key]


class MapLoader:
    def __init__(self):
        self.maps = {}

        self.loadAllMaps()
        
    def getMaps(self):
        return self.maps
    
    def getMap(self, key):
        return self.maps[key]

    def getLongestMapLength(self):
        longest = 0
        for mapName in self.maps:
            if len(mapName) > longest:
                longest = len(mapName)
        return longest

    def addMap(self, mapName, path):
        self.maps[mapName] = path

    def loadAllMaps(self):
        for key, level in config["maps"].items():
            m = os.path.join(MAPSFOLDER, level)
            self.maps[key] = m
            

