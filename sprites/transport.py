import pygame
from pygame.locals import *
import pygame.gfxdraw
from config import *
import os
import random
import decimal
import math

from node import *
from person import *
vec = pygame.math.Vector2


class Transport(pygame.sprite.Sprite):
    def __init__(self, game, groups, currentConnection, direction):
        self.groups = groups
        pygame.sprite.Sprite.__init__(self, self.groups)
        
        self.game = game
        self.currentConnection = currentConnection
        self.currentNode = self.currentConnection.getFrom()
        self.width = 30
        self.height = 30

        self.offx, self.offy = -5, -5 # -5 is half the offset of the connector
        self.vel = vec(0, 0)
        self.pos = vec(self.currentConnection.getFrom().x + self.offx, self.currentConnection.getFrom().y + self.offy)

        self.speed = float(decimal.Decimal(random.randrange(40, 60)))
        self.direction = direction #0 forwards, 1 backwards
        
        self.dirty = True

        self.moving = True
        self.timer = 0
        self.timerLength = 250

        #people travelling in the transport
        self.people = []

        self.imageName = "train"
        self.stopType = MetroStation


    def addPerson(self, person):
        self.people.append(person)

    def removePerson(self, person):
        self.people.remove(person)
    
    def getPeople(self):
        return self.people

    # Set people waiting at the train station to boarding the transportation 
    def setPeopleDeparting(self):
        # If theres no one at the station, dont bother trying to add anyone
        if len(self.currentNode.getPeople()) <= 0:
            return

        for person in self.currentNode.getPeople():
            if person.getStatus() == Person.Status.WAITING: # If they're waiting for the train
                person.setStatus(Person.Status.BOARDING)


    # Add multiple people who are departing on the transportation
    def addPeople(self):
        # If theres no one at the station, dont bother trying to add anyone
        if len(self.currentNode.getPeople()) <= 0:
            return

        for person in self.currentNode.getPeople():
            # Only remove people from the station once the train is moving
            if person.getStatus() == Person.Status.BOARDING:
                self.addPerson(person)
                self.currentNode.removePerson(person)
                person.setStatus(Person.Status.MOVING)



    # Remove multiple people who are departing from the transportation
    def removePeople(self):
        if len(self.people) <= 0:
            return

        for person in self.people:
            if person.getStatus() == Person.Status.DEPARTING:
                self.removePerson(person) # Remove the person from the transport
                self.currentNode.addPerson(person)  # Add the person back to the node where the transport is stopped
                person.setStatus(Person.Status.UNASSIGNED)  # Set the person to unassigned so they can be moved
                person.setCurrentNode(self.currentNode) # Set the persons current node to the node they're at

                # Position the person offset to the node
                person.pos.x = (self.currentNode.x - self.currentNode.offx) + person.offx
                person.pos.y = (self.currentNode.y - self.currentNode.offy) + person.offy

                person.rect.topleft = person.pos * self.game.renderer.getScale()
                person.moveStatusIndicator()


    def setSpeed(self, speed):
        self.speed = speed

    def setDirection(self, direction):
        self.direction = direction


    def setMoving(self, moving):
        self.moving = moving

    
    def getMoving(self):
        return self.moving
        
        
    def __render(self):
        self.dirty = False

        self.image = self.game.imageLoader.getImage(self.imageName)
        self.image = pygame.transform.smoothscale(self.image, (int(self.width * self.game.renderer.getScale()), 
                                                            int(self.height * self.game.renderer.getScale())))
        self.rect = self.image.get_rect()

    def draw(self):
        if self.dirty or self.image is None: self.__render()
        self.game.renderer.addSurface(self.image, (self.rect))

        if self.timer > 0:
            #draw the time indicator
            self.drawTimer()



    def setConnection(self, nextNode):
        possibleNodes = []
        backwardsNodes = []


        for connection in nextNode.getConnections():
            if connection.getType() == self.currentConnection.getType():
                if connection.getDirection() == self.direction:
                    possibleNodes.append(connection)
                else:
                    backwardsNodes.append(connection)

        #it can keep going the same direction
        if len(possibleNodes) > 0:
            # if theres multiple possible nodes, pick a random one                          #TO DO - make transports follow specific path
            self.currentConnection = possibleNodes[random.randint(0, len(possibleNodes) - 1)]
        else:
            self.direction = not self.direction
            self.currentConnection = backwardsNodes[0]

        self.currentNode = self.currentConnection.getFrom()



    def drawTimer(self):
        scale = self.game.renderer.getScale()

        # Arc Indicator 
        offx = 0.01
        step = self.timer / (self.timerLength / 2) + 0.02
        for x in range(6):
            pygame.draw.arc(self.game.renderer.gameDisplay, YELLOW, ((self.pos.x - 4) * scale, (self.pos.y - 4) * scale, (self.width + 8) * scale, (self.height + 8) * scale), math.pi / 2 + offx, math.pi / 2 + math.pi * step, 8)
            offx += 0.01


    def setNextConnection(self):
        nextNode = self.currentConnection.getTo()
        
        # If the transport is moving, set its next connection to the next upcoming node
        if self.moving:
            self.setConnection(nextNode)

        if isinstance(self.currentNode, self.stopType):

            # Remove anyone departing before we add new people
            self.removePeople()

            # Set people waiting for the transportation to departing 
            self.setPeopleDeparting()

            self.moving = False
            self.timer += 1

            # Leaving the station
            if self.timer > self.timerLength:
                self.moving = True
                self.timer = 0

                # Add the people boarding to the transportation
                self.addPeople()


    #move all the people within the transport relative to its location
    def movePeople(self):
        if len(self.people) <= 0:
            return

        for person in self.people:
            person.pos = self.pos + vec(person.offx, person.offy)
            person.rect.topleft = person.pos * self.game.renderer.getScale()
            person.moveStatusIndicator()


    def update(self):
        if hasattr(self, 'rect'):
            dx, dy = (((self.currentConnection.getTo().x - self.currentConnection.getTo().offx) - self.pos.x) + self.offx, ((self.currentConnection.getTo().y - self.currentConnection.getTo().offy) - self.pos.y) + self.offy)
            dis = math.sqrt(dx ** 2 + dy ** 2)

            self.vel = (0, 0)

            if dis > 1 and self.moving: #move towards the node
                # Slow down when reaching a stop
                if dis <= 15 and isinstance(self.currentConnection.getTo(), self.stopType):
                    self.vel = (vec(dx, dy) * (self.speed / 10)) * self.game.dt
                else:
                    self.vel = vec(dx, dy) / dis * float(self.speed) * self.game.dt
                self.movePeople()

            else: #its reached the node
                self.setNextConnection()

            self.pos += self.vel
            self.rect.topleft = self.pos * self.game.renderer.getScale()


class Taxi(Transport):
    pass


class Bus(Transport):
    def __init__(self, game, groups, currentConnection, direction):
        super().__init__(game, groups, currentConnection, direction)
        self.imageName = "bus"
        self.stopType = BusStop


class Metro(Transport):
    pass
