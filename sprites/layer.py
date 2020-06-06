import pygame
from pygame.locals import *
import pygame.gfxdraw
from config import *
import os
import random
import math

from gridManager import *
from person import *

class Layer(pygame.sprite.Sprite):
    def __init__(self, spriteRenderer, groups):
        self.groups = groups
        #layer added to sprite group first
        pygame.sprite.Sprite.__init__(self, self.groups) 
        self.spriteRenderer = spriteRenderer
        self.game = self.spriteRenderer.game
   
        self.grid = GridManager(self.game, self.groups) # each layer has its own grid manager
        
        self.nodes = self.grid.getNodes()
        self.connections = self.grid.getConnections()

        self.components = []


    def addPerson(self):
        p = Person(self.spriteRenderer, self.groups, self.nodes[0])
        return p

    def addComponent(self, component):
        self.components.append(component)


    def addConnections(self):
        for connection in self.connections:
            connection.getFrom().addConnection(connection)


    def createConnections(self):
        for connection in self.connections:
            if connection.getDirection() == 0: # From node
                self.drawConnection(connection.color, connection.fromNode, connection.toNode, 10, 10)
                self.drawConnection(BLACK, connection.fromNode, connection.toNode, 3, 6)
                self.drawConnection(BLACK, connection.fromNode, connection.toNode, 3, 14)


    def drawConnection(self, color, fromNode, toNode, thickness, offset):
        scale = self.game.renderer.getScale()

        dx, dy = (((fromNode.x - fromNode.offx) - (toNode.x - toNode.offx)), ((fromNode.y - fromNode.offy) - (toNode.y - toNode.offy)))

        if dx != 0 and dy != 0:
            posx = (int(((fromNode.x - fromNode.offx) + offset) * scale), int(((fromNode.y - fromNode.offy) + 10) * scale))
            posy = (int(((toNode.x - toNode.offx) + offset) * scale), int(((toNode.y - toNode.offy) + 10) * scale))
        else:
            posx = (int(((fromNode.x - fromNode.offx) + offset) * scale), int(((fromNode.y - fromNode.offy) + offset) * scale))
            posy = (int(((toNode.x - toNode.offx) + offset) * scale), int(((toNode.y - toNode.offy) + offset) * scale))
        
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
    def __init__(self, spriteRenderer, groups):
        super().__init__(spriteRenderer, groups)
        self.grid.createGrid("layer 1")
        self.addConnections()  


class Layer2(Layer):
    def __init__(self, spriteRenderer, groups):
        super().__init__(spriteRenderer, groups)
        self.grid.createGrid("layer 2")
        self.addConnections()     



class Layer3(Layer):
    def __init__(self, spriteRenderer, groups):
        super().__init__(spriteRenderer, groups)
        self.grid.createGrid("layer 3")
        self.addConnections()            



class Layer4(Layer):
    def __init__(self, spriteRenderer, groups):
        super().__init__(spriteRenderer, groups)
        background = Background(self.game, "river", (600, 250), (config["graphics"]["displayWidth"] - 600, config["graphics"]["displayHeight"] - 250))
        self.addComponent(background)

        

        
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