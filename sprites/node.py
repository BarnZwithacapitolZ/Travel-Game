import pygame
import pygame.gfxdraw
import math
import personHolder
import clickManager as CLICKMANAGER
import person as PERSON
from pygame.locals import BLEND_MIN
from config import YELLOW, HOVERGREY
from enum import Enum

vec = pygame.math.Vector2


class NodeType(Enum):
    REGULAR = "regular"

    # Stop types
    STOP = "stops"
    BUSSTOP = "bus"
    METROSTATION = "metro"
    TRAMSTOP = "tram"

    # Destination (location) types
    DESTINATION = "destinations"
    AIRPORT = "airport"
    OFFICE = "office"
    HOUSE = "house"
    SCHOOL = "school"
    SHOP = "shop"

    # Special node types
    SPECIAL = "specials"
    NOWALKNODE = "noWalkNode"

    # Return a list of all the type nodes
    @classmethod
    def aslist(cls):
        return [cls.REGULAR, cls.STOP, cls.DESTINATION, cls.SPECIAL]


class Node(pygame.sprite.Sprite):
    def __init__(
            self, spriteRenderer, groups, number, connectionType, x, y,
            personClickManager, transportClickManager):
        self.groups = groups
        super().__init__(self.groups)

        self.spriteRenderer = spriteRenderer
        self.game = self.spriteRenderer.game
        self.number = number
        self.connectionType = connectionType
        self.personClickManager = personClickManager
        self.transportClickManager = transportClickManager
        self.width = 20
        self.height = 20

        self.offset = vec(0, 0)
        self.pos = vec(x, y) + self.offset

        # All connections to / from this node
        self.connections = []

        # All transport currently at this node
        self.transports = []

        # All people currently at this node
        self.people = []
        self.personHolder = personHolder.PersonHolder(
            self.game, self.groups, self,
            self.spriteRenderer.getPersonHolderClickManager())

        # Node Type definition
        self.type = NodeType.REGULAR
        self.subType = NodeType.REGULAR

        self.dirty = True

        self.mouseOver = False
        self.images = ["node"]
        self.currentImage = 0

    @staticmethod
    def checkRegularNode(node):
        instances = [NodeType.STOP, NodeType.DESTINATION, NodeType.SPECIAL]
        for instance in instances:
            if node.getType() == instance:
                return False
        return True

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

    def getPersonHolder(self):
        return self.personHolder

    def getType(self):
        return self.type

    def getSubType(self):
        return self.subType

    def setCurrentImage(self, image):
        self.currentImage = image
        self.dirty = True

    # Add a connection to the node
    def addConnection(self, connection):
        self.connections.append(connection)

    def setConnections(self, connections=[]):
        self.connections = connections

    def setTransports(self, transports=[]):
        self.transports = transports

    def setMouseOver(self, mouseOver):
        self.mouseOver = mouseOver
        self.dirty = True

    # Add a transport to the node
    def addTransport(self, transport):
        self.transports.append(transport)

    def remove(self):
        self.kill()

    # Add a person to the node
    def addPerson(self, person):
        if person in self.people:
            return

        self.people.append(person)

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

    def drawOutline(self, color=YELLOW):
        scale = (
            self.game.renderer.getScale()
            * self.spriteRenderer.getFixedScale())

        offx = 0.01
        for x in range(1):
            pygame.draw.arc(
                self.game.renderer.gameDisplay, color, (
                    (self.pos.x - 1) * scale, (self.pos.y - 1) * scale,
                    (self.width + 2) * scale, (self.height + 2) * scale),
                math.pi / 2 + offx, math.pi / 2, int(3.5 * scale))

            offx += 0.02

    def __render(self):
        self.dirty = False

        self.image = self.game.imageLoader.getImage(
            self.images[self.currentImage],
            (self.width * self.spriteRenderer.getFixedScale(),
                self.height * self.spriteRenderer.getFixedScale()))

        self.rect = self.image.get_rect()

        self.rect.topleft = (
            self.pos * self.game.renderer.getScale()
            * self.spriteRenderer.getFixedScale())

    def makeSurface(self):
        if self.dirty or self.image is None:
            self.__render()

    def drawPaused(self, surface):
        self.makeSurface()
        surface.blit(self.image, (self.rect))

    def draw(self):
        self.makeSurface()
        self.game.renderer.addSurface(self.image, (self.rect))

        # if self.personClickManager.getNode() == self:
        #     self.game.renderer.addSurface(None, None, self.drawOutline)

    def events(self):
        mx, my = pygame.mouse.get_pos()
        difference = self.game.renderer.getDifference()
        mx -= difference[0]
        my -= difference[1]

        # click event; setting the node for the transport
        if (self.rect.collidepoint((mx, my))
                and self.game.clickManager.getRightClicked()
                and self.transportClickManager.getTransport() is not None):
            self.transportClickManager.setNode(self)
            self.game.clickManager.setRightClicked(False)

        # Click event; setting the node for the person
        if (self.rect.collidepoint((mx, my))
                and self.game.clickManager.getRightClicked()
                and self.personClickManager.getPerson() is not None):
            # Prevent the node and the player from being
            # pressed at the same time
            for person in self.people:
                if person.getMouseOver():
                    return

            if len(self.transports) > 0:
                # check the route returned is []
                # If the route is impossible press the transport,
                # otherwise press the node
                routeLength = (len(self.personClickManager.pathFinding(
                    self.personClickManager.getPerson().getCurrentNode(),
                    self)))

                if routeLength <= 0:
                    # Prioratize pressing the transport instead of a node
                    # (if the transport is on a node)
                    for transport in self.transports:
                        if transport.getMouseOver():
                            return

            # If the player is moving on a transport,
            # dont allow them to select a node
            if (self.personClickManager.getPerson().getStatus()
                    != PERSON.Person.Status.MOVING
                    and self.personClickManager.getPerson().getStatus()
                    != PERSON.Person.Status.DEPARTING):

                self.personClickManager.setNode(self)
                self.game.clickManager.setRightClicked(False)

        # Hover over event; for transport
        if (self.rect.collidepoint((mx, my))
                and not self.mouseOver
                and self.transportClickManager.getTransport() is not None):
            # Prevent the node and the player from being hovered over
            # at the same time
            for person in self.people:
                if person.getMouseOver():
                    return

            self.mouseOver = True
            self.image.fill(HOVERGREY, special_flags=BLEND_MIN)

        # Hover over event; for person
        if (self.rect.collidepoint((mx, my))
                and not self.mouseOver
                and self.personClickManager.getPerson() is not None):
            # Prevent the node and the player from being pressed
            # at the same time
            for person in self.people:
                if person.getMouseOver():
                    return

            # If the player is moving on a transport,
            # dont show hovering over a node
            if (self.personClickManager.getPerson().getStatus()
                    != PERSON.Person.Status.MOVING
                    and self.personClickManager.getPerson().getStatus()
                    != PERSON.Person.Status.DEPARTING):
                self.mouseOver = True
                self.image.fill(HOVERGREY, special_flags=BLEND_MIN)

        # Hover out event
        if not self.rect.collidepoint((mx, my)) and self.mouseOver:
            self.mouseOver = False
            self.currentImage = 0
            self.dirty = True

    def update(self):
        if not self.dirty and not self.spriteRenderer.getPaused():
            self.events()


