import person as PERSON
import node as NODE
from enum import Enum, auto


class ClickManager:
    def __init__(self, game):
        self.game = game
        self.clicked = False
        self.rightClicked = False
        self.spaceBar = False
        self.speedUp = False

    def getClicked(self):
        return self.clicked

    def getRightClicked(self):
        return self.rightClicked

    def getSpaceBar(self):
        return self.spaceBar

    def getSpeedUp(self):
        return self.speedUp

    def setClicked(self, clicked):
        self.clicked = clicked

    def setRightClicked(self, rightClicked):
        self.rightClicked = rightClicked

    def setSpaceBar(self, spaceBar):
        self.spaceBar = spaceBar

    def setSpeedUp(self, speedUp):
        self.speedUp = speedUp

    # for a given node, return the adjacent nodes
    def getAdjacentNodes(self, n):
        adjNodes = []

        for connection in n["node"].getConnections():
            node = {"node": connection.getTo(), "parent": n}
            adjNodes.append(node)
        return adjNodes

    # Function: aStartPathFinding
    # Input:  Node A
    #         Node B
    # Output: List path (empty if no path is found)
    def aStarPathFinding(self, A, B):
        openList = []
        closedList = []

        startNode = {"node": A, "g": 0, "h": 0, "f": 0, "parent": None}
        endNode = {"node": B, "g": 0, "h": 0, "f": 0, "parent": None}

        openList.append(startNode)

        # While the openlist is not empty
        while len(openList) > 0:

            # Set the current node
            currentNode = openList[0]
            currentIndex = 0

            for index, item in enumerate(openList):
                if item["f"] < currentNode["f"]:
                    currentNode = item
                    currentIndex = index

            openList.pop(currentIndex)
            closedList.append(currentNode)

            # Check if the current node is the goal
            if currentNode["node"].getNumber() == endNode["node"].getNumber():
                path = []
                current = currentNode

                while current is not None:
                    path.append(current["node"])
                    current = current["parent"]

                return path[::-1]

            children = self.getAdjacentNodes(currentNode)

            for child in children:
                c = False
                # Child is in the closed list
                for closedNode in closedList:
                    if (child["node"].getNumber() ==
                            closedNode["node"].getNumber()):
                        c = True

                if c:
                    continue

                # Get the distance between the child and the current node
                for connection in child["node"].getConnections():
                    if (connection.getTo().getNumber() ==
                            currentNode["node"].getNumber()):
                        dis = connection.getDistance()
                        break

                # Create f, g and g values
                child["g"] = currentNode["g"] + dis
                child["h"] = (
                    (child["node"].pos - child["node"].offset)
                    - (endNode["node"].pos - endNode["node"].offset)).length()
                child["f"] = child["g"] + child["h"]

                # Child is already in the open list
                o = False
                for openNode in openList:
                    if (child["node"].getNumber() ==
                            openNode["node"].getNumber()
                            and child["g"] > openNode["g"]):
                        o = True

                if o:
                    continue

                # Add the child to the open list
                openList.append(child)

        return []  # Return the empty path if route is impossible


class PersonHolderClickManager(ClickManager):
    def __init__(self, game):
        super().__init__(game)
        self.personHolder = None

    def setPersonHolder(self, personHolder):
        self.personHolder = personHolder

    def getPersonHolder(self):
        return self.personHolder


