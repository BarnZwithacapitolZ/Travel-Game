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
        super().__init__(self.groups)

        self.game = game
        self.number = number
        self.connectionType = connectionType
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


    # Add a transport to the node
    def addTransport(self, transport):
        self.transports.append(transport)


    # Add a person to the node
    def addPerson(self, person):
        self.people.append(person)


    # Remove a person from the node
    def removePerson(self, person):
        if person not in self.people:
            return

        self.people.remove(person)


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

        if self.rect.collidepoint((mx, my)) and self.game.clickManager.getClicked() and self.game.clickManager.getPerson() is not None:
            # Prevent the node and the player from being pressed at the same time
            for person in self.people:
                if person.getMouseOver() and person != self.game.clickManager.getPerson():
                    return
                    
            # If the player is moving on a transport, dont allow them to select a node
            if self.game.clickManager.getPerson().getStatusValue() != 4 and self.game.clickManager.getPerson().getStatusValue() != 5:
                self.game.clickManager.setNode(self)
                self.game.clickManager.setClicked(False)

        if self.rect.collidepoint((mx, my)) and not self.mouseOver and self.game.clickManager.getPerson() is not None:
            # Prevent the node and the player from being pressed at the same time
            for person in self.people:
                if person.getMouseOver() and person != self.game.clickManager.getPerson():
                    return

            # If the player is moving on a transport, dont show hovering over a node 
            if self.game.clickManager.getPerson().getStatusValue() != 4 and self.game.clickManager.getPerson().getStatusValue() != 5:
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
    def __init__(self, game, groups, number, connectionType, x, y, connectionManager):
        super().__init__(game, groups, number, connectionType, x, y)

        self.connectionManager = connectionManager
        self.images = ["node", "nodeSelected", "nodeStart", "nodeEnd"]


    # Override the events function
    def events(self):
        mx, my = pygame.mouse.get_pos()
        mx -= self.game.renderer.getDifference()[0]
        my -= self.game.renderer.getDifference()[1]

        
        if self.rect.collidepoint((mx, my)) and self.game.clickManager.getClicked() and self.game.mapEditor.getLayer() != 4:
            self.game.clickManager.setClicked(False)

            if self.connectionManager.getStartNode() is None:
                self.connectionManager.setStartNode(self)
            else:
                self.connectionManager.setEndNode(self)

        if self.rect.collidepoint((mx, my)) and not self.mouseOver and self.connectionManager.getStartNode() != self and self.game.mapEditor.getLayer() != 4:
            self.mouseOver = True
            self.currentImage = 1
            self.dirty = True

            for connection in self.connections:
                print("From " + str(connection.getFrom().number) + ", To " + str(connection.getTo().number) + ", Length " + str(connection.getDistance()) + ', direction ' + str(connection.getDirection()) + ", Layer " + connection.getType())

        if not self.rect.collidepoint((mx, my)) and self.mouseOver and self.connectionManager.getStartNode() != self and self.game.mapEditor.getLayer() != 4:
            self.mouseOver = False
            self.currentImage = 0
            self.dirty = True




class BusStop(Node):
    def __init__(self, game, groups, number, connectionType, x, y):
        super().__init__(game, groups, number, connectionType, x, y)
        self.width = 25
        self.height = 25
        self.offset = vec(-2.5, -2.5)
        self.pos = self.pos + self.offset
        self.images = ["busStation", "nodeSelected"]


class EditorBusStop(EditorNode, BusStop):
    def __init__(self, game, groups, number, connectionType, x, y, connectionManager):
        super().__init__(game, groups, number, connectionType, x, y, connectionManager)

        self.images = ["busStation", "nodeSelected", "nodeStart", "nodeEnd"]


class MetroStation(Node):
    def __init__(self, game, groups, number, connectionType, x, y):
        super().__init__(game, groups, number, connectionType, x, y)

        self.width = 25
        self.height = 25
        self.offset = vec(-2.5, -2.5)
        self.pos = self.pos + self.offset
        self.images = ["metro", "nodeSelected"]


class EditorMetroStation(EditorNode, MetroStation):
    def __init__(self, game, groups, number, connectionType, x, y, connectionManager):
        super().__init__(game, groups, number, connectionType, x, y, connectionManager)

        self.images = ["metro", "nodeSelected", "nodeStart", "nodeEnd"]