class EditorNode(Node):
    def __init__(
            self, spriteRenderer, groups, number, connectionType, x, y,
            clickManager, personClickManager, transportClickManager):
        super().__init__(
            spriteRenderer, groups, number, connectionType, x, y,
            personClickManager, transportClickManager)
        self.clickManager = clickManager
        self.images = ["node", "nodeStart", "nodeEnd"]

    # Override the events function
    def events(self):
        mx, my = pygame.mouse.get_pos()
        difference = self.game.renderer.getDifference()
        mx -= difference[0]
        my -= difference[1]

        # Cant click on a node in the top layer
        if (self.rect.collidepoint((mx, my))
                and self.game.clickManager.getClicked()
                and self.game.mapEditor.getAllowEdits()):  # click event
            self.game.clickManager.setClicked(False)

            if (self.game.mapEditor.getCurrentLayer() != 4
                    or self.game.mapEditor.getPreviousLayer() is not None):
                node = self
                # If they are on the preview layer,
                # get the preview node from the top layer
                if self.game.mapEditor.getPreviousLayer() is not None:
                    node = self.spriteRenderer.getNodeFromDifferentLayer(
                        self, self.game.mapEditor.getPreviousLayer())

                # Only want to check click events if we know the node exists
                if node is None:
                    return

                # Add a connection
                if (self.clickManager.getClickType()
                        ==
                        CLICKMANAGER.EditorClickManager.ClickType.CONNECTION):
                    # Set the preview start node if its on the top layer
                    if self != node:
                        (self.clickManager.setPreviewStartNode(self)
                            if self.clickManager.getPreviewStartNode() is None
                            else self.clickManager.setPreviewEndNode(self))

                    # If its the preview node we want to make it mouseover
                    # to change the image to the same as the node below it
                    node.mouseOver = True
                    (self.clickManager.setStartNode(node)
                        if self.clickManager.getStartNode() is None
                        else self.clickManager.setEndNode(node))

                # Add a transport
                elif (self.clickManager.getClickType()
                        ==
                        CLICKMANAGER.EditorClickManager.ClickType.TRANSPORT):
                    self.clickManager.addTransport(node)

                # Add a stop
                elif (self.clickManager.getClickType()
                        == CLICKMANAGER.EditorClickManager.ClickType.STOP):
                    self.clickManager.addNode(node, NodeType.STOP.value)

                # Add a destination
                elif (self.clickManager.getClickType()
                        ==
                        CLICKMANAGER.EditorClickManager.ClickType.DESTINATION):
                    self.clickManager.addNode(node, NodeType.DESTINATION.value)

                # Add a special node type
                elif (self.clickManager.getClickType()
                        ==
                        CLICKMANAGER.EditorClickManager.ClickType.SPECIAL):
                    self.clickManager.addNode(node, NodeType.SPECIAL.value)

                # Delete a transport
                elif (self.clickManager.getClickType()
                        ==
                        CLICKMANAGER.EditorClickManager.ClickType.DTRANSPORT):
                    self.clickManager.deleteTransport(node)

                # Delete a Node type (stops, destinations, special etc.)
                elif (self.clickManager.getClickType()
                        == CLICKMANAGER.EditorClickManager.ClickType.DNODE):
                    self.clickManager.deleteNode(node)

            else:
                self.spriteRenderer.messageSystem.addMessage(
                    "You cannot place items on the top layer!")

        # hover over event
        elif (self.rect.collidepoint((mx, my)) and not self.mouseOver
                and self.clickManager.getStartNode() != self
                and self.clickManager.getPreviewStartNode() != self
                and (
                    self.game.mapEditor.getCurrentLayer() != 4
                    or self.game.mapEditor.getPreviousLayer() is not None)
                and self.game.mapEditor.getAllowEdits()):  # Hover over event
            self.mouseOver = True
            self.image.fill(HOVERGREY, special_flags=BLEND_MIN)

            if self.clickManager.getStartNode() is not None:
                node = self
                if self.game.mapEditor.getPreviousLayer() is not None:
                    node = self.spriteRenderer.getNodeFromDifferentLayer(
                        self, self.game.mapEditor.getPreviousLayer())

                if node is not None:
                    self.clickManager.setTempEndNode(node)

        # hover out event
        elif (not self.rect.collidepoint((mx, my)) and self.mouseOver
                and self.clickManager.getStartNode() != self
                and self.clickManager.getPreviewStartNode() != self
                and (
                    self.game.mapEditor.getCurrentLayer() != 4
                    or self.game.mapEditor.getPreviousLayer() is not None
        )):  # Hover out event
            self.mouseOver = False
            self.currentImage = 0
            self.dirty = True

            if self.clickManager.getTempEndNode() is not None:
                self.clickManager.removeTempEndNode()


