from person import *
from node import *
import copy

class ClickManager:
    def __init__(self, game):
        self.game = game
        self.node = None
        self.person = None
        self.clicked = False
        self.personClicked = False


    #### Getters ####

    # Return if a person is current selected
    def getPersonClicked(self):
        return self.personClicked


    # Return if the mouse has been pressed
    def getClicked(self):
        return self.clicked


    # Return the current selected person
    def getPerson(self):
        return self.person


    #### Setters ####

    # Set the mouse pressed
    def setClicked(self, clicked):
        self.clicked = clicked


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
                        if isinstance(B, MetroStation): # If its a stop on a different layer, switch to that layer at the end of the path
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
                        if isinstance(B, MetroStation): # If its a stop on a different layer, switch to that layer at the end of the path
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

        for connection in n.getConnections():
            node = copy.copy(connection.getTo())
            node.parent = n
            adjNodes.append(node)
        return adjNodes


    '''
        function: aStartPathFinding
        input:  Node startNode
                Node endNode
        output: List path (empty if no path is found)
    '''
    def aStarPathFinding(self, startNode, endNode):
        openList = []
        closedList = []

        startNode.g = startNode.h = startNode.f = 0
        startNode.parent = None
        endNode.h = endNode.h = endNode.f = 0
        endNode.parent = None

        openList.append(startNode)

        # While the openlist is not empty
        while len(openList) > 0:

            # Set the current node
            currentNode = openList[0]
            currentIndex = 0

            for index, item in enumerate(openList):
                if item.f < currentNode.f:
                    currentNode = item
                    currentIndex = index            

            openList.pop(currentIndex)
            closedList.append(currentNode)

            # Check if the current node is the goal
            if currentNode.getNumber() == endNode.getNumber():
                path = []
                current = currentNode

                while current is not None:
                    path.append(current)
                    current = current.parent

                return path[::-1]

            children = self.getAdjacentNodes(currentNode)

            for child in children:
                c = False
                # Child is in the closed list
                for closedNode in closedList:
                    if child.getNumber() == closedNode.getNumber():
                        c = True
                if c: continue

                # Get the distance between the child and the current node
                for connection in child.getConnections():
                    if connection.getTo().getNumber() == currentNode.getNumber():
                        dis = connection.getDistance()
                        break
                
                # Create f, g and g values
                child.g = currentNode.g + dis                     
                child.h = ((child.pos - child.offset) - (endNode.pos - endNode.offset)).length()
                child.f = child.g + child.h

                # Child is already in the open list
                o = False
                for openNode in openList:
                    if child.getNumber() == openNode.getNumber() and child.g > openNode.g:
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

            if self.person.getStatus() == Person.Status.UNASSIGNED or self.person.getStatus() == Person.Status.WAITING or self.person.getStatus() == Person.Status.BOARDING or self.person.getStatus() == Person.Status.WALKING:
                # Clear the players current path before assigning a new one
                self.person.clearPath()
                
                # Create the path
                for node in self.pathFinding():
                    self.person.addToPath(node)

                self.person.setCurrentImage(0)
                self.personClicked = False

                #after the click is managed, clear the player and the node to allow for another click management
                self.person = None
                self.node = None
