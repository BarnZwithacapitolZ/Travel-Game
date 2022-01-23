import random
import json
from node import Node, EditorNode, NodeType
from connection import Connection
from transport import Metro, Bus, Tram, Taxi
from config import (
    DEFAULTBOARDWIDTH, DEFAULTBOARDHEIGHT, LAYERNODEMAPPINGS,
    LAYERTRANSPORTMAPPINGS)


class GridManager:
    def __init__(self, layer, groups, level=None, spacing=(1.5, 1.5)):
        self.layer = layer
        self.spriteRenderer = self.layer.getSpriteRenderer()
        self.game = self.layer.game
        self.groups = groups
        self.level = level
        self.levelName = ""

        self.nodes = []
        self.connections = []
        self.tempConnections = []
        self.transports = []
        self.destinations = []

        self.width = DEFAULTBOARDWIDTH
        self.height = DEFAULTBOARDHEIGHT

        # Set the new width, height from the map data
        if self.level is not None:
            self.loadMap()

        scale = min(
            DEFAULTBOARDWIDTH / self.width, DEFAULTBOARDHEIGHT / self.height)

        # apply the starting fixed scale when first rendering
        scale += self.spriteRenderer.getStartingFixedScale()
        self.spriteRenderer.setFixedScale(scale)

        self.nodePositions = self.setNodePositions(
            spacing[0], spacing[1], self.width, self.height)

        # Mappings between name and the element being added to the map
        self.transportMappings = {
            "metro": Metro,
            "bus": Bus,
            "tram": Tram,
            "taxi": Taxi
        }

        # Define which nodes we can add to each of the 3 layers
        self.layerNodeMappings = LAYERNODEMAPPINGS

        # Define which transports we can add to each of the 3 layers
        self.layerTransportMappings = LAYERTRANSPORTMAPPINGS

    def getNodePositions(self):
        return self.nodePositions

    def getNodeMappingsByLayer(self):
        if self.layer.getNumber() not in self.layerNodeMappings:
            return []
        return self.layerNodeMappings[self.layer.getNumber()]

    def getTransportMappingsByLayer(self):
        if self.layer.getNumber() not in self.layerTransportMappings:
            return []
        return self.layerTransportMappings[self.layer.getNumber()]

    def getLevelName(self):
        return self.levelName

    # return the nodes, in a list to be appended to each layer
    def getNodes(self):
        return self.nodes

    # Return the connections, in a list for each layer
    def getConnections(self):
        return self.connections

    def getTempConnections(self):
        return self.tempConnections

    # Return the transportations, in a list for each layer
    def getTransports(self):
        return self.transports

    def getDestinations(self):
        return self.destinations

    def getMap(self):
        if hasattr(self, 'map'):
            return self.map
        return {}

    # Generate an 18 * 10 board of possible node positions
    # (x and y locations) for nodes to be added to
    def setNodePositions(
            self, offx=1.5, offy=1.5, width=DEFAULTBOARDWIDTH,
            height=DEFAULTBOARDHEIGHT):
        # Offset on the x coordinate
        # Offset on the y coordinate
        spacing = 50  # Spacing between each node
        positions = []

        scale = (
            min(self.width / DEFAULTBOARDHEIGHT,
                self.height / DEFAULTBOARDHEIGHT)
            if min(
                self.width / DEFAULTBOARDWIDTH,
                self.height / DEFAULTBOARDHEIGHT) > 1 else 1)

        for i in range(width):
            for x in range(height):
                positions.append((
                    (i + offx * scale) * spacing,
                    (x + offy * scale) * spacing))

        return positions

    def addConnections(self, connectionType, A, B, temp=False):
        # Only need to draw one of the connections
        c1 = Connection(self.spriteRenderer, connectionType, A, B, temp, True)
        c2 = Connection(self.spriteRenderer, connectionType, B, A, temp)

        if temp:
            self.tempConnections.append(c1)
            self.tempConnections.append(c2)

        else:
            self.connections.append(c1)  # Forwards
            self.connections.append(c2)  # Backwards

        return c1, c2

    def removeConnections(self, connections=[]):
        for connection in connections:
            self.connections.remove(connection)

    def removeTempConnections(self):
        self.tempConnections = []

    # Check for an opposing connection in the opposite direction as the
    # current connection
    def getOppositeConnection(self, currentConnection):
        for connection in self.connections:
            if (connection.getFrom() == currentConnection.getTo()
                    and connection.getTo() == currentConnection.getFrom()):
                return currentConnection, connection

        # There is no opposite connection
        return False

    # From the search node, return the key from the mappings dicts
    def reverseMappingsSearch(self, dic, searchValue):
        for key, value in dic.items():
            if isinstance(searchValue, value):
                return key
        return False

    # Load the .json map data into a dictionary
    def loadMap(self):
        if isinstance(self.level, dict):
            self.map = self.level

        else:
            with open(self.level) as f:
                self.map = json.load(f)

        self.levelName = self.map["mapName"]  # Get the name of the map
        self.width = self.map["width"]
        self.height = self.map["height"]

    # Add a node to the grid if the node is not already on the grid
    def addNode(self, connection, connectionType, currentNodes, direction):
        if connection[direction] not in currentNodes:
            n = self.addRegularNode(
                connectionType, connection[direction], [
                    self.spriteRenderer.getPersonClickManager(),
                    self.spriteRenderer.getTransportClickManager()])

            # Check and add all special nodes
            self.setNodeTypeFromMap(
                n, NodeType.SPECIAL.value, connectionType,
                connection[direction])

            # Check and add all stop nodes
            self.setNodeTypeFromMap(
                n, NodeType.STOP.value, connectionType, connection[direction])

            # Check and add all destination nodes
            self.setNodeTypeFromMap(
                n, NodeType.DESTINATION.value, connectionType,
                connection[direction])

            currentNodes.append(connection[direction])

        return currentNodes

    def addRegularNode(
            self, connectionType, number, clickManagers=[], x=None, y=None):
        # If the x, y coordinates aren't provided then we'll use the positions
        # loaded in from the map.
        if x is None:
            x = self.nodePositions[number][0]

        if y is None:
            y = self.nodePositions[number][1]

        # If there are more than 2 click managers we know its an editor node.
        if len(clickManagers) <= 2:
            n = Node(
                self.spriteRenderer, self.groups, number, connectionType,
                x, y, clickManagers[0], clickManagers[1])

        else:
            n = EditorNode(
                self.spriteRenderer, self.groups, number, connectionType,
                x, y, clickManagers[0], clickManagers[1], clickManagers[2])

        # Append to the list of total nodes
        self.nodes.append(n)
        return n

    def setNodeTypeFromMap(self, n, nodeType, connectionType, number):
        if (nodeType not in self.map
                or connectionType not in self.map[nodeType]):
            return

        for node in self.map[nodeType][connectionType]:
            if node['location'] != number:
                continue

            self.setNodeType(n, nodeType, node['type'])

    def setNodeType(self, n, nodeType, nodeSubType):
        if nodeType == "stops":
            n.setDimensions(25, 25)
            n.setType(NodeType.STOP)

            if nodeSubType == "bus":
                n.setSubType(NodeType.BUSSTOP)
                n.setFirstImage("busStation")

            elif nodeSubType == 'metro':
                n.setSubType(NodeType.METROSTATION)
                n.setFirstImage("trainStation")

            elif nodeSubType == 'tram':
                n.setSubType(NodeType.TRAMSTOP)
                n.setFirstImage("tramStation")

        elif nodeType == "destinations":
            self.destinations.append(n)
            n.setDimensions(30, 30)
            n.setType(NodeType.DESTINATION)

            if nodeSubType == 'airport':
                n.setSubType(NodeType.AIRPORT)
                n.setFirstImage("airport")

            elif nodeSubType == 'office':
                n.setSubType(NodeType.OFFICE)
                n.setFirstImage("office")

            elif nodeSubType == 'house':
                n.setSubType(NodeType.HOUSE)
                n.setFirstImage("house")

            elif nodeSubType == 'school':
                n.setSubType(NodeType.SCHOOL)
                n.setFirstImage("school")

            elif nodeSubType == 'shop':
                n.setSubType(NodeType.SHOP)
                n.setFirstImage("shop")

        elif nodeType == "specials":
            n.setType(NodeType.SPECIAL)

            if nodeSubType == 'noWalkNode':
                n.setSubType(NodeType.NOWALKNODE)
                n.setFirstImage('nodeNoWalking')

    def replaceNode(
            self, node, connectionType, nodeType=None, nodeSubType=None):
        number = node.getNumber()
        # need to transfer the connections from the old node to the new node
        connections = node.getConnections()
        transports = node.getTransports()
        self.nodes.remove(node)
        node.remove()

        n = self.addRegularNode(
            connectionType, number, [
                self.spriteRenderer.getClickManager(),
                self.spriteRenderer.getPersonClickManager(),
                self.spriteRenderer.getTransportClickManager()
            ], self.nodePositions[number][0], self.nodePositions[number][1])

        if nodeType is not None and nodeSubType is not None:
            self.setNodeType(n, nodeType, nodeSubType)

        # Need to replace the connection with the new node,
        # otherwise it cant be deleted
        for connection in self.connections:
            if connection.getFrom().getNumber() == n.getNumber():
                connection.setFromNode(n)

            elif connection.getTo().getNumber() == n.getNumber():
                connection.setToNode(n)

        n.setConnections(connections)
        n.setTransports(transports)
        return n

    # Create the grid by adding all the nodes and connections to the grid
    def createGrid(self, connectionType):
        currentNodes = []

        if connectionType in self.map["connections"]:
            for connection in self.map["connections"][connectionType]:
                # Add the nodes in the connection
                currentNodes = self.addNode(
                    connection, connectionType, currentNodes, 0)
                currentNodes = self.addNode(
                    connection, connectionType, currentNodes, 1)

                for node in self.nodes:
                    if node.getNumber() == connection[0]:
                        n1 = node

                    if node.getNumber() == connection[1]:
                        n2 = node

                # Create the connection with the nodes
                self.addConnections(connectionType, n1, n2)

    # Create a full grid with all the nodes populated and no connections
    # (for the map editor)
    def createFullGrid(self, connectionType):
        clickManagers = [
            self.spriteRenderer.getClickManager(),
            self.spriteRenderer.getPersonClickManager(),
            self.spriteRenderer.getTransportClickManager()]

        if self.level is None:
            for number, position in enumerate(self.nodePositions):
                n = EditorNode(
                    self.spriteRenderer, self.groups, number, connectionType,
                    position[0], position[1], clickManagers[0],
                    clickManagers[1], clickManagers[2])
                self.nodes.append(n)

        else:
            # Loop through all the node positions
            for number, position in enumerate(self.nodePositions):
                n = self.addRegularNode(
                    connectionType, number, clickManagers, position[0],
                    position[1])

                # Check and add all special editor nodes
                self.setNodeTypeFromMap(
                    n, NodeType.SPECIAL.value, connectionType, number)

                # Check and add all stop editor nodes
                self.setNodeTypeFromMap(
                    n, NodeType.STOP.value, connectionType, number)

                # Check and add all destination editor nodes
                self.setNodeTypeFromMap(
                    n, NodeType.DESTINATION.value, connectionType, number)

            if connectionType in self.map["connections"]:
                for connection in self.map["connections"][connectionType]:
                    for node in self.nodes:
                        if node.getNumber() == connection[0]:
                            n1 = node
                        if node.getNumber() == connection[1]:
                            n2 = node

                    self.addConnections(connectionType, n1, n2)

    # Load the transportation to the grid on a specified connection
    def loadTransport(self, connectionType, running=True):
        if (len(self.connections) <= 0
                or connectionType not in self.map["transport"]):
            return

        # For each transportation in the map
        for transport in self.map["transport"][connectionType]:
            possibleConnections = []

            # for each connection, find the connection of the transportation
            for connection in self.connections:
                # Ensure it is on the right connection going in the
                # right direction
                if connection.getFrom().getNumber() == transport["location"]:
                    possibleConnections.append(connection)

            # pick a random connection to change the direction
            if len(possibleConnections) > 0:
                connection = possibleConnections[
                    random.randint(0, len(possibleConnections) - 1)]

                t = self.transportMappings[transport["type"]](
                    self.spriteRenderer, self.groups, connection, running,
                    self.spriteRenderer.getTransportClickManager(),
                    self.spriteRenderer.getPersonClickManager())
                self.transports.append(t)

    # Add a transport to the map within the map editor
    def addTransport(
            self, connectionType, connection, transport, running=True):
        t = transport(
            self.spriteRenderer, self.groups, connection, running,
            self.spriteRenderer.getTransportClickManager(),
            self.spriteRenderer.getPersonClickManager())
        self.transports.append(t)

    # Remove a transport from the map within the map editor
    def removeTransport(self, transport):
        self.transports.remove(transport)
        transport.remove()

    @staticmethod
    def getMapValues(width, height, reverse=False):
        mapValues = {}
        nodes = 0
        for x in range(0, width):
            for y in range(0, height):
                if reverse:
                    mapValues[(x, y)] = nodes
                else:
                    mapValues[nodes] = (x, y)
                nodes += 1
        return mapValues
