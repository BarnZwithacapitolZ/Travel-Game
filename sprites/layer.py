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

class Layer(pygame.sprite.Sprite):
    def __init__(self, spriteRenderer, groups, level = None, spacing = (1.5, 1.5)):
        self.groups = groups
        #layer added to sprite group first
        super().__init__(self.groups)
        self.spriteRenderer = spriteRenderer
        self.game = self.spriteRenderer.game
        self.level = level
   
        self.grid = GridManager(self, self.groups, self.level, spacing) # each layer has its own grid manager
        
        self.nodes = self.grid.getNodes()
        self.connections = self.grid.getConnections()

        self.components = []


    #### Getters ####
    
    # Get the grid of the layer
    def getGrid(self):
        return self.grid

    def getSpriteRenderer(self):
        return self.spriteRenderer


    #### Setters ####

    # Add a component to the layer
    def addComponent(self, component):
        self.components.append(component)


    # Add the connections to each of the nodes in each connection, given a set of connections
    def addConnections(self, connections = None):
        if connections is None:
            connections = self.connections

        for connection in connections:
            connection.getFrom().addConnection(connection)

    
    def removeConnections(self, connections = None):
        if connections is None:
            connections = self.connections

        for connection in connections:
            connection.getFrom().removeConnection(connection)


    # Add a person to the layer
    def addPerson(self, destinations = None):
        # No nodes in the layer to add the person to, or no entrances for person to come from
        if len(self.nodes) <= 0 or len(self.grid.getEntrances()) <= 0:
            return 

        if destinations == None:
            destinations = self.grid.getDestinations() 

        # Add the person to a random node on the layer
        node = random.randint(0, len(self.grid.getEntrances()) - 1)
        currentNode = self.grid.getEntrances()[node]

        peopleTypes = [Manager, Commuter]
        person = random.randint(0, len(peopleTypes) - 1)

        p = peopleTypes[person](self.spriteRenderer, self.groups, currentNode, self.spriteRenderer.getPersonClickManager(), self.spriteRenderer.getTransportClickManager())
        p.setDestination(destinations)

        # Put the player at a position outside of the map
        p.addToPath(currentNode.getConnections()[0].getTo())
        return p

    
    # Create the connections by drawing them to the screen
    def createConnections(self):
        for connection in self.connections:
            if connection.getDirection() == Connection.Direction.FORWARDS: # From node
                self.drawConnection(connection.getColor(), connection.getFrom(), connection.getTo(), 10, 10)

                if connection.getSideColor() is not None:
                    self.drawConnection(connection.getSideColor(), connection.getFrom(), connection.getTo(), 3, 6)
                    self.drawConnection(connection.getSideColor(), connection.getFrom(), connection.getTo(), 3, 14)


    # THESE DONT NEED TO BE DRAWN EACH FRAME, BLIT TO A SURFACE AND JUST DRAW THAT SURFACE
    # Draw a connection to the screen
    def drawConnection(self, color, fromNode, toNode, thickness, offset):
        scale = self.game.renderer.getScale() * self.spriteRenderer.getFixedScale()
        dxy = (fromNode.pos - fromNode.offset) - (toNode.pos - toNode.offset)

        if dxy.x != 0 and dxy.y != 0:
            posx = ((fromNode.pos - fromNode.offset) + vec(offset, 10)) * scale
            posy = ((toNode.pos - toNode.offset) + vec(offset, 10)) * scale
        else:
            posx = ((fromNode.pos - fromNode.offset) + vec(offset, offset)) * scale
            posy = ((toNode.pos - toNode.offset) + vec(offset, offset)) * scale
        
        pygame.draw.line(self.game.renderer.gameDisplay, color, posx, posy, int(thickness * scale))


    def resize(self):
        for component in self.components:
            component.dirty = True


    def draw(self):
        for component in self.components:
            component.draw()

        # does not need to be drawn each and every frame
        self.createConnections()



class Layer1(Layer):
    def __init__(self, spriteRenderer, groups, level, spacing = (1.5, 1)):
        super().__init__(spriteRenderer, groups, level, spacing)
        self.grid.createGrid("layer 1")
        self.addConnections()  


class Layer2(Layer):
    def __init__(self, spriteRenderer, groups, level, spacing = (1.5, 1)):
        super().__init__(spriteRenderer, groups, level, spacing)
        self.grid.createGrid("layer 2")
        self.addConnections()     



class Layer3(Layer):
    def __init__(self, spriteRenderer, groups, level, spacing = (1.5, 1)):
        super().__init__(spriteRenderer, groups, level, spacing)
        self.grid.createGrid("layer 3")
        self.addConnections()            



class Layer4(Layer):
    def __init__(self, spriteRenderer, groups, level):
        super().__init__(spriteRenderer, groups, level)
        background = Background(self.game, "river", (600, 250), (config["graphics"]["displayWidth"] - 600, config["graphics"]["displayHeight"] - 250))
        self.addComponent(background)



class EditorLayer1(Layer):
    def __init__(self, spriteRenderer, groups, level = None):
        super().__init__(spriteRenderer, groups, level)
        self.grid.createFullGrid("layer 1")
        self.addConnections()



class EditorLayer2(Layer):
    def __init__(self, spriteRenderer, groups, level = None):
        super().__init__(spriteRenderer, groups, level)
        self.grid.createFullGrid("layer 2")
        self.addConnections()


class EditorLayer3(Layer):
    def __init__(self, spriteRenderer, groups, level = None):
        super().__init__(spriteRenderer, groups, level)
        self.grid.createFullGrid("layer 3")
        self.addConnections()


class EditorLayer4(Layer):
    def __init__(self, spriteRenderer, groups, level = None):
        super().__init__(spriteRenderer, groups, level)



    
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

        self.image = self.game.imageLoader.getImage(self.imageName)
        self.image = pygame.transform.smoothscale(self.image, (int(self.width * self.game.renderer.getScale()), 
                                                            int(self.height * self.game.renderer.getScale())))
        self.rect = self.image.get_rect()
        self.rect.x = self.x * self.game.renderer.getScale()
        self.rect.y = self.y * self.game.renderer.getScale()


    def draw(self):
        if self.dirty or self.image is None: self.__render()
        self.game.renderer.gameDisplay.blit(self.image, self.rect)