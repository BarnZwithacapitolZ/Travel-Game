from pygame.locals import *
import pygame.gfxdraw
from config import *
import os
import math

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

    
    def addToAmountToAdd(self, amountToAdd):
        # only add the extra if the meter isn't already full
        if self.amount < self.totalAmount:
            self.amountToAdd += amountToAdd

    
    # update by an iterative value (i.e -0.2)
    def updateAmount(self, amount, removeFromAdd = False):
        self.amount += amount * 100 * self.game.dt
        self.spriteRenderer.getHud().updateSlowDownMeter(self.amount)

        if removeFromAdd:
            self.amountToAdd -= 0.2 * 100 * self.game.dt


    def events(self):
        # if spacebar is pressed and the flag isn't called
        if self.game.clickManager.getSpaceBar() and not self.empty:
            if self.amount > 0:
                self.spriteRenderer.setDt(self.spriteRenderer.getStartDt() - 0.5)
                self.updateAmount(-0.2)
            else:
                # self.clickManager.setSpaceBarFlag(True)
                self.empty = True
                self.spriteRenderer.setDt(self.spriteRenderer.getStartDt())
                if self.amount < self.totalAmount:
                    self.updateAmount(0.02)

        # if the spacebar isn't pressed and the flag is called
        elif not self.game.clickManager.getSpaceBar() and self.empty:
            self.empty = False

         # if there is amount left in the add
        elif self.amountToAdd > 0:
            if self.amount < self.totalAmount:
                self.updateAmount(0.2, True)

            # when the meter is full we don't want to add the bonus anymore 
            else:
                self.amountToAdd = 0

        else:
            self.spriteRenderer.setDt(self.spriteRenderer.getStartDt())
            if self.amount < self.totalAmount:
                self.updateAmount(0.02)

    def update(self):
        self.events()
    