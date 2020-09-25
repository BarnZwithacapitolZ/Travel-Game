import pygame
from pygame.locals import *
import pygame.gfxdraw
from config import *
import os
import random
import math

from engine import ImageLoader
from enum import Enum
import node as NODE

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
        FLAG = 6
        

    def __init__(self, renderer, groups, currentNode, clickManager, transportClickManager):
        self.groups = groups
        super().__init__(self.groups)
        self.renderer = renderer
        self.clickManager = clickManager
        self.transportClickManager = transportClickManager
        self.game = self.renderer.game
        self.width = 20
        self.height = 20
        
        self.currentNode = currentNode
        self.startingConnectionType = self.currentNode.connectionType
        self.currentConnectionType = self.currentNode.connectionType
        self.currentNode.addPerson(self)

        #List of possible destinations that the player can have (different player types might have different destinatiosn that they go to)
        self.possibleDestinations = (NODE.Airport, NODE.Office) # Default is to accept all types
        self.destination = None

        self.budget = 20

        self.offset = vec(-10, -15) #-10, -20 # Move it back 10 pixels x, 20 pixels y
        self.pos = (self.currentNode.pos + self.offset) - self.currentNode.offset
        self.vel = vec(0, 0)

        self.mouseOver = False
        self.speed = 32
        self.path = []

        self.travellingOn = None

        self.status = Person.Status.UNASSIGNED

        self.dirty = True

        self.imageName = "person"

        self.statusIndicator = StatusIndicator(self.game, self.groups, self)

        self.timer = random.randint(70, 100)
        self.rad = 5
        self.step = 15



    #### Getters ####

    # Return the current status (Status) of the person
    def getStatus(self):
        return self.status


    # Return the status value (int) of the person
    def getStatusValue(self):
        return self.status.value


    # Return the current node that the person is at
    def getCurrentNode(self):
        return self.currentNode


    # Return the current connection type of the person
    def getCurrentConnectionType(self): 
        return self.currentConnectionType


    # Return the connection type that the person started at
    def getStartingConnectionType(self):
        return self.startingConnectionType


    # Return the layer, given the connection 
    def getLayer(self, connection):
        if connection == "layer 1":
            return self.renderer.layer1
        if connection == "layer 2":
            return self.renderer.layer2
        if connection == "layer 3":
            return self.renderer.layer3


    def getMouseOver(self):
        return self.mouseOver


    def getPossibleDestinations(self):
        return self.possibleDestinations

    
    def getBudget(self):
        return self.budget


    def getDestination(self):
        return self.destination


    def getTravellingOn(self):
        return self.travellingOn


    #### Setters ####

    # Set the persons status
    def setStatus(self, status):
        self.status = status


    # Set the current node that the person is at
    def setCurrentNode(self, node):
        self.currentNode = node


    def setPosition(self, pos):
        self.pos = pos
        self.dirty = True


    def setTravellingOn(self, travellingOn):
        self.travellingOn = travellingOn


    def setDestination(self, destinations = []):
        possibleDestinations = []
        for destination in destinations:
            # If the destination is one of the persons possible destinations and not the node the player is currently on
            if isinstance(destination, self.possibleDestinations) and destination.getNumber() != self.currentNode.getNumber():
                possibleDestinations.append(destination)

        destination = random.randint(0, len(possibleDestinations) - 1)
        self.destination = possibleDestinations[destination]


    def remove(self):
        self.kill()
        self.statusIndicator.kill()


    # Add a node to the persons path
    def addToPath(self, node):
        self.path.append(node)

    
    # Remove a node from the persons path
    def removeFromPath(self, node):
        self.path.remove(node)

    
    # Clear the players path by removing all nodes 
    # To Do: FIX PLAYER WALKING BACK TO CURRENT NODE WHEN NEW PATH IS ASSINGNED
    def clearPath(self, newPath):
        if len(self.path) <= 0 or len(newPath) <= 0:
            return

        # The new path is going in the same direction, so we delete its starting node since the player has already passed this
        if self.path[0] in newPath:
            del newPath[0]

        self.path = []


    def complete(self):
        self.renderer.addToCompleted()
        self.remove()


    # Switch the person and their status indicator from one layer to a new layer
    def switchLayer(self, oldLayer, newLayer):
        oldLayer.remove(self)
        newLayer.add(self)
        oldLayer.remove(self.statusIndicator)
        newLayer.add(self.statusIndicator)
        self.currentConnectionType = self.currentNode.connectionType


    # Move the status indicator above the plerson so follow the persons movement
    def moveStatusIndicator(self):
        if not hasattr(self.statusIndicator, 'rect'):
            return

        self.statusIndicator.pos = self.pos + self.statusIndicator.offset
        self.statusIndicator.rect.topleft = self.statusIndicator.pos * self.game.renderer.getScale()



    # Visualize the players path by drawing the connection between each node in the path
    def drawPath(self):
        if len(self.path) <= 0:
            return

        start = self.path[0]
        scale = self.game.renderer.getScale()
        thickness = 3

        for previous, current in zip(self.path, self.path[1:]):
            posx = ((previous.pos - previous.offset) + vec(10, 10)) * scale
            posy = ((current.pos - current.offset) + vec(10, 10)) * scale

            pygame.draw.line(self.game.renderer.gameDisplay, YELLOW, posx, posy, int(thickness * scale))
            
        # Connection from player to the first node in the path
        startx = ((self.pos - self.offset) + vec(10, 10)) * scale
        starty = ((start.pos - start.offset) + vec(10, 10)) * scale
        pygame.draw.line(self.game.renderer.gameDisplay, YELLOW, startx, starty, int(thickness * scale))


    def drawTimerOutline(self):
        scale = self.game.renderer.getScale()
        thickness = 4

        start = (self.pos - self.offset) + vec(7, -10)
        middle = (self.pos + vec(30, -40)) 
        end = middle + vec(30, 0)

        pygame.draw.lines(self.game.renderer.gameDisplay, YELLOW, False, [start * scale, middle * scale, end * scale], int(thickness * scale))


    def drawTimerTime(self):
        self.fontImage = self.timerFont.render(str(round(self.timer, 1)), True, BLACK)
        self.game.renderer.addSurface(self.fontImage, (self.pos + vec(32, -35)) * self.game.renderer.getScale())


    def drawDestination(self):
        if self.destination is None:
            return 

        scale = self.game.renderer.getScale()
        thickness = 4

        pos = (self.destination.pos - vec(self.rad, self.rad)) * scale 
        size = vec(self.destination.width + (self.rad * 2), self.destination.height + (self.rad * 2)) * scale
        rect = pygame.Rect(pos, size)

        pygame.draw.lines(self.game.renderer.gameDisplay, YELLOW, False, [rect.topleft + (vec(0, 10) * scale), rect.topleft, rect.topleft + (vec(10, 0) * scale)], int(thickness * scale))
        pygame.draw.lines(self.game.renderer.gameDisplay, YELLOW, False, [rect.topright + (vec(-10, 0) * scale), rect.topright, rect.topright + (vec(0, 10) * scale)], int(thickness * scale))
        pygame.draw.lines(self.game.renderer.gameDisplay, YELLOW, False, [rect.bottomleft + (vec(0, -10) * scale), rect.bottomleft, rect.bottomleft + (vec(10, 0) * scale)], int(thickness * scale))
        pygame.draw.lines(self.game.renderer.gameDisplay, YELLOW, False, [rect.bottomright + (vec(-10, 0) * scale), rect.bottomright, rect.bottomright + (vec(0, -10) * scale)], int(thickness * scale))

        # pygame.draw.ellipse(self.game.renderer.gameDisplay, YELLOW, rect, int(7 * scale))


    def drawOutline(self):
        scale = self.game.renderer.getScale()

        offx = 0.01
        for x in range(6):
            pygame.draw.arc(self.game.renderer.gameDisplay, YELLOW, ((self.pos.x) * scale, (self.pos.y) * scale, (self.width) * scale, (self.height) * scale), math.pi / 2 + offx, math.pi / 2, int(3.5 * scale))
            
            offx += 0.02


    def __render(self):
        self.dirty = False

        self.image = self.game.imageLoader.getImage(self.imageName)
        self.image = pygame.transform.smoothscale(self.image, (int(self.width * self.game.renderer.getScale()), 
                                                            int(self.height * self.game.renderer.getScale())))
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos * self.game.renderer.getScale()

        self.timerFont = pygame.font.Font(pygame.font.get_default_font(), int(15 * self.game.renderer.getScale()))



    def draw(self):
        if self.dirty or self.image is None: self.__render()
        self.game.renderer.addSurface(self.image, (self.rect))

        if self.mouseOver or self.clickManager.getPerson() == self:
            self.drawTimerTime()
            self.game.renderer.addSurface(None, None, self.drawTimerOutline)

         # Visualize the players path
        if self.clickManager.getPerson() == self:
            self.drawPath()
            self.drawDestination()
            self.game.renderer.addSurface(None, None, self.drawOutline)


    def events(self):
        self.vel = vec(0, 0)

        mx, my = pygame.mouse.get_pos()
        mx -= self.game.renderer.getDifference()[0]
        my -= self.game.renderer.getDifference()[1]
        

        # If the mouse is clicked, but not on a person, unset the person from the clickmanager (no one clicked)
        # Unlick event
        if not self.rect.collidepoint((mx, my)) and self.game.clickManager.getClicked():
            self.clickManager.setPerson(None)


        # Click event
        if self.rect.collidepoint((mx, my)) and self.game.clickManager.getClicked():
            if self.currentNode.getMouseOver():
                return

            # Click off the transport (if selected)
            if self.transportClickManager.getTransport() is not None:
                self.transportClickManager.setTransport(None)
                
            self.clickManager.setPerson(self)

            if self.status == Person.Status.UNASSIGNED:
                if isinstance(self.currentNode, NODE.Stop):
                    self.status = Person.Status.WAITING
                elif isinstance(self.currentNode, NODE.Node):
                    self.status = Person.Status.FLAG

            elif self.status == Person.Status.WAITING or self.status == Person.Status.FLAG:
                self.status = Person.Status.UNASSIGNED
            
            elif self.status == Person.Status.BOARDING:
                self.status = Person.Status.UNASSIGNED
            
            elif self.status == Person.Status.MOVING:
                self.status = Person.Status.DEPARTING

            elif self.status == Person.Status.DEPARTING:
                self.status = Person.Status.MOVING

            self.game.clickManager.setClicked(False)
            
        # Hover over event
        if self.rect.collidepoint((mx, my)) and not self.mouseOver:
            # hover over a node when person is hovered over, unset the hover on the node
            if self.currentNode.getMouseOver():
                self.currentNode.setMouseOver(False)

            # hover over a transport when person is hovered over, unset the hover on the transport
            for transport in self.currentNode.getTransports():
                if transport.getMouseOver():
                    transport.setMouseOver(False)

            if self.travellingOn is not None:
                self.travellingOn.setMouseOver(False)

            self.image.fill(HOVERGREY, special_flags=BLEND_MIN)
            self.mouseOver = True
        
        # Hover out event
        if not self.rect.collidepoint((mx, my)) and self.mouseOver:
            self.mouseOver = False
            self.dirty = True


    def update(self):
        if hasattr(self, 'rect'):
            self.events()
            # print(self.status)

            self.timer -= self.game.dt
            self.rad += self.step * self.game.dt

            # Increase the radius of the selector showing the destination
            if self.rad > 10 and self.step > 0 or self.rad <= 5 and self.step < 0:
                self.step = -self.step
                
            if self.timer <= 0:
                self.remove()

            if self.currentNode.getNumber() == self.destination.getNumber():
                self.complete()


            if len(self.path) > 0:
                path = self.path[0]

                dxy = (path.pos - path.offset) - self.pos + self.offset
                dis = dxy.length()

                if dis > 1:
                    self.status = Person.Status.WALKING
                    self.vel = dxy / dis * float(self.speed) * self.game.dt
                    self.moveStatusIndicator()

                else:
                    self.currentNode.removePerson(self)
                    self.currentNode = path
                    self.currentNode.addPerson(self)
                    self.path.remove(path)

                    # No more nodes in the path, the person is no longer walking and is unassigned
                    if len(self.path) <= 0:
                        self.status = Person.Status.UNASSIGNED

                    if self.currentConnectionType != self.currentNode.connectionType:
                        self.switchLayer(self.getLayer(self.currentConnectionType), self.getLayer(self.currentNode.connectionType))
                
                self.pos += self.vel
                self.rect.topleft = self.pos * self.game.renderer.getScale()



class Manager(Person):
    def __init__(self, renderer, groups, currentNode, clickManager, transportClickManager):
        super().__init__(renderer, groups, currentNode,clickManager, transportClickManager)
        self.possibleDestinations = (NODE.Airport, NODE.Office)
        self.budget = 40

        self.imageName = "manager"


    # Office, airport
    # has a very high budget so can afford taxis etc.

class Commuter(Person):
    def __init__(self, renderer, groups, currentNode, clickManager, transportClickManager):
        super().__init__(renderer, groups, currentNode, clickManager, transportClickManager)
        self.possibleDestinations = (NODE.Airport, NODE.Office)
        self.budget = 12

    # Office, home?
    # has a small budget so cant rly afford many taxis etc.
 


class StatusIndicator(pygame.sprite.Sprite):
    def __init__(self, game, groups, currentPerson):
        self.groups = groups
        super().__init__(self.groups)
        self.game = game
        self.currentPerson = currentPerson

        self.width = 10
        self.height = 10

        self.offset = vec(-2.5, -10)
        self.pos = self.currentPerson.pos + self.offset

        self.dirty = True

        self.images = [None, "walking", "waiting", "boarding", None, "departing", "flag"]
        self.currentState = self.currentPerson.getStatusValue()


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
