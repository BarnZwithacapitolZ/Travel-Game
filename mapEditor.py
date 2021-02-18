import pygame

from gridManager import *
from node import *
from menu import *
from spriteRenderer import *
from clickManager import *

class MapEditor(SpriteRenderer):
    def __init__(self, game):
        super().__init__(game)

        # Hud for when the game is running
        self.hud = EditorHud(self.game)
        self.clickManager = EditorClickManager(self.game)

        self.allowEdits = True

    def getSaved(self):
        return self.levelData["saved"]

    def getDeletable(self):
        return self.levelData["deletable"]

    def getAllowEdits(self):
        return self.allowEdits

    def getClickManager(self):
        return self.clickManager


    def setAllowEdits(self, allowEdits):
        self.allowEdits = allowEdits

    def setMapSize(self, size = (18, 10)):
        if not hasattr(self, 'levelData'):
            return

        self.levelData["width"] = size[0]
        self.levelData["height"] = size[1]
        

    # returns true if dropdowns have been closed, false otherwise
    def isDropdownsClosed(self):
        if self.rendering and not self.allowEdits:
            self.hud.closeDropdowns()
            return True
        return False
    
    
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


    # check the user can save the level by meeting the criteria
    def canSaveLevel(self):
        if 'layer 1' not in self.levelData['connections'] and 'layer 2' not in self.levelData['connections'] and 'layer 3' not in self.levelData['connections']:
            return False, "You haven't added anything to the map!"
        elif 'layer 2' not in self.levelData['connections'] or len(self.levelData['connections']['layer 2']) <= 0: # no layer 2 connections for the player to spawn on
            return False, "There must be a road for people to travel on!"
        elif len(self.levelData['destinations']) <= 0:
            return False, "There is no destinations for people to reach!"

        return [True]

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


    # given two nodes A & B, work out all intersecting child connecting nodes along the parent connection between A & B
    def getIntersetingConnections(self, layer, startNode, endNode):
        distance = ((startNode.pos) - (endNode.pos)).length()
        connections = []

        for node in layer.getGrid().getNodes():
            buffer = 0.1 # radius around the line to include nodes within
            d1 = (node.pos - startNode.pos).length()
            d2 = (node.pos - endNode.pos).length()

            if d1 + d2 >= distance - buffer and d1 + d2 <= distance + buffer:
                connections.append(node)

        return connections


    def createTempConnection(self, connectionType, startNode, endNode):
        layer = self.getGridLayer(connectionType)  
        connections = self.getIntersetingConnections(layer, startNode, endNode)

        for x in range(len(connections) - 1):
            newConnections = layer.getGrid().addConnections(connectionType, connections[x], connections[x + 1], True)

            # Only add the new connections to the nodes
            layer.addTempConnections(newConnections)
            layer.createConnections()


    def createConnection(self, connectionType, startNode, endNode):
        layer = self.getGridLayer(connectionType)
        connections = self.getIntersetingConnections(layer, startNode, endNode)
      
        for x in range(len(connections) - 1):
            newConnections = layer.getGrid().addConnections(connectionType, connections[x], connections[x + 1])

            # Only add the new connections to the nodes
            layer.addConnections(newConnections)
            layer.createConnections()

            # Add the new connection to the level data
            connection = [connections[x].getNumber(), connections[x + 1].getNumber()]
            if connection not in self.levelData["connections"].setdefault(connectionType, []):
                self.levelData["connections"][connectionType].append(connection)


    def addTransport(self, connectionType, connection):
        layer = self.getGridLayer(connectionType)

        key = self.clickManager.getAddType()
        mappings = layer.getGrid().getTransportMappings()

        if key in mappings:
            layer.getGrid().addTransport(connectionType, connection, mappings[key], False) # False so the transports dont move
            self.levelData["transport"].setdefault(connectionType, []).append({
                "location": connection.getFrom().getNumber(),
                "type": str(key)
            })


    # TO DO: Maybe let the user select the stop type they want to add so there can be different types of stops on each layer?
    def addStop(self, connectionType, node):
        layer = self.getGridLayer(connectionType)

        key = self.clickManager.getAddType()
        mappings = layer.getGrid().getEditorStopMappings()

        if key in mappings:
            newNode = layer.getGrid().replaceNode(connectionType, node, mappings[key])
            self.levelData["stops"].setdefault(connectionType, []).append({
                "location": newNode.getNumber(),
                "type": str(key)
            })


    def addDestination(self, connectionType, node):
        layer = self.getGridLayer(connectionType)

        key = self.clickManager.getAddType()
        mappings = layer.getGrid().getEditorDestinationMappings()

        if key in mappings:
            newNode = layer.getGrid().replaceNode(connectionType, node, mappings[key])
            self.levelData["destinations"].setdefault(connectionType, []).append({
                "location": newNode.getNumber(),
                "type": str(key)
            })


    def deleteDestination(self, connectionType, node):
        layer = self.getGridLayer(connectionType)

        mappings = layer.getGrid().getEditorDestinationMappings()
        key = layer.getGrid().reverseMappingsSearch(mappings, node)

        if key:
            newNode = layer.getGrid().replaceNode(connectionType, node, EditorNode)

            self.levelData["destinations"][connectionType].remove({
                "location": newNode.getNumber(),
                "type": str(key)
            })


    def deleteTransport(self, connectionType, node):
        layer = self.getGridLayer(connectionType)

        # Since a node in the editor can only have one transport on it
        transport = node.getTransports()[0]

        mappings = layer.getGrid().getTransportMappings()
        key = layer.getGrid().reverseMappingsSearch(mappings, transport)

        if key:
            node.removeTransport(transport)
            layer.getGrid().removeTransport(transport)

            self.levelData["transport"][connectionType].remove({
                "location": node.getNumber(),
                "type": str(key)
            })        


    def deleteStop(self, connectionType, node):
        layer = self.getGridLayer(connectionType)

        mappings = layer.getGrid().getEditorStopMappings()
        key = layer.getGrid().reverseMappingsSearch(mappings, node)

        if key:
            newNode = layer.getGrid().replaceNode(connectionType, node, EditorNode)

            self.levelData["stops"][connectionType].remove({
                "location": newNode.getNumber(),
                "type": str(key)
            })


    def deleteConnection(self, connectionType, connection):
        layer = self.getGridLayer(connectionType)

        connections = layer.getGrid().getOppositeConnection(connection)

        if connections:
            layer.getGrid().removeConnections(connections)
            layer.removeConnections(connections)

            self.levelData["connections"][connectionType].remove([connection.getFrom().getNumber(), connection.getTo().getNumber()])
        else:
            return


    def removeAllTempConnections(self, connectionType):
        layer = self.getGridLayer(connectionType)

        layer.removeTempConnections()
        layer.getGrid().removeTempConnections()
        layer.createConnections()


    def updateConnection(self, layer, group):
        if self.currentLayer == layer:
            for connection in group.getGrid().getConnections():
                connection.update()    


    def update(self):
        if self.rendering:
            self.allSprites.update()

            # if there is a click and a connection is not set, remove the start node
            if self.clickManager.getStartNode() is not None and self.game.clickManager.getClicked():
                self.clickManager.setStartNode(None)
                self.game.clickManager.setClicked(False)


            if self.clickManager.getClickType() == EditorClickManager.ClickType.DCONNECTION:
                self.updateConnection(1, self.gridLayer1)
                self.updateConnection(2, self.gridLayer2)
                self.updateConnection(3, self.gridLayer3)
