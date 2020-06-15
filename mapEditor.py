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
    def createLevel(self, level = None):
        self.clearLevel()

        self.gridLayer4 = EditorLayer4(self, self.connectionManager, (self.allSprites, self.layer4), level) 
        self.gridLayer3 = EditorLayer3(self, self.connectionManager, (self.allSprites, self.layer3, self.layer4), level)
        self.gridLayer1 = EditorLayer1(self, self.connectionManager, (self.allSprites, self.layer1, self.layer4), level)
        self.gridLayer2 = EditorLayer2(self, self.connectionManager, (self.allSprites, self.layer2, self.layer4), level)


        self.gridLayer1.grid.loadTransport("layer 1", False)
        self.gridLayer2.grid.loadTransport("layer 2", False)
        self.gridLayer3.grid.loadTransport("layer 3", False)

        self.removeDuplicates()

        # Set the level data equal to the maps config file
        if level is not None:
            self.levelData = self.gridLayer4.getGrid().getMap()

    def saveLevel(self):
        pass


    def createConnection(self, connectionType, startNode, endNode):
        layer = self.getGridLayer(connectionType)
        newConnections = layer.getGrid().addConnections(connectionType, startNode, endNode)

        # Only add the new connections to the nodes
        layer.addConnections(newConnections)

        # Add the new connection to the level data
        self.levelData["connections"].setdefault(connectionType, []).append([startNode.getNumber(), endNode.getNumber()])


    def deleteConnection(self, connection):
        pass
        

