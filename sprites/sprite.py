import pygame
import abc
from utils import overrides, getScale


class Sprite(pygame.sprite.Sprite):
    def __init__(self, spriteRenderer, groups, clickManagers=[]):
        self.groups = groups
        self.priority = self.getPriority()
        super().__init__(self.groups)

        self.spriteRenderer = spriteRenderer
        self.game = self.spriteRenderer.game
        self.clickManagers = clickManagers

        self.mouseOver = False
        self.dirty = True

        # Any entities to be added to the sprite
        self.entities = {}

    def getMouseOver(self):
        return self.mouseOver

    def setMouseOver(self, mouseOver):
        self.mouseOver = mouseOver

    # Calculate the topleft corner of a sprite based on the
    # spriteRenderers scale and offset.
    def getTopLeft(self, target):
        return (
            (target.pos + self.spriteRenderer.offset)
            * getScale(self.game, self.spriteRenderer))

    # Defines the priority of the rendering order, a sprite with a > priority
    # than another sprite will be drawn above that other sprite.
    def getPriority(self):
        if len(self.groups) > 0 and type(self.groups) is tuple:
            return len(self.groups[0].sprites())

        return 0

    def getEntities(self, key):
        if key not in self.entities:
            return []
        return self.entities[key]

    def addEntity(self, key, entity):
        self.entities.setdefault(key, []).append(entity)

    def deleteEntities(self, key):
        if key not in self.entities:
            return
        del self.entities[key]

    # Remove the sprite from all groups that contain it,
    # the sprite is no longer drawn.
    @overrides(pygame.sprite.Sprite)
    def kill(self):
        super().kill()
        del self

    # Make the sprites image for blitting, call the private render method.
    @abc.abstractmethod
    def makeSurface(self):
        return

    # Make the sprites image and blit it to the paused surface (provided).
    def drawPaused(self, surface):
        self.makeSurface()
        surface.blit(self.image, (self.rect))

    # Make the sprites image and add it to the surface array for blitting
    # to the main game display.
    def draw(self):
        self.makeSurface()
        self.game.renderer.addSurface(self.image, (self.rect))

    # Click and mouse events.
    @abc.abstractmethod
    def events(self):
        return

    # Update the sprite, contains physics calculations.
    @abc.abstractmethod
    def update(self):
        return
