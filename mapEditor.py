import pygame
import copy
import os
import json
from pygame.locals import Color
from gridManager import GridManager
from node import NodeType
from hud import EditorHud
from spriteRenderer import SpriteRenderer
from clickManager import EditorClickManager
from config import config, dump, MAPSFOLDER
from layer import Layer


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
        self.showTransport = True

        # Map editor always has all connection types available
        # (to edit  each layer)
        self.connectionTypes = ["layer 1", "layer 2", "layer 3", "layer 4"]

        self.previousLayer = None

    def getSaved(self):
        return self.levelData["saved"]

    def getDeletable(self):
        return self.levelData["deletable"]

    def getAllowEdits(self):
        return self.allowEdits

    def getShowTransport(self):
        return self.showTransport

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

    def setShowTransport(self, showTransport):
        self.showTransport = showTransport

    def undoChange(self):
        if not self.rendering or len(self.levelChanges) <= 1:
            return
        popped = self.levelChanges.pop()
        self.poppedLevelChanges.append(popped)
        self.levelData = copy.deepcopy(self.levelChanges[-1])

    def redoChange(self):
        if not self.rendering or len(self.poppedLevelChanges) <= 0:
            return
        popped = self.poppedLevelChanges.pop()
        self.levelChanges.append(popped)
        self.levelData = copy.deepcopy(popped)

    def addChange(self):
        change = copy.deepcopy(self.levelData)
        # Only add the changes if it actually changes the level data
        if change != self.levelChanges[-1]:
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
        if (nodeType not in self.levelData
                or layer not in self.levelData[nodeType]):
            return

        for key, node in list(enumerate(self.levelData[nodeType][layer])):
            n1 = oldMapPos[node["location"]]
            if n1 in newMapPos:
                n2 = newMapPos[n1]
                node["location"] = n2
            else:
                del self.levelData[nodeType][layer][key]

    def translateNodeSet(self, nodeType, oldMapPos, newMapPos):
        self.translateNodes(nodeType, "layer 1", oldMapPos, newMapPos)
        self.translateNodes(nodeType, "layer 2", oldMapPos, newMapPos)
        self.translateNodes(nodeType, "layer 3", oldMapPos, newMapPos)

    def setMapSize(self, size=(18, 10)):
        if not hasattr(self, 'levelData'):
            return

        oldMapPos = GridManager.getMapValues(
            self.levelData["width"], self.levelData["height"])
        newMapPos = GridManager.getMapValues(size[0], size[1], True)

        self.translateConnections("layer 1", oldMapPos, newMapPos)
        self.translateConnections("layer 2", oldMapPos, newMapPos)
        self.translateConnections("layer 3", oldMapPos, newMapPos)

        # Move transports to new position for each layer
        self.translateNodeSet("transport", oldMapPos, newMapPos)

        # Move special nodes to new positions for each layer
        self.translateNodeSet(NodeType.SPECIAL.value, oldMapPos, newMapPos)

        # Move stops to new positions for each layer
        self.translateNodeSet(NodeType.STOP.value, oldMapPos, newMapPos)

        # Move destinations to new positions for each layer
        self.translateNodeSet(NodeType.DESTINATION.value, oldMapPos, newMapPos)

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

        # Make sure the background data exists and if not add it in
        if ("backgrounds" in self.levelData
                and "layer " + str(layer) in self.levelData['backgrounds']):
            self.levelData['backgrounds'][
                "layer " + str(layer)] = backgroundColor
            self.levelData['backgrounds']['darkMode'] = darkMode

        else:
            self.levelData['backgrounds'] = {
                "layer " + str(layer): backgroundColor,
                "darkMode": darkMode
            }

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

        self.gridLayer4 = Layer(self, (self.allSprites, self.layer4), 4, level)
        self.gridLayer3 = Layer(self, (
            self.allSprites, self.layer3, self.layer4), 3, level)
        self.gridLayer2 = Layer(self, (
            self.allSprites, self.layer2, self.layer4), 2, level)
        self.gridLayer1 = Layer(self, (
            self.allSprites, self.layer1, self.layer4), 1, level)

        # Ordering of the layers.
        self.gridLayer3.createGrid(True)
        self.gridLayer1.createGrid(True)
        self.gridLayer2.createGrid(True)
        self.setGridLayer4Lines()

        # Add the transport not running (so it doesnt move)
        if self.showTransport:
            self.gridLayer1.grid.loadTransport("layer 1", False)
            self.gridLayer2.grid.loadTransport("layer 2", False)
            self.gridLayer3.grid.loadTransport("layer 3", False)

        self.removeDuplicates(addIndicator=False)

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
            # Delete the map file from the filePath.
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
            layer.createTempConnections(newConnections, False)

        # Add the new temp connections to layer 4 for previewing
        self.gridLayer4.setLayerTempLines(
            self.gridLayer1, self.gridLayer2, self.gridLayer3)

    def createConnection(self, connectionType, startNode, endNode):
        layer = self.getGridLayer(connectionType)
        connections = self.getIntersetingConnections(layer, startNode, endNode)

        for x in range(len(connections) - 1):
            connection = [
                connections[x].getNumber(), connections[x + 1].getNumber()]

            # We don't want to add the connection to the map if an equivelant
            # connection already exists
            if connection in self.levelData["connections"].setdefault(
                    connectionType, []):
                continue

            newConnections = layer.getGrid().addConnections(
                connectionType, connections[x], connections[x + 1])

            # Only add the new connections to the nodes
            layer.addConnections(newConnections)
            layer.createConnections(newConnections, False)

            # Add the new connection to the level data
            self.levelData["connections"][connectionType].append(
                connection)

        self.setGridLayer4Lines()
        self.addChange()

    def checkCanAddItem(self, node, item="node"):
        layer = self.getGridLayer(node.getConnectionType())
        key = self.clickManager.getAddType()

        # Get the respective mappings for nodes and transports
        if item == "node":
            mappings = layer.getGrid().getNodeMappingsByLayer()
        elif item == "transport":
            mappings = layer.getGrid().getTransportMappingsByLayer()
        else:
            mappings = []

        # Check if we can add the transport / node to the layer,
        # if not, throw the error message
        if key not in mappings:
            self.messageSystem.addMessage(f"You cannot add a {key} to \
                {self.getLayerName(node.getConnectionType()).lower()} \
                layer :(")
            return False
        return True

    def addTransport(self, connectionType, connection):
        layer = self.getGridLayer()

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

    def swapNode(self, oldNodeType, newNodeType, connectionType, node):
        self.deleteNode(connectionType, node, False, False)
        self.addNode(newNodeType, connectionType, node)

    def addNode(
            self, nodeType, connectionType, node, replaceNode=True,
            addChange=True):
        layer = self.getGridLayer(connectionType)
        key = self.clickManager.getAddType()

        if replaceNode:
            # Replace the current node with the one we want to place down
            layer.getGrid().replaceNode(
                node, connectionType, nodeType, key)

        # Add the node to the data, or if the connection type doesn't exist
        # set its default to the empty list (for adding to later)
        if nodeType in self.levelData:
            self.levelData[nodeType].setdefault(
                connectionType, []).append({
                    "location": node.getNumber(), "type": str(key)})

        else:
            self.levelData[nodeType] = {connectionType: [{
                "location": node.getNumber(),
                "type": str(key)
            }]}

        if addChange:
            self.addChange()

    def deleteNode(
            self, connectionType, node, replaceNode=True,
            addChange=True):
        layer = self.getGridLayer(connectionType)

        if replaceNode:
            # Replace with default editor node
            layer.getGrid().replaceNode(node, connectionType)

        # Remove the node from the data
        self.levelData[node.getType().value][connectionType].remove({
            "location": node.getNumber(),
            "type": str(node.getSubType().value)})

        if addChange:
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

    def deleteConnection(self, connectionType, connection):
        layer = self.getGridLayer(connectionType)

        connections = layer.getGrid().getOppositeConnection(connection)

        if connections:
            # Remove the connections from the layer and its associalted grid.
            layer.removeConnections(connections)

            # 'Reset' the lines by creating all the connections again,
            # excluding the ones we just deleted.
            layer.createConnections()

            self.levelData["connections"][connectionType].remove(
                [
                    connection.getFrom().getNumber(),
                    connection.getTo().getNumber()])

            if len(self.levelData["connections"][connectionType]) <= 0:
                del self.levelData["connections"][connectionType]

            # Set the layer 4 lines equal to the sum of all the other
            # layers lines.
            self.setGridLayer4Lines()
            self.addChange()

        else:
            return

    def removeAllTempConnections(self, connectionType):
        layer = self.getGridLayer(connectionType)

        # Remove all temp connecionts from layer and its grid.
        layer.removeAllTempConnections()

        # 'Reset' the lines by creating all the connections again,
        # excluding the lines we just deleted.
        layer.createTempConnections()

        # Remove the new temp connections to layer 4 for previewing.
        self.gridLayer4.setLayerTempLines(
            self.gridLayer1, self.gridLayer2, self.gridLayer3)

    def updateConnection(self, layer, connections):
        if (self.currentLayer == layer
                and (
                    self.currentLayer != 4 or self.previousLayer is not None)):
            for connection in connections:
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

        grid1Connections = self.gridLayer1.getGrid().getConnections()
        grid2Connections = self.gridLayer2.getGrid().getConnections()
        grid3Connections = self.gridLayer3.getGrid().getConnections()

        if (self.clickManager.getClickType()
                == EditorClickManager.ClickType.DCONNECTION):
            self.updateConnection(1, grid1Connections)
            self.updateConnection(2, grid2Connections)
            self.updateConnection(3, grid3Connections)
            self.updateConnection(
                4, grid1Connections + grid2Connections + grid3Connections)

    def update(self):
        if not self.rendering:
            return

        self.allSprites.update()
        self.hud.update()
        self.messageSystem.update()

        self.events()
