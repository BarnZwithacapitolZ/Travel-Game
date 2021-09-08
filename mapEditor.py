import pygame
import copy
import os
import json
from pygame.locals import Color
from gridManager import GridManager
from node import EditorNode
from menu import EditorHud
from spriteRenderer import SpriteRenderer
from clickManager import EditorClickManager
from config import config, dump, MAPSFOLDER
from layer import EditorLayer1, EditorLayer2, EditorLayer3, EditorLayer4


class MapEditor(SpriteRenderer):
    def __init__(self, game):
        super().__init__(game)

        # Hud for when the game is running
        self.hud = EditorHud(self)
        self.clickManager = EditorClickManager(self.game)
        # Array to hold all the changes made to the map. TODO:
        #   should this have a limit on the size
        #   (otherwise it could get huge and be slow??)
        self.levelChanges = []
        self.poppedLevelChanges = []
        self.allowEdits = True

        self.connectionTypes = ["layer 1", "layer 2", "layer 3", "layer 4"]

        self.previousLayer = None

    def getSaved(self):
        return self.levelData["saved"]

    def getDeletable(self):
        return self.levelData["deletable"]

    def getAllowEdits(self):
        return self.allowEdits

    def getClickManager(self):
        return self.clickManager

    def getLevelChanges(self):
        return self.levelChanges

    def getPoppedLevelChanges(self):
        return self.poppedLevelChanges

    def getPreviousLayer(self):
        return self.previousLayer

    def setAllowEdits(self, allowEdits):
        self.allowEdits = allowEdits

    def undoChange(self):
        if self.rendering:
            if len(self.levelChanges) > 1:
                popped = self.levelChanges.pop()
                self.poppedLevelChanges.append(popped)
                self.levelData = copy.deepcopy(self.levelChanges[-1])

    def redoChange(self):
        if self.rendering:
            if len(self.poppedLevelChanges) > 0:
                popped = self.poppedLevelChanges.pop()
                self.levelChanges.append(popped)
                self.levelData = copy.deepcopy(popped)

    def addChange(self):
        change = copy.deepcopy(self.levelData)
        self.levelChanges.append(change)

    def translateConnections(self, layer, oldMapPos, newMapPos):
        if layer not in self.levelData["connections"]:
            return

        newConnections = []
        for connection in self.levelData["connections"][layer]:
            c1 = oldMapPos[connection[0]]
            c2 = oldMapPos[connection[1]]

            if c1 in newMapPos and c2 in newMapPos:
                n1 = newMapPos[c1]
                n2 = newMapPos[c2]
                newConnections.append([n1, n2])

        self.levelData["connections"][layer] = newConnections

    def translateNodes(self, nodeType, layer, oldMapPos, newMapPos):
        if layer not in self.levelData[nodeType]:
            return

        for key, node in list(enumerate(self.levelData[nodeType][layer])):
            n1 = oldMapPos[node["location"]]
            if n1 in newMapPos:
                n2 = newMapPos[n1]
                node["location"] = n2
            else:
                del self.levelData[nodeType][layer][key]

    def setMapSize(self, size=(18, 10)):
        if not hasattr(self, 'levelData'):
            return

        oldMapPos = GridManager.getMapValues(
            self.levelData["width"], self.levelData["height"])
        newMapPos = GridManager.getMapValues(size[0], size[1], True)

        self.translateConnections("layer 1", oldMapPos, newMapPos)
        self.translateConnections("layer 2", oldMapPos, newMapPos)
        self.translateConnections("layer 3", oldMapPos, newMapPos)

        self.translateNodes("transport", "layer 1", oldMapPos, newMapPos)
        self.translateNodes("transport", "layer 2", oldMapPos, newMapPos)
        self.translateNodes("transport", "layer 3", oldMapPos, newMapPos)

        self.translateNodes("stops", "layer 1", oldMapPos, newMapPos)
        self.translateNodes("stops", "layer 2", oldMapPos, newMapPos)
        self.translateNodes("stops", "layer 3", oldMapPos, newMapPos)

        self.translateNodes("destinations", "layer 1", oldMapPos, newMapPos)
        self.translateNodes("destinations", "layer 2", oldMapPos, newMapPos)
        self.translateNodes("destinations", "layer 3", oldMapPos, newMapPos)

        self.levelData["width"] = size[0]
        self.levelData["height"] = size[1]

        self.addChange()

    def setTotalToComplete(self, total):
        if not hasattr(self, 'levelData'):
            return

        self.levelData['total'] = total
        self.addChange()

    def setBackgroundColor(self, layer, backgroundColor, darkMode=False):
        if not hasattr(self, 'levelData'):
            return

        # Cast to array if Color object
        if type(backgroundColor) is Color:
            backgroundColor = [
                backgroundColor[0], backgroundColor[1], backgroundColor[2]]

        self.levelData['backgrounds']["layer " + str(layer)] = backgroundColor
        self.levelData['backgrounds']['darkMode'] = darkMode
        self.addChange()

    # Returns true if dropdowns have been closed, false otherwise
    def isDropdownsClosed(self):
        if self.rendering and not self.allowEdits:
            self.hud.closeDropdowns()
            return True
        return False

    # Override creating the level
    def createLevel(self, level=None, clearChanges=False, layer=None):
        self.clearLevel()
        self.connectionTypes = ["layer 1", "layer 2", "layer 3", "layer 4"]

        self.gridLayer4 = EditorLayer4(
            self, (self.allSprites, self.layer4), level)
        self.gridLayer3 = EditorLayer3(
            self, (self.allSprites, self.layer3, self.layer4), level)
        self.gridLayer1 = EditorLayer1(
            self, (self.allSprites, self.layer1, self.layer4), level)
        self.gridLayer2 = EditorLayer2(
            self, (self.allSprites, self.layer2, self.layer4), level)

        self.gridLayer4.addLayerLines(
            self.gridLayer1, self.gridLayer2, self.gridLayer3)

        # Add the transport not running (so it doesnt move)
        self.gridLayer1.grid.loadTransport("layer 1", False)
        self.gridLayer2.grid.loadTransport("layer 2", False)
        self.gridLayer3.grid.loadTransport("layer 3", False)

        self.removeDuplicates()

        # Set the level data equal to the maps config file
        if level is not None:
            self.levelData = self.gridLayer4.getGrid().getMap()

        # Creating a new level
        if clearChanges:
            self.levelChanges = [copy.deepcopy(self.levelData)]
            self.poppedLevelChanges = []

        # load the level on a specific layer (for undoing / redoing changes)
        if layer is not None:
            self.showLayer(layer)

    # Check the user can save the level by meeting the criteria
    def canSaveLevel(self):
        # Get the total amount of locations from each layer for comparison
        totalDestinations = 0
        for desintations in self.levelData['destinations'].values():
            totalDestinations += len(desintations)

        if ('layer 1' not in self.levelData['connections'] and
            'layer 2' not in self.levelData['connections']
                and 'layer 3' not in self.levelData['connections']):

            return False, "You haven't added anything to the map!"

        elif (  # No layer 2 connections for the player to spawn ons
            'layer 2' not in self.levelData['connections']
                or len(self.levelData['connections']['layer 2']) <= 0):

            return False, "There must be a road for people to travel on!"

        elif totalDestinations <= 1:
            return False, "There must be at least 2 locations \
                for people to spawn on and reach!"

        return [True]

    # Save As function
    def saveLevelAs(self):
        # Name of the map
        self.levelData["mapName"] = self.game.textHandler.getString()
        self.levelData["deletable"] = True
        self.levelData["saved"] = True

        # saveName = "map" + str(
        #    len(self.game.mapLoader.getMaps()) + 1) + '.json'
        saveName = (
            "map_" +
            self.game.textHandler.getString().replace(" ", "_") + '.json')
        path = os.path.join(MAPSFOLDER, saveName)

        with open(path, "w") as f:
            json.dump(self.levelData, f)

        config["maps"]["custom"][self.game.textHandler.getString()] = saveName
        dump(config)

        self.game.mapLoader.addMap(
            self.game.textHandler.getString(),
            path, self.game.mapLoader.getCustomMaps())
        self.game.mainMenu.updateCustomMaps()

    # Remove a map, which has already been saved,
    # from the maps folder and references in config

    # TODO: FIX NAMING CONVENTION OF MAPS SO WHEN DELETED IT DOESNT
    # MESS WITH THE OTHER MAPS WHEN CREATING A NEW MAP

    def deleteLevel(self):
        path = self.game.mapLoader.getMap(self.levelData["mapName"])
        if os.path.exists(path):
            # Delete the level
            os.remove(path)
            self.game.mapLoader.removeMap(self.levelData["mapName"])
            self.game.mapLoader.removeCustomMap(self.levelData["mapName"])
            self.game.mainMenu.updateCustomMaps()
            del config["maps"]["custom"][self.levelData["mapName"]]
            dump(config)

    # given two nodes A & B, work out all intersecting child
    # connecting nodes along the parent connection between A & B
    def getIntersetingConnections(self, layer, startNode, endNode):
        distance = ((startNode.pos) - (endNode.pos)).length()
        connections = []

        for node in layer.getGrid().getNodes():
            buffer = 0.1  # Radius around the line to include nodes within
            d1 = (node.pos - startNode.pos).length()
            d2 = (node.pos - endNode.pos).length()

            if d1 + d2 >= distance - buffer and d1 + d2 <= distance + buffer:
                connections.append(node)

        return connections

    def createTempConnection(self, connectionType, startNode, endNode):
        layer = self.getGridLayer(connectionType)
        connections = self.getIntersetingConnections(layer, startNode, endNode)

        for x in range(len(connections) - 1):
            newConnections = layer.getGrid().addConnections(
                connectionType, connections[x], connections[x + 1], True)

            # Only add the new connections to the nodes
            layer.addTempConnections(newConnections)
            layer.createConnections()

        # Add the new temp connections to layer 4 for previewing
        self.gridLayer4.addLayerLines(
            self.gridLayer1, self.gridLayer2, self.gridLayer3)

    def createConnection(self, connectionType, startNode, endNode):
        layer = self.getGridLayer(connectionType)
        connections = self.getIntersetingConnections(layer, startNode, endNode)

        for x in range(len(connections) - 1):
            newConnections = layer.getGrid().addConnections(
                connectionType, connections[x], connections[x + 1])

            # Only add the new connections to the nodes
            layer.addConnections(newConnections)
            layer.createConnections()

            # Add the new connection to the level data
            connection = [
                connections[x].getNumber(), connections[x + 1].getNumber()]

            if connection not in self.levelData["connections"].setdefault(
                    connectionType, []):
                self.levelData["connections"][connectionType].append(
                    connection)

        self.addChange()

    def addTransport(self, connectionType, connection):
        layer = self.getGridLayer(connectionType)

        key = self.clickManager.getAddType()
        mappings = layer.getGrid().getTransportMappings()

        if key in mappings:
            layer.getGrid().addTransport(  # False so the transports dont move
                connectionType, connection, mappings[key], False)
            self.levelData["transport"].setdefault(connectionType, []).append({
                "location": connection.getFrom().getNumber(),
                "type": str(key)
            })

        self.addChange()

    # TO DO: Maybe let the user select the stop type they want to add,
    # so there can be different types of stops on each layer?
    def addStop(self, connectionType, node):
        layer = self.getGridLayer(connectionType)

        key = self.clickManager.getAddType()
        mappings = layer.getGrid().getEditorStopMappings()

        if key in mappings:
            newNode = layer.getGrid().replaceNode(
                connectionType, node, mappings[key])

            self.levelData["stops"].setdefault(connectionType, []).append({
                "location": newNode.getNumber(), "type": str(key)})

        self.addChange()

    def addDestination(self, connectionType, node):
        layer = self.getGridLayer(connectionType)

        key = self.clickManager.getAddType()
        mappings = layer.getGrid().getEditorDestinationMappings()

        if key in mappings:
            newNode = layer.getGrid().replaceNode(
                connectionType, node, mappings[key])

            self.levelData["destinations"].setdefault(
                connectionType, []).append({
                    "location": newNode.getNumber(), "type": str(key)})

        self.addChange()

    def deleteDestination(self, connectionType, node):
        layer = self.getGridLayer(connectionType)

        mappings = layer.getGrid().getEditorDestinationMappings()
        key = layer.getGrid().reverseMappingsSearch(mappings, node)

        if key:
            newNode = layer.getGrid().replaceNode(
                connectionType, node, EditorNode)

            self.levelData["destinations"][connectionType].remove({
                "location": newNode.getNumber(), "type": str(key)})

        self.addChange()

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
                "location": node.getNumber(), "type": str(key)})

        self.addChange()

    def deleteStop(self, connectionType, node):
        layer = self.getGridLayer(connectionType)

        mappings = layer.getGrid().getEditorStopMappings()
        key = layer.getGrid().reverseMappingsSearch(mappings, node)

        if key:
            newNode = layer.getGrid().replaceNode(
                connectionType, node, EditorNode)

            self.levelData["stops"][connectionType].remove({
                "location": newNode.getNumber(),
                "type": str(key)
            })

        self.addChange()

    def deleteConnection(self, connectionType, connection):
        layer = self.getGridLayer(connectionType)

        connections = layer.getGrid().getOppositeConnection(connection)

        if connections:
            layer.getGrid().removeConnections(connections)
            layer.removeConnections(connections)

            self.levelData["connections"][connectionType].remove(
                [
                    connection.getFrom().getNumber(),
                    connection.getTo().getNumber()])

            if len(self.levelData["connections"][connectionType]) <= 0:
                del self.levelData["connections"][connectionType]
            self.addChange()

        else:
            return

    def removeAllTempConnections(self, connectionType):
        layer = self.getGridLayer(connectionType)

        layer.removeTempConnections()
        layer.getGrid().removeTempConnections()
        layer.createConnections()

        # remove the new temp connections to layer 4 for previewing
        self.gridLayer4.addLayerLines(
            self.gridLayer1, self.gridLayer2, self.gridLayer3)

    def updateConnection(self, layer, group):
        if self.currentLayer == layer:
            for connection in group.getGrid().getConnections():
                connection.update()

    def events(self):
        if (pygame.mouse.get_pressed()[2]
                and self.game.clickManager.getRightClicked()
                and self.currentLayer != 4):
            self.game.clickManager.setRightClicked(False)
            self.previousLayer = self.currentLayer
            self.showLayer(4)

            # Show the currently selected node at the top
            if self.clickManager.getStartNode() is not None:
                node = self.getTopNode(self.clickManager.getStartNode())
                self.clickManager.setPreviewStartNode(node)
                # Change the image of the top node to match the one beneath it
                node.setMouseOver(True)

        elif (not pygame.mouse.get_pressed()[2]
                and self.previousLayer is not None):
            self.showLayer(self.previousLayer)
            self.previousLayer = None

        # if there is a click and a connection is not set,
        # then remove the start node
        if (self.clickManager.getStartNode() is not None
                and self.game.clickManager.getClicked()):
            self.clickManager.setStartNode(None)
            self.game.clickManager.setClicked(False)

        if (self.clickManager.getClickType()
                == EditorClickManager.ClickType.DCONNECTION):
            self.updateConnection(1, self.gridLayer1)
            self.updateConnection(2, self.gridLayer2)
            self.updateConnection(3, self.gridLayer3)

    def update(self):
        if not self.rendering:
            return

        self.allSprites.update()
        self.hud.update()
        self.messageSystem.update()

        self.events()
