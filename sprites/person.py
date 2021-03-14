import pygame
from pygame.locals import *
import pygame.gfxdraw
from config import *
import os
import random
import math
import numpy

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
        BOARDINGTAXI = 4
        MOVING = 5
        DEPARTING = 6
        FLAG = 7
        

    def __init__(self, spriteRenderer, groups, clickManager, transportClickManager, spawnDestinations, possibleSpawns, possibleDestinations):
        self.groups = groups
        super().__init__(self.groups)
        self.spriteRenderer = spriteRenderer
        self.clickManager = clickManager
        self.transportClickManager = transportClickManager
        self.game = self.spriteRenderer.game
        self.width = 20
        self.height = 20

        #List of possible destinations that the player can have (different player types might have different destinatiosn that they go to)
        self.possibleSpawns = possibleSpawns
        self.possibleDestinations = possibleDestinations
        self.spawnDestinations = spawnDestinations
        self.destination = None
        self.spawn = None
        
        self.setSpawn(self.spawnDestinations)
        self.setDestination(self.spawnDestinations)

        self.currentNode = self.spawn
        self.startingConnectionType = "layer 2" #  always start on the second layer 
        self.currentConnectionType = self.currentNode.connectionType

        self.offset = vec(-10, -15) #-10, -20 # Move it back 10 pixels x, 20 pixels y
        self.pos = (self.currentNode.pos + self.offset) - self.currentNode.offset
        self.vel = vec(0, 0)

        self.currentNode.addPerson(self)

        self.speed = 20
        self.budget = 20
        self.path = []

        self.travellingOn = None

        self.mouseOver = False
        self.status = Person.Status.UNASSIGNED

        self.dirty = True

        self.imageName = "person"

        self.statusIndicator = StatusIndicator(self.game, self.groups, self)

        self.timer = random.randint(70, 100)
        # self.timer = 20
        self.rad = 5
        self.step = 15

        # Switch to the layer that the player spawned on
        self.switchLayer(self.getLayer(self.startingConnectionType), self.getLayer(self.currentConnectionType))


    # static function to check which player types can spawn on the map dependent on the desitations available
    @staticmethod
    def checkPeopleTypes(peopleTypes, previousPeopleTypes, spawnDestinations):
        possiblePlayerTypes = {}
        finalPlayerTypes = []
        finalPlayerWeights = []

        for person in peopleTypes:
            possiblePlayerTypes[person] = {}
            for node in spawnDestinations:
                if isinstance(node, person.getPossibleSpawns()):
                    possiblePlayerTypes[person].setdefault('spawns', []).append(node)

                elif isinstance(node, person.getPossibleDestinations()):
                    possiblePlayerTypes[person].setdefault('destinations', []).append(node)
  
        for person, spawnDestinations in possiblePlayerTypes.items():
            # if there is more than one spawn node, we know there are two different types (spawn and destination)
            if 'spawns' in spawnDestinations and len(spawnDestinations['spawns']) > 1:
                finalPlayerTypes.append(person)
                continue 
            elif 'spawns' in spawnDestinations and 'destinations' in spawnDestinations:
                finalPlayerTypes.append(person)
                continue

        # no players can spawn
        if len(finalPlayerTypes) <= 0:
            return [], []

        weights = numpy.full(shape = len(finalPlayerTypes), fill_value = 100 / len(finalPlayerTypes), dtype = numpy.int)
        for i in range(len(finalPlayerTypes)):
            occurances = previousPeopleTypes.count(finalPlayerTypes[i])
            weights[i] -= (occurances * 10)
            indexes = [j for j, x in enumerate(weights) if j != i]
            for k in indexes:
                weights[k] += (occurances * 10) / (len(finalPlayerTypes) - 1)

        return finalPlayerTypes, weights


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
            return self.spriteRenderer.layer1
        elif connection == "layer 2":
            return self.spriteRenderer.layer2
        elif connection == "layer 3":
            return self.spriteRenderer.layer3


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
        betterDestinations = []
        for destination in destinations:
            # If the destination is one of the persons possible destinations and not the node the player is currently on
            if isinstance(destination, self.possibleDestinations) and destination.getNumber() != self.spawn.getNumber():
                possibleDestinations.append(destination)

        for desintation in possibleDestinations:
            if not isinstance(desintation, type(self.spawn)):
                betterDestinations.append(desintation)

        if len(betterDestinations) > 0:
            possibleDestinations = betterDestinations

        destination = random.randint(0, len(possibleDestinations) - 1)
        self.destination = possibleDestinations[destination]


    def setSpawn(self, spawns = []):
        possibleSpawns = []
        for spawn in spawns:
            if isinstance(spawn, self.possibleSpawns):
                possibleSpawns.append(spawn)

        spawn = random.randint(0, len(possibleSpawns) - 1)
        self.spawn = possibleSpawns[spawn]


    def remove(self):
        self.kill()
        self.statusIndicator.kill()
        self.spriteRenderer.setTotalPeople(self.spriteRenderer.getTotalPeople() - 1)


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
        self.spriteRenderer.setTotalPeople(self.spriteRenderer.getTotalPeople() + 1)
        self.spriteRenderer.addToCompleted()
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
        self.statusIndicator.rect.topleft = self.statusIndicator.pos * self.game.renderer.getScale() * self.spriteRenderer.getFixedScale()



    # Visualize the players path by drawing the connection between each node in the path
    def drawPath(self):
        if len(self.path) <= 0:
            return

        start = self.path[0]
        scale = self.game.renderer.getScale() * self.spriteRenderer.getFixedScale()
        thickness = 3

        for previous, current in zip(self.path, self.path[1:]):
            posx = ((previous.pos - previous.offset) + vec(10, 10)) * scale
            posy = ((current.pos - current.offset) + vec(10, 10)) * scale

            pygame.draw.line(self.game.renderer.gameDisplay, YELLOW, posx, posy, int(thickness * scale))
            
        # Connection from player to the first node in the path
        startx = ((self.pos - self.offset) + vec(10, 10)) * scale
        starty = ((start.pos - start.offset) + vec(10, 10)) * scale
        pygame.draw.line(self.game.renderer.gameDisplay, YELLOW, startx, starty, int(thickness * scale))


    def drawTimerOutline(self, surface):
        scale = self.game.renderer.getScale() * self.spriteRenderer.getFixedScale()
        thickness = 4

        start = (self.pos - self.offset) + vec(7, -10)
        middle = (self.pos + vec(30, -40)) 
        end = middle + vec(30, 0)

        pygame.draw.lines(surface, YELLOW, False, [start * scale, middle * scale, end * scale], int(thickness * scale))


    def drawTimerTime(self):
        textColor = Color("white") if self.spriteRenderer.getDarkMode() else BLACK
        self.fontImage = self.timerFont.render(str(round(self.timer, 1)), True, textColor)
        self.game.renderer.addSurface(self.fontImage, (self.pos + vec(32, -35)) * self.game.renderer.getScale() * self.spriteRenderer.getFixedScale())


    # Draw how long is left at each stop 
    def drawTimer(self, surface):
        scale = self.game.renderer.getScale() * self.spriteRenderer.getFixedScale()
        length = 10

        # Arc Indicator 
        offx = 0.01
        step = self.timer / (length / 2) + 0.02
        for x in range(6):
            pygame.draw.arc(surface, YELLOW, ((self.pos.x - 4) * scale, (self.pos.y - 4) * scale, (self.width + 8) * scale, (self.height + 8) * scale), math.pi / 2 + offx, math.pi / 2 + math.pi * step, int(4 * scale))
            offx += 0.01


    def drawDestination(self):
        if self.destination is None:
            return 

        scale = self.game.renderer.getScale() * self.spriteRenderer.getFixedScale()
        thickness = 4

        pos = (self.destination.pos - vec(self.rad, self.rad)) * scale 
        size = vec(self.destination.width + (self.rad * 2), self.destination.height + (self.rad * 2)) * scale
        rect = pygame.Rect(pos, size)

        pygame.draw.lines(self.game.renderer.gameDisplay, YELLOW, False, [rect.topleft + (vec(0, 10) * scale), rect.topleft, rect.topleft + (vec(10, 0) * scale)], int(thickness * scale))
        pygame.draw.lines(self.game.renderer.gameDisplay, YELLOW, False, [rect.topright + (vec(-10, 0) * scale), rect.topright, rect.topright + (vec(0, 10) * scale)], int(thickness * scale))
        pygame.draw.lines(self.game.renderer.gameDisplay, YELLOW, False, [rect.bottomleft + (vec(0, -10) * scale), rect.bottomleft, rect.bottomleft + (vec(10, 0) * scale)], int(thickness * scale))
        pygame.draw.lines(self.game.renderer.gameDisplay, YELLOW, False, [rect.bottomright + (vec(-10, 0) * scale), rect.bottomright, rect.bottomright + (vec(0, -10) * scale)], int(thickness * scale))

        # pygame.draw.ellipse(self.game.renderer.gameDisplay, YELLOW, rect, int(7 * scale))


    def drawOutline(self, surface):
        scale = self.game.renderer.getScale() * self.spriteRenderer.getFixedScale()

        offx = 0.01
        for x in range(6):
            pygame.draw.arc(surface, YELLOW, ((self.pos.x) * scale, (self.pos.y) * scale, (self.width) * scale, (self.height) * scale), math.pi / 2 + offx, math.pi / 2, int(3.5 * scale))
            offx += 0.02


    def __render(self):
        self.dirty = False
        self.image = self.game.imageLoader.getImage(self.imageName, (self.width * self.spriteRenderer.getFixedScale(), self.height * self.spriteRenderer.getFixedScale()))
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos * self.game.renderer.getScale() * self.spriteRenderer.getFixedScale()

        self.timerFont = pygame.font.Font(pygame.font.get_default_font(), int(15 * self.game.renderer.getScale() * self.spriteRenderer.getFixedScale())) # do I need the fixed scale to change here?



    def draw(self):
        if self.dirty or self.image is None: self.__render()
        self.game.renderer.addSurface(self.image, (self.rect))

        if self.mouseOver or self.clickManager.getPerson() == self:
            self.drawTimerTime()
            self.drawDestination()
            self.game.renderer.addSurface(None, None, self.drawTimerOutline)

         # Visualize the players path
        if self.clickManager.getPerson() == self:
            self.drawPath()
            self.game.renderer.addSurface(None, None, self.drawOutline)

        if self.timer <= 10:
            self.game.renderer.addSurface(None, None, self.drawTimer)



    def events(self):
        self.vel = vec(0, 0)

        mx, my = pygame.mouse.get_pos()
        difference = self.game.renderer.getDifference()
        mx -= difference[0]
        my -= difference[1]
        

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
                if isinstance(self.currentNode, NODE.Stop) or isinstance(self.currentNode, NODE.Destination):
                    self.status = Person.Status.WAITING
                elif isinstance(self.currentNode, NODE.Node):
                    self.status = Person.Status.FLAG

            elif self.status == Person.Status.WAITING:
                # or if its a desintation on layer 2
                if isinstance(self.currentNode, NODE.BusStop) or (isinstance(self.currentNode, NODE.Destination) and self.currentNode.getConnectionType() == "layer 2"): # toggle between waiting for a bus and flagging a taxi
                    self.status = Person.Status.FLAG
                else:
                    self.status = Person.Status.UNASSIGNED
                    
            elif self.status == Person.Status.FLAG:
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

            self.timer -= self.game.dt * self.spriteRenderer.getDt()
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
                    self.vel = dxy / dis * float(self.speed) * self.game.dt * self.spriteRenderer.getDt()
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
                self.rect.topleft = self.pos * self.game.renderer.getScale() * self.spriteRenderer.getFixedScale()



