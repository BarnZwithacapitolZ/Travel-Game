import pygame
from pygame.locals import *
from config import *
import os

vec = pygame.math.Vector2

class Renderer:
    def __init__(self, game):
        self.game = game
        self.width = config["graphics"]["displayWidth"]
        self.height = config["graphics"]["displayHeight"]
        self.windowWidth = config["graphics"]["displayWidth"]
        self.windowHeight = config["graphics"]["displayHeight"]

        # we can use these variables to set the resolution on fullscreen
        self.monitorWidth = pygame.display.Info().current_w
        self.monitorHeight = pygame.display.Info().current_h

        # self.monitorWidth = 1280
        # self.monitorHeight = 720

        self.screen = pygame.display.set_mode((self.windowWidth, self.windowHeight), pygame.RESIZABLE | pygame.DOUBLEBUF)
        self.gameDisplay = pygame.Surface((self.width, self.height))

        self.scale = 1 # control the scale of whats on screen
        self.fixedScale = 1 # used to control the fixed scale, i.e to make things bigger on screen seperate from screen size
        self.surfaces = []
        self.dirtySurfaces = []

        self.fpsFont = pygame.font.Font(pygame.font.get_default_font(), 30)
        self.fontImage = self.fpsFont.render(str(int(self.game.clock.get_fps())), False, RED)



    # Prepare the gamedisplay for blitting to, this means overriding it with a new color
    def prepareSurface(self, color):
        # self.gameDisplay.fill(color)
        pygame.draw.rect(self.gameDisplay, color, (0, 0, config["graphics"]["displayWidth"] * self.scale, config["graphics"]["displayHeight"] * self.scale))
        self.dirtySurfaces.append(self.gameDisplay.get_rect())


    # Add a surface to the gameDisplay
    def addSurface(self, surface, rect, method = None):
        self.surfaces.append((surface, rect, method))


    def addDirtySurface(self, surface):
        self.dirtySurfaces.append(surface)


    def setWidth(self, width):
        self.width = width


    def setHeight(self, height):
        self.height = height


    def setFixedScale(self, fixedScale):
        self.fixedScale = fixedScale


    def getScale(self):
        return self.scale


    def getFixedScale(self):
        return self.fixedScale


    def getDifference(self):
        difx = (self.windowWidth - self.width) / 2
        dify = (self.windowHeight - self.height) / 2
        return (difx, dify)


    def getHeight(self):
        return self.height


    def setFullscreen(self):
        self.setScale((self.monitorWidth, self.monitorHeight), True)


    def unsetFullscreen(self):
        self.setScale((config["graphics"]["displayWidth"], config["graphics"]["displayHeight"]))


    def setScale(self, size, fullscreen = False):
        size = list(size)
        if size[0] < config["graphics"]["minDisplayWidth"]: size[0] = config["graphics"]["minDisplayWidth"]
        if size[1] < config["graphics"]['minDisplayHeight']: size[1] = config["graphics"]["minDisplayHeight"]

        self.scale = round(min(size[1] / config["graphics"]["displayHeight"], size[0] / config["graphics"]["displayWidth"]), 1) * self.fixedScale

        self.width = (config["graphics"]["displayWidth"] * self.scale)
        self.height = (config["graphics"]["displayHeight"] * self.scale)
        self.windowWidth = size[0]
        self.windowHeight = size[1]

        # print((self.width, self.height), (self.windowWidth, self.windowHeight))

        if fullscreen:
            self.screen = pygame.display.set_mode((int(self.windowWidth), int(self.windowHeight)), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
        else:
            self.screen = pygame.display.set_mode((int(self.windowWidth), int(self.windowHeight)), pygame.RESIZABLE | pygame.DOUBLEBUF)

        self.gameDisplay = pygame.Surface((self.width, self.height))

        self.game.spriteRenderer.resize()
        self.game.mapEditor.resize()
        self.game.optionMenu.resize()
        self.game.mainMenu.resize()       


    # on tick function
    def render(self):
        for surface in self.surfaces:
            if surface[2]:
                surface[2](self.gameDisplay)
            else:
                self.gameDisplay.blit(surface[0], surface[1])

        self.gameDisplay.blit(self.fontImage, (950, 10))

        self.screen.blit(self.gameDisplay, (0 + self.getDifference()[0], 0 + self.getDifference()[1]))
        # self.screen.blit(pygame.transform.scale(self.gameDisplay, (int(self.windowWidth), int(self.windowHeight))), (0, 0))

        # pygame.display.update(self.dirtySurfaces) #self.screen.get_rect() ?
        pygame.display.update()

        self.surfaces = []
        self.dirtySurfaces = []

        self.fontImage = self.fpsFont.render(str(int(self.game.clock.get_fps())), False, RED)


class ImageLoader:
    def __init__(self):
        self.images = {}

        self.loadAllImages()

    def loadAllImages(self):
        for key, data in config["images"].items():
            if data["alpha"]:
                i = pygame.image.load(os.path.join(ASSETSFOLDER, data["image"])).convert_alpha()
            else:
                i = pygame.image.load(os.path.join(ASSETSFOLDER, data["image"])).convert()
                # i.set_colorkey()

            self.images[key] = i

    def getImage(self, key):
        return self.images[key]

    @staticmethod
    def changeImageColor(image, newColor, oldColor = None):
        for x in range(image.get_width()):
            for y in range(image.get_height()):
                pixel = image.get_at((x, y))
                if pixel == oldColor or oldColor is None:
                    newColor.a = pixel.a
                    image.set_at((x, y), newColor)



class AudioLoader:
    def __init__(self):
        # pygame.mixer.set_num_channels(5)

        self.sounds = {}
        self.music = {}

        self.loadAllSounds()


    def getSound(self, key):
        return self.sounds[key]


    def playSound(self, key):
        self.sounds[key].play()


    def setChannels(self):
        return


    def loadAllSounds(self):
        for key, audio in config["audio"]["sounds"].items():
            a = pygame.mixer.Sound(os.path.join(AUDIOFOLDER, audio["file"]))
            a.set_volume(audio["volume"])
            self.sounds[key] = a


class MapLoader:
    def __init__(self):
        self.maps = {}

        self.loadAllMaps()


    def getMaps(self):
        return self.maps


    def getMap(self, key):
        return self.maps[key]


    def getLongestMapLength(self):
        longest = 0
        for mapName in self.maps:
            if len(mapName) > longest:
                longest = len(mapName)
        return longest


    def addMap(self, mapName, path):
        self.maps[mapName] = path


    def removeMap(self, mapName):
        del self.maps[mapName]


    def loadAllMaps(self):
        for key, level in config["maps"].items():
            m = os.path.join(MAPSFOLDER, level)
            self.maps[key] = m


    def checkMapExists(self, mapName):
        if mapName in self.maps:
            return True
        return False