class NoWalkNode(Node):
    def __init__(
            self, spriteRenderer, groups, number, connectionType, x, y,
            personClickManager, transportClickManager):
        super().__init__(
            spriteRenderer, groups, number, connectionType, x, y,
            personClickManager, transportClickManager)
        self.images = ["nodeNoWalking"]
        self.type = NodeType.SPECIAL
        self.subType = NodeType.NOWALKNODE


class EditorNoWalkNode(EditorNode, NoWalkNode):
    def __init__(
            self, spriteRenderer, groups, number, connectionType, x, y,
            clickManager, personClickManager, transportClickManager):
        EditorNode.__init__(
            self, spriteRenderer, groups, number, connectionType, x, y,
            clickManager, personClickManager, transportClickManager)
        NoWalkNode.__init__(
            self, spriteRenderer, groups, number, connectionType, x, y,
            personClickManager, transportClickManager)

        self.images = ["nodeNoWalking", "nodeStart", "nodeEnd"]


# To Do: Parent class for all stops
class Stop(Node):
    def __init__(
            self, spriteRenderer, groups, number, connectionType, x, y,
            personClickManager, transportClickManager):
        super().__init__(
            spriteRenderer, groups, number, connectionType, x, y,
            personClickManager, transportClickManager)
        self.width = 25
        self.height = 25
        self.offset = vec(-2.5, -2.5)
        self.pos = self.pos + self.offset

        self.type = NodeType.STOP
        self.subType = NodeType.STOP


