from person import *
import copy

class ClickManager:
    def __init__(self, game):
        self.game = game
        self.node = None
        self.person = None
        self.clicked = False
        self.personClicked = False

    def setClicked(self, clicked):
        self.clicked = clicked


    def setPersonClicked(self, personClicked):
        self.personClicked = personClicked


    def getPersonClicked(self):
        return self.personClicked


    def getClicked(self):
        return self.clicked


    def setNode(self, node):
        self.node = node
        self.movePerson()

    
    def setPerson(self, person):
        if self.person != person:
            if self.person is not None:
                self.person.setCurrentImage(0)

            if person is not None:
                person.setCurrentImage(2)
                self.personClicked = True
            else:
                self.personClicked = False

        self.person = person
        self.movePerson()


    def getPerson(self):
        return self.person


    def pathFinding(self):
        A = self.person.getCurrentNode() # Start (where we come from)
        B = self.node # End (Where we are going)
        finalNode = None

        # Not of the same connection
        if self.person.getStartingConnectionType() != B.getConnectionType():
            layer = self.game.spriteRenderer.getGridLayer(A.getConnectionType())
            nodes = layer.getGrid().getNodes()

            for node in nodes:
                if node.getNumber() == B.getNumber():
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
            if finalNode is not None: path.append(finalNode)
            return path
        return None

    # for a given node, return the adjacent nodes
    def getAdjacentNodes(self, n):
        topleft = n.getNumber() - 11
        top = n.getNumber() - 1
        topright = n.getNumber() + 9
        left = n.getNumber() - 10
        right = n.getNumber() + 10
        bottomleft = n.getNumber() - 9
        bottom = n.getNumber() + 1
        bottomright = n.getNumber() + 11

        adjacent = [topleft, top, topright, left, right, bottomleft, bottom, bottomright]
        adjNodes = []

        for connection in n.getConnections():
            node = connection.getTo()
            for adj in adjacent:
                if node.getNumber() == adj:
                    newnode = copy.copy(node)
                    newnode.parent = n
                    adjNodes.append(newnode)
        return adjNodes


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
                # Child is in the closed list
                for closedNode in closedList:
                    if child.getNumber() == closedNode.getNumber():
                        continue

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
                for openNode in openList:
                    if child.getNumber() == openNode.getNumber() and child.g > openNode.g:
                        continue

                # Add the child to the open list
                openList.append(child)


    def movePerson(self):
        if self.node and self.person is None:
            self.node = None

        if self.node is not None and self.person is not None:
            if self.person.getStatus() == Person.Status.UNASSIGNED or self.person.getStatus() == Person.Status.WAITING or self.person.getStatus() == Person.Status.BOARDING:
                dxy = (self.node.pos - self.node.offset) - self.person.pos + self.person.offset


                path = self.pathFinding()

                if path is not None:
                    for node in path:
                        self.person.addToPath(node)


                # if abs(int(dxy.x)) <= 50 and abs(int(dxy.y)) <= 50:
                #     #path finding herererere
                #     self.person.addToPath(self.node)
                #     self.person.setStatus(Person.Status.WALKING)

                self.person.setCurrentImage(0)
                self.personClicked = False

                #after the click is managed, clear the player and the node to allow for another click management
                self.person = None
                self.node = None


class AStarNode:
    def __init__(self, parent = None, pos = None):
        self.parent = parent
        self.pos = pos

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.pos == other.pos
    