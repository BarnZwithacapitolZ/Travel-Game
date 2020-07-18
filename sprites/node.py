import pygame
from pygame.locals import *
import pygame.gfxdraw
from config import *
import os
import math

import clickManager as CLICKMANAGER
import person as PERSON

vec = pygame.math.Vector2

class Node(pygame.sprite.Sprite):
    def __init__(self, game, groups, number, connectionType, x, y, clickManager):
        self.groups = groups
        super().__init__(self.groups)

        self.game = game
        self.number = number
        self.connectionType = connectionType
        self.clickManager = clickManager
        self.width = 20
        self.height = 20

        self.offset = vec(0, 0)
        self.pos = vec(x, y) + self.offset

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


    #### Getters ####

    # Return the connections, in a list, of the node
    def getConnections(self):
        return self.connections


    # Return the connection type of the node
    def getConnectionType(self):
        return self.connectionType


    # Return the transports at the node -- is this even used??
    def getTransports(self):
        return self.transports


    # Return the people, as a list, currently at the node
    def getPeople(self):
        return self.people


    # Return the node number
    def getNumber(self):
        return self.number


    def getMouseOver(self):
        return self.mouseOver


    #### Setters ####

    def setCurrentImage(self, image):
        self.currentImage = image
        self.dirty = True

    # Add a connection to the node
    def addConnection(self, connection):
        self.connections.append(connection)

    
    def setConnections(self, connections = []):
        self.connections = connections


    def setTransports(self, transports = []):
        self.transports = transports


    # Add a transport to the node
    def addTransport(self, transport):
        self.transports.append(transport)


    # Add a person to the node
    def addPerson(self, person):
        self.people.append(person)


    def remove(self):
        self.kill()


    # Remove a person from the node
    def removePerson(self, person):
        if person not in self.people:
            return

        self.people.remove(person)

    def removeTransport(self, transport):
        if transport not in self.transports:
            return

        self.transports.remove(transport)


    def removeConnection(self, connection):
        self.connections.remove(connection)


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


    def events(self):
        mx, my = pygame.mouse.get_pos()
        mx -= self.game.renderer.getDifference()[0]
        my -= self.game.renderer.getDifference()[1]

        if self.rect.collidepoint((mx, my)) and self.game.clickManager.getClicked() and self.clickManager.getPerson() is not None:
            # Prevent the node and the player from being pressed at the same time
            for person in self.people:
                if person.getMouseOver() and person != self.clickManager.getPerson():
                    return
                    
            # If the player is moving on a transport, dont allow them to select a node
            if self.clickManager.getPerson().getStatus() != PERSON.Person.Status.MOVING and self.clickManager.getPerson().getStatus() != PERSON.Person.Status.DEPARTING:
                self.clickManager.setNode(self)
                self.game.clickManager.setClicked(False)


        if self.rect.collidepoint((mx, my)) and not self.mouseOver and self.clickManager.getPerson() is not None:
            # Prevent the node and the player from being pressed at the same time
            for person in self.people:
                if person.getMouseOver() and person != self.clickManager.getPerson():
                    return

            # If the player is moving on a transport, dont show hovering over a node 
            if self.clickManager.getPerson().getStatus() != PERSON.Person.Status.MOVING and self.clickManager.getPerson().getStatus() != PERSON.Person.Status.DEPARTING:
                self.mouseOver = True
                self.currentImage = 1
                self.dirty = True

            # print(self.number)
            # print(self.people)

            # for connection in self.connections:
            #     print("From " + str(connection.getFrom().number) + ", To " + str(connection.getTo().number) + ", Length " + str(connection.getDistance()) + ', direction ' + str(connection.getDirection()))
        
        
        if not self.rect.collidepoint((mx, my)) and self.mouseOver:
            self.mouseOver = False
            self.currentImage = 0
            self.dirty = True


    def update(self):
        if not self.dirty:
            self.events()



