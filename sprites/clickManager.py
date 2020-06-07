from person import *


class ClickManager:
    def __init__(self, game):
        
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


    def movePerson(self):
        if self.node and self.person is None:
            self.node = None

        if self.node is not None and self.person is not None:
            if self.person.getStatus() == Person.Status.UNASSIGNED or self.person.getStatus() == Person.Status.WAITING or self.person.getStatus() == Person.Status.BOARDING:
                dxy = (self.node.pos - self.node.offset) - self.person.pos + self.person.offset

                if abs(int(dxy.x)) <= 50 and abs(int(dxy.y)) <= 50:
                    #path finding herererere
                    self.person.addToPath(self.node)
                    self.person.setStatus(Person.Status.WALKING)

                self.person.setCurrentImage(0)
                self.personClicked = False

                #after the click is managed, clear the player and the node to allow for another click management
                self.person = None
                self.node = None