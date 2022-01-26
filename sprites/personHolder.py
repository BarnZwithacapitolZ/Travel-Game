import pygame
import math
import node as NODE
from config import BLACK, GREY, WHITE
from transport import Transport

vec = pygame.math.Vector2


class PersonHolder(pygame.sprite.Sprite):
    def __init__(self, game, groups, target, clickManager):
        self.groups = groups
        self.priority = 0
        super().__init__([])
        self.game = game
        self.target = target
        self.spriteRenderer = self.target.spriteRenderer
        self.clickManager = clickManager

        self.width, self.height = 20, 20
        self.drawerWidth, self.drawerHeight = 0, 0

        # Need these to be attributes so they can be used when
        # moving the player on the transports
        self.drawerSpacing = 2.5
        self.drawerCols = 2

        self.people = []
        self.open = False

        # Used to stop people events for people in the holder
        # (so player can click on the holder instead)
        self.canClick = False

        self.offset = vec(-10, -15)
        self.pos = self.target.pos + self.offset

        self.drawerOffset = self.offset
        self.drawerPos = self.pos

        self.dirty = True
        self.mouseOver = False

        self.color = WHITE

    def getPeople(self):
        return self.people

    def getOpen(self):
        return self.open

    def getCanClick(self):
        return self.canClick

    def getMouseOver(self):
        return self.mouseOver

    def setOpen(self, open):
        self.open = open

    def setCanClick(self, canClick):
        self.canClick = canClick

    def setMouseOver(self, mouseOver):
        self.mouseOver = mouseOver

    def addPerson(self, person):
        if person in self.people:
            return

        self.people.append(person)

        # We give the holder same priority as the highest priority person
        if person.priority > self.priority:
            self.priority = person.priority

        if len(self.people) > 1:
            # Show the holder
            self.add(self.groups)

            # If the holder is already open we don't want to remove people
            # then add them back
            if self.open:
                self.openHolder()

            else:
                self.closeHolder()

    def removePerson(self, person, switchLayer=False):
        if person not in self.people:
            return

        self.people.remove(person)

        # Position the player back against the target
        person.pos = (self.target.pos - self.target.offset) + person.offset
        person.rect.topleft = (
            person.pos * self.game.renderer.getScale()
            * self.spriteRenderer.getFixedScale())
        person.moveStatusIndicator()

        person.addToLayer()
        person.addToLayer("layer 4")
        person.setCanClick(True)

        # We don't want to call this when switching layer
        if len(self.people) > 1 and self.open and not switchLayer:
            self.closeHolder(True)

        elif len(self.people) == 1:
            if self.open:
                self.game.audioLoader.playSound("collapse")

            self.remove(self.groups)
            self.canClick = False
            self.open = False
            self.clickManager.setPersonHolder(None)

            # Will only ever be one person left so we can just
            # directly modify them
            person = self.people[0]
            person.addToLayer()
            person.addToLayer("layer 4")
            person.setCanClick(True)

            if isinstance(self.target, Transport):
                person.pos.x = (
                    self.target.pos.x + self.target.width + person.offset.x)
                person.pos.y = self.target.pos.y + person.offset.y

            else:
                person.pos = (
                    (self.target.pos - self.target.offset) + person.offset)

            person.rect.topleft = (
                person.pos * self.game.renderer.getScale()
                * self.spriteRenderer.getFixedScale())
            person.moveStatusIndicator()

    def movePeople(self, addToLayers=False):
        offset = vec(self.drawerSpacing, self.drawerSpacing)

        for i, person in enumerate(self.people):
            if addToLayers:
                person.addToLayer()
                person.addToLayer("layer 4")
                person.setCanClick(True)

            person.pos = self.drawerPos + offset

            # If a player spawns in the holder they won't have an image
            # (since they're not added to any groups that draw them) so
            # we need to make their image
            person.makeSurface()

            person.rect.topleft = (
                person.pos * self.game.renderer.getScale()
                * self.spriteRenderer.getFixedScale())
            person.moveStatusIndicator()
            offset.x += person.width + self.drawerSpacing

            if (i + 1) % self.drawerCols == 0:
                offset.x = self.drawerSpacing
                offset.y += person.height + self.drawerSpacing

    def openHolder(self):
        if len(self.people) <= 1:
            return

        # We want to close any existing open person holders
        if self.clickManager.getPersonHolder() is not None:
            self.clickManager.getPersonHolder().closeHolder()

        # Width and height of a person should always be the same,
        # so we can just use the first person in the holder
        personWidth = self.people[0].width
        personHeight = self.people[0].height

        self.drawerWidth = (
            self.drawerSpacing + (
                (personWidth + self.drawerSpacing)
                * (len(self.people) if len(self.people)
                    <= self.drawerCols else self.drawerCols)))

        self.drawerHeight = (
            self.drawerSpacing + (
                (personHeight + self.drawerSpacing)
                * math.ceil(len(self.people) / self.drawerCols)))

        self.drawerOffset = (
            vec((-self.drawerWidth) + 15, (-self.drawerHeight) + 10))

        # If it a transport we want the holder to appear on the
        # RIGHT side not the left
        if isinstance(self.target, Transport):
            self.drawerPos.x = (
                self.target.pos.x + self.target.width + self.offset.x)
            self.drawerPos.y = self.target.pos.y + self.drawerOffset.y

        else:
            self.drawerPos = self.target.pos + self.drawerOffset

        self.movePeople(True)

        self.clickManager.setPersonHolder(self)
        self.open = True
        self.canClick = False
        self.color = GREY
        self.dirty = True

    def closeHolder(self, audio=False):
        if len(self.people) <= 1:
            return

        for person in self.people:
            person.removeFromLayer()
            person.removeFromLayer("layer 4")
            person.setCanClick(False)

            # Reset the players positions, and make sure any new people
            # spawning have an image
            person.pos = (self.target.pos - self.target.offset) + person.offset
            person.makeSurface()
            person.rect.topleft = (
                person.pos * self.game.renderer.getScale()
                * self.spriteRenderer.getFixedScale())
            person.moveStatusIndicator()

        # Reset the position of the holder when transport is
        # stationary at a stop
        if isinstance(self.target, Transport):
            self.pos.x = self.target.pos.x + self.target.width + self.offset.x
            self.pos.y = self.target.pos.y + self.offset.y

        if audio:
            self.game.audioLoader.playSound("collapse")

        self.clickManager.setPersonHolder(None)
        self.open = False
        self.canClick = True
        self.color = WHITE
        self.dirty = True

        # Reset the person holder clicks to stop pressing a holder on
        # a different layer
        self.spriteRenderer.resetPersonHolderClicks()

    def __render(self):
        self.dirty = False

        if not self.open:
            self.image = pygame.Surface((
                    self.width * self.game.renderer.getScale()
                    * self.spriteRenderer.getFixedScale(), self.height
                    * self.game.renderer.getScale()
                    * self.spriteRenderer.getFixedScale()
                ), pygame.SRCALPHA).convert_alpha()

            self.rect = self.image.get_rect()

            self.rect.topleft = (
                self.pos * self.game.renderer.getScale()
                * self.spriteRenderer.getFixedScale())

            # Do I need the fixed scale to change here?
            self.counterFont = pygame.font.Font(
                pygame.font.get_default_font(), int(
                    12 * self.game.renderer.getScale()
                    * self.spriteRenderer.getFixedScale()))

            pygame.draw.ellipse(self.image, self.color, (
                0, 0, self.rect.width, self.rect.height))

            self.fontImage = self.counterFont.render(
                "+" + str(len(self.people)), True, BLACK)

            size = pygame.font.Font(
                pygame.font.get_default_font(), 12).size(
                    "+" + str(len(self.people)))

            rect = (vec(
                self.width / 2 - (size[0] / 2),
                self.height / 2 - (size[1] / 2))
                * self.game.renderer.getScale()
                * self.spriteRenderer.getFixedScale())

            self.image.blit(self.fontImage, rect)

        else:
            self.image = pygame.Surface((
                    self.drawerWidth * self.game.renderer.getScale()
                    * self.spriteRenderer.getFixedScale(), self.drawerHeight
                    * self.game.renderer.getScale()
                    * self.spriteRenderer.getFixedScale()
                ), pygame.SRCALPHA).convert_alpha()

            self.rect = self.image.get_rect()
            self.rect.topleft = (
                self.drawerPos * self.game.renderer.getScale()
                * self.spriteRenderer.getFixedScale())

            pygame.draw.rect(self.image, self.color, (
                0, 0, self.rect.width, self.rect.height), border_radius=int(
                    10 * self.game.renderer.getScale()
                    * self.spriteRenderer.getFixedScale()))

    def makeSurface(self):
        if self.dirty or self.image is None:
            self.__render()

    def drawPaused(self, surface):
        self.makeSurface()
        surface.blit(self.image, (self.rect))

    def draw(self):
        self.makeSurface()
        self.game.renderer.addSurface(self.image, (self.rect))

    def events(self):
        mx, my = pygame.mouse.get_pos()
        difference = self.game.renderer.getDifference()
        mx -= difference[0]
        my -= difference[1]

        if self.open:
            # Click off event.
            if (not self.rect.collidepoint((mx, my))
                    and self.game.clickManager.getClicked()):
                self.closeHolder(True)

            return

        # Click event.
        if (self.rect.collidepoint((mx, my))
                and self.game.clickManager.getClicked()
                and self.canClick):
            self.game.clickManager.setClicked(False)
            self.game.audioLoader.playSound("expand")
            self.openHolder()

            # When we click on the holder it opens and we no longer need to
            # check for hover events
            self.mouseOver = False
            self.game.clickManager.setMouseOver(None)

        # Hover over event.
        elif (self.rect.collidepoint((mx, my)) and not self.mouseOver
                and self.game.clickManager.isTop(self)):
            self.mouseOver = True
            self.game.clickManager.setMouseOver(self)
            self.color = GREY
            self.dirty = True

        # Hover out event.
        elif not self.rect.collidepoint((mx, my)) and self.mouseOver:
            self.mouseOver = False
            self.game.clickManager.setMouseOver(None)
            self.color = WHITE
            self.dirty = True

    def update(self):
        if not hasattr(self, 'rect'):
            return

        self.events()
