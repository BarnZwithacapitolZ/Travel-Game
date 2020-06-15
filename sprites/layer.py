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

class Layer(pygame.sprite.Sprite):
    def __init__(self, spriteRenderer, groups, level = None):
        self.groups = groups
        #layer added to sprite group first
        super().__init__(self.groups)
        self.spriteRenderer = spriteRenderer
        self.game = self.spriteRenderer.game
        self.level = level
   
        self.grid = GridManager(self.game, self.groups, self.level) # each layer has its own grid manager
        
        self.nodes = self.grid.getNodes()
        self.connections = self.grid.getConnections()

        self.components = []


    #### Getters ####
    
    # Get the grid of the layer
    def getGrid(self):
        return self.grid


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


    # Add a person to the layer
    def addPerson(self):
        # No nodes in the layer to add the person to
        if len(self.nodes) <= 0:
            return 

        # Add the person to a random node on the layer
        node = random.randint(0, len(self.nodes) - 1)
        p = Person(self.spriteRenderer, self.groups, self.nodes[node])

        # Add the person to a random node on the layer
        node = random.randint(0, len(self.nodes) - 1)
        p = Person(self.spriteRenderer, self.groups, self.nodes[node])
        return p

    
    # Create the connections by drawing them to the screen
    def createConnections(self):
        for connection in self.connections:
            if connection.getDirection() == Connection.Direction.FORWARDS: # From node
                self.drawConnection(connection.getColor(), connection.getFrom(), connection.getTo(), 10, 10)

                if connection.getSideColor() is not None:
                    self.drawConnection(connection.getSideColor(), connection.getFrom(), connection.getTo(), 3, 6)
                    self.drawConnection(connection.getSideColor(), connection.getFrom(), connection.getTo(), 3, 14)


    # Draw a connection to the screen
    def drawConnection(self, color, fromNode, toNode, thickness, offset):
        scale = self.game.renderer.getScale()
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
    def __init__(self, spriteRenderer, groups, level):
        super().__init__(spriteRenderer, groups, level)
        self.grid.createGrid("layer 1")
        self.addConnections()  


class Layer2(Layer):
    def __init__(self, spriteRenderer, groups, level):
        super().__init__(spriteRenderer, groups, level)
        self.grid.createGrid("layer 2")
        self.addConnections()     



class Layer3(Layer):
    def __init__(self, spriteRenderer, groups, level):
        super().__init__(spriteRenderer, groups, level)
        self.grid.createGrid("layer 3")
        self.addConnections()            



class Layer4(Layer):
    def __init__(self, spriteRenderer, groups, level):
        super().__init__(spriteRenderer, groups, level)
        background = Background(self.game, "river", (600, 250), (config["graphics"]["displayWidth"] - 600, config["graphics"]["displayHeight"] - 250))
        self.addComponent(background)



class EditorLayer1(Layer):
    def __init__(self, spriteRenderer, connectionManager, groups, level = None):
        super().__init__(spriteRenderer, groups, level)
        self.grid.createFullGrid("layer 1", connectionManager)
        self.addConnections()



class EditorLayer2(Layer):
    def __init__(self, spriteRenderer, connectionManager, groups, level = None):
        super().__init__(spriteRenderer, groups, level)
        self.grid.createFullGrid("layer 2", connectionManager)
        self.addConnections()



class EditorLayer3(Layer):
    def __init__(self, spriteRenderer, connectionManager, groups, level = None):
        super().__init__(spriteRenderer, groups, level)
        self.grid.createFullGrid("layer 3", connectionManager)
        self.addConnections()




class EditorLayer4(Layer):
    def __init__(self, spriteRenderer, connectionManager, groups, level = None):
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