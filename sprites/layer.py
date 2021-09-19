import pygame
import pygame.gfxdraw
import random
import math
from config import config, CREAM
from gridManager import GridManager
from person import Person, Manager, Commuter

vec = pygame.math.Vector2


class Layer():
    def __init__(
            self, spriteRenderer, groups, connectionType, level=None,
            spacing=(1.5, 1.5)):
        self.groups = groups

        # Layer added to sprite group first
        # super().__init__(self.groups)

        self.spriteRenderer = spriteRenderer
        self.game = self.spriteRenderer.game
        self.connectionType = connectionType
        self.level = level

        # each layer has its own grid manager
        self.grid = GridManager(self, self.groups, self.level, spacing)

        self.components = []
        self.lines = []
        self.previousPeopleTypes = []
        self.people = []

        self.number = 1

        self.loadBackgroundColor(CREAM)

    # Get the grid of the layer
    def getGrid(self):
        return self.grid

    def getSpriteRenderer(self):
        return self.spriteRenderer

    def getLines(self):
        return self.lines

    def getLineSurface(self):
        if hasattr(self, 'lineSurface'):
            return self.lineSurface

    def getNumber(self):
        return self.number

    def getPeople(self):
        return self.people

    def setLines(self, lines):
        self.lines = lines

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

    def addTempConnections(self, connections):
        for connection in connections:
            connection.getFrom().addConnection(connection)

    def removeTempConnections(self):
        for connection in self.grid.getTempConnections():
            connection.getFrom().removeConnection(connection)

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
            self.spriteRenderer, self.groups,
            self.spriteRenderer.getPersonClickManager(),
            self.spriteRenderer.getTransportClickManager(), destinations)

        self.previousPeopleTypes.append(type(p))

        self.spriteRenderer.setTotalPeople(
            self.spriteRenderer.getTotalPeople() + 1)

        return p

    # Create the connections by drawing them to the screen
    def createConnections(self, connections=None):
        connections = (
            self.grid.getTempConnections() + self.grid.getConnections()
            if connections is None else connections)
        self.lines = []

        for connection in connections:
            if connection.getDraw():
                # Center "main" line
                self.createLines(
                    connection.getColor(), connection.getFrom(),
                    connection.getTo(), 10, 10)

                # Outer "border" lines
                if connection.getSideColor() is not None:
                    self.createLines(
                        connection.getSideColor(), connection.getFrom(),
                        connection.getTo(), 3, 6)
                    self.createLines(
                        connection.getSideColor(), connection.getFrom(),
                        connection.getTo(), 3, 14)

        self.render()

    # Word out the x and y of each connection and append it to the list
    def createLines(self, color, fromNode, toNode, thickness, offset):
        scale = (
            self.game.renderer.getScale()
            * self.spriteRenderer.getFixedScale())

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

        posx = ((fromNode.pos - fromNode.offset) + angleOffset) * scale
        posy = ((toNode.pos - toNode.offset) + angleOffset) * scale

        self.lines.append({
            "posx": posx,
            "posy": posy,
            "color": color,
            "thickness": thickness * scale
        })

    def resize(self):
        # resize all the layer components
        for component in self.components:
            component.dirty = True
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
        self.lineSurface = pygame.Surface((
            int(config["graphics"]["displayWidth"]
                * self.game.renderer.getScale()),
            int(config["graphics"]["displayHeight"]
                * self.game.renderer.getScale()))).convert()

        self.lineSurface.fill(self.backgroundColor)

        for component in self.components:
            component.draw(self.lineSurface)

        for line in self.lines:
            pygame.draw.line(
                self.lineSurface, line["color"], line["posx"], line["posy"],
                int(line["thickness"]))

        if nodes is not None:
            for node in nodes:
                # call the render function so there is an image to blit
                node.draw()
                self.lineSurface.blit(node.image, (node.rect))

    def draw(self):
        if len(self.lines) > 0:
            self.game.renderer.gameDisplay.blit(self.lineSurface, (0, 0))

        else:
            pygame.draw.rect(
                self.game.renderer.gameDisplay, self.backgroundColor,
                (0, 0, config["graphics"]["displayWidth"]
                    * self.game.renderer.getScale(),
                    config["graphics"]["displayHeight"]
                    * self.game.renderer.getScale()))


class Layer1(Layer):
    def __init__(self, spriteRenderer, groups, level, spacing=(1.5, 1)):
        super().__init__(spriteRenderer, groups, "layer 1", level, spacing)
        self.number = 1
        self.grid.createGrid(self.connectionType)
        self.addConnections()
        self.createConnections()


class Layer2(Layer):
    def __init__(self, spriteRenderer, groups, level, spacing=(1.5, 1)):
        super().__init__(spriteRenderer, groups, "layer 2", level, spacing)
        self.number = 2
        self.grid.createGrid(self.connectionType)
        self.addConnections()
        self.createConnections()


class Layer3(Layer):
    def __init__(self, spriteRenderer, groups, level, spacing=(1.5, 1)):
        super().__init__(spriteRenderer, groups, "layer 3", level, spacing)
        self.number = 3
        self.grid.createGrid(self.connectionType)
        self.addConnections()
        self.createConnections()


class Layer4(Layer):
    def __init__(self, spriteRenderer, groups, level):
        super().__init__(spriteRenderer, groups, "layer 4", level)
        self.number = 4
        # background = Background(self.game, "river", (600, 250),
        # (config["graphics"]["displayWidth"] - 600,
        # config["graphics"]["displayHeight"] - 250))
        # self.addComponent(background)

    def addLayerLines(self, layer1, layer2, layer3):
        lines = layer1.getLines() + layer2.getLines() + layer3.getLines()
        self.lines = lines
        self.render()


class MenuLayer4(Layer):
    def __init__(self, spriteRenderer, groups, level):
        super().__init__(spriteRenderer, groups, "layer 4", level)
        # background = Background(self.game, "river", (600, 250),
        # (config["graphics"]["displayWidth"] - 600,
        # config["graphics"]["displayHeight"] - 250))
        # self.addComponent(background)

    def addLayerLines(self, layer1, layer2, layer3):
        lines = (
            layer1.getLines()
            + layer2.getLines()
            + layer3.getLines())
        nodes = (
            layer1.getGrid().getNodes()
            + layer2.getGrid().getNodes()
            + layer3.getGrid().getNodes())

        self.spriteRenderer.removeDuplicates(nodes, nodes)

        self.lines = lines
        self.render(nodes)


class EditorLayer1(Layer):
    def __init__(self, spriteRenderer, groups, level=None):
        super().__init__(spriteRenderer, groups, "layer 1", level)
        self.grid.createFullGrid(self.connectionType)
        self.addConnections()
        self.createConnections()


class EditorLayer2(Layer):
    def __init__(self, spriteRenderer, groups, level=None):
        super().__init__(spriteRenderer, groups, "layer 2", level)
        self.grid.createFullGrid(self.connectionType)
        self.addConnections()
        self.createConnections()


class EditorLayer3(Layer):
    def __init__(self, spriteRenderer, groups, level=None):
        super().__init__(spriteRenderer, groups, "layer 3", level)
        self.grid.createFullGrid(self.connectionType)
        self.addConnections()
        self.createConnections()


class EditorLayer4(Layer):
    def __init__(self, spriteRenderer, groups, level=None):
        super().__init__(spriteRenderer, groups, "layer 4", level)

    def addLayerLines(self, layer1, layer2, layer3):
        lines = layer1.getLines() + layer2.getLines() + layer3.getLines()
        self.lines = lines
        self.render()


class Background():
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
