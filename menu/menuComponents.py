import pygame
import string
import abc
import math
import copy
import os
from config import (
    config, FONTFOLDER, GREEN, BLACK, TRUEBLACK, SCANLINES, RED, YELLOW, WHITE)
from utils import vec, overrides
from transitionFunctions import transitionMessageRight
from engine import ImageLoader


class TextHandler:
    def __init__(self):
        self.active = False
        self.lengthReached = False
        self.pointer = self.previousPointer = 0
        self.string = []

        self.keys = list(string.ascii_letters) + list(string.digits)
        self.keys.append(" ")
        self.currentKey = None

    def getActive(self):
        return self.active

    def getPressed(self):
        return False if self.currentKey is None else True

    def getCurrentKey(self):
        return self.currentKey

    def getLengthReached(self):
        return self.lengthReached

    def getPointer(self):
        return self.pointer

    def getPreviousPointer(self):
        return self.previousPointer

    def getString(self, pointer=False):
        return (
            ''.join(self.string[:self.pointer]) if pointer
            else ''.join(self.string))

    def setCurrentKey(self, currentKey):
        self.currentKey = currentKey

    def setString(self, string=[]):
        self.string = string

    def setLengthReached(self, lengthReached):
        self.lengthReached = lengthReached

    def setPointer(self, pointer):
        if pointer > len(self.string) or pointer < 0:
            return
        self.previousPointer = self.pointer
        self.pointer = pointer

    def setPreviousPointer(self, previousPointer):
        self.previousPointer = previousPointer

    def removeLast(self):
        if self.pointer > 0:
            del self.string[self.pointer - 1]
            self.setPointer(self.pointer - 1)

    # When active clear the text so its ready for input
    def setActive(self, active):
        self.active = active

        if self.active:
            self.string = []
            self.pointer = 0

    def events(self, event):
        self.setCurrentKey(event.key)

        if self.active:
            if event.key == pygame.K_BACKSPACE:
                self.removeLast()
            else:
                if event.unicode in self.keys and not self.lengthReached:
                    if self.pointer == len(self.string):
                        self.string.append(event.unicode)

                    else:
                        b = self.string[:]
                        insert = self.pointer
                        b[insert:insert] = [event.unicode]
                        self.string = b

                    self.setPointer(self.pointer + 1)

                if event.key == config["controls"]["left"]["current"]:
                    self.setPointer(self.pointer - 1)
                elif event.key == config["controls"]["right"]["current"]:
                    self.setPointer(self.pointer + 1)


class MenuComponent:
    def __init__(self, menu, color=None, size=tuple(), pos=tuple()):
        self.menu = menu
        self.color = color
        self.width = size[0]
        self.height = size[1]
        self.x = pos[0]
        self.y = pos[1]
        self.size = size

        self.pos = vec(self.x, self.y)
        self.offset = vec(0, 0)

        self.events = []
        self.animations = {}
        self.components = []

        self.dirty = True
        self.responsive = True

        self.mouseOver = False
        self.clicked = False

        self.timer = 0  # For use in animation the component

    def getAnimations(self):
        return self.animations

    def getOffset(self):
        return self.offset

    def getColor(self):
        return self.color

    def getTimer(self):
        return self.timer

    def getRightX(self):
        return self.x + self.width

    def getBottomY(self):
        return self.y + self.height

    def setSize(self, size=tuple()):
        self.width = size[0]
        self.height = size[1]

    def setColor(self, color):
        self.color = color

    def setPos(self, pos=tuple()):
        self.x = pos[0]
        self.y = pos[1]

    def setOffset(self, offset):
        self.offset = offset

    def setTimer(self, timer):
        self.timer = timer

    def add(self, obj):
        self.components.append(obj)

    def addEvent(self, function, event, **kwargs):
        self.events.append(
            {'function': function, 'event': event, 'kwargs': kwargs})

    def addAnimation(self, function, event, **kwargs):
        self.animations[function] = (event, kwargs)

    def removeAnimation(self, function):
        del self.animations[function]

    def removeEvent(self, function, event, **kwargs):
        event = {'function': function, 'event': event, 'kwargs': kwargs}
        if event in self.events:
            self.events.remove(event)

    def clearAnimations(self):
        self.animations = {}

    def clearEvents(self):
        self.events = []

    def resize(self):
        self.dirty = True
        for component in self.components:
            component.resize()

    def addComponents(self):
        if self.image is None:
            return

        for component in list(self.components):
            component.drawPaused(self.image)
            # component.makeSurface()

            # if component.image is not None:
            #     self.image.blit(component.image, (component.rect))

    @abc.abstractmethod
    def makeSurface(self):
        return

    def drawPaused(self, surface):
        self.makeSurface()
        surface.blit(self.image, (self.rect))

    def draw(self):
        self.makeSurface()
        self.menu.renderer.addSurface(self.image, self.rect)

    @abc.abstractmethod
    def update(self):
        return


