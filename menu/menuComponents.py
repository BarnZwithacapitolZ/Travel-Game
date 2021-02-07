import pygame 
from pygame.locals import *
from config import *
from transitionFunctions import transitionMessageRight
import string

vec = pygame.math.Vector2


class TextHandler:
    def __init__(self):
        self.text = ""
        self.active = False
        self.lengthReached = False
        self.pressed = False
        
        self.keys = list(string.ascii_letters) + list(string.digits)
        self.keys.append(" ")

    def getText(self):
        return self.text

    def getActive(self):
        return self.active

    def getPressed(self):
        return self.pressed

    def getLengthReached(self):
        return self.lengthReached

    def setPressed(self, pressed):
        self.pressed = pressed

    def setText(self, text):
        self.text = text#

    def setLengthReached(self, lengthReached):
        self.lengthReached = lengthReached

    # When active clear the text so its ready for input
    def setActive(self, active):
        self.active = active

        if self.active:
            self.text = ""

    def events(self, event):
        if self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if event.unicode in self.keys and not self.lengthReached:
                    self.text += event.unicode


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


        self.events = {}
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
        # self.events.append((function, event))
        self.events[function] = (event, kwargs)

    def addAnimation(self, function, event, **kwargs):
        self.animations[function] = (event, kwargs)

    def removeAnimation(self, function):
        del self.animations[function]

    def getAnimations(self):
        return self.animations

    def getOffset(self):
        return self.offset




class Label(MenuComponent):
    def __init__(self, menu, text, fontSize, color, pos = tuple()):
        super().__init__(menu, color, (1, 1), pos)

        self.text = text
        self.fontName = pygame.font.get_default_font()
        # self.fontName = os.path.join(FONTFOLDER, config["fonts"]["openSans"])
        self.fontSize = fontSize
        self.bold = False
        self.italic = False
        self.underline = False
        
    def setFontSize(self, fontSize):
        self.fontSize = fontSize

    def getFontSize(self):
        # we don't want to use self.font since this is multiplied by the display size, which we don't want
        return pygame.font.Font(self.fontName, self.fontSize).size(self.text)

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

        self.image = self.font.render(self.text, config["graphics"]["antiAliasing"], self.color)

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
    def __init__(self, menu, fontSize, color, pos = tuple(), maxLength = 40):
        super().__init__(menu, "", fontSize, color, pos)
        self.menu.game.textHandler.setText("")
        self.maxLength = maxLength

        self.flashing = True
        self.timer = 0
        self.indicator = Shape(self.menu, self.color, (3, fontSize), self.pos)


    def setText(self):        
        if len(self.menu.game.textHandler.getText()) < self.maxLength:
            self.menu.game.textHandler.setLengthReached(False)
        else:
            self.menu.game.textHandler.setLengthReached(True)

        if self.text != self.menu.game.textHandler.getText():
            self.text = self.menu.game.textHandler.getText()
            self.dirty = True


    def setFlashing(self):
        if hasattr(self.indicator, 'rect'):
            self.indicator.x = self.x + self.width
            self.indicator.rect.x = self.indicator.x * self.menu.renderer.getScale()

            self.timer += 60 * self.menu.game.dt

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


class Shape(MenuComponent):
    def __init__(self, menu, color, size = tuple(), pos = tuple(), shapeType = "rect", shapeOutline = 0, shapeBorderRadius = [0, 0, 0, 0], alpha = None):   
        super().__init__(menu, color, size, pos)
        self.shapeType = shapeType
        self.shapeOutline = shapeOutline
        self.shapeBorderRadius = shapeBorderRadius
        self.alpha = alpha

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
                                                            int(self.height * self.menu.renderer.getScale())))
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

        self.image = self.menu.game.imageLoader.getImage(self.imageName)
        self.image = pygame.transform.smoothscale(self.image, (int(self.width * self.menu.renderer.getScale()), 
                                                            int(self.height * self.menu.renderer.getScale())))
        self.rect = self.image.get_rect()
        self.rect.x = self.x * self.menu.renderer.getScale()
        self.rect.y = self.y * self.menu.renderer.getScale()
        if self.alpha is not None: self.image.set_alpha(self.alpha, pygame.RLEACCEL)


    def draw(self):
        if self.dirty or self.image is None: self.__render()
        self.menu.renderer.addSurface(self.image, (self.rect))