class BusStop(Stop):
    def __init__(
            self, spriteRenderer, groups, number, connectionType, x, y,
            personClickManager, transportClickManager):
        super().__init__(
            spriteRenderer, groups, number, connectionType, x, y,
            personClickManager, transportClickManager)
        self.images = ["busStation"]
        self.subType = NodeType.BUSSTOP


class EditorBusStop(EditorNode, BusStop):
    def __init__(
            self, spriteRenderer, groups, number, connectionType, x, y,
            clickManager, personClickManager, transportClickManager):
        EditorNode.__init__(
            self, spriteRenderer, groups, number, connectionType, x, y,
            clickManager, personClickManager, transportClickManager)
        BusStop.__init__(
            self, spriteRenderer, groups, number, connectionType, x, y,
            personClickManager, transportClickManager)
        self.images = ["busStation", "nodeStart", "nodeEnd"]


class MetroStation(Stop):
    def __init__(
            self, spriteRenderer, groups, number, connectionType, x, y,
            personClickManager, transportClickManager):
        super().__init__(
            spriteRenderer, groups, number, connectionType, x, y,
            personClickManager, transportClickManager)
        self.images = ["trainStation"]
        self.subType = NodeType.METROSTATION


class EditorMetroStation(EditorNode, MetroStation):
    def __init__(
            self, spriteRenderer, groups, number, connectionType, x, y,
            clickManager, personClickManager, transportClickManager):
        EditorNode.__init__(
            self, spriteRenderer, groups, number, connectionType, x, y,
            clickManager, personClickManager, transportClickManager)
        MetroStation.__init__(
            self, spriteRenderer, groups, number, connectionType, x, y,
            personClickManager, transportClickManager)
        self.images = ["trainStation", "nodeStart", "nodeEnd"]


class TramStop(Stop):
    def __init__(
            self, spriteRenderer, groups, number, connectionType, x, y,
            personClickManager, transportClickManager):
        super().__init__(
            spriteRenderer, groups, number, connectionType, x, y,
            personClickManager, transportClickManager)
        self.images = ["tramStation"]
        self.subType = NodeType.TRAMSTOP


class EditorTramStop(EditorNode, TramStop):
    def __init__(
            self, spriteRenderer, groups, number, connectionType, x, y,
            clickManager, personClickManager, transportClickManager):
        EditorNode.__init__(
            self, spriteRenderer, groups, number, connectionType, x, y,
            clickManager, personClickManager, transportClickManager)
        TramStop.__init__(
            self, spriteRenderer, groups, number, connectionType, x, y,
            clickManager, transportClickManager)
        self.images = ["tramStation", "nodeStart", "nodeEnd"]


class Destination(Node):
    def __init__(
            self, spriteRenderer, groups, number, connectionType, x, y,
            personClickManager, transportClickManager):
        super().__init__(
            spriteRenderer, groups, number, connectionType, x, y,
            personClickManager, transportClickManager)
        self.width = 30
        self.height = 30
        self.offset = vec(-5, -5)
        self.pos = self.pos + self.offset

        self.type = NodeType.DESTINATION
        self.subType = NodeType.DESTINATION