class Label(MenuComponent):
    def __init__(
            self, menu, text, fontSize, color, pos=tuple(),
            backgroundColor=None):
        super().__init__(menu, color, (1, 1), pos)

        self.text = str(text)
        self.finalMessage = []
        self.fontName = pygame.font.get_default_font()
        self.fontName = os.path.join(
            FONTFOLDER, config["fonts"]["whiteRabbit"])
        # self.fontName = os.path.join(FONTFOLDER, config["fonts"]["bitwise"])
        self.fontSize = fontSize
        self.bold = False
        self.italic = False
        self.underline = False
        self.backgroundColor = backgroundColor

        self.finalMessage = self.splitText()

    @overrides(MenuComponent)
    def getRightX(self):
        return self.x + self.getFontSize()[0]

    @overrides(MenuComponent)
    def getBottomY(self):
        return self.y + self.getFontSize()[1]

    def setFontSize(self, fontSize):
        self.fontSize = fontSize

    def setBackgrondColor(self, backgroundColor):
        self.backgroundColor = backgroundColor

    # get the total font size of all msg components in the finalMessage
    def getTotalFontSize(self, font, finalMessage):
        size = vec(0, 0)
        for msg in finalMessage:
            size.x += font.size(msg)[0]
            size.y += font.size(msg)[1]
        return size

    # we don't want to use self.font since this is multiplied by the
    # display size, which we don't want
    def getFontSize(self, text=None):
        text = self.text if text is None else text
        finalMessage = self.splitText(text)  # split into components

        font = pygame.font.Font(self.fontName, int(self.fontSize))
        font.set_bold(self.bold)
        font.set_italic(self.italic)
        font.set_underline(self.underline)

        return self.getTotalFontSize(font, finalMessage)

    # get the scaled font size by using the label font
    def getFontSizeScaled(self, text=None):
        text = self.text if text is None else text
        finalMessage = self.splitText(text)
        return self.getTotalFontSize(self.font, finalMessage)

    def getFontSizeInt(self):
        return self.fontSize

    def getCharPositions(self, text=None):
        text = self.text if text is None else text
        finalMessage = self.splitText(text)

        positions = []
        runningString = ''
        for msg in finalMessage:
            for char in list(msg):
                runningString += char
                pos = self.getFontSizeScaled(runningString)
                positions.append(pos)
            runningString += '\n'
        return positions

    def setFontName(self, fontName):
        self.fontName = fontName

    def setText(self, text):
        self.text = str(text)
        self.finalMessage = self.splitText()

    def setBold(self, bold):
        self.bold = bold

    def setItalic(self, italic):
        self.italic = italic

    def setUnderline(self, underline):
        self.underline = underline

    def getText(self):
        return self.text

    # Split the message at \n into individual components
    def splitText(self, text=None):
        text = self.text if text is None else text
        finalMessage = []

        if "\n" in text:
            for word in text.split("\n"):
                finalMessage.append(word.strip())

        else:
            finalMessage = [text]
        return finalMessage

    def __render(self):
        self.dirty = False

        self.font = pygame.font.Font(
            self.fontName, int(self.fontSize * self.menu.renderer.getScale()))

        self.font.set_bold(self.bold)
        self.font.set_italic(self.italic)
        self.font.set_underline(self.underline)

        labels = []
        width = height = y = 0
        for msg in self.finalMessage:
            label = self.font.render(
                msg, config["graphics"]["antiAliasing"], self.color,
                self.backgroundColor)
            labelWidth = label.get_rect().width / self.menu.renderer.getScale()

            # We want the width of the label to be the width of the max word
            if labelWidth > width:
                width = labelWidth

            height += label.get_rect().height / self.menu.renderer.getScale()
            labels.append(label)

        if self.backgroundColor is None:
            self.image = pygame.Surface((
                width * self.menu.renderer.getScale(),
                height * self.menu.renderer.getScale()),
                pygame.SRCALPHA, 32).convert_alpha()

        else:
            self.image = pygame.Surface((
                width * self.menu.renderer.getScale(),
                height * self.menu.renderer.getScale())).convert()
            self.image.fill(self.backgroundColor)

        for label in labels:
            self.image.blit(label, (0, y))
            y += label.get_rect().height

        self.rect = self.image.get_rect()

        # Set the width, height to the exact size of the font
        self.width = width
        self.height = height

        # Reset the x, y coordinates since these are set to 0 in get_rect()
        self.rect.x = self.x * self.menu.renderer.getScale()
        self.rect.y = self.y * self.menu.renderer.getScale()

    @overrides(MenuComponent)
    def makeSurface(self):
        if self.dirty or self.image is None:
            self.__render()


class ControlKey(Label):
    def __init__(self, menu, text, fontSize, color, pos=tuple(), border=True):
        super().__init__(menu, text, fontSize, color, pos)
        self.offset = vec(20, 10)
        self.border = border

    def getBorder(self):
        return self.border

    def setBorder(self, border):
        self.border = border

    def __render(self):
        super().makeSurface()

        # Increase the width and height to include the offset for the border
        # since it currently just has the size for the label
        self.width += self.offset.x
        self.height += self.offset.y

        self.finalImage = pygame.Surface((
            self.width * self.menu.renderer.getScale(),
            self.height * self.menu.renderer.getScale()),
            pygame.SRCALPHA, 32).convert_alpha()
        self.finalImage.blit(self.image, (
            (self.offset.x / 2) * self.menu.renderer.getScale(),
            (self.offset.y / 2 + 1) * self.menu.renderer.getScale()))
        self.rect = self.finalImage.get_rect()

        # Reset the x, y coordinates since these are set to 0 in get_rect()
        self.rect.x = self.x * self.menu.renderer.getScale()
        self.rect.y = (self.y - 5) * self.menu.renderer.getScale()

        # Add the border to the image
        if self.border:
            border = Rectangle(
                self.menu, self.color, (self.width, self.height), (0, 0),
                shapeOutline=3, shapeBorderRadius=[10, 10, 10, 10])
            border.drawPaused(self.finalImage)

    @overrides(Label)
    def makeSurface(self):
        if self.dirty or self.image is None:
            self.__render()

    @overrides(Label)
    def draw(self):
        self.makeSurface()
        self.menu.renderer.addSurface(self.finalImage, self.rect)

    @overrides(Label)
    def drawPaused(self, surface):
        self.makeSurface()
        surface.blit(self.finalImage, (self.rect))


