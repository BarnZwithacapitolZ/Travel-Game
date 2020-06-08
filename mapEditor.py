import pygame

from gridManager import *

class MapEditor:
    def __init__(self, game):
        self.game = game
        self.nodePositions = GridManager.setNodePositions()

        self.createGrid()

    def createGrid(self):
        print(self.nodePositions)

