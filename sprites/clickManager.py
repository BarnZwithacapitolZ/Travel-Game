from person import *


class ClickManager:
    def __init__(self, game):
        
        self.node = None
        self.person = None
        self.clicked = False

    def setClicked(self, clicked):
        self.clicked = clicked


    def getClicked(self):
        return self.clicked


    def setNode(self, node):
        self.node = node
        self.movePerson()
    
    def setPerson(self, person):
        self.person = person
        self.movePerson()

    def movePerson(self):
        if self.node and self.person is None:
            self.node = None


        if self.node is not None and self.person is not None:
            dx, dy = (((self.node.x - self.node.offx) - self.person.pos.x) + self.person.offx, ((self.node.y - self.node.offy ) - self.person.pos.y) + self.person.offy)

            if abs(int(dx)) <= 50 and abs(int(dy)) <= 50:
                #path finding herererere
                self.person.addToPath(self.node)
                self.person.setStatus(Person.Status.WALKING)

                #after the click is managed, clear the player and the node to allow for another click management
                self.person = None
                self.node = None