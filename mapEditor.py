import pygame

from gridManager import *
from node import *
from menu import *

class MapEditor:
    def __init__(self, game):
        self.game = game
        self.nodePositions = GridManager.setNodePositions()

        self.createGrid()

        self.hud = EditorHud(self.game)
        self.rendering = False


    def setRendering(self, rendering):
        self.rendering = rendering
        self.hud.main() if self.rendering else self.hud.close()


    def getHud(self):
        return self.hud

    def createGrid(self):
        pass



    def render(self):
        if self.rendering:
            self.hud.display()

