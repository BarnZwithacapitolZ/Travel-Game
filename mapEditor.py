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

    def getDeletable(self):
        return self.levelData["deletable"]
    
    
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

        # saveName = "map" + str(len(self.game.mapLoader.getMaps()) + 1) + '.json'
        saveName = "map_" + self.game.textHandler.getText().replace(" ", "_") + '.json'
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


    # Remove a map, which has already been saved, from the maps folder and references in config
    # TODO: FIX NAMING CONVENTION OF MAPS SO WHEN DELETED IT DOESNT MESS WITH THE OTHER MAPS WHEN CREATING A NEW MAP
    def deleteLevel(self):
        path = self.game.mapLoader.getMap(self.levelData["mapName"])
        if os.path.exists(path):
            os.remove(path) # Delete the level
            self.game.mapLoader.removeMap(self.levelData["mapName"])
            del config["maps"][self.levelData["mapName"]]
            dump(config)

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

        number = connection.getFrom().getNumber()

        self.levelData["transport"].setdefault(connectionType, []).append(number)


    # TO DO: Maybe let the user select the stop type they want to add so there can be different types of stops on each layer?
    def addStop(self, connectionType, node):
        layer = self.getGridLayer(connectionType)

        if connectionType == "layer 2":
            stopType = EditorBusStop
        else:
            stopType = EditorMetroStation

        newNode = layer.getGrid().replaceNode(connectionType, node, stopType)

        self.levelData["stops"].setdefault(connectionType, []).append(newNode.getNumber())


    def deleteTransport(self, connectionType, node):
        layer = self.getGridLayer(connectionType)

        # Since a node in the editor can only have one transport on it
        transport = node.getTransports()[0]

        node.removeTransport(transport)
        layer.getGrid().removeTransport(transport)

        self.levelData["transport"][connectionType].remove(node.getNumber())
        

    def deleteStop(self, connectionType, node):
        layer = self.getGridLayer(connectionType)

        newNode = layer.getGrid().replaceNode(connectionType, node, EditorNode)

        self.levelData["stops"][connectionType].remove(newNode.getNumber())


    def deleteConnection(self, connection):
        pass
        

    def update(self):
        super().update()

        if self.rendering:
            if self.currentLayer == 1:
                for connection in self.gridLayer1.getGrid().getConnections():
                    connection.update()
            
            elif self.currentLayer == 2:
                for connection in self.gridLayer2.getGrid().getConnections():
                    connection.update()

            elif self.currentLayer == 3:
                for connection in self.gridLayer3.getGrid().getConnections():
                    connection.update()