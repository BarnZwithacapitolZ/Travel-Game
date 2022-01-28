import pygame
from config import YELLOW
from utils import overrides, vec
from sprite import Sprite


class Particle(Sprite):
    def __init__(self, groups, currentPerson, color=YELLOW):
        super().__init__(currentPerson.spriteRenderer, groups, [])
        self.currentPerson = currentPerson
        self.color = color
        self.start, self.end = 100, 0
        self.rad = 0
        self.alpha = self.start

        self.currentPerson.addEntity(self)

    def __render(self):
        self.dirty = False

        self.pos = ((
            self.currentPerson.pos - vec(self.rad, self.rad))
            * self.game.renderer.getScale()
            * self.spriteRenderer.getFixedScale())

        self.size = (vec(
            self.currentPerson.width + (self.rad * 2),
            self.currentPerson.height + (self.rad * 2))
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
            if len(self.currentPerson.getEntities()) < 3:
                Particle(self.groups, self.currentPerson)
            else:
                self.currentPerson.setEntities([])

        # Since the particle is short-lived, this is ok.
        self.dirty = True