class Manager(Person):
    def __init__(self, renderer, groups, clickManager, transportClickManager, spawnDestinations):
        super().__init__(renderer, groups, clickManager, transportClickManager, spawnDestinations, Manager.getPossibleSpawns(), Manager.getPossibleDestinations())
        self.budget = 40
        self.imageName = "manager"

    @staticmethod
    def getPossibleSpawns():
        return (NODE.House, NODE.Office)

    @staticmethod
    def getPossibleDestinations():
        return (NODE.Office, NODE.House) 


    # Office, airport
    # has a very high budget so can afford taxis etc.

class Commuter(Person):
    def __init__(self, renderer, groups, clickManager, transportClickManager, spawnDestinations):
        super().__init__(renderer, groups, clickManager, transportClickManager, spawnDestinations, Commuter.getPossibleSpawns(), Commuter.getPossibleDestinations())
        self.budget = 12
        self.imageName = "person"

    @staticmethod
    def getPossibleSpawns():
        return (NODE.House, NODE.Airport)

    @staticmethod
    def getPossibleDestinations():
        return (NODE.Airport, NODE.House)

    # Office, home?
    # has a small budget so cant rly afford many taxis etc.
 


class StatusIndicator(pygame.sprite.Sprite):
    def __init__(self, game, groups, currentPerson):
        self.groups = groups
        super().__init__(self.groups)
        self.game = game
        self.currentPerson = currentPerson
        self.spriteRenderer = self.currentPerson.spriteRenderer

        self.width = 10
        self.height = 10

        self.offset = vec(-2.5, -10)
        self.pos = self.currentPerson.pos + self.offset

        self.dirty = True

        self.images = [None, "walking", "waiting", "boarding", "boarding", None, "departing", "flag"]
        self.currentState = self.currentPerson.getStatusValue()


    def __render(self):
        self.dirty = False
        self.image = self.game.imageLoader.getImage(self.images[self.currentState], (self.width * self.spriteRenderer.getFixedScale(), self.height * self.spriteRenderer.getFixedScale()))
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos * self.game.renderer.getScale() * self.spriteRenderer.getFixedScale()


    def draw(self):
        if self.images[self.currentState] is None:
            return

        if self.dirty or self.image is None: self.__render()
        self.game.renderer.addSurface(self.image, (self.rect))

    
    def update(self):
        if self.currentPerson.getStatusValue() != self.currentState:
            self.dirty = True
            self.currentState = self.currentPerson.getStatusValue()
