import pygame
import person as PERSON
import node as NODE
from enum import Enum

class ClickManager:
    def __init__(self, game):
        self.game = game
        self.clicked = False

    #### Getters

    # Return if the mouse has been pressed
    def getClicked(self):
        return self.clicked


    #### Setters ####

    # Set the mouse pressed
    def setClicked(self, clicked):
        self.clicked = clicked



class GameClickManager(ClickManager):
    def __init__(self, game):
        super().__init__(game)
        self.node = None # A
        self.person = None # B

        self.personClicked = False


    #### Getters ####

    # Return if a person is current selected
    def getPersonClicked(self):
        return self.personClicked


    # Return the current selected person
    def getPerson(self):
        return self.person


    #### Setters ####

    # Set the person has been selected
    def setPersonClicked(self, personClicked):
        self.personClicked = personClicked


    # Set the current selected node
    def setNode(self, node):
        self.node = node
        self.movePerson()

    
    # Set the current selected person
    def setPerson(self, person):
        if self.person != person: # New person is different from current person
            # Remove selected image from current person
            if self.person is not None:
                self.person.setCurrentImage(0)

            # Set selected image of new person
            if person is not None:
                person.setCurrentImage(2)
                self.personClicked = True
            else:
                self.personClicked = False

        # Set the new person
        self.person = person
        self.movePerson()


    '''
        function: pathFinding
        input:  Node A
                Node B
        output: List path (empty if no path is found)
    '''
    def pathFinding(self):
        A = self.person.getCurrentNode() # Start (where we come from)
        B = self.node # End (Where we are going)
        finalNode = None
        path = []

        # Selected a node different from the players layer
        if self.person.getStartingConnectionType() != B.getConnectionType():
            # The start and end nodes are on different layers, diferent to the players layer 
            if A.getConnectionType() != B.getConnectionType():
                layer = self.game.spriteRenderer.getGridLayer(self.person.getStartingConnectionType())
                nodes = layer.getGrid().getNodes()

                # Set the start and end node to be the equivelant node on the players layer 
                for node in nodes:
                    if node.getNumber() == A.getNumber():
                        A = node

                    if node.getNumber() == B.getNumber():
                        if isinstance(B, NODE.MetroStation) or isinstance(B, NODE.TramStop): # If its a stop on a different layer, switch to that layer at the end of the path
                            finalNode = B
                        B = node

            # The start and end nodes are on the same layer (but different from the players layer)
            elif A.getConnectionType() == B.getConnectionType():
                layer = self.game.spriteRenderer.getGridLayer(self.person.getStartingConnectionType())
                nodes = layer.getGrid().getNodes()

                # Set the start and end node to be the equivelant node on the players layer 
                for node in nodes:
                    if node.getNumber() == A.getNumber():
                        A = node

                    if node.getNumber() == B.getNumber():
                        if isinstance(B, NODE.MetroStation) or isinstance(B, NODE.TramStop): # If its a stop on a different layer, switch to that layer at the end of the path
                            finalNode = B
                        B = node                        

        # Within the same layer 
        if self.person.getStartingConnectionType() == B.getConnectionType():

            # Player is on a node in a different layer 
            if A.getConnectionType() != B.getConnectionType():
                layer = self.game.spriteRenderer.getGridLayer(B.getConnectionType())
                nodes = layer.getGrid().getNodes()

                # Get the same node on the players layer and set that as the starting node instead
                for node in nodes:
                    if node.getNumber() == A.getNumber():
                        A = node

            path = self.aStarPathFinding(A, B)

            # Append the final node and switch to the different layer
            if finalNode is not None and len(path) > 0: path.append(finalNode)
        
        return path


    # for a given node, return the adjacent nodes
    def getAdjacentNodes(self, n):
        adjNodes = []

        for connection in n["node"].getConnections():
            node = {"node": connection.getTo(), "parent": n}
            adjNodes.append(node)
        return adjNodes


    '''
        function: aStartPathFinding
        input:  Node A
                Node B
        output: List path (empty if no path is found)
    '''
    def aStarPathFinding(self, A, B):
        openList = []
        closedList = []

        # startNode.g = startNode.h = startNode.f = 0
        # startNode.parent = None
        # endNode.h = endNode.h = endNode.f = 0
        # endNode.parent = None

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
                    if child["node"].getNumber() == closedNode["node"].getNumber():
                        c = True
                if c: continue

                # Get the distance between the child and the current node
                for connection in child["node"].getConnections():
                    if connection.getTo().getNumber() == currentNode["node"].getNumber():
                        dis = connection.getDistance()
                        break
                
                # Create f, g and g values
                child["g"] = currentNode["g"] + dis                     
                child["h"] = ((child["node"].pos - child["node"].offset) - (endNode["node"].pos - endNode["node"].offset)).length()
                child["f"] = child["g"] + child["h"]

                # Child is already in the open list
                o = False
                for openNode in openList:
                    if child["node"].getNumber() == openNode["node"].getNumber() and child["g"] > openNode["g"]:
                        o = True
                if o: continue

                # Add the child to the open list
                openList.append(child)

        print("Route is impossible")
        return [] # Return the empty path if route is impossible


    # Move the person by setting the persons path when the person and the node are both set
    def movePerson(self):
        # node is set but person isnt
        if self.node and self.person is None:
            self.node = None

        # Both the node and the person are set, we can create a path
        if self.node is not None and self.person is not None:
            # Only move the person if they're a curtain state

            if self.person.getStatus() == PERSON.Person.Status.UNASSIGNED or self.person.getStatus() == PERSON.Person.Status.WAITING or self.person.getStatus() == PERSON.Person.Status.BOARDING or self.person.getStatus() == PERSON.Person.Status.WALKING or self.person.getStatus() == PERSON.Person.Status.FLAG:
                # Create the path
                path = self.pathFinding()

                # Clear the players current path before assigning a new one
                self.person.clearPath(path)

                for node in path:
                    self.person.addToPath(node)

                self.person.setCurrentImage(0)
                self.personClicked = False

                #after the click is managed, clear the player and the node to allow for another click management
                self.person = None
                self.node = None



