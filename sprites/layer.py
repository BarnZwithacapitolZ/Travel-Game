import pygame
from pygame.locals import *
import pygame.gfxdraw
from config import *
import os
import random
import math

from gridManager import *
from connection import *
from person import *


vec = pygame.math.Vector2

class Layer():
    def __init__(self, spriteRenderer, groups, background, level = None, spacing = (1.5, 1.5)):
        self.groups = groups
        #layer added to sprite group first
        # super().__init__(self.groups)
        self.spriteRenderer = spriteRenderer
        self.game = self.spriteRenderer.game
        self.backgroundColor = background
        self.level = level
   
        self.grid = GridManager(self, self.groups, self.level, spacing) # each layer has its own grid manager

        self.components = []
        self.lines = []
        self.previousPeopleTypes = []


    #### Getters ####
    
    # Get the grid of the layer
    def getGrid(self):
        return self.grid

    def getSpriteRenderer(self):
        return self.spriteRenderer

    def getLines(self):
        return self.lines


    #### Setters ####

    def setLines(self, lines):
        self.lines = lines

    # Add a component to the layer
    def addComponent(self, component):
        self.components.append(component)


    # Add the connections to each of the nodes in each connection, given a set of connections
    def addConnections(self, connections = None):
        if connections is None:
            connections = self.grid.getConnections()

        for connection in connections:
            connection.getFrom().addConnection(connection)

    
    def removeConnections(self, connections = None):
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
    def addPerson(self, destinations = None):
        # No nodes in the layer to add the person to, or no entrances for person to come from
        destinations = destinations if destinations is not None else self.grid.getDestinations()

        if len(self.grid.getNodes()) <= 0 or len(destinations) <= 0:
            return 

        peopleTypes = [Manager, Commuter]
        peopleTypes, weights = Person.checkPeopleTypes(peopleTypes, self.previousPeopleTypes, destinations)
        picks = [v for v, w in zip(peopleTypes, weights) for x in range(w)]

        p = random.choice(picks)(self.spriteRenderer, self.groups, self.spriteRenderer.getPersonClickManager(), self.spriteRenderer.getTransportClickManager(), destinations)
        self.previousPeopleTypes.append(type(p))

        return p

    # Create the connections by drawing them to the screen
    def createConnections(self):
        connections = self.grid.getTempConnections() + self.grid.getConnections()
        self.lines = []
        for connection in connections:
            if connection.getDraw():
                self.createLines(connection.getColor(), connection.getFrom(), connection.getTo(), 10, 10)

                if connection.getSideColor() is not None:
                    self.createLines(connection.getSideColor(), connection.getFrom(), connection.getTo(), 3, 6)
                    self.createLines(connection.getSideColor(), connection.getFrom(), connection.getTo(), 3, 14)
        self.drawLines()


    # Word out the x and y of each connection and append it to the list
    def createLines(self, color, fromNode, toNode, thickness, offset):
        scale = self.game.renderer.getScale() * self.spriteRenderer.getFixedScale()
        dxy = (fromNode.pos - fromNode.offset) - (toNode.pos - toNode.offset) # change in direction
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
        for component in self.components:
            component.dirty = True
        self.createConnections()


    def drawLines(self):
        self.lineSurface = pygame.Surface((int(config["graphics"]["displayWidth"] * self.game.renderer.getScale()), 
                                            int(config["graphics"]["displayHeight"] * self.game.renderer.getScale()))).convert()
        self.lineSurface.fill(self.backgroundColor)

        for line in self.lines:
            pygame.draw.line(self.lineSurface, line["color"], line["posx"], line["posy"], int(line["thickness"]))


    def draw(self):
        for component in self.components:
            component.draw()

        # does not need to be drawn each and every frame
        # self.game.renderer.gameDisplay.lock()
        # for line in self.lines:
        #     pygame.draw.line(self.game.renderer.gameDisplay, line["color"], line["posx"], line["posy"], int(line["thickness"]))
        # self.game.renderer.addSurface(self.lineSurface, (0, 0))
        if len(self.lines) > 0:
            self.game.renderer.gameDisplay.blit(self.lineSurface, (0, 0))
        else:
            pygame.draw.rect(self.game.renderer.gameDisplay, self.backgroundColor, (0, 0, config["graphics"]["displayWidth"] * self.game.renderer.getScale(), config["graphics"]["displayHeight"] * self.game.renderer.getScale()))

        # self.game.renderer.gameDisplay.unlock()   



class Layer1(Layer):
    def __init__(self, spriteRenderer, groups,background, level, spacing = (1.5, 1)):
        super().__init__(spriteRenderer, groups, background, level, spacing)
        self.grid.createGrid("layer 1")
        self.addConnections()  
        self.createConnections()


class Layer2(Layer):
    def __init__(self, spriteRenderer, groups, background, level, spacing = (1.5, 1)):
        super().__init__(spriteRenderer, groups, background, level, spacing)
        self.grid.createGrid("layer 2")
        self.addConnections()     
        self.createConnections()


class Layer3(Layer):
    def __init__(self, spriteRenderer, groups, background, level, spacing = (1.5, 1)):
        super().__init__(spriteRenderer, groups, background, level, spacing)
        self.grid.createGrid("layer 3")
        self.addConnections()        
        self.createConnections()


class Layer4(Layer):
    def __init__(self, spriteRenderer, groups, background, level):
        super().__init__(spriteRenderer, groups, background, level)
        background = Background(self.game, "river", (600, 250), (config["graphics"]["displayWidth"] - 600, config["graphics"]["displayHeight"] - 250))
        # self.addComponent(background)
        # self.grid.createGrid("layer 3")
        # self.grid.createGrid("layer 1")
        # self.grid.createGrid("layer 2")
        # self.addConnections()        
        # self.createConnections()
        # self.drawLines()

    def resize(self):
        for component in self.components:
            component.dirty = True

        self.drawLines()


class EditorLayer1(Layer):
    def __init__(self, spriteRenderer, groups, background, level = None):
        super().__init__(spriteRenderer, groups, background, level)
        self.grid.createFullGrid("layer 1")
        self.addConnections()
        self.createConnections()


class EditorLayer2(Layer):
    def __init__(self, spriteRenderer, groups, background, level = None):
        super().__init__(spriteRenderer, groups, background, level)
        self.grid.createFullGrid("layer 2")
        self.addConnections()
        self.createConnections()


class EditorLayer3(Layer):
    def __init__(self, spriteRenderer, groups, background, level = None):
        super().__init__(spriteRenderer, groups, background, level)
        self.grid.createFullGrid("layer 3")
        self.addConnections()
        self.createConnections()


class EditorLayer4(Layer):
    def __init__(self, spriteRenderer, groups, background, level = None):
        super().__init__(spriteRenderer, groups, background, level)

    def resize(self):
        for component in self.components:
            component.dirty = True

        self.drawLines()

    
class Background():
    def __init__(self, game, imageName, size = tuple(), pos = tuple()):
        self.game = game
        self.imageName = imageName
        
        self.width = size[0]
        self.height = size[1]
        self.x = pos[0]
        self.y = pos[1]

        self.dirty = True

    def __render(self):
        self.dirty = False
        self.image = self.game.imageLoader.getImage(self.imageName, (self.width, self.height))
        self.rect = self.image.get_rect()
        self.rect.x = self.x * self.game.renderer.getScale()
        self.rect.y = self.y * self.game.renderer.getScale()


    def draw(self):
        if self.dirty or self.image is None: self.__render()
        self.game.renderer.gameDisplay.blit(self.image, self.rect)