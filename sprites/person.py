import pygame
from pygame.locals import *
import pygame.gfxdraw
from config import *
import os
import random
import math

from enum import Enum
from node import *

vec = pygame.math.Vector2


class Person(pygame.sprite.Sprite):
    # Players different status's
    class Status(Enum):
        UNASSIGNED = 0
        WALKING = 1
        WAITING = 2
        BOARDING = 3
        MOVING = 4
        DEPARTING = 5
        

    def __init__(self, renderer, groups, currentNode):
        self.groups = groups
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.renderer = renderer
        self.game = self.renderer.game
        self.width = 20
        self.height = 20
        
        self.currentNode = currentNode
        self.startingConnectionType = self.currentNode.connectionType
        self.currentConnectionType = self.currentNode.connectionType
        self.currentNode.addPerson(self)

        self.offset = vec(-10, -15) #-10, -20 # Move it back 10 pixels x, 20 pixels y
        self.pos = (self.currentNode.pos + self.offset) - self.currentNode.offset
        self.vel = vec(0, 0)

        self.mouseOver = False
        self.speed = 32
        self.path = []

        self.status = Person.Status.UNASSIGNED

        self.dirty = True

        self.mouseOver = False
        self.images = ["person", "personSelected", "personClicked"]
        self.currentImage = 0

        self.statusIndicator = StatusIndicator(self.game, self.groups, self)


    def moveStatusIndicator(self):
        if not hasattr(self.statusIndicator, 'rect'):
            return

        self.statusIndicator.pos = self.pos + self.statusIndicator.offset
        self.statusIndicator.rect.topleft = self.statusIndicator.pos * self.game.renderer.getScale()


    def __render(self):
        self.dirty = False

        self.image = self.game.imageLoader.getImage(self.images[self.currentImage])
        self.image = pygame.transform.smoothscale(self.image, (int(self.width * self.game.renderer.getScale()), 
                                                            int(self.height * self.game.renderer.getScale())))
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos * self.game.renderer.getScale()


    def draw(self):
        if self.dirty or self.image is None: self.__render()
        self.game.renderer.addSurface(self.image, (self.rect))


    def setStatus(self, status):
        self.status = status


    def setCurrentNode(self, node):
        self.currentNode = node


    def setCurrentImage(self, currentImage):
        self.currentImage = currentImage
        self.dirty = True # Redraw the image to the new image


    def getStatus(self):
        return self.status


    def getStatusValue(self):
        return self.status.value


    def getCurrentNode(self):
        return self.currentNode


    def getCurrentConnectionType(self):
        return self.currentConnectionType

    
    def getStartingConnectionType(self):
        return self.startingConnectionType


    def addToPath(self, node):
        self.path.append(node)

    
    def removeFromPath(self, node):
        self.path.remove(node)


    def switchLayer(self, oldLayer, newLayer):
        oldLayer.remove(self)
        newLayer.add(self)
        oldLayer.remove(self.statusIndicator)
        newLayer.add(self.statusIndicator)
        self.currentConnectionType = self.currentNode.connectionType


    def events(self):
        self.vel = vec(0, 0)

        mx, my = pygame.mouse.get_pos()
        mx -= self.game.renderer.getDifference()[0]
        my -= self.game.renderer.getDifference()[1]

        # If the mouse is clicked, but not on a person, unset the person from the clickmanager (no one clicked)
        if not self.rect.collidepoint((mx, my)) and self.game.clickManager.getClicked():
            self.game.clickManager.setPerson(None)

        if self.rect.collidepoint((mx, my)) and self.game.clickManager.getClicked():
            self.game.clickManager.setPerson(self)

            if self.status == Person.Status.UNASSIGNED:
                if isinstance(self.currentNode, MetroStation) or isinstance(self.currentNode, BusStop):
                    self.status = Person.Status.WAITING

            elif self.status == Person.Status.WAITING:
                self.status = Person.Status.UNASSIGNED
            
            elif self.status == Person.Status.BOARDING:
                self.status = Person.Status.UNASSIGNED
            
            elif self.status == Person.Status.MOVING:
                self.status = Person.Status.DEPARTING

            elif self.status == Person.Status.DEPARTING:
                self.status = Person.Status.MOVING

            self.game.clickManager.setClicked(False)
            
        if self.rect.collidepoint((mx, my)) and not self.mouseOver and not self.game.clickManager.getPersonClicked():
            self.mouseOver = True
            self.currentImage = 1
            self.dirty = True
        
        if not self.rect.collidepoint((mx, my)) and self.mouseOver and not self.game.clickManager.getPersonClicked():
            self.mouseOver = False
            self.currentImage = 0
            self.dirty = True


    def getLayer(self, connection):
        if connection == "layer 1":
            return self.renderer.layer1
        if connection == "layer 2":
            return self.renderer.layer2
        if connection == "layer 3":
            return self.renderer.layer3


    def update(self):
        if hasattr(self, 'rect'):
            self.events()
            # print(self.status)

            if len(self.path) > 0:
                path = self.path[0]

                dxy = (path.pos - path.offset) - self.pos + self.offset
                dis = dxy.length()

                if dis > 1:
                    self.status = Person.Status.WALKING
                    self.vel = dxy / dis * float(self.speed) * self.game.dt
                    self.moveStatusIndicator()

                else:
                    self.status = Person.Status.UNASSIGNED
                    self.currentNode.removePerson(self)
                    self.currentNode = path
                    self.currentNode.addPerson(self)
                    self.path.remove(path)

                    if self.currentConnectionType != self.currentNode.connectionType:
                        self.switchLayer(self.getLayer(self.currentConnectionType), self.getLayer(self.currentNode.connectionType))
                
                self.pos += self.vel
                self.rect.topleft = self.pos * self.game.renderer.getScale()




class StatusIndicator(pygame.sprite.Sprite):
    def __init__(self, game, groups, currentPerson):
        self.groups = groups
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.currentPerson = currentPerson

        self.width = 10
        self.height = 10

        self.offset = vec(-2.5, -10)
        self.pos = self.currentPerson.pos + self.offset

        self.dirty = True

        self.images = [None, "walking", "waiting", "boarding", None, "departing"]
        self.currentState = self.currentPerson.getStatusValue()


    def die(self):
        self.kill()


    def __render(self):
        self.dirty = False

        self.image = self.game.imageLoader.getImage(self.images[self.currentState])
        self.image = pygame.transform.smoothscale(self.image, (int(self.width * self.game.renderer.getScale()), 
                                                            int(self.height * self.game.renderer.getScale())))
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos * self.game.renderer.getScale()


    def draw(self):
        if self.images[self.currentState] is None:
            return

        if self.dirty or self.image is None: self.__render()
        self.game.renderer.addSurface(self.image, (self.rect))

    
    def update(self):
        if self.currentPerson.getStatusValue() != self.currentState:
            self.dirty = True
            self.currentState = self.currentPerson.getStatusValue()
