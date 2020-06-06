import pygame
from pygame.locals import *
import pygame.gfxdraw
from config import *
import os
import math

vec = pygame.math.Vector2

class Node(pygame.sprite.Sprite):
    def __init__(self, game, groups, number, connectionType, x, y):
        self.groups = groups
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.game = game
        self.number = number
        self.connectionType = connectionType
        self.offx, self.offy = 0, 0
        self.width = 20
        self.height = 20
        self.x = x - self.offx
        self.y = y - self.offy

        #all connections to / from this node
        self.connections = []

        # all transport currently at this node
        self.transports = []

        # all people currently at this node
        self.people = []

        self.dirty = True

        self.mouseOver = False
        self.images = ["node", "nodeSelected"]
        self.currentImage = 0

    def __render(self):
        self.dirty = False

        self.image = self.game.imageLoader.getImage(self.images[self.currentImage])
        self.image = pygame.transform.smoothscale(self.image, (int(self.width * self.game.renderer.getScale()), 
                                                            int(self.height * self.game.renderer.getScale())))
        self.rect = self.image.get_rect()
        self.rect.x = self.x * self.game.renderer.getScale()
        self.rect.y = self.y * self.game.renderer.getScale()


    def draw(self):
        if self.dirty or self.image is None: self.__render()
        self.game.renderer.addSurface(self.image, (self.rect))

    
    def addConnection(self, connection):
        self.connections.append(connection)

    
    def addTransport(self, transport):
        self.transports.append(transport)

    
    def addPerson(self, person):
        self.people.append(person)
    
    def removePerson(self, person):
        self.people.remove(person)


    def getConnections(self):
        return self.connections


    def getTransports(self):
        return self.transports


    def getPeople(self):
        return self.people


    def getNumber(self):
        return self.number

    def events(self):
        mx, my = pygame.mouse.get_pos()
        mx -= self.game.renderer.getDifference()[0]
        my -= self.game.renderer.getDifference()[1]

        if self.rect.collidepoint((mx, my)) and self.game.clickManager.getClicked():
            self.game.clickManager.setNode(self)
            self.game.clickManager.setClicked(False)

        if self.rect.collidepoint((mx, my)) and not self.mouseOver:
            self.mouseOver = True
            self.currentImage = 1
            self.dirty = True

            # print(self.number)
            # print(self.people)

            # for connection in self.connections:
            #     print("From " + str(connection.getFrom().number) + ", To " + str(connection.getTo().number) + ", Length " + str(connection.getLength()) + ', direction ' + str(connection.getDirection()))
        
        if not self.rect.collidepoint((mx, my)) and self.mouseOver:
            self.mouseOver = False
            self.currentImage = 0
            self.dirty = True


    def update(self):
        if not self.dirty:
            self.events()




class BusStop(Node):
    def __init__(self, game, groups, number, connectionType, x, y):
        super().__init__(game, groups, number, connectionType, x, y)
        self.width = 25
        self.height = 25
        self.offx, self.offy = -2.5, -2.5
        self.x = self.x + self.offx
        self.y = self.y + self.offy
        self.images = ["busStation", "nodeSelected"]


class MetroStation(Node):
    def __init__(self, game, groups, number, connectionType, x, y):
        super().__init__(game, groups, number, connectionType, x, y)

        self.width = 25
        self.height = 25
        self.offx, self.offy = -2.5, -2.5 #move it back 2.5 pixels in x and y as it is a large surface
        self.x = self.x + self.offx
        self.y = self.y + self.offy
        self.images = ["metro", "nodeSelected"]
