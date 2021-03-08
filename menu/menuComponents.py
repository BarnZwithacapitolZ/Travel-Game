import pygame 
from pygame.locals import *
from config import *
from transitionFunctions import transitionMessageRight
import string

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
    def __init__(self, menu, color, size = tuple(), pos = tuple()):
        self.menu = menu
        self.color = color
        self.width = size[0]
        self.height = size[1]
        self.x = pos[0]
        self.y = pos[1]
        self.size = size
        self.pos = pos
        self.offset = vec(0, 0)


        self.events = []
        self.animations = {}

        self.dirty = True
        self.responsive = True

        self.mouseOver = False

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

    def addEvent(self, function, event, **kwargs):
        self.events.append({
            'function': function,
            'event': event,
            'kwargs': kwargs
        })

    def addAnimation(self, function, event, **kwargs):
        self.animations[function] = (event, kwargs)

    def removeAnimation(self, function):
        del self.animations[function]

    def removeEvent(self, event):
        if event in self.events:
            self.events.remove(event)

    def getAnimations(self):
        return self.animations

    def getOffset(self):
        return self.offset


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
        return pygame.font.Font(self.fontName, self.fontSize).size(text)

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

    def render(self):
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
        

    def draw(self):
        if self.dirty or self.image is None: self.render()
        self.menu.renderer.addSurface(self.image, self.rect)


class InputBox(Label):
    def __init__(self, menu, fontSize, color, background, width, pos = tuple()):
        super().__init__(menu, "", fontSize, color, pos)
        self.menu.game.textHandler.setString([])
        self.menu.game.textHandler.setPointer(0)
        self.inputWidth = width # max length of text input 

        self.flashing = True
        self.timer = 0
        self.background = background
        self.indicator = Shape(self.menu, self.color, (3, fontSize), self.pos)

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

    
    def draw(self):
        if self.dirty or self.image is None: self.render()
        self.menu.renderer.addSurface(self.image, self.rect)

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
    def __init__(self, menu, color, size = tuple(), pos = tuple(), shapeType = "rect", shapeOutline = 0, shapeBorderRadius = [0, 0, 0, 0], alpha = None):   
        super().__init__(menu, color, size, pos)
        self.shapeType = shapeType
        self.shapeOutline = shapeOutline        
        self.shapeBorderRadius = shapeBorderRadius
        self.alpha = alpha

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

    def render(self):
        self.dirty = False

        pos = vec(self.x, self.y) * self.menu.renderer.getScale()
        size = vec(self.width, self.height) * self.menu.renderer.getScale()
        self.rect = pygame.Rect(pos, size)
        self.outline = self.shapeOutline * self.menu.renderer.getScale()
        self.borderRadius = [i * self.menu.renderer.getScale() for i in self.shapeBorderRadius]

        if self.alpha is not None:
            self.image = pygame.Surface((self.size)).convert()
            self.image = pygame.transform.scale(self.image, (int(self.width * self.menu.renderer.getScale()), 
                                                            int(self.height * self.menu.renderer.getScale()))).convert()
            self.image.set_alpha(self.alpha, pygame.RLEACCEL)
            self.drawShape(self.image)

            
    def drawShape(self, surface):
        if self.shapeType == "rect":
            pygame.draw.rect(surface, self.color, self.rect, int(self.outline), 
                border_top_left_radius = int(self.borderRadius[0]),
                border_top_right_radius  = int(self.borderRadius[1]),
                border_bottom_left_radius = int(self.borderRadius[2]),
                border_bottom_right_radius = int(self.borderRadius[3]))
        elif self.shapeType == "ellipse":
            # pygame.draw.ellipse(self.game.renderer.gameDisplay, YELLOW, rect, int(7 * scale))
            pygame.draw.ellipse(surface, self.color, self.rect, int(self.outline))


    def draw(self):
        if self.dirty or self.rect is None: self.render()
        if self.alpha is not None:
            self.menu.renderer.addSurface(self.image, (self.rect))
        else:
            self.menu.renderer.addSurface(None, None, self.drawShape)


class MessageBox(Shape):
    def __init__(self, menu, message, margin = tuple()):   
        super().__init__(menu, GREEN, (0, 0), (0, 0), 'rect', 0, [10, 10, 10, 10])
        self.timer = 0
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


    def draw(self):
        if self.dirty or self.rect is None: self.render()
        self.menu.renderer.addSurface(None, None, self.drawShape)

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


    def __render(self):
        self.dirty = False
        self.image = self.menu.game.spriteRenderer.createLevelSurface(self.level).convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (int(self.width * self.menu.renderer.getScale()), 
                                                                int(self.height * self.menu.renderer.getScale()))).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = self.x * self.menu.renderer.getScale()
        self.rect.y = self.y * self.menu.renderer.getScale()

        # add labels
        # self.mapTitle = Label(self.menu, self.levelName, 30, BLACK, (50, 50))
        # self.mapTitle.render()
        # self.image.blit(self.mapTitle.image, (self.mapTitle.rect))

        # draw scanlines if enabled
        if config["graphics"]["scanlines"]["enabled"]:
            self.scanlines = pygame.Surface((int(self.width * self.menu.renderer.getScale()), int(self.height * self.menu.renderer.getScale())))
            self.scanlines.fill(SCANLINES)
            self.menu.renderer.drawScanlines(self.scanlines)
            self.scanlines.set_alpha(config["graphics"]["scanlines"]["opacity"])
            self.image.blit(self.scanlines, (0, 0))


        # make rounded corners
        size = self.image.get_size()
        self.rectImage = pygame.Surface(size, pygame.SRCALPHA)
        # self.rectImage.fill(self.menu.getBackgroundColor())
        pygame.draw.rect(self.rectImage, Color("white"), (0, 0, *size), border_radius = int(50 * self.menu.renderer.getScale()))
        self.image.blit(self.rectImage, (0, 0), None, pygame.BLEND_RGBA_MIN)
        pygame.draw.rect(self.image, self.color, (0, 0, *size), width = int(30 * self.menu.renderer.getScale()), border_radius = int(50 * self.menu.renderer.getScale()))


    def draw(self):
        if self.dirty or self.image is None: self.__render()
        self.menu.renderer.addSurface(self.image, (self.rect))


class Image(MenuComponent):
    def __init__(self, menu, imageName, color, size = tuple(), pos = tuple(), alpha = None):
        super().__init__(menu, color, size, pos)
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


    def draw(self):
        if self.dirty or self.image is None: self.__render()
        self.menu.renderer.addSurface(self.image, (self.rect))
