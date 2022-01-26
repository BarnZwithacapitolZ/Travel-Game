import pygame


class Sprite(pygame.sprite.Sprite):
    def __init__(self, spriteRenderer, groups, clickManagers=[]):
        self.groups = groups
        self.priority = self.getPriority()
        super().__init__(self.groups)

        self.spriteRenderer = spriteRenderer
        self.game = self.spriteRenderer.game

        self.mouseOver = False
        self.dirty = False

    def getMouseOver(self):
        return self.mouseOver

    def setMouseOver(self, mouseOver):
        return self.mouseOver

    def getPriority(self):
        if len(self.groups) > 0:
            return len(self.groups[0].sprites())

        return 0