class ControlLabel(Label):
    def __init__(self, menu, text, keyName, fontSize, color, pos=tuple()):
        super().__init__(menu, text, fontSize, color, pos)
        self.keyName = keyName
        self.keyInt = config["controls"][keyName]["current"]
        self.initialKeyInt = copy.deepcopy(self.keyInt)
        self.keyText = pygame.key.name(self.keyInt)
        self.keyTextFontSize = self.fontSize
        self.keyTextBorder = True
        self.spacing = 15

    def getKeyName(self):
        return self.keyName

    def getKeyInt(self):
        return self.keyInt

    def getInitialKeyInt(self):
        return self.initialKeyInt

    def getKeyText(self):
        return self.keyText

    def getKeyTextFontSize(self):
        return self.keyTextFontSize

    def getKeyTextBorder(self):
        return self.keyTextBorder

    def setKeyInt(self, keyInt):
        self.keyInt = keyInt

    def setKeyText(self, keyText):
        self.keyText = keyText

    def setKeyTextFontSize(self, keyTextFontSize):
        self.keyTextFontSize = keyTextFontSize

    def setKeyTextBorder(self, keyTextBorder):
        self.keyTextBorder = keyTextBorder

    def __render(self):
        super().makeSurface()
        key = ControlKey(
            self.menu, self.keyText, self.keyTextFontSize, self.color, (0, 0),
            self.keyTextBorder)
        key.setPos(
            (self.width + self.spacing, key.getOffset().y / 2))

        # Increase the width and height to include the key
        self.width += (
            key.getOffset().x + self.spacing + key.getFontSize()[0])
        self.height += key.getOffset().y

        self.finalImage = pygame.Surface((
            self.width * self.menu.renderer.getScale(),
            self.height * self.menu.renderer.getScale()),
            pygame.SRCALPHA, 32).convert_alpha()
        self.finalImage.blit(self.image, (
            0, (key.getOffset().y / 2) * self.menu.renderer.getScale()))
        self.rect = self.finalImage.get_rect()

        # Reset the x, y coordinates since these are set to 0 in get_rect()
        self.rect.x = self.x * self.menu.renderer.getScale()
        self.rect.y = (
            (self.y - (key.getOffset().y / 2))
            * self.menu.renderer.getScale())

        key.drawPaused(self.finalImage)

    @overrides(Label)
    def makeSurface(self):
        if self.dirty or self.image is None:
            self.__render()

    @overrides(Label)
    def draw(self):
        self.makeSurface()
        self.menu.renderer.addSurface(self.finalImage, self.rect)

    @overrides(Label)
    def drawPaused(self, surface):
        self.makeSurface()
        surface.blit(self.finalImage, (self.rect))


class InputBox(Label):
    def __init__(
            self, menu, fontSize, color, background, width, pos=tuple(),
            backgroundColor=None):
        super().__init__(menu, "", fontSize, color, pos, backgroundColor)
        self.menu.game.textHandler.setString([])
        self.menu.game.textHandler.setPointer(0)
        self.inputWidth = width  # max length of text input

        self.flashing = True
        self.background = background
        self.indicator = Rectangle(
            self.menu, self.color, (
                3, self.getFontSize("hello world!")[1]), self.pos)

    # TODO: a better way to do this without using the textHandler
    # (just setting the string directly)
    def setDefaultText(self, defaultText):
        self.menu.game.textHandler.setString(str(defaultText))
        self.menu.game.textHandler.setPointer(len(str(defaultText)))

    def setText(self):
        width = (self.getFontSizeScaled(
            self.menu.game.textHandler.getString())[0]
            / self.menu.renderer.getScale())

        if width < self.inputWidth:
            self.menu.game.textHandler.setLengthReached(False)

        else:
            self.menu.game.textHandler.setLengthReached(True)
            self.menu.game.textHandler.removeLast()
            return

        # Update the text of the inputbox to be the new string
        super().setText(self.menu.game.textHandler.getString())
        self.dirty = True

    def moveIndicator(self):
        if hasattr(self.indicator, 'rect'):
            self.indicator.x = (self.x + self.getFontSizeScaled(
                self.menu.game.textHandler.getString(True))[0]
                / self.menu.renderer.getScale())
            self.indicator.rect.x = (
                self.indicator.x * self.menu.renderer.getScale())

    def setFlashing(self):
        if (self.menu.game.textHandler.getPointer()
                != self.menu.game.textHandler.getPreviousPointer()):
            self.moveIndicator()
            self.menu.game.textHandler.setPreviousPointer(
                self.menu.game.textHandler.getPointer())

        self.timer += 60 * self.menu.game.dt

        # every 25ms
        if self.timer >= 25:
            self.flashing = not self.flashing
            self.timer = 0

    def resizeIndicator(self):
        self.indicator.dirty = True

    @overrides(Label)
    def draw(self):
        super().draw()

        if self.flashing:
            self.indicator.draw()

    @overrides(Label)
    def drawPaused(self, surface):
        self.makeSurface()
        surface.blit(self.image, (self.rect))
        self.indicator.drawPaused(surface)

    @overrides(Label)
    def update(self):
        if not hasattr(self, 'rect'):
            return

        self.setFlashing()

        # change the text
        if (self.menu.game.textHandler.getActive()
                and self.text != self.menu.game.textHandler.getString()):
            self.setText()

        mx, my = pygame.mouse.get_pos()
        difference = self.menu.renderer.getDifference()
        mx -= difference[0]
        my -= difference[1]
        indicatorPos = 0

        if (self.rect.collidepoint((mx, my))
                and self.menu.game.clickManager.getClicked()):
            self.menu.game.clickManager.setClicked(False)
            positions = [x[0] for x in self.getCharPositions()]
            positions.insert(0, 0)

            # Get the positions in the center of each character
            newPositions = []
            for x in range(len(positions) - 1):
                newPositions.append(
                    positions[x] + ((positions[x + 1] - positions[x]) / 2))

            for x in range(len(newPositions)):
                # Final character in the list
                if (x + 1 >= len(newPositions)
                        and mx - self.rect.x > newPositions[x]):
                    indicatorPos = x + 1
                    break
                elif (mx - self.rect.x > newPositions[x]
                        and mx - self.rect.x < newPositions[x + 1]):
                    indicatorPos = x + 1
                    break

            self.menu.game.textHandler.setPointer(indicatorPos)

        elif (self.background.rect.collidepoint((mx, my))
                and self.menu.game.clickManager.getClicked()):
            self.menu.game.clickManager.setClicked(False)

            # if we click anywhere in the box greater than the length
            # of the text, set the pointer to the max position
            if mx > self.rect.x + self.rect.width:
                indicatorPos = len(self.text)

            self.menu.game.textHandler.setPointer(indicatorPos)


