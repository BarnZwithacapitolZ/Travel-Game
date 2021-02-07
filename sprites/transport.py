import pygame
from pygame.locals import *
import pygame.gfxdraw
from config import *
import os
import random
import decimal
import math

import node as NODE
import person as PERSON
import connection as CONNECTION    

vec = pygame.math.Vector2


class Transport(pygame.sprite.Sprite):
    def __init__(self, spriteRenderer, groups, currentConnection, running, clickManager, personClickManager):
        self.groups = groups
        super().__init__(self.groups)
        
        self.spriteRenderer = spriteRenderer
        self.game = self.spriteRenderer.game
        self.currentConnection = currentConnection
        self.currentNode = self.currentConnection.getFrom()
        self.currentNode.addTransport(self)
        self.width = 30
        self.height = 30

        self.offset = vec(-5, -5) # -5 is half the offset of the connector
        self.vel = vec(0, 0)
        self.pos = (self.currentConnection.getFrom().pos - self.currentConnection.getFrom().offset) + self.offset

        self.speed = float(decimal.Decimal(random.randrange(50, 60)))
        
        self.mouseOver = False
        self.dirty = True

        self.running = running
        self.moving = self.running
        self.timer = 0
        self.timerLength = 300

        self.clickManager = clickManager
        self.personClickManager = personClickManager

        #people travelling in the transport
        self.people = []

        self.imageName = "train"
        self.stopType = NODE.MetroStation

        self.path = []


    #### Getters ####

    # Return the people, in a list, current on the transport
    def getPeople(self):
        return self.people


    # Return if the transport is moving or not
    def getMoving(self):
        return self.moving


    def getCurrentNode(self):
        return self.currentNode


    def getMouseOver(self):
        return self.mouseOver


    #### Setters ####

    def setSpeed(self, speed):
        self.speed = speed

    def setMoving(self, moving):
        self.moving = moving

    def setMouseOver(self, mouseOver):
        self.mouseOver = mouseOver
        self.dirty = True


    # Set the connection that the transport will follow next
    def setConnection(self, nextNode):
        totalConnections = []
        possibleConnections = []

        for connection in nextNode.getConnections():
            if connection.getConnectionType() == self.currentConnection.getConnectionType():
                if not isinstance(connection.getTo(), NODE.EntranceNode):
                    totalConnections.append(connection)

        if len(totalConnections) <= 1:
            self.currentConnection = totalConnections[0]
        else:
            for connection in totalConnections:
                if not (connection.getFrom().getNumber() == self.currentConnection.getFrom().getNumber() and connection.getTo().getNumber() == self.currentConnection.getTo().getNumber() \
                    or connection.getFrom().getNumber() == self.currentConnection.getTo().getNumber() and connection.getTo().getNumber() == self.currentConnection.getFrom().getNumber()):
                    possibleConnections.append(connection)
        
            self.currentConnection = possibleConnections[random.randint(0, len(possibleConnections) - 1)]

        self.currentNode.removeTransport(self)
        self.currentNode = self.currentConnection.getFrom()
        self.currentNode.addTransport(self)



    # Set the next connection for the transport to follow
    def setNextConnection(self):
        nextNode = self.currentConnection.getTo()
        
        # If the transport is moving, set its next connection to the next upcoming node
        if self.moving:
            self.setConnection(nextNode)

        if isinstance(self.currentNode, self.stopType): # and len(self.currentNode.getPeople()) > 0

            # Remove anyone departing before we add new people
            self.removePeople()

            # Set people waiting for the transportation to departing 
            self.setPeopleBoarding()

            self.moving = False
            self.timer += 100 * self.game.dt * self.spriteRenderer.getDt()

            # Leaving the station
            if self.timer > self.timerLength:
                self.moving = True
                self.timer = 0

                # Add the people boarding to the transportation
                self.addPeople()


    # Set people waiting at the train station to boarding the transportation 
    def setPeopleBoarding(self):
        # If theres no one at the station, dont bother trying to add anyone
        if len(self.currentNode.getPeople()) <= 0:
            return

        for person in self.currentNode.getPeople():
            if person.getStatus() == PERSON.Person.Status.WAITING: # If they're waiting for the train
                person.setStatus(PERSON.Person.Status.BOARDING)


    def addToPath(self, node):
        self.path.append(node)


    def clearPath(self, newPath):
        if len(newPath) == 1:
            connections = self.currentConnection.getTo().getConnections()
            for connection in connections:
                if connection.getFrom().getNumber() == self.currentConnection.getTo().getNumber() and connection.getTo().getNumber() == newPath[0].getNumber():
                    self.currentConnection = connection
                    break
            
            self.currentNode.removeTransport(self)
            self.currentNode = self.currentConnection.getFrom()
            self.currentNode.addTransport(self)

        if len(self.path) <= 0 or len(newPath) <= 0:
            # if the node the transport is currently heading towards is in the new path, then we dont need the first node 
            if self.currentConnection.getTo() in newPath:
                del newPath[0]  
                
            return

        if self.path[0] in newPath:
            del newPath[0]

        self.path = []


    # Add a person to the transport
    def addPerson(self, person):
        self.people.append(person)

    # Remove a person from the transport
    def removePerson(self, person):
        self.people.remove(person)


    def remove(self):
        self.kill()
    

    # Add multiple people who are departing on the transportation
    def addPeople(self):
        # If theres no one at the station, dont bother trying to add anyone
        if len(self.currentNode.getPeople()) <= 0:
            return

        for person in self.currentNode.getPeople():
            # Only remove people from the station once the train is moving
            if person.getStatus() == PERSON.Person.Status.BOARDING:
                self.addPerson(person)
                self.currentNode.removePerson(person)
                person.setStatus(PERSON.Person.Status.MOVING)
                person.setTravellingOn(self)
                # Make the person unclicked?
                # self.game.clickManager.setPerson(None)


    # Remove multiple people who are departing from the transportation
    def removePeople(self):
        if len(self.people) <= 0:
            return

        for person in self.people:
            if person.getStatus() == PERSON.Person.Status.DEPARTING:
                self.removePerson(person) # Remove the person from the transport
                self.currentNode.addPerson(person)  # Add the person back to the node where the transport is stopped
                person.setStatus(PERSON.Person.Status.UNASSIGNED)  # Set the person to unassigned so they can be moved
                person.setCurrentNode(self.currentNode) # Set the persons current node to the node they're at
                person.setTravellingOn(None)

                # Position the person offset to the node
                person.pos = (self.currentNode.pos - self.currentNode.offset) + person.offset
                person.rect.topleft = person.pos * self.game.renderer.getScale() * self.spriteRenderer.getFixedScale()
                person.moveStatusIndicator()


    #move all the people within the transport relative to its location
    def movePeople(self):
        if len(self.people) <= 0:
            return

        for person in self.people:
            person.pos = self.pos + person.offset
            person.rect.topleft = person.pos * self.game.renderer.getScale() * self.spriteRenderer.getFixedScale()
            person.moveStatusIndicator()

            # Check if the person has reached their destination and if they have remove
            if person.getDestination().getNumber() == self.currentNode.getNumber():
                person.complete()    
                self.removePerson(person)            


    # Draw how long is left at each stop 
    def drawTimer(self):
        scale = self.game.renderer.getScale() * self.spriteRenderer.getFixedScale()

        # Arc Indicator 
        offx = 0.01
        step = self.timer / (self.timerLength / 2) + 0.02
        for x in range(6):
            pygame.draw.arc(self.game.renderer.gameDisplay, YELLOW, ((self.pos.x - 4) * scale, (self.pos.y - 4) * scale, (self.width + 8) * scale, (self.height + 8) * scale), math.pi / 2 + offx, math.pi / 2 + math.pi * step, 8)
            offx += 0.01


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


    def drawOutline(self, surface):
        scale = self.game.renderer.getScale() * self.spriteRenderer.getFixedScale()

        offx = 0.01
        for x in range(6):
            pygame.draw.arc(surface, YELLOW, ((self.pos.x - 2) * scale, (self.pos.y - 2) * scale, (self.width + 4) * scale, (self.height + 4) * scale), math.pi / 2 + offx, math.pi / 2, int(4 * scale))
            
            offx += 0.02


    def __render(self):
        self.dirty = False

        self.image = self.game.imageLoader.getImage(self.imageName)
        self.image = pygame.transform.smoothscale(self.image, (int(self.width * self.game.renderer.getScale() * self.spriteRenderer.getFixedScale()), 
                                                            int(self.height * self.game.renderer.getScale() * self.spriteRenderer.getFixedScale())))
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos * self.game.renderer.getScale() * self.spriteRenderer.getFixedScale()



    def draw(self):
        if self.dirty or self.image is None: self.__render()
        self.game.renderer.addSurface(self.image, (self.rect))

        if self.timer > 0:
            #draw the time indicator
            self.drawTimer()
        
        if self.clickManager.getTransport() == self:
            self.drawPath()
            self.game.renderer.addSurface(None, None, self.drawOutline)


    def events(self):
        mx, my = pygame.mouse.get_pos()
        mx -= self.game.renderer.getDifference()[0]
        my -= self.game.renderer.getDifference()[1]


        if not self.rect.collidepoint((mx, my)) and self.game.clickManager.getClicked():
            self.clickManager.setTransport(None)

        if self.rect.collidepoint((mx, my)) and self.game.clickManager.getClicked():
            for person in self.currentNode.getPeople():
                if person.getMouseOver():
                    return

            # Click off the person (if selected)
            if self.personClickManager.getPerson() is not None:
                self.personClickManager.setPerson(None)

            self.clickManager.setTransport(self)

            self.game.clickManager.setClicked(False)

        # Hover over event
        if self.rect.collidepoint((mx, my)) and not self.mouseOver:
            # hover over a node when transport is hovered over, unset the hover on the node
            if self.currentNode.getMouseOver():
                self.currentNode.setMouseOver(False)

            for person in self.currentNode.getPeople() + self.people:
                if person.getMouseOver():
                    return
            

            self.image.fill(HOVERGREY, special_flags=BLEND_MIN)
            self.mouseOver = True 

        # Hover out event
        if not self.rect.collidepoint((mx, my)) and self.mouseOver:
            self.mouseOver = False
            self.dirty = True


    def update(self):
        if hasattr(self, 'rect') and self.running:
            self.events()

            # Reset velocity to prevent infinate movement
            self.vel = vec(0, 0)

            # if the path is set follow it, only if the transport is not stopped at a stop
            if len(self.path) > 0 and self.moving:
                path = self.path[0]

                dxy = (path.pos - path.offset) - self.pos + self.offset
                dis = dxy.length()

                if dis >= 0.5 and self.moving:
                    # if its the last node in the path, slow down if the last node is a stop
                    if len(self.path) <= 1: 
                        if dis <= 15 and isinstance(self.currentConnection.getTo(), self.stopType):
                            self.vel = (dxy * (self.speed / 10)) * self.game.dt * self.spriteRenderer.getDt()
                        else:
                            self.vel = dxy / dis * float(self.speed) * self.game.dt * self.spriteRenderer.getDt()
                            
                    else:
                        self.vel = dxy / dis * float(self.speed) * self.game.dt * self.spriteRenderer.getDt()

                    self.movePeople()

                else:
                    # set the current connection to be one of the paths connections (just pick a random one)
                    if len(self.path) > 1:
                        fromNode = path.getConnections()[0].getFrom().getNumber()
                        toNode = self.path[1].getNumber()

                        for connection in path.getConnections():
                            if connection.getFrom().getNumber() == fromNode and connection.getTo().getNumber() == toNode:
                                self.currentConnection = connection
                                break

                        self.currentNode.removeTransport(self)
                        self.currentNode = self.currentConnection.getFrom()
                        self.currentNode.addTransport(self)

                    self.path.remove(path)

                self.pos += self.vel
                self.rect.topleft = self.pos * self.game.renderer.getScale() * self.spriteRenderer.getFixedScale()

            else:
                dxy = (self.currentConnection.getTo().pos - self.currentConnection.getTo().offset) - self.pos + self.offset
                dis = dxy.length()
                
                if dis >= 0.5 and self.moving: #move towards the node
                    # Speed up when leaving a stop
                    # Change the number taken away from the length of the connection for the length of the smooth starting 
                    # Change the other number to say when the smooth starting should begin (after how many pixels)
                    if dis >= self.currentConnection.getDistance() - 15 and dis <= self.currentConnection.getLength().length() - 0.5 and isinstance(self.currentNode, self.stopType):
                        self.vel = (-(self.currentConnection.getLength() + dxy) * (self.speed / 12)) * self.game.dt * self.spriteRenderer.getDt()

                    # Slow down when reaching a stop
                    # Change what number the distance is smaller than for the length of smooth stopping; larger lengths may make transport further from target
                    elif dis <= 15 and isinstance(self.currentConnection.getTo(), self.stopType):
                        self.vel = (dxy * (self.speed / 10)) * self.game.dt * self.spriteRenderer.getDt()

                    else:
                        self.vel = dxy / dis * float(self.speed) * self.game.dt * self.spriteRenderer.getDt()
                    self.movePeople()

                else: #its reached the node
                    self.setNextConnection()
                    self.pos = (self.currentConnection.getFrom().pos - self.currentConnection.getFrom().offset) + self.offset

                self.pos += self.vel
                self.rect.topleft = self.pos * self.game.renderer.getScale() * self.spriteRenderer.getFixedScale()


