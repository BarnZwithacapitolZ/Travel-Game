import pygame 
from pygame.locals import *
from config import *
from transitionFunctions import transitionMessageRight
import string
import abc
import math
import copy

vec = pygame.math.Vector2


class TextHandler:
    def __init__(self):
        self.active = False
        self.lengthReached = False
        self.pressed = False
        self.pointer = 0
        self.string = []
        
        self.keys = list(string.ascii_letters) + list(string.digits)
        self.keys.append(" ")


    def getActive(self):
        return self.active


    def getPressed(self):
        return self.pressed


    def getLengthReached(self):
        return self.lengthReached


    def getPointer(self):
        return self.pointer


    def getString(self, pointer = False):
        return ''.join(self.string[:self.pointer]) if pointer else ''.join(self.string) 


    def setPressed(self, pressed):
        self.pressed = pressed


    def setString(self, string = []):
        self.string = string


    def setLengthReached(self, lengthReached):
        self.lengthReached = lengthReached


    def setPointer(self, pointer):
        if pointer > len(self.string) or pointer < 0:
            return
        self.pointer = pointer


    def removeLast(self):
        if self.pointer > 0:
            del self.string[self.pointer - 1]
            self.pointer -= 1


    # When active clear the text so its ready for input
    def setActive(self, active):
        self.active = active

        if self.active:
            self.string = []


    def events(self, event):
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

                    self.pointer += 1

                if pygame.key.name(event.key) == config["controls"]["left"]:
                    self.setPointer(self.pointer - 1)
                elif pygame.key.name(event.key) == config["controls"]["right"]:
                    self.setPointer(self.pointer + 1)