class PersonClickManager(ClickManager):
    def __init__(self, game):
        super().__init__(game)
        self.node = None  # A
        self.person = None  # B
        self.personClicked = False

    # Return if a person is current selected
    def getPersonClicked(self):
        return self.personClicked

    # Return the current selected person
    def getPerson(self):
        return self.person

    # Return the current selected node
    def getNode(self):
        return self.node

    # Set the person has been selected
    def setPersonClicked(self, personClicked):
        self.personClicked = personClicked

    # Set the current selected node
    def setNode(self, node):
        self.node = node
        self.movePerson()

    # Set the current selected person
    def setPerson(self, person):
        # New person is different from current person
        if self.person != person:
            # Set selected image of new person
            if person is not None:
                self.personClicked = True

            else:
                self.personClicked = False

        # Set the new person
        self.person = person
        self.movePerson()

    # Override
    def getAdjacentNodes(self, n):
        adjNodes = []

        for connection in n["node"].getConnections():
            # We don't want to include no walk nodes
            if not isinstance(connection.getTo(), NODE.NoWalkNode):
                node = {"node": connection.getTo(), "parent": n}
                adjNodes.append(node)
        return adjNodes

    # Function: pathFinding
    # Input:  Node A
    #         Node B
    # Output: List path (empty if no path is found)
    def pathFinding(self, A=None, B=None):
        # Start (where we come from)
        A = self.person.getCurrentNode() if A is None else A

        # End (Where we are going)
        B = self.node if B is None else B

        finalNode = None
        path = []

        # Selected a node different from the players layer
        if self.person.getStartingConnectionType() != B.getConnectionType():
            startingConnectionAFound, startingConnectionBFound = False, False

            # The start and end nodes are on different layers,
            # diferent to the players layer
            if (A.getConnectionType() != B.getConnectionType()
                    or A.getConnectionType() == B.getConnectionType()):
                layer = self.game.spriteRenderer.getGridLayer(
                    self.person.getStartingConnectionType())
                nodes = layer.getGrid().getNodes()

                # Set the start and end node to be the equivelant
                # node on the players layer
                for node in nodes:
                    if node.getNumber() == A.getNumber():
                        A = node
                        startingConnectionAFound = True

                    if node.getNumber() == B.getNumber():
                        # If its a stop on a different layer,
                        # switch to that layer at the end of the path
                        if (isinstance(B, NODE.MetroStation)
                                or isinstance(B, NODE.TramStop)):
                            finalNode = B
                        B = node
                        startingConnectionBFound = True

            # A path can only be formed if there is startingConnectionType
            # nodes at the start and end of the player path
            # (even if they are on a different layer), otherwise empty path
            if not startingConnectionAFound or not startingConnectionBFound:
                return path

        # Within the same layer
        if self.person.getStartingConnectionType() == B.getConnectionType():

            # Player is on a node in a different layer
            if A.getConnectionType() != B.getConnectionType():
                layer = self.game.spriteRenderer.getGridLayer(
                    B.getConnectionType())
                nodes = layer.getGrid().getNodes()

                # Get the same node on the players layer and set that as the
                # starting node instead
                for node in nodes:
                    if node.getNumber() == A.getNumber():
                        A = node

            path = self.aStarPathFinding(A, B)

            # Append the final node and switch to the different layer
            if finalNode is not None and len(path) > 0:
                path.append(finalNode)

        return path

    # Move the person by setting the persons path when the person and
    # the node are both set
    def movePerson(self):
        # node is set but person isnt
        if self.node and self.person is None:
            self.node = None

        # Both the node and the person are set, we can create a path
        if self.node is not None and self.person is not None:
            # Only move the person if they're a curtain state

            if (self.person.getStatus() == PERSON.Person.Status.UNASSIGNED
                    or self.person.getStatus() == PERSON.Person.Status.WAITING
                    or self.person.getStatus() == PERSON.Person.Status.BOARDING
                    or self.person.getStatus() == PERSON.Person.Status.WALKING
                    or self.person.getStatus() == PERSON.Person.Status.FLAG):
                # Create the path
                path = self.pathFinding()

                if len(path) > 0:
                    self.game.audioLoader.playSound("uiFinishSelect", 2)

                else:
                    self.game.audioLoader.playSound("uiError", 0)

                # Clear the players current path before assigning a new one
                self.person.clearPath(path)

                for node in path:
                    self.person.addToPath(node)

                self.personClicked = False

                # after the click is managed, clear the player and the node to
                # allow for another click management
                self.node = None