# TODO: finish this implementation
class NumberIncrementer(Label):
    def __init__(
            self, menu, defaultAmount, fontSize, color, pos=tuple(),
            backgroundColor=None, minAmount=0, maxAmount=10):
        self.defaultAmount = int(defaultAmount)
        self.minAmount = int(minAmount)
        self.maxAmount = int(maxAmount)

        # Check default value in range
        if (self.defaultAmount < self.minAmount
                or self.defaultAmount > self.maxAmount):
            self.defaultAmount = int(
                round((self.minAmount + self.maxAmount) / 2, 0))

        super().__init__(
            menu, self.defaultAmount, fontSize, color, pos, backgroundColor)

    def __render(self):
        super().makeSurface()

        # print(self.getFontSize())

        upArrowBox = Rectangle(
            self.menu, BLACK, (5, self.getFontSize()[1] / 2), (0, 0))
        downArrowBox = Rectangle(
            self.menu, RED, (5, self.getFontSize()[1] / 2), (0, 11))

        upArrowBox.drawPaused(self.image)
        downArrowBox.drawPaused(self.image)

    @overrides(Label)
    def makeSurface(self):
        if self.dirty or self.image is None:
            self.__render()


class Shape(MenuComponent):
    def __init__(
            self, menu, color, size=tuple(), pos=tuple(), shapeOutline=0,
            shapeBorderRadius=[0, 0, 0, 0], alpha=None, fill=None):
        super().__init__(menu, color, size, pos)
        self.shapeOutline = shapeOutline
        self.shapeBorderRadius = shapeBorderRadius
        self.alpha = alpha
        self.fill = fill

        if not config["graphics"]["smoothCorners"]:
            self.shapeBorderRadius = [0, 0, 0, 0]

    def getShapeType(self):
        return self.shapeType

    def getShapeOutline(self):
        return self.shapeOutline

    def getAlpha(self):
        return self.alpha if self.alpha is not None else 0

    def setShapeType(self, shapeType):
        self.shapeType = shapeType

    def setShapeOutline(self, shapeOutline):
        self.shapeOutline = shapeOutline

    def setAlpha(self, alpha):
        self.alpha = alpha

    def setRect(self):
        pos = vec(self.x, self.y) * self.menu.renderer.getScale()
        size = vec(self.width, self.height) * self.menu.renderer.getScale()
        self.rect = pygame.Rect(pos, size)
        return pos, size

    def setBorder(self):
        self.outline = self.shapeOutline * self.menu.renderer.getScale()
        self.borderRadius = [
            i * self.menu.renderer.getScale() for i in self.shapeBorderRadius]

    def __render(self):
        self.dirty = False

        pos, size = self.setRect()
        self.setBorder()

        # Create the image for blitting onto other
        # surfaces, even if its not used in this shape
        self.image = pygame.Surface(size).convert()
        if self.alpha is not None:
            self.image.set_alpha(self.alpha, pygame.RLEACCEL)
        if self.fill is not None:
            self.drawShape(self.image, self.fill, pygame.Rect(0, 0, *size), 0)
        self.drawShape(
            self.image, self.color, pygame.Rect(0, 0, *size), self.outline)

        self.addComponents()

    @abc.abstractmethod
    def drawShape(self, surface, color=None, rect=None, outline=None):
        return

    # Get either the object attribute or variable
    # depending on if its None or not
    def getShapeComponents(self, color, rect, outline):
        color = self.color if color is None else color
        rect = self.rect if rect is None else rect
        outline = self.outline if outline is None else outline

        return color, rect, outline

    @overrides(MenuComponent)
    def makeSurface(self):
        if self.dirty or self.rect is None:
            self.__render()

    @overrides(MenuComponent)
    def drawPaused(self, surface):
        self.makeSurface()
        if (self.alpha is not None or len(self.components) > 0
                or self.fill is not None):
            surface.blit(self.image, (self.rect))

        else:
            self.drawShape(surface)

    @overrides(MenuComponent)
    def draw(self):
        self.makeSurface()
        if (self.alpha is not None or len(self.components) > 0
                or self.fill is not None):
            self.menu.renderer.addSurface(self.image, (self.rect))

        else:
            self.menu.renderer.addSurface(None, None, self.drawShape)


class Rectangle(Shape):
    def __init__(
            self, menu, color, size=tuple(), pos=tuple(), shapeOutline=0,
            shapeBorderRadius=[0, 0, 0, 0], alpha=None, fill=None):
        super().__init__(
            menu, color, size, pos, shapeOutline, shapeBorderRadius, alpha,
            fill)

    @overrides(Shape)
    def drawShape(
            self, surface, color=None, rect=None, outline=None,
            borderRadius=None):
        color, rect, outline = self.getShapeComponents(color, rect, outline)
        borderRadius = (
            self.borderRadius if borderRadius is None else borderRadius)

        pygame.draw.rect(
            surface, color, rect, int(outline),
            border_top_left_radius=int(borderRadius[0]),
            border_top_right_radius=int(borderRadius[1]),
            border_bottom_left_radius=int(borderRadius[2]),
            border_bottom_right_radius=int(borderRadius[3]))


