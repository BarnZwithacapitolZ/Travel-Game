import pygame
import pygame._sdl2
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

        self.screen = pygame.display.set_mode((self.windowWidth, self.windowHeight), pygame.RESIZABLE | pygame.DOUBLEBUF, vsync = 1)
        self.gameDisplay = pygame.Surface((self.width, self.height))

        self.scale = 1 # control the scale of whats on screen
        self.fixedScale = 1 # used to control the fixed scale, i.e to make things bigger on screen seperate from screen size
        self.diff = vec(0, 0)
        self.offset = vec(0, 0)
        self.surfaces = []
        self.dirtySurfaces = []

        self.fpsFont = pygame.font.Font(pygame.font.get_default_font(), 30)
        self.fontImage = self.fpsFont.render(str(int(self.game.clock.get_fps())), False, RED)
        self.createScanlines()


    # Prepare the gamedisplay for blitting to, this means overriding it with a new color
    def prepareSurface(self, color):
        self.gameDisplay.fill(color)
        # pygame.draw.rect(self.gameDisplay, color, (0, 0, config["graphics"]["displayWidth"] * self.scale, config["graphics"]["displayHeight"] * self.scale))
        # self.dirtySurfaces.append(self.gameDisplay.get_rect())
    

    def drawScanlines(self, surface):
        # step = int(2 * self.scale) if int(2 * self.scale) >= 2 else 2
        step = 5
        for i in range(0, int(self.height), step):
            pos1 = (0, i)
            pos2 = (int(self.width), i)
            pygame.draw.line(surface, (0, 0, 0, 60), pos1, pos2, 1)
            

    def createScanlines(self):
        self.scanlines = pygame.Surface((self.width, self.height)).convert()
        self.scanlines.fill(SCANLINES)
        self.drawScanlines(self.scanlines)
        self.scanlines.set_alpha(config["graphics"]["scanlines"]["opacity"])


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
        return self.diff


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

        self.scale = min(size[1] / config["graphics"]["displayHeight"], size[0] / config["graphics"]["displayWidth"]) * self.fixedScale

        self.width = (config["graphics"]["displayWidth"] * self.scale)
        self.height = (config["graphics"]["displayHeight"] * self.scale)
        self.windowWidth = size[0]
        self.windowHeight = size[1]
        self.diff.x = (self.windowWidth - self.width) / 2
        self.diff.y = (self.windowHeight - self.height) / 2

        if fullscreen:
            self.screen = pygame.display.set_mode((int(self.windowWidth), int(self.windowHeight)), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF, vsync = 1)
        else:
            self.screen = pygame.display.set_mode((int(self.windowWidth), int(self.windowHeight)), pygame.RESIZABLE | pygame.DOUBLEBUF, vsync = 1)

        self.gameDisplay = pygame.Surface((self.width, self.height)) #.convert()

        self.game.spriteRenderer.resize()
        self.game.mapEditor.resize()
        self.game.optionMenu.resize()
        self.game.mainMenu.resize()       
        self.createScanlines()


    # on tick function
    def render(self):
        for surface in self.surfaces:
            if surface[2]:
                surface[2](self.gameDisplay)
            else:
                self.gameDisplay.blit(surface[0], surface[1])

        self.gameDisplay.blit(self.fontImage, (950, 10))

        if not self.game.mainMenu.levelSelectOpen:
            if config["graphics"]["scanlines"]["enabled"]: 
                self.gameDisplay.blit(self.scanlines, (0, 0))
            pygame.draw.rect(self.gameDisplay, TRUEBLACK, (-30 * self.scale, -30 * self.scale, (config["graphics"]["displayWidth"] + 60) * self.scale, (config["graphics"]["displayHeight"] + 60) * self.scale), int(30 * self.scale), border_radius = int(80 * self.scale))
            

        self.screen.blit(self.gameDisplay, (0 + self.getDifference()[0], 0 + self.getDifference()[1]))
        # self.screen.blit(pygame.transform.smoothscale(self.gameDisplay, (int(self.width), int(self.height))), (0, 0))

        # pygame.display.update(self.dirtySurfaces) #self.screen.get_rect() ?
        pygame.display.update()

        self.surfaces = []
        self.dirtySurfaces = []

        self.fontImage = self.fpsFont.render(str(int(self.game.clock.get_fps())), False, RED)


class ImageLoader:
    def __init__(self, game):
        self.game = game
        self.images = {}
        self.loadAllImages()

    def loadAllImages(self):
        for key, data in config["images"].items():
            i = pygame.image.load(os.path.join(ASSETSFOLDER, data["image"]))
            i = i.convert_alpha() if data["alpha"] else i.convert()

            self.images[key] = {
                "image": i,
                "data": data
            }

    def getImage(self, key, scale = tuple()):
        image = self.images[key]["image"]
        data = self.images[key]["data"]

        if scale: # if there is a scale
            if config["graphics"]["smoothscale"]:
                image = pygame.transform.smoothscale(image, (int(scale[0] * self.game.renderer.getScale()),
                                                            int(scale[1] * self.game.renderer.getScale())))
            else:
                image = pygame.transform.scale(image, (int(scale[0] * self.game.renderer.getScale()),
                                                            int(scale[1] * self.game.renderer.getScale())))
            image = image.convert_alpha() if data["alpha"] else image.convert()

        return image


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
        pygame.mixer.set_num_channels(3)

        self.sounds = {}
        self.music = {}

        self.setChannels()
        self.loadAllSounds()


    def getSound(self, key):
        return self.sounds[key]


    def playSound(self, key, chan = 0):
        self.channels[chan].play(self.sounds[key])


    def stopSound(self, chan = 0):
        self.channels[chan].stop()


    def fadeOutSound(self, duration, chan = 0):
        self.channels[chan].fadeout(duration)


    def setChannels(self):
        # Channel 0 reserved for hud sounds 
        # Channel 1 reserved for game sounds
        # Channel 2 reserved for extra game sounds
        self.channels = [pygame.mixer.Channel(i) for i in range(3)]
        

    def loadAllSounds(self):
        for key, audio in config["audio"]["sounds"].items():
            a = pygame.mixer.Sound(os.path.join(AUDIOFOLDER, audio["file"]))
            a.set_volume(audio["volume"])
            self.sounds[key] = a


class MapLoader:
    def __init__(self):
        self.maps = {}
        self.builtInMaps = {}
        self.customMaps = {}

        self.loadAllMaps()


    def getMaps(self):
        return self.maps


    def getBuiltInMaps(self):
        return self.builtInMaps


    def getCustomMaps(self):
        return self.customMaps


    def getMap(self, key):
        return self.maps[key]

    
    def getMapData(self, key):
        level = self.maps[key]
        with open(level) as f:
            return json.load(f)


    def getLongestMapLength(self):
        longest = 0
        for mapName in self.maps:
            if len(mapName) > longest:
                longest = len(mapName)
        return longest


    def addMap(self, mapName, path, mapDict):
        mapDict[mapName] = path
        self.maps[mapName] = path


    def removeMap(self, mapName):
        del self.maps[mapName]


    def loadMaps(self, maps, mapDict):
        for key, level in maps.items():
            m = os.path.join(MAPSFOLDER, level)
            self.maps[key] = m
            mapDict[key] = m


    def loadAllMaps(self):
        self.loadMaps(config["maps"]["builtIn"], self.builtInMaps) # Load built-in levels
        self.loadMaps(config["maps"]["custom"], self.customMaps) # Load custom levels


    def checkMapExists(self, mapName):
        if mapName in self.maps:
            return True
        return False


