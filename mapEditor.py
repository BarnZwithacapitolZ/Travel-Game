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
        self.clickManager = EditorClickManager(self.game)


    def getSaved(self):
        return self.levelData["saved"]
    
    
    # Override creating the level
    def createLevel(self, level = None):
        self.clearLevel()

        self.gridLayer4 = EditorLayer4(self, (self.allSprites, self.layer4), level) 
        self.gridLayer3 = EditorLayer3(self, (self.allSprites, self.layer3, self.layer4), level)
        self.gridLayer1 = EditorLayer1(self, (self.allSprites, self.layer1, self.layer4), level)
        self.gridLayer2 = EditorLayer2(self, (self.allSprites, self.layer2, self.layer4), level)

        # Add the transport not running (so it doesnt move)
        self.gridLayer1.grid.loadTransport("layer 1", False)
        self.gridLayer2.grid.loadTransport("layer 2", False)
        self.gridLayer3.grid.loadTransport("layer 3", False)

        self.removeDuplicates()

        # Set the level data equal to the maps config file
        if level is not None:
            self.levelData = self.gridLayer4.getGrid().getMap()


    # Save As function
    def saveLevelAs(self):
        # Name of the map
        self.levelData["mapName"] = self.game.textHandler.getText()
        self.levelData["deletable"] = True
        self.levelData["saved"] = True

        saveName = "map" + str(len(self.game.mapLoader.getMaps()) + 1) + '.json'
        path = os.path.join(MAPSFOLDER, saveName)

        with open(path, "w") as f:
            json.dump(self.levelData, f)
        f.close()

        config["maps"][self.game.textHandler.getText()] = saveName
        dump(config)

        self.game.mapLoader.addMap(self.game.textHandler.getText(), path)

    
    # Save function, for when the level has already been created before (and is being edited)
    def saveLevel(self):
        with open(self.game.mapLoader.getMap(self.levelData["mapName"]), "w") as f:
            json.dump(self.levelData, f)
        f.close()


    def createConnection(self, connectionType, startNode, endNode):
        layer = self.getGridLayer(connectionType)
        newConnections = layer.getGrid().addConnections(connectionType, startNode, endNode)

        # Only add the new connections to the nodes
        layer.addConnections(newConnections)

        # Add the new connection to the level data
        self.levelData["connections"].setdefault(connectionType, []).append([startNode.getNumber(), endNode.getNumber()])


    def addTransport(self, connectionType, connection):
        layer = self.getGridLayer(connectionType)

        layer.getGrid().addTransport(connectionType, connection, False)

        node = connection.getFrom().getNumber()

        self.levelData["transport"].setdefault(connectionType, []).append(node)


    def deleteConnection(self, connection):
        # if the path to the file exists
        if os.path.exists("myfile.json"):
            os.remove("myfile.json") # delete the file
        

