import pygame
from pygame.locals import *
from config import *
import os
import json
import random

from layer import *
from clickManager import *
from node import *
from gridManager import *
from meterController import *
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
        self.messageSystem = MessageHud(self.game)
        self.openingMenu = GameOpeningMenu(self.game)

        self.personClickManager = PersonClickManager(self.game)
        self.transportClickManager = TransportClickManager(self.game)

        self.rendering = False

        # Game timer to keep track of how long has been played 
        self.timer = 0
        self.timeStep = 11.5 # make this dependant on the level and make it decrease as the number of people who reach their destinations increase
        # self.timeStep = 8
        self.timeSetMet = False

        self.dt = 1 # control the speed of whats on screen
        self.startDt = self.dt
        self.fixedScale = 1 # control the size of whats on the screen

        self.setDefaultMap()

        self.completed = 0
        self.totalToComplete = 0 # default is 0

        self.slowDownMeterAmount = 75

        self.debug = False

        self.connectionTypes = ["layer 4"] # the connection types availabe on the map (always has layer 4)


    def setDefaultMap(self):
        self.levelData = {
            "mapName": "", 
            "deletable": True, # Map can / cannot be deleted; maps that cant be deleted cant be opened in the editor
            "saved": False, # Has the map been saved before 
            "width": 18,
            "height": 10,
            "completion": {
                "total": 10,
                "completed": False,
                "time": 0
            },
            "backgrounds": {
                "layer 1": CREAM,
                "layer 2": CREAM,
                "layer 3": CREAM,
                "layer 4": CREAM
            },
            "connections": {}, 
            "transport": {}, 
            "stops": {},
            "destinations": {}
        } # Level data to be stored, for export to JSON


    def setRendering(self, rendering, transition = False):
        self.rendering = rendering
        self.hud.main(transition) if self.rendering else self.hud.close()
        self.messageSystem.main() if self.rendering else self.messageSystem.close()
        
    def runOpeningMenu(self):
        if self.rendering and not self.debug: 
            self.openingMenu.main()

    def setCompleted(self, completed):
        self.completed = completed
        self.hud.setCompletedText(str(self.completed))

    def setTotalToComplete(self, totalToComplete):
        self.totalToComplete = totalToComplete

    def setSlowDownMeterAmount(self, slowDownMeterAmount):
        self.slowDownMeterAmount = slowDownMeterAmount

    def setDt(self, dt):
        self.dt = dt

    def setFixedScale(self, fixedScale):
        self.fixedScale = fixedScale

    def setDebug(self, debug):
        self.debug = debug

    def getStartDt(self):
        return self.startDt

    def getDt(self):
        return self.dt

    def getFixedScale(self):
        return self.fixedScale

    def getHud(self):
        return self.hud

    def getMessageSystem(self):
        return self.messageSystem

    def getLevel(self):
        return self.level

    def getLevelData(self):
        return self.levelData

    def getPersonClickManager(self):
        return self.personClickManager

    def getTransportClickManager(self):
        return self.transportClickManager

    def getLayer(self):
        return self.currentLayer

    def getCompleted(self):
        return self.completed

    def getTotalToComplete(self):
        return self.totalToComplete

    def getSlowDownMeterAmount(self):
        return self.slowDownMeterAmount

    def getDebug(self):
        return self.debug

    def getConnectionTypes(self):
        return self.connectionTypes

    def addToCompleted(self):
        self.completed += 1
        # self.timeStep -= 0.5
        self.hud.setCompletedText(str(self.completed))
        self.meter.addToAmountToAdd(20)


    # Reset the level back to its default state
    def clearLevel(self):
        self.timer = 0
        self.allSprites.empty()
        self.layer1.empty()
        self.layer2.empty()
        self.layer3.empty()
        self.layer4.empty()

        # Reset the layers to show the top layer
        self.currentLayer = 4
        self.connectionTypes = []
        self.setDefaultMap()


    def createLevel(self, level, debug = False):
        self.clearLevel()
        self.setCompleted(0) 
        self.debug = debug

        # for running the game in test mode (when testing a level)
        if self.debug: 
            self.hud = PreviewHud(self.game)
            spacing = (1.5, 1.5) # push the level down since we have hud at the top
        else: 
            self.hud = GameHud(self.game)
            spacing = (1.5, 1)

        # ordering matters -> stack
        self.gridLayer4 = Layer4(self, (self.allSprites, self.layer4), level)

        # Set the name of the level
        self.level = self.gridLayer4.getGrid().getLevelName()

        # Set the level data
        self.levelData = self.gridLayer4.getGrid().getMap()

        # we want to get which connectionTypes are available in the map
        for connectionType in self.levelData['connections']:
            self.connectionTypes.append(connectionType)

        self.gridLayer3 = Layer3(self, (self.allSprites, self.layer3, self.layer4), level, spacing)
        self.gridLayer1 = Layer1(self, (self.allSprites, self.layer1, self.layer4), level, spacing)
        self.gridLayer2 = Layer2(self, (self.allSprites, self.layer2, self.layer4), level, spacing) # walking layer at the bottom so nodes are drawn above metro stations
        self.gridLayer4.addLayerLines(self.gridLayer1, self.gridLayer2, self.gridLayer3)

        self.gridLayer1.grid.loadTransport("layer 1")
        self.gridLayer2.grid.loadTransport("layer 2")
        self.gridLayer3.grid.loadTransport("layer 3")

        self.removeDuplicates()

        # Set all the destinations to be the destinations from all layers
        layer1Destinations =  self.gridLayer1.getGrid().getDestinations() 
        layer2Destinations =  self.gridLayer2.getGrid().getDestinations() 
        layer3Destinations =  self.gridLayer3.getGrid().getDestinations() 
        self.allDestinations = layer1Destinations + layer2Destinations + layer3Destinations

        # set number of people to complete level
        self.totalToComplete = random.randint(8, 12)

        self.meter = MeterController(self, self.allSprites, self.slowDownMeterAmount)

        # if there is more than one layer we want to be able to see 'all' layers at once (layer 4) otherwise we only need to see the single layer
        if len(self.connectionTypes) > 1 or self.debug:
            self.connectionTypes.append("layer 4")
        else:
            self.showLayer(self.getLayerInt(self.connectionTypes[0]))


    def getGridLayer(self, connectionType):
        if connectionType == "layer 1":
            return self.gridLayer1
        elif connectionType == "layer 2":
            return self.gridLayer2
        elif connectionType == "layer 3":
            return self.gridLayer3
            
    def getLayerInt(self, connectionType):
        if connectionType == "layer 1":
            return 1
        elif connectionType == "layer 2":
            return 2
        elif connectionType == "layer 3":
            return 3
        elif connectionType == "layer 4":
            return 4


    # Remove duplicate nodes on layer 4 for layering
    def removeDuplicates(self):
        seen = {}
        dupes = []

        layer1Nodes = self.gridLayer1.getGrid().getNodes()
        layer2Nodes = self.gridLayer2.getGrid().getNodes()
        layer3Nodes = self.gridLayer3.getGrid().getNodes()

        allnodes = layer1Nodes + layer2Nodes + layer3Nodes

        # Do i need to add tram stops????????????

        # Make sure stops are at the front of the list, so they are not removed 
        allnodes = sorted(allnodes, key=lambda x:isinstance(x, Stop))
        allnodes = sorted(allnodes, key=lambda x:isinstance(x, Destination))
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
            self.events()

            self.timer += self.game.dt * self.dt # we want players to spawn in line with the in-game time
            if int(self.timer) % self.timeStep == 0:
                if not self.timeSetMet:
                    # print("is this called??")
                    self.timeSetMet = True

                    # Create a person, passing through all the destinations from all layers so that persons destination can be from any layer
                    self.gridLayer2.addPerson(self.allDestinations)
            else:
                self.timeSetMet = False      

            
    def events(self):
        keys = pygame.key.get_pressed()
        key = [pygame.key.name(k) for k,v in enumerate(keys) if v]

        # if len(key) == 1:
        #     if key[0] == config["controls"]["dtDown"]: # slow down
        #         if self.dt != self.startDt -0.5:
        #             self.game.audioLoader.playSound("slowIn", 1)

        #         self.dt = self.startDt - 0.5
        #     elif key[0] == config["controls"]["dtUp"]: # speed up

        #         self.dt = self.startDt + 0.5
        # else:
        #     if self.dt != self.startDt:
        #         self.game.audioLoader.playSound("slowOut", 1)


        #     self.dt = self.startDt
        # keys = pygame.key.get_pressed()
        # key = [pygame.key.name(k) for k, v in enumerate(keys) if v]

        # if len(key) == 1:
        #     if key[0] == config["controls"]["dtDown"]:
        #         self.game.clickManager.setSpaceBar(True)
        # else:
        #     self.game.clickManager.setSpaceBar(False)   
        
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            self.game.clickManager.setSpaceBar(True)
        else:
            self.game.clickManager.setSpaceBar(False)


    def showLayer(self, layer):
        # only switch to a layer that is in the map
        if "layer " + str(layer) in self.connectionTypes: 
            self.currentLayer = layer
            self.resize() #redraw the nodes so that the mouse cant collide with them
            self.hud.updateLayerText()


    def resize(self):
        # If a layer has any images, they must be resized here
        if self.rendering:
            self.gridLayer1.resize()
            self.gridLayer2.resize()
            self.gridLayer3.resize()    
            self.gridLayer4.resize() # only need to do this if it has components

            # we want to reset the layer 4 lines with the new ones (resized) from the other layers
            self.gridLayer4.addLayerLines(self.gridLayer1, self.gridLayer2, self.gridLayer3) 
            
            # resize huds and menus
            self.hud.resize()
            self.messageSystem.resize()
            self.openingMenu.resize()

            for sprite in self.allSprites:
                sprite.dirty = True


    def renderLayer(self, layer, gridLayer, group):
        if self.currentLayer == layer:
            gridLayer.draw()
            for sprite in group:
                sprite.draw()


    def render(self):
        if self.rendering:    
            self.renderLayer(1, self.gridLayer1, self.layer1)
            self.renderLayer(2, self.gridLayer2, self.layer2)
            self.renderLayer(3, self.gridLayer3, self.layer3)
            self.renderLayer(4, self.gridLayer4, self.layer4)


            # Render the hud above all the other sprites
            self.hud.display()
            self.messageSystem.display()
            self.openingMenu.display()
            
