import personHolder
import clickManager as CLICKMANAGER
import person as PERSON
from pygame.locals import BLEND_MIN
from config import HOVERGREY
from utils import overrides, vec, getMousePos
from enum import Enum
from sprite import Sprite


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


class Node(Sprite):
    def __init__(
            self, spriteRenderer, groups, number, connectionType, x, y,
            clickManagers=[]):
        super().__init__(spriteRenderer, groups, clickManagers)
        self.number = number
        self.connectionType = connectionType
        self.personClickManager = self.clickManagers[0]
        self.transportClickManager = self.clickManagers[1]

        self.width, self.height = 20, 20
        self.offset = vec(0, 0)
        self.pos = vec(x, y) + self.offset

        # If the node is below another nodes on layer 4
        self.below = []

        # If the node is above another nodes on layer 4
        self.above = []

        # All connections to / from this node
        self.connections = []

        # All transport currently at this node
        self.transports = []

        # All people currently at this node
        self.people = []
        self.personHolder = personHolder.PersonHolder(
            self.groups, self,
            self.spriteRenderer.getPersonHolderClickManager())

        # Node Type definition
        self.type = NodeType.REGULAR
        self.subType = NodeType.REGULAR

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

    def getPersonHolder(self):
        return self.personHolder

    def getType(self):
        return self.type

    def getSubType(self):
        return self.subType

    def getImages(self):
        return self.images

    def getAbove(self):
        return self.above

    def setType(self, nodeType):
        self.type = nodeType

    def setSubType(self, subType):
        self.subType = subType

    def setDimensions(self, width, height):
        self.offset = vec((self.width - width) / 2, (self.height - height) / 2)
        self.width = width
        self.height = height

        # Recalculate position with offset in mind.
        self.pos = self.pos + self.offset

    def setFirstImage(self, image):
        self.images[0] = image

    def setCurrentImage(self, image):
        self.currentImage = image
        self.dirty = True

    def addBelowNode(self, below):
        # We only care about non regular nodes that are below or below.
        if (self.type == NodeType.REGULAR
                or below.getType() == NodeType.REGULAR):
            return

        self.below.append(below)

    def addAboveNode(self, above):
        # We only care about non regular nodes that are above or below.
        if (self.type == NodeType.REGULAR
                or above.getType() == NodeType.REGULAR):
            return

        indicator = BelowIndicator(
            (self.spriteRenderer.allSprites, self.spriteRenderer.layer4),
            self, above)
        self.above.append(indicator)

    # Add a connection to the node
    def addConnection(self, connection):
        self.connections.append(connection)

    def setConnections(self, connections=[]):
        self.connections = connections

    def setTransports(self, transports=[]):
        self.transports = transports

    # Add a transport to the node
    def addTransport(self, transport):
        self.transports.append(transport)

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

    def __render(self):
        self.dirty = False

        self.image = self.game.imageLoader.getImage(
            self.images[self.currentImage],
            (self.width * self.spriteRenderer.getFixedScale(),
                self.height * self.spriteRenderer.getFixedScale()))

        self.rect = self.image.get_rect()

        self.rect.topleft = self.getTopLeft(self)

    @overrides(Sprite)
    def makeSurface(self):
        if self.dirty or self.image is None:
            self.__render()

    @overrides(Sprite)
    def events(self):
        if self.game.mainMenu.getOpen():
            return
        mx, my = getMousePos(self.game)

        # click event; setting the node for the transport
        if (self.rect.collidepoint((mx, my))
                and self.game.clickManager.getRightClicked()
                and self.transportClickManager.getTransport() is not None):

            self.transportClickManager.setNode(self)
            self.game.clickManager.setRightClicked(False)

        # Click event; setting the node for the person
        elif (self.rect.collidepoint((mx, my))
                and self.game.clickManager.getRightClicked()
                and self.personClickManager.getPerson() is not None):
            # If the player is moving on a transport,
            # dont allow them to select a node
            if (self.personClickManager.getPerson().getStatus()
                    != PERSON.Person.Status.MOVING
                    and self.personClickManager.getPerson().getStatus()
                    != PERSON.Person.Status.DEPARTING):

                self.personClickManager.setNode(self)
                self.game.clickManager.setRightClicked(False)

        # Hover over event; for transport
        elif (self.rect.collidepoint((mx, my))
                and not self.mouseOver
                and self.transportClickManager.getTransport() is not None
                and self.game.clickManager.isTop(self)):
            self.mouseOver = True
            self.game.clickManager.setMouseOver(self)
            self.image.fill(HOVERGREY, special_flags=BLEND_MIN)
            self.dirty = False

        # Hover over event; for person
        elif (self.rect.collidepoint((mx, my))
                and not self.mouseOver
                and self.personClickManager.getPerson() is not None
                and self.game.clickManager.isTop(self)):
            # If the player is moving on a transport,
            # dont show hovering over a node
            if (self.personClickManager.getPerson().getStatus()
                    == PERSON.Person.Status.MOVING
                    and self.personClickManager.getPerson().getStatus()
                    == PERSON.Person.Status.DEPARTING):
                return

            self.mouseOver = True
            self.game.clickManager.setMouseOver(self)
            self.image.fill(HOVERGREY, special_flags=BLEND_MIN)
            self.dirty = False

        # Hover out event
        elif not self.rect.collidepoint((mx, my)) and self.mouseOver:
            self.mouseOver = False
            self.game.clickManager.setMouseOver(None)
            self.currentImage = 0
            self.dirty = True

    @overrides(Sprite)
    def update(self):
        if not self.dirty and not self.spriteRenderer.getPaused():
            self.events()

    def __repr__(self):
        return (
            f"Node(type={self.type}, subType={self.subType}, "
            f"number={self.number}, connectionType={self.connectionType})")


