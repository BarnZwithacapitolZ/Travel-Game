import pygame
import math
import abc
from config import YELLOW, WHITE, BLACK
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

    def getOption(self, key, attribute, default):
        options = self.decorators[key]
        return options[attribute] if attribute in options else default

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
        if ('timer' not in self.decorators
                or self.spriteRenderer.getLives() is None):
            return

        # Get the options or defaults
        length = self.getOption('timer', 'length', 20)
        thickness = self.getOption('timer', 'thickness', 5)

        if self.target.timer <= 0 or self.target.timer > length:
            return

        scale = getScale(self.game, self.spriteRenderer)
        offset = self.spriteRenderer.offset

        offx = 0.01
        step = self.target.timer / (length / 2) + 0.02
        for _ in range(6):
            pygame.draw.arc(
                surface, YELLOW, (
                    (self.target.pos.x - 4 + offset.x) * scale,
                    (self.target.pos.y - 4 + offset.y) * scale,
                    (self.width + 8) * scale, (self.height + 8) * scale),
                math.pi / 2 + offx, math.pi / 2 + math.pi * step,
                int(thickness * scale))

            offx += 0.01

    # Visualize the path by drawing the connection between each node
    def drawPath(self, surface):
        if 'path' not in self.decorators:
            return

        path = self.getOption('path', 'path', [])

        if len(path) <= 0:
            return

        start = path[0]
        scale = getScale(self.game, self.spriteRenderer)
        offset = self.spriteRenderer.offset
        thickness = 3

        for previous, current in zip(path, path[1:]):
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

    def drawDestination(self, surface):
        if 'destination' not in self.decorators:
            return

        destination = self.getOption('destination', 'destination', None)

        if destination is None:
            return

        scale = getScale(self.game, self.spriteRenderer)
        offset = self.spriteRenderer.offset
        thickness = 4

        pos = ((
            destination.pos - vec(self.target.rad, self.target.rad) + offset)
            * scale)
        size = vec(
            destination.width + (self.target.rad * 2),
            destination.height + (self.target.rad * 2)) * scale
        rect = pygame.Rect(pos, size)

        pygame.draw.lines(
            surface, YELLOW, False, [
                rect.topleft + (vec(0, 10) * scale), rect.topleft,
                rect.topleft + (vec(10, 0) * scale)], int(thickness * scale))
        pygame.draw.lines(
            surface, YELLOW, False, [
                rect.topright + (vec(-10, 0) * scale), rect.topright,
                rect.topright + (vec(0, 10) * scale)], int(thickness * scale))
        pygame.draw.lines(
            surface, YELLOW, False, [
                rect.bottomleft + (vec(0, -10) * scale), rect.bottomleft,
                rect.bottomleft + (vec(10, 0) * scale)],
            int(thickness * scale))
        pygame.draw.lines(
            surface, YELLOW, False, [
                rect.bottomright + (vec(-10, 0) * scale), rect.bottomright,
                rect.bottomright + (vec(0, -10) * scale)],
            int(thickness * scale))

    def drawTimerOutline(self, surface):
        if ('timerOutline' not in self.decorators
                or self.spriteRenderer.getLives() is None):
            return

        scale = getScale(self.game, self.spriteRenderer)
        offset = self.spriteRenderer.offset

        start = (self.target.pos - self.target.offset) + vec(7, -12)
        middle = (self.target.pos + vec(30, -40))
        end = middle + vec(30, 0)

        pygame.draw.lines(
            surface, YELLOW, False, [
                (start + offset) * scale, (middle + offset) * scale,
                (end + offset) * scale], int(4 * scale))

    def drawTimerTime(self, surface=None):
        if ('timerTime' not in self.decorators
                or self.spriteRenderer.getLives() is None):
            return

        textColor = (
            WHITE if self.spriteRenderer.getDarkMode() else BLACK)

        fontImage = self.timerFont.render(
            str(round(self.target.timer, 1)), True, textColor)

        rect = ((
            self.target.pos + vec(32, -35) + self.spriteRenderer.offset)
            * getScale(self.game, self.spriteRenderer))

        if surface is None:
            self.game.renderer.addSurface(fontImage, (rect))
        else:
            surface.blit(fontImage, (rect))

    def __render(self):
        self.dirty = False
        # do I need the fixed scale to change here?
        self.timerFont = pygame.font.Font(
            pygame.font.get_default_font(),
            int(15 * getScale(self.game, self.spriteRenderer)))

    def makeSurface(self):
        if self.dirty:  # Don't check image since we don't have one
            self.__render()

    @overrides(Sprite)
    @abc.abstractmethod
    def drawPaused(self, surface):
        return

    @overrides(Sprite)
    def draw(self):
        self.makeSurface()
        # TODO: probably want to do this in a conditional
        # so its not always added?
        self.game.renderer.addSurface(None, None, self.drawTimer)

        if (self.target.mouseOver
                or self.clickManager.getTarget() == self.target):
            self.drawTimerTime()
            self.drawDestination(self.game.renderer.gameDisplay)
            self.game.renderer.addSurface(None, None, self.drawTimerOutline)

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
