from sprite import Sprite
from entity import MouseClick
from utils import checkKeyExist


# TODO: SHOULD NOT BE A SPRITE!!!!!!!!!!
class TutorialManager(Sprite):
    def __init__(self, spriteRenderer, groups, ordering):
        super().__init__(spriteRenderer, groups, [])
        self.ordering = ordering
        self.sequence, self.previousSequence = 0, -1
        self.previousTarget = None

        self.setClicks(False)

    def setSequence(self, sequence):
        self.sequence = sequence

        # At the end of the sequence we always want to allow clicks
        if self.sequence >= len(self.ordering):
            self.setClicks(True)

    def getSequence(self):
        return self.sequence

    # We don't want to allow objects that aren't the subject to be moved
    def setClicks(self, clicks):
        for transport in self.spriteRenderer.getAllTransports():
            transport.setCanClick(clicks)
        for person in self.spriteRenderer.getAllPeople():
            person.setCanClick(clicks)

    def checkWaitForPrevious(self):
        if (self.previousSequence < 0
                or self.previousSequence >= len(self.ordering)):
            return False

        if (not checkKeyExist(
                self.ordering[self.previousSequence], ["wait"], True)):
            return False

        previousSeq = next(iter(self.ordering[self.previousSequence].items()))

        # If the previous sequence doesn't have a right click,
        # we don't have to wait for anything
        if previousSeq[1] is None:
            return False

        dest = self.spriteRenderer.getNode(previousSeq[1])
        previousDest = self.previousTarget.getCurrentNode()
        if previousDest.getNumber() == dest.getNumber():
            return False
        return True

    def addMouseClick(self, target, clickManager, dest):
        self.setClicks(False)
        target.setCanClick(True)
        MouseClick((
            self.spriteRenderer.allSprites, self.spriteRenderer.aboveEntities),
            target, self, [clickManager], next=dest)
        self.previousSequence = self.sequence
        self.previousTarget = target

    def update(self):
        if (self.sequence == self.previousSequence
                or self.sequence >= len(self.ordering)
                or self.checkWaitForPrevious()):
            return

        currentSeq = next(iter(self.ordering[self.sequence].items()))
        if currentSeq[0].split('_')[0] == "person":
            subType = checkKeyExist(
                self.ordering[self.sequence], ["subType"], None)
            dest = self.spriteRenderer.getNode(currentSeq[1], subType=subType)
            pid = int(currentSeq[0].split('_')[1])
            found = False
            for person in self.spriteRenderer.getAllPeople():
                if person.getId() != pid:
                    continue
                found = True

                # Check if they need to be travelling on a transport,
                # or at a specific node.
                onTransport = checkKeyExist(
                    self.ordering[self.sequence], ["transport"], False)
                at = checkKeyExist(self.ordering[self.sequence], ["at"], None)
                travellingOn = person.getTravellingOn()
                if onTransport:
                    if travellingOn is None or (
                            at and travellingOn.getCurrentNode().getNumber()
                            != at):
                        continue

                elif not onTransport:
                    if travellingOn is not None or (
                            at and person.getCurrentNode().getNumber() != at):
                        continue

                self.addMouseClick(
                    person, self.spriteRenderer.getPersonClickManager(), dest)
                return

            # If the person doesn't exist yet, we set everything clickable
            if not found:
                self.setClicks(True)

        elif currentSeq[0].split('_')[0] == "transport":
            # Do transport stuff here
            dest = self.spriteRenderer.getNode(currentSeq[1])
            tid = int(currentSeq[0].split('_')[1])
            for transport in self.spriteRenderer.getAllTransports():
                if transport.getId() != tid:
                    continue

                self.addMouseClick(
                    transport, self.spriteRenderer.getTransportClickManager(),
                    dest)
                return
