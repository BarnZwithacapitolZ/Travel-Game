import pygame 
from pygame.locals import *
from config import *

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
        self.type = ""

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
        # self.fontName = config["fonts"]["joystix"]
        self.fontSize = fontSize
        self.bold = False
        self.italic = False
        self.underline = False
        self.type = "text"

        self.setFont(self.menu.renderer.getHeight())

    def setFont(self, height):
        self.font = pygame.font.Font(self.fontName, int(self.fontSize * height / config["graphics"]["displayHeight"]))

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

        self.font.set_bold(self.bold)
        self.font.set_italic(self.italic)
        self.font.set_underline(self.underline)

        self.image = self.font.render(self.text, config["graphics"]["antiAliasing"], self.color)
        self.rect = self.image.get_rect()

        self.rect.x = self.x * self.menu.renderer.getScale()
        self.rect.y = self.y * self.menu.renderer.getScale()
        

    def draw(self):
        if self.dirty or self.image is None: self.__render()
        self.menu.renderer.addSurface(self.image, self.rect)



class Shape(MenuComponent):
    def __init__(self, menu, color, size = tuple(), pos = tuple(), alpha = None):   
        super().__init__(menu, color, size, pos)
        self.type = "button"
        self.alpha = alpha

        self.image = pygame.Surface((self.size)).convert()
        self.image.fill(self.color)
        if self.alpha is not None: self.image.set_alpha(self.alpha, pygame.RLEACCEL)
        self.rect = self.image.get_rect()

        self.__render()
        

    def __render(self):
        self.dirty = False

        self.rect.x = self.x * self.menu.renderer.getScale()
        self.rect.y = self.y * self.menu.renderer.getScale()
        
        self.image = pygame.transform.scale(self.image, (int(self.width * self.menu.renderer.getScale()), 
                                                            int(self.height * self.menu.renderer.getScale())))

    def draw(self):
        if self.dirty or self.image is None: self.__render()
        self.menu.renderer.addSurface(self.image, (self.rect))


class Image(MenuComponent):
    def __init__(self, menu, imageName, color, size = tuple(), pos = tuple(), alpha = None):
        super().__init__(menu, color, size, pos)
        self.type = "image"
        self.imageName = imageName
        self.alpha = alpha

        self.dirty = True

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
