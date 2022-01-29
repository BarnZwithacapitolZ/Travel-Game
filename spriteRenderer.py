import pygame
import random
from config import config, dump, DEFAULTLIVES, DEFAULTBACKGROUND, LAYERNAMES
from layer import Layer
from clickManager import (
    PersonClickManager, TransportClickManager, PersonHolderClickManager)
from node import NodeType
from meterController import MeterController
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
        self.startingFixedScale = 0
        self.paused = False  # Individual pause for the levels

        self.setDefaultMap()

        self.totalPeople, self.completed, self.totalToComplete = 0, 0, 0
        self.totalPeopleNone = False
        self.slowDownMeterAmount = 75

        self.debug = False
        self.darkMode = False

        # The connection types availabe on the map (always has layer 4)
        self.connectionTypes = ["layer 4"]

    def setDefaultMap(self):
        self.levelData = {
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

    # Save function, for when the level has already
    # been created before (and is being edited)
    def saveLevel(self):
        self.game.mapLoader.saveMap(self.levelData["mapName"], self.levelData)

    def setRendering(self, rendering, transition=False):
        self.rendering = rendering
        self.hud.main(transition) if self.rendering else self.hud.close()

        if self.rendering:
            self.messageSystem.main()
        else:
            self.messageSystem.close()

        # Create the paused surface when first rendering
        self.createPausedSurface()

    def runStartScreen(self):
        if self.rendering and not self.debug:
            self.menu.startScreen()

    def runEndScreen(self, completed=False):
        if self.rendering and not self.debug:
            if completed:
                self.menu.endScreenComplete(True)  # Run with transition
            else:
                self.menu.endScreenGameOver(True)  # Run with transition

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

    def setStartingFixedScale(self, startingFixedScale):
        self.startingFixedScale = startingFixedScale

    def setDebug(self, debug):
        self.debug = debug

    def setDarkMode(self):
        if ("backgrounds" in self.levelData and
            "darkMode" in self.levelData["backgrounds"]
                and self.levelData["backgrounds"]["darkMode"]):
            self.darkMode = True

        else:
            self.darkMode = False

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
        self.totalPeopleNone = False
        self.belowEntities.empty()
        self.aboveEntities.empty()
        self.allSprites.empty()
        self.layer1.empty()
        self.layer2.empty()
        self.layer3.empty()
        self.layer4.empty()

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

        self.gridLayer4 = Layer(self, (self.allSprites, self.layer4), 4, level)
        self.gridLayer3 = Layer(self, (
            self.allSprites, self.layer3, self.layer4), 3, level)
        self.gridLayer2 = Layer(self, (
            self.allSprites, self.layer2, self.layer4), 2, level)
        self.gridLayer1 = Layer(self, (
            self.allSprites, self.layer1, self.layer4), 1, level)

        # Set the name of the level
        self.level = self.gridLayer4.getGrid().getLevelName()

        # Set the level data
        self.levelData = self.gridLayer4.getGrid().getMap()

        # for running the game in test mode (when testing a level)
        if self.debug:
            # Push the level down since we have hud at the top
            spacing = (1.5, 1.5)
            self.hud = PreviewHud(self, spacing)
        else:
            spacing = (1.5, 1)
            self.hud = GameHud(self, spacing)

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

        # Set number of people to complete level
        if "total" not in self.levelData:
            self.totalToComplete = random.randint(8, 12)

        else:
            self.totalToComplete = self.levelData["total"]

        # Set the lives
        if ("options" in self.levelData
                and "lives" in self.levelData["options"]):
            self.lives = (
                DEFAULTLIVES if self.levelData["options"]["lives"] else None)

        else:
            self.lives = DEFAULTLIVES

        self.meter = MeterController(
            self, self.allSprites, self.slowDownMeterAmount)
        self.setDarkMode()

        # If there is more than one layer we want to be able
        # to see 'all' layers at once (layer 4)
        # otherwise we only need to see the single layer
        if len(self.connectionTypes) > 1 or self.debug:
            self.connectionTypes.append("layer 4")

        else:
            self.showLayer(
                self.getGridLayer(self.connectionTypes[0]).getNumber())

    # Draw the level to a surface and return this surface for blitting
    # (i.e for maps on the level selection screen)
    def createLevelSurface(self, level):
        self.clearLevel()
        self.startingFixedScale = -0.2

        spacings = {
            (16, 9): (3.5, 2),
            (18, 10): (4, 2.5),
            (20, 11): (4.5, 2.8),
            (22, 12): (5, 3)}

        gridLayer4 = Layer(self, (), 4, level)

        # Work out the spacing of the map for use in the other layers
        levelData = gridLayer4.getGrid().getMap()
        size = (levelData["width"], levelData["height"])
        spacing = spacings[size]

        gridLayer3 = Layer(self, (), 3, level, spacing)
        gridLayer2 = Layer(self, (), 2, level, spacing)
        gridLayer1 = Layer(self, (), 1, level, spacing)

        # Grid ordering
        gridLayer3.createGrid()
        gridLayer1.createGrid()
        gridLayer2.createGrid()
        # Set the lines from all layers
        gridLayer4.setLayerLines(gridLayer1, gridLayer2, gridLayer3, True)

        # TODO add transports to line surface
        # gridLayer1.grid.loadTransport("layer 1", False)
        # gridLayer2.grid.loadTransport("layer 2", False)
        # gridLayer3.grid.loadTransport("layer 3", False)

        return gridLayer4.getLineSurface()

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

    # Get all the nodes from all layers in the spriterenderer
    def getAllNodes(self, layer1, layer2, layer3):
        layer1Nodes = layer1.getGrid().getNodes()
        layer2Nodes = layer2.getGrid().getNodes()
        layer3Nodes = layer3.getGrid().getNodes()
        allNodes = layer3Nodes + layer2Nodes + layer1Nodes

        return allNodes

    def getNode(self, node, sortNodes=False):
        layer1Node = [self.gridLayer1.getGrid().getNode(node)]
        layer2Node = [self.gridLayer2.getGrid().getNode(node)]
        layer3Node = [self.gridLayer3.getGrid().getNode(node)]
        allNodes = layer3Node + layer2Node + layer1Node
        allNodes = list(filter(lambda x: x is not None, allNodes))

        return allNodes

    # Remove duplicate nodes on layer 4 for layering
    def removeDuplicates(
            self, allNodes=None, removeLayer=None, addIndicator=True):
        seen = {}
        removeLayer = self.layer4 if removeLayer is None else removeLayer

        if allNodes is None:
            allNodes = self.getAllNodes(
                self.gridLayer1, self.gridLayer2, self.gridLayer3)

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
        allNodes = self.getAllNodes(
            self.gridLayer1, self.gridLayer2, self.gridLayer3)
        allNodes = SpriteRenderer.sortNodes(allNodes)

        for node in allNodes:
            if node.getNumber() == bottomNode.getNumber():
                return node

        return bottomNode

    # if there is an equivelant node on a different layer, return it,
    # else return none (no node)
    def getNodeFromDifferentLayer(self, currentNode, differentLayer):
        layer = self.getGridLayer(differentLayer)

        for node in layer.getGrid().getNodes():
            if node.getNumber() == currentNode.getNumber():
                return node
        return None

    def events(self):
        if pygame.key.get_pressed()[config["controls"]["slowdown"]["current"]]:
            self.game.clickManager.setSpaceBar(True)

            if (
                self.dt != self.startDt - self.meter.getSlowDownAmount()
                    and not self.meter.getEmpty()):
                # TODO: we want to slow down the game music here instead
                self.game.audioLoader.playSound("slowIn", 1)

        elif pygame.key.get_pressed()[
                config["controls"]["fastforward"]["current"]]:
            self.game.clickManager.setSpeedUp(True)

            if self.dt != self.startDt + self.meter.getSpeedUpAmount():
                self.hud.toggleFastForward(True)

        else:
            if self.dt < self.startDt:
                # TODO: we want to spped up the game music here instead
                self.game.audioLoader.playSound("slowOut", 1)
            elif self.dt > self.startDt:
                self.hud.toggleFastForward()

            self.game.clickManager.setSpaceBar(False)
            self.game.clickManager.setSpeedUp(False)

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

        if self.paused:
            return

        self.events()
        self.timer += self.game.dt * self.dt

        # Always spawn a person if there is no people left on the map,
        # to stop player having to wait
        if self.timer > self.timeStep:
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
                or "layer " + str(layer) not in self.connectionTypes):
            return

        self.currentLayer = layer
        self.game.clickManager.resetMouseOver()

        # Redraw the nodes so that the mouse cant collide with them
        for node in self.getAllNodes(
                self.gridLayer1, self.gridLayer2, self.gridLayer3):
            node.dirty = True

        self.hud.updateLayerText()

    # TODO: If a layer has any images, they must be resized here
    def resize(self):
        if not self.rendering:
            return

        self.gridLayer1.resize()
        self.gridLayer2.resize()
        self.gridLayer3.resize()
        # Only need to do this if it has components
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
        if self.currentLayer == layerInt:
            gridLayer.draw()
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

        else:
            if hasattr(self, 'pausedSurface'):
                self.game.renderer.addSurface(
                    self.pausedSurface, (self.pausedSurface.get_rect()))

        self.hud.display()
        self.messageSystem.display()
        self.menu.display()