class TransportClickManager(ClickManager):
    def __init__(self, game):
        super().__init__(game)
        self.node = None
        self.transport = None

    def getTransport(self):
        return self.transport

    def getNode(self):
        return self.node

    def setNode(self, node):
        self.node = node
        self.moveTransport()

    def setTransport(self, transport):
        self.transport = transport
        self.moveTransport()

    def pathFinding(self):
        A = self.transport.getCurrentNode()
        B = self.node
        path = []

        if A == B and not self.transport.getMoving():
            return path

        path = self.aStarPathFinding(A, B)
        return path

    def moveTransport(self):
        # node is set but transport isnt
        if self.node and self.transport is None:
            self.node = None

        if self.node is not None and self.transport is not None:
            # only set the path if the bus is moving
            path = self.pathFinding()

            if len(path) > 0:
                self.game.audioLoader.playSound("uiFinishSelect", 2)

            else:
                self.game.audioLoader.playSound("uiError", 0)

            self.transport.setFirstPathNode(path)
            self.transport.clearPath(path)

            for node in path:
                self.transport.addToPath(node)

            # self.transport = None
            self.node = None


class EditorClickManager(ClickManager):
    class ClickType(Enum):
        CONNECTION = auto()
        STOP = auto()
        TRANSPORT = auto()
        DESTINATION = auto()
        SPECIAL = auto()

        # D at front signifies deletion options
        DCONNECTION = auto()
        DTRANSPORT = auto()
        DNODE = auto()

    def __init__(self, game):
        super().__init__(game)
        self.startNode = None  # A
        self.endNode = None  # B
        self.previewStartNode = None
        self.previewEndNode = None
        self.tempEndNode = None  # used for visualizing path

        self.clickType = EditorClickManager.ClickType.CONNECTION
        self.addType = "metro"

    def clearNodes(self):
        self.startNode = None
        self.endNode = None
        self.tempEndNode = None

    def getStartNode(self):
        return self.startNode

    def getEndNode(self):
        return self.endNode

    def getTempEndNode(self):
        return self.tempEndNode

    def getPreviewStartNode(self):
        return self.previewStartNode

    def getClickType(self):
        return self.clickType

    def getAddType(self):
        return self.addType

    def setAddType(self, addType):
        self.addType = addType

    def setClickType(self, clickType):
        self.clickType = clickType

        if self.clickType != EditorClickManager.ClickType.CONNECTION:
            if self.startNode is not None:
                self.startNode = None

    def setPreviewStartNode(self, previewStartNode):
        if previewStartNode == self.startNode:
            return

        self.previewStartNode = previewStartNode
        if self.previewStartNode is not None:
            self.previewStartNode.setCurrentImage(1)

    def setPreviewEndNode(self, previewEndNode):
        if previewEndNode == self.endNode:
            return

        self.previewEndNode = previewEndNode
        if self.previewEndNode is not None:
            self.previewEndNode.setCurrentImage(2)

    def setStartNode(self, node):
        self.startNode = node
        if self.startNode is not None:
            self.game.audioLoader.playSound("uiStartSelect", 2)
            self.startNode.setCurrentImage(1)
            self.createConnection()

    def setEndNode(self, node):
        # If the end node is on a different layer to the start node,
        # make it be the start node
        if node.getConnectionType() != self.startNode.getConnectionType():
            self.game.audioLoader.playSound("uiStartSelect", 2)
            self.startNode = node
            node.setCurrentImage(1)
            return

        self.game.audioLoader.playSound("uiFinishSelect", 2)
        self.endNode = node
        self.endNode.setCurrentImage(2)
        self.createConnection()

    def setTempEndNode(self, node):
        # if its not on the same layer we can't visualize it
        if node.getConnectionType() != self.startNode.getConnectionType():
            return

        self.tempEndNode = node
        self.createTempConnection()

    def removeTempEndNode(self):
        self.game.mapEditor.removeAllTempConnections(
            self.tempEndNode.getConnectionType())
        self.tempEndNode = None

    def createTempConnection(self):
        # check both start and end nodes are set
        if self.startNode is not None and self.tempEndNode is not None:
            # check the start node is not the same as the end node
            if self.startNode.getNumber() != self.tempEndNode.getNumber():
                # check both nodes are on the same layer
                if (self.startNode.getConnectionType()
                        == self.tempEndNode.getConnectionType()):
                    # create a new temporary connection
                    self.game.mapEditor.createTempConnection(
                        self.startNode.getConnectionType(), self.startNode,
                        self.tempEndNode)

    def createConnection(self):
        # check both start and end nodes are set
        if self.startNode is not None and self.endNode is not None:
            # check the start node is not the same as the end node
            if self.startNode.getNumber() != self.endNode.getNumber():
                # check both nodes are on the same layer
                if (self.startNode.getConnectionType()
                        == self.endNode.getConnectionType()):
                    # Create a new connection
                    self.game.mapEditor.createConnection(
                        self.startNode.getConnectionType(), self.startNode,
                        self.endNode)

            self.startNode = None
            self.endNode = None
            self.previewStartNode = None
            self.previewEndNode = None

    def addTransport(self, node):
        # No connections to the node, we cant add any transport
        if len(node.getConnections()) > 0 and len(node.getTransports()) < 1:
            self.game.audioLoader.playSound("uiSuccess", 1)
            self.game.mapEditor.addTransport(
                node.getConnectionType(), node.getConnections()[0])

        else:
            self.game.audioLoader.playSound("uiError", 1)

    def addNode(self, node, nodeType):
        # TODO: add subtype values to nodes so we can compare subtype
        if len(node.getConnections()) <= 0: # or node.getType().value == nodeType:
            self.game.audioLoader.playSound("uiError", 1)
            return

        self.game.audioLoader.playSound("uiSuccess", 1)

        # Its not a regular node, we want to swap the nodes instead of adding
        if not NODE.Node.checkRegularNode(node):
            self.game.mapEditor.swapNode(
                node.getType().value, nodeType, node.getConnectionType(), node)

        else:
            self.game.mapEditor.addNode(
                nodeType, node.getConnectionType(), node)

    # Delete any node from the map (stops, locations, specials etc.)
    def deleteNode(self, node):
        if node.getType() == NODE.NodeType.REGULAR:
            self.game.audioLoader.playSound("uiError", 1)
            return

        self.game.audioLoader.playSound("uiCancel", 1)
        self.game.mapEditor.deleteNode(
            node.getType().value, node.getConnectionType(), node)

    def deleteConnection(self, connection):
        fromNode = connection.getFrom()
        toNode = connection.getTo()

        self.game.audioLoader.playSound("uiCancel", 1)
        self.game.mapEditor.deleteConnection(
            connection.getConnectionType(), connection)

        # Remove any stops and transports from nodes with no connections
        if len(fromNode.getConnections()) <= 0:
            self.deleteTransport(fromNode)
            self.deleteNode(fromNode, NODE.Stop, "stops")
            self.deleteNode(fromNode, NODE.Destination, "destinations")
            self.deleteNode(fromNode, NODE.NoWalkNode, "specials")

        if len(toNode.getConnections()) <= 0:
            self.deleteTransport(toNode)
            self.deleteNode(toNode, NODE.Stop, "stops")
            self.deleteNode(toNode, NODE.Destination, "destinations")
            self.deleteNode(toNode, NODE.NoWalkNode, "specials")

    def deleteTransport(self, node):
        # Check that there is a transportation to delete
        if len(node.getTransports()) < 1:
            return
        self.game.audioLoader.playSound("uiCancel", 1)
        self.game.mapEditor.deleteTransport(node.getConnectionType(), node)


class ControlClickManager(ClickManager):
    def __init__(self, game):
        super().__init__(game)
        self.controlKey = None

    def getControlKey(self):
        return self.controlKey

    def setControlKey(self, controlKey):
        self.controlKey = controlKey
