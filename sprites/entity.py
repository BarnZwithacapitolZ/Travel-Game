import pygame
import math
import abc
from config import YELLOW
from utils import overrides, vec
from sprite import Sprite


class Particle(Sprite):
    def __init__(self, groups, target, color=YELLOW):
        super().__init__(target.spriteRenderer, groups, [])
        self.target = target
        self.color = color
        self.start, self.end = 100, 0
        self.rad = 0
        self.alpha = self.start

        self.target.addEntity(self)

    def __render(self):
        self.dirty = False

        self.pos = ((
            self.target.pos - vec(self.rad, self.rad))
            * self.game.renderer.getScale()
            * self.spriteRenderer.getFixedScale())

        self.size = (vec(
            self.target.width + (self.rad * 2),
            self.target.height + (self.rad * 2))
            * self.game.renderer.getScale()
            * self.spriteRenderer.getFixedScale())

        self.image = pygame.Surface((self.size)).convert()
        self.image.set_colorkey((0, 0, 0))  # Remove black border

        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos

        pygame.draw.ellipse(self.image, self.color, pygame.Rect(
            0, 0, *self.size))

        self.image.set_alpha(self.alpha, pygame.RLEACCEL)

    @overrides(Sprite)
    def makeSurface(self):
        if self.dirty or self.image is None:
            self.__render()

    @overrides(Sprite)
    def update(self):
        self.rad += 60 * self.game.dt * self.spriteRenderer.getDt()
        self.alpha -= 120 * self.game.dt * self.spriteRenderer.getDt()

        if self.alpha < self.end:
            self.kill()
            if len(self.target.getEntities()) < 3:
                Particle(self.groups, self.target)
            else:
                self.target.setEntities([])

        # Since the particle is short-lived, this is ok.
        self.dirty = True


class Outline(Sprite):
    def __init__(self, groups, target, clickManagers=[]):
        super().__init__(target.spriteRenderer, groups, clickManagers)
        self.target = target
        self.clickManager = self.clickManagers[0]

        self.width, self.height = self.target.width, self.target.height

    def drawOutline(self, surface):
        scale = (
            self.game.renderer.getScale()
            * self.spriteRenderer.getFixedScale())

        # Set the position of the outline to the position of the target.
        self.pos = self.target.pos

        offx = 0.01
        for x in range(6):
            pygame.draw.arc(
                surface, YELLOW, (
                    (self.pos.x) * scale, (self.pos.y) * scale,
                    (self.width) * scale, (self.height) * scale),
                math.pi / 2 + offx, math.pi / 2, int(3.5 * scale))

            offx += 0.02

    @overrides(Sprite)
    @abc.abstractmethod
    def drawPaused(self, surface):
        return

    @overrides(Sprite)
    def draw(self):
        if self.clickManager.getPerson() == self.target:
            self.game.renderer.addSurface(None, None, self.drawOutline)