class Meter(Rectangle):
    def __init__(
            self, menu, color, outlineColor, innerColor, amount=tuple(),
            size=tuple(), pos=tuple(), shapeOutline=0,
            shapeBorderRadius=[0, 0, 0, 0], alpha=None):
        super().__init__(
            menu, color, size, pos, shapeOutline, shapeBorderRadius, alpha)
        self.outlineColor = outlineColor
        self.innerColor = innerColor
        self.amount = amount

    def setAmount(self, amount=tuple()):
        self.amount = amount

    def getAmount(self, amount):
        return self.amount

    def __render(self):
        self.dirty = False

        pos, size = self.setRect()
        sizeAmount = (
            vec(self.amount[0], self.amount[1])
            * self.menu.renderer.getScale())
        self.rectAmount = pygame.Rect(pos, sizeAmount)

        self.setBorder()

        self.image = pygame.Surface(size, pygame.SRCALPHA, 32).convert_alpha()
        self.drawShape(
            self.image, self.color, pygame.Rect(0, 0, *size),
            pygame.Rect(0, 0, *sizeAmount), self.outline)

        self.addComponents()

    @overrides(Rectangle)
    def drawShape(
            self, surface, color=None, rect=None, rectAmount=None,
            outline=None):
        rectAmount = self.rectAmount if rectAmount is None else rectAmount

        self.rectAmount.x = self.rect.x
        self.rectAmount.y = self.rect.y

        super().drawShape(surface, color, rect, 0)
        super().drawShape(surface, self.innerColor, rectAmount, 0)
        super().drawShape(surface, self.outlineColor, rect, outline)

    @overrides(Rectangle)
    def makeSurface(self):
        if self.dirty or self.image is None:
            self.__render()


class DifficultyMeter(Rectangle):
    def __init__(
            self, menu, foregroundcolor, backgroundColor, length, amount,
            spacing, size=tuple(), pos=tuple(), shapeOutline=0,
            shapeBorderRadius=[0, 0, 0, 0], alpha=None, fill=None):
        super().__init__(
            menu, foregroundcolor, size, pos, shapeOutline, shapeBorderRadius,
            alpha, fill)
        self.backgroundColor = backgroundColor
        self.length = length
        self.amount = amount
        self.spacing = spacing
        self.fullSize = (
            (self.width * self.length) + (self.spacing * self.length),
            self.height)

    def getAmount(self):
        return self.amount

    def getFullSize(self):
        return self.fullSize

    def setAmount(self, amount):
        self.amount = amount

    def __render(self):
        self.dirty = False

        pos, size = self.setRect()
        self.setBorder()
        self.gap = self.spacing * self.menu.renderer.getScale()

        self.fullsize = copy.copy(size)
        self.fullsize[0] = (size[0] * self.length) + (self.gap * self.length)

        self.image = pygame.Surface(self.fullsize).convert()
        if self.alpha is not None:
            self.image.set_alpha(self.alpha, pygame.RLEACCEL)
        if self.fill is not None:
            self.drawShape(self.image, self.fill, pygame.Rect(0, 0, *size), 0)
        self.drawShape(
            self.image, self.color, pygame.Rect(0, 0, *size), self.outline)

    @overrides(Rectangle)
    def drawShape(self, surface, color=None, rect=None, outline=None):
        rect = self.rect if rect is None else rect
        offx = rect.x
        remaining = self.length - self.amount

        for x in range(self.amount):
            newRect = pygame.Rect(offx, rect.y, rect.width, rect.height)
            super().drawShape(surface, color, newRect, outline)
            offx += rect.width + self.gap

        for i in range(remaining):
            newRect = pygame.Rect(offx, rect.y, rect.width, rect.height)
            super().drawShape(surface, self.backgroundColor, newRect, outline)
            offx += rect.width + self.gap

    @overrides(Rectangle)
    def makeSurface(self):
        if self.dirty or self.rect is None:
            self.__render()


