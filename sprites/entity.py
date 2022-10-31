import pygame
import math
import abc
from config import YELLOW
from utils import overrides, vec, getScale
from sprite import Sprite


class Particle(Sprite):
    def __init__(self, groups, target, color=YELLOW, infinite=False):
        super().__init__(target.spriteRenderer, groups, [])
        self.target = target
        self.color = color
        self.start, self.end = 100, 0
        self.rad = 0
        self.alpha = self.start

        # Run endlessly
        self.infinite = infinite

        self.target.addEntity('particles', self)

    def getInfinite(self):
        return self.infinite

    def setInfinite(self, infinite):
        self.infinite = infinite

    def __render(self):
        self.dirty = False

        self.pos = self.target.pos - vec(self.rad, self.rad)

        self.size = (vec(
            self.target.width + (self.rad * 2),
            self.target.height + (self.rad * 2))
            * getScale(self.game, self.spriteRenderer))

        self.image = pygame.Surface((self.size)).convert()
        self.image.set_colorkey((0, 0, 0))  # Remove black border

        self.rect = self.image.get_rect()
        self.rect.topleft = self.getTopLeft(self)

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
            if len(self.target.getEntities('particles')) < 3 or self.infinite:
                Particle(self.groups, self.target, infinite=self.infinite)
            else:
                self.target.deleteEntities('particles')

        # Since the particle is short-lived, this is ok.
        self.dirty = True


class MouseClick(Sprite):
    def __init__(self, groups, target, direction="left"):
        super().__init__(target.spriteRenderer, groups, [])
        self.target = target
        self.direction = direction

    def __render(self):
        pass

    @overrides(Sprite)
    def makeSurface(self):
        if self.dirty or self.image is None:
            self.__render()

    @overrides(Sprite)
    def update(self):
        # We want to animate the entity here
        pass


class Decorators(Sprite):
    def __init__(self, groups, target, clickManagers=[]):
        super().__init__(target.spriteRenderer, groups, clickManagers)
        self.target = target
        self.clickManager = self.clickManagers[0]
        self.width, self.height = self.target.width, self.target.height
        self.decorators = {}

        self.target.addEntity('decorators', self)

    def addDecorator(self, decorator, options=[]):
        if decorator not in self.decorators:
            self.decorators[decorator] = options

    def removeDecorator(self, decorator):
        if decorator in self.decorators:
            del self.decorators[decorator]

    def drawOutline(self, surface):
        if 'outline' not in self.decorators:
            return

        scale = getScale(self.game, self.spriteRenderer)
        offset = self.spriteRenderer.offset

        offx = 0.01
        for _ in range(6):
            pygame.draw.arc(
                surface, YELLOW, (
                    (self.target.pos.x - 2 + offset.x) * scale,
                    (self.target.pos.y - 2 + offset.y) * scale,
                    (self.width + 4) * scale, (self.height + 4) * scale),
                math.pi / 2 + offx, math.pi / 2, int(3.5 * scale))

            offx += 0.02

    def drawTimer(self, surface):
        pass

    # Visualize the path by drawing the connection between each node
    def drawPath(self, surface):
        if len(self.target.path) <= 0 or 'path' not in self.decorators:
            return

        start = self.target.path[0]
        scale = getScale(self.game, self.spriteRenderer)
        offset = self.spriteRenderer.offset
        thickness = 3

        for previous, current in zip(self.target.path, self.target.path[1:]):
            posx = (
                ((previous.pos - previous.offset) + vec(10, 10) + offset)
                * scale)
            posy = (
                ((current.pos - current.offset) + vec(10, 10) + offset)
                * scale)

            pygame.draw.line(surface, YELLOW, posx, posy, int(
                thickness * scale))

        # Connection from target to the first node in the path
        startx = (
            ((self.target.pos - self.target.offset) + vec(10, 10) + offset)
            * scale)
        starty = ((start.pos - start.offset) + vec(10, 10) + offset) * scale
        pygame.draw.line(
            surface, YELLOW, startx, starty, int(thickness * scale))

    @overrides(Sprite)
    @abc.abstractmethod
    def drawPaused(self, surface):
        return

    @overrides(Sprite)
    def draw(self):
        if self.clickManager.getTarget() == self.target:
            self.drawPath(self.game.renderer.gameDisplay)
            self.game.renderer.addSurface(None, None, self.drawOutline)


class StatusIndicator(Sprite):
    def __init__(self, groups, target):
        super().__init__(target.spriteRenderer, groups, [])
        self.target = target
        self.width, self.height = 10, 10
        self.offset = vec(-2.5, -10)
        self.pos = self.target.pos + self.offset

        self.target.addEntity('statusIndicators', self)

        if self.spriteRenderer.getDarkMode():
            self.images = [
                None, "walkingWhite", "waitingWhite", "boardingWhite",
                "boardingWhite", None, "departingWhite", "flagWhite"]

        else:
            self.images = [
                None, "walking", "waiting", "boarding", "boarding", None,
                "departing", "flag"]
        self.currentState = self.target.getStatusValue() - 1

    def __render(self):
        self.dirty = False

        if self.images[self.currentState] is not None:
            self.image = self.game.imageLoader.getImage(
                self.images[self.currentState], (
                    self.width * self.spriteRenderer.getFixedScale(),
                    self.height * self.spriteRenderer.getFixedScale()))
            self.rect = self.image.get_rect()

        # If the image is none, we want to create a Rect so we can still move
        # the status indicator, but set the image to the None attribute
        else:
            self.image = self.images[self.currentState]
            self.rect = pygame.Rect(
                0, 0,
                self.width * self.spriteRenderer.getFixedScale(),
                self.height * self.spriteRenderer.getFixedScale())

        self.rect.topleft = self.getTopLeft(self)

    # TODO: just add and remove the sprite from groups instead of setting the
    # image to None.
    @overrides(Sprite)
    def makeSurface(self):
        if self.dirty:
            self.__render()
        if self.image is None:
            return False
        return True

    @overrides(Sprite)
    def drawPaused(self, surface):
        if self.makeSurface():
            surface.blit(self.image, (self.rect))

    @overrides(Sprite)
    def draw(self):
        if self.makeSurface():
            self.game.renderer.addSurface(self.image, (self.rect))

    @overrides(Sprite)
    def update(self):
        if (self.target.getStatusValue() - 1) != self.currentState:
            self.dirty = True
            self.currentState = self.target.getStatusValue() - 1