class EditorNode(Node):
    def __init__(self, game, groups, number, connectionType, x, y, clickManager):
        super().__init__(game, groups, number, connectionType, x, y, clickManager)

        self.images = ["node", "nodeSelected", "nodeStart", "nodeEnd"]


    # Override the events function
    def events(self):
        mx, my = pygame.mouse.get_pos()
        mx -= self.game.renderer.getDifference()[0]
        my -= self.game.renderer.getDifference()[1]

        if not self.rect.collidepoint((mx, my)) and self.game.clickManager.getClicked():
            # Unset the clicked on node
            pass

        # Cant click on a node in the top layer
        if self.rect.collidepoint((mx, my)) and self.game.clickManager.getClicked() and self.game.mapEditor.getLayer() != 4 and self.game.mapEditor.getAllowEdits():
            self.game.clickManager.setClicked(False)

            if self.clickManager.getClickType() == CLICKMANAGER.EditorClickManager.ClickType.CONNECTION:    # Add a connection
                self.clickManager.setStartNode(self) if self.clickManager.getStartNode() is None else self.clickManager.setEndNode(self)
            elif self.clickManager.getClickType() == CLICKMANAGER.EditorClickManager.ClickType.TRANSPORT:   # Add a transport
                self.clickManager.addTransport(self)
            elif self.clickManager.getClickType() == CLICKMANAGER.EditorClickManager.ClickType.STOP:        # Add a stop                       
                self.clickManager.addStop(self)
            elif self.clickManager.getClickType() == CLICKMANAGER.EditorClickManager.ClickType.DESTINATION: # Add a destination
                self.clickManager.addDestination(self)
            elif self.clickManager.getClickType() == CLICKMANAGER.EditorClickManager.ClickType.DTRANSPORT:  # Delete a transport
                self.clickManager.deleteTransport(self)
            elif self.clickManager.getClickType() == CLICKMANAGER.EditorClickManager.ClickType.DSTOP:       # Delete a stop
                self.clickManager.deleteStop(self)
            elif self.clickManager.getClickType() == CLICKMANAGER.EditorClickManager.ClickType.DDESTINATION:# Delete a destination
                self.clickManager.deleteDestination(self)
 
        if self.rect.collidepoint((mx, my)) and not self.mouseOver and self.clickManager.getStartNode() != self and self.game.mapEditor.getLayer() != 4 and self.game.mapEditor.getAllowEdits():
            self.mouseOver = True
            self.currentImage = 1
            self.dirty = True

            # for connection in self.connections:
            #     print("From " + str(connection.getFrom().number) + ", To " + str(connection.getTo().number) + ", Length " + str(connection.getDistance()) + ', direction ' + str(connection.getDirection()) + ", Layer " + connection.getType())

        if not self.rect.collidepoint((mx, my)) and self.mouseOver and self.clickManager.getStartNode() != self and self.game.mapEditor.getLayer() != 4:
            self.mouseOver = False
            self.currentImage = 0
            self.dirty = True




class EntranceNode(Node):
    def __init__(self, game, groups, number, connectionType, x, y, clickManager):
        super().__init__(game, groups, number, connectionType, x, y, clickManager)
        print(self.number)

    # Empty draw function so its a hidden node
    def draw(self):
        pass



# To Do: Parent class for all stops
class Stop(Node):
    def __init__(self, game, groups, number, connectionType, x, y, clickManager):
        super().__init__(game, groups, number, connectionType, x, y, clickManager)
        self.width = 25
        self.height = 25
        self.offset = vec(-2.5, -2.5)
        self.pos = self.pos + self.offset


class BusStop(Stop):
    def __init__(self, game, groups, number, connectionType, x, y, clickManager):
        super().__init__(game, groups, number, connectionType, x, y, clickManager)
        self.images = ["busStation", "nodeSelected"]


class EditorBusStop(EditorNode, BusStop):
    def __init__(self, game, groups, number, connectionType, x, y, clickManager):
        super().__init__(game, groups, number, connectionType, x, y, clickManager)
        self.images = ["busStation", "nodeSelected", "nodeStart", "nodeEnd"]


class MetroStation(Stop):
    def __init__(self, game, groups, number, connectionType, x, y, clickManager):
        super().__init__(game, groups, number, connectionType, x, y, clickManager)
        self.images = ["metro", "nodeSelected"]


class EditorMetroStation(EditorNode, MetroStation):
    def __init__(self, game, groups, number, connectionType, x, y, clickManager):
        super().__init__(game, groups, number, connectionType, x, y, clickManager)
        self.images = ["metro", "nodeSelected", "nodeStart", "nodeEnd"]


class TramStop(Stop):
    def __init__(self, game, groups, number, connectionType, x, y, clickManager):
        super().__init__(game, groups, number, connectionType, x, y, clickManager)
        self.images = ["tramStation", "nodeSelected"]


class EditorTramStop(EditorNode, TramStop):
    def __init__(self, game, groups, number, connectionType, x, y, clickManager):
        super().__init__(game, groups, number, connectionType, x, y, clickManager)
        self.images = ["tramStation", "nodeSelected", "nodeStart", "nodeEnd"]



class Destination(Node):
    def __init__(self, game, groups, number, connectionType, x, y, clickManager):
        super().__init__(game, groups, number, connectionType, x, y, clickManager)
        self.width = 30
        self.height = 30
        self.offset = vec(-5, -5)
        self.pos = self.pos + self.offset



class Airport(Destination):
    def __init__(self, game, groups, number, connectionType, x, y, clickManager):
        super().__init__(game, groups, number, connectionType, x, y, clickManager)
        self.images = ["airport", "nodeSelected"]


class EditorAirport(EditorNode, Airport):
    def __init__(self, game, groups, number, connectionType, x, y, clickManager):
        super().__init__(game, groups, number, connectionType, x, y, clickManager)
        self.images = ["airport", "nodeSelected", "nodeStart", "nodeEnd"]


class Office(Destination):
    def __init__(self, game, groups, number, connectionType, x, y, clickManager):
        super().__init__(game, groups, number, connectionType, x, y, clickManager)
        self.images = ["office", "nodeSelected"]
        
class EditorOffice(EditorNode, Office):
    def __init__(self, game, groups, number, connectionType, x, y, clickManager):
        super().__init__(game, groups, number, connectionType, x, y, clickManager)

        self.images = ["office", "nodeSelected", "nodeStart", "nodeEnd"]