class Slider(Rectangle):
    def __init__(
            self, menu, color, amount, callback, size=tuple(), pos=tuple(),
            shapeOutline=0, shapeBorderRadius=[0, 0, 0, 0], alpha=None,
            fill=None):
        super().__init__(
            menu, color, size, pos, shapeOutline, shapeBorderRadius, alpha,
            fill)
        self.totalAmount = 100
        self.amount = amount * self.totalAmount
        self.callback = callback
        self.y -= (self.height / 2)

        self.handleWidth = max(self.width / 20, 10)
        self.handleX = self.x + (self.amount * (
            (self.width - self.handleWidth) / self.totalAmount))

    def getAmount(self):
        return self.amount / self.totalAmount

    def setAmount(self, amount):
        self.amount = amount * self.totalAmount
        self.handleX = self.x + (self.amount * (
            (self.width - self.handleWidth) / self.totalAmount))
        self.dirty = True

    def __render(self):
        self.dirty = False

        pos, size = self.setRect()
        posBar = vec(self.x, self.y + (self.height / 2)) * \
            self.menu.renderer.getScale()
        posHandle = vec(self.handleX, self.y) * self.menu.renderer.getScale()
        sizeHandle = vec(self.handleWidth, self.height * 2) * \
            self.menu.renderer.getScale()
        self.rectBar = pygame.Rect(posBar, size)
        self.rectHandle = pygame.Rect(posHandle, sizeHandle)

        self.setBorder()

        fullSize = vec(size[0], sizeHandle[1])

        self.image = pygame.Surface(fullSize).convert()
        if self.alpha is not None:
            self.image.set_alpha(self.alpha, pygame.RLEACCEL)
        if self.fill is not None:
            self.drawShape(self.image, self.fill, pygame.Rect(
                0, (self.height / 2) * self.menu.renderer.getScale(), *size), pygame.Rect(0, 0, *sizeHandle), 0)
        self.drawShape(
            self.image, self.color, pygame.Rect(0, (self.height / 2) * self.menu.renderer.getScale(), *size), pygame.Rect(0, 0, *sizeHandle), self.outline)

        self.addComponents()

    @overrides(Rectangle)
    def drawShape(
            self, surface, color=None, rect=None, rectHandle=None,
            outline=None):
        rect = self.rectBar if rect is None else rect
        rectHandle = self.rectHandle if rectHandle is None else rectHandle

        super().drawShape(surface, color, rect, outline)
        super().drawShape(surface, BLACK, rectHandle, 0, [20, 20, 20, 20])

    @overrides(Rectangle)
    def makeSurface(self):
        if self.dirty or self.rect is None:
            self.__render()

    @overrides(Rectangle)
    def update(self):
        if not hasattr(self, 'rect'):
            return

        mx, my = pygame.mouse.get_pos()
        difference = self.menu.renderer.getDifference()
        mx -= difference[0]
        my -= difference[1]

        self.amount = (
            (self.handleX - self.x)
            / ((self.width - self.handleWidth) / self.totalAmount))

        if (self.rectHandle.collidepoint((mx, my))
                and pygame.mouse.get_pressed()[0]):
            self.clicked = True
        elif not pygame.mouse.get_pressed()[0] and self.clicked:
            self.clicked = False
            self.callback(self, self.getAmount())

        if self.clicked:
            self.handleX = (
                (mx / self.menu.renderer.getScale()) - (self.handleWidth / 2))

            if self.handleX <= self.x:
                self.handleX = self.x
            elif self.handleX >= (self.x + self.width) - self.handleWidth:
                self.handleX = (self.x + self.width) - self.handleWidth

            self.rectHandle.x = self.handleX * self.menu.renderer.getScale()


class Ellipse(Shape):
    def __init__(
            self, menu, color, size=tuple(), pos=tuple(), shapeOutline=0,
            alpha=None, fill=None):
        super().__init__(
            menu, color, size, pos, shapeOutline, alpha=alpha, fill=fill)

    @overrides(Shape)
    def drawShape(self, surface, color=None, rect=None, outline=None):
        color, rect, outline = self.getShapeComponents(color, rect, outline)
        pygame.draw.ellipse(surface, color, rect, int(outline))


class Arc(Shape):
    def __init__(
            self, menu, color, startAngle, stopAngle, size=tuple(),
            pos=tuple(), shapeOutline=0, alpha=None, fill=None):
        super().__init__(
            menu, color, size, pos, shapeOutline, alpha=alpha, fill=fill)
        self.startAngle = startAngle
        self.stopAngle = stopAngle

    def setStartAngle(self, startAngle):
        self.startAngle = startAngle

    def setStopAngle(self, stopAngle):
        self.stopAngle = stopAngle

    @overrides(Shape)
    def drawShape(self, surface, color=None, rect=None, outline=None):
        color, rect, outline = self.getShapeComponents(color, rect, outline)
        pygame.draw.arc(
            surface, color, rect, self.startAngle, self.stopAngle,
            int(outline))


class Timer(Arc):
    def __init__(
            self, menu, backgroundColor, foregoundColor, timer, step,
            size=tuple(), pos=tuple(), shapeOutline=0, alpha=None, fill=None):
        super().__init__(
            menu, foregoundColor, 0, 0, size, pos, shapeOutline, alpha, fill)
        self.timer = timer
        self.length = 100
        self.step = self.length / step
        self.backgroundColor = backgroundColor

    def getStep(self):
        return self.step

    def setBackgroundColor(self, backgroundColor):
        self.backgroundColor = backgroundColor

    def __render(self):
        self.dirty = False

        step = (self.length - self.timer) / (self.length / 2)
        self.startAngle = math.pi / 2 + math.pi * step
        self.stopAngle = math.pi / 2

        pos, size = self.setRect()
        self.setBorder()

        self.image = pygame.Surface(size, pygame.SRCALPHA, 32).convert_alpha()
        # self.image.fill(BLACK)
        # self.image.set_alpha(255, pygame.RLEACCEL)
        self.drawShape(
            self.image, self.color, pygame.Rect(0, 0, *size), self.outline)

    @overrides(Arc)
    def drawShape(self, surface, color=None, rect=None, outline=None):
        color, rect, outline = self.getShapeComponents(color, rect, outline)
        offx = 0.01

        # inside circle
        pygame.draw.ellipse(
            surface, self.backgroundColor, rect, int(outline - 1))

        # outside timer
        for x in range(6):
            pygame.draw.arc(
                surface, color, rect, self.startAngle + offx, self.stopAngle,
                int(outline))
            offx += 0.01

    @overrides(Arc)
    def makeSurface(self):
        if self.dirty or self.rect is None:
            self.__render()


