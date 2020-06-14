import pygame

from gridManager import *
from node import *
from menu import *
from engine import *

class MapEditor(SpriteRenderer):
    def __init__(self, game):
        super().__init__(game)

        # Hud for when the game is running
        self.hud = EditorHud(self.game)

        self.connectionManager = ConnectionManager(self.game)


    
    # Override creating the level
    def createLevel(self):
        self.clearLevel()

        self.gridLayer4 = EditorLayer4(self, self.connectionManager, (self.allSprites, self.layer4)) # Do i even need this layer????
        self.gridLayer3 = EditorLayer3(self, self.connectionManager, (self.allSprites, self.layer3, self.layer4))
        self.gridLayer1 = EditorLayer1(self, self.connectionManager, (self.allSprites, self.layer1, self.layer4))
        self.gridLayer2 = EditorLayer2(self, self.connectionManager, (self.allSprites, self.layer2, self.layer4))


    def createConnection(self, connectionType, startNode, endNode):
        layer = self.getGridLayer(connectionType)
        newConnections = layer.getGrid().addConnections(connectionType, startNode, endNode)

        # Only add the new connections to the nodes
        layer.addConnections(newConnections)

        