class MenuComponent:
    def __init__(self, menu, color = None, size = tuple(), pos = tuple()):
        self.menu = menu
        self.color = color
        self.width = size[0]
        self.height = size[1]
        self.x = pos[0]
        self.y = pos[1]
        self.size = size

        self.pos = vec(self.x, self.y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.offset = vec(0, 0)

        self.events = []
        self.animations = {}
        self.components = []

        self.dirty = True
        self.responsive = True

        self.mouseOver = False

        self.timer = 0 # For use in animation the component
        

    def getAnimations(self):
        return self.animations


    def getOffset(self):
        return self.offset


    def getColor(self):
        return self.color

    
    def getTimer(self):
        return self.timer


    def setSize(self, size = tuple()):
        self.width = size[0]
        self.height = size[1]


    def setColor(self, color):
        self.color = color


    def setPos(self, pos = tuple()):
        self.x = pos[0]
        self.y = pos[1]


    def setOffset(self, offset):
        self.offset = offset


    def setTimer(self, timer):
        self.timer = timer


    def add(self, obj):
        self.components.append(obj)


    def addEvent(self, function, event, **kwargs):
        self.events.append({'function': function, 'event': event, 'kwargs': kwargs})


    def addAnimation(self, function, event, **kwargs):
        self.animations[function] = (event, kwargs)


    def removeAnimation(self, function):
        del self.animations[function]


    def removeEvent(self, function, event, **kwargs):
        event = {'function': function, 'event': event,'kwargs': kwargs}
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


    def update(self):
        self.acc += self.vel * 0.5
        self.vel += self.acc * self.menu.game.dt
        self.pos += self.vel * self.menu.game.dt + 10 * self.acc * self.menu.game.dt ** 2

        self.rect.topleft = self.pos * self.menu.renderer.getScale()


    @abc.abstractmethod
    def __render(self):
        return


    @abc.abstractmethod
    def makeSurface(self):
        return


    def addComponents(self):
        if self.image is None: return

        for component in list(self.components):
            component.drawPaused(self.image)
            # component.makeSurface()
            
            # if component.image is not None:
            #     self.image.blit(component.image, (component.rect))


    def draw(self):
        self.makeSurface()
        self.menu.renderer.addSurface(self.image, self.rect)


    def drawPaused(self, surface):
        self.makeSurface()
        surface.blit(self.image, (self.rect))


class Label(MenuComponent):
    def __init__(self, menu, text, fontSize, color, pos = tuple()):
        super().__init__(menu, color, (1, 1), pos)

        self.text = text
        # self.fontName = pygame.font.get_default_font()
        self.fontName = os.path.join(FONTFOLDER, config["fonts"]["whiteRabbit"])
        # self.fontName = os.path.join(FONTFOLDER, config["fonts"]["bitwise"])
        self.fontSize = fontSize
        self.bold = False
        self.italic = False
        self.underline = False
        

    def setFontSize(self, fontSize):
        self.fontSize = fontSize


    # we don't want to use self.font since this is multiplied by the display size, which we don't want
    def getFontSize(self, text = None):
        text = self.text if text is None else text
        return pygame.font.Font(self.fontName, int(self.fontSize)).size(text)


    # get the scaled font size by using the label font
    def getFontSizeScaled(self, text = None):
        text = self.text if text is None else text
        return self.font.size(text)


    def getCharPositions(self, text = None):
        text = self.text if text is None else text
        runningString = ''
        positions = []

        for char in list(text):
            runningString += char
            pos = self.getFontSizeScaled(runningString)
            positions.append(pos)
        return positions


    def setFontName(self, fontName):
        self.fontName = fontName


    def setText(self, text):
        self.text = text


    def setBold(self, bold):
        self.bold = bold


    def setItalic(self, italic):
        self.italic = italic


    def setUnderline(self, underline):
        self.underline = underline


    def getText(self):
        return self.text


    def __render(self):
        self.dirty = False

        self.font = pygame.font.Font(self.fontName, int(self.fontSize * self.menu.renderer.getScale()))

        self.font.set_bold(self.bold)
        self.font.set_italic(self.italic)
        self.font.set_underline(self.underline)

        self.image = self.font.render(self.text, config["graphics"]["antiAliasing"], self.color).convert_alpha()

        self.rect = self.image.get_rect()

        # Scale down as font is automatically sized to scale when set
        self.width = self.rect.width / self.menu.renderer.getScale()
        self.height= self.rect.height / self.menu.renderer.getScale()

        self.rect.x = self.x * self.menu.renderer.getScale()
        self.rect.y = self.y * self.menu.renderer.getScale()


    def makeSurface(self):
        if self.dirty or self.image is None: self.__render()


class InputBox(Label):
    def __init__(self, menu, fontSize, color, background, width, pos = tuple()):
        super().__init__(menu, "", fontSize, color, pos)
        self.menu.game.textHandler.setString([])
        self.menu.game.textHandler.setPointer(0)
        self.inputWidth = width # max length of text input 

        self.flashing = True
        self.background = background
        self.indicator = Rectangle(self.menu, self.color, (3, fontSize), self.pos)


    def setText(self):   
        width = (self.getFontSizeScaled(self.menu.game.textHandler.getString())[0] / self.menu.renderer.getScale())
                
        if width < self.inputWidth:
            self.menu.game.textHandler.setLengthReached(False)
        else:
            self.menu.game.textHandler.setLengthReached(True)
            self.menu.game.textHandler.removeLast()
            return

        if self.text != self.menu.game.textHandler.getString():
            self.text = self.menu.game.textHandler.getString()
            self.dirty = True


    def setFlashing(self):
        if hasattr(self.indicator, 'rect'):
            self.indicator.x = self.x + self.getFontSizeScaled(self.menu.game.textHandler.getString(True))[0] / self.menu.renderer.getScale()
            self.indicator.rect.x = self.indicator.x * self.menu.renderer.getScale()

            self.timer += 60 * self.menu.game.dt

            # when timer hits 25 toggle flassing on / off
            if self.timer >= 25:
                self.flashing = not self.flashing
                self.timer = 0


    def resizeIndicator(self):
        self.indicator.dirty = True


    def drawPaused(self, surface):
        self.makeSurface()
        surface.blit(self.image, (self.rect))
        self.indicator.drawPaused(surface)

    
    def draw(self):
        super().draw()

        self.setFlashing()

        if self.flashing:
            self.indicator.draw()

        # change the text
        if self.menu.game.textHandler.getActive():
            self.setText()      


        mx, my = pygame.mouse.get_pos()
        difference = self.menu.renderer.getDifference()
        mx -= difference[0]
        my -= difference[1]
        
        if self.rect.collidepoint((mx, my)) and self.menu.game.clickManager.getClicked():
            self.menu.game.clickManager.setClicked(False)
            indicatorPos = 0
            positions = [x[0] for x in self.getCharPositions()]

            for x in range(len(positions)):
                if mx - self.rect.x > positions[x] and mx - self.rect.x < positions[x + 1]:
                    indicatorPos = x + 1
                    break
            
            self.menu.game.textHandler.setPointer(indicatorPos)
        
        if self.background.rect.collidepoint((mx, my)) and self.menu.game.clickManager.getClicked():
            self.menu.game.clickManager.setClicked(False)
            
            # if we click anywhere in the box greater than the length of the text, set the pointer to the max position
            if mx > self.rect.x + self.rect.width:
                self.menu.game.textHandler.setPointer(len(self.text))
       

class Shape(MenuComponent):
    def __init__(self, menu, color, size = tuple(), pos = tuple(), shapeOutline = 0, shapeBorderRadius = [0, 0, 0, 0], alpha = None, fill = None):   
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


    def __render(self):
        self.dirty = False

        pos = vec(self.x, self.y) * self.menu.renderer.getScale()
        size = vec(self.width, self.height) * self.menu.renderer.getScale()
        self.rect = pygame.Rect(pos, size)
        self.outline = self.shapeOutline * self.menu.renderer.getScale()
        self.borderRadius = [i * self.menu.renderer.getScale() for i in self.shapeBorderRadius]

        # Create the image for blitting onto other
        # surfaces, even if its not used in this shape
        self.image = pygame.Surface(size).convert()
        if self.alpha is not None: self.image.set_alpha(self.alpha, pygame.RLEACCEL)
        if self.fill is not None: self.drawShape(self.image, self.fill, Rect(0, 0, *size), 0)
        self.drawShape(self.image, self.color, Rect(0, 0, *size), self.outline)

        self.addComponents()


    @abc.abstractmethod
    def drawShape(self, surface, color = None, rect = None, outline = None):
        return


    # Get either the object attribute or variable depending on if its None or not
    def getShapeComponents(self, color, rect, outline):
        color = self.color if color is None else color
        rect = self.rect if rect is None else rect
        outline = self.outline if outline is None else outline

        return color, rect, outline


    def makeSurface(self):
        if self.dirty or self.rect is None: self.__render()

    
    def drawPaused(self, surface):
        self.makeSurface()
        if self.alpha is not None or len(self.components) > 0 or self.fill is not None:
            surface.blit(self.image, (self.rect))
        else:
            self.drawShape(surface)


    def draw(self):
        self.makeSurface()
        if self.alpha is not None or len(self.components) > 0 or self.fill is not None:
            self.menu.renderer.addSurface(self.image, (self.rect))
        else:
            self.menu.renderer.addSurface(None, None, self.drawShape)


class Rectangle(Shape):
    def __init__(self, menu, color, size = tuple(), pos = tuple(), shapeOutline = 0, shapeBorderRadius = [0, 0, 0, 0], alpha = None, fill = None):
        super().__init__(menu, color, size, pos, shapeOutline, shapeBorderRadius, alpha, fill)  


    def drawShape(self, surface, color = None, rect = None, outline = None):
        color, rect, outline = self.getShapeComponents(color, rect, outline)

        pygame.draw.rect(surface, color, rect, int(outline), 
                border_top_left_radius = int(self.borderRadius[0]),
                border_top_right_radius  = int(self.borderRadius[1]),
                border_bottom_left_radius = int(self.borderRadius[2]),
                border_bottom_right_radius = int(self.borderRadius[3]))


# Rectangle with on border radius that is made filling a shape, not drawing a rect
class FillRectangle(Rectangle):
    def __init__(self, menu, color, size = tuple(), pos = tuple(), shapeOutline = 0, fill = None):
        super().__init__(menu, color, size, pos, shapeOutline, fill = fill)


    def __render(self):
        self.dirty = False

        pos = vec(self.x, self.y) * self.menu.renderer.getScale()
        size = vec(self.width, self.height) * self.menu.renderer.getScale()
        self.outline = self.shapeOutline * self.menu.renderer.getScale()
        self.borderRadius = [0, 0, 0, 0] # Cant have a radius on a surface
        fillColor = self.fill if self.outline > 0 else self.color

        self.image = pygame.Surface(size, pygame.SRCALPHA).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = pos

        self.image.fill(fillColor)
        if self.outline > 0: super().drawShape(self.image, self.color, Rect(0, 0, *size), self.outline)

        self.addComponents()


    def makeSurface(self):
        if self.dirty or self.image is None: self.__render()


    def drawPaused(self, surface):
        self.makeSurface()
        surface.blit(self.image, (self.rect))

    
    def draw(self):
        self.makeSurface()
        self.menu.renderer.addSurface(self.image, (self.rect))


class Meter(Rectangle):
    def __init__(self, menu, color, outlineColor, innerColor, amount = tuple(), size = tuple(), pos = tuple(), shapeOutline = 0, shapeBorderRadius = [0, 0, 0, 0], alpha = None):
        super().__init__(menu, color, size, pos, shapeOutline, shapeBorderRadius, alpha)
        self.outlineColor = outlineColor
        self.innerColor = innerColor
        self.amount = amount

    
    def setAmount(self, amount = tuple()):
        self.amount = amount


    def getAmount(self, amount):
        return self.amount


    def __render(self):
        self.dirty = False

        pos = vec(self.x, self.y) * self.menu.renderer.getScale()
        size = vec(self.width, self.height) * self.menu.renderer.getScale()
        sizeAmount = vec(self.amount[0], self.amount[1]) * self.menu.renderer.getScale()
        
        self.rect = pygame.Rect(pos, size)
        self.rectAmount = pygame.Rect(pos, sizeAmount)
        
        self.outline = self.shapeOutline * self.menu.renderer.getScale()
        self.borderRadius = [i * self.menu.renderer.getScale() for i in self.shapeBorderRadius]

        self.image = pygame.Surface(size, pygame.SRCALPHA, 32).convert_alpha()
        self.drawShape(self.image, self.color, Rect(0, 0, *size), Rect(0, 0, *sizeAmount), self.outline)

        self.addComponents()

    
    def drawShape(self, surface, color = None, rect = None, rectAmount = None, outline = None):
        rectAmount = self.rectAmount if rectAmount is None else rectAmount

        self.rectAmount.x = self.rect.x
        self.rectAmount.y = self.rect.y

        super().drawShape(surface, color, rect, 0)
        super().drawShape(surface, self.innerColor, rectAmount, 0)       
        super().drawShape(surface, self.outlineColor, rect, outline)

    
    def makeSurface(self):
        if self.dirty or self.image is None: self.__render()



class DifficultyMeter(Rectangle):
    def __init__(self, menu, foregroundcolor, backgroundColor, length, amount, spacing, size = tuple(), pos = tuple(), shapeOutline = 0, shapeBorderRadius = [0, 0, 0, 0], alpha = None, fill = None):
        super().__init__(menu, foregroundcolor, size, pos, shapeOutline, shapeBorderRadius, alpha, fill)
        self.backgroundColor = backgroundColor
        self.length = length
        self.amount = amount
        self.spacing = spacing
        self.fullSize = ((self.width * self.length) + (self.spacing * self.length), self.height)


    def getAmount(self):
        return self.amount


    def getFullSize(self):
        return self.fullSize


    def setAmount(self, amount):
        self.amount = amount


    def __render(self):
        self.dirty = False

        pos = vec(self.x, self.y) * self.menu.renderer.getScale()
        size = vec(self.width, self.height) * self.menu.renderer.getScale()
        self.rect = pygame.Rect(pos, size)
        self.outline = self.shapeOutline * self.menu.renderer.getScale()
        self.borderRadius = [i * self.menu.renderer.getScale() for i in self.shapeBorderRadius]
        self.gap = self.spacing * self.menu.renderer.getScale()

        self.fullsize = copy.copy(size)
        self.fullsize[0] = (size[0] * self.length) + (self.gap * self.length)

        self.image = pygame.Surface(self.fullsize).convert()
        if self.alpha is not None: self.image.set_alpha(self.alpha, pygame.RLEACCEL)
        if self.fill is not None: self.drawShape(self.image, self.fill, Rect(0, 0, *size), 0)
        self.drawShape(self.image, self.color, Rect(0, 0, *size), self.outline)


    def drawShape(self, surface, color = None, rect = None, outline = None):
        rect = self.rect if rect is None else rect
        offx = rect.x
        remaining = self.length - self.amount

        for x in range(self.amount):
            newRect = Rect(offx, rect.y, rect.width, rect.height)
            super().drawShape(surface, color, newRect, outline)
            offx += rect.width + self.gap

        for i in range(remaining):
            newRect = Rect(offx, rect.y, rect.width, rect.height)
            super().drawShape(surface, self.backgroundColor, newRect, outline)
            offx += rect.width + self.gap


    def makeSurface(self):
        if self.dirty or self.rect is None: self.__render()


class Ellipse(Shape):
    def __init__(self, menu, color, size = tuple(), pos = tuple(), shapeOutline = 0, alpha = None, fill = None):
        super().__init__(menu, color, size, pos, shapeOutline, alpha = alpha, fill = fill)   


    def drawShape(self, surface, color = None, rect = None, outline = None):
        color, rect, outline = self.getShapeComponents(color, rect, outline)
        pygame.draw.ellipse(surface, color, rect, int(outline))


class Arc(Shape):
    def __init__(self, menu, color, startAngle, stopAngle, size = tuple(), pos = tuple(), shapeOutline = 0, alpha = None, fill = None):
        super().__init__(menu, color, size, pos, shapeOutline, alpha = alpha, fill = fill) 
        self.startAngle = startAngle
        self.stopAngle = stopAngle

    
    def setStartAngle(self, startAngle):
        self.startAngle = startAngle


    def setStopAngle(self, stopAngle):
        self.stopAngle = stopAngle


    def drawShape(self, surface, color = None, rect = None, outline = None):
        color, rect, outline = self.getShapeComponents(color, rect, outline)
        pygame.draw.arc(surface, color, rect, self.startAngle, self.stopAngle, int(outline))


class Timer(Arc):
    def __init__(self, menu, backgroundColor, foregoundColor, timer, step, size = tuple(), pos = tuple(), shapeOutline = 0, alpha = None, fill = None):
        super().__init__(menu, foregoundColor, 0, 0, size, pos, shapeOutline, alpha, fill)
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

        pos = vec(self.x, self.y) * self.menu.renderer.getScale()
        size = vec(self.width, self.height) * self.menu.renderer.getScale()
        self.rect = pygame.Rect(pos, size)
        self.outline = self.shapeOutline * self.menu.renderer.getScale()

        self.image = pygame.Surface(size, pygame.SRCALPHA, 32).convert_alpha()
        # self.image.fill(BLACK)
        # self.image.set_alpha(255, pygame.RLEACCEL)
        self.drawShape(self.image, self.color, Rect(0, 0, *size), self.outline)


    def drawShape(self, surface, color = None, rect = None, outline = None):
        color, rect, outline = self.getShapeComponents(color, rect, outline)
        offx = 0.01

        # inside circle
        pygame.draw.ellipse(surface, self.backgroundColor, rect, int(outline - 1)) 

        # outside timer
        for x in range(6):
            pygame.draw.arc(surface, color, rect, self.startAngle + offx, self.stopAngle, int(outline))
            offx += 0.01


    def makeSurface(self):
        if self.dirty or self.rect is None: self.__render()


class MessageBox(Rectangle):
    def __init__(self, menu, message, margin = tuple()):   
        super().__init__(menu, GREEN, (0, 0), (0, 0), 0, [10, 10, 10, 10])
        self.messages = []
        self.marginX = margin[0]
        self.marginY = margin[1]
        self.message = message
        self.offset = vec(10, 10)

        self.addLabels(message)


    def setPos(self, pos = tuple()):
        self.x = pos[0]
        self.y = pos[1]
        for message in self.messages:
            width = message.getFontSize()[0]
            message.setPos(((pos[0] + self.width) - (width + self.offset.x), (pos[1] + self.offset.y) + message.offset.y))


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
            m = Label(self.menu, msg, 25, Color("white"), (0, 0)) # first we siet the x and y to 0 since we don't know the width yet
            width, height = m.getFontSize()
            m.setOffset(vec(0, totalHeight))
            totalHeight += height

            if width > biggestWidth:
                biggestWidth = width

            self.messages.append(m)

        self.setSize((biggestWidth + (self.offset.x * 2), totalHeight + (self.offset.y * 2)))
        # pos: 
        #   x = displaywidth - (width of the biggest message + width of the margin + width of the offset * 2 (for both sides)
        #   y = 0 - the total height of the message box + height of the offset * 2 (for both sides)
        self.setPos((config["graphics"]["displayWidth"] - (biggestWidth + self.marginX + (self.offset.x * 2)) , 0 - (totalHeight + (self.offset.y * 2))))


    def remove(self):
        self.menu.components.remove(self)
        self.menu.removeMessage(self.message)
        for message in self.messages:
            self.menu.components.remove(message)

        del self


    def drawPaused(self, surface):
        self.makeSurface()
        self.drawShape(surface)


    def draw(self):
        self.makeSurface()
        self.menu.renderer.addSurface(None, None, self.drawShape)
        # self.menu.renderer.addSurface(self.image, (self.rect))


        self.timer += self.menu.game.dt

        if self.timer > 4:
            self.addAnimation(transitionMessageRight, 'onLoad', speed = 18, x = config["graphics"]["displayWidth"])
            # self.menu.components.remove(self)
            # for message in self.messages:
            #     self.menu.components.remove(message)


class Map(MenuComponent):
    def __init__(self, menu, level, levelInt, size = tuple(), pos = tuple()):  
        super().__init__(menu, TRUEBLACK, size, pos)
        self.levelName = level
        self.level = menu.game.mapLoader.getMap(self.levelName)
        self.levelInt = levelInt
        self.levelData = menu.game.mapLoader.getMapData(self.levelName)


    def getLevel(self):
        return self.level


    def getLevelInt(self):
        return self.levelInt


    def getLevelData(self):
        return self.levelData


    # draw scanlines if enabled
    def drawScanlines(self):    
        if config["graphics"]["scanlines"]["enabled"]:
            scanlines = pygame.Surface((int(self.width * self.menu.renderer.getScale()), int(self.height * self.menu.renderer.getScale())))
            
            fillColor = BLACK if self.levelData["locked"]["isLocked"] else SCANLINES
            scanlines.fill(fillColor)

            self.menu.renderer.drawScanlines(scanlines)
            alpha = 95 if self.levelData["locked"]["isLocked"] else config["graphics"]["scanlines"]["opacity"]
            scanlines.set_alpha(alpha)

            self.image.blit(scanlines, (0, 0))


    # show that the level is locked
    def drawLocked(self):
        if self.levelData["locked"]["isLocked"]:
            locked = Image(self.menu, "locked", (100, 100), (self.width / 2 - 50, self.height / 2- 50))
            key = Image(self.menu, "keyGreen", (30, 30), (self.width / 2 - 80, self.height - 50))
            unlock = Label(self.menu, str(self.levelData["locked"]["unlock"]), 20, RED, (key.x + key.width + 10, key.y + (key.height / 2) - 8))
            keyText = Label(self.menu, "to unlock", 20, GREEN, (unlock.x + unlock.getFontSize()[0] + 5, unlock.y))

            locked.makeSurface()
            key.makeSurface()
            unlock.makeSurface()
            keyText.makeSurface()
            self.image.blit(locked.image, (locked.rect))
            self.image.blit(key.image, (key.rect))
            self.image.blit(unlock.image, (unlock.rect))
            self.image.blit(keyText.image, (keyText.rect))

            # draw the overlay when the scanlines aren't enabled
            if not config["graphics"]["scanlines"]["enabled"]:
                overlay = pygame.Surface((int(self.width * self.menu.renderer.getScale()), int(self.height * self.menu.renderer.getScale())))
                overlay.fill(BLACK)
                overlay.set_alpha(95)
                self.image.blit(overlay, (0, 0))


    # make rounded corners
    def roundedCorners(self):
        size = self.image.get_size()
        rectImage = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(rectImage, Color("white"), (0, 0, *size), border_radius = int(50 * self.menu.renderer.getScale()))
        self.image.blit(rectImage, (0, 0), None, pygame.BLEND_RGBA_MIN)

        pygame.draw.rect(self.image, self.color, (0, 0, *size), width = int(10 * self.menu.renderer.getScale()), border_radius = int(30 * self.menu.renderer.getScale()))


    def drawDifficulty(self):
        textColor = BLACK
        
        # can't use sprite renderer dark mode since it wont be different for every map
        if "backgrounds" in self.levelData and "darkMode" in self.levelData["backgrounds"] and self.levelData["backgrounds"]["darkMode"]:
            textColor = Color("white")

        difficultyText = Label(self.menu, "Difficulty", 15, textColor, (30, self.height - 60))
        difficultyText.makeSurface()
        self.image.blit(difficultyText.image, (difficultyText.rect))

        difficulty = DifficultyMeter(self.menu, RED, BLACK, 4, self.levelData["difficulty"], 2, (15, 15), (30, difficultyText.y + (difficultyText.getFontSizeScaled()[1] / self.menu.renderer.getScale() + 5)))
        difficulty.drawPaused(self.image)


    def __render(self):
        self.dirty = False
        self.finalImage = pygame.Surface((self.width * self.menu.renderer.getScale(), self.height * self.menu.renderer.getScale())).convert()
        self.image = self.menu.game.spriteRenderer.createLevelSurface(self.level).convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (int(self.width * self.menu.renderer.getScale()), 
                                                                int(self.height * self.menu.renderer.getScale()))).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = self.x * self.menu.renderer.getScale()
        self.rect.y = self.y * self.menu.renderer.getScale()

        # add labels
        self.mapTitle = Label(self.menu, self.levelName, 30, GREEN, (30, 25))
        self.mapTitle.makeSurface()
        self.image.blit(self.mapTitle.image, (self.mapTitle.rect))

        self.drawDifficulty()
        self.drawLocked()
        self.drawScanlines()
        self.roundedCorners()

        self.finalImage.fill(self.menu.getBackgroundColor())
        self.finalImage.blit(self.image, (0, 0))

    
    def makeSurface(self):
        if self.dirty or self.image is None: self.__render()


class Image(MenuComponent):
    def __init__(self, menu, imageName, size = tuple(), pos = tuple(), alpha = None):
        super().__init__(menu, None, size, pos)
        self.imageName = imageName
        self.alpha = alpha


    def getImageName(self):
        return self.imageName


    def getAlpha(self):
        return self.alpha if self.alpha is not None else 0


    def setImageName(self, imageName):
        self.imageName = imageName


    def setAlpha(self, alpha):
        self.alpha = alpha
        

    def __render(self):
        self.dirty = False
        self.image = self.menu.game.imageLoader.getImage(self.imageName, (self.width, self.height))
        self.rect = self.image.get_rect()
        self.rect.x = self.x * self.menu.renderer.getScale()
        self.rect.y = self.y * self.menu.renderer.getScale()
        if self.alpha is not None: self.image.set_alpha(self.alpha, pygame.RLEACCEL)
        self.addComponents()


    def makeSurface(self):
        if self.dirty or self.image is None: self.__render()