class MessageBox(Rectangle):
    def __init__(self, menu, message, margin=tuple()):
        super().__init__(menu, GREEN, (0, 0), (0, 0), 0, [10, 10, 10, 10])
        self.messages = []
        self.marginX = margin[0]
        self.marginY = margin[1]
        self.message = message
        self.offset = vec(10, 10)

        self.addLabels(message)

    def setPos(self, pos=tuple()):
        self.x = pos[0]
        self.y = pos[1]
        for message in self.messages:
            width = message.getFontSize()[0]
            message.setPos((
                (pos[0] + self.width) - (width + self.offset.x),
                (pos[1] + self.offset.y) + message.offset.y))

    def setRectPos(self):
        self.rect.x = self.x * self.menu.renderer.getScale()
        self.rect.y = self.y * self.menu.renderer.getScale()
        for message in self.messages:
            if hasattr(message, 'rect'):
                message.rect.x = message.x * self.menu.renderer.getScale()
                message.rect.y = message.y * self.menu.renderer.getScale()

    def addMessages(self):
        for message in self.messages:
            self.menu.add(message)

    def addLabels(self, message):
        maxCharLimit = 25
        curWord = 0
        finalMessage = ['']
        for word in message.split():
            if len(finalMessage[curWord]) + len(word) < maxCharLimit:
                finalMessage[curWord] += word + ' '
            else:
                finalMessage.append(word + ' ')
                curWord += 1

        del maxCharLimit, curWord

        biggestWidth, totalHeight = 0, 0
        for msg in finalMessage:
            # first we set the x and y to 0 since we don't know the width yet
            m = Label(self.menu, msg, 25, WHITE, (0, 0))
            width, height = m.getFontSize()
            m.setOffset(vec(0, totalHeight))
            totalHeight += height

            if width > biggestWidth:
                biggestWidth = width

            self.messages.append(m)

        self.setSize((
            biggestWidth + (self.offset.x * 2),
            totalHeight + (self.offset.y * 2)))

        # pos:
        #   x = displaywidth - (width of the biggest message + width of
        #   the margin + width of the offset * 2 (for both sides)
        #   y = 0 - the total height of the message box + height of
        #    the offset * 2 (for both sides)

        self.setPos((
            config["graphics"]["displayWidth"] - (
                biggestWidth + self.marginX + (self.offset.x * 2)),
            0 - (totalHeight + (self.offset.y * 2))))

    def remove(self):
        self.menu.components.remove(self)
        self.menu.removeMessage(self.message)
        for message in self.messages:
            self.menu.components.remove(message)

        del self

    @overrides(Rectangle)
    def drawPaused(self, surface):
        self.makeSurface()
        self.drawShape(surface)

    @overrides(Rectangle)
    def draw(self):
        self.makeSurface()
        self.menu.renderer.addSurface(None, None, self.drawShape)
        # self.menu.renderer.addSurface(self.image, (self.rect))

    @overrides(Rectangle)
    def update(self):
        self.timer += self.menu.game.dt

        if self.timer > 4:
            self.addAnimation(
                transitionMessageRight, 'onLoad', speed=18,
                x=config["graphics"]["displayWidth"])
            # self.menu.components.remove(self)
            # for message in self.messages:
            #     self.menu.components.remove(message)


# A class for any selectable component in the level selection screens.
# - i.e. a map or a region for different maps.
class LevelSelect(MenuComponent, metaclass=abc.ABCMeta):
    def __init__(
            self, menu, name, borderColor, size=tuple(), pos=tuple()):
        super().__init__(menu, borderColor, size, pos)
        self.name = name
        self.levelData = {}  # Default level data
        self.scanlinesLockedOpacity = 65

    def getName(self):
        return self.name

    def getLevelData(self):
        return self.levelData

    # Draw scanlines to the component if enabled.
    def drawScanlines(self):
        if not config["graphics"]["scanlines"]["enabled"]:
            return

        scanlines = pygame.Surface((
            int(self.width * self.menu.renderer.getScale()),
            int(self.height * self.menu.renderer.getScale())))

        fillColor = (
            TRUEBLACK if self.levelData["locked"]["isLocked"]
            else SCANLINES)
        scanlines.fill(fillColor)

        self.menu.renderer.drawScanlines(scanlines)
        alpha = (
            self.scanlinesLockedOpacity if self.levelData["locked"]["isLocked"]
            else config["graphics"]["scanlines"]["opacity"])
        scanlines.set_alpha(alpha, pygame.RLEACCEL)

        self.image.blit(scanlines, (0, 0))

    # Show that the level is locked and the amount of keys to unlock it.
    def drawLocked(self):
        if not self.levelData["locked"]["isLocked"]:
            return

        locked = Image(self.menu, "locked", (100, 100), (
            self.width / 2 - 50, self.height / 2 - 50))
        key = Image(self.menu, "keyGreen", (30, 30), (
            self.width / 2 - 80, self.height - 50))

        # The amount required to unlock the level.
        unlock = Label(
            self.menu, str(self.levelData["locked"]["unlock"]), 20, RED,
            (key.x + key.width + 10, key.y + (key.height / 2) - 8))
        keyText = Label(self.menu, "to unlock", 20, GREEN, (
            unlock.x + unlock.getFontSize()[0] + 5, unlock.y))

        # Draw the components to the image.
        locked.drawPaused(self.image)
        key.drawPaused(self.image)
        unlock.drawPaused(self.image)
        keyText.drawPaused(self.image)

        # draw the overlay when the scanlines aren't enabled
        if not config["graphics"]["scanlines"]["enabled"]:
            overlay = pygame.Surface((
                int(self.width * self.menu.renderer.getScale()),
                int(self.height * self.menu.renderer.getScale())))
            overlay.fill(BLACK)
            overlay.set_alpha(95)
            self.image.blit(overlay, (0, 0))

    # Make the corners of the component rounded.
    def roundedCorners(self):
        size = self.image.get_size()
        rectImage = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(
            rectImage, WHITE, (0, 0, *size),
            border_radius=int(50 * self.menu.renderer.getScale()))
        self.image.blit(rectImage, (0, 0), None, pygame.BLEND_RGBA_MIN)

        pygame.draw.rect(
            self.image, self.color, (0, 0, *size),
            width=int(10 * self.menu.renderer.getScale()),
            border_radius=int(30 * self.menu.renderer.getScale()))

    @overrides(MenuComponent)
    def draw(self):
        self.makeSurface()
        # It is more efficient to render the final image.
        self.menu.renderer.addSurface(self.finalImage, self.rect)


