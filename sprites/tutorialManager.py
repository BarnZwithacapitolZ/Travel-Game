from sprite import Sprite
from entity import MouseClick


# TODO: SHOULD NOT BE A SPRITE!!!!!!!!!!
class TutorialManager(Sprite):
    def __init__(self, spriteRenderer, groups, ordering):
        super().__init__(spriteRenderer, groups, [])
        self.ordering = ordering
        self.sequence, self.previousSequence = 0, -1
        self.previousTarget = None

    def setSequence(self, sequence):
        self.sequence = sequence

    def getSequence(self):
        return self.sequence

    def checkWaitForPrevious(self):
        if (self.previousSequence < 0
                or self.previousSequence >= len(self.ordering)):
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
        if currentSeq[0].split('_')[0] == 'person':
            dest = self.spriteRenderer.getNode(currentSeq[1])
            pid = int(currentSeq[0].split('_')[1])
            for person in self.spriteRenderer.getAllPeople():
                if person.getId() != pid:
                    continue

                self.addMouseClick(
                    person, self.spriteRenderer.getPersonClickManager(), dest)
                break

        elif currentSeq[0].split('_')[0] == 'transport':
            # Do transport stuff here
            dest = self.spriteRenderer.getNode(currentSeq[1])
            tid = int(currentSeq[0].split('_')[1])
            for transport in self.spriteRenderer.getAllTransports():
                if transport.getId() != tid:
                    continue

                self.addMouseClick(
                    transport, self.spriteRenderer.getTransportClickManager(),
                    dest)
                break
