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

    def getLayer(self):
        return self.currentLayer


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
        self.hud.updateLayerText()


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
            