class Map(LevelSelect):
    def __init__(self, menu, name, size=tuple(), pos=tuple()):
        super().__init__(menu, name, TRUEBLACK, size, pos)

        # Path to level
        self.level = menu.game.mapLoader.getMap(self.name)

        # Level JSON data
        self.levelData = menu.game.mapLoader.getMapData(self.name)

    def getLevelPath(self):
        return self.level

    def drawDifficulty(self):
        textColor = BLACK

        # can't use sprite renderer dark mode since it wont be different
        # for every map
        if ("backgrounds" in self.levelData
                and "darkMode" in self.levelData["backgrounds"]
                and self.levelData["backgrounds"]["darkMode"]):
            textColor = WHITE

        difficultyText = Label(
            self.menu, "Difficulty", 15, textColor, (30, self.height - 60))
        difficultyText.drawPaused(self.image)

        difficulty = DifficultyMeter(
            self.menu, RED, textColor, 4, self.levelData["difficulty"], 2,
            (15, 15), (30, difficultyText.y + (
                difficultyText.getFontSizeScaled()[1]
                / self.menu.renderer.getScale() + 5)))
        difficulty.drawPaused(self.image)

    def drawScore(self):
        if "score" not in self.levelData:
            return

        textColor = BLACK

        if ("backgrounds" in self.levelData
                and "darkMode" in self.levelData["backgrounds"]
                and self.levelData["backgrounds"]["darkMode"]):
            textColor = WHITE

        scoreText = Label(
            self.menu, "Score", 15, textColor, (140, self.height - 60))
        scoreText.drawPaused(self.image)

        score = DifficultyMeter(
            self.menu, YELLOW, textColor, 3, self.levelData["score"], 2,
            (15, 15), (140, scoreText.y + (
                scoreText.getFontSizeScaled()[1]
                / self.menu.renderer.getScale() + 5)))
        score.drawPaused(self.image)

    def __render(self):
        self.dirty = False
        self.finalImage = pygame.Surface((
            self.width * self.menu.renderer.getScale(),
            self.height * self.menu.renderer.getScale())).convert()

        # We get the level image of the map
        self.image = self.menu.game.spriteRenderer.createLevelSurface(
            self.level).convert_alpha()

        # We scale the level to the size of the map object
        self.image = pygame.transform.smoothscale(self.image, (int(
            self.width * self.menu.renderer.getScale()),
            int(self.height * self.menu.renderer.getScale()))).convert_alpha()\

        self.rect = self.image.get_rect()
        self.rect.x = self.x * self.menu.renderer.getScale()
        self.rect.y = self.y * self.menu.renderer.getScale()

        # add labels
        self.mapTitle = Label(self.menu, self.name, 30, GREEN, (30, 25))
        self.mapTitle.drawPaused(self.image)

        self.drawDifficulty()
        self.drawScore()
        self.drawLocked()
        self.drawScanlines()
        self.roundedCorners()

        self.finalImage.fill(self.menu.getBackgroundColor())
        self.finalImage.blit(self.image, (0, 0))

    @overrides(MenuComponent)
    def makeSurface(self):
        if self.dirty or self.image is None:
            self.__render()


class Region(LevelSelect):
    def __init__(self, menu, name, size=tuple(), pos=tuple()):
        super().__init__(menu, name, TRUEBLACK, size, pos)

        # Region JSON data
        self.levelData = menu.game.regionLoader.getRegion(self.name)

    def __render(self):
        self.dirty = False
        self.finalImage = pygame.Surface((
            self.width * self.menu.renderer.getScale(),
            self.height * self.menu.renderer.getScale())).convert()

        self.image = Image(self.menu, 'trainStation', (self.width, self.height), (0, 0))
        self.image.makeSurface()
        self.image = self.image.image

        self.rect = self.image.get_rect()
        self.rect.x = self.x * self.menu.renderer.getScale()
        self.rect.y = self.y * self.menu.renderer.getScale()

        self.drawLocked()
        self.drawScanlines()
        self.roundedCorners()

        self.finalImage.fill(self.menu.getBackgroundColor())
        self.finalImage.blit(self.image, (0, 0))

    @overrides(MenuComponent)
    def makeSurface(self):
        if self.dirty or self.image is None:
            self.__render()


class Image(MenuComponent):
    def __init__(self, menu, imageName, size=tuple(), pos=tuple(), alpha=None):
        super().__init__(menu, None, size, pos)
        self.imageName = imageName
        self.alpha = alpha
        self.xbool = False
        self.ybool = False
        self.rot = 0

    def getImageName(self):
        return self.imageName

    def getAlpha(self):
        return self.alpha if self.alpha is not None else 0

    def setImageName(self, imageName):
        self.imageName = imageName

    def setAlpha(self, alpha):
        self.alpha = alpha

    def flipImage(self, xbool=False, ybool=False):
        self.xbool = xbool
        self.ybool = ybool

    def rotateImage(self, angle):
        self.rot = angle

    def __render(self):
        self.dirty = False
        self.image = self.menu.game.imageLoader.getImage(
            self.imageName, (self.width, self.height))

        if self.xbool or self.ybool:
            self.image = ImageLoader.flipImage(
                self.image, self.xbool, self.ybool)
        if self.rot > 0:
            self.image = ImageLoader.rotateImage(self.image, self.rot)

        self.rect = self.image.get_rect()
        self.rect.x = self.x * self.menu.renderer.getScale()
        self.rect.y = self.y * self.menu.renderer.getScale()

        if self.alpha is not None:
            self.image.set_alpha(self.alpha, pygame.RLEACCEL)

        self.addComponents()

    @overrides(MenuComponent)
    def makeSurface(self):
        if self.dirty or self.image is None:
            self.__render()
