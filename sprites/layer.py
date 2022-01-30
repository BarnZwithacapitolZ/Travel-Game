import pygame
import pygame.gfxdraw
import random
import math
from config import config, DEFAULTBACKGROUND
from utils import vec
from gridManager import GridManager
from person import Person, Manager, Commuter


class Layer:
    def __init__(
            self, spriteRenderer, groups, number, level=None,
            spacing=(1.5, 1.5)):
        self.groups = groups

        # Layer added to sprite group first
        # super().__init__(self.groups)

        self.spriteRenderer = spriteRenderer
        self.game = self.spriteRenderer.game
        self.number = number
        self.connectionType = "layer " + str(number)
        self.level = level

        # each layer has its own grid manager
        self.grid = GridManager(self, self.groups, self.level, spacing)

        self.components = []
        self.lines = []
        self.tempLines = []
        self.previousPeopleTypes = []
        self.people = []

        self.loadBackgroundColor(DEFAULTBACKGROUND)

        self.createLineSurface()

    def createLineSurface(self):
        self.lineSurface = pygame.Surface((
            int(config["graphics"]["displayWidth"]
                * self.game.renderer.getScale()),
            int(config["graphics"]["displayHeight"]
                * self.game.renderer.getScale()))).convert()

    def createGrid(self, full=False):
        (self.grid.createFullGrid(self.connectionType) if full
            else self.grid.createGrid(self.connectionType))
        self.addConnections()
        self.createConnections()

    # Get the grid of the layer
    def getGrid(self):
        return self.grid

    def getSpriteRenderer(self):
        return self.spriteRenderer

    def getLines(self):
        return self.lines

    def getTempLines(self):
        return self.tempLines

    def getLineSurface(self):
        if hasattr(self, 'lineSurface'):
            return self.lineSurface

    def getNumber(self):
        return self.number

    def getPeople(self):
        return self.people

    def setLines(self, lines):
        self.lines = lines

    def setLayerLines(self, layer1, layer2, layer3, removeDuplicates=False):
        lines = layer1.getLines() + layer2.getLines() + layer3.getLines()
        nodes = None

        if removeDuplicates:
            nodes = self.spriteRenderer.getAllNodes(layer1, layer2, layer3)
            self.spriteRenderer.removeDuplicates(nodes, nodes, False)

        self.lines = lines
        self.render(nodes)

    def setLayerTempLines(self, layer1, layer2, layer3):
        lines = (
            layer1.getTempLines() + layer2.getTempLines()
            + layer3.getTempLines())
        self.tempLines = lines
        self.render()

    def addPerson(self, person):
        if person in self.people:
            return

        self.people.append(person)

    def removePerson(self, person):
        if person not in self.people:
            return

        self.people.remove(person)

    # Add a component to the layer
    def addComponent(self, component):
        self.components.append(component)

    # Add the connections to each of the nodes in each connection,
    # given a set of connections
    def addConnections(self, connections=None):
        if connections is None:
            connections = self.grid.getConnections()

        for connection in connections:
            connection.getFrom().addConnection(connection)

    def removeConnections(self, connections=None):
        if connections is None:
            connections = self.grid.getConnections()

        for connection in connections:
            connection.getFrom().removeConnection(connection)
        self.grid.removeConnections(connections)

    def addTempConnections(self, connections):
        for connection in connections:
            connection.getFrom().addConnection(connection)

    def removeAllTempConnections(self):
        for connection in self.grid.getTempConnections():
            connection.getFrom().removeConnection(connection)
        self.grid.removeTempConnections()

    # Add a person to the layer
    def createPerson(self, destinations=None):
        # No nodes in the layer to add the person to, or no entrances
        # for person to come from
        destinations = (
            destinations if destinations is not None
            else self.grid.getDestinations())

        if len(self.grid.getNodes()) <= 0 or len(destinations) <= 0:
            return

        peopleTypes = [Manager, Commuter]
        peopleTypes, weights = Person.checkPeopleTypes(
            peopleTypes, self.previousPeopleTypes, destinations)

        # no people can spawn, return
        if len(peopleTypes) <= 0 or len(weights) <= 0:
            return

        picks = [v for v, w in zip(peopleTypes, weights) for x in range(w)]

        p = random.choice(picks)(
            self.spriteRenderer, self.groups, destinations, [
                self.spriteRenderer.getPersonClickManager(),
                self.spriteRenderer.getTransportClickManager()])

        self.previousPeopleTypes.append(type(p))

        self.spriteRenderer.setTotalPeople(
            self.spriteRenderer.getTotalPeople() + 1)

        return p

    def createConnectionLines(self, connections, lines):
        if len(connections) <= 0:
            return

        for connection in connections:
            if connection.getDraw():
                # Center "main" line
                self.createLines(
                    lines, connection.getColor(), connection.getFrom(),
                    connection.getTo(), 10, 10)

                # Outer "border" lines
                if connection.getSideColor() is not None:
                    self.createLines(
                        lines, connection.getSideColor(),
                        connection.getFrom(), connection.getTo(), 3, 6)
                    self.createLines(
                        lines, connection.getSideColor(),
                        connection.getFrom(), connection.getTo(), 3, 14)

    # Create the connections by drawing them to the screen
    def createConnections(self, connections=None, reset=True):
        connections = (
            self.grid.getConnections()
            if connections is None else connections)

        if reset:
            self.lines = []

        self.createConnectionLines(connections, self.lines)
        self.render()

    def createTempConnections(self, connections=None, reset=True):
        connections = (
            self.grid.getTempConnections()
            if connections is None else connections)

        if reset:
            self.tempLines = []

        self.createConnectionLines(connections, self.tempLines)
        self.render()

    # Word out the x and y of each connection and append it to the list
    def createLines(self, lines, color, fromNode, toNode, thickness, offset):
        scale = (
            self.game.renderer.getScale()
            * self.spriteRenderer.getFixedScale())
        offxy = self.spriteRenderer.offset

        # change in direction
        dxy = (fromNode.pos - fromNode.offset) - (toNode.pos - toNode.offset)
        angle = math.atan2(dxy.x, dxy.y)
        angle = abs(math.degrees(angle))

        angleOffset = vec(offset, 10)
        if dxy.x != 0 and dxy.y != 0:
            if (angle > 140 and angle < 180) or (angle > 0 and angle < 40):
                angleOffset = vec(offset, 10)
            elif angle > 40 and angle < 140:
                angleOffset = vec(10, offset)

        # 90, 180
        else:
            angleOffset = vec(offset, offset)

        posx = ((fromNode.pos - fromNode.offset) + angleOffset + offxy) * scale
        posy = ((toNode.pos - toNode.offset) + angleOffset + offxy) * scale

        lines.append({
            "posx": posx,
            "posy": posy,
            "color": color,
            "thickness": thickness * scale
        })

    def resize(self):
        # resize all the layer components
        for component in self.components:
            component.dirty = True

        # Scale the line surface then draw the scaled lines to that surface
        self.createLineSurface()
        self.createConnections()

    def loadBackgroundColor(self, default):
        levelData = self.grid.getMap()

        if ("backgrounds" in levelData
                and self.connectionType in levelData["backgrounds"]):
            self.backgroundColor = (
                levelData["backgrounds"][self.connectionType])

        else:
            self.backgroundColor = default

    def render(self, nodes=None):
        self.lineSurface.fill(self.backgroundColor)

        if len(self.components) > 0:
            for component in self.components:
                component.draw(self.lineSurface)

        if len(self.lines + self.tempLines) > 0:
            for line in self.lines + self.tempLines:
                pygame.draw.line(
                    self.lineSurface, line["color"], line["posx"],
                    line["posy"], int(line["thickness"]))

        if nodes is not None:
            for node in nodes:
                # call the render function so there is an image to blit
                node.draw()
                self.lineSurface.blit(node.image, (node.rect))

    def draw(self):
        if len(self.lines + self.tempLines) > 0:
            self.game.renderer.gameDisplay.blit(self.lineSurface, (0, 0))

        # Case in mapEditor with 0 lines drawn,we can just draw a rect
        # instead of blitting an entier surface for better performance.
        else:
            pygame.draw.rect(
                self.game.renderer.gameDisplay, self.backgroundColor,
                (0, 0, config["graphics"]["displayWidth"]
                    * self.game.renderer.getScale(),
                    config["graphics"]["displayHeight"]
                    * self.game.renderer.getScale()))


class Background:
    def __init__(self, game, imageName, size=tuple(), pos=tuple()):
        self.game = game
        self.imageName = imageName

        self.width = size[0]
        self.height = size[1]
        self.x = pos[0]
        self.y = pos[1]

        self.dirty = True

    def __render(self):
        self.dirty = False
        self.image = self.game.imageLoader.getImage(
            self.imageName, (self.width, self.height))
        self.rect = self.image.get_rect()
        self.rect.x = self.x * self.game.renderer.getScale()
        self.rect.y = self.y * self.game.renderer.getScale()

    def draw(self, surface):
        if self.dirty or self.image is None:
            self.__render()

        surface.blit(self.image, self.rect)