class EditorNode(Node):
    def __init__(
            self, spriteRenderer, groups, number, connectionType, x, y,
            clickManagers=[]):
        super().__init__(
            spriteRenderer, groups, number, connectionType, x, y,
            clickManagers)
        self.clickManager = self.clickManagers[2]
        self.images = ["node", "nodeStart", "nodeEnd"]

    @overrides(Node)
    def events(self):
        if self.game.mainMenu.getOpen():
            return
        mx, my = getMousePos(self.game)

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


class BelowIndicator(Sprite):
    def __init__(self, groups, currentNode, target):
        super().__init__(currentNode.spriteRenderer, groups, [])
        self.currentNode = currentNode
        self.target = target

        self.width, self.height = 11.5, 11.5
        self.offset = vec(21, 19 + (
            len(self.currentNode.getAbove()) * self.width))
        self.pos = self.currentNode.pos + self.offset

    def __render(self):
        self.dirty = False

        self.image = self.game.imageLoader.getImage(
            self.target.getImages()[0], (
                self.width * self.spriteRenderer.getFixedScale(),
                self.height * self.spriteRenderer.getFixedScale()))
        self.rect = self.image.get_rect()

        self.rect.topleft = self.getTopLeft(self)

    @overrides(Sprite)
    def makeSurface(self):
        if self.dirty or self.image is None:
            self.__render()

    @overrides(Sprite)
    def events(self):
        if self.game.mainMenu.getOpen():
            return
        mx, my = getMousePos(self.game)

        # Click event; take the player to the layer below that is
        # being indicated.
        if (self.rect.collidepoint((mx, my))
                and self.game.clickManager.getClicked()
                and self.game.clickManager.getMouseOver() == self):
            self.game.clickManager.setClicked(False)
            self.spriteRenderer.showLayer(
                int(self.target.getConnectionType()[-1]))

        # Hover over event.
        elif (self.rect.collidepoint((mx, my)) and not self.mouseOver
                and self.game.clickManager.isTop(self)):
            self.mouseOver = True
            self.image.fill(HOVERGREY, special_flags=BLEND_MIN)
            self.game.clickManager.setMouseOver(self)
            self.dirty = False

        # Hover out event.
        elif not self.rect.collidepoint((mx, my)) and self.mouseOver:
            self.mouseOver = False
            self.game.clickManager.setMouseOver(None)
            self.dirty = True

    @overrides(Sprite)
    def update(self):
        if not self.dirty:
            self.events()
