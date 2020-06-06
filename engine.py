import pygame
from pygame.locals import *
from config import *
import os

from layer import *
from clickManager import *
from node import *

vec = pygame.math.Vector2

class Renderer:
    def __init__(self):
        self.width = config["graphics"]["displayWidth"]
        self.height = config["graphics"]["displayHeight"]
        self.windowWidth = config["graphics"]["displayWidth"]
        self.windowHeight = config["graphics"]["displayHeight"]

        self.monitorWidth = pygame.display.Info().current_w
        self.monitorHeight = pygame.display.Info().current_h

        self.screen = pygame.display.set_mode((self.windowWidth, self.windowHeight), pygame.RESIZABLE)
        self.gameDisplay = pygame.Surface((self.width, self.height))

        # self.gameDisplay.set_alpha(None)

        self.scale = 1
        self.surfaces = []


    # Prepare the gamedisplay for blitting to, this means overriding it with a new color
    def prepareSurface(self, color):
        self.gameDisplay.fill(color)


    # Add a surface to the gameDisplay
    def addSurface(self, surface, pos = tuple(), resize = False):
        self.surfaces.append((surface, vec(pos[0], pos[1]), resize))


    def setWidth(self, width):
        self.width = width


    def setHeight(self, height):
        self.height = height


    def getScale(self):
        return self.scale


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

        self.scale = round(min(size[1] / config["graphics"]["displayHeight"], size[0] / config["graphics"]["displayWidth"]), 1)
        
        self.width = (config["graphics"]["displayWidth"] * self.scale)
        self.height = (config["graphics"]["displayHeight"] * self.scale)
        self.windowWidth = size[0]
        self.windowHeight = size[1]
        if fullscreen:
            self.screen = pygame.display.set_mode((int(self.windowWidth), int(self.windowHeight)), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
        else:
            self.screen = pygame.display.set_mode((int(self.windowWidth), int(self.windowHeight)), pygame.RESIZABLE)
        self.gameDisplay = pygame.Surface((self.width, self.height))  


    # on tick function
    def render(self):
        # self.gameDisplay.fill((	35, 201, 220)) #white

        for surface in self.surfaces:    
            self.gameDisplay.blit(surface[0], (surface[1].x, surface[1].y))

        self.screen.blit(self.gameDisplay, (0 + self.getDifference()[0], 0 + self.getDifference()[1]))
        self.surfaces = []
        
        pygame.display.update()


class SpriteRenderer():
    #loads all the sprites into groups and stuff
    def __init__(self, game):
        self.allSprites = pygame.sprite.Group()
        self.layer1 = pygame.sprite.Group() # layer 1
        self.layer2 = pygame.sprite.Group() # layer 2
        self.layer3 = pygame.sprite.Group() # layer 3
        self.layer4 = pygame.sprite.Group() # layer 4 is all layers combined
        self.game = game
        self.currentLayer = 4


    def createLevel(self):
        # ordering matters -> stack
        
        self.allLayers = Layer4(self, (self.allSprites, self.layer4))
        layer3 = Layer3(self, (self.allSprites, self.layer3, self.layer4))
        layer1 = Layer1(self, (self.allSprites, self.layer1, self.layer4))
        layer2 = Layer2(self, (self.allSprites, self.layer2, self.layer4)) # walking layer at the bottom so nodes are drawn above metro stations

        layer1.grid.loadTransport("layer 1")
        # layer2.grid.loadTransport("layer 2")
        # layer3.grid.loadTransport("layer 3")

        layer2.addPerson()

        self.removeDuplicates()

    # Remove duplicate nodes on layer 4 for layering
    def removeDuplicates(self):
        seen = {}
        dupes = []
        
        for sprite in self.layer4:
            if isinstance(sprite, Node):
                if sprite.getNumber() not in seen:
                    seen[sprite.getNumber()] = 1
                else:
                    if seen[sprite.getNumber()] == 1:
                        dupes.append(sprite)
                    seen[sprite.getNumber()] += 1
        
        for sprite in dupes:
            self.layer4.remove(sprite)



    def update(self):
        self.allSprites.update()


    def showLayer(self, layer):
        self.currentLayer = layer
        self.resize() #redraw the nodes so that the mouse cant collide with them


    def getLayer(self):
        return self.currentLayer


    def resize(self):
        self.allLayers.resize()
        for sprite in self.allSprites:
            sprite.dirty = True


    def render(self):
        if self.currentLayer == 1:
            for sprite in self.layer1:
                sprite.draw()
            
        elif self.currentLayer == 2:
            for sprite in self.layer2:
                sprite.draw()

        elif self.currentLayer == 3:
            for sprite in self.layer3:
                sprite.draw()

        elif self.currentLayer == 4:
            for sprite in self.layer4:
                sprite.draw()


class ImageLoader:
    def __init__(self):
        self.images = {}

        self.loadAllImages()

    def loadAllImages(self):
        for key, image in config["images"].items():
            i = pygame.image.load(os.path.join(ASSETSFOLDER, image)).convert_alpha()
            self.images[key] = i

    def getImage(self, key):
        return self.images[key]


class SoundEnging:
    pass
    