from utils import overrides
from sprite import Sprite
from entity import MouseClick


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
                if person.getId() == pid:
                    MouseClick((
                        self.spriteRenderer.allSprites,
                        self.spriteRenderer.aboveEntities), person, self,
                        [self.spriteRenderer.getPersonClickManager()],
                        next=dest)
                    self.previousSequence = self.sequence
                    self.previousTarget = person
                    break

        elif currentSeq[0].split('_')[0] == 'transport':
            # Do transport stuff here
            dest = self.spriteRenderer.getNode(currentSeq[1])
            tid = int(currentSeq[0].split('_')[1])
            for transport in self.spriteRenderer.getAllTransports(self.spriteRenderer.gridLayer1, self.spriteRenderer.gridLayer2, self.spriteRenderer.gridLayer3):
                if transport.getId() == tid:
                    MouseClick((
                        self.spriteRenderer.allSprites,
                        self.spriteRenderer.aboveEntities), transport, self,
                        [self.spriteRenderer.getTransportClickManager()],
                        next=dest)
                    self.previousSequence = self.sequence
                    self.previousTarget = transport
                    break


# TODO: not sure if this should be a sprite??
class MeterController(Sprite):
    def __init__(self, spriteRenderer, groups, amount):
        super().__init__(spriteRenderer, groups, [])
        self.amount = amount
        self.totalAmount = amount
        self.amountToAdd = 0
        self.empty = False

        # How fast to decrease the meter when slowing down
        self.decreaseSpeed = 0.2

        # How fast to increase the meter when not full
        self.increaseSpeed = 0.02

        # How slow to make the game (half its speed currently)
        self.slowDownAmount = 0.5

        # How fast to make the game when fast forwarding
        self.speedUpAmount = self.slowDownAmount

    def addToAmountToAdd(self, amountToAdd):
        # only add the extra if the meter isn't already full
        if self.amount < self.totalAmount:
            self.amountToAdd += amountToAdd

    # update by an iterative value (i.e -0.2)
    def updateAmount(self, amount, removeFromAdd=False):
        self.amount += amount * 100 * self.game.dt
        self.spriteRenderer.getHud().updateSlowDownMeter(self.amount)

        if removeFromAdd:
            self.amountToAdd -= self.decreaseSpeed * 100 * self.game.dt

    @overrides(Sprite)
    def events(self):
        # if spacebar is pressed and the flag isn't called
        if self.game.clickManager.getSpaceBar() and not self.empty:
            if self.amount > 0:
                self.spriteRenderer.setDt(
                    self.spriteRenderer.getStartDt() - self.slowDownAmount)
                self.updateAmount(-self.decreaseSpeed)

            # We have reached the end of the meter
            else:
                self.game.audioLoader.restoreMusic()
                self.empty = True
                self.spriteRenderer.setDt(self.spriteRenderer.getStartDt())

        # If the spacebar isn't pressed and the flag is called
        elif not self.game.clickManager.getSpaceBar() and self.empty:
            self.empty = False

        # If there is amount left in the add
        elif self.amountToAdd > 0:
            if self.amount < self.totalAmount:
                self.updateAmount(self.decreaseSpeed, True)

            # When the meter is full we don't want to add the bonus anymore
            else:
                self.amountToAdd = 0

        # Speed up the game
        elif self.game.clickManager.getSpeedUp():
            self.spriteRenderer.setDt(
                self.spriteRenderer.getStartDt() + self.speedUpAmount)

        else:
            self.spriteRenderer.setDt(self.spriteRenderer.getStartDt())

    @overrides(Sprite)
    def update(self):
        self.events()

        # Gradually increase the meter if not filled
        if self.amount < self.totalAmount:
            self.updateAmount(self.increaseSpeed)
