import pygame
import random
import copy
from config import config, dump, DEFAULTLIVES, LAYERNAMES, DEFAULTLEVELCONFIG
from utils import vec, checkKeyExist
from person import Person
from transport import Transport
from layer import Layer
from clickManager import (
    PersonClickManager, TransportClickManager, PersonHolderClickManager)
from node import NodeType
from meterController import MeterController
from tutorialManager import TutorialManager
from menu import GameMenu
from hud import GameHud, MessageHud, PreviewHud


class SpriteRenderer():
    # Loads all the sprites into groups and stuff
    def __init__(self, game):
        self.allSprites = pygame.sprite.Group()
        self.belowEntities = pygame.sprite.Group()
        self.aboveEntities = pygame.sprite.Group()
        self.layer1 = pygame.sprite.Group()  # layer 1
        self.layer2 = pygame.sprite.Group()  # layer 2
        self.layer3 = pygame.sprite.Group()  # layer 3
        self.layer4 = pygame.sprite.Group()  # layer 4 is all layers combined
        self.game = game
        self.currentLayer = 4

        self.level = ""

        # Hud for when the game is running
        self.hud = GameHud(self)
        self.menu = GameMenu(self)
        self.messageSystem = MessageHud(self.game)

        self.personClickManager = PersonClickManager(self.game)
        self.transportClickManager = TransportClickManager(self.game)
        self.personHolderClickManager = PersonHolderClickManager(self.game)

        self.rendering = False

        # Game timer to keep track of how long has been played
        self.timer = 0

        # Make this dependant on the level and make it decrease
        # as the number of people who reach their destinations increase
        self.timeStep = 25

        self.lives = DEFAULTLIVES
        self.score, self.bestScore = 0, 0

        self.dt = 1  # Control the speed of whats on screen
        self.startDt = self.dt
        self.fixedScale = 1  # Control the size of whats on the screen
        self.offset = vec(0, 0)

        self.startingFixedScale = 0
        self.paused = False  # Individual pause for the levels

        self.setDefaultMap()

        self.totalPeople, self.completed, self.totalToComplete = 0, 0, 0
        self.sequence = 0  # Keep track of the spawning order
        self.totalPeopleNone = False
        self.slowDownMeterAmount = 75

        self.debug = False
        self.darkMode = False

        # The connection types availabe on the map (always has layer 4)
        self.connectionTypes = ["layer 4"]

    def setDefaultMap(self):
        # We deepcopy to stop leveldata making changes to the imported dict.
        self.levelData = copy.deepcopy(DEFAULTLEVELCONFIG)

    # Save function, for when the level has already
    # been created before (and is being edited)
    def saveLevel(self):
        self.game.mapLoader.saveMap(self.levelData["mapName"], self.levelData)

    def setRendering(self, rendering, transition=False):
        self.rendering = rendering

        # We load the game hud if we are rending the level,
        # otherwise we close the hud
        self.hud.main(transition) if self.rendering else self.hud.close()

        (self.messageSystem.main() if self.rendering
            else self.messageSystem.close())

        # Create the paused surface when first rendering
        self.createPausedSurface()

    def runStartScreen(self):
        if self.rendering and not self.debug:
            self.menu.startScreen()

    def runEndScreen(self, completed=False):
        if not self.rendering or self.debug:
            return

        self.game.audioLoader.restoreMusic()
        (self.menu.endScreenComplete(True) if completed
            else self.menu.endScreenGameOver(True))

    # When the player completed the level, set it to complete
    # in the level data and save the data
    def setLevelComplete(self):
        if not hasattr(self, 'levelData'):
            return

        # If the level is not already set to completed, complete it
        if not self.levelData["completion"]["completed"]:
            self.levelData["completion"]["completed"] = True
            self.saveLevel()

    # Use the number of lives left to work out the players score TODO:
    #   Make this use other factors in the future

    # Return the previous keys and difference so
    # this can be used in the menu animation
    def setLevelScore(self):
        if not hasattr(self, 'levelData'):
            return

        self.score = self.lives if self.lives is not None else DEFAULTLIVES
        previousScore = 0

        if "score" in self.levelData:
            previousScore = self.levelData["score"]
            self.bestScore = previousScore

        if self.score > previousScore:
            self.levelData["score"] = self.score
            self.saveLevel()

        if self.score - previousScore > 0:
            scoreDifference = self.score - previousScore
        else:
            scoreDifference = 0

        # Use this in the menu animation
        previousKeys = config["player"]["keys"]
        config["player"]["keys"] += scoreDifference
        dump(config)

        return previousKeys, scoreDifference, previousScore

    def setTotalToComplete(self, totalToComplete):
        self.totalToComplete = totalToComplete

    def setSlowDownMeterAmount(self, slowDownMeterAmount):
        self.slowDownMeterAmount = slowDownMeterAmount

    def setDt(self, dt):
        self.dt = dt

    def setFixedScale(self, fixedScale):
        self.fixedScale = fixedScale

    def setOffset(self, offset=tuple()):
        self.offset = vec(offset[0], offset[1])

    def setSequence(self, sequence):
        self.sequence = sequence

    def calculateOffset(self):
        scaleChange = self.fixedScale - 1.0
        offX = -((config["graphics"]["displayWidth"] / 2) * scaleChange)
        offY = -((config["graphics"]["displayHeight"] / 2) * scaleChange)

        self.offset = vec(offX, offY)

    def setDebug(self, debug):
        self.debug = debug

    def setDarkMode(self):
        self.darkMode = (
            True if checkKeyExist(self.levelData, ['backgrounds', 'darkMode'])
            else False)

    def setTotalPeople(self, totalPeople):
        self.totalPeople = totalPeople

    def setLives(self, lives):
        self.lives = lives

    def togglePaused(self):
        self.dt = 0
        self.paused = not self.paused
        # self.createPausedSurface()

        if self.paused:
            # We don't want to show hover over for nodes when paused.
            self.game.clickManager.resetMouseOver()

    def getStartDt(self):
        return self.startDt

    def getDt(self):
        return self.dt

    def getFixedScale(self):
        return self.fixedScale

    def getStartingFixedScale(self):
        return self.startingFixedScale

    def getHud(self):
        return self.hud

    def getMenu(self):
        return self.menu

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

    def getCompleted(self):
        return self.completed

    def getTotalToComplete(self):
        return self.totalToComplete

    def getSlowDownMeterAmount(self):
        return self.slowDownMeterAmount

    def getSequence(self):
        return self.sequence

    def getDebug(self):
        return self.debug

    def getConnectionTypes(self):
        return self.connectionTypes

    def getDarkMode(self):
        return self.darkMode

    def getTotalPeople(self):
        return self.totalPeople

    def getLives(self):
        return self.lives

    def getAllDestination(self):
        if hasattr(self, 'allDestinations'):
            return self.allDestinations

    def getScore(self):
        return self.score

    def getBestScore(self):
        return self.bestScore

    def getPaused(self):
        return self.paused

    def getCurrentLayer(self):
        return self.currentLayer

    def getCurrentLayerString(self):
        return "layer " + str(self.currentLayer)

    def getPersonHolderClickManager(self):
        return self.personHolderClickManager

    def setGridLayer4Lines(self):
        return self.gridLayer4.setLayerLines(
            self.gridLayer1, self.gridLayer2, self.gridLayer3)

    def removeLife(self):
        if self.lives is None:
            return

        self.lives -= 1
        # remove a heart from the hud here or something
        self.hud.setLifeAmount()
        if self.lives <= 0:
            # Although we pause the game in the timer, we want to
            # stop anything else from reducing the life count here whilst the
            # timer is decreasing (so no one can die whilst it is decreasing)
            pass

    def addToCompleted(self):
        self.completed += 1
        # self.timeStep -= 0.5
        self.hud.setCompletedAmount()
        self.meter.addToAmountToAdd(20)

    # Reset the level back to its default state
    def clearLevel(self):
        self.paused = False  # Not to confuse the option menu
        self.startingFixedScale = 0  # reset the scale back to default
        self.timer = 0
        self.totalPeople = 0
        self.sequence = 0  # Reset the sequence to start over
        self.totalPeopleNone = False
        self.belowEntities.empty()
        self.aboveEntities.empty()
        self.allSprites.empty()
        self.layer1.empty()
        self.layer2.empty()
        self.layer3.empty()
        self.layer4.empty()

        # Reset the local ID's on the person and the transport
        Person.newid = 0
        Transport.newid = 0

        # Reset the layers to show the top layer
        self.currentLayer = 4
        self.connectionTypes = []
        self.setDefaultMap()

        # Make sure mouse over is set to None.
        self.game.clickManager.resetMouseOver()

    def createLevel(self, level, debug=False):
        self.clearLevel()
        # Currently this calls the wrong hud as its done before the hud is set
        self.completed = 0
        self.debug = debug

        # for running the game in test mode (when testing a level)
        if self.debug:
            # Push the level down since we have hud at the top
            spacing = (1.5, 1.5)
            self.hud = PreviewHud(self, spacing)
        else:
            spacing = (1.5, 1.2)
            self.hud = GameHud(self, spacing)

        self.gridLayer4 = Layer(self, (
            self.allSprites, self.layer4), 4, level, spacing)
        self.gridLayer3 = Layer(self, (
            self.allSprites, self.layer3, self.layer4), 3, level, spacing)
        self.gridLayer2 = Layer(self, (
            self.allSprites, self.layer2, self.layer4), 2, level, spacing)
        self.gridLayer1 = Layer(self, (
            self.allSprites, self.layer1, self.layer4), 1, level, spacing)

        # Set the name of the level
        self.level = self.gridLayer4.getGrid().getLevelName()

        # Set the board scale
        self.gridLayer4.getGrid().setBoardScale()

        # Set the level data
        self.levelData = self.gridLayer4.getGrid().getMap()

        # we want to get which connectionTypes are available in the map
        for connectionType in self.levelData['connections']:
            self.connectionTypes.append(connectionType)

        # Ordering of the layers (first = lowest).
        self.gridLayer1.createGrid()
        self.gridLayer2.createGrid()
        self.gridLayer3.createGrid()
        self.setGridLayer4Lines()

        # Remove node duplicates before we add the transport so that below
        # indicators are rendered below the transport.
        self.removeDuplicates()

        # Add the different transports to the different layers.
        self.gridLayer1.grid.loadTransport("layer 1")
        self.gridLayer2.grid.loadTransport("layer 2")
        self.gridLayer3.grid.loadTransport("layer 3")

        # Set all the destinations to be the destinations from all layers.
        layer1Destinations = self.gridLayer1.getGrid().getDestinations()
        layer2Destinations = self.gridLayer2.getGrid().getDestinations()
        layer3Destinations = self.gridLayer3.getGrid().getDestinations()
        self.allDestinations = (
            layer1Destinations + layer2Destinations + layer3Destinations)

        # Set number of people to complete level.
        if "total" not in self.levelData:
            # The minimum amount required for any given level.
            minAmount = 3

            # Scale with the difficulty.
            self.totalToComplete = random.randint(
                minAmount * self.levelData["difficulty"],
                5 * self.levelData["difficulty"])

        else:
            self.totalToComplete = self.levelData["total"]

        # Set the lives
        self.lives = (
            DEFAULTLIVES if checkKeyExist(self.levelData, ['options', 'lives'])
            else None)

        self.meter = MeterController(
            self, self.allSprites, self.slowDownMeterAmount)

        if 'tutorial' in self.levelData:
            self.tutorialManager = TutorialManager(
                self, self.allSprites, self.levelData['tutorial'])

        self.setDarkMode()

        # If there is more than one layer we want to be able
        # to see 'all' layers at once (layer 4)
        # otherwise we only need to see the single layer
        if len(self.connectionTypes) > 1 or self.debug:
            self.connectionTypes.append("layer 4")

        else:
            self.showLayer(
                self.getGridLayer(self.connectionTypes[0]).getNumber())

    # Draw the level to a surface and return this surface for blitting (image)
    # (i.e for maps on the level selection screen)
    def createLevelSurface(self, level):
        self.clearLevel()
        self.startingFixedScale = -0.2

        spacings = {
            (16, 9): (3.5, 2),
            (18, 10): (4, 2.5),
            (20, 11): (4.5, 2.8),
            (22, 12): (5, 3)}

        self.gridLayer4 = Layer(self, (), 4, level)

        # Set the board scale
        self.gridLayer4.getGrid().setBoardScale()

        # Work out the spacing of the map for use in the other layers
        levelData = self.gridLayer4.getGrid().getMap()
        size = (levelData["width"], levelData["height"])
        spacing = spacings[size]

        self.gridLayer3 = Layer(self, (), 3, level, spacing)
        self.gridLayer2 = Layer(self, (), 2, level, spacing)
        self.gridLayer1 = Layer(self, (), 1, level, spacing)

        # Grid ordering
        self.gridLayer3.createGrid()
        self.gridLayer1.createGrid()
        self.gridLayer2.createGrid()

        self.gridLayer1.grid.loadTransport("layer 1", False)
        self.gridLayer2.grid.loadTransport("layer 2", False)
        self.gridLayer3.grid.loadTransport("layer 3", False)

        # Set the lines from all layers
        self.gridLayer4.setLayerLines(
            self.gridLayer1, self.gridLayer2, self.gridLayer3, True)

        return self.gridLayer4.getLineSurface()

    # Create a new surface when the game is paused with all the sprites
    # currently in the game, so these don't have to be drawn every frame
    # (as they are not moving)
    def createPausedSurface(self):
        if not self.rendering or not self.game.paused:
            return

        self.pausedSurface = pygame.Surface((
            int(config["graphics"]["displayWidth"]
                * self.game.renderer.getScale()),
            int(config["graphics"]["displayHeight"]
                * self.game.renderer.getScale()))).convert()

        self.pausedSurface.blit(self.getGridLayer().getLineSurface(), (0, 0))

        for entity in self.belowEntities:
            entity.drawPaused(self.pausedSurface)

        self.renderPausedLayer(1, self.layer1)
        self.renderPausedLayer(2, self.layer2)
        self.renderPausedLayer(3, self.layer3)
        self.renderPausedLayer(4, self.layer4)

        for entity in self.aboveEntities:
            entity.drawPaused(self.pausedSurface)

        # for component in (
        #     self.hud.getComponents()
        #         + self.messageSystem.getComponents()):
        #     # draw hud and message system
        #     component.drawPaused(self.pausedSurface)

        return self.pausedSurface

    def connectionTypeTranslations(self, connectionType=None, layers=[]):
        if len(layers) < 4 or len(layers) > 4:
            return

        connectionType = (
            self.currentLayer if connectionType is None else connectionType)

        if connectionType == "layer 1" or connectionType == 1:
            return layers[0]
        elif connectionType == "layer 2" or connectionType == 2:
            return layers[1]
        elif connectionType == "layer 3" or connectionType == 3:
            return layers[2]
        elif connectionType == "layer 4" or connectionType == 4:
            return layers[3]

    def getSpriteLayer(self, connectionType=None):
        return self.connectionTypeTranslations(connectionType, [
            self.layer1, self.layer2, self.layer3, self.layer4])

    def getGridLayer(self, connectionType=None):
        return self.connectionTypeTranslations(connectionType, [
            self.gridLayer1, self.gridLayer2, self.gridLayer3,
            self.gridLayer4])

    def getLayerName(self, connectionType=None):
        return self.connectionTypeTranslations(connectionType, LAYERNAMES)

    @staticmethod
    def sortNodes(nodes):
        nodes = sorted(
            nodes, key=lambda x: x.getType() == NodeType.SPECIAL,
            reverse=True)
        nodes = sorted(
            nodes, key=lambda x: x.getType() == NodeType.STOP,
            reverse=True)
        nodes = sorted(
            nodes, key=lambda x: x.getType() == NodeType.DESTINATION,
            reverse=True)
        return nodes

    def getNode(self, n, allNodes=None, returnNode=None):
        allNodes = self.getAllNodes() if allNodes is None else allNodes
        for node in allNodes:
            if node.getNumber() == n:
                return node
        return returnNode

    # Return all the nodes from all layers in the spriterenderer
    def getAllNodes(self):
        layer1Nodes = self.gridLayer1.getGrid().getNodes()
        layer2Nodes = self.gridLayer2.getGrid().getNodes()
        layer3Nodes = self.gridLayer3.getGrid().getNodes()
        return layer3Nodes + layer2Nodes + layer1Nodes

    # Return all the transports from all layers in the spriterenderer
    def getAllTransports(self):
        layer1Transports = self.gridLayer1.getGrid().getTransports()
        layer2Transports = self.gridLayer2.getGrid().getTransports()
        layer3Transports = self.gridLayer3.getGrid().getTransports()
        return layer1Transports + layer2Transports + layer3Transports

    # Return all the current people on a given level
    # Don't need to pass the layers as this will not be called in level select
    def getAllPeople(self):
        layer1People = self.gridLayer1.getPeople()
        layer2People = self.gridLayer2.getPeople()
        layer3People = self.gridLayer3.getPeople()
        return layer1People + layer2People + layer3People

    # Remove duplicate nodes on layer 4 for layering
    def removeDuplicates(
            self, allNodes=None, removeLayer=None, addIndicator=True):
        seen = {}
        removeLayer = self.layer4 if removeLayer is None else removeLayer

        if allNodes is None:
            allNodes = self.getAllNodes()

        # Put any node that is not a regular node at the front of the list,
        # so they are not removed and the regular node is
        allNodes = SpriteRenderer.sortNodes(allNodes)

        for node in allNodes:
            if node.getNumber() not in seen:
                seen[node.getNumber()] = node
            else:
                if addIndicator:
                    node.addBelowNode(seen[node.getNumber()])
                    seen[node.getNumber()].addAboveNode(node)
                removeLayer.remove(node)

    # if there is a node above the given node,
    # return the highest node, else return node
    def getTopNode(self, bottomNode):
        return self.getNode(
            bottomNode.getNumber(),
            SpriteRenderer.sortNodes(self.getAllNodes()), bottomNode)

    # if there is an equivelant node on a different layer, return it,
    # else return none (no node)
    def getNodeFromDifferentLayer(self, currentNode, differentLayer):
        layer = self.getGridLayer(differentLayer)
        return self.getNode(
            currentNode.getNumber(), layer.getGrid().getNodes())

    def checkKeyPress(self, key, pressed, spaceBar, speedUp):
        if (pygame.key.get_pressed()[key] == pressed
                and self.game.clickManager.getSpaceBar() == spaceBar
                and self.game.clickManager.getSpeedUp() == speedUp):
            return True
        return False

    def events(self):
        slowDownKey = config["controls"]["slowdown"]["current"]
        speedUpKey = config["controls"]["fastforward"]["current"]

        if self.checkKeyPress(slowDownKey, True, False, False):
            self.game.clickManager.setSpaceBar(True)
            self.game.audioLoader.slowDownMusic()

        elif self.checkKeyPress(slowDownKey, False, True, False):
            self.game.clickManager.setSpaceBar(False)
            self.game.audioLoader.restoreMusic(slowDown=True)

        elif (self.checkKeyPress(speedUpKey, True, False, False)
                and not self.hud.fastForward.clicked):
            self.game.clickManager.setSpeedUp(True)
            self.game.audioLoader.speedUpMusic()
            self.hud.toggleFastForward(True)

        elif (self.checkKeyPress(speedUpKey, False, False, True)
                and not self.hud.fastForward.clicked):
            self.game.clickManager.setSpeedUp(False)
            self.game.audioLoader.restoreMusic(speedUp=True)
            self.hud.toggleFastForward()

    def update(self):
        # If we're not rendering, do nothing
        if not self.rendering:
            return

        # If we're rendering but paused, we still want to update the sprites
        # so that we can still hover over them, draw destination etc.
        self.allSprites.update()
        self.hud.update()
        self.messageSystem.update()
        self.menu.update()

        # TODO: Update the managers here???????????????????

        # If the game is paused or the main main is open (splash screen)
        # then we don't want to allow interaction.
        if self.paused or self.game.mainMenu.getOpen():
            return

        self.events()
        self.timer += self.game.dt * self.dt

        # Always spawn a person if there is no people left on the map,
        # to stop player having to wait
        if (self.timer > self.timeStep
                and not checkKeyExist(
                    self.levelData, ['options', 'limitPeople'])):
            self.timer = 0
            self.gridLayer2.createPerson(self.allDestinations)

        if self.totalPeople <= 0:
            if not self.totalPeopleNone:
                self.timer = 0
                self.totalPeopleNone = True

            # wait 2 seconds before spawing the next
            # person when there is no people left
            if self.timer > 2 and self.totalPeopleNone:
                self.timer = 0
                self.gridLayer2.createPerson(self.allDestinations)
                self.totalPeopleNone = False

    def showLayer(self, layer):
        if (not self.rendering
                or f"layer {str(layer)}" not in self.connectionTypes):
            return

        self.currentLayer = layer
        self.game.clickManager.resetMouseOver()

        # Redraw the nodes so that the mouse cant collide with them
        for node in self.getAllNodes():
            node.dirty = True

        self.hud.updateLayerText()

    # TODO: If a layer has any images, they must be resized here
    def resize(self):
        if not self.rendering:
            return

        self.gridLayer1.resize()
        self.gridLayer2.resize()
        self.gridLayer3.resize()
        self.gridLayer4.resize()

        # We want to reset the layer 4 lines with the
        # new ones (resized) from the other layers
        self.setGridLayer4Lines()

        # resize huds and menus
        self.hud.resize()
        self.menu.resize()
        self.messageSystem.resize()

        for sprite in self.allSprites:
            sprite.dirty = True

        self.createPausedSurface()

    # Draw all the sprites in a layer, based on what layer the player
    # is currently on
    def renderLayer(self, layerInt, gridLayer, group):
        if self.currentLayer != layerInt:
            return

        # First we draw the layer surface including the background
        # color and lines.
        gridLayer.draw()

        # Draw all sprites on top of the background and lines
        # (including nodes).
        for sprite in group:
            sprite.draw()

    # Draw all sprites to the paused surface, based on what layer the player
    # is currently on
    def renderPausedLayer(self, layerInt, group):
        if self.currentLayer == layerInt:
            for sprite in group:
                sprite.drawPaused(self.pausedSurface)

    def render(self):
        if not self.rendering:
            return

        if not self.game.paused:
            # Entities drawn below the other sprites.
            for entity in self.belowEntities:
                entity.draw()

            self.renderLayer(1, self.gridLayer1, self.layer1)
            self.renderLayer(2, self.gridLayer2, self.layer2)
            self.renderLayer(3, self.gridLayer3, self.layer3)
            self.renderLayer(4, self.gridLayer4, self.layer4)

            # Entities drawn above all the other sprites.
            for entity in self.aboveEntities:
                entity.draw()

        # When the game is paused, we blit the map as a single surface
        # for better performance.
        else:
            if hasattr(self, 'pausedSurface'):
                self.game.renderer.addSurface(
                    self.pausedSurface, (self.pausedSurface.get_rect()))

        # Don't show any hud elements on the splash screen
        if not self.game.mainMenu.getOpen():
            self.hud.display()
            self.messageSystem.display()
            self.menu.display()