class Taxi(Transport):
    def __init__(self, spriteRenderer, groups, currentConnection, running, clickManager, personClickManager):
        super().__init__(spriteRenderer, groups, currentConnection, running, clickManager, personClickManager)

        self.imageName = "taxi"
        self.stopType = NODE.Node

        #self.timerLength = 200 # To Do: choose a value length

        self.hasStopped = False

    # override
    def setPeopleBoarding(self):
        # If theres no one at the station, dont bother trying to add anyone
        if len(self.currentNode.getPeople()) <= 0:
            return

        for person in self.currentNode.getPeople():
            if person.getStatus() == PERSON.Person.Status.FLAG: # If they're waiting for the train
                person.setStatus(PERSON.Person.Status.BOARDING)


    # override 
    def setNextConnection(self):
        nextNode = self.currentConnection.getTo()
        
        # If the transport is moving, set its next connection to the next upcoming node
        if self.moving:
            self.setConnection(nextNode)
            self.hasStopped = False


        if isinstance(self.currentNode, self.stopType) and self.checkTaxiStop(self.currentNode) or self.hasStopped:

            # Set people waiting for the transportation to departing 
            self.setPeopleBoarding()

            self.moving = False
            self.timer += 100 * self.game.dt * self.spriteRenderer.getDt()

            # Leaving the station
            if self.timer > self.timerLength:
                self.moving = True
                self.timer = 0

                # Add the people boarding to the transportation
                self.addPeople()


        elif isinstance(self.currentNode, self.stopType) and self.checkPersonStop(self.currentNode):
            # Remove anyone departing before we add new people
            self.removePeople()
            # Do I want to show the timer here?


    def checkTaxiStop(self, node):
        # only stop if there is someone flagging the taxi down, dont stop if the taxi is already carrying someone 
        if len(node.getPeople()) <= 0 or len(self.people) >= 1:
            return False

        for person in node.getPeople():
            if person.getStatus() == PERSON.Person.Status.FLAG or person.getStatus() == PERSON.Person.Status.BOARDING:
                self.hasStopped = True
                return True
        return False


    def checkPersonStop(self, node):
        if len(self.people) <= 0:
            return False

        for person in self.people:
            if person.getStatus() == PERSON.Person.Status.DEPARTING:
                self.hasStopped = True
                return True
        return False


    # override
    def update(self):
        if hasattr(self, 'rect') and self.running:
            self.events()
            self.vel = vec(0, 0)

            if len(self.path) > 0 and self.moving:
                path = self.path[0]

                dxy = (path.pos - path.offset) - self.pos + self.offset
                dis = dxy.length()

                if dis >= 0.5 and self.moving:
                    # if its the last node in the path, slow down if the last node is a stop
                    if len(self.path) <= 1: 
                        if dis <= 15 and isinstance(self.currentConnection.getTo(), self.stopType):
                            if self.checkTaxiStop(self.currentConnection.getTo()) or self.checkPersonStop(self.currentConnection.getTo()):
                                self.vel = (dxy * (self.speed / 10)) * self.game.dt * self.spriteRenderer.getDt()
                            else:
                                self.vel = dxy / dis * float(self.speed) * self.game.dt * self.spriteRenderer.getDt()
                       
                        else:
                            self.vel = dxy / dis * float(self.speed) * self.game.dt * self.spriteRenderer.getDt()
                            
                    else:
                        self.vel = dxy / dis * float(self.speed) * self.game.dt * self.spriteRenderer.getDt()

                    self.movePeople()

                else:
                    if len(self.path) > 1:
                        fromNode = path.getConnections()[0].getFrom().getNumber()
                        toNode = self.path[1].getNumber()

                        for connection in path.getConnections():
                            if connection.getFrom().getNumber() == fromNode and connection.getTo().getNumber() == toNode:
                                self.currentConnection = connection
                                break

                        self.currentNode.removeTransport(self)
                        self.currentNode = self.currentConnection.getFrom()
                        self.currentNode.addTransport(self)

                    self.path.remove(path)

                self.pos += self.vel
                self.rect.topleft = self.pos * self.game.renderer.getScale() * self.spriteRenderer.getFixedScale()

            else:
                dxy = (self.currentConnection.getTo().pos - self.currentConnection.getTo().offset) - self.pos + self.offset
                dis = dxy.length()

                if dis >= 0.5 and self.moving: #move towards the node
                    # speed up when leaving
                    if dis >= self.currentConnection.getDistance() - 15 and dis <= self.currentConnection.getLength().length() - 0.5 and isinstance(self.currentNode, self.stopType):
                        if self.checkTaxiStop(self.currentNode) or self.checkPersonStop(self.currentNode) or self.hasStopped:
                            self.vel = (-(self.currentConnection.getLength() + dxy) * (self.speed / 12)) * self.game.dt * self.spriteRenderer.getDt()
                        else:
                            self.vel = dxy / dis * float(self.speed) * self.game.dt * self.spriteRenderer.getDt()

                    # slow down when stopping
                    elif dis <= 15 and isinstance(self.currentConnection.getTo(), self.stopType):
                        if self.checkTaxiStop(self.currentConnection.getTo()) or self.checkPersonStop(self.currentConnection.getTo()):
                            self.vel = (dxy * (self.speed / 10)) * self.game.dt * self.spriteRenderer.getDt()
                        else:
                            self.vel = dxy / dis * float(self.speed) * self.game.dt * self.spriteRenderer.getDt()
                            
                    else:
                        self.vel = dxy / dis * float(self.speed) * self.game.dt * self.spriteRenderer.getDt()

                    self.movePeople()

                else: # At the node
                    self.setNextConnection()
                    self.pos = (self.currentConnection.getFrom().pos - self.currentConnection.getFrom().offset) + self.offset
                
                self.pos += self.vel
                self.rect.topleft = self.pos * self.game.renderer.getScale() * self.spriteRenderer.getFixedScale()



class Bus(Transport):
    def __init__(self, spriteRenderer, groups, currentConnection, running, clickManager, personClickManager):
        super().__init__(spriteRenderer, groups, currentConnection, running, clickManager, personClickManager)
        self.imageName = "bus"
        self.stopType = NODE.BusStop



class Tram(Transport):
    def __init__(self, spriteRenderer, groups, currentConnection, running, clickManager, personClickManager):
        super().__init__(spriteRenderer, groups, currentConnection, running, clickManager, personClickManager)
        self.imageName = "tram"
        self.stopType = NODE.TramStop


class Metro(Transport):
    def __init__(self, spriteRenderer, groups, currentConnection, running, clickManager, personClickManager):
        super().__init__(spriteRenderer, groups, currentConnection, running, clickManager, personClickManager)
