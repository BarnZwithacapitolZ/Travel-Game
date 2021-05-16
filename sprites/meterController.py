import pygame

vec = pygame.math.Vector2


class MeterController(pygame.sprite.Sprite):
    def __init__(self, spriteRenderer, groups, amount):
        self.groups = groups
        super().__init__(self.groups)

        self.spriteRenderer = spriteRenderer
        self.game = self.spriteRenderer.game

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

    def getEmpty(self):
        return self.empty

    def getSlowDownAmount(self):
        return self.slowDownAmount

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

    def events(self):
        # if spacebar is pressed and the flag isn't called
        if self.game.clickManager.getSpaceBar() and not self.empty:
            if self.amount > 0:
                self.spriteRenderer.setDt(
                    self.spriteRenderer.getStartDt() - self.slowDownAmount)
                self.updateAmount(-self.decreaseSpeed)

            # We have reached the end of the meter
            else:
                self.game.audioLoader.playSound("slowOut", 1)
                self.empty = True
                self.spriteRenderer.setDt(self.spriteRenderer.getStartDt())
                if self.amount < self.totalAmount:
                    self.updateAmount(self.increaseSpeed)

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

        else:
            self.spriteRenderer.setDt(self.spriteRenderer.getStartDt())
            if self.amount < self.totalAmount:
                self.updateAmount(self.increaseSpeed)

    def update(self):
        self.events()