class Airport(Destination):
    def __init__(
            self, spriteRenderer, groups, number, connectionType, x, y,
            personClickManager, transportClickManager):
        super().__init__(
            spriteRenderer, groups, number, connectionType, x, y,
            personClickManager, transportClickManager)
        self.images = ["airport"]
        self.subType = NodeType.AIRPORT


class EditorAirport(EditorNode, Airport):
    def __init__(
            self, spriteRenderer, groups, number, connectionType, x, y,
            clickManager, personClickManager, transportClickManager):
        EditorNode.__init__(
            self, spriteRenderer, groups, number, connectionType, x, y,
            clickManager, personClickManager, transportClickManager)
        Airport.__init__(
            self, spriteRenderer, groups, number, connectionType, x, y,
            personClickManager, transportClickManager)
        self.images = ["airport", "nodeStart", "nodeEnd"]


class Office(Destination):
    def __init__(
            self, spriteRenderer, groups, number, connectionType, x, y,
            personClickManager, transportClickManager):
        super().__init__(
            spriteRenderer, groups, number, connectionType, x, y,
            personClickManager, transportClickManager)
        self.images = ["office"]
        self.subType = NodeType.OFFICE


class EditorOffice(EditorNode, Office):
    def __init__(
            self, spriteRenderer, groups, number, connectionType, x, y,
            clickManager, personClickManager, transportClickManager):
        EditorNode.__init__(
            self, spriteRenderer, groups, number, connectionType, x, y,
            clickManager, personClickManager, transportClickManager)
        Office.__init__(
            self, spriteRenderer, groups, number, connectionType, x, y,
            personClickManager, transportClickManager)
        self.images = ["office", "nodeStart", "nodeEnd"]


class House(Destination):
    def __init__(
            self, spriteRenderer, groups, number, connectionType, x, y,
            personClickManager, transportClickManager):
        super().__init__(
            spriteRenderer, groups, number, connectionType, x, y,
            personClickManager, transportClickManager)
        self.images = ["house"]
        self.subType = NodeType.HOUSE


class EditorHouse(EditorNode, House):
    def __init__(
            self, spriteRenderer, groups, number, connectionType, x, y,
            clickManager, personClickManager, transportClickManager):
        EditorNode.__init__(
            self, spriteRenderer, groups, number, connectionType, x, y,
            clickManager, personClickManager, transportClickManager)
        House.__init__(
            self, spriteRenderer, groups, number, connectionType, x, y,
            personClickManager, transportClickManager)
        self.images = ["house", "nodeStart", "nodeEnd"]


class School(Destination):
    def __init__(
            self, spriteRenderer, groups, number, connectionType, x, y,
            personClickManager, transportClickManager):
        super().__init__(
            spriteRenderer, groups, number, connectionType, x, y,
            personClickManager, transportClickManager)
        self.images = ["school"]
        self.subType = NodeType.SCHOOL


class EditorSchool(EditorNode, School):
    def __init__(
            self, spriteRenderer, groups, number, connectionType, x, y,
            clickManager, personClickManager, transportClickManager):
        EditorNode.__init__(
            self, spriteRenderer, groups, number, connectionType, x, y,
            clickManager, personClickManager, transportClickManager)
        School.__init__(
            self, spriteRenderer, groups, number, connectionType, x, y,
            personClickManager, transportClickManager)
        self.images = ["school", "nodeStart", "nodeEnd"]


class Shop(Destination):
    def __init__(
            self, spriteRenderer, groups, number, connectionType, x, y,
            personClickManager, transportClickManager):
        super().__init__(
            spriteRenderer, groups, number, connectionType, x, y,
            personClickManager, transportClickManager)
        self.images = ["shop"]
        self.subType = NodeType.SHOP


class EditorShop(EditorNode, Shop):
    def __init__(
            self, spriteRenderer, groups, number, connectionType, x, y,
            clickManager, personClickManager, transportClickManager):
        EditorNode.__init__(
            self, spriteRenderer, groups, number, connectionType, x, y,
            clickManager, personClickManager, transportClickManager)
        Shop.__init__(
            self, spriteRenderer, groups, number, connectionType, x, y,
            personClickManager, transportClickManager)
        self.images = ["shop", "nodeStart", "nodeEnd"]