class EditorClickManager(ClickManager):
    class ClickType(Enum):
        CONNECTION = 1
        STOP = 2
        TRANSPORT = 3
        DESTINATION = 4

        # D at front signifies deletion options
        DCONNECTION = 5
        DSTOP = 6
        DTRANSPORT = 7
        DDESTINATION = 8


    def __init__(self, game):
        super().__init__(game)
        self.startNode = None # A
        self.endNode = None # B

        self.clickType = EditorClickManager.ClickType.CONNECTION
        self.addType = "metro"


    def getStartNode(self):
        return self.startNode

    def getEndNode(self):
        return self.endNode

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


    def setStartNode(self, node):
        self.startNode = node
        self.startNode.setCurrentImage(2)
        self.createConnection()

    def setEndNode(self, node):
        # If the end node is on a different layer to the start node, make it be the start node
        if node.getConnectionType() != self.startNode.getConnectionType():
            self.startNode = node
            node.setCurrentImage(2)
            return

        self.endNode = node
        self.endNode.setCurrentImage(3)
        self.createConnection()


    def createConnection(self):
        if self.startNode is not None and self.endNode is not None:
            if self.startNode.getNumber() != self.endNode.getNumber():            
                if self.startNode.getConnectionType() == self.endNode.getConnectionType():
                    # Create a new connection
                    self.game.mapEditor.createConnection(self.startNode.getConnectionType(), self.startNode, self.endNode)
                    

            self.startNode = None
            self.endNode = None


    def addTransport(self, node):
        # No connections to the node, we cant add any transport
        if len(node.getConnections()) > 0 and len(node.getTransports()) < 1:
            self.game.mapEditor.addTransport(node.getConnectionType(), node.getConnections()[0])


    def addStop(self, node):
        # No connections to the node, we dont want to add a stop if nothing can stop at it
        if len(node.getConnections()) > 0 and not isinstance(node, NODE.Stop):
            self.game.mapEditor.addStop(node.getConnectionType(), node)


    def deleteConnection(self, connection):
        fromNode = connection.getFrom()
        toNode = connection.getTo()

        self.game.mapEditor.deleteConnection(connection.getConnectionType(), connection)

        # Remove any stops and transports from nodes with no connections
        if len(fromNode.getConnections()) <= 0:
            self.deleteTransport(fromNode)
            self.deleteStop(fromNode)
        
        if len(toNode.getConnections()) <= 0:
            self.deleteTransport(toNode)
            self.deleteStop(toNode)


    def deleteTransport(self, node):
        # Check that there is a transportation to delete
        if len(node.getTransports()) >= 1:
            self.game.mapEditor.deleteTransport(node.getConnectionType(), node)


    def deleteStop(self, node):
        # Make sure it is actually a stop
        if isinstance(node, NODE.Stop):
            self.game.mapEditor.deleteStop(node.getConnectionType(), node)            

