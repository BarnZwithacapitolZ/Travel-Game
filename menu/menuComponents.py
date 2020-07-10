import pygame 
from pygame.locals import *
from config import *
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

        self.events = []
        self.animations = []

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

    def addEvent(self, function, event):
        self.events.append((function, event))

    def addAnimation(self, function, event):
        self.animations.append((function, event))



class Label(MenuComponent):
    def __init__(self, menu, text, fontSize, color, pos = tuple()):
        super().__init__(menu, color, (1, 1), pos)

        self.text = text
        self.fontName = pygame.font.get_default_font()
        # self.fontName = os.path.join(FONTFOLDER, config["fonts"]["joystix"])
        self.fontSize = fontSize
        self.bold = False
        self.italic = False
        self.underline = False


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

            self.timer += 1

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
    def __init__(self, menu, color, size = tuple(), pos = tuple(), shapeType = "rect", shapeOutline = 0):   
        super().__init__(menu, color, size, pos)
        self.shapeType = shapeType
        self.shapeOutline = shapeOutline

    def getShapeType(self):
        return self.shapeType


    def getShapeOutline(self):
        return self.shapeOutline

    
    def setShapeType(self, shapeType):
        self.shapeType = shapeType


    def setShapeOutline(self, shapeOutline):
        self.shapeOutline = shapeOutline


    def __render(self):
        self.dirty = False

        pos = vec(self.x, self.y) * self.menu.renderer.getScale()
        size = vec(self.width, self.height) * self.menu.renderer.getScale()
        self.rect = pygame.Rect(pos, size)
        self.outline = self.shapeOutline * self.menu.renderer.getScale()

    def drawShape(self):
        if self.shapeType == "rect":
            pygame.draw.rect(self.menu.renderer.gameDisplay, self.color, self.rect, int(self.outline))
        elif self.shapeType == "ellipse":
            # pygame.draw.ellipse(self.game.renderer.gameDisplay, YELLOW, rect, int(7 * scale))
            pygame.draw.ellipse(self.menu.renderer.gameDisplay, self.color, self.rect, int(self.outline))


    def draw(self):
        if self.dirty or self.rect is None: self.__render()
        self.menu.renderer.addSurface(None, None, self.drawShape)



class Image(MenuComponent):
    def __init__(self, menu, imageName, color, size = tuple(), pos = tuple(), alpha = None):
        super().__init__(menu, color, size, pos)
        self.imageName = imageName
        self.alpha = alpha


    def setImageName(self, imageName):
        self.imageName = imageName
        

    def __render(self):
        self.dirty = False

        self.image = self.menu.game.imageLoader.getImage(self.imageName)
        self.image = pygame.transform.smoothscale(self.image, (int(self.width * self.menu.renderer.getScale()), 
                                                            int(self.height * self.menu.renderer.getScale())))
        self.rect = self.image.get_rect()
        self.rect.x = self.x * self.menu.renderer.getScale()
        self.rect.y = self.y * self.menu.renderer.getScale()

    def draw(self):
        if self.dirty or self.image is None: self.__render()
        self.menu.renderer.addSurface(self.image, (self.rect))
